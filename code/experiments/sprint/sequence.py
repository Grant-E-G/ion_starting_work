"""GPU pretrained masked marginals and contextual residue features; no fitting."""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import torch
from Bio import SeqIO
from data import AA, DATA, FEATURES, OUT, RAW, constants, load_bk
from huggingface_hub import model_info, snapshot_download
from transformers import AutoModelForMaskedLM, AutoTokenizer

MODELS = {
    "esm2_8m": "facebook/esm2_t6_8M_UR50D",
    "esm2_35m": "facebook/esm2_t12_35M_UR50D",
    "esm2_150m": "facebook/esm2_t30_150M_UR50D",
    "esm2_3b": "facebook/esm2_t36_3B_UR50D",
    "esm1v_650m": "facebook/esm1v_t33_650M_UR90S_1",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--datasets", nargs="+", default=["bk", *constants()])
    args = parser.parse_args()
    assert (
        torch.cuda.is_available()
    ), "Use documented GPU execution permissions/environment"
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.manual_seed(1729)
    meta_path = DATA / f"{args.model}_model.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    else:
        revision = model_info(MODELS[args.model]).sha
        meta = {"name": MODELS[args.model], "revision": revision}
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    start = time.perf_counter()
    snapshot_download(
        meta["name"],
        revision=meta["revision"],
        allow_patterns=[
            "config.json",
            "pytorch_model*.bin",
            "pytorch_model.bin.index.json",
            "model.safetensors",
            "vocab.txt",
            "tokenizer_config.json",
            "special_tokens_map.json",
        ],
    )
    options = (
        {
            "torch_dtype": torch.float16,
            "low_cpu_mem_usage": True,
            "device_map": {"": "cuda"},
        }
        if args.model == "esm2_3b"
        else {}
    )
    model = (
        AutoModelForMaskedLM.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True, **options
        )
        .eval()
        .to("cuda")
    )
    tokenizer = AutoTokenizer.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    )
    aa_ids = tokenizer.convert_tokens_to_ids(list(AA))
    setup_seconds = time.perf_counter() - start
    for name in args.datasets:
        destination = FEATURES / f"{name}_{args.model}.npz"
        if destination.exists():
            print("cached", destination, flush=True)
            continue
        if name == "bk":
            sequence = str(next(SeqIO.parse(RAW / "6V3G.fasta", "fasta")).seq)
            frame = load_bk()
            sites = sorted(set(frame.resN.astype(int) - 1))
            assert all(sequence[int(v[1:-1]) - 1] == v[0] for v in frame.id)
        elif name == "kir":
            from kir_transfer import original

            _, sequence = original().kir_reference()
            sites = list(range(len(sequence)))
        elif name == "adrb2":
            from adrb2_data import wt_sequence

            sequence = wt_sequence()
            sites = list(range(len(sequence)))
        else:
            sequence = constants()[name]["wt_aa"]
            sites = list(range(len(sequence)))
        scores: np.ndarray = np.full((len(sequence), len(AA)), np.nan, dtype=np.float32)
        hidden_size = model.config.hidden_size
        hidden = np.full((len(sequence), hidden_size), np.nan, dtype=np.float32)
        # 1022-residue windows fit the learned positional limit of ESM-1v.
        # BK is 1065 residues; mutation-centred windows retain native order.
        windows: dict[int, dict] = {}
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        for j, site in enumerate(sites):
            left = max(0, min(site - 511, len(sequence) - 1022))
            seq = sequence[left : left + 1022]
            position = site - left + 1
            if left not in windows:
                encoded = tokenizer(seq, return_tensors="pt").to("cuda")
                with torch.inference_mode():
                    wt = (
                        model(**encoded, output_hidden_states=True)
                        .hidden_states[-1][0, 1 : len(seq) + 1]
                        .cpu()
                        .numpy()
                    )
                windows[left] = {"encoded": encoded, "hidden": wt}
            hidden[site] = windows[left]["hidden"][position - 1]
            encoded = {
                key: value.clone() for key, value in windows[left]["encoded"].items()
            }
            encoded["input_ids"][0, position] = tokenizer.mask_token_id
            with torch.inference_mode():
                logits = model(**encoded).logits[0, position, aa_ids]
                # Differences are unchanged by normalizing over canonical AAs.
                scores[site] = torch.log_softmax(logits, 0).cpu().numpy()
            if j % 100 == 0:
                print(
                    args.model,
                    name,
                    j,
                    len(sites),
                    round(time.perf_counter() - start, 2),
                    flush=True,
                )
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        assert np.isfinite(scores[sites]).all() and np.isfinite(hidden[sites]).all()
        with torch.inference_mode():
            aa_embedding = model.get_input_embeddings().weight[aa_ids].cpu().numpy()
        np.savez_compressed(
            destination,
            sequence=np.array(sequence),
            aa=np.array(AA),
            masked_logp=scores,
            wt_hidden=hidden,
            aa_embedding=aa_embedding,
            sites=np.array(sites),
        )
        receipt = {
            "model": meta,
            "dataset": name,
            "sequence_length": len(sequence),
            "sites": len(sites),
            "inference_seconds": elapsed,
            "setup_seconds": setup_seconds,
            "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
            "peak_reserved_MiB": torch.cuda.max_memory_reserved() / 2**20,
            "gpu": torch.cuda.get_device_name(0),
            "torch": torch.__version__,
            "scope": "Masked token likelihood and WT contextual features, not calibrated functional predictions",
            "context": "Mutation-centred 1022 aa windows; full sequence for shorter proteins",
            "parameters": sum(p.numel() for p in model.parameters()),
            "parameter_dtype": str(next(model.parameters()).dtype),
        }
        (OUT / f"{name}_{args.model}_resources.json").write_text(
            json.dumps(receipt, indent=2) + "\n"
        )
        print(json.dumps(receipt), flush=True)
        del windows
    print("finished", args.model, flush=True)


if __name__ == "__main__":
    main()
