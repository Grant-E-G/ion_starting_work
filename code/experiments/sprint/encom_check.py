"""Bounded published mutation-sensitive normal-mode/entropy component test.

NRGten/ENCoM defaults beta1, pseudo-physical entropy units; no calibrated gating
free energies. No custom Hessian simulator. Start with WT numerical/runtime gate.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from Bio.PDB import PDBParser
from data import OUT, RAW
from nrgten.encom import ENCoM
from threadpoolctl import threadpool_limits


def native_inputs() -> None:
    folder = OUT / "encom"
    folder.mkdir(exist_ok=True)
    sites = []
    for identifier in ["6V3G", "6V38"]:
        chain = PDBParser(QUIET=True).get_structure(
            identifier, RAW / f"{identifier}.pdb"
        )[0]["A"]
        sites.append(
            {
                residue.id[1]
                for residue in chain
                if residue.id[0] == " "
                and "CA" in residue
                and 20 <= residue.id[1] <= 350
            }
        )
    common = sites[0] & sites[1]
    for state, identifier in [("closed", "6V3G"), ("open", "6V38")]:
        lines = [
            line
            for line in (RAW / f"{identifier}.pdb").read_text().splitlines()
            if line.startswith("ATOM")
            and line[21] == "A"
            and int(line[22:26]) in common
        ]
        (folder / f"{state}_native.pdb").write_text("\n".join(lines) + "\nEND\n")


def measure(
    path: Path, displacement: np.ndarray | None = None, save_modes: bool = False
) -> dict:
    start = time.perf_counter()
    model = ENCoM(str(path), ignore_hetatms=True, use_pickle=False)
    values = np.asarray(model.eigvals)
    assert np.isfinite(values).all()
    tolerance = max(abs(values).max() * 1e-8, 1e-8)
    zero = int((abs(values) < tolerance).sum())
    assert (
        zero == 6 and (values[6:] > 0).all()
    ), "Hessian has extra disconnected/unstable modes"
    symmetry = float(abs(model.h - model.h.T).max())
    assert symmetry < 1e-6
    translation = np.tile([1.0, 0, 0], len(values) // 3)
    translation_relative = float(
        np.linalg.norm(model.h @ translation) / np.linalg.norm(model.h)
    )
    assert translation_relative < 1e-8
    result = {
        "input": str(path),
        "seconds": time.perf_counter() - start,
        "masses": len(values) // 3,
        "zero_modes": zero,
        "Hessian_symmetry_max_error": symmetry,
        "entropy_beta1": float(model.compute_vib_entropy(beta=1)),
        "entropy_rigid_rotor": float(model.compute_vib_entropy_rigid_rotor()),
        "first_positive_eigenvalue": float(values[6]),
        "last_eigenvalue": float(values[-1]),
        "entropy_units": "Published ENCoM pseudo-physical units; not thermodynamic kcal/mol or calibrated channel populations",
    }
    result["rigid_translation_relative_residual"] = translation_relative
    result["low20_mean_log_eigenvalue"] = float(np.log(values[6:26]).mean())
    if displacement is not None:
        assert displacement.shape == model.mol.masscoords.shape
        flat = displacement.ravel()
        result["harmonic_transition_work"] = float(0.5 * flat @ model.h @ flat)
    if save_modes:
        np.savez_compressed(
            path.parent / f"{path.stem}_modes.npz", eigenvalues=values, hessian=model.h
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdb", type=Path)
    args = parser.parse_args()
    native_inputs()
    path = args.pdb if args.pdb is not None else OUT / "encom/closed_native.pdb"
    result = measure(path, save_modes=True)
    path.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=2):
        main()
