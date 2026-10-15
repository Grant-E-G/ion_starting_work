"""Actual mutant minus WT embeddings on an independent BK panel; GPU precision.

No new pretrained model or experimental fine tuning. The external study's exact
accession is used; its pore window is identical to the structural reference.
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
import torch
from Bio import SeqIO
from data import DATA, FEATURES, OUT, RAW, load_bk
from transformers import AutoModelForMaskedLM, AutoTokenizer


def main() -> None:
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    torch.backends.cuda.matmul.allow_tf32 = False
    destination = FEATURES / "external_bk_sequence_deltas.npz"
    if destination.exists():
        print("cached", destination)
        return
    training = load_bk()
    external = pd.read_csv(OUT / "external_bk_measurements.csv").drop_duplicates("id")
    source_wt = str(next(SeqIO.parse(RAW / "6V3G.fasta", "fasta")).seq)
    exact_wt = str(next(SeqIO.parse(RAW / "bk_external_AAB65837.fasta", "fasta")).seq)
    assert source_wt[:1022] == exact_wt[:1022]
    metadata = json.loads((DATA / "esm1v_650m_model.json").read_text())
    start = time.perf_counter()
    model = AutoModelForMaskedLM.from_pretrained(
        metadata["name"],
        revision=metadata["revision"],
        local_files_only=True,
        low_cpu_mem_usage=True,
        device_map={"": "cuda"},
    ).eval()
    tokenizer = AutoTokenizer.from_pretrained(
        metadata["name"], revision=metadata["revision"], local_files_only=True
    )
    setup = time.perf_counter() - start

    def inputs(ident: str, reference: str) -> tuple[str, str, list[int]]:
        chars = list(reference)
        sites = []
        for token in ident.split(","):
            site = int(token[1:-1]) - 1
            assert reference[site] == token[0]
            chars[site] = token[-1]
            sites.append(site)
        left = max(0, min(min(sites) - 511, len(chars) - 1022))
        return (
            "".join(chars[left : left + 1022]),
            reference[left : left + 1022],
            [site - left + 1 for site in sites],
        )

    source_records = [inputs(ident, source_wt) for ident in training.id]
    external_records = [inputs(ident, exact_wt) for ident in external.id]
    native = {}
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    for record in [*source_records, *external_records]:
        _, reference, _ = record
        if reference not in native:
            encoded = tokenizer(reference, return_tensors="pt").to("cuda")
            with torch.inference_mode():
                hidden = model.esm(**encoded).last_hidden_state[0]
            native[reference] = hidden.cpu().numpy()
    with np.load(FEATURES / "bk_esm1v_650m_mutant_embeddings.npz") as values:
        order = pd.Index(values["ids"]).get_indexer(training.id)
        assert (order >= 0).all()
        pooled = values["pooled"][order]
        mutated = values["mutated_sites"][order]
    reference_pool = np.stack(
        [
            native[reference][1 : len(reference) + 1].mean(0)
            for _, reference, _ in source_records
        ]
    )
    reference_site = np.stack(
        [native[reference][sites].sum(0) for _, reference, sites in source_records]
    )
    source_delta = np.column_stack([pooled - reference_pool, mutated - reference_site])
    values = []
    for record in external_records:
        sequence, reference, sites = record
        encoded = tokenizer(sequence, return_tensors="pt").to("cuda")
        with torch.inference_mode():
            hidden = model.esm(**encoded).last_hidden_state[0].cpu().numpy()
        values.append(
            np.concatenate(
                [
                    hidden[1 : len(sequence) + 1].mean(0)
                    - native[reference][1 : len(reference) + 1].mean(0),
                    hidden[sites].sum(0) - native[reference][sites].sum(0),
                ]
            )
        )
    external_delta = np.stack(values)
    # Check that old and new extraction implementations agree before readout.
    errors = []
    for index in range(3):
        sequence, _, sites = source_records[index]
        encoded = tokenizer(sequence, return_tensors="pt").to("cuda")
        with torch.inference_mode():
            hidden = model.esm(**encoded).last_hidden_state[0].cpu().numpy()
        errors.append(
            float(
                max(
                    abs(hidden[1 : len(sequence) + 1].mean(0) - pooled[index]).max(),
                    abs(hidden[sites].mean(0) - mutated[index]).max(),
                )
            )
        )
    assert (
        max(errors) < 0.001
        and np.isfinite(source_delta).all()
        and np.isfinite(external_delta).all()
    )
    np.savez_compressed(
        destination,
        training_ids=training.id.to_numpy(dtype=str),
        external_ids=external.id.to_numpy(dtype=str),
        training_delta=source_delta,
        external_delta=external_delta,
    )
    torch.cuda.synchronize()
    receipt = {
        "model": metadata,
        "training_constructs": len(training),
        "external_constructs": len(external),
        "native_windows": len(native),
        "setup_seconds": setup,
        "inference_seconds": time.perf_counter() - start,
        "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
        "old_cache_max_embedding_error": max(errors),
        "representation": "Whole-window mean mutant-minus-WT plus sum of mutated-site hidden differences; native controls are exactlyzero. Does not assume additive mutant transformer responses.",
        "sequence_audit": "External1113aaAAB65837 and reference1065aa share first1056residues; this pore panel uses the identical1022aa window. C-terminal effects outside the window are unmodelled.",
    }
    (OUT / "external_bk_sequence_resources.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    # Small paired throughput/precision probe; source features above stayFP32.
    probe_ids = ["L302I", "M304I"]
    probes = [inputs(ident, exact_wt) for ident in probe_ids]
    encoded = tokenizer([record[0] for record in probes], return_tensors="pt").to(
        "cuda"
    )
    references = tokenizer([record[1] for record in probes], return_tensors="pt").to(
        "cuda"
    )

    def embed(batch: dict, half: bool) -> torch.Tensor:
        with torch.inference_mode(), torch.autocast(
            "cuda", dtype=torch.float16, enabled=half
        ):
            return model.esm(**batch).last_hidden_state.float()

    deltas = {}
    times: dict[str, list[float]] = {"FP32": [], "autocastFP16": []}
    for half in [False, True]:
        native_hidden, mutant_hidden = embed(references, half), embed(encoded, half)
        delta = []
        for i, (sequence, _, sites) in enumerate(probes):
            delta.append(
                torch.cat(
                    [
                        (
                            mutant_hidden[i, 1 : len(sequence) + 1]
                            - native_hidden[i, 1 : len(sequence) + 1]
                        ).mean(0),
                        (mutant_hidden[i, sites] - native_hidden[i, sites]).sum(0),
                    ]
                )
            )
        deltas[half] = torch.stack(delta).cpu().numpy()
    for _ in range(3):
        for half, label in [(False, "FP32"), (True, "autocastFP16")]:
            torch.cuda.synchronize()
            before = time.perf_counter()
            embed(encoded, half)
            torch.cuda.synchronize()
            times[label].append(time.perf_counter() - before)
    relative = np.linalg.norm(deltas[True] - deltas[False], axis=1) / np.maximum(
        np.linalg.norm(deltas[False], axis=1), 1e-12
    )
    (OUT / "gpu_precision_probe.json").write_text(
        json.dumps(
            {
                "model": metadata,
                "sequence_length": 1022,
                "batch_size": 2,
                "probe_mutants": probe_ids,
                "times_seconds": times,
                "FP32_median_over_FP16_median": float(
                    np.median(times["FP32"]) / np.median(times["autocastFP16"])
                ),
                "delta_relative_L2_errors": relative.tolist(),
                "passes_predeclared5percent_delta_tolerance": bool(
                    (relative <= 0.05).all()
                ),
                "timing": "Alternating paired measurements under shared GPU load, not isolated throughput",
                "scope": "Parameter weights remainFP32; FP16autocast numerical/throughput check, not a functional accuracy guarantee. Exported external benchmark usesFP32.",
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
