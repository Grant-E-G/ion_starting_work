"""Standalone scientific figures from saved calculations; no refitting or smoothed data."""

from __future__ import annotations

import json

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from physics import ROOT


def plots() -> None:
    out = ROOT / "notes/ompf/figures"
    out.mkdir(exist_ok=True)
    measurements = pd.read_csv(ROOT / "sources/ompf/measurements.csv")
    primary = measurements[measurements.study == "miedema2004"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
    for ax, (salt, c) in zip(
        axes.ravel(), [("KCl", 0.1), ("KCl", 1.0), ("NaCl", 0.1), ("NaCl", 1.0)]
    ):
        subset = primary[(primary.salt == salt) & (primary.molarity_M == c)]
        wt = subset[subset.variant == "WT"].iloc[0]
        subset = subset[subset.variant != "WT"]
        xs = np.arange(len(subset))
        variants = list(subset.variant)
        ratio = subset.conductance_nS / wt.conductance_nS
        error = np.hypot(
            subset.error_nS / wt.conductance_nS,
            subset.conductance_nS * wt.error_nS / wt.conductance_nS**2,
        )
        ax.errorbar(
            xs,
            ratio,
            yerr=error,
            fmt="ko",
            capsize=3,
            label="Experiment (reported dispersion)",
        )
        for h, marker in [(0.15, "s"), (0.1, "^"), (0.075, "v")]:
            values = []
            geometry = []
            basefile = (
                ROOT / f"notes/ompf/trimer/WT_trimer_c{c}_h{h}_nonlinear_pb_seed0.json"
            )
            if not basefile.exists():
                continue
            base = json.loads(basefile.read_text())["predictions"][salt]
            for v in variants:
                p = (
                    ROOT
                    / f"notes/ompf/trimer/{v}_trimer_c{c}_h{h}_nonlinear_pb_seed0.json"
                )
                if not p.exists():
                    break
                r = json.loads(p.read_text())["predictions"][salt]
                values.append(r["physics_nS"] / base["physics_nS"])
                geometry.append(r["geometry_nS"] / base["geometry_nS"])
            if len(values) != len(variants):
                continue
            ax.plot(xs, values, marker=marker, label=f"Physics h={h:g} nm")
            if h == 0.075:
                ax.plot(xs, geometry, "x--", label="Geometry h=0.075 nm")
        ax.axhline(1, color="gray", linestyle=":")
        ax.axhline(1.05, color="gray", linestyle="--", alpha=0.4)
        ax.set_xticks(xs, variants)
        ax.set_title(f"{salt} {c:g} M")
        ax.set_ylabel("Mutant / WT conductance")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle("Matched zero-voltage slope cohort: full trimer, WT-normalized")
    fig.tight_layout()
    fig.savefig(out / "gain_predictions.png", dpi=180)
    fig.savefig(out / "gain_predictions.pdf")
    plt.close(fig)
    frame = pd.read_csv(
        ROOT / "notes/ompf/comparisons_trimer_nonlinear_pb_h0.15_seed0.csv"
    )
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, (name, condition) in zip(
        axes,
        [
            ("Matched zero-voltage slope", frame.study == "miedema2004"),
            ("Finite-voltage challenges", frame.study != "miedema2004"),
        ],
    ):
        subset = frame[condition & (frame.variant != "WT")]
        for model, marker in [
            ("physics", "o"),
            ("geometry", "x"),
            ("charge_entry", "^"),
        ]:
            ax.scatter(
                subset.observed_ratio,
                subset[model + "_ratio"],
                marker=marker,
                label=model,
            )
        ax.plot([0.5, 2.0], [0.5, 2.0], "k:", lw=1)
        ax.set_xlabel("Observed mutant / WT")
        ax.set_ylabel("Predicted mutant / WT")
        ax.set_title(name)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "baseline_comparison.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, variant in zip(axes, ["WT", "EAE"]):
        p = (
            ROOT
            / f"notes/ompf/trimer/{variant}_trimer_c0.1_h0.15_nonlinear_pb_seed0_field.npz"
        )
        field = np.load(p)
        u = field["potential"]
        water = field["water"]
        k = u.shape[2] // 2
        display = np.ma.masked_where(~water[:, :, k], u[:, :, k])
        im = ax.imshow(
            display.T,
            origin="lower",
            extent=[-5.25, 5.25, -5.25, 5.25],
            vmin=-5,
            vmax=5,
            cmap="coolwarm",
        )
        ax.set_title(f"{variant}: accessible aqueous potential")
        ax.set_xlabel("x (nm)")
        ax.set_ylabel("y (nm)")
    fig.colorbar(im, ax=axes, label="e phi / kT", shrink=0.8)
    fig.suptitle("Full biological trimer, 0.1 M salt; inaccessible regions masked")
    fig.savefig(out / "electrostatic_slice.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    plots()
