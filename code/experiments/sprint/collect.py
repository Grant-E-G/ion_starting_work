"""Collate reproducible results; distinguish WT gains from percentile metrics.

No fitting or model selection. Large GB1 prediction files are streamed so the
report step can coexist with local model runs without loading gigabytes of CSV.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from data import OUT
from metrics import evaluate


def neural() -> pd.DataFrame:
    rows: list[dict] = []
    for folder in ["vep", "finetune", "metl_finetune"]:
        for path in sorted((OUT / folder).glob("*.json")):
            result = json.loads(path.read_text())
            if "case" not in result:
                continue
            case = result["case"]
            metadata = {
                key: result.get(key)
                for key in [
                    "dataset",
                    "architecture",
                    "features",
                    "protocol",
                    "seed",
                    "train_limit",
                    "train_n",
                    "validation_n",
                    "best_epoch",
                    "seconds",
                    "peak_allocated_MiB",
                    "checkpoint",
                    "mode",
                    "physical",
                ]
            }
            metadata.update(
                {
                    "case": case,
                    "experiment": folder,
                    "development_labels_total": result["train_n"]
                    + result["validation_n"],
                    "encoding": (
                        result.get("aaindex_mode", "full") if folder == "vep" else None
                    ),
                    "published_configuration": "_S2" in case,
                    "LLR_divisor": (
                        result.get("llr_divisor", 1 if "rawLLR" in case else 10)
                        if "esm" in case
                        else None
                    ),
                    "backbone_selected": (
                        result.get("best_epoch", -1) >= 250
                        if folder == "metl_finetune"
                        else None
                    ),
                }
            )
            metadata["utility_scope"] = (
                "WT gain"
                if result["dataset"] in ["avgfp", "gb1"]
                else "Training top-decile enrichment; WT gain unverified"
            )
            metadata["train_positive_examples"] = result.get("train_positive_examples")
            metadata["validation_positive_examples"] = result.get(
                "validation_positive_examples"
            )
            blocks = {
                "all": result.get("all", result.get("positive")),
                "singles": result.get("singles"),
            }
            if folder == "vep" and result["dataset"] == "gb1":
                predictions = pd.read_csv(
                    path.with_name(path.stem + "_predictions.csv")
                )
                blocks = {
                    "all": evaluate(
                        predictions.actual.to_numpy(),
                        predictions.predicted.to_numpy(),
                        float(np.log(1.2)),
                    )
                }
                singles = predictions[predictions.mutations == 1]
                if len(singles):
                    blocks["singles"] = evaluate(
                        singles.actual.to_numpy(),
                        singles.predicted.to_numpy(),
                        float(np.log(1.2)),
                    )
            for subset, values in blocks.items():
                if values:
                    rows.append({**metadata, "subset": subset, **values})
    result = pd.DataFrame(rows)
    result.to_csv(OUT / "neural_cases.csv", index=False)
    return result


def gb1_reference_metrics(path: Path) -> list[dict]:
    """WT gain>=ln1.2, never relabel training90th-percentile as WT gain."""
    group_columns = ["dataset", "protocol", "seed", "features", "learner"]
    grouped: dict[tuple, list[np.ndarray]] = {}
    for chunk in pd.read_csv(path, chunksize=100000):
        chunk = chunk[chunk.dataset == "gb1"]
        if not len(chunk):
            continue
        for key, part in chunk.groupby(group_columns, sort=False):
            values = np.column_stack(
                [part.actual, part.predicted, part.id.str.count(",") + 1]
            )
            grouped.setdefault(key, []).append(values)
    tag = path.stem.removeprefix("tabular_predictions_")
    metadata = pd.read_csv(OUT / f"tabular_metrics_{tag}.csv")
    metadata = metadata[
        (metadata.dataset == "gb1") & (metadata.subset == "all")
    ].set_index(group_columns)
    rows = []
    for key, parts in grouped.items():
        matrix = np.concatenate(parts)
        info = metadata.loc[key]
        assert isinstance(
            info, pd.Series
        ), "Do not count duplicated method rows as extra repeats"
        for subset, mask in [
            ("all", np.ones(len(matrix), dtype=bool)),
            ("singles", matrix[:, 2] == 1),
        ]:
            if not mask.any():
                continue
            actual, predicted = matrix[mask, 0], matrix[mask, 1]
            selected = predicted >= np.log(1.2)
            rows.append(
                {
                    **dict(zip(group_columns, key, strict=True)),
                    "tag": tag,
                    "subset": subset,
                    "train_n": int(info.train_n),
                    "validation_n": int(info.validation_n),
                    "development_labels_total": int(info.train_n + info.validation_n),
                    "predicted_gain_n": int(selected.sum()),
                    "predicted_gain_precision": (
                        float((actual[selected] >= np.log(1.2)).mean())
                        if selected.any()
                        else None
                    ),
                    **evaluate(actual, predicted, float(np.log(1.2))),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-gb1", action="store_true")
    args = parser.parse_args()
    cases = neural()
    if not args.skip_gb1:
        rows = []
        for tag in ["binding", "actual_mutants", "gb1_val256"]:
            path = OUT / f"tabular_predictions_{tag}.csv"
            if path.exists():
                rows.extend(gb1_reference_metrics(path))
        pd.DataFrame(rows).to_csv(OUT / "gb1_WT_gain_metrics.csv", index=False)
    summaries = {}
    for filename, keys in [
        (
            "bk_matched_metrics.csv",
            ["protocol", "handling", "target", "features", "direction"],
        ),
        ("bk_null_metrics.csv", ["protocol", "features", "direction"]),
        (
            "bk_classification_metrics.csv",
            ["protocol", "features", "learner", "objective"],
        ),
        (
            "bk_classification_metrics_3b.csv",
            ["protocol", "features", "learner", "objective"],
        ),
        ("boosted_metrics.csv", ["protocol", "base", "physical", "direction"]),
        (
            "condition_metrics.csv",
            ["cohort", "protocol", "features", "learner", "direction"],
        ),
        ("adrb2_metrics.csv", ["scope", "features", "learner", "objective"]),
        (
            "tabular_metrics_gfp96total.csv",
            ["dataset", "protocol", "features", "learner", "subset"],
        ),
    ]:
        path = OUT / filename
        if not path.exists():
            continue
        data = pd.read_csv(path)
        numeric = [
            column
            for column in [
                "pearson",
                "rmse",
                "P20",
                "AP",
                "average_precision",
                "prevalence",
                "site_diverse_P10",
            ]
            if column in data
        ]
        means = data.groupby(keys, dropna=False)[numeric].mean().reset_index()
        means["repeats"] = data.groupby(keys, dropna=False).size().to_numpy()
        means.to_csv(OUT / filename.replace("metrics", "summary"), index=False)
        summaries[filename] = len(data)
    (OUT / "collection_manifest.json").write_text(
        json.dumps(
            {
                "neural_cases": int(cases.case.nunique()),
                "other_metric_rows": summaries,
                "scope": "Rows repeat mutants across models/seeds; not independent experiments. GB1benefit metrics recomputed from fixed predictions against verifiedWT, historicalpercentile metrics preserved.",
            },
            indent=2,
        )
        + "\n"
    )
    print("Collated", cases.case.nunique(), "neural fits")


if __name__ == "__main__":
    main()
