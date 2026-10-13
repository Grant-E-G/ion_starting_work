"""Refresh all principal comparisons from cached predictions; no physical calculations."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "code/experiments/ompf"


def execute(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=ROOT, check=True)


if __name__ == "__main__":
    execute("dataset.py")
    for extra in [
        [],
        ["--trimer"],
        ["--seed", "1"],
        ["--trimer", "--spacing", "0.075", "--allow-subset"],
    ]:
        execute("benchmark.py", "--compare-only", *extra)
    for directory, tag, trimer, spacing in [
        ("reaction/monomer_h0.15_s3/predictions", "image_monomer_s3", False, "0.15"),
        ("reaction/trimer_h0.15_s3/predictions", "image_trimer_s3", True, "0.15"),
        ("reaction/trimer_h0.1_s3/predictions", "image_trimer_s3", True, "0.1"),
        ("combined/v0.03", "image_volume003", True, "0.15"),
        ("combined/v0.1", "image_volume01", True, "0.15"),
    ]:
        execute(
            "benchmark.py",
            "--compare-only",
            "--directory",
            str(ROOT / "notes/ompf" / directory),
            "--tag",
            tag,
            "--spacing",
            spacing,
            "--allow-subset",
            *(["--trimer"] if trimer else []),
        )
    execute("calibration.py", "--trimer")
    execute(
        "calibration.py",
        "--trimer",
        "--directory",
        str(ROOT / "notes/ompf/reaction/trimer_h0.15_s3/predictions"),
        "--tag",
        "image_trimer_s3",
    )
    execute("salt_consistency.py")
    execute("state_challenge.py")
    execute("state_challenge.py", "--trimer")
    execute("ranking.py")
    execute("summarize.py")
    execute("plots.py")
    execute("decision_plots.py")
