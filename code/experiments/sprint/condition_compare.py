"""Does measured assay-control context explain BK prediction failures?

No mutant Vhalf is used as input. WT control voltage and nominal calcium are
known before measuring a mutant, but were absent from the sequence/structure
benchmark. This is a context diagnostic, not a validated new engineering model.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from bk import features, select_model
from data import DATA, OUT, load_bk, write_immutable
from metrics import evaluate
from threadpoolctl import threadpool_limits


def main() -> None:
    frame = load_bk()
    conditions = (
        pd.read_csv(OUT / "bk_assay_conditions.csv").set_index("id").loc[frame.id]
    )
    calcium = conditions["[Ca0]/M"].to_numpy()
    context = np.column_stack(
        [
            conditions["WTV1/2[Ca0]/mV"],
            calcium > 0,
            np.log10(np.maximum(calcium, 1e-12)),
            pd.get_dummies(frame.Species, dtype=float),
        ]
    )
    available = features(frame)
    blocks = {"assay_control_only_diagnostic": context}
    for base in ["cheap", "esm1v_650m_sequence"]:
        x = available[base]
        blocks[base] = x
        blocks[base + "_assay_context"] = np.column_stack([x, context])
        blocks[base + "_assay_context_energy"] = np.column_stack(
            [x, context, available["audited_energy"]]
        )
    policy = {
        "hypothesis": "Unmodelled assay controls or mixed WT species may limit the physical/sequence benchmark",
        "inputs": "Only WT controlVhalf, nominalcalcium, species; no MT controlVhalf, mutant labels or publication identifier as input",
        "warning": "WT control is mathematically part of the delta label; context gains can include mathematical coupling and do not establish a causal physical model. Most auxiliary/splice/temperature/lipid conditions remain unknown.",
        "cohorts": "All numeric445 and human-only numeric subset; same immutable tests, no new splits",
        "model_selection": "Same Ridge/RF candidates, validationMAE; human-only cohort matches structural species but is not assumed homogeneous in assay conditions",
        "status": "Exploratory diagnosis following a confirmed source-context discrepancy; not new independent validation",
    }
    policy["metadata_correction"] = (
        "Originalpolicy text saidMSE; actual sharedselector and saved choices used validation_mae. This corrects documentation only; originalpolicy preserved, predictions unchanged."
    )
    write_immutable(
        DATA / "condition_compare_policy_v2.json", json.dumps(policy, indent=2) + "\n"
    )
    parts = pd.read_csv(DATA / "bk_partitions.csv")
    y = frame.target.to_numpy()
    rows: list[dict] = []
    predictions: list[dict] = []
    choices: list[dict] = []
    for cohort in ["all_numeric", "human_species_only_assays_unresolved"]:
        eligible = ~frame.censored.to_numpy()
        if cohort.startswith("human"):
            eligible &= frame.Species.to_numpy() == "hslo1"
        for (protocol, seed), partition in parts.groupby(["protocol", "seed"]):
            split = frame.id.map(partition.set_index("id").split).to_numpy()
            train, val, test = [
                np.flatnonzero((split == label) & eligible)
                for label in ["train", "validation", "test"]
            ]
            if len(train) < 10 or len(val) < 3 or not len(test):
                continue
            for name, x in blocks.items():
                for learner in ["ridge", "rf"]:
                    model, choice = select_model(learner, x, y, train, val, int(seed))
                    output = model.predict(x[test])
                    for direction in [1, -1]:
                        rows.append(
                            {
                                "cohort": cohort,
                                "protocol": protocol,
                                "seed": int(seed),
                                "features": name,
                                "learner": learner,
                                "direction": direction,
                                "train_n": len(train),
                                "validation_n": len(val),
                                **evaluate(y[test], output, 50 * direction, direction),
                            }
                        )
                    predictions.extend(
                        {
                            "cohort": cohort,
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
                            "cohort": cohort,
                            "protocol": protocol,
                            "seed": int(seed),
                            "features": name,
                            "learner": learner,
                            **choice,
                        }
                    )
            pd.DataFrame(rows).to_csv(OUT / "condition_metrics.csv", index=False)
            pd.DataFrame(predictions).to_csv(
                OUT / "condition_predictions.csv", index=False
            )
            (OUT / "condition_choices.json").write_text(
                json.dumps(choices, indent=2, default=int) + "\n"
            )
            print(cohort, protocol, seed, "completed", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
