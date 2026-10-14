"""Export scientific comparisons; figures describe measured held-out sequences only."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from data import OUT


def save(fig, name: str) -> None:
    folder = OUT / "figures"
    folder.mkdir(exist_ok=True)
    for ext in ["png", "pdf"]:
        fig.savefig(folder / f"{name}.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plots() -> None:
    m = pd.read_csv(OUT / "metrics.csv")
    p = pd.read_csv(OUT / "predictions.csv", low_memory=False)
    panels = [
        ("bedbrook_temporal", "bedbrook_current", "Later ChR rounds"),
        ("bedbrook_cluster90", "bedbrook_current", "ChR 90%-identity components"),
        ("kir_site_hash", "kir_function", "Kir function: unseen sites"),
        ("kir_site_hash", "kir_surface", "Kir trafficking: unseen sites"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    models = [
        "WT_null",
        "properties_Ridge",
        "conservation_Ridge",
        "sequence_Ridge",
        "esm_Ridge",
        "esm_physics_Ridge",
    ]
    for ax, (protocol, dataset, title) in zip(axes.ravel(), panels):
        sub = m[(m.protocol == protocol) & (m.dataset == dataset)].set_index("model")
        names = models + (
            ["sequence_GP"]
            if dataset.startswith("bedbrook")
            else ["sequence_HGB", "sequence_physics_HGB"]
        )
        ax.bar(
            np.arange(len(names)),
            sub.loc[names, "precision20"],
            label="Point-estimate gains",
        )
        if dataset.startswith("kir"):
            ax.plot(
                np.arange(len(names)),
                sub.loc[names, "conservative_precision20"],
                "ko",
                label="Gain + reported-SE filter",
            )
            ax.legend(fontsize=6)
        ax.axhline(
            float(sub.loc["WT_null", "prevalence"]),
            ls=":",
            color="gray",
            label="Gain prevalence",
        )
        ax.set_xticks(
            np.arange(len(names)),
            [
                n.replace("_Ridge", "")
                .replace("sequence", "seq")
                .replace("physics", "struct")
                for n in names
            ],
            rotation=35,
            ha="right",
            fontsize=8,
        )
        ax.set_ylim(0, 1)
        ax.set_ylabel("Expected precision among top 20")
        ax.set_title(title)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(
        "Retrospective gain selection; point gains are not verified neuronal benefit\nTies use fractional expectation. SE filter unavailable for ChR means."
    )
    fig.tight_layout()
    save(fig, "gain_selection")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, (protocol, title) in zip(
        axes,
        [
            ("bedbrook_temporal", "Temporal: ESM ridge"),
            ("bedbrook_cluster90", "Component holdout: sequence GP"),
        ],
    ):
        name = "esm_Ridge" if protocol.endswith("temporal") else "sequence_GP"
        sub = p[(p.protocol == protocol) & (p.model == name)]
        ax.scatter(
            sub.observed,
            sub.prediction,
            c=sub.beneficial,
            cmap="coolwarm",
            vmin=0,
            vmax=1,
        )
        limits = [0, max(sub.observed.max(), sub.prediction.max()) * 1.05]
        ax.plot(limits, limits, "k:")
        ax.set_xlim(limits)
        ax.set_ylim(limits)
        ax.set_xlabel("Measured peak current (nA)")
        ax.set_ylabel("Predicted peak current (nA)")
        ax.set_title(title)
    fig.tight_layout()
    save(fig, "current_transfer")
    curves = pd.read_csv(OUT / "mscl_curves.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8), sharey=True)
    for ax, variant in zip(axes, ["V23T", "V23D", "G22N"]):
        sub = curves[curves.variant == variant]
        obs = sub[sub.model == "WT_null"]
        ax.plot(
            obs.tension_mN_m,
            obs.observed_parameter_reconstruction,
            "ko-",
            label="Measured-parameter reconstruction",
        )
        for model in sub.model.unique():
            case = sub[sub.model == model]
            ax.plot(case.tension_mN_m, case.prediction, "--", label=model)
        ax.set_xlabel("Tension (mN/m)")
        ax.set_title(f"{variant}: its site withheld")
        ax.set_ylim(-0.03, 1.03)
    axes[0].set_ylabel("Equilibrium relative conductance")
    axes[0].legend(fontsize=6)
    fig.suptitle(
        "MscL: 3 mutant genotypes, only 2 sites; curves are not extra independent labels"
    )
    fig.tight_layout()
    save(fig, "mscl_mapping_failure")


if __name__ == "__main__":
    plots()
