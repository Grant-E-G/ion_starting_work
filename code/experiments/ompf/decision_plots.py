"""Export decision figures, keeping retrospective gains and challenge failures visible."""

from __future__ import annotations

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from physics import ROOT


def save(fig: plt.Figure, name: str) -> None:
    for extension in ["png", "pdf"]:
        fig.savefig(
            ROOT / f"notes/ompf/figures/{name}.{extension}",
            dpi=180,
            bbox_inches="tight",
        )
    plt.close(fig)


def plots() -> None:
    folder = ROOT / "notes/ompf"
    coarse = pd.read_csv(
        folder / "comparisons_trimer_image_trimer_s3_nonlinear_pb_h0.15_seed0.csv"
    )
    fine = pd.read_csv(
        folder / "comparisons_trimer_image_trimer_s3_nonlinear_pb_h0.1_seed0.csv"
    )
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
    for ax, (salt, concentration) in zip(
        axes.ravel(), [("KCl", 0.1), ("KCl", 1.0), ("NaCl", 0.1), ("NaCl", 1.0)]
    ):
        group = coarse[
            (coarse.study == "miedema2004")
            & (coarse.variant != "WT")
            & (coarse.salt == salt)
            & (coarse.molarity_M == concentration)
        ]
        xs = np.arange(len(group))
        ax.plot(xs, group.observed_ratio, "ko", label="Experimental means")
        ax.plot(xs, group.physics_ratio, "s-", label="Image + PB, 0.15 nm")
        ax.plot(xs, group.geometry_ratio, "x--", label="Geometry, 0.15 nm")
        detailed = fine[
            (fine.study == "miedema2004")
            & (fine.variant != "WT")
            & (fine.salt == salt)
            & (fine.molarity_M == concentration)
        ].set_index("variant")
        ax.plot(
            xs,
            detailed.loc[group.variant, "physics_ratio"],
            "^-",
            label="Image + PB, 0.10 nm",
        )
        ax.axhline(1, linestyle=":", color="gray")
        ax.set_xticks(xs, group.variant)
        ax.set_ylabel("Mutant / WT conductance")
        ax.set_title(f"{salt} {concentration:g} M")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle(
        "Retrospective gains: eight conditions, only three constructs\nWT-normalized; image correction investigated after ordinary-PB failures"
    )
    fig.tight_layout()
    save(fig, "image_gain_predictions")

    frame = pd.read_csv(folder / "global_calibration_trimer_image_trimer_s3.csv")
    wt = frame[(frame.study == "miedema2004") & (frame.variant == "WT")].sort_values(
        ["salt", "molarity_M"]
    )
    labels = [f"{row.salt}\n{row.molarity_M:g} M" for row in wt.itertuples()]
    xs = np.arange(len(wt))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(xs - 0.16, wt.conductance_nS, width=0.32, label="Experimental WT")
    ax.bar(
        xs + 0.16,
        wt.physics_global_nS,
        width=0.32,
        label="Image model: one WT calibration",
    )
    ax.set_xticks(xs, labels)
    ax.set_ylabel("Trimer conductance (nS)")
    ax.set_title("Absolute transfer after calibration at WT 1 M KCl")
    ax.legend()
    fig.tight_layout()
    save(fig, "absolute_WT_transfer")

    frame = pd.read_csv(folder / "state_challenge_trimer.csv")
    data = pd.read_csv(ROOT / "sources/ompf/measurements.csv")
    data = data[data.study == "miedema_d127_2006"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for x, variant in enumerate(["D127N", "D127K"]):
        observed = data[data.variant == variant]
        ax.errorbar(
            np.full(len(observed), x - 0.15),
            observed.conductance_nS,
            yerr=observed.error_nS,
            fmt="ko",
            capsize=3,
            label="Distinct experimental populations" if x == 0 else None,
        )
        for shift, model, marker in [(0.05, "ordinary", "s"), (0.2, "image", "^")]:
            row = frame[(frame.variant == variant) & (frame.model == model)].iloc[0]
            ax.plot(
                x + shift,
                row.predicted_nS,
                marker,
                markersize=8,
                label=f"{model} scalar model" if x == 0 else None,
            )
    ax.axhline(0.710, linestyle=":", color="gray", label="Study WT mean")
    ax.set_xticks([0, 1], ["D127N", "D127K"])
    ax.set_ylabel("Trimer slope conductance (nS)")
    ax.set_title(
        "Additional-site challenge: scalar predictions miss state behavior\nError bars are reported dispersion, not confidence intervals"
    )
    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "D127_state_challenge")


if __name__ == "__main__":
    plots()
