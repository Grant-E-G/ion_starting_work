"""Recover exact published BK feature/split identities without functional fitting."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import DATA, OUT, RAW, load_bk, write_immutable
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler

PUBLISHED_COLUMNS = [
    "dHyd",
    "score",
    "fa_atr",
    "fa_rep",
    "fa_sol",
    "fa_intra_rep",
    "fa_intra_sol_xover4",
    "lk_ball_wtd",
    "fa_elec",
    "pro_close",
    "hbond_sr_bb",
    "hbond_bb_sc",
    "hbond_sc",
    "omega",
    "fa_dun",
    "p_aa_pp",
    "fa_water_to_bilayer",
    "resN",
    "rmsf",
    "psasa",
    "cov271",
    "cov316",
    "cov271-n",
    "cov316-n",
    "SIFT",
    "MEMBX",
    "SECS",
    "POREX",
    "BURIED",
    "BORDER",
]
ENERGY_COLUMNS = PUBLISHED_COLUMNS[1:17]


def main() -> None:
    frame = load_bk()
    raw = frame[PUBLISHED_COLUMNS].to_numpy()
    raw_min, raw_max = raw.min(0), raw.max(0)
    rows, checks = [], []
    for seed in range(5):
        folder = RAW / f"bkpred/data/split{seed}"
        published = np.vstack(
            [
                np.load(folder / "X5_train.npy"),
                np.load(folder / "validation/X_test.npy"),
            ]
        )
        targets = np.concatenate(
            [
                np.load(folder / "y5_train.npy").ravel(),
                np.load(folder / "validation/y_test.npy").ravel(),
            ]
        )
        slope = (published.max(0) - published.min(0)) / (raw_max - raw_min)
        intercept = published.min(0) - slope * raw_min
        transformed = raw * slope + intercept
        distance = cdist(published, transformed)
        match = distance.argmin(1)
        maximum_error = float(distance[np.arange(len(match)), match].max())
        assert maximum_error < 1e-10 and len(np.unique(match)) == len(frame)
        scaler = StandardScaler().fit(raw[match[:378]])
        scaled_error = float(abs(scaler.transform(raw[match]) - published).max())
        expected_y = 200 * np.tanh(frame.target.to_numpy()[match] / 200)
        target_error = float(abs(expected_y - targets).max())
        assert scaled_error < 1e-10 and target_error < 1e-10
        train_sites = set(frame.resN.iloc[match[:378]])
        test_sites = frame.resN.iloc[match[378:]]
        for i, source in enumerate(match):
            rows.append(
                {
                    "protocol": "published_random",
                    "seed": seed,
                    "id": frame.id.iloc[source],
                    "split": "train" if i < 378 else "test",
                }
            )
        checks.append(
            {
                "split": seed,
                "row_matching_max_L2_error": maximum_error,
                "train_only_scaler_max_error": scaled_error,
                "target_transform_max_error": target_error,
                "test_rows": len(test_sites),
                "test_rows_at_seen_sites": int(test_sites.isin(train_sites).sum()),
                "test_seen_site_fraction": float(test_sites.isin(train_sites).mean()),
            }
        )
    write_immutable(
        DATA / "bk_published_partitions.csv", pd.DataFrame(rows).to_csv(index=False)
    )
    write_immutable(
        DATA / "bk_published_feature_map.json",
        json.dumps(
            {
                "columns": PUBLISHED_COLUMNS,
                "energy_columns": ENERGY_COLUMNS,
                "normalization": "StandardScaler fitted on each original 378-row training set",
                "target_transform": "200*tanh(raw_mV/200)",
                "proof": "Unique bijective row matching and affine column recovery verified to <1e-10 for all five splits",
                "censoring": "Actual raw-table bounds -370 and +300, despite reversed magnitudes in prose; primary new comparisons exclude these 28 records",
                "caveat": "Covariance anchors were selected using known functional hotspots and remain secondary descriptors",
            },
            indent=2,
        )
        + "\n",
    )
    (OUT / "bk_published_data_audit.json").write_text(
        json.dumps(checks, indent=2) + "\n"
    )
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
