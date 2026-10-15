"""Discriminate missing-site calibration from failed physical extrapolation.

All existing Olson single/double mutants at the four Wu sites are development
labels; independently measured Wu triples/quadruples remain prediction-only.
Compare physical transfer with additive, pairwise and Hamming-kernel controls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time

import numpy as np
import pandas as pd
import torch
from data import AA, DATA, FEATURES, OUT, RAW, load_vep, write_immutable
from gb1_transfer import SITES, prepare
from metrics import evaluate, precision_at_k
from scipy.linalg import cho_factor, cho_solve
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def components() -> tuple[pd.DataFrame, str]:
    frame, sequence, _ = load_vep("gb1")
    frame = frame[
        [all(p in SITES for _, p, _ in parsed) for parsed in frame.parsed]
    ].reset_index(drop=True)
    assert len(frame) == 2242
    codes = []
    for parsed in frame.parsed:
        chars = [sequence[p] for p in SITES]
        for _, p, alt in parsed:
            chars[SITES.index(p)] = alt
        codes.append("".join(chars))
    frame["mut"] = codes
    double = sorted(
        frame.index[frame.num_mutations == 2],
        key=lambda i: hashlib.sha256(
            ("GB1-components:" + frame.id[i]).encode()
        ).hexdigest(),
    )
    frame["split"] = "train"
    frame.loc[double[: len(double) // 5], "split"] = "validation"
    partition = frame[["id", "mut", "split"]].to_csv(index=False)
    policy = {
        "hypothesis": "Earlier extrapolation withheld all four mutation sites. Calibrating function on existing component singles/doubles may allow physical readouts to predict higher-order interactions; must beat empirical/additive/pairwise/kernel controls",
        "data": "All2242existingOlsonsingle/doubleconstructs atfour sites; no Wu function label used in fit/selection",
        "partition_sha256": hashlib.sha256(partition.encode()).hexdigest(),
        "validation": "Label-blind hash20%old doubles; all76singles training; settings chosen only using oldvalidationMSE, then refitall2242",
        "test": "Previously frozen147193measuredWuI20fitRawtriple/quadruples, noimputed scores",
        "models": "WT-zero anchoredRidgealpha1/10/100/1000; ExtraTrees300leaf2/8 whenfeatures<=500; Hammingexpkernelbeta.25/.5/1/2 andRidgealpha.01/.1/1/10",
        "controls": "Siteonehotadditive; pairwiseonehot; kernel has no physical terms; measured oldsingle/pairexpansions preserved separately",
        "scope": "Exploratory followup after inspecting zero-site-calibration transfer failure; not an additional blind test or free-label prospective result. Uses2242existingexperimental labels.",
    }
    write_immutable(
        DATA / "gb1_components_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    write_immutable(DATA / "gb1_components_partitions.csv", partition)
    return frame, sequence


def features() -> None:
    sys.path.insert(0, str(RAW / "metl"))
    import metl
    from metl_check import CHECKPOINTS
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    frame, sequence = components()
    sequences = [sequence]
    for parsed in frame.parsed:
        chars = list(sequence)
        for _, p, alt in parsed:
            chars[p] = alt
        sequences.append("".join(chars))
    for key in ["gb1_binding", "gb1_binding_control", "esm2_35m"]:
        path = FEATURES / f"gb1_components_{key}.npz"
        if path.exists():
            continue
        start = time.perf_counter()
        torch.cuda.reset_peak_memory_stats()
        if key.startswith("gb1"):
            model, encoder = metl.get_from_checkpoint(
                str(RAW / "metl/weights" / CHECKPOINTS[key])
            )
            model.eval().to("cuda")
            encoded = encoder.encode_sequences(sequences)
            captured: list[torch.Tensor] = []

            def capture(_module, _inputs, output, captured=captured):
                captured.append(output.detach())

            hook = model.model.avg_pooling.register_forward_hook(capture)
            attributes = []
            latent = []
            for i in range(0, len(encoded), 256):
                captured.clear()
                with torch.inference_mode():
                    output = model(
                        torch.tensor(encoded[i : i + 256], device="cuda"),
                        pdb_fn=str(RAW / "metl/pdbs/2qmt_p.pdb"),
                    )
                attributes.append(output.cpu().numpy())
                latent.append(captured[0].cpu().numpy())
            hook.remove()
            a, h = np.concatenate(attributes), np.concatenate(latent)
            np.savez_compressed(
                path,
                ids=frame.id.to_numpy(dtype=str),
                attributes=a[1:] - a[:1],
                latent=h[1:] - h[:1],
            )
        else:
            meta = json.loads((DATA / "esm2_35m_model.json").read_text())
            tokenizer = AutoTokenizer.from_pretrained(
                meta["name"], revision=meta["revision"]
            )
            model = (
                AutoModelForMaskedLM.from_pretrained(
                    meta["name"], revision=meta["revision"]
                )
                .eval()
                .to("cuda")
            )
            rows = []
            for i in range(0, len(sequences), 256):
                batch = tokenizer(sequences[i : i + 256], return_tensors="pt").to(
                    "cuda"
                )
                with torch.inference_mode():
                    output = (
                        model.esm(**batch)
                        .last_hidden_state[:, 1 : len(sequence) + 1]
                        .mean(1)
                    )
                rows.append(output.cpu().numpy())
            a = np.concatenate(rows)
            np.savez_compressed(
                path, ids=frame.id.to_numpy(dtype=str), pooled_delta=a[1:] - a[:1]
            )
        torch.cuda.synchronize()
        receipt = {
            "method": key,
            "variants": len(frame),
            "seconds": time.perf_counter() - start,
            "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
            "precision": "FP32",
        }
        (OUT / f"gb1_components_{key}_resources.json").write_text(
            json.dumps(receipt, indent=2) + "\n"
        )
        print(receipt, flush=True)
        del model
        torch.cuda.empty_cache()


def codes(frame: pd.DataFrame) -> np.ndarray:
    return np.array(
        [[AA.index(alt) for alt in code] for code in frame.mut], dtype=np.int8
    )


def sequence_features(code: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    identity = np.eye(20, dtype=np.float32)
    native = np.array([AA.index(a) for a in "VDGV"])
    onehot = identity[code] - identity[native]
    pairs = []
    for i in range(4):
        for j in range(i + 1, 4):
            pairs.append(
                (onehot[:, i, :, None] * onehot[:, j, None, :]).reshape(len(code), 400)
            )
    return onehot.reshape(len(code), 80), np.column_stack(
        [onehot.reshape(len(code), 80), *pairs]
    )


def compare() -> None:
    old, _ = components()
    test = prepare()
    test = test[test.HD >= 3].reset_index(drop=True)
    first, second = codes(old), codes(test)
    additive, pairwise = sequence_features(first)
    native = np.array([AA.index(a) for a in "VDGV"])
    identity = np.eye(20, dtype=np.float32)
    new_additive = (identity[second] - identity[native]).reshape(len(second), 80)
    blocks: dict[str, tuple[np.ndarray, np.ndarray | None]] = {
        "site_additive": (additive, new_additive),
        "site_pairwise": (pairwise, None),
    }
    for key in ["esm2_35m", "gb1_binding", "gb1_binding_control"]:
        with np.load(FEATURES / f"gb1_components_{key}.npz") as source, np.load(
            FEATURES / f"gb1_transfer_{key}.npz"
        ) as external:
            assert np.array_equal(source["ids"], old.id)
            index = pd.Index(external["ids"]).get_indexer(test.id)
            assert (index >= 0).all()
            if key == "esm2_35m":
                blocks["ESM35"] = (
                    source["pooled_delta"],
                    external["pooled_delta"][index],
                )
            else:
                for column, new_column in [
                    ("attributes", "attributes_native"),
                    ("latent", "latent_native"),
                ]:
                    a, b = source[column], external[new_column][index]
                    blocks[f"{key}_{column}"] = (a, b)
                    if column == "attributes":
                        blocks[f"ESM35_{key}"] = (
                            np.column_stack([blocks["ESM35"][0], a]),
                            np.column_stack([blocks["ESM35"][1], b]),
                        )
    train = np.flatnonzero(old.split.to_numpy() == "train")
    val = np.flatnonzero(old.split.to_numpy() == "validation")
    y = old.target.to_numpy()
    outputs = {}
    choices = []
    for name, (x, new) in blocks.items():
        for learner in (["ridge", "extra"] if x.shape[1] <= 500 else ["ridge"]):
            options = []
            for setting in ([1, 10, 100, 1000] if learner == "ridge" else [2, 8]):
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
                zero = model.predict(np.zeros((1, x.shape[1])))[0]
                loss = float(np.mean((model.predict(x[val]) - zero - y[val]) ** 2))
                options.append((loss, setting, model))
            loss, setting, model = min(options, key=lambda item: item[0])
            model.fit(x, y)
            prediction = (
                model.predict(new)
                if new is not None
                else np.concatenate(
                    [
                        model.predict(sequence_features(second[i : i + 512])[1])
                        for i in range(0, len(second), 512)
                    ]
                )
            )
            outputs[f"{name}_{learner}"] = (
                prediction - model.predict(np.zeros((1, x.shape[1])))[0]
            )
            choices.append(
                {
                    "features": name,
                    "learner": learner,
                    "validation_MSE": loss,
                    "setting": setting,
                }
            )
    # Bounded full kernel, streamed external prediction; no147kx2242allocation.
    distance = (first[:, None, :] != first[None, :, :]).sum(2)
    native = np.array([AA.index(a) for a in "VDGV"])
    distance_wt = (first != native).sum(1)
    candidates = []
    for beta in [0.25, 0.5, 1, 2]:
        kernel = np.exp(-beta * distance)
        for alpha in [0.01, 0.1, 1, 10]:
            coefficients = cho_solve(
                cho_factor(kernel[np.ix_(train, train)] + alpha * np.eye(len(train))),
                y[train],
            )
            zero = np.exp(-beta * distance_wt[train]) @ coefficients
            loss = float(
                np.mean(
                    (kernel[np.ix_(val, train)] @ coefficients - zero - y[val]) ** 2
                )
            )
            candidates.append((loss, beta, alpha))
    loss, beta, alpha = min(candidates)
    kernel = np.exp(-beta * distance)
    coefficients = cho_solve(cho_factor(kernel + alpha * np.eye(len(y))), y)
    zero = np.exp(-beta * distance_wt) @ coefficients
    prediction = []
    for i in range(0, len(second), 512):
        prediction.append(
            np.exp(-beta * (second[i : i + 512, None, :] != first[None, :, :]).sum(2))
            @ coefficients
            - zero
        )
    outputs["Hamming_kernel_ridge"] = np.concatenate(prediction)
    choices.append(
        {
            "features": "Hamming_kernel",
            "validation_MSE": loss,
            "beta": beta,
            "alpha": alpha,
        }
    )
    rows: list[dict] = []
    predictions: list[dict] = []
    raw = prepare()
    single = raw[raw.HD == 1].set_index("id").I20fitRaw.to_dict()
    best = np.array(
        [max([1] + [single[token] for token in ident.split(",")]) for ident in test.id]
    )
    beyond = test.I20fitRaw.to_numpy() >= 1.2 * best
    rescue = np.array(
        [all(single[token] <= 1 for token in ident.split(",")) for ident in test.id]
    )
    for name, prediction in outputs.items():
        for order in [3, 4, 0]:
            mask = test.HD.to_numpy() == order if order else np.ones(len(test), bool)
            rows.append(
                {
                    "features": name,
                    "order": order,
                    "development_labels": len(old),
                    "beyond_parent_P20": precision_at_k(
                        prediction[mask], beyond[mask], 20
                    ),
                    "beyond_parent_increment_P20": precision_at_k(
                        prediction[mask] - np.log(best[mask]), beyond[mask], 20
                    ),
                    "rescue_P20": precision_at_k(
                        prediction[mask & rescue],
                        test.I20fitRaw.to_numpy()[mask & rescue] >= 1.2,
                        20,
                    ),
                    "readcount_supported_gain_P20": precision_at_k(
                        prediction[mask],
                        test.readcount_supported_gain.to_numpy()[mask],
                        20,
                    ),
                    **evaluate(
                        test.target.to_numpy()[mask],
                        prediction[mask],
                        float(np.log(1.2)),
                    ),
                }
            )
        predictions.extend(
            {
                "features": name,
                "id": ident,
                "predicted": float(p),
                "actual": float(a),
                "HD": int(hd),
            }
            for ident, p, a, hd in zip(
                test.id, prediction, test.target, test.HD, strict=True
            )
        )
    pd.DataFrame(rows).to_csv(OUT / "gb1_components_metrics.csv", index=False)
    pd.DataFrame(predictions).to_csv(
        OUT / "gb1_components_predictions.csv", index=False
    )
    (OUT / "gb1_components_choices.json").write_text(
        json.dumps(choices, indent=2) + "\n"
    )
    print(pd.DataFrame(rows).query("order==0").round(3).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["features", "compare"])
    args = parser.parse_args()
    torch.set_num_threads(2)
    with threadpool_limits(limits=3):
        {"features": features, "compare": compare}[args.mode]()


if __name__ == "__main__":
    main()
