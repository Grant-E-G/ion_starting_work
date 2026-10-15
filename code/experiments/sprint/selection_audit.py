"""Paired, fixed-family summaries; never select a method by its test score."""

from __future__ import annotations

import json

import pandas as pd
from data import OUT


def paired_neural() -> pd.DataFrame:
    frame = pd.read_csv(OUT / "neural_cases.csv")
    pairs = []
    # Fixed predeclared-method contrasts, complete seed pairs only. Historical
    # generic and corrected S2 fits are separate, never pooled as extra repeats.
    vep = frame[
        (frame.experiment == "vep")
        & (frame.encoding == "mutation")
        & (frame.subset == "all")
    ]
    contrasts = [
        ("sequence", "rosetta"),
        ("sequence", "evoef_matched"),
        ("indicator", "rosetta"),
        ("sequence", "rosetta_rmsf"),
        ("sequence", "evoef_matched_rmsf"),
        ("esm2_35m", "esm2_35m_rosetta_rmsf"),
    ]
    for keys, block in vep.groupby(
        [
            "dataset",
            "protocol",
            "architecture",
            "published_configuration",
            "train_limit",
            "LLR_divisor",
        ],
        dropna=False,
    ):
        # NoLLR rows have NaN divisor, while LLR rows have1/10. First two
        # contrasts do not use anLLR; third compares matched scale only.
        for first, second in contrasts:
            a = block[block.features == first].set_index("seed")
            b = block[block.features == second].set_index("seed")
            seeds = sorted(set(a.index) & set(b.index))
            if not seeds:
                continue
            assert (
                a.index.is_unique and b.index.is_unique
            ), "Keep encoding/configuration/budget variants separate"
            for seed in seeds:
                row = {
                    "experiment": "vep",
                    "dataset": keys[0],
                    "protocol": keys[1],
                    "architecture": keys[2],
                    "published_configuration": keys[3],
                    "LLR_divisor": keys[5],
                    "first": first,
                    "second": second,
                    "seed": int(seed),
                    "development_labels_total": int(
                        a.loc[seed, "development_labels_total"]
                    ),
                }
                for metric in ["pearson", "P20", "average_precision"]:
                    row[f"{metric}_first"] = a.loc[seed, metric]
                    row[f"{metric}_second"] = b.loc[seed, metric]
                    row[f"{metric}_difference"] = (
                        b.loc[seed, metric] - a.loc[seed, metric]
                    )
                pairs.append(row)
    for experiment, field, contrasts in [
        ("finetune", "physical", [("none", "rosetta"), ("none", "evoef_matched")]),
        (
            "metl_finetune",
            "checkpoint",
            [("random_gfp", "gfp"), ("binding_control", "binding")],
        ),
    ]:
        source = frame[(frame.experiment == experiment) & (frame.subset == "all")]
        # Include case suffix for validation stride so full/capped validation
        # fits are not merged. Baseline/method cases differ only infield token.
        source = source.copy()
        source["validation_stride5"] = source.case.str.contains("_v5")
        group = [
            "dataset",
            "protocol",
            "train_n",
            "validation_n",
            "validation_stride5",
        ] + (["mode"] if experiment == "finetune" else [])
        for keys, block in source.groupby(group, dropna=False):
            for first, second in contrasts:
                a = block[block[field] == first].set_index("seed")
                b = block[block[field] == second].set_index("seed")
                seeds = sorted(set(a.index) & set(b.index))
                if not seeds:
                    continue
                assert a.index.is_unique and b.index.is_unique
                for seed in seeds:
                    row = {
                        "experiment": experiment,
                        "dataset": keys[0],
                        "protocol": keys[1],
                        "architecture": (
                            keys[-1] if experiment == "finetune" else "METL2M"
                        ),
                        "published_configuration": None,
                        "LLR_divisor": None,
                        "first": first,
                        "second": second,
                        "seed": int(seed),
                        "development_labels_total": int(
                            a.loc[seed, "development_labels_total"]
                        ),
                    }
                    for metric in ["pearson", "P20", "average_precision"]:
                        row[f"{metric}_first"] = a.loc[seed, metric]
                        row[f"{metric}_second"] = b.loc[seed, metric]
                        row[f"{metric}_difference"] = (
                            b.loc[seed, metric] - a.loc[seed, metric]
                        )
                    pairs.append(row)
    result = pd.DataFrame(pairs)
    result.to_csv(OUT / "paired_neural_contrasts.csv", index=False)
    return result


def interval_diagnostics() -> None:
    results = []
    path = OUT / "external_bk_predictions.csv"
    if path.exists():
        data = pd.read_csv(path)
        test = data[(data.calcium_uM == 0) & ~data.overlap_control]
        for family, part in test.groupby("family"):
            p = part.predicted_mV.to_numpy()
            half = part.empirical90_halfwidth_mV.to_numpy()
            actual = part.actual_mV.to_numpy()
            confident = p + half <= -50
            results.append(
                {
                    "dataset": "external_BK2024",
                    "features": family,
                    "test_n": len(part),
                    "interval_type": "Empirical old-source siteOOF90 residual halfwidth, no distribution-free external guarantee",
                    "halfwidth_mV": float(half[0]),
                    "coverage": float((abs(p - actual) <= half).mean()),
                    "confident_left_gain_n": int(confident.sum()),
                    "confident_left_gain_precision": (
                        float((actual[confident] <= -50).mean())
                        if confident.any()
                        else None
                    ),
                }
            )
    (OUT / "interval_diagnostics.json").write_text(json.dumps(results, indent=2) + "\n")


def main() -> None:
    result = paired_neural()
    keys = [
        "experiment",
        "dataset",
        "protocol",
        "architecture",
        "published_configuration",
        "LLR_divisor",
        "first",
        "second",
        "development_labels_total",
    ]
    values = [
        column
        for column in result
        if column.endswith(("_first", "_second", "_difference"))
    ]
    summary = result.groupby(keys, dropna=False)[values].mean().reset_index()
    summary["complete_seed_pairs"] = (
        result.groupby(keys, dropna=False).size().to_numpy()
    )
    summary.to_csv(OUT / "paired_neural_summary.csv", index=False)
    interval_diagnostics()
    (OUT / "selection_audit_scope.json").write_text(
        json.dumps(
            {
                "pairs": len(result),
                "summary_rows": len(summary),
                "scope": "Descriptive paired fixed-method contrasts. Seeds have overlapping test constructs, are not independent experimental replicates; no multiplicity-adjusted significance claim. Incomplete pairs excluded. No best-test model chosen.",
            },
            indent=2,
        )
        + "\n"
    )
    print(len(result), "paired neural contrasts")


if __name__ == "__main__":
    main()
