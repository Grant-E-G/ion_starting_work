"""A representation bound and a WT-only two-parameter calibration diagnostic.

If cation/anion fields are chemically identical across NaCl/KCl, G_Na/G_K is a
positive weighted average of D_Na/D_K and 1. No grid or protein geometry can
break that bound. Extra effective D_Na is fitted only to WT, never to mutants.
"""

from __future__ import annotations

import json

import pandas as pd
from physics import ROOT

if __name__ == "__main__":
    data = pd.read_csv(ROOT / "sources/ompf/measurements.csv")
    study = data[data.study == "miedema2004"]
    lower = 1.33 / 1.96
    rows = []
    for (v, c), group in study.groupby(["variant", "molarity_M"]):
        if set(group.salt) != {"NaCl", "KCl"}:
            continue
        na = group[group.salt == "NaCl"].iloc[0]
        k = group[group.salt == "KCl"].iloc[0]
        rows.append(
            {
                "variant": v,
                "concentration_M": c,
                "observed_NaCl_over_KCl": float(na.conductance_nS / k.conductance_nS),
                "model_lower_bound": lower,
                "model_upper_bound": 1.0,
                "reported_dispersion_upper_ratio": float(
                    (na.conductance_nS + na.error_nS) / (k.conductance_nS - k.error_nS)
                ),
                "note": "Ratio of reported means; dispersion bound is descriptive, not a confidence interval",
            }
        )
    pd.DataFrame(rows).to_csv(
        ROOT / "notes/ompf/salt_representation_bound.csv", index=False
    )
    predictions = []
    parameters = []
    for tag, directory in [
        ("ordinary", ROOT / "notes/ompf/trimer"),
        ("image", ROOT / "notes/ompf/reaction/trimer_h0.15_s3/predictions"),
    ]:
        wt = json.loads(
            (directory / "WT_trimer_c1.0_h0.15_nonlinear_pb_seed0.json").read_text()
        )["predictions"]["KCl"]
        scale = 4.2 / wt["physics_nS"]
        cation_factor = (2.39 / scale - wt["anion_nS"]) / wt["cation_nS"]
        assert cation_factor > 0
        # Factor multiplies K cation contribution, so effective DNa = factor*DK.
        parameters.append(
            {
                "model": tag,
                "common_mobility_scale": scale,
                "effective_DNa_nm2_s": cation_factor * 1.96e9,
                "calibration": "Miedema2004 WT 1M KCl and 1M NaCl; two WT-only parameters; no mutant fit",
            }
        )
        for _, r in data[data.evaluation_eligible].iterrows():
            p = json.loads(
                (
                    directory
                    / f"{r.variant}_trimer_c{r.molarity_M}_h0.15_nonlinear_pb_seed0.json"
                ).read_text()
            )["predictions"]["KCl"]
            raw = (
                p["physics_nS"]
                if r.salt == "KCl"
                else cation_factor * p["cation_nS"] + p["anion_nS"]
            )
            unit_factor = 1 if r.reporting_unit == "trimer" else 1 / 3
            reference = json.loads(
                (
                    directory
                    / f"WT_trimer_c{r.molarity_M}_h0.15_nonlinear_pb_seed0.json"
                ).read_text()
            )["predictions"]["KCl"]
            base = (
                reference["physics_nS"]
                if r.salt == "KCl"
                else cation_factor * reference["cation_nS"] + reference["anion_nS"]
            )
            wt_exp = data[
                (data.study == r.study)
                & (data.variant == "WT")
                & (data.salt == r.salt)
                & (data.molarity_M == r.molarity_M)
            ].iloc[0]
            predictions.append(
                {
                    "model": tag,
                    "measurement_id": r.measurement_id,
                    "study": r.study,
                    "variant": r.variant,
                    "salt": r.salt,
                    "concentration_M": r.molarity_M,
                    "observed_nS": r.conductance_nS,
                    "predicted_global_nS": scale * unit_factor * raw,
                    "observed_ratio": r.conductance_nS / wt_exp.conductance_nS,
                    "predicted_ratio": raw / base,
                    "calibration_row": bool(
                        r.study == "miedema2004"
                        and r.variant == "WT"
                        and r.molarity_M == 1.0
                    ),
                }
            )
    pd.DataFrame(predictions).to_csv(
        ROOT / "notes/ompf/two_WT_calibration_predictions.csv", index=False
    )
    report = {
        "bound": {
            "lower": lower,
            "upper": 1.0,
            "assumptions": "Common cation equilibrium/transport field, same Cl field, fixed DNa/DK and nonnegative contributions; applies to all present constitutive variants",
        },
        "observed": rows,
        "two_WT_parameters": parameters,
        "inference": "Central WT salt ratios violate the fixed-bulk-D representation. This cannot be repaired by grid refinement or a larger folding model within the same chemical assumptions.",
        "limitation": "The bound alone does not reject a within-salt WT-normalized mutation model; its independent mutant transfer must be tested separately.",
    }
    (ROOT / "notes/ompf/salt_consistency.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
