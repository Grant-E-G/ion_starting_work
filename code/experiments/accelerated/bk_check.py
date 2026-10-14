"""Fixed-model BK gating benchmark using published precomputed physical features.

No Rosetta/MD features are generated locally. Signed voltage shifts are functional
changes, not established therapeutic gains. Historical feature-selection leakage
and heterogeneous experimental protocols remain limitations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from components import OUT, ROOT
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "predictive"))
from benchmark import precision_at_k


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uncensored", action="store_true")
    args = parser.parse_args()
    suffix = "_uncensored" if args.uncensored else ""
    start = time.perf_counter()
    raw = ROOT / "sources/accelerated/raw"
    frame = pd.read_csv(raw / "bk_data_scores.csv")
    source = pd.read_excel(
        raw / "bk_data_BK_mutations.xlsx", sheet_name="training_data"
    ).dropna(subset=["Mutation"])
    assert len(frame) == len(source) == 473
    assert not frame.Mutation.duplicated().any()
    frame = frame.merge(
        source[["Mutation", "Species", "Source(s)"]],
        on=["Mutation", "Species"],
        validate="one_to_one",
    )
    assert len(frame) == 473
    rows = []
    for protocol in ["site", "publication"]:
        for r in frame.itertuples(index=False, name=None):
            record = dict(zip(frame.columns, r))
            group = (
                str(int(record["resN"]))
                if protocol == "site"
                else str(record["Source(s)"])
            )
            bucket = (
                int(
                    hashlib.sha256(
                        f"BK-feasibility-20261014:{group}".encode()
                    ).hexdigest()[:8],
                    16,
                )
                % 10
            )
            split = "train" if bucket < 6 else "validation" if bucket < 8 else "test"
            rows.append(
                {
                    "protocol": protocol,
                    "id": record["Mutation"],
                    "group": group,
                    "split": split,
                }
            )
    partitions = pd.DataFrame(rows)
    path = ROOT / "sources/accelerated/bk_partitions.csv"
    text = partitions.to_csv(index=False)
    if path.exists():
        assert path.read_text() == text, "Refusing changed BK partitions"
    else:
        path.write_text(text)
    # Freeze columns and fixed learner before reading any held-out outcomes into metrics.
    energy = frame.columns[
        frame.columns.get_loc("score") : frame.columns.get_loc("rama_prepro") + 1
    ].tolist()
    geometry = ["rmsf", "psasa", "SECS", "WATX", "MEMBX", "POREX", "BURIED", "BORDER"]
    cheap = ["WT", "MT", "resN", "WThyd", "MThyd", "dHyd", "SIFT"]
    # Covariance anchors were selected with functional knowledge in the paper;
    # exclude them from primary energy/geometry comparisons.
    cov = [c for c in frame if c.startswith("cov")]
    config = {
        "energy_columns": energy,
        "geometry_columns": geometry,
        "cheap_columns": cheap,
        "excluded_label_informed_covariance": cov,
        "rf": "300 trees, minleaf3, max_features=1.0, seed1729; fixed before predictions",
        "objectives": "negative shift <=-50mV and positive shift >=50mV; not therapeutic benefit",
        "partition_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "scope": "Precomputed upstream features; new retrospective grouped splits, not a prospective reproduction",
    }
    policy = ROOT / "sources/accelerated/bk_policy.json"
    content = json.dumps(config, indent=2) + "\n"
    if policy.exists():
        assert policy.read_text() == content
    else:
        policy.write_text(content)
    methods = {
        "hydrophobicity": frame[["WThyd", "MThyd", "dHyd"]].to_numpy(),
        "cheap": frame[cheap].to_numpy(),
        "energies": frame[energy].to_numpy(),
        "cheap_energies": frame[cheap + energy].to_numpy(),
        "cheap_geometry": frame[cheap + geometry].to_numpy(),
        "cheap_energy_geometry": frame[cheap + energy + geometry].to_numpy(),
        "published_full_descriptors": frame[cheap + energy + geometry + cov].to_numpy(),
    }
    y = frame["dV[Ca0]"].to_numpy()
    metrics = []
    predictions = []
    for protocol in ["site", "publication"]:
        parts = partitions[partitions.protocol == protocol].set_index("id")
        split = frame.Mutation.map(parts.split).to_numpy()
        train = split == "train"
        test = split == "test"
        if args.uncensored:
            finite_measurement = (y > -370) & (y < 300)
            train = train & finite_measurement
            test = test & finite_measurement
        for method, x in {"WT_null": np.zeros((len(frame), 1)), **methods}.items():
            t = time.perf_counter()
            if method == "WT_null":
                p = np.zeros(int(test.sum()))
            elif method == "hydrophobicity":
                scale = StandardScaler().fit(x[train])
                model = Ridge(alpha=100.0).fit(scale.transform(x[train]), y[train])
                p = model.predict(scale.transform(x[test]))
            else:
                model = RandomForestRegressor(
                    n_estimators=300,
                    min_samples_leaf=3,
                    max_features=1.0,
                    random_state=1729,
                    n_jobs=4,
                ).fit(x[train], y[train])
                p = model.predict(x[test])
            actual = y[test]
            neg = actual <= -50
            pos = actual >= 50
            metrics.append(
                {
                    "protocol": protocol,
                    "method": method,
                    "n": int(test.sum()),
                    "train_n": int(train.sum()),
                    "negative_prevalence": float(neg.mean()),
                    "positive_prevalence": float(pos.mean()),
                    "negative_P10": precision_at_k(-p, neg, 10),
                    "positive_P10": precision_at_k(p, pos, 10),
                    "negative_P20": precision_at_k(-p, neg, 20),
                    "positive_P20": precision_at_k(p, pos, 20),
                    "mae": float(np.mean(abs(p - actual))),
                    "rmse": float(np.sqrt(np.mean((p - actual) ** 2))),
                    "spearman": (
                        float(spearmanr(p, actual).statistic)
                        if np.std(p) > 1e-12
                        else 0.0
                    ),
                    "fit_predict_seconds": time.perf_counter() - t,
                }
            )
            for ident, v, pr in zip(frame.Mutation[test], actual, p):
                predictions.append(
                    {
                        "protocol": protocol,
                        "method": method,
                        "id": ident,
                        "actual_mV": v,
                        "predicted_mV": pr,
                    }
                )
    pd.DataFrame(metrics).to_csv(OUT / f"bk_metrics{suffix}.csv", index=False)
    pd.DataFrame(predictions).to_csv(OUT / f"bk_predictions{suffix}.csv", index=False)
    audit = {
        "observations": len(frame),
        "independent_sites": frame.resN.nunique(),
        "species": frame.Species.value_counts().to_dict(),
        "split_counts": partitions.groupby(["protocol", "split"])
        .size()
        .to_dict()
        .__str__(),
        "source_group_policy": "Entire source-string grouped; multiple-source shared-publication overlap remains possible",
        "flag_bound_rows": int(((y <= -370) | (y >= 300)).sum()),
        "uncensored_only": args.uncensored,
        "feature_generation_measured_here": False,
        "total_seconds": time.perf_counter() - start,
        "peak_rss_MiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
    }
    (OUT / f"bk_audit{suffix}.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(pd.DataFrame(metrics).to_string(index=False))
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
