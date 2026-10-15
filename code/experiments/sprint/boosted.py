"""Does a nonlinear, low-dimensional learner reveal a physical increment?

Prior large sequence features had mainly linear readouts. Training-only PCA
plus histogram boosting tests this learner limitation, without a new simulator.
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from bk import features
from data import DATA, OUT, load_bk, write_immutable
from metrics import precision_at_k, site_diverse_precision
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, log_loss
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def main() -> None:
    frame = load_bk()
    available = features(frame)
    cheap = available["cheap"]
    bases = [
        name
        for name in [
            "cheap",
            "esm2_35m_mutant",
            "esm1v_650m_mutant",
            "esm2_3b_sequence",
        ]
        if name in available
    ]
    energies = {
        "none": np.zeros((len(frame), 0)),
        "audited": available["audited_energy"],
        "local": available["cheap_local_energy"][:, cheap.shape[1] :],
        "metl_state": available["metl_global3d_state"],
    }
    policy = {
        "hypothesis": "Energy information may be nonlinear and obscured by large sequence dimensionality",
        "sequence_projection": "Training-only StandardScaler plus randomizedPCA32, randomseed=fold, retaining cheap AA/hydropathy/conservation features separately",
        "classifier": "Histogram gradient boosting, lr.05,150iterations,minleaf10,classbalanced,no internal early stopping",
        "grid": "7/15 leaf nodes x L2=1/10, validation AP then logloss",
        "data": "Same strict site/publication-component partitions and uncensored445 source mutants; validation is not joined to training",
        "utility": "Signed shifts>=50mV, not established therapeutic benefit",
        "status": "Exploratory learner-family test on an already inspected corpus; no new independent validation",
    }
    write_immutable(DATA / "boosted_policy.json", json.dumps(policy, indent=2) + "\n")
    parts = pd.read_csv(DATA / "bk_partitions.csv")
    rows: list[dict] = []
    predictions: list[dict] = []
    choices: list[dict] = []
    for (protocol, seed), partition in parts.groupby(["protocol", "seed"]):
        split = frame.id.map(partition.set_index("id").split).to_numpy()
        train, val, test = [
            np.flatnonzero((split == name) & ~frame.censored.to_numpy())
            for name in ["train", "validation", "test"]
        ]
        for base in bases:
            x = available[base]
            if base != "cheap":
                scale = StandardScaler().fit(x[train, cheap.shape[1] :])
                pca = PCA(
                    n_components=min(32, len(train) - 1),
                    svd_solver="randomized",
                    random_state=int(seed),
                ).fit(scale.transform(x[train, cheap.shape[1] :]))
                x = np.column_stack(
                    [cheap, pca.transform(scale.transform(x[:, cheap.shape[1] :]))]
                )
            for physical, values in energies.items():
                inputs = np.column_stack([x, values])
                for direction in [1, -1]:
                    positive = direction * frame.target.to_numpy() >= 50
                    start = time.perf_counter()
                    outcomes = []
                    for leaves in [7, 15]:
                        for regularization in [1, 10]:
                            model = HistGradientBoostingClassifier(
                                learning_rate=0.05,
                                max_iter=150,
                                max_leaf_nodes=leaves,
                                min_samples_leaf=10,
                                l2_regularization=regularization,
                                class_weight="balanced",
                                early_stopping=False,
                                random_state=int(seed),
                            ).fit(inputs[train], positive[train])
                            pv = model.predict_proba(inputs[val])[:, 1]
                            outcomes.append(
                                (
                                    -float(average_precision_score(positive[val], pv)),
                                    float(
                                        log_loss(
                                            positive[val],
                                            np.clip(pv, 1e-8, 1 - 1e-8),
                                            labels=[False, True],
                                        )
                                    ),
                                    model,
                                )
                            )
                    neg_ap, loss, chosen = min(outcomes, key=lambda item: item[:2])
                    score = chosen.predict_proba(inputs[test])[:, 1]
                    rows.append(
                        {
                            "protocol": protocol,
                            "seed": int(seed),
                            "base": base,
                            "physical": physical,
                            "direction": direction,
                            "test_n": len(test),
                            "prevalence": float(positive[test].mean()),
                            "P20": precision_at_k(score, positive[test], 20),
                            "site_diverse_P10": site_diverse_precision(
                                score, positive[test], frame.resN.to_numpy()[test], 10
                            ),
                            "AP": float(average_precision_score(positive[test], score)),
                            "seconds": time.perf_counter() - start,
                        }
                    )
                    choices.append(
                        {
                            "protocol": protocol,
                            "seed": int(seed),
                            "base": base,
                            "physical": physical,
                            "direction": direction,
                            "validation_AP": -neg_ap,
                            "validation_logloss": loss,
                            "model": str(chosen),
                        }
                    )
                    predictions.extend(
                        {
                            "protocol": protocol,
                            "seed": int(seed),
                            "base": base,
                            "physical": physical,
                            "direction": direction,
                            "id": ident,
                            "actual": bool(label),
                            "probability_uncalibrated": float(value),
                        }
                        for ident, label, value in zip(
                            frame.id[test], positive[test], score, strict=True
                        )
                    )
        pd.DataFrame(rows).to_csv(OUT / "boosted_metrics.csv", index=False)
        pd.DataFrame(predictions).to_csv(OUT / "boosted_predictions.csv", index=False)
        (OUT / "boosted_choices.json").write_text(json.dumps(choices, indent=2) + "\n")
        print(protocol, seed, "completed", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
