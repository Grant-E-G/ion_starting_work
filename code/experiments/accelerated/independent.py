"""Fixed zero-shot checks on independent publications; stability is not channel function."""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from Bio import SeqIO
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from components import AA, CACHE, OUT, ROOT, WW, mapping, mpnn
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForMaskedLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "predictive"))
from benchmark import precision_at_k


def inputs() -> tuple[list, dict]:
    inputs = []
    audit = {}
    for name, site, ref, chain_id in [
        ("ompla", 181, "A", "C"),
        ("pagp", 104, "A", "A"),
    ]:
        pdb = PDBParser(QUIET=True).get_structure(name, CACHE / f"{name}.pdb")[0][
            chain_id
        ]
        residues = [
            r for r in pdb if r.id[0] == " " and "CA" in r and seq1(r.resname) in AA
        ]
        seq = "".join(seq1(r.resname) for r in residues)
        index = next(i for i, r in enumerate(residues) if r.id[1] == site)
        source = CACHE / (
            "OmpLA_Moon_Fleming_set.dat"
            if name == "ompla"
            else "PagP_Marx_Fleming_set.dat"
        )
        refseq = seq[:index] + ref + seq[index + 1 :]
        variants = []
        for line in source.read_text().splitlines():
            bits = line.split()
            alt = bits[2]
            if alt == "A" or (name == "ompla" and alt == "P"):
                continue
            ddg = float(bits[-2])
            variants.append(
                {
                    "id": f"A{site}{alt}",
                    "index": index,
                    "wt": ref,
                    "alt": alt,
                    "ddg": ddg,
                    "gain": ddg < -0.5,
                }
            )
        inputs.append((name, refseq, variants, chain_id))
        audit[name] = {
            "site_author_number": site,
            "resolved_sequence_index0": index,
            "template_residue": seq[index],
            "experimental_reference": ref,
            "n": len(variants),
            "sequence": refseq,
        }
    full = str(next(SeqIO.parse(CACHE / "5ZIH.fasta", "fasta")).seq)
    pdb = PDBParser(QUIET=True).get_structure("chr", CACHE / "5ZIH.pdb")[0]["A"]
    residues = [
        r for r in pdb if r.id[0] == " " and "CA" in r and seq1(r.resname) in AA
    ]
    seq = "".join(seq1(r.resname) for r in residues)
    match = mapping(full, seq)
    reverse = {j: i for i, j in match.items()}
    auth = {r.id[1]: reverse[j] for j, r in enumerate(residues) if j in reverse}
    assert full[auth[176]] == "K"
    full = full[: auth[176]] + "R" + full[auth[176] + 1 :]
    policy = json.loads(
        (ROOT / "sources/accelerated/evaluation_policy.json").read_text()
    )["chrimson"]
    variants = []
    for v in policy["panel"]:
        site = int(v[1:-1])
        index = auth[site]
        assert full[index] == v[0], (v, index, full[index])
        variants.append(
            {
                "id": v,
                "index": index,
                "wt": v[0],
                "alt": v[-1],
                "gain": v in policy["current_gains"],
                "missing": v in policy["unpatchable_exclude"],
            }
        )
    inputs.append(("chrimson", full, variants, "A"))
    audit["chrimson"] = {
        "sequence": full,
        "author_to_sequence_index0": auth,
        "scope": "PDB-derived chimeric surrogate +K176R, not verified experimental fusion sequence",
    }
    return inputs, audit


def main() -> None:
    torch.set_num_threads(4)
    cases, audit = inputs()
    rows = []
    timings: dict = {}
    model_specs = [
        (
            "esm2_8m",
            json.loads(
                (ROOT / "sources/predictive/raw/pretrained_model.json").read_text()
            ),
        ),
        (
            "esm1v_650m",
            json.loads((ROOT / "sources/accelerated/esm1v_model.json").read_text()),
        ),
    ]
    for label, meta in model_specs:
        start = time.perf_counter()
        model = AutoModelForMaskedLM.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        ).eval()
        tokenizer = AutoTokenizer.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        )
        load_seconds = time.perf_counter() - start
        for name, seq, variants, chain_id in cases:
            t = time.perf_counter()
            enc = tokenizer(seq, return_tensors="pt")
            scores = {}
            for index in sorted({v["index"] for v in variants}):
                ids = enc["input_ids"].clone()
                ids[0, index + 1] = tokenizer.mask_token_id
                with torch.inference_mode():
                    logits = (
                        model(input_ids=ids, attention_mask=enc["attention_mask"])
                        .logits[0, index + 1]
                        .numpy()
                    )
                scores[index] = logits
            for v in variants:
                score = (
                    scores[v["index"]][tokenizer.convert_tokens_to_ids(v["alt"])]
                    - scores[v["index"]][tokenizer.convert_tokens_to_ids(v["wt"])]
                )
                rows.append(
                    dict(dataset=name, method=label, **v, prediction=float(score))
                )
            timings[f"{label}:{name}"] = {
                "inference_seconds": time.perf_counter() - t,
                "masked_sites": len(scores),
                "sequence_length": len(seq),
                "parameters": sum(p.numel() for p in model.parameters()),
                "load_seconds": load_seconds,
                "peak_rss_MiB_process_cumulative": resource.getrusage(
                    resource.RUSAGE_SELF
                ).ru_maxrss
                / 1024,
            }
            print(label, name, timings[f"{label}:{name}"], flush=True)
        del model, tokenizer
    for name, seq, variants, chain_id in cases:
        path = CACHE / ("5ZIH.pdb" if name == "chrimson" else f"{name}.pdb")
        seq_p, probs, mpnn_timing = mpnn(name, chain_id, path)
        match = mapping(seq, seq_p)
        timings[f"mpnn:{name}"] = mpnn_timing
        for v in variants:
            if v["index"] not in match:
                continue
            j = match[v["index"]]
            assert seq_p[j] in [v["wt"], "K", "V"] or name == "chrimson", (
                name,
                v,
                seq_p[j],
            )
            score = (
                probs[j, (AA + "X").index(v["alt"])]
                - probs[j, (AA + "X").index(v["wt"])]
            )
            rows.append(
                dict(dataset=name, method="proteinmpnn", **v, prediction=float(score))
            )
            rows.append(
                dict(
                    dataset=name,
                    method="WW_transfer",
                    **v,
                    prediction=WW[v["wt"]] - WW[v["alt"]],
                )
            )
    for name, _seq, variants, _chain_id in cases:
        for v in variants:
            rows.append(dict(dataset=name, method="WT_null", **v, prediction=0.0))
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "independent_predictions.csv", index=False)
    results = []
    for (dataset, method), g in frame.groupby(["dataset", "method"]):
        if dataset == "chrimson":
            g = g[g.missing != True]
        k = 5
        d = {
            "dataset": dataset,
            "method": method,
            "n": len(g),
            "positive": int(g.gain.sum()),
            "prevalence": g.gain.mean(),
            "precision5": precision_at_k(g.prediction.to_numpy(), g.gain.to_numpy(), k),
            "auc": roc_auc_score(g.gain, g.prediction),
        }
        if dataset != "chrimson":
            d["stability_spearman"] = (
                spearmanr(-g.ddg, g.prediction).statistic
                if np.std(g.prediction) > 1e-12
                else 0.0
            )
        results.append(d)
    pd.DataFrame(results).to_csv(OUT / "independent_metrics.csv", index=False)
    (OUT / "independent_resources.json").write_text(
        json.dumps(timings, indent=2) + "\n"
    )
    (OUT / "independent_input_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n"
    )
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
