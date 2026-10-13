"""Finite-volume 3D electrostatics with equilibrium linear-response ion transport.

Coordinates nm, charges elementary-charge units, potential e*phi/(k_B*T).
Transport is reduced frozen-background Smoluchowski, not full self-consistent PNP.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pyamg
from numpy.typing import NDArray
from scipy import ndimage, sparse
from scipy.sparse.linalg import cg
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[3]
E = 1.602176634e-19
KB = 1.380649e-23
EPS0 = 8.8541878128e-12
AVOGADRO = 6.02214076e23


@dataclass(frozen=True)
class Config:
    spacing_nm: float = 0.15
    half_xy_nm: float = 3.15
    half_z_nm: float = 4.05
    membrane_half_nm: float = 1.5
    aperture_radius_nm: float = 1.35
    ion_radius_nm: float = 0.10
    epsilon_protein: float = 4.0
    epsilon_membrane: float = 2.0
    epsilon_water: float = 78.5
    temperature_K: float = 298.15
    concentration_M: float = 1.0
    ion_volume_nm3: float = 0.0
    electrostatics: str = "linear_pb"
    tolerance: float = 1e-8


def mesh(config: Config) -> tuple[np.ndarray, tuple[int, int, int]]:
    axes = [
        np.linspace(-r, r, round(2 * r / config.spacing_nm) + 1)
        for r in (config.half_xy_nm, config.half_xy_nm, config.half_z_nm)
    ]
    # Require exact specified spacing, rather than silently changing it per axis.
    for a in axes:
        assert np.allclose(np.diff(a), config.spacing_nm)
    grids = np.meshgrid(*axes, indexing="ij")
    return np.stack(grids, axis=-1).reshape(-1, 3), grids[0].shape


def neighbors(shape: tuple[int, int, int]) -> tuple[np.ndarray, np.ndarray]:
    ids = np.arange(np.prod(shape)).reshape(shape)
    left = []
    right = []
    for axis in range(3):
        low = [slice(None)] * 3
        high = [slice(None)] * 3
        low[axis] = slice(None, -1)
        high[axis] = slice(1, None)
        left.append(ids[tuple(low)].ravel())
        right.append(ids[tuple(high)].ravel())
    return np.concatenate(left), np.concatenate(right)


def laplacian(
    n: int, left: np.ndarray, right: np.ndarray, weight: np.ndarray
) -> sparse.csr_matrix:
    diag = np.bincount(
        np.concatenate([left, right]),
        weights=np.concatenate([weight, weight]),
        minlength=n,
    )
    return sparse.coo_matrix(
        (
            np.concatenate([diag, -weight, -weight]),
            (
                np.concatenate([np.arange(n), left, right]),
                np.concatenate([np.arange(n), right, left]),
            ),
        ),
        shape=(n, n),
    ).tocsr()


def solve_spd(
    a: sparse.csr_matrix, b: np.ndarray, tol: float
) -> tuple[np.ndarray, dict]:
    start = time.perf_counter()
    count = 0

    def callback(_: np.ndarray) -> None:
        nonlocal count
        count += 1

    ml = pyamg.smoothed_aggregation_solver(a, max_coarse=50, symmetry="symmetric")
    x, info = cg(
        a,
        b,
        M=ml.aspreconditioner(),
        rtol=tol,
        atol=1e-12,
        maxiter=1000,
        callback=callback,
    )
    residual = float(np.linalg.norm(a @ x - b) / max(float(np.linalg.norm(b)), 1e-30))
    if info != 0:
        raise RuntimeError(f"CG failed: info={info} residual={residual}")
    return x, {
        "iterations": count,
        "relative_residual": residual,
        "seconds": time.perf_counter() - start,
    }


def deposit_charges(
    xyz: np.ndarray,
    charges: np.ndarray,
    points: np.ndarray,
    shape: tuple[int, int, int],
    h: float,
) -> np.ndarray:
    fractional = (xyz - points[0]) / h
    lower = np.floor(fractional).astype(int)
    remainder = fractional - lower
    rho = np.zeros(np.prod(shape))
    for corner in np.ndindex(2, 2, 2):
        index = lower + np.array(corner)
        valid = np.all((index >= 0) & (index < np.array(shape)), axis=1)
        if not valid.all():
            raise ValueError("Atomic charge outside simulation box")
        w = np.prod(np.where(np.array(corner), remainder, 1 - remainder), axis=1)
        np.add.at(rho, np.ravel_multi_index(index.T, shape), charges * w / h**3)
    assert np.isclose(rho.sum() * h**3, charges.sum(), atol=1e-10)
    return rho


def geometry(
    data: dict, points: np.ndarray, shape: tuple[int, int, int], config: Config
) -> tuple[np.ndarray, np.ndarray]:
    heavy = data["heavy"]
    xyz = data["xyz"][heavy]
    radii = data["radii"][heavy]
    distance, index = cKDTree(xyz).query(
        points, k=list(range(1, min(8, len(xyz)) + 1)), workers=4
    )
    surface = (distance - radii[index]).min(axis=1)
    protein = surface < 0
    membrane = (np.abs(points[:, 2]) < config.membrane_half_nm) & (
        np.linalg.norm(
            points[:, None, :2] - data.get("apertures", np.zeros((1, 2)))[None, :, :],
            axis=2,
        ).min(axis=1)
        >= config.aperture_radius_nm
    )
    eps = np.full(len(points), config.epsilon_water)
    eps[membrane] = config.epsilon_membrane
    eps[protein] = config.epsilon_protein
    water = (surface >= config.ion_radius_nm) & ~membrane
    # A connected component must touch both reservoirs; otherwise it cannot conduct.
    labels, _num = ndimage.label(water.reshape(shape))
    spanning = np.intersect1d(np.unique(labels[:, :, 0]), np.unique(labels[:, :, -1]))
    spanning = spanning[spanning != 0]
    water = np.isin(labels, spanning).ravel()
    return eps, water


def screening_response(
    u: np.ndarray, nu: float, self_energy: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Consistent lattice-gas response including a fixed dielectric-image potential."""
    if not 0 <= nu < 1:
        raise ValueError("Bulk lattice occupancy must be <1")
    clipped = np.clip(u, -30, 30)
    sinh = np.sinh(clipped)
    cosh = np.cosh(clipped)
    penalty = np.exp(-self_energy) if self_energy is not None else np.ones_like(u)
    denominator = 1 - nu + nu * penalty * cosh
    return (
        penalty * sinh / denominator,
        penalty * ((1 - nu) * cosh + nu * penalty) / denominator**2,
    )


def ion_density_factor(
    u: np.ndarray, valence: int, config: Config, self_energy: np.ndarray | None = None
) -> np.ndarray:
    density = config.concentration_M * AVOGADRO / 1e24
    nu = 2 * density * config.ion_volume_nm3
    if not 0 <= nu < 1:
        raise ValueError("Bulk lattice occupancy must be <1")
    penalty = np.exp(-self_energy) if self_energy is not None else np.ones_like(u)
    return penalty * np.exp(-valence * u) / (1 - nu + nu * penalty * np.cosh(u))


def electrostatic(
    data: dict,
    points: np.ndarray,
    shape: tuple[int, int, int],
    eps: np.ndarray,
    water: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
    config: Config,
    self_energy: np.ndarray | None = None,
) -> tuple[np.ndarray, dict]:
    h = config.spacing_nm
    lb_vac = E**2 / (4 * np.pi * EPS0 * KB * config.temperature_K) * 1e9
    density = config.concentration_M * AVOGADRO / 1e24
    kappa2 = 8 * np.pi * (lb_vac / config.epsilon_water) * density
    nu = 2 * density * config.ion_volume_nm3
    weights = (2 * eps[left] * eps[right] / (eps[left] + eps[right])) / h**2
    operator = laplacian(len(points), left, right, weights)
    screen = config.epsilon_water * kappa2 * water
    rho = deposit_charges(data["xyz"], data["charges"], points, shape, h)
    rhs = 4 * np.pi * lb_vac * rho
    boundary: NDArray[np.bool_] = np.zeros(shape, dtype=bool)
    for axis in range(3):
        sl: list[slice | int] = [slice(None)] * 3
        for side in [0, -1]:
            sl[axis] = side
            boundary[tuple(sl)] = True
    interior = ~boundary.ravel()
    a = operator[interior][:, interior].tocsr()
    wi = self_energy[interior] if self_energy is not None else None
    lin = a + sparse.diags(
        screen[interior] * (np.exp(-wi) if wi is not None else 1), format="csr"
    )
    potential = np.zeros(len(points))
    stats: dict[str, Any] = {}
    if config.electrostatics == "linear_pb":
        if config.ion_volume_nm3:
            raise ValueError("Steric correction requires nonlinear PB")
        potential[interior], stats = solve_spd(lin, rhs[interior], config.tolerance)
    elif config.electrostatics == "nonlinear_pb":
        u = np.zeros(interior.sum())
        b = rhs[interior]
        s = screen[interior]
        for step in range(60):
            sinh, cosh = screening_response(u, nu, wi)
            residual = a @ u + s * sinh - b
            norm = np.linalg.norm(residual) / max(float(np.linalg.norm(b)), 1e-30)
            if norm < 1e-7:
                break
            update, _inner = solve_spd(
                a + sparse.diags(s * cosh, format="csr"), -residual, config.tolerance
            )
            # Backtracking on nonlinear residual; no label-dependent choices.
            factor = 1.0
            while factor > 1e-6:
                candidate = u + factor * update
                trial = a @ candidate + s * screening_response(candidate, nu, wi)[0] - b
                if np.linalg.norm(trial) < np.linalg.norm(residual):
                    break
                factor *= 0.5
            u = candidate
        else:
            raise RuntimeError("Nonlinear PB did not converge")
        potential[interior] = u
        stats = {"newton_steps": step, "relative_residual": float(norm)}
    else:
        raise ValueError(config.electrostatics)
    response = (
        potential * (np.exp(-self_energy) if self_energy is not None else 1)
        if config.electrostatics == "linear_pb"
        else screening_response(potential, nu, self_energy)[0]
    )
    fixed_charge = float(rho.sum() * h**3)
    mobile_charge = -float(np.sum(screen * response) * h**3 / (4 * np.pi * lb_vac))
    outward_flux = -float(
        np.sum((operator @ potential)[boundary.ravel()]) * h**3 / (4 * np.pi * lb_vac)
    )
    stats.update(
        mobile_charge_e=mobile_charge,
        outward_electric_flux_equivalent_e=outward_flux,
        gauss_law_relative_error=abs(outward_flux - fixed_charge - mobile_charge)
        / max(abs(fixed_charge), 1.0),
    )
    stats.update(
        charge_e=float(rho.sum() * h**3),
        max_abs_water_potential_kT=float(np.max(np.abs(potential[water]))),
        debye_length_nm=float(1 / np.sqrt(kappa2)),
        max_potential_all_kT=float(np.abs(potential).max()),
    )
    return potential, stats


def transport(
    potential: np.ndarray,
    water: np.ndarray,
    shape: tuple[int, int, int],
    left: np.ndarray,
    right: np.ndarray,
    config: Config,
    valence: int,
    diffusion_nm2_s: float,
    self_energy: np.ndarray | None = None,
) -> tuple[float, dict]:
    if not water.any():
        return 0.0, {
            "iterations": 0,
            "relative_residual": 0.0,
            "seconds": 0.0,
            "flux_plane_spread_relative": 0.0,
            "dimensionless_flux": 0.0,
            "min_response": 0.0,
            "max_response": 0.0,
            "water_nodes": 0,
        }
    # Symmetric edge permeability from arithmetic mean potential, a midpoint approximation.
    edge = water[left] & water[right]
    l = left[edge]
    r = right[edge]
    expo = -valence * 0.5 * (potential[l] + potential[r])
    if np.abs(expo).max() > 30:
        raise ValueError("Potential outside representable dilute-ion regime (>30 kT)")
    if abs(valence) != 1:
        raise ValueError("This prototype supports monovalent ions only")
    weight = np.sqrt(
        ion_density_factor(
            potential[l],
            valence,
            config,
            self_energy[l] if self_energy is not None else None,
        )
        * ion_density_factor(
            potential[r],
            valence,
            config,
            self_energy[r] if self_energy is not None else None,
        )
    )
    mapping: NDArray[np.int64] = np.full(len(water), -1, dtype=np.int64)
    mapping[water] = np.arange(water.sum())
    lm = mapping[l]
    rm = mapping[r]
    a = laplacian(int(water.sum()), lm, rm, weight)
    gridids = np.arange(len(water)).reshape(shape)
    low = gridids[:, :, 0].ravel()
    high = gridids[:, :, -1].ravel()
    fixed = np.zeros(water.sum(), dtype=bool)
    v = np.zeros(water.sum())
    fixed[mapping[low[water[low]]]] = True
    fixed[mapping[high[water[high]]]] = True
    v[mapping[high[water[high]]]] = 1.0
    free = ~fixed
    b = -(a @ v)[free]
    zl = l % shape[2]
    zr = r % shape[2]
    zedge = zr == zl + 1
    tolerance = config.tolerance
    for refinement in range(4):
        v[free], stats = solve_spd(a[free][:, free].tocsr(), b, tolerance)
        differences = v[rm] - v[lm]
        currents = weight * differences
        planes = np.bincount(zl[zedge], weights=currents[zedge], minlength=shape[2] - 1)
        flux = float(planes.mean())
        relative_spread = float(np.ptp(planes) / max(abs(flux), 1e-30))
        energy_flux = float(np.sum(weight * differences**2))
        energy_disagreement = abs(energy_flux - flux) / max(abs(flux), 1e-30)
        if max(relative_spread, energy_disagreement) < 1e-4:
            break
        tolerance *= 0.01
    else:
        raise RuntimeError(
            f"Flux conservation failed: spread={relative_spread}, energy disagreement={energy_disagreement}"
        )
    stats.update(
        conservation_refinements=refinement,
        final_cg_tolerance=tolerance,
        energy_flux_disagreement_relative=energy_disagreement,
    )
    density = config.concentration_M * AVOGADRO / 1e24
    # (e^2/kT) [C/V] * D [nm^2/s] * n [nm^-3] * h [nm] -> Siemens.
    conductance = (
        E**2
        / (KB * config.temperature_K)
        * diffusion_nm2_s
        * density
        * config.spacing_nm
        * flux
        * 1e9
    )
    stats.update(
        flux_plane_spread_relative=relative_spread,
        dimensionless_flux=flux,
        min_response=float(v.min()),
        max_response=float(v.max()),
        water_nodes=int(water.sum()),
    )
    return float(conductance), stats


def run(
    variant: str,
    config: Config,
    seed: int = 0,
    output: Path | None = None,
    self_energy_file: Path | None = None,
) -> dict:
    start = time.perf_counter()
    input_file = ROOT / f"sources/ompf/prepared/{variant}_seed{seed}.npz"
    data = dict(np.load(input_file))
    points, shape = mesh(config)
    left, right = neighbors(shape)
    eps, water = geometry(data, points, shape, config)
    self_energy = np.load(self_energy_file)["self_energy"] if self_energy_file else None
    if self_energy is not None and self_energy.shape != water.shape:
        raise ValueError("Image map grid does not match transport grid")
    if not water.any():
        raise RuntimeError("Pore disconnected on this grid")
    potential, pbstats = electrostatic(
        data, points, shape, eps, water, left, right, config, self_energy
    )
    predictions = {}
    transport_stats: dict[str, Any] = {}
    # Infinite-dilution diffusion values at 298 K: approximation at 1M, WT scale calibrated later.
    for salt, dplus in [("KCl", 1.96e9), ("NaCl", 1.33e9)]:
        if salt == "KCl":
            plus, sp = transport(
                potential, water, shape, left, right, config, +1, 1.0, self_energy
            )
            minus, sm = transport(
                potential, water, shape, left, right, config, -1, 1.0, self_energy
            )
            zero, sg = transport(
                np.zeros_like(potential), water, shape, left, right, config, +1, 1.0
            )
            transport_stats = {"cation": sp, "anion": sm, "geometry": sg}
        predictions[salt] = {
            "physics_nS": plus * dplus + minus * 2.03e9,
            "geometry_nS": zero * (dplus + 2.03e9),
            "cation_nS": plus * dplus,
            "anion_nS": minus * 2.03e9,
        }
    water_image = self_energy[water] if self_energy is not None else None
    result = {
        "variant": variant,
        "seed": seed,
        "prepared_input": str(input_file.relative_to(ROOT)),
        "prepared_sha256": hashlib.sha256(input_file.read_bytes()).hexdigest(),
        "self_energy_source": (
            str(self_energy_file.resolve().relative_to(ROOT))
            if self_energy_file and self_energy_file.resolve().is_relative_to(ROOT)
            else str(self_energy_file) if self_energy_file else None
        ),
        "config": asdict(config),
        "shape": shape,
        "grid_nodes": len(points),
        "electrostatics": pbstats,
        "transport": transport_stats,
        "predictions": predictions,
        "density_diagnostics": {
            "maximum_implied_ion_molarity": float(
                config.concentration_M
                * max(
                    float(
                        (
                            ion_density_factor(potential[water], 1, config, water_image)
                        ).max()
                    ),
                    float(
                        (
                            ion_density_factor(
                                potential[water], -1, config, water_image
                            )
                        ).max()
                    ),
                )
            ),
            "note": "Local mean-field density diagnostic, not experimental ion occupancy",
        },
        "seconds": time.perf_counter() - start,
        "process_peak_RSS_MiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        / 1024,
        "model_unit": (
            "full trimer"
            if variant.endswith("_trimer")
            else "one monomer; multiply by three for a trimer; intermonomer fields omitted"
        ),
    }
    if output:
        output.mkdir(parents=True, exist_ok=True)
        stem = f"{variant}_c{config.concentration_M}_h{config.spacing_nm}_{config.electrostatics}_seed{seed}"
        (output / f"{stem}.json").write_text(json.dumps(result, indent=2) + "\n")
        np.savez_compressed(
            output / f"{stem}_field.npz",
            potential=potential.reshape(shape),
            water=water.reshape(shape),
            epsilon=eps.reshape(shape),
        )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--variant", default="WT")
    p.add_argument("--concentration", type=float, default=1.0)
    p.add_argument("--spacing", type=float, default=0.15)
    p.add_argument("--nonlinear", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--trimer", action="store_true")
    args = p.parse_args()
    config = Config(
        spacing_nm=args.spacing,
        half_xy_nm=5.25 if args.trimer else 3.15,
        concentration_M=args.concentration,
        electrostatics="nonlinear_pb" if args.nonlinear else "linear_pb",
    )
    print(
        json.dumps(
            run(
                args.variant + ("_trimer" if args.trimer else ""),
                config,
                args.seed,
                ROOT / "notes/ompf/results",
            ),
            indent=2,
        )
    )
