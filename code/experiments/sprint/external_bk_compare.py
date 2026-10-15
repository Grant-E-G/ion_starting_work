"""External-publication function test, including a known-parent shortcut.

Readout tuning uses only old473-source data (445 numeric records). New2024
measurements never tune coefficients/hyperparameters. All models enforce WTzero.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from bk_audit import ENERGY_COLUMNS
from bk_nullaware import scans
from data import AA, DATA, FEATURES, OUT, RAW, load_bk, write_immutable
from metrics import precision_at_k
from scipy.stats import pearsonr
from sklearn.linear_model import Ridge
from sklearn.metrics import average_precision_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--encom", action="store_true")
    args = parser.parse_args()
    tag = "_encom" if args.encom else ""
    old = load_bk()
    dynamics = None
    if args.encom:
        assert (OUT / "encom_resources.json").exists()
        dynamics = pd.read_csv(FEATURES / "bk_encom.csv").set_index("id")
        if "error" in dynamics:
            dynamics = dynamics[dynamics.error.isna()]
        old = old[old.id.isin(dynamics.index)].reset_index(drop=True)
    frame = pd.read_csv(OUT / "external_bk_measurements.csv")
    source = scans()
    pca = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")
    atomic = pd.read_csv(FEATURES / "external_bk_evoef_atomic.csv").set_index(
        "mutation"
    )
    combined = pd.read_csv(FEATURES / "external_bk_evoef_compounds.csv").set_index(
        "mutation"
    )
    evo = pd.read_csv(FEATURES / "bk_evoef_r20.csv").set_index("mutation").loc[old.id]
    energy_columns = [
        column for column in evo if column.startswith("state_difference_")
    ]

    def chemical(ident: str) -> np.ndarray:
        vectors = []
        for token in ident.split(","):
            wt, alt = AA.index(token[0]), AA.index(token[-1])
            vectors.append(
                np.concatenate(
                    [
                        np.eye(20)[alt] - np.eye(20)[wt],
                        pca[alt] - pca[wt],
                        [source.loc[token, "dHyd"], source.loc[token, "SIFT"] - 1],
                    ]
                )
            )
        return np.stack(vectors).sum(0)

    cheap = np.stack([chemical(ident) for ident in old.id])
    external_cheap = np.stack([chemical(ident) for ident in frame.id])
    physical = old[ENERGY_COLUMNS].to_numpy()
    external_physical = np.stack(
        [
            source.loc[ident.split(","), ENERGY_COLUMNS].sum().to_numpy()
            for ident in frame.id
        ]
    )
    local = evo[energy_columns].to_numpy()
    external_local, external_union_additive = [], []
    for ident in frame.id:
        if "," not in ident:
            values = atomic.loc[ident, energy_columns].to_numpy(dtype=float)
            external_local.append(values)
            external_union_additive.append(values)
        else:
            external_local.append(
                np.array(
                    [
                        combined.loc[
                            ident, column.replace("state_difference_", "joint_")
                        ]
                        for column in energy_columns
                    ]
                )
            )
            external_union_additive.append(
                np.array(
                    [
                        combined.loc[
                            ident,
                            column.replace("state_difference_", "matched_additive_"),
                        ]
                        for column in energy_columns
                    ]
                )
            )
    joint, additive = np.stack(external_local), np.stack(external_union_additive)
    with np.load(FEATURES / "external_bk_sequence_deltas.npz") as arrays:
        old_order = pd.Index(arrays["training_ids"]).get_indexer(old.id)
        new_order = pd.Index(arrays["external_ids"]).get_indexer(frame.id)
        assert (old_order >= 0).all() and (new_order >= 0).all()
        sequence, external_sequence = (
            arrays["training_delta"][old_order],
            arrays["external_delta"][new_order],
        )
    families = {
        "chemical_delta": (cheap, external_cheap),
        "chemical_published_energy": (
            np.column_stack([cheap, physical]),
            np.column_stack([external_cheap, external_physical]),
        ),
        "sequence_delta": (
            np.column_stack([cheap, sequence]),
            np.column_stack([external_cheap, external_sequence]),
        ),
        "sequence_published_energy": (
            np.column_stack([cheap, sequence, physical]),
            np.column_stack([external_cheap, external_sequence, external_physical]),
        ),
        "chemical_EvoEF2_joint": (
            np.column_stack([cheap, local]),
            np.column_stack([external_cheap, joint]),
        ),
        "chemical_EvoEF2_matched_additive": (
            np.column_stack([cheap, local]),
            np.column_stack([external_cheap, additive]),
        ),
        "sequence_EvoEF2_joint": (
            np.column_stack([cheap, sequence, local]),
            np.column_stack([external_cheap, external_sequence, joint]),
        ),
        "sequence_EvoEF2_matched_additive": (
            np.column_stack([cheap, sequence, local]),
            np.column_stack([external_cheap, external_sequence, additive]),
        ),
    }
    if dynamics is not None:
        names = [
            column
            for column in dynamics
            if "_delta_" in column or column.startswith("state_difference_")
        ]
        dynamic_old = dynamics.loc[old.id, names].to_numpy()
        dynamic_new = dynamics.loc[frame.id, names].to_numpy()
        families["chemical_ENCoM"] = (
            np.column_stack([cheap, dynamic_old]),
            np.column_stack([external_cheap, dynamic_new]),
        )
        families["sequence_ENCoM"] = (
            np.column_stack([cheap, sequence, dynamic_old]),
            np.column_stack([external_cheap, external_sequence, dynamic_new]),
        )
    policy: dict = {
        "families": list(families),
        "WT_constraint": "Readout(mutant)-readout(zero mutation features)",
        "hyperparameters": "Ridgealpha1/10/100/1000, selected using only old-source5-fold siteGroupKFoldMSE; then refit445numeric records",
        "physical": "Published atomic16term sums; EvoEF2 actual multi-mutant states versus additive constituents in the same crop/repacking mask",
        "sequence": "650M actual-mutant-minus-WT mean and mutated-site representation; no new language-model training",
        "baseline": "Known-parent-only uses numeric pre2023constituents; does not invent neutral measurements for unknown constituents",
        "primary_test": "10new zeroCa genotypes; 2overlapcontrols and25uM measurements excluded",
        "utility": "P3/P5 for leftward shift>=50mV and optional apparent-slope retention; ranking only predicts voltage, not slope",
        "interpretation": "Four positives inheritL312A. Also score the new modifications relative to matchedL312A control. Missing standalone constituent functions prevent identifying experimental epistasis.",
    }
    if args.encom:
        policy["training_cohort_n"] = int((~old.censored).sum())
        policy["hyperparameters"] = policy["hyperparameters"].replace(
            "445numeric", str(policy["training_cohort_n"]) + "numeric"
        )
    write_immutable(
        DATA / f"external_bk_model_policy{tag}.json",
        json.dumps(policy, indent=2) + "\n",
    )
    numeric = ~old.censored.to_numpy()
    y = old.target.to_numpy()[numeric]
    groups = old.resN.to_numpy()[numeric]
    old_lookup = old.loc[numeric].set_index("id").target.to_dict()
    predictions = {
        "WT_null": np.zeros(len(frame)),
        "known_parent_only": np.array(
            [
                min(
                    [0]
                    + [
                        old_lookup[token]
                        for token in ident.split(",")
                        if token in old_lookup
                    ]
                )
                for ident in frame.id
            ]
        ),
    }
    settings: list[dict] = []
    widths = {
        "WT_null": float(np.quantile(abs(y), 0.9)),
        "known_parent_only": float(np.quantile(abs(y), 0.9)),
    }

    def fitted(x: np.ndarray, response: np.ndarray, train: np.ndarray, alpha: float):
        keep = x[train].std(0) > 1e-8
        scale = StandardScaler().fit(x[train][:, keep])
        model = Ridge(alpha=alpha).fit(
            scale.transform(x[train][:, keep]), response[train]
        )

        def predict(values: np.ndarray) -> np.ndarray:
            return (
                model.predict(scale.transform(values[:, keep]))
                - model.predict(scale.transform(np.zeros((1, x.shape[1]))[:, keep]))[0]
            )

        return predict

    for name, (all_x, test_x) in families.items():
        x = all_x[numeric]
        possibilities = []
        for alpha in [1, 10, 100, 1000]:
            oof = np.zeros(len(y))
            for train, val in GroupKFold(5).split(x, y, groups):
                oof[val] = fitted(x, y, train, alpha)(x[val])
            possibilities.append((float(np.mean((oof - y) ** 2)), alpha, oof))
        loss, alpha, oof = min(possibilities, key=lambda value: value[0])
        predictions[name] = fitted(x, y, np.arange(len(y)), alpha)(test_x)
        widths[name] = float(np.quantile(abs(oof - y), 0.9))
        settings.append(
            {
                "family": name,
                "alpha": alpha,
                "old_source_site_CV_MSE": loss,
                "OOF90_residual_halfwidth_mV": widths[name],
            }
        )
    test = (frame.calcium_uM == 0) & ~frame.single_training_overlap
    actual = frame.target_mV.to_numpy()
    positive = frame.gating_shift50.to_numpy()
    joint_positive = frame.shift_with_slope_retained.to_numpy()
    rows: list[dict] = []
    output: list[dict] = []
    contrasts: list[dict] = []
    parent_index = frame.index[(frame.id == "L312A") & (frame.calcium_uM == 0)][0]
    change = test & frame.id.str.contains("L312A")
    for name, prediction in predictions.items():
        target, p = actual[test], prediction[test]
        rows.append(
            {
                "family": name,
                "test_n": int(test.sum()),
                "MAE_mV": float(abs(p - target).mean()),
                "pearson": (
                    float(pearsonr(target, p).statistic) if np.std(p) > 1e-12 else 0.0
                ),
                "left_gain_prevalence": float(positive[test].mean()),
                "left_gain_P3": precision_at_k(-p, positive[test], 3),
                "left_gain_P5": precision_at_k(-p, positive[test], 5),
                "left_gain_AP": float(average_precision_score(positive[test], -p)),
                "left_gain_slope_retained_P3": precision_at_k(
                    -p, joint_positive[test], 3
                ),
                "OOF90_halfwidth_mV": widths[name],
                "external90_coverage": float((abs(p - target) <= widths[name]).mean()),
                "increment_over_L312A_MAE_mV": float(
                    abs(
                        (prediction[change] - prediction[parent_index])
                        - (actual[change] - actual[parent_index])
                    ).mean()
                ),
            }
        )
        output.extend(
            {
                "family": name,
                "id": ident,
                "calcium_uM": float(calcium),
                "overlap_control": bool(overlap),
                "actual_mV": float(value),
                "predicted_mV": float(pr),
                "empirical90_halfwidth_mV": widths[name],
            }
            for ident, calcium, overlap, value, pr in zip(
                frame.id,
                frame.calcium_uM,
                frame.single_training_overlap,
                actual,
                prediction,
                strict=True,
            )
        )
        contrasts.extend(
            {
                "family": name,
                "id": ident,
                "measured_change_from_matched_L312A_mV": float(observed),
                "predicted_change_from_L312A_mV": float(pr),
            }
            for ident, observed, pr in zip(
                frame.id[change],
                actual[change] - actual[parent_index],
                prediction[change] - prediction[parent_index],
                strict=True,
            )
        )
    pd.DataFrame(rows).to_csv(OUT / f"external_bk_metrics{tag}.csv", index=False)
    pd.DataFrame(output).to_csv(OUT / f"external_bk_predictions{tag}.csv", index=False)
    pd.DataFrame(contrasts).to_csv(
        OUT / f"external_bk_parent_contrasts{tag}.csv", index=False
    )
    (OUT / f"external_bk_model_selection{tag}.json").write_text(
        json.dumps(settings, indent=2) + "\n"
    )
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
