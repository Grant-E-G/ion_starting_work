"""Verify cached ESM-1v inference on CUDA against identical CPU inputs."""

from __future__ import annotations

import json
import time
from pathlib import Path

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA unavailable: run outside the device-hiding sandbox with a CUDA "
            "PyTorch build; see root AGENTS.md."
        )
    torch.set_num_threads(4)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    meta = json.loads((ROOT / "sources/accelerated/esm1v_model.json").read_text())
    # Deposited structure sequence: a hardware test, not a functional benchmark.
    lines = (ROOT / "sources/accelerated/raw/5ZIH.fasta").read_text().splitlines()
    sequence = "".join(line.strip() for line in lines[1:] if not line.startswith(">"))
    tokenizer = AutoTokenizer.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    )
    model = AutoModelForMaskedLM.from_pretrained(
        meta["name"], revision=meta["revision"], local_files_only=True
    ).eval()
    encoded = tokenizer(sequence, return_tensors="pt")
    sites = torch.linspace(1, len(sequence), 13).long().tolist()
    inputs = []
    for site in sites:
        item = {key: value.clone() for key, value in encoded.items()}
        item["input_ids"][0, site] = tokenizer.mask_token_id
        inputs.append(item)

    def run(device: str) -> tuple[torch.Tensor, float]:
        prepared = [{key: value.to(device) for key, value in x.items()} for x in inputs]
        if device == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            outputs = [
                model(**item).logits[0, site].detach()
                for item, site in zip(prepared, sites, strict=True)
            ]
        if device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        return torch.stack(outputs).cpu(), elapsed

    cpu, cpu_seconds = run("cpu")
    model.to("cuda")
    with torch.inference_mode():
        model(**{key: value.to("cuda") for key, value in inputs[0].items()})
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    gpu, gpu_seconds = run("cuda")
    repeat, repeat_seconds = run("cuda")
    assert torch.isfinite(gpu).all(), "Nonfinite model logits"
    torch.testing.assert_close(cpu, gpu, atol=1e-3, rtol=1e-4)
    torch.testing.assert_close(gpu, repeat, atol=1e-5, rtol=1e-5)
    receipt = {
        "scope": "Hardware/numerical smoke test; no functional prediction claim",
        "model": meta,
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        "device_total_MiB": torch.cuda.get_device_properties(0).total_memory / 2**20,
        "parameters": sum(p.numel() for p in model.parameters()),
        "sequence_source": "sources/accelerated/raw/5ZIH.fasta",
        "sequence_length": len(sequence),
        "masked_sites": sites,
        "precision": "float32; TF32 disabled",
        "cpu_threads": 4,
        "cpu_inference_seconds": cpu_seconds,
        "gpu_inference_seconds": gpu_seconds,
        "gpu_repeat_seconds": repeat_seconds,
        "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
        "peak_reserved_MiB": torch.cuda.max_memory_reserved() / 2**20,
        "cpu_gpu_max_abs_logit_difference": (cpu - gpu).abs().max().item(),
        "gpu_repeat_max_abs_logit_difference": (gpu - repeat).abs().max().item(),
        "timing_excludes": "Download, model loading, transfer to GPU, initial warmup",
    }
    destination = ROOT / "notes/accelerated/gpu_verification.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
