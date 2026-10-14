"""Train on frozen training partitions; choose only on validation; evaluate fixed tests.

No target label, measured trafficking, or selected paper features enter model inputs.
"""

from __future__ import annotations

import json
import resource
import time
import warnings

import numpy as np
import pandas as pd
from data import DATA, OUT, load_bedbrook, load_kir, sha
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def precision_at_k(pred: np.ndarray, gains: np.ndarray, k: int) -> float:
    """Expected precision under random tie breaking; null must not exploit input row order."""
    k = min(k, len(pred))
    boundary = np.sort(pred)[-k]
    above = pred > boundary
    tied = pred == boundary
    return float((gains[above].sum() + (k - above.sum()) * gains[tied].mean()) / k)


def metrics(
    y: np.ndarray,
    pred: np.ndarray,
    threshold: float,
    robust: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> dict:
    gains = y > threshold
    chosen = pred > threshold
    return {
        "n": len(y),
        "beneficial": int(gains.sum()),
        "conservative_beneficial": int(robust.sum()),
        "prevalence": float(gains.mean()),
        "mae": float(abs(y - pred).mean()),
        "rmse": float(np.sqrt(np.mean((y - pred) ** 2))),
        "spearman": (
            float(spearmanr(y, pred).statistic) if np.std(pred) > 1e-12 else 0.0
        ),
        "precision10": precision_at_k(pred, gains, 10),
        "precision20": precision_at_k(pred, gains, 20),
        "conservative_precision20": precision_at_k(pred, robust, 20),
        "enrichment20": precision_at_k(pred, gains, 20)
        / max(float(gains.mean()), 1e-12),
        "predicted_gain_count": int(chosen.sum()),
        "gain_precision": float(gains[chosen].mean()) if chosen.any() else None,
        "gain_recall": float((gains & chosen).sum() / max(int(gains.sum()), 1)),
        "interval90_coverage": float(((lower <= y) & (y <= upper)).mean()),
        "interval90_mean_width": float((upper - lower).mean()),
        "lower_bound_gain_count": int((lower > threshold).sum()),
        "lower_bound_gain_precision": (
            float(gains[lower > threshold].mean())
            if (lower > threshold).any()
            else None
        ),
    }


def features_for(frame: pd.DataFrame, dataset: str) -> dict[str, np.ndarray]:
    with np.load(
        DATA
        / (
            "features/bedbrook.npz"
            if dataset == "bedbrook_current"
            else "features/kir.npz"
        )
    ) as data:
        lookup = {v: i for i, v in enumerate(data["ids"])}
        indices = [lookup[v] for v in frame.id]
        result = {k: data[k][indices].astype(float) for k in data.files if k != "ids"}
    result["sequence_physics"] = np.column_stack(
        [result["sequence"], result["physics"]]
    )
    result["esm_physics"] = np.column_stack([result["esm"], result["physics"]])
    return result


def fit_predict(
    name: str,
    x: np.ndarray,
    y: np.ndarray,
    train: np.ndarray,
    val: np.ndarray,
    test: np.ndarray,
) -> tuple:
    start = time.perf_counter()
    scaler = StandardScaler().fit(x[train])
    a = scaler.transform(x[train])
    b = scaler.transform(x[val])
    c = scaler.transform(x[test])
    transform = np.log1p if name.startswith("bedbrook:") else lambda z: z
    inverse = np.expm1 if name.startswith("bedbrook:") else lambda z: z
    observed = transform(y[train])
    algorithm = name.split(":")[-1]
    options = []
    if algorithm == "GP":
        # Scaling by active feature count makes length scales comparable across feature families.
        norm = np.sqrt(max(int((scaler.var_ > 1e-10).sum()), 1))
        a = a / norm
        b = b / norm
        c = c / norm
        for length in [0.5, 1.0, 2.0]:
            for noise in [0.03, 0.15]:
                kernel = ConstantKernel(1.0, constant_value_bounds="fixed") * Matern(
                    length_scale=length, length_scale_bounds="fixed", nu=1.5
                ) + WhiteKernel(noise, noise_level_bounds="fixed")
                model = GaussianProcessRegressor(
                    kernel=kernel, optimizer=None, normalize_y=True, alpha=1e-7
                )
                model.fit(a, observed)
                p = inverse(model.predict(b))
                error = float(abs(p - y[val]).mean())
                options.append((error, {"length": length, "noise": noise}, model))
    elif algorithm == "HGB":
        model = HistGradientBoostingRegressor(
            max_iter=150,
            max_depth=3,
            min_samples_leaf=20,
            learning_rate=0.05,
            l2_regularization=1.0,
            random_state=1729,
            early_stopping=False,
        )
        model.fit(a, observed)
        options = [
            (
                float(abs(inverse(model.predict(b)) - y[val]).mean()),
                {"depth": 3, "trees": 150},
                model,
            )
        ]
    else:
        for alpha in [1.0, 10.0, 100.0]:
            model = Ridge(alpha=alpha, solver="lsqr", tol=1e-7)
            model.fit(a, observed)
            error = float(abs(inverse(model.predict(b)) - y[val]).mean())
            options.append((error, {"alpha": alpha}, model))
    error, parameters, model = min(options, key=lambda z: z[0])
    validation = inverse(model.predict(b))
    prediction = inverse(model.predict(c))
    if algorithm == "GP":
        _, std = model.predict(c, return_std=True)
        z = model.predict(c)
        lower = inverse(z - 1.645 * std)
        upper = inverse(z + 1.645 * std)
    else:
        q = np.quantile(abs(validation - y[val]), 0.9, method="higher")
        lower = prediction - q
        upper = prediction + q
    return (
        prediction,
        lower,
        upper,
        {
            "parameters": parameters,
            "validation_MAE": error,
            "seconds": time.perf_counter() - start,
            "training_rows": int(train.sum()),
            "validation_rows": int(val.sum()),
            "test_rows": int(test.sum()),
            "interval": (
                "GP approximate posterior"
                if algorithm == "GP"
                else "validation residual radius; reused model-selection data, not guaranteed conformal"
            ),
        },
    )


def benchmark() -> None:
    partitions = pd.read_csv(DATA / "partitions.csv")
    freeze = json.loads((DATA / "freeze.json").read_text())
    assert sha(DATA / "partitions.csv") == freeze["partition_sha256"]
    kir, _ka = load_kir()
    bed, ba = load_bedbrook()
    allrows = pd.concat([kir, bed], ignore_index=True)
    reports = []
    predictions = []
    resources = []
    for (protocol, dataset), part in partitions.groupby(["protocol", "dataset"]):
        frame = part.merge(
            allrows[allrows.dataset == dataset],
            on=["dataset", "id"],
            validate="one_to_one",
        )
        train = (frame.split == "train").to_numpy()
        val = (frame.split == "validation").to_numpy()
        test = (frame.split == "test").to_numpy()
        assert not (set(frame[train].group) & set(frame[test].group))
        x = features_for(frame, dataset)
        y = frame.score.to_numpy(float)
        threshold = ba["gain_threshold_nA"] if dataset == "bedbrook_current" else 0.3
        robust = (
            y > threshold
            if dataset == "bedbrook_current"
            else y - 1.96 * frame.se.to_numpy(float) > 0.3
        )
        reference = (
            ba["reference_best_parent_nA"] if dataset == "bedbrook_current" else 0.0
        )
        specs = [
            ("WT_null", None, None),
            ("training_mean", None, None),
            ("properties_Ridge", "properties", "Ridge"),
            ("conservation_Ridge", "conservation", "Ridge"),
            ("geometry_Ridge", "geometry", "Ridge"),
            ("physics_Ridge", "physics", "Ridge"),
            ("sequence_Ridge", "sequence", "Ridge"),
            ("sequence_physics_Ridge", "sequence_physics", "Ridge"),
            ("esm_Ridge", "esm", "Ridge"),
            ("esm_physics_Ridge", "esm_physics", "Ridge"),
        ]
        if dataset == "bedbrook_current":
            specs += [
                ("sequence_GP", "sequence", "GP"),
                ("sequence_physics_GP", "sequence_physics", "GP"),
                ("esm_GP", "esm", "GP"),
            ]
        else:
            specs += [
                ("esm_score_Ridge", "esm_score", "Ridge"),
                ("sequence_HGB", "sequence", "HGB"),
                ("sequence_physics_HGB", "sequence_physics", "HGB"),
            ]
        for model_name, feature, algorithm in specs:
            if feature is None:
                const = reference if model_name == "WT_null" else float(y[train].mean())
                p = np.full(test.sum(), const)
                q = np.quantile(abs(y[val] - const), 0.9, method="higher")
                lo = p - q
                hi = p + q
                meta = {
                    "parameters": {},
                    "validation_MAE": float(abs(y[val] - const).mean()),
                    "seconds": 0.0,
                }
            else:
                assert algorithm is not None
                p, lo, hi, meta = fit_predict(
                    ("bedbrook:" if dataset == "bedbrook_current" else "kir:")
                    + algorithm,
                    x[feature],
                    y,
                    train,
                    val,
                    test,
                )
            report = dict(
                protocol=protocol,
                dataset=dataset,
                model=model_name,
                **metrics(y[test], p, threshold, robust[test], lo, hi),
                **meta,
            )
            reports.append(report)
            resources.append(
                dict(protocol=protocol, dataset=dataset, model=model_name, **meta)
            )
            for i, pr, l, u in zip(np.flatnonzero(test), p, lo, hi):
                r = frame.iloc[i]
                predictions.append(
                    {
                        "protocol": protocol,
                        "dataset": dataset,
                        "model": model_name,
                        "id": r.id,
                        "group": r.group,
                        "position": r.position,
                        "observed": y[i],
                        "prediction": float(pr),
                        "gain_threshold": threshold,
                        "beneficial": bool(y[i] > threshold),
                        "conservative_beneficial": bool(robust[i]),
                        "reported_SE": None if pd.isna(r.se) else float(r.se),
                        "lower90": float(l),
                        "upper90": float(u),
                    }
                )
            print(
                protocol,
                dataset,
                model_name,
                "MAE",
                round(report["mae"], 4),
                "rho",
                round(report["spearman"], 3),
                "P20",
                round(report["precision20"], 3),
                flush=True,
            )
    pd.DataFrame(predictions).to_csv(OUT / "predictions.csv", index=False)
    pd.DataFrame(reports).to_csv(OUT / "metrics.csv", index=False)
    (OUT / "model_resources.json").write_text(
        json.dumps(
            {
                "fits": resources,
                "process_peak_RSS_MiB": resource.getrusage(
                    resource.RUSAGE_SELF
                ).ru_maxrss
                / 1024,
                "feature_note": "Coarse structure descriptors test a specific approximation; no general conclusion about physics follows from their failure.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="An input array is constant")
    benchmark()
