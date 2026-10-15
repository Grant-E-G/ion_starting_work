"""Utility-focused functional-change classification, beyond damage-dominated MSE."""

from __future__ import annotations

import argparse
import json
import re
import time
import warnings

import numpy as np
import pandas as pd
from adrb2_compare import feature_blocks, selection
from bk import features
from data import DATA, OUT, load_bk
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

warnings.filterwarnings("ignore", category=ConvergenceWarning)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["bk", "adrb2"], required=True)
    parser.add_argument("--tag", default="")
    parser.add_argument("--feature-pattern", default=".*")
    args = parser.parse_args()
    if args.dataset == "bk":
        frame = load_bk()
        available = features(frame)
        names = [
            "cheap",
            "cheap_audited_energy",
            "cheap_local_energy",
            "cheap_metl_global3d_state",
            "esm2_35m_mutant",
            "esm2_35m_mutant_audited_energy",
            "esm2_35m_mutant_metl_global3d_state",
            "esm1v_650m_sequence",
            "esm1v_650m_sequence_audited_energy",
            "esm1v_650m_mutant",
            "esm1v_650m_mutant_audited_energy",
            "esm2_3b_sequence",
            "esm2_3b_sequence_audited_energy",
        ]
        arrays = {key: available[key] for key in names if key in available}
        parts = pd.read_csv(DATA / "bk_partitions.csv")
        cases = [
            (
                protocol,
                int(fold),
                frame.id.map(rows.set_index("id").split).to_numpy(),
                ~frame.censored.to_numpy(),
            )
            for (protocol, fold), rows in parts.groupby(["protocol", "seed"])
        ]
        labels = {
            "positive_shift50mV": frame.target.to_numpy() >= 50,
            "negative_shift50mV": frame.target.to_numpy() <= -50,
        }
    else:
        frame = pd.read_csv(OUT / "adrb2_measurements.csv")
        arrays = feature_blocks(frame)
        arrays.pop("WT_null")
        arrays = {
            key: value
            for key, value in arrays.items()
            if key
            in [
                "cheap",
                "EVmutation",
                "esm2_35m",
                "esm1v_650m",
                "esm2_3b",
                "metl_global3d_state_difference",
                "metl_global3d_closed",
                "metl_global1d_closed",
                "esm2_35m_metl_global3d_state_difference",
                "esm2_3b_metl_global3d_state_difference",
                "esm1v_650m_metl_global3d_state_difference",
                "metl_global3d_two_state",
                "esm2_3b_metl_global3d_two_state",
                "esm1v_650m_metl_global3d_two_state",
            ]
        }
        cases = [
            (
                scope,
                seed,
                frame.split.to_numpy(),
                frame.quality.to_numpy()
                & (
                    frame.structure_eligible.to_numpy()
                    if scope == "resolved_core"
                    else True
                ),
            )
            for scope in ["resolved_core", "all_sites_sequence_only"]
            for seed in [10, 24, 36, 42, 56]
        ]
        basal = (frame.rep1_basal_WT >= 1.5) & (frame.rep2_basal_WT >= 1.5)
        labels = {
            "response_gain20percent": frame.gain.to_numpy(),
            "potency_gain_constraints": frame.joint_gain.to_numpy(),
            "basal_gain50percent": basal.to_numpy(),
            "basal_gain_capacity": (
                basal & (frame.rep1_emax_WT >= 0.8) & (frame.rep2_emax_WT >= 0.8)
            ).to_numpy(),
        }
    arrays = {
        key: value
        for key, value in arrays.items()
        if re.fullmatch(args.feature_pattern, key)
    }
    suffix = f"_{args.tag}" if args.tag else ""
    rows: list[dict] = []
    predictions: list[dict] = []
    choices: list[dict] = []
    for protocol, seed, split, eligible in cases:
        train, val, test = [
            np.flatnonzero((split == label) & eligible)
            for label in ["train", "validation", "test"]
        ]
        if args.dataset == "adrb2":
            train = np.random.RandomState(seed).permutation(train)[:1000]
        for objective, y in labels.items():
            for name, x in {
                "constant_prior": np.zeros((len(frame), 1)),
                **arrays,
            }.items():
                if protocol == "all_sites_sequence_only" and "metl" in name:
                    continue
                if name != "EVmutation" and not np.isfinite(x[eligible]).all():
                    continue
                for learner in (
                    ["prior"]
                    if name == "constant_prior"
                    else ["logistic", "extra"] if x.shape[1] < 250 else ["logistic"]
                ):
                    start = time.perf_counter()
                    positive = int(y[train].sum())
                    if positive in [0, len(train)] or learner == "prior":
                        p = np.full(len(test), (positive + 0.5) / (len(train) + 1))
                        chosen: dict = {
                            "reason": (
                                "No trainable contrast"
                                if positive in [0, len(train)]
                                else "Training prevalence prior"
                            )
                        }
                    else:
                        if learner == "logistic":
                            candidates = [
                                make_pipeline(
                                    SimpleImputer(),
                                    StandardScaler(),
                                    LogisticRegression(
                                        C=c,
                                        class_weight="balanced",
                                        solver="liblinear",
                                        max_iter=1000,
                                        random_state=seed,
                                    ),
                                )
                                for c in [0.01, 0.1, 1, 10]
                            ]
                        else:
                            candidates = [
                                make_pipeline(
                                    SimpleImputer(),
                                    ExtraTreesClassifier(
                                        n_estimators=300,
                                        min_samples_leaf=leaf,
                                        max_features="sqrt",
                                        class_weight="balanced",
                                        random_state=seed,
                                        n_jobs=3,
                                    ),
                                )
                                for leaf in [1, 3]
                            ]
                        fitted = []
                        for model in candidates:
                            model.fit(x[train], y[train])
                            pv = model.predict_proba(x[val])[:, 1]
                            ap = (
                                float(average_precision_score(y[val], pv))
                                if y[val].any()
                                else 0.0
                            )
                            loss = log_loss(
                                y[val],
                                np.clip(pv, 1e-8, 1 - 1e-8),
                                labels=[False, True],
                            )
                            fitted.append((-ap, loss, model))
                        neg_ap, loss, model = min(fitted, key=lambda item: item[:2])
                        p = model.predict_proba(x[test])[:, 1]
                        chosen = {
                            "validation_AP": -neg_ap,
                            "validation_logloss": loss,
                            "model": str(model),
                        }
                    metrics = selection(p, y[test])
                    predicted_gain = p >= 0.5
                    rows.append(
                        {
                            "protocol": protocol,
                            "seed": seed,
                            "objective": objective,
                            "features": name,
                            "learner": learner,
                            "train_n": len(train),
                            "train_positives": positive,
                            "validation_positives": int(y[val].sum()),
                            "test_n": len(test),
                            "test_positives": int(y[test].sum()),
                            "Brier_uncalibrated": float(brier_score_loss(y[test], p)),
                            "predicted_positive_n": int(predicted_gain.sum()),
                            "predicted_positive_precision": (
                                float(y[test][predicted_gain].mean())
                                if predicted_gain.any()
                                else None
                            ),
                            "seconds": time.perf_counter() - start,
                            **metrics,
                        }
                    )
                    predictions.extend(
                        {
                            "protocol": protocol,
                            "seed": seed,
                            "objective": objective,
                            "features": name,
                            "learner": learner,
                            "id": ident,
                            "actual": bool(actual),
                            "probability_uncalibrated": float(probability),
                        }
                        for ident, actual, probability in zip(
                            frame.id[test], y[test], p, strict=True
                        )
                    )
                    choices.append(
                        {
                            "protocol": protocol,
                            "seed": seed,
                            "objective": objective,
                            "features": name,
                            "learner": learner,
                            **chosen,
                        }
                    )
        pd.DataFrame(rows).to_csv(
            OUT / f"{args.dataset}_classification_metrics{suffix}.csv", index=False
        )
        pd.DataFrame(predictions).to_csv(
            OUT / f"{args.dataset}_classification_predictions{suffix}.csv", index=False
        )
        (OUT / f"{args.dataset}_classification_choices{suffix}.json").write_text(
            json.dumps(choices, indent=2) + "\n"
        )
        print(args.dataset, protocol, seed, "completed", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
