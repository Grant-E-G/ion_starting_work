"""Measure preparation wall time and whole-device memory, without claiming per-process VRAM."""

from __future__ import annotations

import json
import resource
import subprocess
import threading
import time

from physics import ROOT
from prepare import prepare


def gpu_snapshot() -> dict:
    fields = ["name", "memory.total", "memory.used", "utilization.gpu", "power.draw"]
    text = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=" + ",".join(fields),
            "--format=csv,noheader,nounits",
        ],
        text=True,
    )
    row = text.strip().split(", ")
    return dict(zip(fields, row))


if __name__ == "__main__":
    before = gpu_snapshot()
    samples: list[dict[str, str]] = []
    stop = threading.Event()

    def sample() -> None:
        while not stop.wait(0.1):
            samples.append(gpu_snapshot())

    thread = threading.Thread(target=sample)
    thread.start()
    started = time.perf_counter()
    try:
        result = prepare("EAE_resource_trimer", "R42E/R82A/R132E", trimer=True)
    finally:
        stop.set()
        thread.join()
    report = {
        "preparation": result,
        "wall_seconds": time.perf_counter() - started,
        "host_process_peak_RSS_MiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        / 1024,
        "before": before,
        "samples": samples,
        "whole_gpu_peak_used_MiB": max(float(s["memory.used"]) for s in samples),
        "note": "Whole-device memory includes display/other processes. Sampling may miss brief peaks. No MD trajectory benchmark.",
    }
    (ROOT / "notes/ompf/resource_preparation.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
