"""Published physical-surrogate inference, source checkpoints only.

No experimentally fine-tuned published weights are used. BK tests whether a
structure-conditioned global surrogate yields cheap mutation-specific state
energies; soluble controls test physical attributes against functional labels.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from data import FEATURES, OUT, RAW, load_bk, load_vep

sys.path.insert(0, str(RAW / "metl"))
import metl

CHECKPOINTS = {
    "global1d": "METL-G-20M-1D-D72M9aEp.pt",
    "global3d": "METL-G-20M-3D-Nr9zCKpR.pt",
    "avgfp_local": "METL-L-2M-3D-GFP-Hr4GNHws.pt",
    "pab1_local": "METL-L-2M-3D-Pab1-2rr8V4th.pt",
    "gb1_local": "METL-L-2M-3D-GB1-epegcFiH.pt",
    "gb1_binding": "METL-BIND-2M-3D-GB1-BINDING-Bo5wn2SG.pt",
    "gb1_binding_control": "METL-BIND-2M-3D-GB1-STANDARD-K6mw24Rg.pt",
}


def bk_states() -> tuple[str, dict[int, int], dict[str, Path]]:
    structures = {
        state: PDBParser(QUIET=True).get_structure(state, RAW / f"{identifier}.pdb")[0][
            "A"
        ]
        for state, identifier in [("closed", "6V3G"), ("open", "6V38")]
    }
    residues = {
        state: {r.id[1]: r for r in chain if r.id[0] == " " and "CA" in r}
        for state, chain in structures.items()
    }
    common = sorted(set(residues["open"]) & set(residues["closed"]))
    sequence = "".join(seq1(residues["closed"][site].resname) for site in common)
    assert sequence == "".join(seq1(residues["open"][site].resname) for site in common)
    mapping = {site: i for i, site in enumerate(common)}
    paths = {}
    for state, identifier in [("closed", "6V3G"), ("open", "6V38")]:
        path = OUT / f"bk_metl_{state}.pdb"
        lines = [
            line
            for line in (RAW / f"{identifier}.pdb").read_text().splitlines()
            if line.startswith("ATOM")
            and line[21] == "A"
            and int(line[22:26]) in mapping
        ]
        path.write_text("\n".join(lines) + "\nEND\n")
        paths[state] = path
    return sequence, mapping, paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", choices=["bk", "avgfp", "pab1", "gb1"], required=True
    )
    parser.add_argument("--model", choices=CHECKPOINTS, required=True)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    destination = (
        FEATURES
        / f"{args.dataset}_metl_{args.model}{'_pilot' if args.limit else ''}.npz"
    )
    if destination.exists():
        print("cached", destination)
        return
    checkpoint = RAW / "metl/weights" / CHECKPOINTS[args.model]
    model, encoder = metl.get_from_checkpoint(str(checkpoint))
    model.eval().to("cuda")
    if args.dataset == "bk":
        frame = load_bk()
        sequence, mapping, structures = bk_states()
        offset = None
    else:
        frame, sequence, offset = load_vep(args.dataset)
        selection = FEATURES / f"{args.dataset}_esm2_35m_mutant_embeddings.npz"
        with np.load(selection) as file:
            ids = file["ids"]
        frame = frame.set_index("id", drop=False).loc[ids].reset_index(drop=True)
        mapping = {position + offset: position for position in range(len(sequence))}
        pdb_name = {"avgfp": "1gfl_cm.pdb", "pab1": "pab1_cm.pdb", "gb1": "2qmt_p.pdb"}[
            args.dataset
        ]
        structures = {"native": RAW / "metl/pdbs" / pdb_name}
    if args.limit:
        frame = frame.head(args.limit)
    sequences = [sequence]
    for parsed in frame.parsed:
        chars = list(sequence)
        for wt, position, alt in parsed:
            assert sequence[mapping[position]] == wt
            chars[mapping[position]] = alt
        sequences.append("".join(chars))
    encoded = encoder.encode_sequences(sequences)
    attributes, representations = {}, {}
    captured = []

    def capture(_module: torch.nn.Module, _inputs: tuple, output: torch.Tensor) -> None:
        captured.append(output.detach())

    hook = model.model.avg_pooling.register_forward_hook(capture)
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    start = time.perf_counter()
    for state, pdb in structures.items():
        rows, hidden = [], []
        for i in range(0, len(encoded), args.batch_size):
            captured.clear()
            values = torch.tensor(encoded[i : i + args.batch_size], device="cuda")
            with torch.inference_mode():
                predicted = (
                    model(values, pdb_fn=str(pdb))
                    if "3d" in args.model
                    or "local" in args.model
                    or "binding" in args.model
                    else model(values)
                )
            rows.append(predicted.cpu().numpy())
            assert len(captured) == 1
            hidden.append(captured[0].cpu().numpy())
            if i % (args.batch_size * 100) == 0:
                print(
                    args.dataset,
                    args.model,
                    state,
                    i,
                    len(encoded),
                    round(time.perf_counter() - start, 1),
                    flush=True,
                )
        matrix, latent = np.concatenate(rows), np.concatenate(hidden)
        attributes[state] = matrix[1:] - matrix[:1]
        representations[state] = latent[1:] - latent[:1]
        assert np.isfinite(matrix).all() and np.isfinite(latent).all()
    hook.remove()
    torch.cuda.synchronize()
    output = {f"attributes_{key}": value for key, value in attributes.items()}
    output.update({f"latent_{key}": value for key, value in representations.items()})
    if args.dataset == "bk":
        output["state_difference"] = attributes["open"] - attributes["closed"]
        output["latent_state_difference"] = (
            representations["open"] - representations["closed"]
        )
        if args.model == "global1d":
            assert np.max(abs(output["state_difference"])) < 1e-6
    np.savez_compressed(destination, ids=frame.id.to_numpy(dtype=str), **output)
    receipt = {
        "dataset": args.dataset,
        "checkpoint": CHECKPOINTS[args.model],
        "sequence_length": len(sequence),
        "constructs": len(frame),
        "states": list(structures),
        "output_dimensions": {key: list(value.shape) for key, value in output.items()},
        "seconds": time.perf_counter() - start,
        "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
        "peak_reserved_MiB": torch.cuda.max_memory_reserved() / 2**20,
        "parameters": sum(p.numel() for p in model.parameters()),
        "scope": "Source-only physical-attribute surrogate; outputs normalized pretraining targets, not calibrated kcal/mol or gating energies; no experimental finetuned checkpoint",
        "BK_limitations": (
            "Common resolved monomer residues, no explicit membrane/cofactors/tetramer; open Ca-bound vs closed Ca-free WT conformations"
            if args.dataset == "bk"
            else None
        ),
    }
    (
        OUT
        / f"{args.dataset}_metl_{args.model}{'_pilot' if args.limit else ''}_resources.json"
    ).write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
