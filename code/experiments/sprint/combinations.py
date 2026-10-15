"""Can physical pretraining improve design beyond measured single mutations?

GB1: train/validate only on singles; test new double variants whose constituents
were measured in training. Compare empirical additivity with pretrained-feature
epistasis corrections. No double-mutant function labels tune any predictor.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time

import numpy as np
import pandas as pd
import torch
from data import DATA, FEATURES, OUT, RAW, load_vep, write_immutable
from metrics import evaluate, precision_at_k
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(RAW / "metl"))
import metl


def main() -> None:
    assert torch.cuda.is_available()
    torch.set_num_threads(3)
    frame, sequence, _ = load_vep("gb1")
    singles = frame[frame.num_mutations == 1]
    rng = np.random.RandomState(1729)
    order = rng.permutation(len(singles))
    train = singles.iloc[order[: int(0.9 * len(order))]]
    validation = singles.iloc[order[int(0.9 * len(order)) :]]
    measured = train.set_index("id").target.to_dict()
    doubles = frame[frame.num_mutations == 2]
    eligible = doubles[
        doubles.id.map(lambda v: all(t in measured for t in v.split(",")))
    ]
    selected = eligible.iloc[
        np.random.RandomState(2718).permutation(len(eligible))[:50000]
    ].copy()
    partition = {
        "train_singles": train.id.tolist(),
        "validation_singles": validation.id.tolist(),
        "test_doubles": selected.id.tolist(),
    }
    text = json.dumps(partition, sort_keys=True)
    policy = {
        "training": "90% of measured GB1 single variants only; remaining singles for validation",
        "test": "Label-blind deterministic50000 eligible double variants; both component single labels must be in training",
        "partition_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "train_n": len(train),
        "validation_n": len(validation),
        "test_n": len(selected),
        "WT_gain": "Double enrichment >=1.2*WT",
        "beyond_parent_gain": "Double enrichment >=1.2*max(WT,best measured constituent)",
        "correction": "Measured single additive sum + f(phi_AB)-f(phi_A)-f(phi_B)+f(phi_WT); coefficients/hyperparameters fit/selected using singles only",
        "scope": "Existing public binding-enrichment data; retrospective combinations, not prospective membrane engineering; no double labels for tuning",
    }
    write_immutable(
        DATA / "combination_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    (OUT / "combination_partitions.json").write_text(text + "\n")
    test_ids = selected.id.tolist()
    parent_values = np.array([[measured[t] for t in v.split(",")] for v in test_ids])
    additive = parent_values.sum(1)
    best_parent = np.maximum(parent_values.max(1), 0)
    actual = selected.target.to_numpy()
    threshold = float(np.log(1.2))
    beyond = actual >= best_parent + threshold
    both_bad = (parent_values < 0).all(axis=1)
    clipping: np.ndarray = np.asarray(
        np.quantile(train.target.to_numpy(), [0.01, 0.99])
    )
    predictions = {
        "WT_null": np.zeros(len(selected)),
        "empirical_additive": additive,
        "additive_clipped": np.clip(additive, clipping[0], clipping[1]),
    }
    source_ids = ["_wt"] + list(singles.id) + test_ids
    candidates = [
        ("binding", "METL-BIND-2M-3D-GB1-BINDING-Bo5wn2SG.pt"),
        ("stability", "METL-BIND-2M-3D-GB1-STANDARD-K6mw24Rg.pt"),
    ]
    resources = []
    for family, checkpoint in candidates:
        destination = FEATURES / f"gb1_combinations_metl_{family}.npz"
        if destination.exists():
            with np.load(destination) as file:
                assert file["ids"].tolist() == source_ids
                phi = file["attributes"]
        else:
            model, encoder = metl.get_from_checkpoint(
                str(RAW / "metl/weights" / checkpoint)
            )
            model.to("cuda").eval()
            encoded = encoder.encode_variants(sequence, source_ids)
            values = []
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
            start = time.perf_counter()
            for i in range(0, len(encoded), 128):
                with torch.inference_mode():
                    output = model(
                        torch.tensor(encoded[i : i + 128], device="cuda"),
                        pdb_fn=str(RAW / "metl/pdbs/2qmt_p.pdb"),
                    )
                values.append(output.cpu().numpy())
                if i % 12800 == 0:
                    print(family, i, len(encoded), flush=True)
            torch.cuda.synchronize()
            phi = np.concatenate(values)
            phi -= phi[:1].copy()
            np.savez_compressed(destination, ids=np.array(source_ids), attributes=phi)
            resources.append(
                {
                    "family": family,
                    "constructs": len(encoded),
                    "seconds": time.perf_counter() - start,
                    "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
                }
            )
            del model
            torch.cuda.empty_cache()
        lookup = {ident: i for i, ident in enumerate(source_ids)}
        fit_indices = np.array([lookup[v] for v in train.id])
        validation_indices = np.array([lookup[v] for v in validation.id])
        double_indices = np.array([lookup[v] for v in test_ids])
        first = np.array([lookup[v.split(",")[0]] for v in test_ids])
        second = np.array([lookup[v.split(",")[1]] for v in test_ids])
        models = [
            make_pipeline(StandardScaler(), Ridge(alpha=alpha))
            for alpha in [0.1, 1, 10, 100]
        ]
        _, fitted = min(
            (
                (
                    float(
                        np.mean(
                            (
                                model.fit(phi[fit_indices], train.target).predict(
                                    phi[validation_indices]
                                )
                                - validation.target
                            )
                            ** 2
                        )
                    ),
                    model,
                )
                for model in models
            ),
            key=lambda item: item[0],
        )
        direct = fitted.predict(phi[double_indices])
        correction = (
            direct
            - fitted.predict(phi[first])
            - fitted.predict(phi[second])
            + fitted.predict(phi[:1])[0]
        )
        predictions[f"{family}_direct"] = direct
        predictions[f"{family}_anchored_correction"] = additive + correction
    rows = []
    for name, prediction in predictions.items():
        metrics = evaluate(actual, prediction, threshold)
        margin = prediction - best_parent
        rows.append(
            {
                "method": name,
                "n": len(selected),
                "WT_gain_prevalence": float((actual >= threshold).mean()),
                "beyond_parent_prevalence": float(beyond.mean()),
                "beyond_parent_P20": precision_at_k(margin, beyond, 20),
                "beyond_parent_P100": precision_at_k(margin, beyond, 100),
                "rescue_P20": precision_at_k(
                    prediction[both_bad], (actual[both_bad] >= threshold), 20
                ),
                "rescue_candidates": int(both_bad.sum()),
                "rescue_prevalence": float((actual[both_bad] >= threshold).mean()),
                **metrics,
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "combination_metrics.csv", index=False)
    table = pd.DataFrame(
        {
            "id": test_ids,
            "actual": actual,
            "parent1": parent_values[:, 0],
            "parent2": parent_values[:, 1],
            **predictions,
        }
    )
    table.to_csv(OUT / "combination_predictions.csv", index=False)
    (OUT / "combination_resources.json").write_text(
        json.dumps(resources, indent=2) + "\n"
    )
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    with threadpool_limits(limits=3):
        main()
