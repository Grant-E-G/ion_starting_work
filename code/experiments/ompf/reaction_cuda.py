"""Batched CUDA conjugate gradients for the same dielectric Green operators.

Numerical backend experiment, not a new physics model. Float64, diagonal
preconditioning, explicit residual checks, and CPU-reference comparison.
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import torch
from numpy.typing import NDArray
from physics import EPS0, KB, ROOT, Config, E, geometry, laplacian, mesh, neighbors
from scipy import sparse


def torch_csr(
    matrix: sparse.csr_matrix, dtype: torch.dtype = torch.float64
) -> torch.Tensor:
    return torch.sparse_csr_tensor(
        torch.tensor(matrix.indptr, dtype=torch.int64, device="cuda"),
        torch.tensor(matrix.indices, dtype=torch.int64, device="cuda"),
        torch.tensor(matrix.data, dtype=dtype, device="cuda"),
        size=matrix.shape,
    )


def batched_cg(
    a: torch.Tensor,
    diagonal: torch.Tensor,
    indices: np.ndarray,
    strength: float,
    tolerance: float = 1e-9,
) -> tuple[np.ndarray, dict]:
    n = a.shape[0]
    k = len(indices)
    source = torch.zeros((n, k), dtype=a.dtype, device="cuda")
    idx = torch.tensor(indices, dtype=torch.int64, device="cuda")
    columns = torch.arange(k, device="cuda")
    source[idx, columns] = strength
    x = torch.zeros_like(source)
    r = source.clone()
    z = r / diagonal[:, None]
    p = z.clone()
    rz = (r * z).sum(dim=0)
    for iteration in range(1200):
        ap = torch.sparse.mm(a, p)
        denom = (p * ap).sum(dim=0)
        alpha = torch.where(denom.abs() > 1e-100, rz / denom, torch.zeros_like(rz))
        x += p * alpha[None, :]
        r -= ap * alpha[None, :]
        if iteration % 10 == 0:
            residual = torch.linalg.vector_norm(r, dim=0) / strength
            if float(residual.max()) < tolerance:
                break
        z = r / diagonal[:, None]
        rznew = (r * z).sum(dim=0)
        beta = torch.where(rz.abs() > 1e-100, rznew / rz, torch.zeros_like(rz))
        p = z + p * beta[None, :]
        rz = rznew
    else:
        raise RuntimeError("CUDA CG did not converge")
    actual = torch.linalg.vector_norm(torch.sparse.mm(a, x) - source, dim=0) / strength
    if float(actual.max()) > tolerance * 10:
        raise RuntimeError(f"CUDA CG true residual failed {float(actual.max())}")
    value = x[idx, columns].cpu().numpy()
    return value, {
        "iterations": iteration + 1,
        "max_true_relative_residual": float(actual.max()),
    }


def gpu_reaction(
    eps: np.ndarray,
    shape: tuple[int, int, int],
    config: Config,
    indices: np.ndarray,
    batch_size: int = 32,
    precision: str = "float64",
) -> tuple[np.ndarray, dict]:
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    left, right = neighbors(shape)
    h = config.spacing_nm
    boundary: NDArray[np.bool_] = np.zeros(shape, dtype=bool)
    boundary[0, :, :] = boundary[-1, :, :] = True
    boundary[:, 0, :] = boundary[:, -1, :] = True
    boundary[:, :, 0] = boundary[:, :, -1] = True
    inside = ~boundary.ravel()
    mapping: NDArray[np.int64] = np.full(len(eps), -1, dtype=np.int64)
    mapping[inside] = np.arange(inside.sum())
    weight = 2 * eps[left] * eps[right] / (eps[left] + eps[right]) / h**2
    a = laplacian(len(eps), left, right, weight)[inside][:, inside].tocsr()
    aw = laplacian(
        len(eps), left, right, np.full(len(left), config.epsilon_water / h**2)
    )[inside][:, inside].tocsr()
    dtype = torch.float64 if precision == "float64" else torch.float32
    ga = torch_csr(a, dtype)
    gw = torch_csr(aw, dtype)
    diag = torch.tensor(a.diagonal(), dtype=dtype, device="cuda")
    diagw = torch.tensor(aw.diagonal(), dtype=dtype, device="cuda")
    lb = E**2 / (4 * np.pi * EPS0 * KB * config.temperature_K) * 1e9
    strength = 4 * np.pi * lb / h**3
    output = []
    stats = []
    tolerance = 1e-9 if precision == "float64" else 1e-5
    for offset in range(0, len(indices), batch_size):
        batch = mapping[indices[offset : offset + batch_size]]
        x, s = batched_cg(ga, diag, batch, strength, tolerance)
        xw, sw = batched_cg(gw, diagw, batch, strength, tolerance)
        output.append(0.5 * (x - xw))
        stats.append({"heterogeneous": s, "water": sw})
        print(
            f"CUDA Green sources {min(offset+batch_size,len(indices))}/{len(indices)}",
            flush=True,
        )
    torch.cuda.synchronize()
    report = {
        "samples": len(indices),
        "seconds": time.perf_counter() - start,
        "batch_size": batch_size,
        "GPU_peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
        "GPU_peak_reserved_MiB": torch.cuda.max_memory_reserved() / 2**20,
        "dtype": precision,
        "torch_version": torch.__version__,
        "device": torch.cuda.get_device_name(),
        "batches": stats,
    }
    return np.concatenate(output), report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--batch", type=int, default=12)
    p.add_argument("--precision", choices=["float64", "float32"], default="float64")
    args = p.parse_args()
    reference = json.loads(
        (ROOT / "notes/ompf/reaction/speed_one_thread.json").read_text()
    )
    config = Config()
    data = dict(np.load(ROOT / "sources/ompf/prepared/WT_seed0.npz"))
    points, shape = mesh(config)
    eps, _water = geometry(data, points, shape, config)
    energy, stats = gpu_reaction(
        eps,
        shape,
        config,
        np.array(reference["source_indices"]),
        args.batch,
        precision=args.precision,
    )
    delta = np.abs(energy - np.array(reference["energies"]))
    stats.update(
        max_absolute_CPU_difference_kT=float(delta.max()),
        energies=energy.tolist(),
        CPU_seconds=reference["seconds"],
        comparison_scope="Identical 12 WT point sources; small backend benchmark, not whole design-loop throughput",
    )
    (
        ROOT / f"notes/ompf/reaction/cuda_reference_check_{args.precision}.json"
    ).write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))
    if delta.max() > (1e-5 if args.precision == "float64" else 1e-3):
        raise AssertionError("CUDA/CPU Green energies disagree")
