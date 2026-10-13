"""Independent APBS comparison for a screened point charge in uniform dielectric."""

from __future__ import annotations

import json

import numpy as np
from physics import ROOT, Config, electrostatic, mesh, neighbors

if __name__ == "__main__":
    c = Config(spacing_nm=0.05, half_xy_nm=1.6, half_z_nm=1.6, concentration_M=0.1)
    points, shape = mesh(c)
    left, right = neighbors(shape)
    data = {"xyz": np.array([[0.0, 0.0, 0.0]]), "charges": np.array([0.01])}
    result, stats = electrostatic(
        data,
        points,
        shape,
        np.full(len(points), 78.5),
        np.ones(len(points), dtype=bool),
        left,
        right,
        c,
    )
    path = ROOT / "notes/ompf/apbs/point_potential-PE0.dx"
    text = path.read_text()
    values = text.split("data follows", 1)[1].split("attribute", 1)[0].split()
    apbs = np.array([float(x) for x in values])
    assert apbs.shape == result.shape
    radius = np.linalg.norm(points, axis=1)
    mask = (radius >= 0.15) & (radius <= 1.3)
    relative = float(np.linalg.norm((result - apbs)[mask]) / np.linalg.norm(apbs[mask]))
    samples = []
    for r in [0.15, 0.3, 0.6, 1.0]:
        i = np.argmin(np.linalg.norm(points - np.array([r, 0.0, 0.0]), axis=1))
        samples.append(
            {"radius_nm": r, "ours_kT": float(result[i]), "apbs_kT": float(apbs[i])}
        )
    report = {
        "relative_L2_error_excluding_charge_core": relative,
        "samples": samples,
        "solver": stats,
        "scope": "Uniform dielectric, LPB, charge=0.01e, identical zero box boundaries. Does not validate protein dielectric surfaces or transport.",
        "apbs_version": "Ubuntu APBS 3.0.0+dfsg1-3build2",
        "source": "https://apbs.readthedocs.io/en/latest/",
        "apbs_inputs": "notes/ompf/apbs/point.in; point.pqr",
    }
    (ROOT / "notes/ompf/apbs/comparison.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
    if relative > 0.02:
        raise AssertionError("Independent LPB solver discrepancy >2%")
