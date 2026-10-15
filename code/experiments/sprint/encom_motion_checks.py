"""Check harmonic-work units, coordinate covariance and signal magnitudes."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import FEATURES, OUT
from encom_check import measure
from encom_features import references
from threadpoolctl import threadpool_limits


def main() -> None:
    structures, motion = references()
    source = OUT / "encom/closed_native.pdb"
    rotated = OUT / "encom/closed_rotated.pdb"
    angle = 0.37
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1],
        ]
    )
    first = measure(source, motion["closed"], save_modes=True)
    second = measure(rotated, motion["closed"] @ rotation)
    a, b = first["harmonic_transition_work"], second["harmonic_transition_work"]
    relative = abs(a - b) / max(abs(a), 1e-12)
    assert relative < 0.001, "Harmonic work fails coordinate-frame/PDB-rounding check"
    with np.load(source.parent / "closed_native_modes.npz") as arrays:
        h = arrays["hessian"]
    flat = motion["closed"].ravel()
    work = float(0.5 * flat @ h @ flat)
    scaled = float(0.5 * (2 * flat) @ h @ (2 * flat))
    shifted = flat + np.tile([1.0, -2.0, 3.0], len(flat) // 3)
    translation = float(0.5 * shifted @ h @ shifted)
    assert abs(scaled - 4 * work) / max(abs(work), 1e-12) < 1e-12
    assert abs(translation - work) / max(abs(work), 1e-12) < 1e-10
    from nrgten.encom import ENCoM

    native = ENCoM(str(source), ignore_hetatms=True, use_pickle=False)
    ca = np.array([r["CA"].coord for r in structures["closed"]])
    mass_error = float(abs(native.mol.masscoords - ca).max())
    assert mass_error < 1e-5
    frame = pd.read_csv(FEATURES / "bk_encom.csv")
    delta = frame.closed_delta_entropy_beta1.abs().to_numpy()
    rounding = json.loads((OUT / "encom_numerical_checks.json").read_text())[
        "rotation_entropy_error"
    ]
    result = {
        "work_native": a,
        "work_rotated_motion_and_structure": b,
        "work_relative_frame_difference": relative,
        "predeclared_relative_tolerance": 0.001,
        "work_displacement_scaling": scaled / work,
        "rigid_translation_work_relative_change": abs(translation - work) / abs(work),
        "masspoint_vs_CA_max_difference_A": mass_error,
        "coordinate_tolerance_note": "Initial1e-6check was tighter than Bio.PDBfloat32 representation at~200A. Observedmax7.57e-6A;1e-5A tolerance is below inputPDB0.001A resolution; masses correspond toCA.",
        "WT_motion_RMS_A": float(
            np.sqrt(np.mean(np.sum(motion["closed"] ** 2, axis=1)))
        ),
        "WT_motion_max_A": float(np.linalg.norm(motion["closed"], axis=1).max()),
        "closed_mutant_entropy_absolute_delta_quantiles": np.quantile(
            delta, [0, 0.1, 0.5, 0.9, 1]
        ).tolist(),
        "fraction_entropy_signals_below_native_coordinate_rounding": float(
            (delta < rounding).mean()
        ),
        "scope": "Checks pseudo-physical descriptor computation. Large known-state displacements need not lie in the harmonic basin; work is not an activation barrier. Rotation includes0.001APDBrounding.",
    }
    (OUT / "encom_work_numerics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()
