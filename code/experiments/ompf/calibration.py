"""One global transport multiplier from WT 1M KCl; test transfer across conditions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from physics import ROOT

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trimer", action="store_true")
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    suffix = "_trimer" if args.trimer else ""
    output_suffix = suffix + ("_" + args.tag if args.tag else "")
    mode = "nonlinear_pb"
    h = 0.15
    frame = pd.read_csv(
        ROOT / f"notes/ompf/comparisons{output_suffix}_{mode}_h{h}_seed0.csv"
    )
    res = ROOT / ("notes/ompf/trimer" if args.trimer else "notes/ompf/results")
    if args.directory is not None:
        res = args.directory
    wt = json.loads((res / f"WT{suffix}_c1.0_h{h}_{mode}_seed0.json").read_text())
    cal = float(
        frame[
            (frame.study == "miedema2004")
            & (frame.variant == "WT")
            & (frame.salt == "KCl")
            & (frame.molarity_M == 1.0)
        ]
        .iloc[0]
        .conductance_nS
    )
    scales = {
        model: cal
        / ((1 if args.trimer else 3) * wt["predictions"]["KCl"][model + "_nS"])
        for model in ["physics", "geometry"]
    }
    rows = []
    for _, r in frame.iterrows():
        result = json.loads(
            (
                res / f"{r.variant}{suffix}_c{r.molarity_M}_h{h}_{mode}_seed0.json"
            ).read_text()
        )
        row = r.to_dict()
        factor = (
            (1 if r.reporting_unit == "trimer" else 1 / 3)
            if args.trimer
            else (3 if r.reporting_unit == "trimer" else 1)
        )
        for model, scale in scales.items():
            row[model + "_global_nS"] = (
                scale * factor * result["predictions"][r.salt][model + "_nS"]
            )
        rows.append(row)
    pd.DataFrame(rows).to_csv(
        ROOT / f"notes/ompf/global_calibration{output_suffix}.csv", index=False
    )
    (ROOT / f"notes/ompf/global_calibration{output_suffix}.json").write_text(
        json.dumps(
            {
                "calibration": "Miedema2004 WT symmetric 1M KCl, 4.2 nS trimer",
                "diffusion_multipliers": scales,
                "other_parameter_fits": 0,
                "warning": "Na/K diffusion ratio, calcium binding and activity corrections uncalibrated",
            },
            indent=2,
        )
        + "\n"
    )
