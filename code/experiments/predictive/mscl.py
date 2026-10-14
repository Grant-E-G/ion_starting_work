"""Falsify a global mutation-to-gating mapping on two withheld mutation sites.

The labels are published occupancy-fitted thermodynamic parameters, not raw traces
or survival benefits. Never count tension points or states as independent mutants.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import DATA, OUT
from features import HYDRO, VOLUME
from scipy.special import softmax

KT_PN_NM = 0.01380649 * 298.15  # 4.1164 pN nm; 1 mN/m * nm^2 = 1 pN nm.
TENSIONS = np.array([0.0, 2.0, 5.0, 8.0, 10.4, 12.0, 15.0])


def state_current(energy: np.ndarray, area: np.ndarray) -> np.ndarray:
    potentials = np.column_stack(
        [
            np.zeros(len(TENSIONS)),
            -energy[None, :] + TENSIONS[:, None] * area[None, :] / KT_PN_NM,
        ]
    )
    return softmax(potentials, axis=1) @ np.array([0.0, 0.13, 0.22, 1.0])


def run() -> None:
    frame = pd.read_csv(DATA / "mscl2005_gating.csv")
    wt = frame[frame.variant == "WT"].set_index("state").loc[["S13", "S22", "O"]]
    e0 = wt.deltaE_kT.to_numpy()
    a0 = wt.deltaA_nm2.to_numpy()
    variants = ["V23T", "V23D", "G22N"]
    results = []
    curves = []
    partitions = pd.DataFrame(
        [
            {
                "held_site": site,
                "variant": v,
                "split": "test" if int(v[1:-1]) == site else "train",
            }
            for site in [22, 23]
            for v in variants
        ]
    )
    target = DATA / "mscl_partitions.csv"
    text = partitions.to_csv(index=False)
    if target.exists():
        assert target.read_text() == text
    else:
        target.write_text(text)
    for held_site in [22, 23]:
        train = [v for v in variants if int(v[1:-1]) != held_site]
        test = [v for v in variants if int(v[1:-1]) == held_site]
        x = np.array([HYDRO[v[-1]] - HYDRO[v[0]] for v in train])
        z = np.array([(VOLUME[v[-1]] - VOLUME[v[0]]) / 100 for v in train])
        delta_e = np.array(
            [
                frame[frame.variant == v]
                .set_index("state")
                .loc[wt.index]
                .deltaE_kT.to_numpy()
                - e0
                for v in train
            ]
        )
        delta_a = np.array(
            [
                frame[frame.variant == v]
                .set_index("state")
                .loc[wt.index]
                .deltaA_nm2.to_numpy()
                - a0
                for v in train
            ]
        )
        beta = float(np.sum(x[:, None] * delta_e) / (3 * np.sum(x * x)))
        eta = float(np.sum(z[:, None] * delta_a) / (3 * np.sum(z * z)))
        for v in test:
            observed = frame[frame.variant == v].set_index("state").loc[wt.index]
            for model in ["WT_null", "hydration_shift", "hydration_and_area"]:
                energy = e0.copy()
                area = a0.copy()
                if model != "WT_null":
                    energy = energy + beta * (HYDRO[v[-1]] - HYDRO[v[0]])
                if model == "hydration_and_area":
                    area = area + eta * (VOLUME[v[-1]] - VOLUME[v[0]]) / 100
                predicted_current = state_current(energy, area)
                observed_current = state_current(
                    observed.deltaE_kT.to_numpy(), observed.deltaA_nm2.to_numpy()
                )
                results.append(
                    {
                        "variant": v,
                        "held_site": held_site,
                        "training_variants": "/".join(train),
                        "model": model,
                        "beta_kT_per_KD_unit": beta if model != "WT_null" else None,
                        "area_coefficient_nm2_per_100A3": (
                            eta if model == "hydration_and_area" else None
                        ),
                        "energy_MAE_kT": float(
                            abs(energy - observed.deltaE_kT.to_numpy()).mean()
                        ),
                        "area_MAE_nm2": float(
                            abs(area - observed.deltaA_nm2.to_numpy()).mean()
                        ),
                        "reconstructed_current_MAE": float(
                            abs(predicted_current - observed_current).mean()
                        ),
                        "negative_predicted_expansion": bool((area < 0).any()),
                    }
                )
                for tension, pred, obs in zip(
                    TENSIONS, predicted_current, observed_current
                ):
                    curves.append(
                        {
                            "variant": v,
                            "model": model,
                            "tension_mN_m": tension,
                            "prediction": pred,
                            "observed_parameter_reconstruction": obs,
                        }
                    )
    pd.DataFrame(results).to_csv(OUT / "mscl_site_holdout.csv", index=False)
    pd.DataFrame(curves).to_csv(OUT / "mscl_curves.csv", index=False)
    (OUT / "mscl_audit.json").write_text(
        json.dumps(
            {
                "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2217497/",
                "table": "I",
                "phenotype": "State-occupancy-derived energy and expansion; reconstructing equilibrium currents is not new experimental validation",
                "independent_mutants": 3,
                "independent_mutation_sites": 2,
                "conditions": "Inside-out E. coli PB104 spheroplast patches; room temperature; -20mV; symmetric200mMKCl90mMMgCl2 10mMCaCl2 10mMHEPES pH6",
                "WT_warning": "Substate WT values use a unified fit to10 traces, no separate SD reported",
                "mapping": "A single hydration coefficient shifts all wetted states; optional single global volume-area coefficient; trained on other mutation site only. No arbitrary per-mutant energies.",
                "selection": "These mutations were chosen historically for GOF gating, not protective survival; all-positive targeted sample cannot establish useful-mutation precision.",
                "library2015": "113 cysteine substitutions plus five chemical modifications: chemically altered proteins not independent sequence genotypes",
                "library2003": "Large phenotype library identified; exact supplementary labels not retrieved; not silently treated as regression labels",
                "G22_1999": "All19 substitutions at one site documented; exact scanned graph data not transcribed as invented numerical labels",
            },
            indent=2,
        )
        + "\n"
    )
    print(pd.DataFrame(results).round(3).to_string(index=False))


if __name__ == "__main__":
    run()
