"""Local GPU feasibility benchmark, not a validated functional predictor."""

import argparse
import csv
import hashlib
import importlib
import json
import platform
import statistics
import time
from pathlib import Path

import torch
from huggingface_hub import model_info
from peft import LoraConfig, inject_adapter_in_model
from transformers import AutoModel, AutoModelForMaskedLM, AutoTokenizer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("output", type=Path)
    parser.add_argument("--revision")
    parser.add_argument(
        "--precision", choices=["bfloat16", "float32"], default="bfloat16"
    )
    parser.add_argument("--panel-only", action="store_true")
    parser.add_argument("--no-training", action="store_true")
    args = parser.parse_args()
    assert torch.cuda.is_available(), "CUDA is required for this benchmark"
    torch.manual_seed(17)
    torch.set_num_threads(4)
    sequence = "".join(
        line.strip()
        for line in Path("sources/gtacr2_reference.fasta").read_text().splitlines()
        if line.strip() and not line.startswith(">")
    )[:266]
    revision = args.revision or model_info(args.model).sha
    amplify = "AMPLIFY" in args.model
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(
        args.model, revision=revision, trust_remote_code=amplify
    )
    loader = AutoModel if amplify else AutoModelForMaskedLM
    model = (
        loader.from_pretrained(
            args.model,
            revision=revision,
            trust_remote_code=amplify,
            dtype=getattr(torch, args.precision),
        )
        .to("cuda")
        .eval()
    )
    if amplify:
        # Upstream's unregistered RoPE table remains on meta after HF loading.
        # Recompute with the exact upstream function, preserving its semantics.
        module = importlib.import_module(type(model).__module__)
        model.freqs_cis = module.precompute_freqs_cis(
            model.config.hidden_size // model.config.num_attention_heads,
            model.config.max_length,
        ).to("cuda")
    torch.cuda.synchronize()
    metadata = {
        "model": args.model,
        "revision": revision,
        "gpu": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "python": platform.python_version(),
        "precision": args.precision,
        "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
        "length": len(sequence),
        "batch_size": 1,
        "load_seconds": time.perf_counter() - started,
        "parameters": sum(p.numel() for p in model.parameters()),
    }
    encoded = tokenizer(sequence, return_tensors="pt")
    ids = encoded["input_ids"].to("cuda")
    assert ids.shape[1] == len(sequence) + 2
    assert tokenizer.convert_ids_to_tokens(ids[0, 1:-1].tolist()) == list(sequence)

    def forward(masked: torch.Tensor) -> torch.Tensor:
        # No padding: AMPLIFY expects additive masks rather than tokenizer masks.
        return model(input_ids=masked).logits

    masked = ids.clone()
    masked[0, 159] = tokenizer.mask_token_id
    with torch.inference_mode():
        forward(masked)
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        times = []
        for _ in range(10):
            tick = time.perf_counter()
            forward(masked)
            torch.cuda.synchronize()
            times.append(time.perf_counter() - tick)
        metadata["forward_median_seconds"] = statistics.median(times)
        metadata["forward_min_seconds"] = min(times)
        metadata["inference_peak_allocated_gib"] = (
            torch.cuda.max_memory_allocated() / 2**30
        )
        metadata["inference_peak_reserved_gib"] = (
            torch.cuda.max_memory_reserved() / 2**30
        )
        rows = []
        tick = time.perf_counter()
        positions = (
            [9, 56, 64, 159, 219, 230]
            if args.panel_only
            else range(1, len(sequence) + 1)
        )
        for position in positions:
            masked = ids.clone()
            masked[0, position] = tokenizer.mask_token_id
            logits = forward(masked)[0, position].float().cpu()
            wild = sequence[position - 1]
            for aa in "ACDEFGHIKLMNPQRSTVWY":
                if aa != wild:
                    rows.append(
                        {
                            "variant": f"{wild}{position}{aa}",
                            "masked_log_odds": float(
                                logits[tokenizer.convert_tokens_to_ids(aa)]
                                - logits[tokenizer.convert_tokens_to_ids(wild)]
                            ),
                        }
                    )
        torch.cuda.synchronize()
        metadata["scan_seconds"] = time.perf_counter() - tick
        metadata["scored_variants"] = len(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.with_suffix(".csv").open("w") as output:
        writer = csv.DictWriter(output, fieldnames=["variant", "masked_log_odds"])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(metadata), flush=True)
    if args.no_training:
        metadata["lora_smoke_status"] = "not requested"
        args.output.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2) + "\n"
        )
        return

    # Synthetic masked-LM optimizer smoke test: establishes hardware fit only.
    # These updates are discarded; they are not phenotype training or validation.
    try:
        targets = [
            name
            for name, module in model.named_modules()
            if isinstance(module, torch.nn.Linear)
            and (
                name.split(".")[-1]
                in {"query", "value", "q", "v", "q_proj", "v_proj", "qkv", "qkv_proj"}
            )
        ]
        assert targets, "No suitable LoRA targets found"
        model = inject_adapter_in_model(
            LoraConfig(r=8, lora_alpha=16, target_modules=targets, lora_dropout=0.0),
            model,
        )
        model.train()
        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad], lr=1e-4
        )
        metadata["lora_trainable_parameters"] = sum(
            p.numel() for p in model.parameters() if p.requires_grad
        )
        metadata["lora_target_modules"] = targets
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        losses, durations = [], []
        for _ in range(3):
            optimizer.zero_grad(set_to_none=True)
            masked = ids.clone()
            masked[0, 159] = tokenizer.mask_token_id
            torch.cuda.synchronize()
            tick = time.perf_counter()
            logits = forward(masked)[0, 159].float()
            loss = torch.nn.functional.cross_entropy(
                logits.unsqueeze(0), ids[0, 159].reshape(1)
            )
            loss.backward()
            optimizer.step()
            torch.cuda.synchronize()
            durations.append(time.perf_counter() - tick)
            losses.append(float(loss.detach()))
        metadata["lora_step_seconds"] = durations
        metadata["lora_smoke_losses"] = losses
        metadata["lora_peak_allocated_gib"] = torch.cuda.max_memory_allocated() / 2**30
        metadata["lora_peak_reserved_gib"] = torch.cuda.max_memory_reserved() / 2**30
        metadata["lora_smoke_status"] = "passed; discarded synthetic updates"
    except Exception as error:
        metadata["lora_smoke_status"] = f"{type(error).__name__}: {error}"
    args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
