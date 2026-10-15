"""Apples-to-apples split/physical ablation using recovered published features."""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from bk import published_rf
from bk_audit import ENERGY_COLUMNS, PUBLISHED_COLUMNS
from data import DATA, OUT, load_bk
from metrics import evaluate
from threadpoolctl import threadpool_limits


def main() -> None:
    frame = load_bk()
    primary = [
        c
        for c in PUBLISHED_COLUMNS
        if c not in ENERGY_COLUMNS and not c.startswith("cov")
    ]
    columns = {
        "WT_geometry_evolution": primary,
        "energy_only": ENERGY_COLUMNS,
        "geometry_evolution_energy": primary + ENERGY_COLUMNS,
        "published_full_secondary": PUBLISHED_COLUMNS,
    }
    parts = pd.concat(
        [
            pd.read_csv(DATA / "bk_partitions.csv"),
            pd.read_csv(DATA / "bk_published_partitions.csv"),
        ],
        ignore_index=True,
    )
    rows: list[dict] = []
    predictions: list[dict] = []
    for protocol in parts.protocol.unique():
        for seed in sorted(parts.seed.unique()):
            split = frame.id.map(
                parts[(parts.protocol == protocol) & (parts.seed == seed)]
                .set_index("id")
                .split
            ).to_numpy()
            # Fixed published RF requires no model/parameter selection. Train on
            # both development groups to match the original 80/20 data budget.
            train, test = np.isin(split, ["train", "validation"]), split == "test"
            for handling in ["uncensored", "paper_flags_diagnostic"]:
                valid = (
                    ~frame.censored.to_numpy()
                    if handling == "uncensored"
                    else np.ones(len(frame), dtype=bool)
                )
                fit, hold = train & valid, test & valid
                for transform in ["raw", "published_tanh200"]:
                    yraw = frame.target.to_numpy()
                    y = yraw if transform == "raw" else 200 * np.tanh(yraw / 200)
                    threshold = (
                        50.0 if transform == "raw" else float(200 * np.tanh(50 / 200))
                    )
                    for name, names in columns.items():
                        start = time.perf_counter()
                        x = frame[names].to_numpy()
                        # Tree partitions are invariant to affine normalization;
                        # explicit scaling matches the released pipeline.
                        from sklearn.preprocessing import StandardScaler

                        scale = StandardScaler().fit(x[fit])
                        model = published_rf(1729).fit(scale.transform(x[fit]), y[fit])
                        p = model.predict(scale.transform(x[hold]))
                        for direction in [1, -1]:
                            rows.append(
                                {
                                    "protocol": protocol,
                                    "seed": seed,
                                    "handling": handling,
                                    "target": transform,
                                    "features": name,
                                    "direction": direction,
                                    "train_n": int(fit.sum()),
                                    "seconds": time.perf_counter() - start,
                                    **evaluate(
                                        y[hold], p, direction * threshold, direction
                                    ),
                                }
                            )
                        predictions.extend(
                            {
                                "protocol": protocol,
                                "seed": seed,
                                "handling": handling,
                                "target": transform,
                                "features": name,
                                "id": ident,
                                "actual": actual,
                                "predicted": predicted,
                            }
                            for ident, actual, predicted in zip(
                                frame.id[hold], y[hold], p, strict=True
                            )
                        )
            pd.DataFrame(rows).to_csv(OUT / "bk_matched_metrics.csv", index=False)
            pd.DataFrame(predictions).to_csv(
                OUT / "bk_matched_predictions.csv", index=False
            )
            print(protocol, seed, "completed", flush=True)
    (OUT / "bk_matched_settings.json").write_text(
        json.dumps(
            {
                "feature_columns": columns,
                "learner": "Exact released fixed RF hyperparameters, seed1729",
                "model_selection": "None; train+validation joined before fitting, outer tests untouched",
                "primary": "uncensored raw-mV comparisons, same splits and data budgets",
                "diagnostic": "Published flags/tanh to reproduce paper; no claim censor flags are exact voltages",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
