"""Compare fresh fixed-fixture solves with archived primary results, without refitting."""

from __future__ import annotations

import json

from physics import ROOT, Config, run

if __name__ == "__main__":
    rows = []
    for variant, concentration, image in [
        ("WT", 0.1, False),
        ("EAE", 1.0, False),
        ("WT", 0.1, True),
        ("EAE", 1.0, True),
    ]:
        name = variant + "_trimer"
        directory = ROOT / (
            "notes/ompf/reaction/trimer_h0.15_s3/predictions"
            if image
            else "notes/ompf/trimer"
        )
        archived = json.loads(
            (
                directory / f"{name}_c{concentration}_h0.15_nonlinear_pb_seed0.json"
            ).read_text()
        )
        energy = (
            ROOT / f"notes/ompf/reaction/trimer_h0.15_s3/{name}_h0.15_s3.npz"
            if image
            else None
        )
        fresh = run(name, Config(**archived["config"]), self_energy_file=energy)
        absolute = max(
            abs(fresh["predictions"][salt][key] - archived["predictions"][salt][key])
            for salt in ["NaCl", "KCl"]
            for key in ["physics_nS", "geometry_nS"]
        )
        if absolute > 1e-6:
            raise AssertionError(
                f"Fixed-fixture regeneration difference: {absolute} nS"
            )
        rows.append(
            {
                "variant": name,
                "concentration_M": concentration,
                "image": image,
                "maximum_prediction_difference_nS": absolute,
                "prepared_sha256": fresh["prepared_sha256"],
                "seconds": fresh["seconds"],
            }
        )
        print(rows[-1], flush=True)
    (ROOT / "notes/ompf/checks/fixed_fixture_regeneration.json").write_text(
        json.dumps(
            {
                "cases": rows,
                "tolerance_nS": 1e-6,
                "note": "Fresh fixed-fixture solves compared to archived primary outputs; hydrogen/side-chain re-preparation excluded",
            },
            indent=2,
        )
        + "\n"
    )
