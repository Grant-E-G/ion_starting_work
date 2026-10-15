"""Useful higher-order selection versus measured single parents and rescue.

Use independent RAW Wu single controls only for evaluation/control-aware ranking;
none were used to fit the transferred models. No new models or sign tuning.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from data import DATA, OUT, write_immutable
from metrics import precision_at_k
from sklearn.metrics import average_precision_score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-order", type=int, choices=[1, 2], default=1)
    args = parser.parse_args()
    suffix = "_pairs" if args.parent_order == 2 else ""
    frame = pd.read_csv(OUT / "gb1_transfer_measurements.csv").set_index("id")
    from itertools import combinations

    controls = frame[frame.HD <= args.parent_order]
    lookup = {
        ",".join(sorted(ident.split(","))): float(value)
        for ident, value in zip(controls.index, controls.I20fitRaw, strict=True)
    }
    all_test = frame[frame.HD >= 3].copy()
    parents = []
    complete = []
    for ident in all_test.index:
        tokens = ident.split(",")
        keys = [
            ",".join(sorted(group))
            for order in range(1, args.parent_order + 1)
            for group in combinations(tokens, order)
        ]
        complete.append(all(key in lookup for key in keys))
        parents.append([lookup[key] for key in keys if key in lookup])
    all_test = all_test[np.array(complete)]
    parents = [values for values, keep in zip(parents, complete, strict=True) if keep]
    best = np.array([max([1] + values) for values in parents])
    all_test["best_raw_parent"] = best
    all_test["beyond_parent"] = all_test.I20fitRaw >= 1.2 * best
    all_test["rescue_pool"] = [
        all(value <= 1 for value in values) for values in parents
    ]
    policy: dict = {
        "hypothesis": "WT-gain enrichment can inherit known beneficial parents; test higher-order improvements beyond the best independently measured single parent and rescue of nonbeneficial singles",
        "parents": "All76RAW Wu I20fitRaw single controls, never processed I20fit or oldOlson-adjusted single labels",
        "model_training": "Existing transfer models unchanged; rawWu single controls were not used to fit model coefficients/hyperparameters",
        "rankings": "Plain predicted logfitness; secondary predicted logfitness-minus-measured best-single logfitness explicitly uses76additionalcontrolmeasurements",
        "utility": "Actualfitness>=1.2*max(1,componentrawsinglefitness); rescue subset allcomponentrawsingle<=1 and combinedfitness>=1.2",
        "scope": "Posthoc fixed-threshold failure analysis of inspected independent dataset; not a new blind test or biological significance certificate. Single-controls are experimental information, not free prospective labels.",
    }
    if args.parent_order == 2:
        policy["parents"] = (
            "All measuredRAW Wu single/double proper parents; require every constituent measurement; processedI20fit ignored"
        )
        policy["rankings"] = (
            "Plain predictedfunction and secondary predictedincrement using allmeasuredsingle/doublecontrols; existingpublished data, notfreeprospectiveinputs"
        )
        policy["parent_order"] = 2
        policy["utility"] = (
            "Actualfitness>=1.2*max(1,allproper measuredsingle/doubleparents); rescuepool allproperparents<=1"
        )
        policy["eligible_test_n"] = len(all_test)
        policy["parent_controls"] = len(controls)
    policy_suffix = suffix + "_v2" if args.parent_order == 2 else suffix
    write_immutable(
        DATA / f"gb1_transfer_utility_policy{policy_suffix}.json",
        json.dumps(policy, indent=2) + "\n",
    )
    table = pd.read_csv(
        OUT / "gb1_transfer_predictions.csv", usecols=["features", "id", "predicted"]
    )
    if args.parent_order == 2 and (OUT / "gb1_components_predictions.csv").exists():
        extra = pd.read_csv(
            OUT / "gb1_components_predictions.csv",
            usecols=["features", "id", "predicted"],
        )
        extra["features"] = "components/" + extra.features
        table = pd.concat([table, extra], ignore_index=True)
    output = []
    families = {
        name: part.set_index("id").predicted for name, part in table.groupby("features")
    }
    families[
        (
            "raw_single_parent_only"
            if args.parent_order == 1
            else "raw_single_double_parent_only"
        )
    ] = np.log(all_test.best_raw_parent)
    for name, scores in families.items():
        prediction = scores.loc[all_test.index].to_numpy()
        for ranking in [
            "predicted_function",
            (
                "predicted_increment_using76controls"
                if args.parent_order == 1
                else "predicted_increment_using_measured_pairs"
            ),
        ]:
            score = (
                prediction
                if ranking == "predicted_function"
                else prediction - np.log(best)
            )
            for subset in ["all_higher_order", "triples", "quadruples", "rescue_pool"]:
                mask = (
                    np.ones(len(all_test), dtype=bool)
                    if subset == "all_higher_order"
                    else (
                        all_test.HD.to_numpy() == 3
                        if subset == "triples"
                        else (
                            all_test.HD.to_numpy() == 4
                            if subset == "quadruples"
                            else all_test.rescue_pool.to_numpy()
                        )
                    )
                )
                target = all_test.beyond_parent.to_numpy()[mask]
                output.append(
                    {
                        "features": name,
                        "ranking": ranking,
                        "subset": subset,
                        "n": int(mask.sum()),
                        "positive_n": int(target.sum()),
                        "prevalence": float(target.mean()),
                        "P20": precision_at_k(score[mask], target, 20),
                        "P100": precision_at_k(score[mask], target, 100),
                        "AP": float(average_precision_score(target, score[mask])),
                    }
                )
    pd.DataFrame(output).to_csv(
        OUT / f"gb1_transfer_utility_metrics{suffix}.csv", index=False
    )
    all_test[
        ["mut", "HD", "I20fitRaw", "best_raw_parent", "beyond_parent", "rescue_pool"]
    ].to_csv(OUT / f"gb1_transfer_parent_controls{suffix}.csv")
    print(
        pd.DataFrame(output)
        .query("subset=='all_higher_order'")
        .round(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
