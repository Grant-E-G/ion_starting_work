"""Existing sequence and physical-surrogate components on an independent GPCR."""

from __future__ import annotations

import argparse
import json
import sys
import time

import numpy as np
import pandas as pd
import torch
from adrb2_data import wt_sequence
from data import DATA, FEATURES, OUT, RAW
from transformers import AutoModelForMaskedLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        choices=["esm2_35m", "esm1v_650m", "metl_global3d", "metl_global1d"],
        required=True,
    )
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    suffix = "" if args.model.startswith("metl") else "_mutant_embeddings"
    destination = FEATURES / f"adrb2_{args.model}{suffix}.npz"
    if destination.exists():
        print("cached", destination)
        return
    frame = pd.read_csv(OUT / "adrb2_measurements.csv")
    sequence = wt_sequence()
    if args.model.startswith("metl"):
        sys.path.insert(0, str(RAW / "metl"))
        import metl

        name = (
            "METL-G-20M-3D-Nr9zCKpR.pt"
            if args.model.endswith("3d")
            else "METL-G-20M-1D-D72M9aEp.pt"
        )
        model, encoder = metl.get_from_checkpoint(str(RAW / "metl/weights" / name))
        model.to("cuda").eval()
        manifest = json.loads((DATA / "adrb2_manifest.json").read_text())
        native_sites = manifest["common_residue_sites"]
        mapping = {site: i for i, site in enumerate(native_sites)}
        reference = "".join(sequence[site - 1] for site in native_sites)
        selected = frame[frame.structure_eligible].copy()
        sequences = [reference]
        for row in selected.itertuples():
            chars = list(reference)
            assert reference[mapping[row.site]] == row.id[0]
            chars[mapping[row.site]] = row.alt
            sequences.append("".join(chars))
        encoded = encoder.encode_sequences(sequences)
        arrays = {}
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        for state in ["closed", "open"]:
            output = []
            for i in range(0, len(encoded), args.batch_size):
                with torch.inference_mode():
                    inputs = torch.tensor(
                        encoded[i : i + args.batch_size], device="cuda"
                    )
                    value = (
                        model(inputs, pdb_fn=str(OUT / f"adrb2_{state}.pdb"))
                        if args.model.endswith("3d")
                        else model(inputs)
                    )
                output.append(value.cpu().numpy())
                if i % (args.batch_size * 100) == 0:
                    print(args.model, state, i, len(encoded), flush=True)
            attributes = np.concatenate(output)
            arrays[state] = attributes[1:] - attributes[:1]
        arrays["state_difference"] = arrays["open"] - arrays["closed"]
        if args.model.endswith("1d"):
            assert np.max(abs(arrays["state_difference"])) < 1e-6
        np.savez_compressed(destination, ids=selected.id.to_numpy(dtype=str), **arrays)
    else:
        meta = json.loads((DATA / f"{args.model}_model.json").read_text())
        model = (
            AutoModelForMaskedLM.from_pretrained(
                meta["name"], revision=meta["revision"], local_files_only=True
            )
            .to("cuda")
            .eval()
        )
        tokenizer = AutoTokenizer.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        )
        selected = frame.copy()
        sequences = []
        for row in selected.itertuples():
            assert sequence[row.site - 1] == row.id[0]
            sequences.append(sequence[: row.site - 1] + row.alt + sequence[row.site :])
        output, mutated = [], []
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        for i in range(0, len(sequences), args.batch_size):
            encoded = tokenizer(
                sequences[i : i + args.batch_size], return_tensors="pt"
            ).to("cuda")
            with torch.inference_mode():
                hidden = model.esm(**encoded).last_hidden_state
                pooled = hidden[:, 1 : len(sequence) + 1].mean(1)
                sites = torch.stack(
                    [
                        hidden[j, int(site)]
                        for j, site in enumerate(
                            selected.site.to_numpy()[i : i + args.batch_size]
                        )
                    ]
                )
            output.append(pooled.cpu().numpy())
            mutated.append(sites.cpu().numpy())
            if i % (args.batch_size * 100) == 0:
                print(args.model, i, len(sequences), flush=True)
        np.savez_compressed(
            destination,
            ids=selected.id.to_numpy(dtype=str),
            pooled=np.concatenate(output),
            mutated_sites=np.concatenate(mutated),
        )
    torch.cuda.synchronize()
    receipt = {
        "dataset": "ADRB2 Jones2020",
        "model": args.model,
        "constructs": len(selected),
        "seconds": time.perf_counter() - start,
        "parameters": sum(p.numel() for p in model.parameters()),
        "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
        "scope": "Existing pretrained inference; no function labels used for feature generation; physical surrogate lacks ligand, lipids and Gs",
        "timing": "Shared local hardware; warm steady-state throughput not separately claimed",
    }
    (OUT / f"adrb2_{args.model}_resources.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
