"""Paired physics ablations, uncertainty, confound and distribution-shift diagnostics.

No model tuning or test-based choice of a winning model. Bootstrap intervals are
conditional retrospective diagnostics; homolog/measurement dependence remains.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from benchmark import precision_at_k
from data import OUT, load_bedbrook, load_kir
from scipy.stats import spearmanr


def paired_bootstrap(frame: pd.DataFrame, a: str, b: str, seed: int = 1729) -> dict:
    first = frame[frame.model == a].set_index("id")
    second = frame[frame.model == b].set_index("id").loc[first.index]
    y = first.observed.to_numpy()
    pa = first.prediction.to_numpy()
    pb = second.prediction.to_numpy()
    gains = first.beneficial.to_numpy(bool)
    groups = first.group.astype(str).to_numpy()
    unique = np.unique(groups)
    members = [np.flatnonzero(groups == g) for g in unique]
    rng = np.random.default_rng(seed)
    deltas = []
    loss = []
    for _ in range(600):
        idx = np.concatenate(
            [members[i] for i in rng.integers(0, len(members), len(members))]
        )
        deltas.append(
            precision_at_k(pb[idx], gains[idx], 20)
            - precision_at_k(pa[idx], gains[idx], 20)
        )
        loss.append(float(np.mean(abs(pb[idx] - y[idx]) - abs(pa[idx] - y[idx]))))
    return {
        "base": a,
        "augmented": b,
        "groups": len(unique),
        "delta_precision20": float(
            precision_at_k(pb, gains, 20) - precision_at_k(pa, gains, 20)
        ),
        "delta_precision20_bootstrap95": np.quantile(deltas, [0.025, 0.975]).tolist(),
        "delta_MAE": float(np.mean(abs(pb - y) - abs(pa - y))),
        "delta_MAE_bootstrap95": np.quantile(loss, [0.025, 0.975]).tolist(),
        "caveat": "Grouped by withheld site for Kir; construct resampling for temporal Bedbrook, conditional on related library. Cluster test has very few independent sequence groups.",
    }


def analyze() -> None:
    predictions = pd.read_csv(OUT / "predictions.csv", low_memory=False)
    scores = pd.read_csv(OUT / "metrics.csv")
    selections = []
    ablations = []
    failures = []
    cheap_comparisons = []
    pairs = [
        ("sequence_Ridge", "sequence_physics_Ridge"),
        ("esm_Ridge", "esm_physics_Ridge"),
        ("sequence_GP", "sequence_physics_GP"),
        ("sequence_HGB", "sequence_physics_HGB"),
    ]
    for (protocol, dataset), frame in predictions.groupby(["protocol", "dataset"]):
        table = scores[(scores.protocol == protocol) & (scores.dataset == dataset)]
        best = table.sort_values(["validation_MAE", "model"]).iloc[0].to_dict()
        selections.append(best)
        cheap = (
            table[
                table.model.isin(
                    [
                        "WT_null",
                        "training_mean",
                        "properties_Ridge",
                        "conservation_Ridge",
                        "geometry_Ridge",
                    ]
                )
            ]
            .sort_values(["validation_MAE", "model"])
            .iloc[0]
        )
        cheap_comparisons.append(
            dict(
                protocol=protocol,
                dataset=dataset,
                **paired_bootstrap(frame, str(cheap.model), best["model"]),
            )
        )
        for a, b in pairs:
            if {a, b} <= set(frame.model):
                ablations.append(
                    dict(
                        protocol=protocol,
                        dataset=dataset,
                        **paired_bootstrap(frame, a, b),
                    )
                )
        chosen = frame[frame.model == best["model"]].copy()
        chosen["residual"] = chosen.prediction - chosen.observed
        for _, r in pd.concat(
            [chosen.nsmallest(3, "residual"), chosen.nlargest(3, "residual")]
        ).iterrows():
            failures.append(r.to_dict())
    pd.DataFrame(selections).to_csv(OUT / "validation_selected_models.csv", index=False)
    pd.DataFrame(failures).to_csv(OUT / "failure_examples.csv", index=False)
    (OUT / "paired_physics_ablations.json").write_text(
        json.dumps(ablations, indent=2) + "\n"
    )
    (OUT / "selected_vs_cheap.json").write_text(
        json.dumps(cheap_comparisons, indent=2) + "\n"
    )
    kir, audit = load_kir()
    surface = kir[kir.dataset == "kir_surface"].set_index("id").score
    confounds = []
    for (protocol, model), frame in predictions[
        predictions.dataset == "kir_function"
    ].groupby(["protocol", "model"]):
        frame = frame.copy()
        frame["surface_observed"] = frame.id.map(surface)
        paired = frame.dropna(subset=["surface_observed"])
        normal = paired[abs(paired.surface_observed) <= 0.3]
        if len(normal):
            confounds.append(
                {
                    "protocol": protocol,
                    "model": model,
                    "paired_rows": len(paired),
                    "normal_surface_rows": len(normal),
                    "observed_function_surface_rho": float(
                        spearmanr(paired.observed, paired.surface_observed).statistic
                    ),
                    "prediction_surface_rho": (
                        float(
                            spearmanr(
                                paired.prediction, paired.surface_observed
                            ).statistic
                        )
                        if paired.prediction.std() > 1e-12
                        else 0
                    ),
                    "normal_surface_gain_prevalence": float(normal.beneficial.mean()),
                    "normal_surface_precision20": precision_at_k(
                        normal.prediction.to_numpy(),
                        normal.beneficial.to_numpy(bool),
                        20,
                    ),
                    "note": "Oracle post-evaluation stratification; measured test surface score never a predictor input",
                }
            )
    pd.DataFrame(confounds).to_csv(OUT / "function_surface_diagnostic.csv", index=False)
    bed, _ba = load_bedbrook()
    kin = "kinetics_off_y"
    cap = float(bed[bed.control][kin].max())
    trade = []
    for (protocol, model), frame in predictions[
        predictions.dataset == "bedbrook_current"
    ].groupby(["protocol", "model"]):
        frame = frame.merge(bed[["id", kin]], on="id", validate="one_to_one")
        known = frame[frame[kin].notna()]
        joint = known.beneficial & (known[kin] <= cap)
        trade.append(
            {
                "protocol": protocol,
                "model": model,
                "known_kinetics": len(known),
                "missing_kinetics": len(frame) - len(known),
                "cap_ms": cap,
                "joint_current_and_kinetics_gains": int(joint.sum()),
                "precision20_joint": precision_at_k(
                    known.prediction.to_numpy(), joint.to_numpy(bool), 20
                ),
                "note": "Exploratory stricter utility diagnostic, not preregistered fitness or a trained kinetics predictor; do not classify missing kinetics as failures",
            }
        )
    pd.DataFrame(trade).to_csv(OUT / "current_kinetics_tradeoff.csv", index=False)
    # A stricter measurement-noise diagnostic uses the observed WT-control spread, not just variant SE.
    noise = []
    for (protocol, dataset, model), frame in predictions[
        predictions.dataset.str.startswith("kir")
    ].groupby(["protocol", "dataset", "model"]):
        endpoint = dataset.split("_")[1]
        floor = audit[endpoint]["control_score_sd"]
        robust = (
            frame.observed.to_numpy()
            - 1.96 * np.sqrt(frame.reported_SE.to_numpy() ** 2 + floor**2)
            > 0.3
        )
        noise.append(
            {
                "protocol": protocol,
                "dataset": dataset,
                "model": model,
                "control_SD": floor,
                "gain_prevalence_with_WT_dispersion": float(robust.mean()),
                "precision20_with_WT_dispersion": precision_at_k(
                    frame.prediction.to_numpy(), robust, 20
                ),
                "note": "Sensitivity to WT-control heterogeneity; approximate, not validated simultaneous confidence intervals",
            }
        )
    pd.DataFrame(noise).to_csv(OUT / "WT_noise_floor_sensitivity.csv", index=False)
    (OUT / "analysis_notes.json").write_text(
        json.dumps(
            {
                "model_selection": "Validation MAE only; full tables expose all models rather than choosing by test result",
                "ranking": "Fractional expectation at tied score boundary; WT-null expected top-k precision equals prevalence. Never exploit sorted input rows.",
                "gain_definitions": "Predefined single-endpoint gains; Kir score is a membrane-potential proxy and surface expression a distinct endpoint. Increased channel function is not inherently better for patients/neurons.",
                "multiple_comparisons": "Many baselines and protocols, exploratory bootstrap intervals, related proteins and small beneficial tails; no confirmatory p-value claim.",
                "uncertainty": "Measured SE and validation residual/GP variance do not eliminate biological replication, domain shift or selected-design biases.",
            },
            indent=2,
        )
        + "\n"
    )
    print(
        pd.DataFrame(selections)[
            [
                "protocol",
                "dataset",
                "model",
                "precision20",
                "conservative_precision20",
                "spearman",
            ]
        ]
        .round(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    analyze()
