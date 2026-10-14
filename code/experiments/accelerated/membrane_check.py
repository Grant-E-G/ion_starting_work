"""Bounded execution of published JAX membrane-energy placement, without MD."""

from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "sources/accelerated/raw"
OUT = ROOT / "notes/accelerated"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default="/tmp/c5r-mempro/bin/python")
    parser.add_argument("--iterations", type=int, default=150)
    parser.add_argument("--starts", type=int, default=4)
    args = parser.parse_args()
    package = RAW / "mempro"
    package.mkdir(exist_ok=True)
    (package / "__init__.py").write_text("")
    for name in ["MemPrO.py", "martini_v3.itp"]:
        (package / name).write_bytes((RAW / name).read_bytes())
    pdb = ROOT / "sources/predictive/raw/3UG9.pdb"
    source = RAW / "chr_core.pdb"
    source.write_text(
        "".join(
            line
            for line in pdb.read_text().splitlines(keepends=True)
            if line.startswith("ATOM") and line[21] == "A"
        )
        + "END\n"
    )
    output = OUT / f"mempro_{args.starts}_{args.iterations}"
    command = [
        args.python,
        str(RAW / "MemPrO.py"),
        "-f",
        str(source),
        "-o",
        str(output),
        "-itp",
        str(RAW / "martini_v3.itp"),
        "-nc",
        "4",
        "-ng",
        str(args.starts),
        "-ni",
        str(args.iterations),
    ]
    env = dict(os.environ, NUM_CPU="4", MPLCONFIGDIR="/tmp/c5r-mpl")
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            command, env=env, capture_output=True, text=True, timeout=180, check=False
        )
        result = {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired:
        result = {"status": "timeout_180s"}
    result.update(
        seconds=time.perf_counter() - start,
        peak_child_rss_MiB=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        / 1024,
        command=command,
        scope="WT C1C2 monomer placement; no retinal or lipids, implicit neutral planar membrane; no mutant energies or function predictions",
    )
    path = output / "orientation.txt"
    if path.exists():
        result["orientation_output"] = path.read_text()
    (OUT / f"mempro_{args.starts}_{args.iterations}_execution.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
