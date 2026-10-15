"""Tie-aware selection metrics, physical ablations and grouped uncertainty."""

from __future__ import annotations

import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import average_precision_score, roc_auc_score


def precision_at_k(prediction: np.ndarray, positive: np.ndarray, k: int) -> float:
    """Expected precision under random tie-breaking, including constant nulls."""
    if not len(prediction):
        return float("nan")
    k = min(k, len(prediction))
    boundary = np.sort(prediction)[-k]
    above = prediction > boundary
    equal = prediction == boundary
    return float(
        (positive[above].sum() + (k - above.sum()) * positive[equal].mean()) / k
    )


def evaluate(
    actual: np.ndarray, prediction: np.ndarray, threshold: float, direction: int = 1
) -> dict[str, float]:
    assert len(actual) == len(prediction) and np.isfinite(prediction).all()
    positive = direction * actual >= direction * threshold
    rank: np.ndarray = direction * prediction
    variable = np.std(prediction) > 1e-12 and np.std(actual) > 1e-12
    both_classes = len(np.unique(positive)) == 2
    return {
        "n": len(actual),
        "prevalence": float(positive.mean()),
        "mae": float(abs(actual - prediction).mean()),
        "rmse": float(np.sqrt(np.mean((actual - prediction) ** 2))),
        "pearson": (
            float(pearsonr(actual, prediction).statistic)
            if variable and len(actual) > 2
            else 0.0
        ),
        "spearman": (
            float(spearmanr(actual, prediction).statistic)
            if variable and len(actual) > 2
            else 0.0
        ),
        "P10": precision_at_k(rank, positive, 10),
        "P20": precision_at_k(rank, positive, 20),
        "P50": precision_at_k(rank, positive, 50),
        "average_precision": (
            float(average_precision_score(positive, rank))
            if both_classes
            else float("nan")
        ),
        "auc": float(roc_auc_score(positive, rank)) if both_classes else float("nan"),
    }


def site_diverse_precision(
    prediction: np.ndarray, positive: np.ndarray, sites: np.ndarray, k: int
) -> float:
    """Pick at most one variant per site; average tied maxima within each site."""
    maxima, success = [], []
    for site in np.unique(sites):
        mask = sites == site
        maximum = prediction[mask].max()
        maxima.append(maximum)
        success.append(float(positive[mask][prediction[mask] == maximum].mean()))
    return precision_at_k(np.asarray(maxima), np.asarray(success), k)


def grouped_bootstrap(
    actual: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    groups: np.ndarray,
    threshold: float,
    direction: int,
    repetitions: int = 2000,
) -> dict:
    """Paired cluster bootstrap of already fixed out-of-fold predictions.

    Describes benchmark uncertainty; does not refit models or prove prospective
    coverage. Repeated sampled groups retain all their observations.
    """
    rng = np.random.RandomState(1729)
    unique = np.unique(groups)
    indices = [np.flatnonzero(groups == group) for group in unique]
    difference = []
    rmse = []
    for _ in range(repetitions):
        sample = np.concatenate(
            [indices[i] for i in rng.randint(0, len(unique), len(unique))]
        )
        y, p, q = actual[sample], first[sample], second[sample]
        positive = direction * y >= direction * threshold
        difference.append(
            precision_at_k(direction * p, positive, 20)
            - precision_at_k(direction * q, positive, 20)
        )
        rmse.append(np.sqrt(np.mean((p - y) ** 2)) - np.sqrt(np.mean((q - y) ** 2)))
    return {
        "groups": len(unique),
        "replicates": repetitions,
        "P20_difference_interval": np.quantile(
            difference, [0.025, 0.5, 0.975]
        ).tolist(),
        "RMSE_difference_interval": np.quantile(rmse, [0.025, 0.5, 0.975]).tolist(),
        "scope": "Paired cluster bootstrap of fixed OOF predictions; no learner refitting",
    }
