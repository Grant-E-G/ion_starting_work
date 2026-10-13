"""Candidate-choice checks; mean-ranking agreement is not significance or validation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from physics import ROOT

if __name__ == "__main__":
    rows = []
    names = [
        "comparisons_trimer_nonlinear_pb_h0.15_seed0.csv",
        "comparisons_trimer_nonlinear_pb_h0.075_seed0.csv",
        "comparisons_image_monomer_s3_nonlinear_pb_h0.15_seed0.csv",
        "comparisons_trimer_image_trimer_s3_nonlinear_pb_h0.15_seed0.csv",
        "comparisons_trimer_image_trimer_s3_nonlinear_pb_h0.1_seed0.csv",
    ]
    for name in names:
        data = pd.read_csv(ROOT / "notes/ompf" / name)
        data = data[(data.study == "miedema2004") & (data.variant != "WT")]
        for (salt, c), group in data.groupby(["salt", "molarity_M"]):
            ordered = group.sort_values("conductance_nS", ascending=False)
            best = ordered.iloc[0]
            runner = ordered.iloc[1]
            gap = best.conductance_nS - runner.conductance_nS
            dispersion = float(np.hypot(best.error_nS, runner.error_nS))
            for model in ["physics", "geometry", "charge", "charge_entry", "null"]:
                top = group[group[model + "_ratio"] == group[model + "_ratio"].max()]
                rows.append(
                    {
                        "comparison": name,
                        "salt": salt,
                        "concentration_M": c,
                        "model": model,
                        "observed_best_by_mean": best.variant,
                        "predicted_top_ties": "/".join(top.variant),
                        "single_choice_matches_mean": bool(
                            len(top) == 1 and top.iloc[0].variant == best.variant
                        ),
                        "observed_gap_nS": gap,
                        "quadrature_reported_dispersion_nS": dispersion,
                        "observed_gap_exceeds_one_reported_dispersion": bool(
                            gap > dispersion
                        ),
                        "caveat": "Reported error statistic undefined; this flag is descriptive, not a confidence test",
                    }
                )
    pd.DataFrame(rows).to_csv(ROOT / "notes/ompf/ranking_choices.csv", index=False)
    print(
        "Saved mean-choice comparisons, including ties and experimental ranking ambiguity"
    )
