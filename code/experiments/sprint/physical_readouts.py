"""Predeclared-sign physical readouts without new experimental model training.

Mechanistic follow-up on the already inspected GB1 combination benchmark,
not a fresh independent confirmation. Source METL weights never saw function
labels; output units are normalized physical-pretraining targets.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import FEATURES, OUT
from metrics import precision_at_k
from scipy.stats import spearmanr
from sklearn.metrics import average_precision_score


def main() -> None:
    frame = pd.read_csv(OUT / "combination_predictions.csv")
    gain = frame.actual.to_numpy() >= np.log(1.2)
    parents = np.maximum(frame[["parent1", "parent2"]].max(axis=1).to_numpy(), 0)
    beyond = frame.actual.to_numpy() >= parents + np.log(1.2)
    specifications = [
        ("stability", "negative_total_score", 0),
        ("binding", "negative_total_score", 0),
        ("binding", "negative_dG_cross", 56),
        ("binding", "negative_dG_separated", 58),
        ("binding", "negative_dG_separated_per_area", 59),
    ]
    rows: list[dict] = []
    predictions: list[dict] = []
    for family, label, index in specifications:
        with np.load(FEATURES / f"gb1_combinations_metl_{family}.npz") as values:
            order = pd.Index(values["ids"]).get_indexer(frame.id)
            assert (order >= 0).all()
            score = -values["attributes"][order, index]
        rows.append(
            {
                "family": family,
                "readout": label,
                "experimental_training_n": 0,
                "n": len(frame),
                "WT_gain_prevalence": float(gain.mean()),
                "WT_gain_P20": precision_at_k(score, gain, 20),
                "WT_gain_P100": precision_at_k(score, gain, 100),
                "WT_gain_AP": float(average_precision_score(gain, score)),
                "spearman": float(spearmanr(frame.actual, score).statistic),
                "beyond_parent_P20": precision_at_k(score, beyond, 20),
                "beyond_parent_scope": "Rank by physical score only; normalized surrogate units cannot be subtracted from experimental log-enrichment parents",
            }
        )
        predictions.extend(
            {
                "id": ident,
                "family": family,
                "readout": label,
                "physical_score": float(value),
            }
            for ident, value in zip(frame.id, score, strict=True)
        )
    pd.DataFrame(rows).to_csv(OUT / "physical_readout_metrics.csv", index=False)
    pd.DataFrame(predictions).to_csv(
        OUT / "physical_readout_predictions.csv", index=False
    )
    (OUT / "physical_readout_scope.json").write_text(
        json.dumps(
            {
                "scope": "Exploratory follow-up on inspected GB1 combination labels; no supervised fitting or sign selection; not a new membrane-function result",
                "source": "METL README output ordering, standard55 followed by17binding attributes",
                "hypothesis": "Function-matched binding energies should carry information absent from generic folding energies",
                "units": "Normalized checkpoint targets, no calibrated kcal/mol, affinity or enrichment prediction",
            },
            indent=2,
        )
        + "\n"
    )
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
