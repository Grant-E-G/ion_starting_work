"""Does directly learning useful gains reveal information hidden by MSE?

GFP positive control: same strict groups/cache, genuine96/1256development-label
budgets. Actual mutant-minus-WT PLM features and physical-source features.
Exploratory objective test on an inspected soluble corpus, not membrane proof.
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd
from data import (
    AA,
    DATA,
    FEATURES,
    OUT,
    RAW,
    SEEDS,
    load_vep,
    vep_split,
    write_immutable,
)
from metrics import precision_at_k
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from tabular import aggregate
from threadpoolctl import threadpool_limits
from vep import lookups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-limit", type=int, required=True)
    parser.add_argument("--validation-limit", type=int, required=True)
    args = parser.parse_args()
    tag = f"n{args.train_limit}_val{args.validation_limit}"
    frame, _sequence, offset = load_vep("avgfp")
    y = frame.target.to_numpy() >= 0.1
    aaindex = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")
    lookup, _, _ = lookups("avgfp")
    identity = np.eye(20)
    chemistry = {
        token: np.concatenate(
            [
                identity[AA.index(token[-1])] - identity[AA.index(token[0])],
                aaindex[AA.index(token[-1])] - aaindex[AA.index(token[0])],
            ]
        )
        for ident in frame.id
        for token in ident.split(",")
    }
    cached = {}
    for model in ["esm2_35m", "esm1v_650m"]:
        with np.load(FEATURES / f"avgfp_{model}_mutant_embeddings.npz") as values:
            cached[model] = {
                key: values[key] for key in ["ids", "pooled", "mutated_sites"]
            }
        with np.load(FEATURES / f"avgfp_{model}.npz") as values:
            cached[model]["native_hidden"] = values["wt_hidden"]
    metl = {}
    with np.load(FEATURES / "avgfp_metl_avgfp_local.npz") as values:
        metl = {
            key: values[key] for key in ["ids", "attributes_native", "latent_native"]
        }
    policy = {
        "hypothesis": "Physical features may help useful-gain selection when the learner optimizes that objective rather than damage-dominated regression MSE",
        "target": "GFP WT-normalizedlog10fluorescence>=.1 (>=25.9%gain), point labels not confidence bounds",
        "budget": vars(args),
        "models": "Class-balancedLogisticC.01/.1/1/10; ExtraTrees300leaf1/3 when<=500features",
        "selection": "Validation AP then logloss; when validation has no positive, only logloss. Train with zero positives uses a prior and is flagged.",
        "features": "Chemical/count controls; exactRosetta and matchedEvoEF2;35/650Mactual-mutant-minusWT; source-onlylocalMETLattributes/latent",
        "partition": "Existing five-seed site/mutation groups; original full-pool train prefixes and label-blind cappedvalidation, no reassignment",
        "status": "Exploratory objective test on inspected soluble data, not a new independent confirmation or membrane target choice",
    }
    write_immutable(
        DATA / f"gain_classifier_{tag}_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    rows: list[dict] = []
    predictions: list[dict] = []
    choices: list[dict] = []
    for protocol in ["site", "mutation"]:
        for seed in SEEDS:
            split = vep_split(frame, "avgfp", protocol, seed, offset)
            train = np.random.RandomState(seed).permutation(
                np.flatnonzero(split == "train")
            )[: args.train_limit]
            val = np.random.RandomState(seed + 314).permutation(
                np.flatnonzero(split == "validation")
            )[: args.validation_limit]
            test = np.flatnonzero(split == "test")
            selected = np.concatenate([train, val, test])
            subset = frame.iloc[selected]
            local_train = np.arange(len(train))
            local_val = np.arange(len(train), len(train) + len(val))
            local_test = np.arange(len(train) + len(val), len(selected))
            positive = y[selected]
            tokens = [ident.split(",") for ident in subset.id]
            counts = subset.num_mutations.to_numpy()
            base = np.column_stack(
                [
                    counts,
                    np.array(
                        [
                            aggregate([chemistry[token] for token in parts])
                            for parts in tokens
                        ]
                    ),
                ]
            )
            blocks = {"cheap": base}
            physical = {}
            for name in ["rosetta", "evoef_matched"]:
                matrix = lookup[name]
                physical[name] = np.array(
                    [
                        aggregate(
                            [
                                matrix[int(token[1:-1]) - offset, AA.index(token[-1])]
                                for token in parts
                            ]
                        )
                        for parts in tokens
                    ]
                )
                blocks[f"cheap_{name}"] = np.column_stack([base, physical[name]])
            for model, values in cached.items():
                index = pd.Index(values["ids"]).get_indexer(subset.id)
                assert (index >= 0).all()
                native_hidden = values["native_hidden"]
                pool_delta = values["pooled"][index] - native_hidden.mean(0)
                native_sites = np.stack(
                    [
                        native_hidden[
                            [int(token[1:-1]) - offset for token in parts]
                        ].sum(0)
                        for parts in tokens
                    ]
                )
                site_delta = (
                    values["mutated_sites"][index] * counts[:, None] - native_sites
                )
                seq = np.column_stack([base, pool_delta, site_delta])
                blocks[f"{model}_delta"] = seq
                for name, matrix in physical.items():
                    blocks[f"{model}_delta_{name}"] = np.column_stack([seq, matrix])
            order = pd.Index(metl["ids"]).get_indexer(subset.id)
            assert (order >= 0).all()
            for block in ["attributes_native", "latent_native"]:
                blocks[f"metl_local_{block}"] = np.column_stack(
                    [base, metl[block][order]]
                )
            blocks["esm1v_650m_delta_metl_attributes"] = np.column_stack(
                [blocks["esm1v_650m_delta"], metl["attributes_native"][order]]
            )
            for name, x in {
                "constant_prior": np.zeros((len(subset), 1)),
                **blocks,
            }.items():
                assert np.isfinite(x).all()
                for learner in (
                    ["prior"]
                    if name == "constant_prior"
                    else ["logistic", "extra"] if x.shape[1] <= 500 else ["logistic"]
                ):
                    start = time.perf_counter()
                    positives = int(positive[local_train].sum())
                    if learner == "prior" or positives in [0, len(local_train)]:
                        score = np.full(
                            len(local_test), (positives + 0.5) / (len(local_train) + 1)
                        )
                        choice: dict = {
                            "reason": (
                                "Training prevalence prior; no contrast"
                                if positives in [0, len(local_train)]
                                else "Training prevalence prior"
                            )
                        }
                    else:
                        candidates = (
                            [
                                make_pipeline(
                                    StandardScaler(),
                                    LogisticRegression(
                                        C=c,
                                        class_weight="balanced",
                                        solver="liblinear",
                                        max_iter=1000,
                                        random_state=seed,
                                    ),
                                )
                                for c in [0.01, 0.1, 1, 10]
                            ]
                            if learner == "logistic"
                            else [
                                ExtraTreesClassifier(
                                    n_estimators=300,
                                    min_samples_leaf=leaf,
                                    class_weight="balanced",
                                    max_features="sqrt",
                                    random_state=seed,
                                    n_jobs=3,
                                )
                                for leaf in [1, 3]
                            ]
                        )
                        options = []
                        for model in candidates:
                            model.fit(x[local_train], positive[local_train])
                            pv = model.predict_proba(x[local_val])[:, 1]
                            ap = (
                                float(average_precision_score(positive[local_val], pv))
                                if positive[local_val].any()
                                else 0.0
                            )
                            loss = float(
                                log_loss(
                                    positive[local_val],
                                    np.clip(pv, 1e-8, 1 - 1e-8),
                                    labels=[False, True],
                                )
                            )
                            options.append((-ap, loss, model))
                        neg_ap, loss, model = min(options, key=lambda item: item[:2])
                        score = model.predict_proba(x[local_test])[:, 1]
                        choice = {
                            "validation_AP": -neg_ap,
                            "validation_logloss": loss,
                            "model": str(model),
                        }
                    for scope, mask in [
                        ("all", np.ones(len(test), dtype=bool)),
                        ("singles", counts[local_test] == 1),
                    ]:
                        if not mask.any():
                            continue
                        labels, values = positive[local_test][mask], score[mask]
                        rows.append(
                            {
                                "protocol": protocol,
                                "seed": seed,
                                "features": name,
                                "learner": learner,
                                "subset": scope,
                                "train_n": len(train),
                                "validation_n": len(val),
                                "train_positives": positives,
                                "validation_positives": int(positive[local_val].sum()),
                                "test_n": int(mask.sum()),
                                "prevalence": float(labels.mean()),
                                "P10": precision_at_k(values, labels, 10),
                                "P20": precision_at_k(values, labels, 20),
                                "AP": (
                                    float(average_precision_score(labels, values))
                                    if labels.any()
                                    else None
                                ),
                                "seconds": time.perf_counter() - start,
                            }
                        )
                    choices.append(
                        {
                            "protocol": protocol,
                            "seed": seed,
                            "features": name,
                            "learner": learner,
                            **choice,
                        }
                    )
                    predictions.extend(
                        {
                            "protocol": protocol,
                            "seed": seed,
                            "features": name,
                            "learner": learner,
                            "id": ident,
                            "actual_gain": bool(label),
                            "probability_uncalibrated": float(value),
                        }
                        for ident, label, value in zip(
                            subset.id.to_numpy()[local_test],
                            positive[local_test],
                            score,
                            strict=True,
                        )
                    )
            pd.DataFrame(rows).to_csv(
                OUT / f"gain_classifier_metrics_{tag}.csv", index=False
            )
            pd.DataFrame(predictions).to_csv(
                OUT / f"gain_classifier_predictions_{tag}.csv", index=False
            )
            (OUT / f"gain_classifier_choices_{tag}.json").write_text(
                json.dumps(choices, indent=2) + "\n"
            )
            print(protocol, seed, "completed", flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
