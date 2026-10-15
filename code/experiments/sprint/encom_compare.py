"""Function test of chemical-contact dynamics on a matched TM-only cohort.

Cheap geometry×chemistry is the control; full473-record results are not compared
against an easier subset. ENCoM hyperparameters never tune against function.
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from bk import select_model
from bk_nullaware import scans
from data import AA, DATA, FEATURES, OUT, RAW, load_bk, write_immutable
from encom_features import references
from metrics import evaluate
from threadpoolctl import threadpool_limits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stable", action="store_true")
    args = parser.parse_args()
    suffix = "_stable" if args.stable else ""
    assert (
        OUT / "encom_resources.json"
    ).exists(), "Finish physical feature generation first"
    native = load_bk()
    computed = pd.read_csv(FEATURES / "bk_encom.csv").set_index("id")
    if "error" in computed:
        computed = computed[computed.error.isna()]
    eligible = native.id.isin(computed.index) & ~native.censored
    frame = native[eligible].reset_index(drop=True)
    y = frame.target.to_numpy()
    source = scans()
    aaindex = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")
    structures, displacement = references()
    site_order = [residue.id[1] for residue in structures["closed"]]
    coord = {
        state: np.array([residue["CA"].coord for residue in chain])
        for state, chain in structures.items()
    }
    degree = {
        state: (np.linalg.norm(points[:, None] - points[None], axis=-1) < 8).sum(1) - 1
        for state, points in coord.items()
    }
    geometry = {
        site: np.array(
            [
                degree["closed"][i],
                degree["open"][i],
                np.linalg.norm(displacement["closed"][i]),
            ]
        )
        for i, site in enumerate(site_order)
    }

    def chemical(token: str) -> np.ndarray:
        wt, alt = AA.index(token[0]), AA.index(token[-1])
        return np.concatenate(
            [
                np.eye(20)[alt] - np.eye(20)[wt],
                aaindex[alt] - aaindex[wt],
                [source.loc[token, "dHyd"], source.loc[token, "SIFT"] - 1],
            ]
        )

    chemistry = np.stack([chemical(token) for token in frame.id])
    interaction = np.stack(
        [
            np.outer(
                aaindex[AA.index(token[-1])] - aaindex[AA.index(token[0])],
                geometry[int(token[1:-1])],
            ).ravel()
            for token in frame.id
        ]
    )
    cheap = np.column_stack([chemistry, interaction])
    names = [
        column
        for column in computed
        if "_delta_" in column or column.startswith("state_difference_")
    ]
    physical = computed.loc[frame.id, names].to_numpy()
    local_frame = (
        pd.read_csv(FEATURES / "bk_evoef_r20.csv").set_index("mutation").loc[frame.id]
    )
    local = local_frame[
        [column for column in local_frame if column.startswith("state_difference_")]
    ].to_numpy()
    with np.load(FEATURES / "external_bk_sequence_deltas.npz") as arrays:
        index = pd.Index(arrays["training_ids"]).get_indexer(frame.id)
        assert (index >= 0).all()
        sequence = arrays["training_delta"][index]
    shuffled = physical.copy()
    rng = np.random.RandomState(1729)
    for site in frame.resN.unique():
        where = np.flatnonzero(frame.resN.to_numpy() == site)
        shuffled[where] = physical[rng.permutation(where)]
    blocks = {
        "chemistry": chemistry,
        "chemistry_WTgeometry": cheap,
        "geometry_EvoEF2": np.column_stack([cheap, local]),
        "geometry_ENCoM": np.column_stack([cheap, physical]),
        "geometry_ENCoM_shuffled_within_site": np.column_stack([cheap, shuffled]),
        "geometry_EvoEF2_ENCoM": np.column_stack([cheap, local, physical]),
        "sequence_geometry": np.column_stack([cheap, sequence]),
        "sequence_geometry_ENCoM": np.column_stack([cheap, sequence, physical]),
    }
    policy = {
        "hypothesis": "Mutation-sensitive collective-mode information should beat cheap geometry×AAIndex and site-preserving shuffled dynamics",
        "physical_parameters": "Published defaults, no function tuning",
        "cohort": "Numeric source variants whose sites are in common273residue TM model and successfully computed; identical cohort for all methods",
        "controls": "Zero-preserving chemistry; WT8Acontactdegrees and aligned-state-motion magnitude×chemicaldelta; EvoEF2; actual650Mmutant-minusWT; within-siteENCoMshuffle seed1729",
        "learner": "Existing Ridge/RF grids, immutable group partitions, validationMSE only",
        "status": "Exploratory new physical family on inspected source corpus; not prospective confirmation or an absolute free-energy model",
    }
    if args.stable:
        policy["numerical_filter"] = (
            "Train-onlyVarianceThreshold1e-10 beforeRidgeStandardScaler; remove floating-point noise/nearconstant columns beforeWTzeroanchor"
        )
    write_immutable(
        DATA / f"encom_comparison_policy{suffix}.json",
        json.dumps(policy, indent=2) + "\n",
    )
    partitions = pd.read_csv(DATA / "bk_partitions.csv")
    rows: list[dict] = []
    predictions: list[dict] = []
    choices: list[dict] = []
    for (protocol, seed), partition in partitions.groupby(["protocol", "seed"]):
        split = frame.id.map(partition.set_index("id").split).to_numpy()
        train, val, test = [
            np.flatnonzero(split == label) for label in ["train", "validation", "test"]
        ]
        for name, x in blocks.items():
            for learner in ["ridge", "rf"]:
                model, selection = select_model(
                    learner,
                    x,
                    y,
                    train,
                    val,
                    int(seed),
                    anchor_zero=True,
                    criterion="mse",
                    stable_features=args.stable,
                )
                output = model.predict(x[test])
                # All descriptors encode a mutation effect, so WT is zero.
                output -= model.predict(np.zeros((1, x.shape[1])))[0]
                for direction in [1, -1]:
                    rows.append(
                        {
                            "protocol": protocol,
                            "seed": int(seed),
                            "features": name,
                            "learner": learner,
                            "direction": direction,
                            "train_n": len(train),
                            "validation_n": len(val),
                            "cohort_n": len(frame),
                            **evaluate(y[test], output, 50 * direction, direction),
                        }
                    )
                predictions.extend(
                    {
                        "protocol": protocol,
                        "seed": int(seed),
                        "features": name,
                        "learner": learner,
                        "id": ident,
                        "actual": float(actual),
                        "predicted": float(value),
                    }
                    for ident, actual, value in zip(
                        frame.id[test], y[test], output, strict=True
                    )
                )
                choices.append(
                    {
                        "protocol": protocol,
                        "seed": int(seed),
                        "features": name,
                        "learner": learner,
                        **selection,
                    }
                )
        pd.DataFrame(rows).to_csv(
            OUT / f"encom_function_metrics{suffix}.csv", index=False
        )
        pd.DataFrame(predictions).to_csv(
            OUT / f"encom_function_predictions{suffix}.csv", index=False
        )
        (OUT / f"encom_function_choices{suffix}.json").write_text(
            json.dumps(choices, indent=2, default=int) + "\n"
        )
        print(protocol, seed, len(frame), "completed", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
