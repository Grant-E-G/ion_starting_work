"""Test whether location/publication shortcuts explain random-split prediction.

All lookup means use development labels only. Unknown groups fall back to the
development mean. Publication features are a confounding diagnostic, not a
deployable protein-design representation.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import DATA, OUT, load_bk, publication_components
from metrics import evaluate


def main() -> None:
    frame = load_bk()
    parts = pd.concat(
        [
            pd.read_csv(DATA / "bk_partitions.csv"),
            pd.read_csv(DATA / "bk_published_partitions.csv"),
        ]
    )
    publication, _ = publication_components(frame["Source(s)"])
    publication = np.asarray(publication)
    categories = {
        "same_site_mean": frame.resN.to_numpy(),
        "publication_component_mean_diagnostic": publication,
        "mutant_residue_mean": frame.id.str[-1].to_numpy(),
    }
    y = frame.target.to_numpy()
    metrics: list[dict] = []
    predictions: list[dict] = []
    for (protocol, seed), rows in parts.groupby(["protocol", "seed"]):
        split = frame.id.map(rows.set_index("id").split).to_numpy()
        train = np.isin(split, ["train", "validation"]) & ~frame.censored.to_numpy()
        test = (split == "test") & ~frame.censored.to_numpy()
        assert not set(frame.id[train]) & set(frame.id[test])
        outputs = {
            "WT_null": np.zeros(test.sum()),
            "development_mean": np.full(test.sum(), y[train].mean()),
        }
        for name, groups in categories.items():
            lookup = (
                pd.DataFrame({"group": groups[train], "target": y[train]})
                .groupby("group")
                .target.mean()
            )
            outputs[name] = (
                pd.Series(groups[test]).map(lookup).fillna(y[train].mean()).to_numpy()
            )
        for direction in [1, -1]:
            for name, prediction in outputs.items():
                metrics.append(
                    {
                        "protocol": protocol,
                        "seed": int(seed),
                        "features": name,
                        "direction": direction,
                        **evaluate(y[test], prediction, 50 * direction, direction),
                    }
                )
        predictions.extend(
            {
                "protocol": protocol,
                "seed": int(seed),
                "features": name,
                "id": ident,
                "actual": float(actual),
                "predicted": float(p),
            }
            for name, output in outputs.items()
            for ident, actual, p in zip(frame.id[test], y[test], output, strict=True)
        )
    pd.DataFrame(metrics).to_csv(OUT / "bk_shortcut_metrics.csv", index=False)
    pd.DataFrame(predictions).to_csv(OUT / "bk_shortcut_predictions.csv", index=False)
    # Prospective author examples are an evidence audit, not our prospective test.
    cases = [
        ("L235H", 13, 6, 42),
        ("L235F", 56, 8, 59),
        ("V236H", -35, 7, -16),
        ("V236N", -11, 7, -15),
    ]
    records = []
    for ident, observed, se, published in cases:
        selected = frame[(frame.resN == int(ident[1:-1])) & ~frame.censored]
        records.append(
            {
                "id": ident,
                "experimental_mV": observed,
                "reported_error_mV": se,
                "published_prediction_mV": published,
                "same_site_numeric_training_n": len(selected),
                "same_site_raw_table_mean_mV": (
                    float(selected.target.mean()) if len(selected) else None
                ),
                "WT_null_mV": 0,
                "site_was_seen": True,
            }
        )
    (OUT / "bk_prospective_evidence_audit.json").write_text(
        json.dumps(
            {
                "scope": "Authors' four selected prospective cases at two previously observed sites; not a new-site panel and not our own prospective validation",
                "cases": records,
                "source_discrepancy": "Table2 V236A=-38+/-1 mV, released data_scores.csv V236A=-50mV; preserve original dataset, do not silently reconcile measurement conditions. L235W is a censored bound and is excluded from numeric means.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
