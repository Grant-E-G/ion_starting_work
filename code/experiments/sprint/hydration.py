"""Bounded static BK pore-hydration limiting-case check using a published grid.

Published CHAP heuristic grid/scoring; approximate deterministic pore profiles,
not a claim to execute the unavailable CHAP C++ pathway extractor. No MD.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from data import OUT, RAW
from scipy.optimize import minimize
from scipy.spatial.distance import cdist

RADII = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80}


def profile(
    identifier: str, source: Path | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    structure = PDBParser(QUIET=True).get_structure(
        identifier, (source if source is not None else RAW / f"{identifier}.pdb")
    )[0]
    chains = [structure[c] for c in "ABCD"]
    centers = {
        site: np.mean([chain[(" ", site, " ")]["CA"].coord for chain in chains], axis=0)
        for site in [298, 310, 316, 320]
    }
    origin = centers[316]
    axis = centers[298] - origin
    axis /= np.linalg.norm(axis)
    reference = np.array([1.0, 0, 0]) if abs(axis[0]) < 0.9 else np.array([0, 1.0, 0])
    first = np.cross(axis, reference)
    first /= np.linalg.norm(first)
    second = np.cross(axis, first)
    basis = np.stack([first, second, axis], axis=1)
    xyz, radii = [], []
    for chain in chains:
        for atom in chain.get_atoms():
            if atom.element in RADII and atom.get_parent().id[0] == " ":
                projected = (atom.coord - origin) @ basis
                if np.linalg.norm(projected[:2]) < 25 and abs(projected[2]) < 35:
                    xyz.append(projected)
                    radii.append(RADII[atom.element])
    coordinates, vdw = np.array(xyz), np.array(radii)
    end_points = sorted([float((centers[site] - origin) @ axis) for site in [310, 320]])
    positions = np.linspace(end_points[0], end_points[1], 51)
    paths = []
    for z in positions:

        def objective(xy: np.ndarray, z: float = float(z)) -> float:
            point = np.array([xy[0], xy[1], z])
            radius = float(np.min(np.linalg.norm(coordinates - point, axis=1) - vdw))
            return -float(radius)

        solutions = [
            minimize(
                objective,
                np.array(start),
                method="Nelder-Mead",
                bounds=[(-2, 2), (-2, 2)],
                options={"xatol": 1e-4, "fatol": 1e-4, "maxiter": 150},
            )
            for start in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        ]
        best = min(solutions, key=lambda item: item.fun)
        paths.append(
            {
                "z_A": z,
                "x_A": best.x[0],
                "y_A": best.x[1],
                "radius_A": -best.fun,
                "start_radius_range_A": float(np.ptp([-s.fun for s in solutions])),
            }
        )
    values = pd.DataFrame(paths)
    scale = json.loads(
        (RAW / "chap/share/data/hydrophobicity/wimley_white_1996.json").read_text()
    )
    hydrophobicity = {
        row["resname"]: row["hydrophobicity"] for row in scale["hydrophobicity"]
    }
    residues = []
    for chain in chains:
        for residue in chain:
            if (
                residue.id[0] != " "
                or "CA" not in residue
                or residue.resname not in hydrophobicity
            ):
                continue
            ca = (residue["CA"].coord - origin) @ basis
            if not positions.min() - 9 <= ca[2] <= positions.max() + 9:
                continue
            sidechain = [
                a
                for a in residue
                if a.element in RADII and a.name not in ["N", "CA", "C", "O", "OXT"]
            ]
            if not sidechain:
                sidechain = [residue["CA"]]
            side_xyz = np.array([(a.coord - origin) @ basis for a in sidechain])
            radial = np.linalg.norm(side_xyz[:, :2], axis=1).min()
            local_radius = np.interp(ca[2], positions, values.radius_A)
            cb = (residue["CB"].coord - origin) @ basis if "CB" in residue else ca
            inward = (
                float(np.dot(cb[:2] - ca[:2], -ca[:2])) > 0 or residue.resname == "GLY"
            )
            if inward and radial <= local_radius + 5.5:
                residues.append(
                    {
                        "chain": chain.id,
                        "site": residue.id[1],
                        "resname": residue.resname,
                        "z_A": ca[2],
                        "hydrophobicity": hydrophobicity[residue.resname],
                    }
                )
    residues_frame = pd.DataFrame(residues)
    assert len(residues_frame) > 0
    weight = np.exp(
        -0.5 * ((positions[:, None] - residues_frame.z_A.to_numpy()[None]) / 4.5) ** 2
    )
    values["hydrophobicity"] = (
        weight @ residues_frame.hydrophobicity.to_numpy()
    ) / weight.sum(axis=1)
    return values, residues_frame


def main() -> None:
    start = time.perf_counter()
    grid = pd.DataFrame(
        json.loads((RAW / "chap/scripts/heuristic/heuristic_grid.json").read_text())
    )
    coordinates = grid[["hydrophobicity", "radius"]].to_numpy()
    outputs = {}
    for state, identifier in [("closed", "6V3G"), ("open", "6V38")]:
        values, residues = profile(identifier)
        query = np.column_stack([values.hydrophobicity, values.radius_A / 10])
        index = cdist(query, coordinates).argmin(1)
        values["published_grid_energy"] = grid.energy.to_numpy()[index]
        values["outside_grid"] = (
            (query[:, 0] < grid.hydrophobicity.min())
            | (query[:, 0] > grid.hydrophobicity.max())
            | (query[:, 1] < grid.radius.min())
            | (query[:, 1] > grid.radius.max())
        )
        values.to_csv(OUT / f"bk_hydration_{state}_profile.csv", index=False)
        residues.to_csv(OUT / f"bk_hydration_{state}_residues.csv", index=False)
        outputs[state] = {
            "min_radius_A": float(values.radius_A.min()),
            "max_radius_A": float(values.radius_A.max()),
            "hydrophobicity_range": [
                float(values.hydrophobicity.min()),
                float(values.hydrophobicity.max()),
            ],
            "max_tabulated_energy": float(values.published_grid_energy.max()),
            "fraction_above_published_2_6_threshold": float(
                (values.published_grid_energy > 2.6).mean()
            ),
            "fraction_outside_grid": float(values.outside_grid.mean()),
            "max_search_start_radius_difference_A": float(
                values.start_radius_range_A.max()
            ),
            "pore_facing_residues_proxy": len(residues),
            "classification_scope": "Energy-profile threshold diagnostic, NOT the full residue SSD>0.55 classifier",
        }
    result = {
        "states": outputs,
        "seconds": time.perf_counter() - start,
        "grid_domain": {
            key: [float(grid[key].min()), float(grid[key].max())]
            for key in ["hydrophobicity", "radius"]
        },
        "radius_units": "Input Angstrom, divided by10 to published grid nm",
        "energy_threshold": "Source R/Python scripts use2.6, documentation describes approximately1RT; tabulated energy scale, not directly mutant gating energy",
        "assumptions": "Protein-only pore, deterministic planar maximum-inscribed-sphere path, Bondi heavy-atom radii, 4.5A Gaussian hydrophobicity bandwidth, 5.5A lining margin and inward CB orientation",
        "implementation_limit": "GROMACS/Boost/RapidJSON absent; no CHAP C++ extraction was run. Approximate profiles are supplied to the published nearest-grid mapping; no silent extrapolation: outside-domain points explicitly flagged.",
        "decision_rule": "If closed/open limiting case does not discriminate, do not build mutation or MD machinery on this approximation.",
        "does_not_prove": "Hydration profiles are not BK gating voltages, sensor-pore coupling or mutant-selection accuracy; no lipids, explicit solvent or cofactors",
    }
    (OUT / "bk_hydration_limiting_cases.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
