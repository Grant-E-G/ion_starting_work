"""Small block-normalized kernel test of sequence/energy complementarity.

Tests a specific alternative to concatenation: many sequence dimensions can
swamp a small physical block under a shared regularizer. No simulator platform.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any

import numpy as np
import pandas as pd
from bk import features
from data import DATA, OUT, load_bk
from metrics import evaluate
from scipy.linalg import solve
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler


def matrix(
    fit: np.ndarray, target: np.ndarray, scale: StandardScaler, kind: str, length: float
) -> np.ndarray:
    x, y = scale.transform(fit), scale.transform(target)
    dimensions = max(1, x.shape[1])
    if kind == "linear":
        return y @ x.T / dimensions
    r = np.sqrt(cdist(y, x, "sqeuclidean") / dimensions) / length
    # Matern 3/2: rougher nonlinear response than a squared-exponential kernel.
    return (1 + np.sqrt(3) * r) * np.exp(-np.sqrt(3) * r)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="blocks")
    args = parser.parse_args()
    frame = load_bk()
    arrays = features(frame)
    cheap_dim = arrays["cheap"].shape[1]
    physical = {"published_energy": arrays["published_energy"]}
    if "cheap_local_energy" in arrays:
        physical["local_energy"] = arrays["cheap_local_energy"][:, cheap_dim:]
    physical["audited_energy"] = arrays["audited_energy"]
    for family, block in [
        ("global1d", "closed"),
        ("global3d", "closed"),
        ("global3d", "state"),
    ]:
        key = f"metl_{family}_{block}"
        if key in arrays:
            physical[key] = arrays[key]
    parts = pd.read_csv(DATA / "bk_partitions.csv")
    rows: list[dict] = []
    predictions: list[dict] = []
    settings: list[dict] = []
    bases = [
        key
        for key in [
            "cheap",
            "esm2_35m_sequence",
            "esm1v_650m_sequence",
            "esm2_35m_mutant",
            "esm1v_650m_mutant",
            "esm2_3b_sequence",
        ]
        if key in arrays
    ]
    policy: dict[str, Any] = {
        "base_features": bases,
        "physical_features": list(physical),
        "alphas": [0.01, 0.1, 1, 10],
        "physical_weights": [0, 0.1, 1, 10],
        "kernels": ["linear", "matern"],
        "length_scales": [0.5, 1, 2],
        "selection": "Validation MSE only; no refit on validation; training-only standardization and dimension-normalized kernels",
    }
    (OUT / f"kernel_policy_{args.tag}.json").write_text(
        json.dumps(policy, indent=2) + "\n"
    )
    for protocol in parts.protocol.unique():
        for fold in sorted(parts.seed.unique()):
            split = frame.id.map(
                parts[(parts.protocol == protocol) & (parts.seed == fold)]
                .set_index("id")
                .split
            ).to_numpy()
            masks = [
                (split == label) & ~frame.censored.to_numpy()
                for label in ["train", "validation", "test"]
            ]
            fit, val, test = [np.flatnonzero(mask) for mask in masks]
            y = frame.target.to_numpy()
            center, spread = y[fit].mean(), y[fit].std()
            response = (y[fit] - center) / spread
            for base in bases:
                x = arrays[base]
                xscale = StandardScaler().fit(x[fit])
                for kind in policy["kernels"]:
                    for energy_name, energy in [
                        ("none", np.zeros((len(frame), 1))),
                        *physical.items(),
                    ]:
                        start = time.perf_counter()
                        escale = StandardScaler().fit(energy[fit])
                        best = None
                        for length in (
                            [1] if kind == "linear" else policy["length_scales"]
                        ):
                            k, kv, kt = [
                                matrix(x[fit], x[index], xscale, kind, length)
                                for index in [fit, val, test]
                            ]
                            e, ev, et = [
                                matrix(energy[fit], energy[index], escale, kind, length)
                                for index in [fit, val, test]
                            ]
                            for weight in (
                                [0]
                                if energy_name == "none"
                                else policy["physical_weights"]
                            ):
                                for alpha in policy["alphas"]:
                                    coefficients = solve(
                                        k + weight * e + alpha * np.eye(len(fit)),
                                        response,
                                        assume_a="pos",
                                    )
                                    pv = (
                                        kv + weight * ev
                                    ) @ coefficients * spread + center
                                    loss = np.mean((pv - y[val]) ** 2)
                                    if best is None or loss < best[0]:
                                        best = (
                                            loss,
                                            (kt + weight * et) @ coefficients * spread
                                            + center,
                                            weight,
                                            alpha,
                                            length,
                                        )
                        assert best is not None
                        loss, prediction, weight, alpha, length = best
                        settings.append(
                            {
                                "protocol": protocol,
                                "fold": int(fold),
                                "base": base,
                                "physical": energy_name,
                                "kernel": kind,
                                "validation_mse": float(loss),
                                "weight": weight,
                                "alpha": alpha,
                                "length": length,
                            }
                        )
                        for direction, threshold in [(1, 50), (-1, -50)]:
                            rows.append(
                                {
                                    "protocol": protocol,
                                    "fold": fold,
                                    "base": base,
                                    "physical": energy_name,
                                    "kernel": kind,
                                    "direction": direction,
                                    "selected_weight": weight,
                                    "seconds": time.perf_counter() - start,
                                    **evaluate(
                                        y[test], prediction, threshold, direction
                                    ),
                                }
                            )
                        predictions.extend(
                            {
                                "protocol": protocol,
                                "fold": fold,
                                "base": base,
                                "physical": energy_name,
                                "kernel": kind,
                                "id": ident,
                                "actual": actual,
                                "predicted": predicted,
                            }
                            for ident, actual, predicted in zip(
                                frame.id[test], y[test], prediction, strict=True
                            )
                        )
            pd.DataFrame(rows).to_csv(
                OUT / f"kernel_metrics_{args.tag}.csv", index=False
            )
            pd.DataFrame(predictions).to_csv(
                OUT / f"kernel_predictions_{args.tag}.csv", index=False
            )
            (OUT / f"kernel_selection_{args.tag}.json").write_text(
                json.dumps(settings, indent=2) + "\n"
            )
            print(protocol, fold, "completed", flush=True)


if __name__ == "__main__":
    main()
