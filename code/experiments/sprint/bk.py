"""BKpred reproduction/modern baselines on strict site/publication holdouts."""

from __future__ import annotations

import argparse
import json
import time
import warnings
from typing import Any

import numpy as np
import pandas as pd
from data import AA, DATA, FEATURES, OUT, RAW, load_bk
from metrics import evaluate, grouped_bootstrap
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_selection import VarianceThreshold
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

warnings.filterwarnings("ignore", category=ConvergenceWarning)


def published_rf(seed: int) -> RandomForestRegressor:
    # Match upstream hyperparameters, with an explicit seed and bounded CPU use.
    return RandomForestRegressor(
        n_estimators=500,
        min_samples_split=2,
        max_leaf_nodes=100,
        max_depth=20,
        max_features=1,
        ccp_alpha=0.01,
        bootstrap=True,
        oob_score=True,
        max_samples=1.0,
        min_samples_leaf=1,
        criterion="squared_error",
        random_state=seed,
        n_jobs=4,
    )


def features(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    onehot = np.eye(20)
    wt = np.array([AA.index(v[0]) for v in frame.id])
    mt = np.array([AA.index(v[-1]) for v in frame.id])
    # Preserve a modern categorical baseline; upstream integer amino-acid IDs
    # otherwise permit arbitrary ordinal splits.
    cheap = np.column_stack(
        [onehot[wt], onehot[mt], frame[["WThyd", "MThyd", "dHyd", "SIFT"]]]
    )
    energy = frame.loc[:, "score":"rama_prepro"].to_numpy()
    energy = 50 * np.tanh(energy / 50)
    geometry = frame[
        ["rmsf", "psasa", "SECS", "WATX", "MEMBX", "POREX", "BURIED", "BORDER"]
    ].to_numpy()
    cov = frame[[c for c in frame if c.startswith("cov")]].to_numpy()
    result = {
        "hydrophobicity": frame[["WThyd", "MThyd", "dHyd"]].to_numpy(),
        "cheap": cheap,
        "published_energy": energy,
        "cheap_energy": np.column_stack([cheap, energy]),
        "cheap_geometry": np.column_stack([cheap, geometry]),
        "cheap_energy_geometry": np.column_stack([cheap, energy, geometry]),
        "published_full_secondary": np.column_stack(
            [
                frame[["WT", "MT", "resN", "WThyd", "MThyd", "dHyd", "SIFT"]],
                energy,
                geometry,
                cov,
            ]
        ),
    }
    for model in ["esm2_8m", "esm2_35m", "esm2_150m", "esm1v_650m", "esm2_3b"]:
        path = FEATURES / f"bk_{model}.npz"
        if not path.exists():
            continue
        with np.load(path) as file:
            sites = frame.resN.to_numpy(dtype=int) - 1
            logp = file["masked_logp"][sites]
            llr = (logp[np.arange(len(frame)), mt] - logp[np.arange(len(frame)), wt])[
                :, None
            ]
            context = file["wt_hidden"][sites]
            # WT contextual hidden states plus AA substitution identity; no
            # mutant structure or mutant contextual embedding implied.
            sequence = np.column_stack([cheap, llr, context])
        result[f"{model}_llr"] = llr
        result[f"{model}_sequence"] = sequence
        result[f"{model}_sequence_energy"] = np.column_stack([sequence, energy])
        result[f"{model}_sequence_geometry"] = np.column_stack([sequence, geometry])
        result[f"{model}_sequence_energy_geometry"] = np.column_stack(
            [sequence, energy, geometry]
        )
    path = FEATURES / "bk_evoef_r20.csv"
    if path.exists():
        local = pd.read_csv(path).set_index("mutation").loc[frame.id]
        state_cols = [c for c in local if c.startswith("state_difference_")]
        local_energy = local[state_cols].to_numpy()
        local_energy = 50 * np.tanh(local_energy / 50)
        result["cheap_local_energy"] = np.column_stack([cheap, local_energy])
        for model in ["esm2_35m", "esm1v_650m", "esm2_3b"]:
            key = f"{model}_sequence"
            if key in result:
                result[f"{model}_sequence_local_energy"] = np.column_stack(
                    [result[key], local_energy]
                )
                result[f"{model}_sequence_all_energy"] = np.column_stack(
                    [result[key], energy, local_energy]
                )
    for model in ["esm2_35m", "esm1v_650m"]:
        path = FEATURES / f"bk_{model}_mutant_embeddings.npz"
        if path.exists():
            with np.load(path) as file:
                order = pd.Index(file["ids"]).get_indexer(frame.id)
                assert (order >= 0).all()
                embedding = np.column_stack(
                    [file["pooled"][order], file["mutated_sites"][order]]
                )
            result[f"{model}_mutant"] = np.column_stack([cheap, embedding])
            result[f"{model}_mutant_energy"] = np.column_stack(
                [cheap, embedding, energy]
            )
            if "cheap_local_energy" in result:
                local_energy = result["cheap_local_energy"][:, cheap.shape[1] :]
                result[f"{model}_mutant_local_energy"] = np.column_stack(
                    [cheap, embedding, local_energy]
                )
    from bk_audit import ENERGY_COLUMNS

    audited = frame[ENERGY_COLUMNS].to_numpy()
    result["audited_energy"] = audited
    result["cheap_audited_energy"] = np.column_stack([cheap, audited])
    for base in [
        "esm2_35m_sequence",
        "esm1v_650m_sequence",
        "esm2_35m_mutant",
        "esm1v_650m_mutant",
        "esm2_3b_sequence",
    ]:
        if base in result:
            result[base + "_audited_energy"] = np.column_stack([result[base], audited])
    for family in ["global1d", "global3d"]:
        path = FEATURES / f"bk_metl_{family}.npz"
        if not path.exists():
            continue
        with np.load(path) as file:
            order = pd.Index(file["ids"]).get_indexer(frame.id)
            assert (order >= 0).all()
            blocks = {"closed": file["attributes_closed"][order]}
            if family == "global3d":
                blocks["state"] = file["state_difference"][order]
                blocks["two_state"] = np.column_stack(
                    [file["attributes_closed"][order], file["attributes_open"][order]]
                )
            for block, values in blocks.items():
                result[f"metl_{family}_{block}"] = values
                result[f"cheap_metl_{family}_{block}"] = np.column_stack(
                    [cheap, values]
                )
                for base in [
                    "esm2_35m_mutant",
                    "esm1v_650m_sequence",
                    "esm1v_650m_mutant",
                    "esm2_3b_sequence",
                ]:
                    if base in result:
                        result[f"{base}_metl_{family}_{block}"] = np.column_stack(
                            [result[base], values]
                        )
    assert all(np.isfinite(x).all() for x in result.values())
    return result


def select_model(
    kind: str,
    x: np.ndarray,
    y: np.ndarray,
    train: np.ndarray,
    validation: np.ndarray,
    seed: int,
    anchor_zero: bool = False,
    criterion: str = "mae",
    stable_features: bool = False,
) -> tuple[Any, dict]:
    if kind == "ridge":
        candidates = [
            make_pipeline(
                *([VarianceThreshold(1e-10)] if stable_features else []),
                StandardScaler(),
                Ridge(alpha=alpha),
            )
            for alpha in [1.0, 10.0, 100.0, 1000.0]
        ]
    elif kind == "rf":
        candidates = [
            published_rf(seed),
            RandomForestRegressor(
                n_estimators=300,
                min_samples_leaf=3,
                max_features=1.0,
                random_state=seed,
                n_jobs=4,
            ),
        ]
    elif kind == "extra":
        candidates = [
            ExtraTreesRegressor(
                n_estimators=300,
                min_samples_leaf=leaf,
                max_features=1.0,
                random_state=seed,
                n_jobs=4,
            )
            for leaf in [1, 3]
        ]
    elif kind == "gp":
        kernel = ConstantKernel(1.0, (0.01, 100)) * Matern(
            length_scale=5.0, length_scale_bounds=(0.1, 1000), nu=1.5
        ) + WhiteKernel(0.1, (1e-4, 10))
        candidates = [
            make_pipeline(
                StandardScaler(),
                GaussianProcessRegressor(
                    kernel=kernel,
                    normalize_y=True,
                    random_state=seed,
                    n_restarts_optimizer=0,
                ),
            )
        ]
    else:
        raise ValueError(kind)
    fitted = []
    for model in candidates:
        model.fit(x[train], y[train])
        p = model.predict(x[validation])
        if anchor_zero:
            p -= model.predict(np.zeros((1, x.shape[1])))[0]
        assert criterion in ["mae", "mse"]
        loss = (
            float(abs(y[validation] - p).mean())
            if criterion == "mae"
            else float(np.mean((y[validation] - p) ** 2))
        )
        fitted.append((loss, model))
    loss, selected = min(fitted, key=lambda item: item[0])
    # Keep validation distinct for calibration; do not refit on it silently.
    return selected, {
        f"validation_{criterion}": loss,
        "zero_anchor_validation": anchor_zero,
        "model": str(selected),
    }


def reproduce() -> None:
    rows = []
    for seed in range(5):
        folder = RAW / f"bkpred/data/split{seed}"
        x = np.load(folder / "X5_train.npy")
        y = np.load(folder / "y5_train.npy").ravel()
        xt = np.load(folder / "validation/X_test.npy")
        yt = np.load(folder / "validation/y_test.npy").ravel()
        stored = np.load(folder / "validation/py_test.npy").ravel()
        start = time.perf_counter()
        model = published_rf(1729).fit(x, y)
        prediction = model.predict(xt)
        rows.append(
            {
                "split": seed,
                "train_n": len(y),
                "test_n": len(yt),
                "feature_count": x.shape[1],
                "target_range": [float(y.min()), float(y.max())],
                "stored_mae": float(np.mean(abs(stored - yt))),
                "reproduced_mae": float(np.mean(abs(prediction - yt))),
                "stored_rmse": float(np.sqrt(np.mean((stored - yt) ** 2))),
                "reproduced_rmse": float(np.sqrt(np.mean((prediction - yt) ** 2))),
                "stored_pearson": float(np.corrcoef(stored, yt)[0, 1]),
                "reproduced_pearson": float(np.corrcoef(prediction, yt)[0, 1]),
                "fit_seconds": time.perf_counter() - start,
            }
        )
        pd.DataFrame({"actual": yt, "stored": stored, "reproduced": prediction}).to_csv(
            OUT / f"bk_published_split{seed}_predictions.csv", index=False
        )
    (OUT / "bk_published_reproduction.json").write_text(
        json.dumps(rows, indent=2) + "\n"
    )
    print(json.dumps(rows, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--kinds", nargs="+", default=["ridge", "rf"])
    parser.add_argument("--tag", default="initial")
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--feature-pattern", default=".*")
    args = parser.parse_args()
    if args.reproduce:
        reproduce()
        return
    frame = load_bk()
    arrays = features(frame)
    import re

    arrays = {
        name: x
        for name, x in arrays.items()
        if re.fullmatch(args.feature_pattern, name)
    }
    (OUT / f"bk_settings_{args.tag}.json").write_text(
        json.dumps(
            {
                "arguments": vars(args),
                "feature_dimensions": {name: x.shape[1] for name, x in arrays.items()},
            },
            indent=2,
        )
        + "\n"
    )
    parts = pd.read_csv(DATA / "bk_partitions.csv")
    results: list[dict] = []
    predictions: list[dict] = []
    selections: list[dict] = []
    for protocol in parts.protocol.unique():
        for seed in sorted(parts.seed.unique()):
            split = frame.id.map(
                parts[(parts.protocol == protocol) & (parts.seed == seed)]
                .set_index("id")
                .split
            ).to_numpy()
            valid = ~frame.censored.to_numpy()
            train, validation, test = [
                (split == label) & valid for label in ["train", "validation", "test"]
            ]
            y = frame.target.to_numpy()
            methods = [("WT_null", "null", np.zeros((len(frame), 1)))] + [
                (name, kind, x)
                for name, x in arrays.items()
                for kind in args.kinds
                if not (kind == "gp" and x.shape[1] > 100)
            ]
            for name, kind, x in methods:
                start = time.perf_counter()
                if kind == "null":
                    p = np.zeros(test.sum())
                    width = np.quantile(abs(y[validation]), 0.9)
                else:
                    model, selection = select_model(
                        kind, x, y, train, validation, 1729 + seed
                    )
                    p = model.predict(x[test])
                    width = np.quantile(
                        abs(y[validation] - model.predict(x[validation])), 0.9
                    )
                    selections.append(
                        dict(
                            protocol=protocol,
                            seed=seed,
                            features=name,
                            learner=kind,
                            **selection,
                        )
                    )
                for direction, threshold in [(1, 50), (-1, -50)]:
                    results.append(
                        dict(
                            protocol=protocol,
                            seed=seed,
                            features=name,
                            learner=kind,
                            direction=direction,
                            train_n=int(train.sum()),
                            validation_n=int(validation.sum()),
                            dimensions=x.shape[1],
                            interval90_coverage=float(
                                (abs(p - y[test]) <= width).mean()
                            ),
                            interval90_halfwidth_mV=float(width),
                            seconds=time.perf_counter() - start,
                            **evaluate(y[test], p, threshold, direction),
                        )
                    )
                predictions.extend(
                    {
                        "protocol": protocol,
                        "seed": seed,
                        "features": name,
                        "learner": kind,
                        "id": ident,
                        "site": int(site),
                        "actual": float(actual),
                        "predicted": float(pr),
                        "halfwidth90": float(width),
                    }
                    for ident, site, actual, pr in zip(
                        frame.id[test], frame.resN[test], y[test], p, strict=True
                    )
                )
            print(protocol, seed, "completed", len(methods), flush=True)
    metrics = pd.DataFrame(results)
    pred = pd.DataFrame(predictions)
    metrics.to_csv(OUT / f"bk_metrics_{args.tag}.csv", index=False)
    pred.to_csv(OUT / f"bk_predictions_{args.tag}.csv", index=False)
    (OUT / f"bk_model_selection_{args.tag}.json").write_text(
        json.dumps(selections, indent=2, default=int) + "\n"
    )
    if args.bootstrap:
        boot = []
        for protocol in pred.protocol.unique():
            for learner in args.kinds:
                for base in ["cheap", "esm2_35m_sequence", "esm1v_650m_sequence"]:
                    baseline = pred[
                        (pred.protocol == protocol)
                        & (pred.learner == learner)
                        & (pred.features == base)
                    ].set_index("id")
                    if baseline.empty:
                        continue
                    for suffix in [
                        "_energy",
                        "_geometry",
                        "_energy_geometry",
                        "_local_energy",
                        "_all_energy",
                    ]:
                        augmented = pred[
                            (pred.protocol == protocol)
                            & (pred.learner == learner)
                            & (pred.features == base + suffix)
                        ].set_index("id")
                        if augmented.empty:
                            continue
                        joined = baseline.join(
                            augmented[["predicted"]],
                            rsuffix="_augmented",
                            validate="one_to_one",
                        )
                        for direction, threshold in [(1, 50), (-1, -50)]:
                            boot.append(
                                dict(
                                    protocol=protocol,
                                    learner=learner,
                                    baseline=base,
                                    augmented=base + suffix,
                                    direction=direction,
                                    **grouped_bootstrap(
                                        joined.actual.to_numpy(),
                                        joined.predicted_augmented.to_numpy(),
                                        joined.predicted.to_numpy(),
                                        joined.index.map(
                                            parts[
                                                (parts.protocol == protocol)
                                                & (parts.seed == 0)
                                            ]
                                            .set_index("id")
                                            .group
                                        ).to_numpy(),
                                        threshold,
                                        direction,
                                    ),
                                )
                            )
        (OUT / f"bk_bootstrap_{args.tag}.json").write_text(
            json.dumps(boot, indent=2) + "\n"
        )
    print(
        metrics.groupby(["protocol", "features", "learner", "direction"])[
            ["P20", "rmse", "pearson"]
        ]
        .mean()
        .to_string()
    )


if __name__ == "__main__":
    with threadpool_limits(limits=4):
        main()
