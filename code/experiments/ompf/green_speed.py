"""Measure Green-function throughput on identical geometry and source locations."""

from __future__ import annotations

import argparse
import json
import os

import numpy as np
from physics import ROOT, Config, geometry, mesh
from reaction import sample_reaction

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--tag", required=True)
    args = p.parse_args()
    c = Config()
    data = dict(np.load(ROOT / "sources/ompf/prepared/WT_seed0.npz"))
    points, shape = mesh(c)
    eps, water = geometry(data, points, shape, c)
    candidates = np.flatnonzero(
        water
        & (abs(points[:, 2]) < 1.2)
        & (np.linalg.norm(points[:, :2], axis=1) < 1.1)
    )
    indices = candidates[np.linspace(0, len(candidates) - 1, 12, dtype=int)]
    energies, stats = sample_reaction(eps, shape, c, indices)
    result = dict(
        tag=args.tag,
        blas_threads=os.environ.get("OPENBLAS_NUM_THREADS"),
        **stats,
        energies=energies.tolist(),
        source_indices=indices.tolist(),
    )
    (ROOT / f"notes/ompf/reaction/speed_{args.tag}.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))
