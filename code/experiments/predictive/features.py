"""Frozen pretrained sequence features and inexpensive fixed-template structure descriptors.

No measured function, trafficking, or label-selected contacts are feature inputs.
Coarse electrostatics/packing descriptors are hypotheses, not calculated channel currents.
"""

from __future__ import annotations

import json
import time

import numpy as np
from Bio import Align, SeqIO
from Bio.Align import substitution_matrices
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from data import AA, DATA, OUT, RAW, kir_reference, load_bedbrook, load_kir

HYDRO = dict(
    zip(
        "ACDEFGHIKLMNPQRSTVWY",
        [
            1.8,
            2.5,
            -3.5,
            -3.5,
            2.8,
            -0.4,
            -3.2,
            4.5,
            -3.9,
            3.8,
            1.9,
            -3.5,
            -1.6,
            -3.5,
            -4.5,
            -0.8,
            -0.7,
            4.2,
            -0.9,
            -1.3,
        ],
    )
)
VOLUME = dict(
    zip(
        "ACDEFGHIKLMNPQRSTVWY",
        [
            88.6,
            108.5,
            111.1,
            138.4,
            189.9,
            60.1,
            153.2,
            166.7,
            168.6,
            166.7,
            162.9,
            114.1,
            112.7,
            143.8,
            173.4,
            89.0,
            116.1,
            140.0,
            227.8,
            193.6,
        ],
    )
)
CHARGE = {a: (-1.0 if a in "DE" else 1.0 if a in "KR" else 0.0) for a in AA}
BLOSUM = substitution_matrices.load("BLOSUM62")


def properties(a: str) -> np.ndarray:
    if a not in AA:
        return np.zeros(6)
    return np.array(
        [
            HYDRO[a],
            CHARGE[a],
            VOLUME[a] / 100,
            float(a in "FWY"),
            float(a == "P"),
            float(a == "G"),
        ]
    )


def mapping(reference: str, target: str) -> dict[int, int]:
    aligner = Align.PairwiseAligner(
        mode="global",
        match_score=2,
        mismatch_score=-1,
        open_gap_score=-8,
        extend_gap_score=-0.5,
    )
    alignment = aligner.align(reference, target)[0]
    result = {}
    for (a, b), (c, d) in zip(*alignment.aligned):
        assert b - a == d - c
        result.update({i: c + i - a for i in range(a, b)})
    return result


def structure(reference: str, name: str) -> dict:
    model = PDBParser(QUIET=True).get_structure(name, RAW / (name + ".pdb"))[0]
    chains = []
    for chain in model:
        residues = [
            r for r in chain if r.id[0] == " " and "CA" in r and seq1(r.resname) in AA
        ]
        if len(residues) > 100:
            chains.append(residues)
    residues = chains[0]
    seq = "".join(seq1(r.resname) for r in residues)
    match = mapping(reference, seq)
    xyz = np.array([r["CA"].coord for r in residues]) / 10
    d = np.linalg.norm(xyz[:, None, :] - xyz[None, :, :], axis=-1)
    contacts = (
        (d < 0.8)
        & (d > 0.01)
        & (abs(np.arange(len(seq))[:, None] - np.arange(len(seq))[None, :]) > 3)
    )
    degree = contacts.sum(axis=1)
    q = np.array([CHARGE[a] for a in seq])
    h = np.array([HYDRO[a] for a in seq])
    screened = np.exp(-d / 0.8) / np.maximum(d, 0.3)
    np.fill_diagonal(screened, 0)
    neighbor_field = (
        13.9 * (screened * contacts) @ q
    )  # kT, assumed epsilon=4 and fixed screening length .8 nm.
    match_identity = np.mean([reference[i] == seq[j] for i, j in match.items()])
    return {
        "map": match,
        "degree": degree,
        "field": neighbor_field,
        "neighbors_h": (contacts @ h) / np.maximum(degree, 1),
        "xyz": xyz,
        "contacts": contacts,
        "distances": d,
        "seq": seq,
        "identity": float(match_identity),
        "mapped": len(match),
    }


def kir_conservation(native: str) -> np.ndarray:
    alignment = list(SeqIO.parse(RAW / "kir_alignment.fas", "fasta"))
    query = str(next(r.seq for r in alignment if r.id == "KCNJ2"))
    ungapped = query.replace("-", "")
    m = mapping(native, ungapped)
    columns = [i for i, a in enumerate(query) if a != "-"]
    counts = np.ones((len(native), 20)) * 0.5
    for i, j in m.items():
        col = columns[j]
        for row in alignment:
            if row.seq[col] in AA:
                counts[i, AA.index(row.seq[col])] += 1
    return np.log(counts / counts.sum(axis=1, keepdims=True))


def kir_features(model, tokenizer) -> dict[str, np.ndarray]:
    import torch

    frame, _ = load_kir()
    frame = frame[frame.dataset == "kir_function"].copy()
    _, native = kir_reference()
    st = structure(native, "6M84")
    cons = kir_conservation(native)
    encoded = tokenizer(native, return_tensors="pt")
    with torch.inference_mode():
        output = model(**encoded, output_hidden_states=True)
        hidden = output.hidden_states[-1][0, 1:-1].numpy()
        embedding = model.get_input_embeddings().weight.detach().numpy()
    unique = sorted(set(frame.position))
    logits = {}
    ids = encoded["input_ids"]
    attention = encoded["attention_mask"]
    for k in range(0, len(unique), 8):
        batch = unique[k : k + 8]
        tokens = ids.repeat(len(batch), 1)
        for i, p in enumerate(batch):
            tokens[i, p] = tokenizer.mask_token_id
        with torch.inference_mode():
            out = model(
                input_ids=tokens, attention_mask=attention.repeat(len(batch), 1)
            ).logits
        for i, p in enumerate(batch):
            logits[p] = out[i, p].numpy()
    # Surface has slightly different variant coverage; generate a shared per-variant lookup below.
    both, _ = load_kir()
    allvariants = both.drop_duplicates("id")
    # A position absent in function but present in surface is unlikely; calculate explicitly if needed.
    for p in sorted(set(allvariants.position) - set(logits)):
        tokens = ids.clone()
        tokens[0, p] = tokenizer.mask_token_id
        with torch.inference_mode():
            logits[p] = (
                model(input_ids=tokens, attention_mask=attention).logits[0, p].numpy()
            )
    rows: dict[str, list] = {
        k: []
        for k in [
            "ids",
            "sequence",
            "properties",
            "conservation",
            "esm",
            "physics",
            "geometry",
            "esm_score",
        ]
    }
    for r in allvariants.itertuples():
        p = r.position - 1
        w = r.wt
        m = r.alt
        rows["ids"].append(r.id)
        wt = properties(w)
        alt = properties(m)
        delta = alt - wt
        onehot = []
        for a in [
            w,
            m,
            *[native[j] if 0 <= j < len(native) else "-" for j in range(p - 3, p + 4)],
        ]:
            onehot.extend([float(a == x) for x in AA])
        onehot.extend([p / len(native), np.sin(p / 20), np.cos(p / 20)])
        rows["sequence"].append(onehot)
        rows["properties"].append(np.r_[wt, alt, delta])
        rows["conservation"].append(
            [cons[p, AA.index(m)] - cons[p, AA.index(w)], float(BLOSUM[w, m])]
        )
        wi = tokenizer.convert_tokens_to_ids(w)
        mi = tokenizer.convert_tokens_to_ids(m)
        score = logits[p + 1][mi] - logits[p + 1][wi]
        rows["esm_score"].append([score])
        rows["esm"].append(
            np.r_[hidden[p], embedding[mi] - embedding[wi], score, delta]
        )
        if p in st["map"]:
            j = st["map"][p]
            degree = st["degree"][j]
            rho = float(np.linalg.norm(st["xyz"][j, :2]))
            geom = np.array(
                [1.0, degree, rho, abs(st["xyz"][j, 2]), st["neighbors_h"][j]]
            )
            # This is a fixed-geometry coarse mutation-energy descriptor, not a fitted per-mutant energy.
            phys = np.r_[
                geom,
                delta,
                delta[1] * st["field"][j],
                delta[0] * degree / 10,
                delta[2] * degree / 10,
                abs(alt[1]) * degree / 10,
            ]
        else:
            geom = np.zeros(5)
            phys = np.r_[geom, delta, np.zeros(4)]
        rows["geometry"].append(geom)
        rows["physics"].append(phys)
    (OUT / "kir_structure_audit.json").write_text(
        json.dumps(
            {
                **{k: st[k] for k in ["identity", "mapped"]},
                "template": "6M84 chicken Kir2.2 forced-open K62W/G178D mutant homolog, not WT mouse Kir2.1",
                "scope": "Fixed monomer C-alpha contacts/coarse charges; no variant-specific structures, explicit PIP2 or state free energies",
            },
            indent=2,
        )
    )
    return {k: np.array(v) for k, v in rows.items()}


def bedbrook_features(model, tokenizer) -> dict[str, np.ndarray]:
    import torch

    frame, _ = load_bedbrook()
    aligned = np.array([list(s) for s in frame.seq])
    L = aligned.shape[1]
    parent_indices = np.flatnonzero(frame.control)
    parent = aligned[parent_indices]
    counts = np.array(
        [[np.sum(parent[:, i] == a) + 0.5 for a in AA + "-"] for i in range(L)]
    )
    freq = np.log(counts / counts.sum(1, keepdims=True))
    c1 = str(frame[frame.id == "C1C2"].iloc[0].seq)
    ungapped = c1.replace("-", "")
    st = structure(ungapped, "3UG9")
    columns = [i for i, a in enumerate(c1) if a != "-"]
    col_to_j = {columns[i]: j for i, j in st["map"].items()}
    pairs = [
        (i, j)
        for i in col_to_j
        for j in col_to_j
        if j > i and st["contacts"][col_to_j[i], col_to_j[j]]
    ]
    features: dict[str, list] = {
        k: []
        for k in [
            "ids",
            "sequence",
            "properties",
            "conservation",
            "physics",
            "geometry",
        ]
    }
    for r, seq in zip(frame.itertuples(), aligned):
        features["ids"].append(r.id)
        features["sequence"].append(
            np.array([[float(a == x) for x in AA + "-"] for a in seq]).ravel()
        )
        values = np.array([properties(a) for a in seq])
        features["properties"].append(
            np.r_[values.mean(0), values.std(0), len(r.sequence) / 400]
        )
        features["conservation"].append(
            [
                sum(freq[i, (AA + "-").index(a)] for i, a in enumerate(seq)) / L,
                *[(seq == s).mean() for s in parent],
            ]
        )
        contact = np.zeros(7)
        for i, j in pairs:
            a = properties(seq[i])
            b = properties(seq[j])
            distance = st["distances"][col_to_j[i], col_to_j[j]]
            contact += np.array(
                [
                    a[0] * b[0],
                    13.9 * a[1] * b[1] * np.exp(-distance / 0.8) / distance,
                    abs(a[2] - b[2]),
                    a[2] + b[2],
                    a[3] * b[3],
                    a[4] + b[4],
                    float(seq[i] == "-" or seq[j] == "-"),
                ]
            )
        contact /= max(len(pairs), 1)
        buried_charge = sum(
            abs(properties(seq[i])[1]) * st["degree"][j] for i, j in col_to_j.items()
        ) / len(col_to_j)
        features["physics"].append(
            np.r_[contact, buried_charge, values.mean(0), values.std(0)]
        )
        features["geometry"].append(
            [contact[2], contact[3], contact[-1], len(r.sequence) / 400]
        )
    reps = []
    for k in range(0, len(frame), 8):
        batch = frame.sequence.iloc[k : k + 8].tolist()
        enc = tokenizer(batch, padding=True, return_tensors="pt")
        with torch.inference_mode():
            hidden = model(**enc, output_hidden_states=True).hidden_states[-1]
        for j, s in enumerate(batch):
            reps.append(hidden[j, 1 : len(s) + 1].mean(0).numpy())
    features["esm"] = reps
    (OUT / "bedbrook_structure_audit.json").write_text(
        json.dumps(
            {
                "identity": st["identity"],
                "mapped": st["mapped"],
                "contacts": len(pairs),
                "note": "All nonlocal C-alpha contacts <0.8 nm from WT 3UG9, independent of measured labels; not selected Data4 contacts",
            },
            indent=2,
        )
    )
    return {k: np.array(v) for k, v in features.items()}


if __name__ == "__main__":
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    torch.set_num_threads(4)
    meta = json.loads((RAW / "pretrained_model.json").read_text())
    model = AutoModelForMaskedLM.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    ).eval()
    tokenizer = AutoTokenizer.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    )
    timings = {}
    for dataset, function in [("kir", kir_features), ("bedbrook", bedbrook_features)]:
        start = time.perf_counter()
        result = function(model, tokenizer)
        np.savez_compressed(DATA / f"features/{dataset}.npz", **result)  # type: ignore[arg-type]  # NumPy also types allow_pickle as a named bool.
        timings[dataset] = {
            "seconds": time.perf_counter() - start,
            "variants": len(result["ids"]),
            "feature_dimensions": {k: list(v.shape) for k, v in result.items()},
            "device": "cpu",
        }
        print(dataset, timings[dataset], flush=True)
    (OUT / "feature_resources.json").write_text(json.dumps(timings, indent=2) + "\n")
