"""Falsify whether an exact WT-null constraint improves BK mutation effects.

The unchanged protein has zero shift regardless of the nominal mutation site.
Compare a published fixed RF, subtracting its matching WT prediction, and adding
one self-mutation control per development site. No new experimental labels.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from bk import published_rf
from bk_audit import ENERGY_COLUMNS, PUBLISHED_COLUMNS
from data import AA, DATA, OUT, RAW, load_bk, write_immutable
from metrics import evaluate
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def scans() -> pd.DataFrame:
    values = pd.concat(
        [pd.read_csv(RAW / f"bkpred/data/scans/{a}.csv") for a in AA]
    ).set_index("Mutation", drop=False)
    assert values.index.is_unique
    return values


def main() -> None:
    source, frame = scans(), load_bk()
    assert (
        np.max(
            abs(
                source.loc[frame.id, PUBLISHED_COLUMNS].to_numpy()
                - frame[PUBLISHED_COLUMNS].to_numpy()
            )
        )
        == 0
    )
    native_ids = frame.id.map(lambda token: token[:-1] + token[0])
    native = source.loc[native_ids].reset_index(drop=True)
    assert np.max(abs(native[ENERGY_COLUMNS].to_numpy())) < 1e-10
    assert np.max(abs(native.dHyd)) < 1e-10
    primary = [
        c
        for c in PUBLISHED_COLUMNS
        if c not in ENERGY_COLUMNS and not c.startswith("cov")
    ]
    blocks = {
        "WT_geometry_evolution": primary,
        "geometry_evolution_energy": primary + ENERGY_COLUMNS,
        "published_full_secondary": PUBLISHED_COLUMNS,
    }
    parts = pd.concat(
        [
            pd.read_csv(DATA / "bk_partitions.csv"),
            pd.read_csv(DATA / "bk_published_partitions.csv"),
        ]
    )
    policy = {
        "hypothesis": "Exact zero-effect WT invariance may remove nuisance site offsets and improve physical mutation-to-function mapping",
        "learner": "Fixed released RF, seed1729, no hyperparameter tuning",
        "augmentation": "One native self-mutation zero-label row per unique development site; no held-out mutant labels",
        "anchoring": "prediction(mutant)-prediction(self-mutation at the same site), no fitted calibration",
        "primary": "Uncensored rawmV, train+validation joined, same immutable site/publication/random test partitions",
        "source_audit": "All473 original30-feature inputs equal published full scans exactly; native energy and hydropathy changes exactlyzero",
        "status": "Exploratory mechanistic follow-up after initial split comparisons; not a new independent test corpus",
    }
    write_immutable(DATA / "bk_null_policy.json", json.dumps(policy, indent=2) + "\n")
    rows: list[dict] = []
    predictions: list[dict] = []
    y = frame.target.to_numpy()
    for (protocol, seed), partition in parts.groupby(["protocol", "seed"]):
        split = frame.id.map(partition.set_index("id").split).to_numpy()
        train = np.isin(split, ["train", "validation"]) & ~frame.censored.to_numpy()
        test = (split == "test") & ~frame.censored.to_numpy()
        self_rows = np.flatnonzero(train)[~native_ids[train].duplicated().to_numpy()]
        for block, columns in blocks.items():
            x, wt = frame[columns].to_numpy(), native[columns].to_numpy()
            for augmentation in [False, True]:
                fit_x = (
                    np.concatenate([x[train], wt[self_rows]])
                    if augmentation
                    else x[train]
                )
                fit_y = (
                    np.concatenate([y[train], np.zeros(len(self_rows))])
                    if augmentation
                    else y[train]
                )
                scaler = StandardScaler().fit(fit_x)
                model = published_rf(1729).fit(scaler.transform(fit_x), fit_y)
                p, reference = model.predict(scaler.transform(x[test])), model.predict(
                    scaler.transform(wt[test])
                )
                for anchor in [False, True]:
                    output = p - reference if anchor else p
                    label = f"{block}{'_WTaugment' if augmentation else ''}{'_WTanchor' if anchor else ''}"
                    for direction in [1, -1]:
                        rows.append(
                            {
                                "protocol": protocol,
                                "seed": int(seed),
                                "features": label,
                                "direction": direction,
                                "training_mutants": int(train.sum()),
                                "WT_controls": len(self_rows) if augmentation else 0,
                                "unanchored_WT_prediction_RMS_mV": float(
                                    np.sqrt(np.mean(reference**2))
                                ),
                                **evaluate(y[test], output, 50 * direction, direction),
                            }
                        )
                    predictions.extend(
                        {
                            "protocol": protocol,
                            "seed": int(seed),
                            "features": label,
                            "id": ident,
                            "actual": float(actual),
                            "predicted": float(value),
                            "WT_prediction": float(ref),
                        }
                        for ident, actual, value, ref in zip(
                            frame.id[test], y[test], output, reference, strict=True
                        )
                    )
        pd.DataFrame(rows).to_csv(OUT / "bk_null_metrics.csv", index=False)
        pd.DataFrame(predictions).to_csv(OUT / "bk_null_predictions.csv", index=False)
        print(protocol, seed, "completed", flush=True)
    # Four author experiments are retrospective source reproduction, never used
    # to tune this fixed learner; later L235A is an inequality, not an exact150.
    novel = source.loc[["L235H", "L235F", "V236H", "V236N", "L235A"]]
    wt = source.loc[[v[:-1] + v[0] for v in novel.index]]
    experimental = [13, 56, -35, -11, 150]
    audit = []
    for block, columns in blocks.items():
        for handling in ["uncensored_raw", "paper_squashed_flags_diagnostic"]:
            valid = (
                ~frame.censored.to_numpy()
                if handling == "uncensored_raw"
                else np.ones(len(frame), dtype=bool)
            )
            response = y if handling == "uncensored_raw" else 200 * np.tanh(y / 200)
            scaler = StandardScaler().fit(frame.loc[valid, columns])
            model = published_rf(1729).fit(
                scaler.transform(frame.loc[valid, columns]), response[valid]
            )
            p, ref = model.predict(scaler.transform(novel[columns])), model.predict(
                scaler.transform(wt[columns])
            )
            for ident, actual, prediction, reference in zip(
                novel.index, experimental, p, ref, strict=True
            ):
                audit.append(
                    {
                        "features": block,
                        "training": handling,
                        "id": ident,
                        "measured_mV": actual if ident != "L235A" else None,
                        "measured_lower_bound_mV": 150 if ident == "L235A" else None,
                        "predicted": float(prediction),
                        "WT_anchor_predicted": float(prediction - reference),
                        "units": (
                            "mV"
                            if handling == "uncensored_raw"
                            else "Published squashed target scale; do not call exact rawmV"
                        ),
                    }
                )
    pd.DataFrame(audit).to_csv(OUT / "bk_authors_novel_reproduction.csv", index=False)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
