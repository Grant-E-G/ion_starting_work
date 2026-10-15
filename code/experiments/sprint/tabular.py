"""Cheap pooled mutation-feature learners versus neural sequence/physics tests."""

from __future__ import annotations

import argparse
import json
import re
import time

import numpy as np
import pandas as pd
from data import AA, FEATURES, OUT, RAW, SEEDS, load_vep, vep_split
from metrics import evaluate
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from vep import lookups


def aggregate(values: list[np.ndarray]) -> np.ndarray:
    x = np.stack(values)
    return np.concatenate([x.sum(axis=0), x.min(axis=0), x.max(axis=0)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datasets", nargs="+", default=["avgfp", "pab1", "gb1", "ube4b", "bgl3"]
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS)
    parser.add_argument("--train-limit", type=int, default=1000)
    parser.add_argument("--validation-limit", type=int, default=0)
    parser.add_argument("--learners", nargs="+", default=["ridge"])
    parser.add_argument("--tag", default="pooled")
    parser.add_argument("--feature-pattern", default=".*")
    args = parser.parse_args()
    rows: list[dict] = []
    predictions: list[dict] = []
    aaindex = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")
    for name in args.datasets:
        frame, _sequence, offset = load_vep(name)
        lookup, _, _ = lookups(name)
        atoms = sorted({token for v in frame.id for token in v.split(",")})
        atomic: dict[str, dict[str, np.ndarray]] = {key: {} for key in lookup}
        cheap: dict[str, np.ndarray] = {}
        context: dict[str, dict[str, np.ndarray]] = {}
        sequence_models = {}
        for model_name in ["esm2_35m", "esm1v_650m"]:
            path = FEATURES / f"{name}_{model_name}.npz"
            if path.exists():
                with np.load(path) as file:
                    sequence_models[model_name] = {
                        key: file[key] for key in ["wt_hidden", "aa_embedding"]
                    }
                context[model_name] = {}
        identity = np.eye(20)
        for token in atoms:
            pos, wt, mt = (
                int(token[1:-1]) - offset,
                AA.index(token[0]),
                AA.index(token[-1]),
            )
            cheap[token] = np.concatenate(
                [aaindex[mt] - aaindex[wt], identity[mt], identity[wt]]
            )
            for key in lookup:
                atomic[key][token] = lookup[key][pos, mt]
            for key, arrays in sequence_models.items():
                hidden, embedding = arrays["wt_hidden"], arrays["aa_embedding"]
                delta = embedding[mt] - embedding[wt]
                context[key][token] = np.concatenate(
                    [hidden[pos], delta, hidden[pos] * delta]
                )
        for protocol in ["site", "mutation"]:
            for seed in args.seeds:
                split = vep_split(frame, name, protocol, seed, offset)
                indices = {
                    part: np.flatnonzero(split == part)
                    for part in ["train", "validation", "test"]
                }
                if args.train_limit:
                    indices["train"] = np.random.RandomState(seed).permutation(
                        indices["train"]
                    )[: args.train_limit]
                if args.validation_limit:
                    indices["validation"] = np.random.RandomState(
                        seed + 314
                    ).permutation(indices["validation"])[: args.validation_limit]
                selected = np.concatenate(list(indices.values()))
                subset = frame.iloc[selected]
                train = np.arange(len(indices["train"]))
                validation = np.arange(
                    len(train), len(train) + len(indices["validation"])
                )
                test = np.arange(len(train) + len(validation), len(selected))
                tokens = [v.split(",") for v in subset.id]
                count = subset.num_mutations.to_numpy()[:, None]
                base = np.column_stack(
                    [
                        count,
                        np.array([aggregate([cheap[t] for t in ts]) for ts in tokens]),
                    ]
                )
                arrays = {"count": count, "cheap": base}
                for key in [
                    "rosetta",
                    "rosetta_shuffled",
                    "rosetta_site_mean",
                    "evoef",
                    "evoef_matched",
                ]:
                    if key in atomic:
                        pooled = np.array(
                            [aggregate([atomic[key][t] for t in ts]) for ts in tokens]
                        )
                        arrays[f"cheap_{key}"] = np.column_stack([base, pooled])
                for key in context:
                    llr = np.array(
                        [aggregate([atomic[key][t] for t in ts]) for ts in tokens]
                    )
                    contextual = np.array(
                        [
                            np.stack([context[key][t] for t in ts]).sum(axis=0)
                            for ts in tokens
                        ]
                    )
                    arrays[f"{key}_llr"] = llr
                    arrays[f"{key}_sequence"] = np.column_stack([base, llr, contextual])
                    for energy in ["rosetta", "evoef_matched"]:
                        if energy in atomic:
                            pooled = np.array(
                                [
                                    aggregate([atomic[energy][t] for t in ts])
                                    for ts in tokens
                                ]
                            )
                            arrays[f"{key}_sequence_{energy}"] = np.column_stack(
                                [arrays[f"{key}_sequence"], pooled]
                            )
                for model_name in ["esm2_35m", "esm1v_650m"]:
                    path = FEATURES / f"{name}_{model_name}_mutant_embeddings.npz"
                    if not path.exists():
                        continue
                    with np.load(path) as file:
                        order = pd.Index(file["ids"]).get_indexer(subset.id)
                        assert (order >= 0).all()
                        embedding = np.column_stack(
                            [file["pooled"][order], file["mutated_sites"][order]]
                        )
                    arrays[f"{model_name}_mutant"] = np.column_stack([base, embedding])
                    for energy in ["rosetta", "evoef_matched"]:
                        if energy in atomic:
                            pooled = np.array(
                                [
                                    aggregate([atomic[energy][t] for t in ts])
                                    for ts in tokens
                                ]
                            )
                            arrays[f"{model_name}_mutant_{energy}"] = np.column_stack(
                                [arrays[f"{model_name}_mutant"], pooled]
                            )
                for family in [
                    f"{name}_local",
                    "global1d",
                    "global3d",
                    "gb1_binding",
                    "gb1_binding_control",
                ]:
                    path = FEATURES / f"{name}_metl_{family}.npz"
                    if not path.exists():
                        continue
                    with np.load(path) as file:
                        order = pd.Index(file["ids"]).get_indexer(subset.id)
                        assert (order >= 0).all()
                        for block in ["attributes_native", "latent_native"]:
                            values = file[block][order]
                            arrays[f"metl_{family}_{block}"] = np.column_stack(
                                [base, values]
                            )
                            key = "esm1v_650m_sequence"
                            if key in arrays:
                                arrays[f"{key}_metl_{family}_{block}"] = (
                                    np.column_stack([arrays[key], values])
                                )
                y = subset.target.to_numpy()
                threshold = (
                    0.1 if name == "avgfp" else float(np.quantile(y[train], 0.9))
                )
                for features, x in arrays.items():
                    if re.fullmatch(args.feature_pattern, features) is None:
                        continue
                    for learner in args.learners:
                        start = time.perf_counter()
                        if learner == "ridge":
                            candidates = [
                                make_pipeline(StandardScaler(), Ridge(alpha=alpha))
                                for alpha in [1, 10, 100, 1000]
                            ]
                        elif learner == "extra":
                            if x.shape[1] > 500:
                                continue
                            candidates = [
                                ExtraTreesRegressor(
                                    n_estimators=300,
                                    min_samples_leaf=leaf,
                                    random_state=seed,
                                    n_jobs=3,
                                )
                                for leaf in [1, 3]
                            ]
                        else:
                            raise ValueError(learner)
                        loss, model = min(
                            (
                                (
                                    float(
                                        np.mean(
                                            (
                                                m.fit(x[train], y[train]).predict(
                                                    x[validation]
                                                )
                                                - y[validation]
                                            )
                                            ** 2
                                        )
                                    ),
                                    m,
                                )
                                for m in candidates
                            ),
                            key=lambda item: item[0],
                        )
                        p = model.predict(x[test])
                        for subset_name, mask in [
                            ("all", np.ones(len(test), dtype=bool)),
                            ("singles", subset.num_mutations.to_numpy()[test] == 1),
                            (
                                "near_WT",
                                (
                                    y[test] >= -0.2
                                    if name == "avgfp"
                                    else np.ones(len(test), dtype=bool)
                                ),
                            ),
                        ]:
                            if not mask.any():
                                continue
                            rows.append(
                                {
                                    "dataset": name,
                                    "protocol": protocol,
                                    "seed": seed,
                                    "features": features,
                                    "learner": learner,
                                    "subset": subset_name,
                                    "train_n": len(train),
                                    "validation_n": len(validation),
                                    "validation_mse": loss,
                                    "threshold": threshold,
                                    "seconds": time.perf_counter() - start,
                                    **evaluate(y[test][mask], p[mask], threshold),
                                }
                            )
                        predictions.extend(
                            {
                                "dataset": name,
                                "protocol": protocol,
                                "seed": seed,
                                "features": features,
                                "learner": learner,
                                "id": ident,
                                "actual": actual,
                                "predicted": pr,
                            }
                            for ident, actual, pr in zip(
                                subset.id.to_numpy()[test], y[test], p, strict=True
                            )
                        )
                # Preserve completed comparisons if a later case fails.
                pd.DataFrame(rows).to_csv(
                    OUT / f"tabular_metrics_{args.tag}.csv", index=False
                )
                pd.DataFrame(predictions).to_csv(
                    OUT / f"tabular_predictions_{args.tag}.csv", index=False
                )
                print(name, protocol, seed, "completed", len(arrays), flush=True)
    (OUT / f"tabular_settings_{args.tag}.json").write_text(
        json.dumps(vars(args), indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
