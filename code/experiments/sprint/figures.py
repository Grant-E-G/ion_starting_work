"""Export a parent-aware scientific comparison from fixed predictions."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from data import OUT
from metrics import precision_at_k


def main() -> None:
    parents = pd.read_csv(OUT / "gb1_transfer_parent_controls_pairs.csv").set_index(
        "id"
    )
    frame = pd.read_csv(OUT / "gb1_transfer_measurements.csv").set_index("id")
    singles = frame[frame.HD == 1].I20fitRaw.to_dict()
    ids = parents.index
    actual = frame.loc[ids].I20fitRaw.to_numpy()
    best_single = np.array(
        [max([1] + [singles[token] for token in ident.split(",")]) for ident in ids]
    )
    column = "best_raw_parent" if "best_raw_parent" in parents else "best_raw_single"
    best_pair = parents[column].to_numpy()
    selected = {
        "Hamming_kernel_ridge": "Sequence kernel\n(validation MSE)",
        "gb1_binding_latent_ridge": "Physical latent\n(validation MSE)",
        "ESM35_gb1_binding_control_ridge": "Sequence + physical\n(exploratory)",
    }
    predictions = pd.read_csv(OUT / "gb1_components_predictions.csv")
    rows = []
    for name, label in selected.items():
        values = (
            predictions[predictions.features == name]
            .set_index("id")
            .predicted.loc[ids]
            .to_numpy()
        )
        for endpoint, target in [
            ("Above WT", actual >= 1.2),
            ("Above best single", actual >= 1.2 * best_single),
            ("Above best double", actual >= 1.2 * best_pair),
        ]:
            rows.append(
                {
                    "method": label,
                    "endpoint": endpoint,
                    "n": len(ids),
                    "P20": precision_at_k(values, target, 20),
                    "prevalence": float(target.mean()),
                }
            )
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "figure_values.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    centers = np.arange(3)
    width = 0.24
    for i, (endpoint, color) in enumerate(
        zip(
            ["Above WT", "Above best single", "Above best double"],
            ["#4c78a8", "#f2a541", "#54a24b"],
            strict=True,
        )
    ):
        heights = table[table.endpoint == endpoint].P20.to_numpy()
        bars = ax.bar(
            centers + (i - 1) * width,
            heights,
            width,
            label=endpoint + " by ≥20%",
            color=color,
        )
        ax.bar_label(
            bars, labels=[f"{100*x:.0f}%" for x in heights], padding=3, fontsize=9
        )
    ax.set_xticks(centers, list(selected.values()))
    ax.set_ylabel("Precision among top 20")
    ax.set_ylim(0, 1.13)
    ax.set_yticks(
        np.arange(0, 1.01, 0.2), [f"{100*x:.0f}%" for x in np.arange(0, 1.01, 0.2)]
    )
    ax.set_title("Independent GB1 assay: WT gain can inherit an existing parent")
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.15)
    fig.text(
        0.12,
        0.015,
        f"Same {len(ids):,} measured higher-order constructs with complete raw parent controls.\n2242 existing older-assay labels; no higher-order test-label training. Exploratory retrospective comparison.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.095, 1, 1))
    folder = OUT / "figures"
    folder.mkdir(exist_ok=True)
    fig.savefig(folder / "parent_aware_selection.png", dpi=220)
    fig.savefig(folder / "parent_aware_selection.pdf")
    plt.close(fig)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
