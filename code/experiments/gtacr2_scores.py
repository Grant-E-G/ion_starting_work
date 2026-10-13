"""CPU masked-marginal feasibility check; scores are not transport predictions."""

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fasta", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", default="facebook/esm2_t6_8M_UR50D")
    parser.add_argument(
        "--scan", action="store_true", help="Score all single substitutions"
    )
    args = parser.parse_args()
    sequence = "".join(
        line.strip()
        for line in args.fasta.read_text().splitlines()
        if line.strip() and not line.startswith(">")
    )[:266]
    variants = ["E9Q", "E56Q", "E64Q", "E159Q", "E219Q", "D230N"]
    for variant in variants:
        assert sequence[int(variant[1:-1]) - 1] == variant[0], variant
    torch.set_num_threads(4)
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForMaskedLM.from_pretrained(args.model).eval()
    loaded = time.perf_counter()
    rows = []
    positions = (
        range(1, len(sequence) + 1)
        if args.scan
        else sorted({int(variant[1:-1]) for variant in variants})
    )
    with torch.inference_mode():
        for position in positions:
            encoded = tokenizer(sequence, return_tensors="pt")
            # ESM adds one leading token; residue numbering is one-based.
            assert encoded["input_ids"].shape[1] == len(sequence) + 2
            encoded["input_ids"][0, position] = tokenizer.mask_token_id
            logits = model(**encoded).logits[0, position]
            substitutions = (
                [
                    f"{sequence[position - 1]}{position}{aa}"
                    for aa in "ACDEFGHIKLMNPQRSTVWY"
                    if aa != sequence[position - 1]
                ]
                if args.scan
                else [v for v in variants if int(v[1:-1]) == position]
            )
            for variant in substitutions:
                score = float(
                    logits[tokenizer.convert_tokens_to_ids(variant[-1])]
                    - logits[tokenizer.convert_tokens_to_ids(variant[0])]
                )
                rows.append({"variant": variant, "masked_log_odds": score})
    with args.output.open("w") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "model": args.model,
        "revision": getattr(model.config, "_commit_hash", None),
        "residues": len(sequence),
        "threads": 4,
        "load_seconds": loaded - started,
        "inference_seconds": time.perf_counter() - loaded,
        "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
        "scored_variants": len(rows),
    }
    args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata))


if __name__ == "__main__":
    main()
