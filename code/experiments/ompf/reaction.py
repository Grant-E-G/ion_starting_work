"""Unscreened dielectric reaction self-energy: independent geometric diagnostic.

w(r)=0.5 q*[phi_heterogeneous(r)-phi_uniform-water(r)]/(kT), q=e.
No mutant labels or protein charges enter this computation. Uses reuse of AMG
preconditioners for many point sources, with the same zero outer boundaries.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pyamg
from numpy.typing import NDArray
from physics import EPS0, KB, ROOT, Config, E, geometry, laplacian, mesh, neighbors
from scipy import ndimage
from scipy.interpolate import NearestNDInterpolator
from scipy.sparse.linalg import cg


def green_operators(
    eps: np.ndarray, shape: tuple[int, int, int], config: Config
) -> tuple:
    left, right = neighbors(shape)
    h = config.spacing_nm
    boundary: NDArray[np.bool_] = np.zeros(shape, dtype=bool)
    boundary[0, :, :] = boundary[-1, :, :] = True
    boundary[:, 0, :] = boundary[:, -1, :] = True
    boundary[:, :, 0] = boundary[:, :, -1] = True
    interior = ~boundary.ravel()
    mapping: NDArray[np.int64] = np.full(len(eps), -1, dtype=np.int64)
    mapping[interior] = np.arange(interior.sum())
    weight = 2 * eps[left] * eps[right] / (eps[left] + eps[right]) / h**2
    a = laplacian(len(eps), left, right, weight)[interior][:, interior].tocsr()
    aw = laplacian(
        len(eps), left, right, np.full(len(left), config.epsilon_water / h**2)
    )[interior][:, interior].tocsr()
    pre = pyamg.smoothed_aggregation_solver(a, max_coarse=50).aspreconditioner()
    prew = pyamg.smoothed_aggregation_solver(aw, max_coarse=50).aspreconditioner()
    return a, aw, pre, prew, mapping, interior


def sample_reaction(
    eps: np.ndarray, shape: tuple[int, int, int], config: Config, indices: np.ndarray
) -> tuple[np.ndarray, dict]:
    started = time.perf_counter()
    a, aw, pre, prew, mapping, interior = green_operators(eps, shape, config)
    lb = E**2 / (4 * np.pi * EPS0 * KB * config.temperature_K) * 1e9
    source_strength = 4 * np.pi * lb / config.spacing_nm**3
    output = []
    worst = 0.0
    for count, index in enumerate(indices):
        source = np.zeros(interior.sum())
        source[mapping[index]] = source_strength
        x, status = cg(a, source, M=pre, rtol=1e-9, atol=1e-12, maxiter=300)
        xw, statusw = cg(aw, source, M=prew, rtol=1e-9, atol=1e-12, maxiter=300)
        if status or statusw:
            raise RuntimeError(f"Green solve failed {status}/{statusw}")
        worst = max(
            worst, float(np.linalg.norm(a @ x - source) / np.linalg.norm(source))
        )
        reaction = 0.5 * (x[mapping[index]] - xw[mapping[index]])
        if reaction < -1e-6:
            raise ValueError(
                "Negative reaction energy for lower-permittivity inclusions"
            )
        output.append(max(0.0, float(reaction)))
        if count % 100 == 0:
            print(f"Green sources {count+1}/{len(indices)}", flush=True)
    return np.array(output), {
        "samples": len(indices),
        "seconds": time.perf_counter() - started,
        "max_relative_residual": worst,
    }


def calculate(
    variant: str,
    config: Config,
    stride: int = 2,
    output: Path | None = None,
    backend: str = "cpu",
) -> dict:
    data = dict(np.load(ROOT / f"sources/ompf/prepared/{variant}_seed0.npz"))
    points, shape = mesh(config)
    eps, water = geometry(data, points, shape, config)
    # The prescribed local region covers the channel and entrances. Bath correction
    # goes to zero outside it; this is a separately documented approximation.
    apertures = data.get("apertures", np.zeros((1, 2)))
    radial = np.linalg.norm(points[:, None, :2] - apertures[None, :, :], axis=2).min(
        axis=1
    )
    region = water & (radial < 1.65) & (abs(points[:, 2]) < 2.7)
    grid: NDArray[np.bool_] = np.zeros(shape, dtype=bool)
    grid[::stride, ::stride, ::stride] = True
    samples = np.flatnonzero(region & grid.ravel())
    if backend in ("cuda", "cuda32"):
        from reaction_cuda import gpu_reaction

        w, stats = gpu_reaction(
            eps,
            shape,
            config,
            samples,
            precision="float32" if backend == "cuda32" else "float64",
        )
    elif backend == "cpu":
        w, stats = sample_reaction(eps, shape, config, samples)
    else:
        raise ValueError(backend)
    if float(w.min()) < -1e-6:
        raise ValueError("Negative dielectric image energy")
    field = np.zeros(len(points))
    field[region] = NearestNDInterpolator(points[samples], w)(points[region])
    # Smooth one voxel to avoid piecewise-nearest steps; no fitting to measurements.
    field = ndimage.gaussian_filter(field.reshape(shape), sigma=0.65).ravel()
    field[~water] = 0.0
    report = dict(
        variant=variant,
        spacing_nm=config.spacing_nm,
        stride=stride,
        **stats,
        maximum_w_kT=float(field.max()),
        mean_sample_w_kT=float(w.mean()),
        approximation="Unscreened monovalent image self-energy; nearest interpolation and 0.65-voxel smoothing; truncated local region r<1.65nm, |z|<2.7nm",
    )
    if output:
        output.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            output / f"{variant}_h{config.spacing_nm}_s{stride}.npz",
            self_energy=field,
            shape=shape,
            points=points[samples],
            samples=w,
        )
        (output / f"{variant}_h{config.spacing_nm}_s{stride}.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", default="WT")
    p.add_argument("--stride", type=int, default=2)
    p.add_argument("--trimer", action="store_true")
    args = p.parse_args()
    variant = args.variant + ("_trimer" if args.trimer else "")
    print(
        json.dumps(
            calculate(
                variant,
                Config(half_xy_nm=5.25 if args.trimer else 3.15),
                args.stride,
                ROOT / "notes/ompf/reaction",
            ),
            indent=2,
        )
    )
