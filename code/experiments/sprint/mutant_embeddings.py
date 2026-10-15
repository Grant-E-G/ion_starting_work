"""Actual mutant-sequence pretrained embeddings, beyond WT-site descriptors."""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import torch
from Bio import SeqIO
from data import (
    DATA,
    FEATURES,
    OUT,
    RAW,
    SEEDS,
    load_bk,
    load_vep,
    vep_split,
)
from sequence import MODELS
from transformers import AutoModelForMaskedLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--datasets", nargs="+", default=["bk", "pab1", "avgfp", "gb1"])
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--train-limit", type=int, default=1000)
    args = parser.parse_args()
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    meta = json.loads((DATA / f"{args.model}_model.json").read_text())
    transformer = (
        AutoModelForMaskedLM.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        )
        .eval()
        .to("cuda")
    )
    tokenizer = AutoTokenizer.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    )
    for name in args.datasets:
        suffix = (
            "" if args.train_limit == 1000 or name == "bk" else f"_n{args.train_limit}"
        )
        destination = FEATURES / f"{name}_{args.model}_mutant_embeddings{suffix}.npz"
        if destination.exists():
            print("cached", destination, flush=True)
            continue
        if name == "bk":
            frame = load_bk()
            sequence = str(next(SeqIO.parse(RAW / "6V3G.fasta", "fasta")).seq)
            offset, selected = 1, np.arange(len(frame))
        else:
            frame, sequence, offset = load_vep(name)
            indices = set()
            for protocol in ["site", "mutation"]:
                for seed in SEEDS:
                    split = vep_split(frame, name, protocol, seed, offset)
                    fit = np.flatnonzero(split == "train")
                    fit = np.random.RandomState(seed).permutation(fit)[
                        : args.train_limit
                    ]
                    indices.update(fit.tolist())
                    indices.update(
                        np.flatnonzero(np.isin(split, ["validation", "test"])).tolist()
                    )
            selected = np.array(sorted(indices))
        records = frame.iloc[selected]
        hidden_values, mutated_values, sequences = [], [], []
        # For BK use the same deterministic mutation-centred context policy as
        # masked marginals. Full sequence for all shorter benchmark proteins.
        sites_list = []
        for parsed in records.parsed:
            chars = list(sequence)
            positions = []
            for wt, site, alt in parsed:
                assert chars[site - offset] == wt
                chars[site - offset] = alt
                positions.append(site - offset)
            left = max(0, min(positions[0] - 511, len(chars) - 1022))
            sequences.append("".join(chars[left : left + 1022]))
            sites_list.append([p - left + 1 for p in positions])
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        start = time.perf_counter()
        for i in range(0, len(sequences), args.batch_size):
            batch = sequences[i : i + args.batch_size]
            encoded = tokenizer(batch, return_tensors="pt", padding=True).to("cuda")
            with torch.inference_mode():
                hidden = transformer.esm(**encoded).last_hidden_state
                mask = encoded["attention_mask"].clone()
                mask[:, 0] = 0
                for j, seq in enumerate(batch):
                    mask[j, len(seq) + 1] = 0
                pooled = (hidden * mask[:, :, None]).sum(1) / mask.sum(1, keepdim=True)
                sites = torch.stack(
                    [
                        hidden[j, positions].mean(0)
                        for j, positions in enumerate(
                            sites_list[i : i + args.batch_size]
                        )
                    ]
                )
            hidden_values.append(pooled.cpu().numpy().astype(np.float32))
            mutated_values.append(sites.cpu().numpy().astype(np.float32))
            if i % (args.batch_size * 100) == 0:
                print(
                    args.model,
                    name,
                    i,
                    len(sequences),
                    round(time.perf_counter() - start, 1),
                    flush=True,
                )
        torch.cuda.synchronize()
        values, site_values = np.concatenate(hidden_values), np.concatenate(
            mutated_values
        )
        assert np.isfinite(values).all() and np.isfinite(site_values).all()
        np.savez_compressed(
            destination,
            ids=records.id.to_numpy(dtype=str),
            pooled=values,
            mutated_sites=site_values,
            selected_indices=selected,
        )
        receipt = {
            "model": meta,
            "dataset": name,
            "constructs": len(records),
            "inference_seconds": time.perf_counter() - start,
            "batch_size": args.batch_size,
            "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
            "peak_reserved_MiB": torch.cuda.max_memory_reserved() / 2**20,
            "device": torch.cuda.get_device_name(),
            "scope": "Actual mutant-sequence representations, no functional model fitting; sequence mean and mean mutated-site hidden states",
            "selection": "Union of frozen train-limit/validation/test rows across five seeds and two grouping protocols; labels not used",
            "timing_caveat": "Other sprint jobs may share CPU/GPU; measured workload wall time, not isolated hardware benchmark",
        }
        (OUT / f"{name}_{args.model}_mutant_embedding_resources.json").write_text(
            json.dumps(receipt, indent=2) + "\n"
        )
        print(json.dumps(receipt), flush=True)
    print("finished", args.model, flush=True)


if __name__ == "__main__":
    main()
