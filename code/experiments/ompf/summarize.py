"""Summarize actual runs, numerical uncertainty and comparisons without refitting."""

from __future__ import annotations

import json

import pandas as pd
from physics import ROOT


def summarize() -> None:
    directory = ROOT / "notes/ompf"
    rows = []
    for folder in [
        "results",
        "mesh",
        "trimer",
        "parameters",
        "sterics",
        "reaction",
        "combined",
    ]:
        for p in (directory / folder).rglob("*.json"):
            r = json.loads(p.read_text())
            if "predictions" not in r:
                continue
            config = r["config"]
            for salt, pred in r["predictions"].items():
                rows.append(
                    dict(
                        folder=folder,
                        case=str(p.parent.relative_to(directory)),
                        variant=r["variant"],
                        seed=r["seed"],
                        salt=salt,
                        concentration_M=config["concentration_M"],
                        spacing_nm=config["spacing_nm"],
                        electrostatics=config["electrostatics"],
                        ion_volume_nm3=config.get("ion_volume_nm3", 0),
                        **pred,
                        seconds=r["seconds"],
                        process_peak_RSS_MiB=r["process_peak_RSS_MiB"],
                        grid_nodes=r["grid_nodes"],
                        max_water_potential_kT=r["electrostatics"][
                            "max_abs_water_potential_kT"
                        ],
                        maximum_flux_spread=max(
                            v["flux_plane_spread_relative"]
                            for v in r["transport"].values()
                        ),
                    )
                )
    frame = pd.DataFrame(rows)
    frame.to_csv(directory / "run_summary.csv", index=False)
    ratios = []
    for _, r in frame.iterrows():
        wt = "WT_trimer" if r.variant.endswith("_trimer") else "WT"
        subset = frame[
            (frame.case == r.case)
            & (frame.variant == wt)
            & (frame.seed == r.seed)
            & (frame.salt == r.salt)
            & (frame.concentration_M == r.concentration_M)
            & (frame.spacing_nm == r.spacing_nm)
            & (frame.electrostatics == r.electrostatics)
            & (frame.ion_volume_nm3 == r.ion_volume_nm3)
        ]
        if len(subset) != 1:
            continue
        base = subset.iloc[0]
        record = r.to_dict()
        for m in ["physics", "geometry"]:
            record[m + "_ratio"] = r[m + "_nS"] / base[m + "_nS"]
        ratios.append(record)
    ratio_frame = pd.DataFrame(ratios)
    ratio_frame.to_csv(directory / "sensitivity_ratios.csv", index=False)
    a = pd.read_csv(directory / "comparisons_nonlinear_pb_h0.15_seed0.csv")
    b = pd.read_csv(directory / "comparisons_nonlinear_pb_h0.15_seed1.csv")
    merged = a.merge(b, on="measurement_id", suffixes=("_seed0", "_seed1"))
    for model in ["physics", "geometry"]:
        merged[model + "_ratio_absolute_change"] = abs(
            merged[model + "_ratio_seed0"] - merged[model + "_ratio_seed1"]
        )
    merged.to_csv(directory / "preparation_variability.csv", index=False)
    report = {
        "run_files": int(len(frame) / 2),
        "maximum_flux_plane_spread_relative": float(frame.maximum_flux_spread.max()),
        "maximum_measured_process_RSS_MiB": float(frame.process_peak_RSS_MiB.max()),
        "prep_replicate_max_ratio_change": float(
            merged.physics_ratio_absolute_change.max()
        ),
        "prep_replicate_note": "Two initializations; not an independent backbone/rotamer ensemble, nor uncertainty calibration",
        "fields": "seconds measure each run; process RSS is process-lifetime high-water, not per-run incremental memory",
        "statistical_note": "Repeated conditions on the same construct are not independent targets; no p-value or confidence interval claimed",
    }
    (directory / "numerical_summary.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    summarize()
