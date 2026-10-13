"""Report state-resolved external data without selecting a favorable population."""

from __future__ import annotations

import argparse
import json

import pandas as pd
from physics import ROOT

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trimer", action="store_true")
    args = parser.parse_args()
    suffix = "_trimer" if args.trimer else ""
    data = pd.read_csv(ROOT / "sources/ompf/measurements.csv")
    subset = data[data.study == "miedema_d127_2006"]
    wt = float(subset[subset.variant == "WT"].iloc[0].conductance_nS)
    rows = []
    for variant in ["D127N", "D127K"]:
        observed = subset[subset.variant == variant]
        for model in ["ordinary", "image"]:
            path = (
                ROOT
                / f"notes/ompf/reaction/state_challenge{suffix}/{model}/{variant}{suffix}_c0.1_h0.15_nonlinear_pb_seed0.json"
            )
            result = json.loads(path.read_text())
            reference_directory = (
                f'notes/ompf/reaction/{"trimer" if args.trimer else "monomer"}_h0.15_s3/predictions'
                if model == "image"
                else "notes/ompf/trimer" if args.trimer else "notes/ompf/results"
            )
            reference = json.loads(
                (
                    ROOT
                    / reference_directory
                    / f"WT{suffix}_c0.1_h0.15_nonlinear_pb_seed0.json"
                ).read_text()
            )
            ratio = (
                result["predictions"]["KCl"]["physics_nS"]
                / reference["predictions"]["KCl"]["physics_nS"]
            )
            prediction = wt * ratio
            rows.append(
                {
                    "variant": variant,
                    "model": model,
                    "predicted_nS": prediction,
                    "predicted_ratio": ratio,
                    "observed_population_means_nS": "/".join(
                        map(str, observed.conductance_nS)
                    ),
                    "reported_counts": "/".join(str(int(n)) for n in observed.n),
                    "observed_min_ratio": float(observed.conductance_nS.min() / wt),
                    "observed_max_ratio": float(observed.conductance_nS.max() / wt),
                    "outside_mean_range_nS": float(
                        max(
                            observed.conductance_nS.min() - prediction,
                            prediction - observed.conductance_nS.max(),
                            0,
                        )
                    ),
                    "caveat": "Scalar range compatibility does not predict state probabilities or identify a high-conductance population",
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(ROOT / f"notes/ompf/state_challenge{suffix}.csv", index=False)
    print(
        frame[
            [
                "variant",
                "model",
                "predicted_ratio",
                "observed_min_ratio",
                "observed_max_ratio",
            ]
        ]
        .round(4)
        .to_string(index=False)
    )
