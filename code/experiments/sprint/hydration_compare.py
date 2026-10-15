"""Does approximate mutation-specific pore hydration beat hydropathy/geometry?

Small, explicitly restricted pore benchmark. Known A316D/V controls are removed;
leave-site-out folds are not replaced by easier random splits. P5 is reported
because some folds contain fewer than20 eligible variants.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from data import DATA, FEATURES, OUT, load_bk
from metrics import evaluate, precision_at_k
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", action="store_true")
    parser.add_argument(
        "--stable",
        action="store_true",
        help="Train-only removal of variance below1e-10 before scaling",
    )
    args = parser.parse_args()
    native = load_bk()
    physical = pd.read_csv(FEATURES / "bk_hydration_mutants.csv").set_index("id")
    frame = native.set_index("id", drop=False).loc[physical.index].copy()
    eligible = ~frame.censored & ~frame.id.isin(["A316D", "A316V"])
    if args.profiles:
        for state in ["closed", "open"]:
            eligible &= (
                physical[f"{state}_delta_interchain_heavy_clashes_below1_5A"].to_numpy()
                <= 0
            )
            eligible &= physical[f"{state}_mutant_peak_outside_grid"].to_numpy() == 0
    frame = frame[eligible].reset_index(drop=True)
    physical = physical.loc[frame.id]
    assert frame.id.is_unique and len(frame) > 10
    y = frame.target.to_numpy()
    cheap = frame[["WThyd", "MThyd", "dHyd", "SIFT"]].to_numpy()
    geometry = physical[
        [f"{state}_delta_min_radius_A" for state in ["closed", "open"]]
    ].to_numpy()
    hydration = physical[
        [
            f"{state}_delta_{name}"
            for state in ["closed", "open"]
            for name in [
                "max_energy",
                "mean_energy",
                "positive_energy_integral_A",
                "dry_fraction",
            ]
        ]
    ].to_numpy()
    hydro = physical[
        [f"{state}_delta_mean_hydrophobicity" for state in ["closed", "open"]]
    ].to_numpy()
    arrays = {
        "hydropathy": cheap,
        "hydropathy_geometry": np.column_stack([cheap, geometry, hydro]),
        "hydropathy_geometry_hydration": np.column_stack(
            [cheap, geometry, hydro, hydration]
        ),
    }
    if args.profiles:
        curves = []
        for token in frame.id:
            values = []
            for state in ["closed", "open"]:
                mutant = pd.read_csv(
                    OUT / "hydration_mutants" / token / f"{state}_profile.csv"
                )
                reference = pd.read_csv(
                    OUT / "hydration_mutants" / f"WT_{token[1:-1]}_{state}.csv"
                )
                assert np.allclose(mutant.z_A, reference.z_A)
                values.extend(
                    (
                        mutant[["radius_A", "hydrophobicity"]].to_numpy()
                        - reference[["radius_A", "hydrophobicity"]].to_numpy()
                    ).ravel()
                )
            curves.append(values)
        base = np.column_stack([cheap, np.array(curves)])
        arrays["full_radius_hydrophobicity_profiles"] = base
        arrays["full_profiles_plus_hydration_grid"] = np.column_stack([base, hydration])
    direct = {
        "closed_water_cost": physical.closed_delta_max_energy.to_numpy(),
        "closed_profile_hydrophobicity": physical.closed_delta_mean_hydrophobicity.to_numpy(),
        "negative_closed_radius_change": -physical.closed_delta_min_radius_A.to_numpy(),
    }
    rows: list[dict] = []
    predictions: list[dict] = []
    parts = pd.read_csv(DATA / "bk_partitions.csv")
    for protocol in ["site", "publication_component"]:
        for seed, partition in parts[parts.protocol == protocol].groupby("seed"):
            split = frame.id.map(partition.set_index("id").split).to_numpy()
            train, test = np.isin(split, ["train", "validation"]), split == "test"
            if train.sum() < 5 or not test.any():
                continue
            outputs = {
                "WT_null": np.zeros(test.sum()),
                **{key: value[test] for key, value in direct.items()},
            }
            for name, x in arrays.items():
                for learner in ["ridge", "extra"]:
                    model = (
                        make_pipeline(
                            *([VarianceThreshold(1e-10)] if args.stable else []),
                            StandardScaler(),
                            Ridge(alpha=10),
                        )
                        if learner == "ridge"
                        else ExtraTreesRegressor(
                            n_estimators=300,
                            min_samples_leaf=2,
                            max_features=1.0,
                            random_state=1729,
                            n_jobs=2,
                        )
                    )
                    outputs[f"{name}_{learner}"] = model.fit(
                        x[train], y[train]
                    ).predict(x[test])
            for name, output in outputs.items():
                direct_only = name in direct
                for direction in [1, -1]:
                    metrics = evaluate(y[test], output, direction * 50, direction)
                    if direct_only:
                        # A ranking proxy is not calibrated in millivolts.
                        metrics.pop("mae")
                        metrics.pop("rmse")
                    rows.append(
                        {
                            "protocol": protocol,
                            "seed": int(seed),
                            "features": name,
                            "direction": direction,
                            "train_n": int(train.sum()),
                            "P5": precision_at_k(
                                direction * output, direction * y[test] >= 50, 5
                            ),
                            "score_units": (
                                "Raw physical ranking proxy" if direct_only else "mV"
                            ),
                            **metrics,
                        }
                    )
                predictions.extend(
                    {
                        "protocol": protocol,
                        "seed": int(seed),
                        "features": name,
                        "id": ident,
                        "site": int(site),
                        "actual": float(actual),
                        "predicted": float(value),
                    }
                    for ident, site, actual, value in zip(
                        frame.id[test], frame.resN[test], y[test], output, strict=True
                    )
                )
    suffix = ("_profiles" if args.profiles else "") + ("_stable" if args.stable else "")
    pd.DataFrame(rows).to_csv(OUT / f"hydration_metrics{suffix}.csv", index=False)
    pd.DataFrame(predictions).to_csv(
        OUT / f"hydration_predictions{suffix}.csv", index=False
    )
    (OUT / f"hydration_benchmark_scope{suffix}.json").write_text(
        json.dumps(
            {
                "eligible_mutants": len(frame),
                "numerical_stabilization": (
                    "Train-only variance>1e-10 filter before standardization"
                    if args.stable
                    else "None; original ill-conditioned runs preserved"
                ),
                "eligible_sites": int(frame.resN.nunique()),
                "excluded": "28 source censor flags where present and A316D/V calibration controls",
                "direct_sign": "Lower closed-state water-insertion cost/hydrophobicity or a larger radius hypothesized to favor negative gating shifts; no calibrated energy-to-voltage conversion",
                "supervised": "Fixed Ridgealpha10 and ExtraTrees300leaf2, no tuning on these small tests, development train+validation joined",
                "warning": "Pore-only small retrospective hypothesis test; water insertion cost is not the protein gating free energy. No remote/allosteric prediction, membrane lipids, sensor coupling or backbone response.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    with threadpool_limits(limits=2):
        main()
