"""Exploratory comparisons on previously inspected tests; never independent validation."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "predictive"))
from benchmark import features_for, precision_at_k
from data import DATA, load_bedbrook, load_kir

OUT = ROOT / "notes/accelerated"


def predict(
    x: np.ndarray,
    y: np.ndarray,
    train: np.ndarray,
    val: np.ndarray,
    test: np.ndarray,
    utility: np.ndarray,
) -> tuple:
    scaler = StandardScaler().fit(x[train])
    a = scaler.transform(x)
    options = []
    for alpha in [1.0, 10.0, 100.0]:
        m = Ridge(alpha=alpha, solver="lsqr", tol=1e-7).fit(a[train], y[train])
        p = m.predict(a[val])
        # Select utility ranking on validation only; not regression loss.
        k = min(10, int(val.sum()))
        options.append(
            (-precision_at_k(p, utility[val], k), np.mean(abs(p - y[val])), alpha, m)
        )
    _, _, alpha, m = min(options, key=lambda z: z[:3])
    return m.predict(a[test]), alpha


def main() -> None:
    start = time.perf_counter()
    feats = pd.read_csv(OUT / "component_features.csv")
    parts = pd.read_csv(DATA / "partitions.csv")
    kir, _ = load_kir()
    bed, _ = load_bedbrook()
    rows = []
    predictions = []
    for frame, protocol in [
        (bed, "bedbrook_temporal"),
        (kir[kir.dataset == "kir_function"], "kir_site_hash"),
        (kir[kir.dataset == "kir_surface"], "kir_site_hash"),
    ]:
        dataset = str(frame.dataset.iloc[0])
        frame = frame.reset_index(drop=True)
        part = parts[
            (parts.protocol == protocol) & (parts.dataset == dataset)
        ].set_index("id")
        split = frame.id.map(part.split).to_numpy()
        train = split == "train"
        val = split == "validation"
        test = split == "test"
        f = (
            feats[feats.dataset == ("bedbrook" if dataset.startswith("bed") else "kir")]
            .set_index("id")
            .loc[frame.id]
        )
        baseline = features_for(frame, dataset)
        mpnn = f[["mpnn"]].to_numpy()
        transfer = f[["transfer"]].to_numpy()
        dyn = f[["gnm_hydro", "gnm_volume"]].to_numpy()
        threshold = (
            1.2 * bed[bed.control].score.max() if dataset.startswith("bed") else 0.3
        )
        y = frame.score.to_numpy()
        gains = y > threshold
        trade = gains.copy()
        known: np.ndarray = np.ones(len(frame), dtype=bool)
        if dataset.startswith("bed"):
            tau = frame["kinetics_off_y"].to_numpy()
            cap = float(frame[frame.control]["kinetics_off_y"].max())
            known = np.isfinite(tau)
            trade = gains & (tau <= cap) & known
        else:
            trade = (y - 1.96 * frame.se.to_numpy()) > threshold
        # Missing kinetics excluded from fitting and utility evaluation, not treated as negatives.
        train = train & known
        val = val & known
        test = test & known
        methods = {
            "WT_null": np.zeros((len(frame), 1)),
            "esm": baseline["esm"],
            "sequence": baseline["sequence"],
            "mpnn": mpnn,
            "transfer": transfer,
            "GNM": dyn,
            "esm_mpnn": np.c_[baseline["esm"], mpnn],
            "esm_transfer": np.c_[baseline["esm"], transfer],
            "esm_GNM": np.c_[baseline["esm"], dyn],
        }
        for method, x in methods.items():
            if method == "WT_null":
                reference = (
                    float(bed[bed.control].score.max())
                    if dataset.startswith("bed")
                    else 0.0
                )
                p = np.full(int(test.sum()), reference)
                alpha = None
            else:
                p, alpha = predict(x, y, train, val, test, trade)
            t = y[test]
            g = gains[test]
            u = trade[test]
            rows.append(
                {
                    "dataset": dataset,
                    "protocol": protocol,
                    "method": method,
                    "n": len(t),
                    "gain_prevalence": g.mean(),
                    "utility_prevalence": u.mean(),
                    "precision20": precision_at_k(p, g, 20),
                    "utility_precision20": precision_at_k(p, u, 20),
                    "spearman": spearmanr(p, t).statistic if np.std(p) > 1e-12 else 0.0,
                    "mae": np.mean(abs(p - t)),
                    "alpha": alpha,
                    "validation_selection": (
                        "fixed_reference"
                        if method == "WT_null"
                        else "utility_P10_then_MAE"
                    ),
                    "evidence": "exploratory previously inspected test",
                }
            )
            for ident, actual, pp, gg, uu in zip(frame.id[test], t, p, g, u):
                predictions.append(
                    {
                        "dataset": dataset,
                        "method": method,
                        "id": ident,
                        "actual": actual,
                        "prediction": pp,
                        "gain": gg,
                        "utility": uu,
                    }
                )
    pd.DataFrame(rows).to_csv(OUT / "comparisons.csv", index=False)
    pd.DataFrame(predictions).to_csv(OUT / "predictions.csv", index=False)
    (OUT / "comparison_resources.json").write_text(
        json.dumps(
            {"seconds": time.perf_counter() - start, "models": len(rows)}, indent=2
        )
    )
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
