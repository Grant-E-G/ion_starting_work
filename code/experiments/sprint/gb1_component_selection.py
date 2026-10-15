"""Select fixed transfer readouts using OLD validation utility, never Wu scores.

Quantifies the difference between best-test anecdotes and executable selection.
All candidate predictions/hyperparameters already frozen by earlier fits.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import DATA, FEATURES, OUT, write_immutable
from gb1_components import codes, components, sequence_features
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def main() -> None:
    old, _ = components()
    y = old.target.to_numpy()
    train = np.flatnonzero(old.split.to_numpy() == "train")
    val = np.flatnonzero(old.split.to_numpy() == "validation")
    code = codes(old)
    a, p = sequence_features(code)
    single = old[old.num_mutations == 1].set_index("id").target.to_dict()
    parents = np.array(
        [max([0] + [single[token] for token in ident.split(",")]) for ident in old.id]
    )
    positive = y >= parents + np.log(1.2)
    blocks = {"site_additive": a, "site_pairwise": p}
    for key in ["esm2_35m", "gb1_binding", "gb1_binding_control"]:
        with np.load(FEATURES / f"gb1_components_{key}.npz") as values:
            assert np.array_equal(values["ids"], old.id)
            if key == "esm2_35m":
                blocks["ESM35"] = values["pooled_delta"]
            else:
                for column in ["attributes", "latent"]:
                    blocks[f"{key}_{column}"] = values[column]
                    if column == "attributes":
                        blocks[f"ESM35_{key}"] = np.column_stack(
                            [blocks["ESM35"], values[column]]
                        )
    selection = json.loads((OUT / "gb1_components_choices.json").read_text())
    rows = []
    for choice in selection:
        name = choice["features"]
        if name == "Hamming_kernel":
            from scipy.linalg import cho_factor, cho_solve

            beta, alpha = choice["beta"], choice["alpha"]
            kernel = np.exp(-beta * (code[:, None, :] != code[None, :, :]).sum(2))
            coefficient = cho_solve(
                cho_factor(kernel[np.ix_(train, train)] + alpha * np.eye(len(train))),
                y[train],
            )
            native = np.array([list("ACDEFGHIKLMNPQRSTVWY").index(aa) for aa in "VDGV"])
            zero = np.exp(-beta * (code[train] != native).sum(1)) @ coefficient
            prediction = kernel[np.ix_(val, train)] @ coefficient - zero
            case = "Hamming_kernel_ridge"
        else:
            x = blocks[name]
            setting = choice["setting"]
            learner = choice["learner"]
            model = (
                make_pipeline(StandardScaler(), Ridge(alpha=setting))
                if learner == "ridge"
                else ExtraTreesRegressor(
                    n_estimators=300,
                    min_samples_leaf=setting,
                    max_features="sqrt",
                    n_jobs=3,
                    random_state=1729,
                )
            )
            model.fit(x[train], y[train])
            prediction = (
                model.predict(x[val]) - model.predict(np.zeros((1, x.shape[1])))[0]
            )
            case = f"{name}_{learner}"
        for ranking, score in [
            ("predicted_function", prediction),
            ("predicted_increment_using76controls", prediction - parents[val]),
        ]:
            rows.append(
                {
                    "features": case,
                    "family": "physical" if "gb1_binding" in case else "nonphysical",
                    "ranking": ranking,
                    "validation_n": len(val),
                    "validation_beyond_parent_positives": int(positive[val].sum()),
                    "validation_beyond_parent_AP": float(
                        average_precision_score(positive[val], score)
                    ),
                    "validation_MSE": float(np.mean((prediction - y[val]) ** 2)),
                }
            )
    data = pd.DataFrame(rows)
    data.to_csv(OUT / "gb1_component_validation_utility.csv", index=False)
    test = pd.read_csv(OUT / "gb1_components_metrics.csv")
    test = test[test.order == 0].set_index("features")
    selected = []
    for (family, ranking), part in data.groupby(["family", "ranking"]):
        for objective in ["validation_MSE", "validation_beyond_parent_AP"]:
            best = part.sort_values(
                [objective, "validation_MSE"],
                ascending=[objective == "validation_MSE", True],
            ).iloc[0]
            selected.append(
                {
                    **best.to_dict(),
                    "selected_by": objective,
                    "test_WT_gain_P20": float(test.loc[best.features, "P20"]),
                    "test_beyond_parent_P20": float(
                        test.loc[
                            best.features,
                            (
                                "beyond_parent_P20"
                                if ranking == "predicted_function"
                                else "beyond_parent_increment_P20"
                            ),
                        ]
                    ),
                    "test_rescue_P20_plain_function": float(
                        test.loc[best.features, "rescue_P20"]
                    ),
                }
            )
    pd.DataFrame(selected).to_csv(
        OUT / "gb1_component_validation_selected.csv", index=False
    )
    policy = {
        "purpose": "Posthoc audit of whether oldvalidation can choose useful fixed physical readouts, not choosing maximumWu testP20",
        "selection": "Existing per-family MSE-selected hyperparameters unchanged; choose family member by oldvalidationMSE or conditionalgainAP, tied byMSE",
        "labels": "OldOlsondoubles relative to76measuredOlsonsingleparents; noWu outcome used forselection. Secondary testincrement ranking explicitly uses76Wu raw single controls",
        "validation_positives": int(positive[val].sum()),
        "validation_n": len(val),
        "scope": "Exploratory selection-rule audit after seeing independenttestresults; chosen rule needs another untouched experiment, no confirmatory significance claim",
    }
    write_immutable(
        DATA / "gb1_component_selection_policy.json",
        json.dumps(policy, indent=2) + "\n",
    )
    print(pd.DataFrame(selected).round(3).to_string(index=False))


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
