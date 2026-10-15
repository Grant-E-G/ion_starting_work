"""Independent membrane-function gain selection with explicit functional tradeoffs."""

from __future__ import annotations

import argparse
import json
import re
import time

import numpy as np
import pandas as pd
from adrb2_data import BASE, wt_sequence
from data import AA, FEATURES, OUT, RAW
from metrics import precision_at_k
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def selection(prediction: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    both = len(np.unique(labels)) == 2
    return {
        "prevalence": float(labels.mean()),
        "P10": precision_at_k(prediction, labels, 10),
        "P20": precision_at_k(prediction, labels, 20),
        "P50": precision_at_k(prediction, labels, 50),
        "AP": (
            float(average_precision_score(labels, prediction)) if both else float("nan")
        ),
        "AUC": float(roc_auc_score(labels, prediction)) if both else float("nan"),
    }


def feature_blocks(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    sequence = wt_sequence()
    pca = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")
    wt = np.array([AA.index(ident[0]) for ident in frame.id])
    alt = np.array([AA.index(a) for a in frame.alt])
    conservation = pd.read_csv(
        BASE / "repo/ancillary/cons/species_js.tsv", sep="\t", header=None
    )
    assert "".join(conservation[1]) == sequence
    cheap = np.column_stack(
        [
            np.eye(20)[wt],
            np.eye(20)[alt],
            pca[alt] - pca[wt],
            frame.site.to_numpy() / len(sequence),
            conservation[0].to_numpy()[frame.site.to_numpy() - 1],
        ]
    )
    blocks = {"WT_null": np.zeros((len(frame), 1)), "cheap": cheap}
    ev = pd.read_csv(BASE / "repo/ancillary/EV-Mut_PLM_b08.csv").set_index("mutant")
    blocks["EVmutation"] = frame.id.map(ev.prediction_epistatic).to_numpy()[:, None]
    for model in ["esm2_35m", "esm1v_650m"]:
        path = FEATURES / f"adrb2_{model}_mutant_embeddings.npz"
        if not path.exists():
            continue
        with np.load(path) as file:
            index = pd.Index(file["ids"]).get_indexer(frame.id)
            assert (index >= 0).all()
            blocks[model] = np.column_stack(
                [cheap, file["pooled"][index], file["mutated_sites"][index]]
            )
    for model in ["esm2_3b"]:
        path = FEATURES / f"adrb2_{model}.npz"
        if not path.exists():
            continue
        with np.load(path) as file:
            sites = frame.site.to_numpy() - 1
            values = file["masked_logp"][sites]
            llr = values[np.arange(len(frame)), alt] - values[np.arange(len(frame)), wt]
            blocks[model] = np.column_stack([cheap, llr, file["wt_hidden"][sites]])
    for model in ["metl_global1d", "metl_global3d"]:
        path = FEATURES / f"adrb2_{model}.npz"
        if not path.exists():
            continue
        with np.load(path) as file:
            index = pd.Index(file["ids"]).get_indexer(frame.id)
            # NaN marks structure absence; full-protein comparisons explicitly
            # exclude these methods rather than inventing physical descriptors.
            valid = index >= 0
            physical_blocks = {
                key: file[key]
                for key in (
                    ["closed", "state_difference"]
                    if model.endswith("3d")
                    else ["closed"]
                )
            }
            if model.endswith("3d"):
                physical_blocks["two_state"] = np.column_stack(
                    [file["closed"], file["open"]]
                )
            for key, matrix in physical_blocks.items():
                values = np.full((len(frame), matrix.shape[1]), np.nan)
                values[valid] = matrix[index[valid]]
                name = f"{model}_{key}"
                blocks[name] = np.column_stack([cheap, values])
                for base in ["esm2_35m", "esm1v_650m", "esm2_3b"]:
                    if base in blocks:
                        blocks[f"{base}_{name}"] = np.column_stack(
                            [blocks[base], values]
                        )
    return blocks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--objective", choices=["potency", "basal"], default="potency")
    parser.add_argument("--tag", default="")
    parser.add_argument("--feature-pattern", default=".*")
    args = parser.parse_args()
    suffix = "" if args.objective == "potency" else "_basal"
    if args.tag:
        suffix += f"_{args.tag}"
    frame = pd.read_csv(OUT / "adrb2_measurements.csv")
    frame["basal_gain"] = (frame.rep1_basal_WT >= 1.5) & (frame.rep2_basal_WT >= 1.5)
    frame["basal_gain_capacity"] = (
        frame.basal_gain & (frame.rep1_emax_WT >= 0.8) & (frame.rep2_emax_WT >= 0.8)
    )
    label = frame.gain if args.objective == "potency" else frame.basal_gain
    joint_label = (
        frame.joint_gain if args.objective == "potency" else frame.basal_gain_capacity
    )
    target_column = 0 if args.objective == "potency" else 1
    arrays = {
        name: values
        for name, values in feature_blocks(frame).items()
        if re.fullmatch(args.feature_pattern, name)
    }
    rows: list[dict] = []
    predictions: list[dict] = []
    settings: list[dict] = []
    thresholds = np.log2([1.2, 1.2, 0.8])
    for scope in ["resolved_core", "all_sites_sequence_only"]:
        eligible = frame.quality.to_numpy() & (
            frame.structure_eligible.to_numpy() if scope == "resolved_core" else True
        )
        targets = frame[["activity", "basal", "emax"]].to_numpy()
        for seed in [10, 24, 36, 42, 56]:
            train = np.flatnonzero(eligible & (frame.split == "train").to_numpy())
            train = np.random.RandomState(seed).permutation(train)[:1000]
            validation = np.flatnonzero(
                eligible & (frame.split == "validation").to_numpy()
            )
            test = np.flatnonzero(eligible & (frame.split == "test").to_numpy())
            center, spread = targets[train].mean(0), targets[train].std(0)
            normalized = (targets - center) / spread
            for name, x in arrays.items():
                if scope == "all_sites_sequence_only" and "metl" in name:
                    continue
                if name != "EVmutation" and not np.isfinite(x[eligible]).all():
                    continue
                for learner in (
                    ["null"]
                    if name == "WT_null"
                    else ["ridge", "extra"] if x.shape[1] < 200 else ["ridge"]
                ):
                    start = time.perf_counter()
                    if learner == "null":
                        prediction = np.zeros((len(test), 3))
                        width = np.quantile(abs(targets[validation]), 0.9, axis=0)
                        choice: dict = {"model": "WT reference"}
                    else:
                        if learner == "ridge":
                            candidates = [
                                make_pipeline(
                                    SimpleImputer(),
                                    StandardScaler(),
                                    Ridge(alpha=alpha),
                                )
                                for alpha in [1, 10, 100, 1000]
                            ]
                        else:
                            candidates = [
                                make_pipeline(
                                    SimpleImputer(),
                                    ExtraTreesRegressor(
                                        n_estimators=300,
                                        min_samples_leaf=leaf,
                                        max_features=1.0,
                                        random_state=seed,
                                        n_jobs=3,
                                    ),
                                )
                                for leaf in [1, 3]
                            ]
                        outcomes = []
                        for model in candidates:
                            model.fit(x[train], normalized[train])
                            pv = model.predict(x[validation]) * spread + center
                            utility = precision_at_k(
                                pv[:, target_column], label.to_numpy()[validation], 20
                            )
                            loss = float(
                                np.mean(((pv - targets[validation]) / spread) ** 2)
                            )
                            outcomes.append((-utility, loss, model, pv))
                        neg_utility, loss, model, pv = min(
                            outcomes, key=lambda item: item[:2]
                        )
                        prediction = model.predict(x[test]) * spread + center
                        width = np.quantile(abs(pv - targets[validation]), 0.9, axis=0)
                        choice = {
                            "model": str(model),
                            "validation_gain_P20": -neg_utility,
                            "validation_normalized_MSE": loss,
                        }
                    joint = (
                        np.minimum.reduce(
                            [
                                prediction[:, 0] - thresholds[0],
                                thresholds[1] - prediction[:, 1],
                                prediction[:, 2] - thresholds[2],
                            ]
                        )
                        if args.objective == "potency"
                        else np.minimum(
                            prediction[:, 1] - np.log2(1.5),
                            prediction[:, 2] - np.log2(0.8),
                        )
                    )
                    for objective, score, labels in [
                        (
                            "response_gain",
                            prediction[:, target_column],
                            label.to_numpy()[test],
                        ),
                        ("gain_under_constraints", joint, joint_label.to_numpy()[test]),
                    ]:
                        rows.append(
                            {
                                "scope": scope,
                                "seed": seed,
                                "features": name,
                                "learner": learner,
                                "objective": objective,
                                "train_n": len(train),
                                "validation_n": len(validation),
                                "test_n": len(test),
                                "activity_MAE_log2": float(
                                    abs(targets[test, 0] - prediction[:, 0]).mean()
                                ),
                                "activity_90_coverage": float(
                                    (
                                        abs(targets[test, 0] - prediction[:, 0])
                                        <= width[0]
                                    ).mean()
                                ),
                                "activity_90_halfwidth": float(width[0]),
                                "seconds": time.perf_counter() - start,
                                **selection(score, labels),
                            }
                        )
                    settings.append(
                        {
                            "scope": scope,
                            "seed": seed,
                            "features": name,
                            "learner": learner,
                            **choice,
                        }
                    )
                    predictions.extend(
                        {
                            "scope": scope,
                            "seed": seed,
                            "features": name,
                            "learner": learner,
                            "id": ident,
                            "site": int(site),
                            "actual_activity": float(y[0]),
                            "actual_basal": float(y[1]),
                            "actual_emax": float(y[2]),
                            "predicted_activity": float(pr[0]),
                            "predicted_basal": float(pr[1]),
                            "predicted_emax": float(pr[2]),
                            "joint_score": float(js),
                            "gain": bool(gain),
                            "joint_gain": bool(jg),
                        }
                        for ident, site, y, pr, js, gain, jg in zip(
                            frame.id[test],
                            frame.site[test],
                            targets[test],
                            prediction,
                            joint,
                            label[test],
                            joint_label[test],
                            strict=True,
                        )
                    )
            pd.DataFrame(rows).to_csv(OUT / f"adrb2_metrics{suffix}.csv", index=False)
            pd.DataFrame(predictions).to_csv(
                OUT / f"adrb2_predictions{suffix}.csv", index=False
            )
            (OUT / f"adrb2_model_selection{suffix}.json").write_text(
                json.dumps(settings, indent=2) + "\n"
            )
            print(scope, seed, "completed", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
