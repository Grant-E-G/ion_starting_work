"""Independent measured four-site GB1 assay: no new-assay label training.

Train on Olson variants that never touch the four Wu sites. Predict measured
triple/quadruple constructs using source-only physical pretraining or ESM35M.
Author I20fit overwrites singles with old Olson values: use I20fitRaw throughout.
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
from metrics import evaluate, precision_at_k
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

SITES = [38, 39, 40, 53]  # zero-based MQY... sequence; author positions39/40/41/54


def prepare() -> pd.DataFrame:
    source = pd.read_csv(RAW / "gb1_wu2016/result/Mutfit", sep="\t")
    source = source[
        source.mut.str.fullmatch("[ACDEFGHIKLMNPQRSTVWY]{4}") & source.I20fitRaw.notna()
    ].copy()
    wt = pd.read_csv(RAW / "gb1_wu2016/result/WTcount", sep="\t").iloc[0]
    reconstructed = (source.IGG20 / wt.IGG20) / (source.Input / wt.Input)
    assert np.allclose(source.I20fitRaw, reconstructed, atol=1e-10)
    assert len(source) == 149361 and source.mut.is_unique
    _old, sequence, offset = load_vep("gb1")
    assert offset == 0 and "".join(sequence[i] for i in SITES) == "VDGV"
    source["id"] = [
        ",".join(
            f"{sequence[p]}{p}{alt}"
            for p, alt in zip(SITES, code, strict=True)
            if sequence[p] != alt
        )
        or "WT"
        for code in source.mut
    ]
    source["target"] = np.log(np.maximum(source.I20fitRaw, 0.01))
    source["measured_gain"] = source.I20fitRaw >= 1.2
    source["readcount_log_SE"] = np.sqrt(
        1 / source.Input + 1 / np.maximum(source.IGG20, 1) + 1 / wt.Input + 1 / wt.IGG20
    )
    source["readcount_supported_gain"] = (
        np.log(np.maximum(source.I20fitRaw, 1e-12)) - 1.96 * source.readcount_log_SE
    ) >= np.log(1.2)
    source["partition"] = np.where(source.HD >= 3, "external_test", "control_only")
    parts = source[["id", "mut", "HD", "partition"]].to_csv(index=False)
    policy = {
        "primary_doi": "10.7554/eLife.16965",
        "raw": "Original authors Mutfit I20fitRaw, input count>=10, canonical AA only; never regression_missing",
        "important_leakage": "I20fit overwrites singles with Olson measurements times1.15868; use independently measured I20fitRaw",
        "WT": "VDGV; raw medium-IgG enrichment relative to WT counts92735input/338346selected",
        "observable": "mRNA-display IgG binding enrichment; not purified affinity, neuronal membrane function or direct energy",
        "test": "Measured Hamming3/4 only; exact zero-based sites38/39/40/53 withheld from all supervised training and validation",
        "training": "1000Olson constructs excluding all four sites;256validation constructs from same eligible old corpus, fixed hash order. No Wu labels used for fitting or model/hyperparameter selection.",
        "selection": "Ridge alpha1/10/100/1000 or ExtraTrees300 leaf2/8 selected by old-label validation MSE; WT-zero anchor; log floor0.01 fixed",
        "benefit": "Raw measured fitness>=1.2WT, P20/P50 and fraction of predicted gains confirmed; secondary compared to known old constituent effects",
        "test_partition_sha256": hashlib.sha256(parts.encode()).hexdigest(),
        "test_n": int((source.HD >= 3).sum()),
        "scope": "New assay and high-order combinations, same protein; not independent protein-family validation. Original Wu display construct differs from model full-length context; alignment verified only at four mutated sites and stated assay scaffold.",
    }
    write_immutable(
        DATA / "gb1_transfer_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    source.to_csv(OUT / "gb1_transfer_measurements.csv", index=False)
    write_immutable(DATA / "gb1_transfer_partitions.csv", parts)
    return source


def features() -> None:
    sys.path.insert(0, str(RAW / "metl"))
    import metl
    from metl_check import CHECKPOINTS
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    frame = prepare()
    _, sequence, _ = load_vep("gb1")
    sequences = [sequence]
    for code in frame.mut:
        chars = list(sequence)
        for p, alt in zip(SITES, code, strict=True):
            chars[p] = alt
        sequences.append("".join(chars))
    for key in ["gb1_binding", "gb1_binding_control", "esm2_35m"]:
        destination = FEATURES / f"gb1_transfer_{key}.npz"
        if destination.exists():
            print("cached", key, flush=True)
            continue
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        if key.startswith("gb1_"):
            model, encoder = metl.get_from_checkpoint(
                str(RAW / "metl/weights" / CHECKPOINTS[key])
            )
            model.eval().to("cuda")
            encoded = encoder.encode_sequences(sequences)
            captured: list[torch.Tensor] = []

            def capture(_module, _inputs, output, captured=captured):
                captured.append(output.detach())

            hook = model.model.avg_pooling.register_forward_hook(capture)
            rows, hidden = [], []
            for i in range(0, len(encoded), 256):
                captured.clear()
                with torch.inference_mode():
                    output = model(
                        torch.tensor(encoded[i : i + 256], device="cuda"),
                        pdb_fn=str(RAW / "metl/pdbs/2qmt_p.pdb"),
                    )
                rows.append(output.cpu().numpy())
                hidden.append(captured[0].cpu().numpy())
            hook.remove()
            values, latent = np.concatenate(rows), np.concatenate(hidden)
            np.savez_compressed(
                destination,
                ids=frame.id.to_numpy(dtype=str),
                attributes_native=values[1:] - values[:1],
                latent_native=latent[1:] - latent[:1],
            )
        else:
            spec = json.loads((DATA / "esm2_35m_model.json").read_text())
            tokenizer = AutoTokenizer.from_pretrained(
                spec["name"], revision=spec["revision"]
            )
            model = (
                AutoModelForMaskedLM.from_pretrained(
                    spec["name"], revision=spec["revision"]
                )
                .eval()
                .to("cuda")
            )
            hidden = []
            for i in range(0, len(sequences), 256):
                batch = tokenizer(
                    sequences[i : i + 256], return_tensors="pt", padding=True
                ).to("cuda")
                with torch.inference_mode():
                    output = (
                        model.esm(**batch)
                        .last_hidden_state[:, 1 : len(sequence) + 1]
                        .mean(1)
                    )
                hidden.append(output.cpu().numpy())
            values = np.concatenate(hidden)
            np.savez_compressed(
                destination,
                ids=frame.id.to_numpy(dtype=str),
                pooled_delta=values[1:] - values[:1],
                native_pooled=values[0],
            )
        torch.cuda.synchronize()
        receipt = {
            "method": key,
            "variants": len(frame),
            "seconds": time.perf_counter() - start,
            "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
            "device": torch.cuda.get_device_name(),
            "precision": "FP32",
            "scope": "Runtime under shared load; setup and serialization included",
        }
        (OUT / f"gb1_transfer_{key}_resources.json").write_text(
            json.dumps(receipt, indent=2) + "\n"
        )
        print(receipt, flush=True)
        del model
        torch.cuda.empty_cache()


def compare() -> None:
    frame = prepare()
    old, _sequence, _ = load_vep("gb1")
    with np.load(FEATURES / "gb1_esm2_35m_mutant_embeddings.npz") as arrays:
        ids = arrays["ids"]
        old = old.set_index("id", drop=False).loc[ids].reset_index(drop=True)
        old_sequence = arrays["pooled"]
    with np.load(FEATURES / "gb1_esm2_35m.npz") as arrays:
        old_sequence -= arrays["wt_hidden"].mean(0)
    eligible = [
        i
        for i, parsed in enumerate(old.parsed)
        if all(position not in SITES for _, position, _ in parsed)
    ]
    training_order = sorted(
        eligible,
        key=lambda i: hashlib.sha256(
            ("gb1-transfer-20261014:" + old.id[i]).encode()
        ).hexdigest(),
    )
    train, val = np.array(training_order[:1000]), np.array(training_order[1000:1256])
    assert len(train) == 1000 and len(val) == 256
    write_immutable(
        DATA / "gb1_transfer_training_partitions.csv",
        pd.DataFrame(
            {
                "id": old.id.iloc[np.r_[train, val]].to_numpy(),
                "split": ["train"] * 1000 + ["validation"] * 256,
            }
        ).to_csv(index=False),
    )
    pca = np.load(RAW / "VEP/data/aaindex/pca-19_norm.npy")

    def chemistry(ident: str) -> np.ndarray:
        delta = np.zeros(20)
        tokens = [] if ident == "WT" else ident.split(",")
        for token in tokens:
            delta[AA.index(token[-1])] += 1
            delta[AA.index(token[0])] -= 1
        # Global AAIndex/identity deltas extrapolate across sites. Site-local
        # onehot coefficients would be untrained at all four external sites.
        return np.r_[delta, delta @ pca, len(tokens)]

    blocks = {
        "chemical_summary": (
            np.stack([chemistry(ident) for ident in old.id]),
            np.stack([chemistry(ident) for ident in frame.id]),
        )
    }
    with np.load(FEATURES / "gb1_transfer_esm2_35m.npz") as arrays:
        assert np.array_equal(arrays["ids"], frame.id)
        blocks["ESM35_actual_delta"] = (old_sequence, arrays["pooled_delta"])
    zero_scores = {}
    for key in ["gb1_binding", "gb1_binding_control"]:
        with np.load(FEATURES / f"gb1_metl_{key}.npz") as arrays:
            index = pd.Index(arrays["ids"]).get_indexer(old.id)
            assert (index >= 0).all()
            source = {
                name: arrays[name][index]
                for name in ["attributes_native", "latent_native"]
            }
        with np.load(FEATURES / f"gb1_transfer_{key}.npz") as arrays:
            assert np.array_equal(arrays["ids"], frame.id)
            indices = (
                {
                    "negative_total_score": 0,
                    "negative_dG_cross": 56,
                    "negative_dG_separated": 58,
                    "negative_dG_separated_per_area": 59,
                }
                if key == "gb1_binding"
                else {"negative_total_score": 0}
            )
            for label, column in indices.items():
                zero_scores[f"{key}_{label}"] = -arrays["attributes_native"][:, column]
            for name, source_values in source.items():
                blocks[f"{key}_{name}"] = (source_values, arrays[name])
                if name == "attributes_native":
                    sequence_old, sequence_new = blocks["ESM35_actual_delta"]
                    blocks[f"ESM35_{key}_attributes"] = (
                        np.column_stack([sequence_old, source_values]),
                        np.column_stack([sequence_new, arrays[name]]),
                    )
    zero_policy = {
        "hypothesis": "Function-matched source-only binding energy should select gains without any experimental readout fitting",
        "scores": list(zero_scores),
        "signs": "Negative normalized energy, fixed from mechanistic direction and previous readout definitions; never selected using newWu labels",
        "units": "Within-one-PDB normalized surrogate outputs, rank only; no kcal, affinity or enrichment calibration",
        "scope": "Independent higher-order assay transfer, same protein; physical pretraining can include related mutants",
    }
    write_immutable(
        DATA / "gb1_transfer_zero_shot_policy.json",
        json.dumps(zero_policy, indent=2) + "\n",
    )
    zero_rows = []
    from scipy.stats import spearmanr
    from sklearn.metrics import average_precision_score

    for label, score in zero_scores.items():
        for order in [3, 4, 0]:
            mask = frame.HD >= 3 if order == 0 else frame.HD == order
            gain = frame.measured_gain.to_numpy()[mask]
            zero_rows.append(
                {
                    "features": label,
                    "order": order,
                    "n": int(mask.sum()),
                    "experimental_training_n": 0,
                    "prevalence": float(gain.mean()),
                    "P20": precision_at_k(score[mask], gain, 20),
                    "P100": precision_at_k(score[mask], gain, 100),
                    "AP": float(average_precision_score(gain, score[mask])),
                    "spearman": float(
                        spearmanr(frame.target.to_numpy()[mask], score[mask]).statistic
                    ),
                    "readcount_supported_gain_P20": precision_at_k(
                        score[mask], frame.readcount_supported_gain.to_numpy()[mask], 20
                    ),
                }
            )
    pd.DataFrame(zero_rows).to_csv(
        OUT / "gb1_transfer_zero_shot_metrics.csv", index=False
    )
    old_y = old.target.to_numpy()
    outputs = {"WT_null": np.zeros(len(frame))}
    choices = []
    for key, (x, new) in blocks.items():
        for learner in ["ridge", "extra"]:
            options = []
            settings = [1, 10, 100, 1000] if learner == "ridge" else [2, 8]
            for setting in settings:
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
                model.fit(x[train], old_y[train])
                zero = model.predict(np.zeros((1, x.shape[1])))[0]
                loss = float(np.mean((model.predict(x[val]) - zero - old_y[val]) ** 2))
                options.append((loss, setting, model, zero))
            loss, setting, model, zero = min(options, key=lambda item: item[0])
            # Refit with development labels after settings chosen, preserving WT.
            model.fit(x[np.r_[train, val]], old_y[np.r_[train, val]])
            outputs[f"{key}_{learner}"] = (
                model.predict(new) - model.predict(np.zeros((1, x.shape[1])))[0]
            )
            choices.append(
                {
                    "features": key,
                    "learner": learner,
                    "old_validation_MSE": loss,
                    "setting": setting,
                }
            )
    # Independent all-single/double empirical control: more existing labels than
    # the1256-label models, explicitly labeled and never mixed into training.
    all_old, _, _ = load_vep("gb1")
    lookup = {
        ",".join(sorted(ident.split(","))): float(value)
        for ident, value in zip(all_old.id, all_old.target, strict=True)
    }
    assert len(lookup) == len(
        all_old
    ), "Canonicalize constructs before treating them as independent"
    single, pairwise, complete = [], [], []
    from itertools import combinations

    for ident in frame.id:
        tokens = [] if ident == "WT" else ident.split(",")
        ok = all(token in lookup for token in tokens)
        additive = sum(lookup.get(token, 0) for token in tokens)
        pair = additive
        for a, b in combinations(tokens, 2):
            joined = ",".join(sorted([a, b]))
            ok &= joined in lookup
            pair += (
                lookup.get(joined, lookup.get(a, 0) + lookup.get(b, 0))
                - lookup.get(a, 0)
                - lookup.get(b, 0)
            )
        single.append(additive)
        pairwise.append(pair)
        complete.append(ok)
    outputs["empirical_all_singles"] = np.array(single)
    outputs["empirical_all_pairs"] = np.array(pairwise)
    rows: list[dict] = []
    predictions: list[dict] = []
    for name, prediction in outputs.items():
        for cohort in ["all_measured", "complete_constituents"]:
            if name.startswith("empirical_") and cohort == "all_measured":
                continue
            for order in [3, 4, 0]:
                mask = (frame.HD >= 3) if order == 0 else frame.HD == order
                if cohort == "complete_constituents":
                    mask &= np.array(complete)
                assert mask.any(), "Empty benchmark cohort is a data/numbering failure"
                y, p = frame.target.to_numpy()[mask], prediction[mask]
                selected = p >= np.log(1.2)
                rows.append(
                    {
                        "features": name,
                        "cohort": cohort,
                        "order": order,
                        "development_labels": (
                            "Existing complete constituents, up to2242labels"
                            if name.startswith("empirical_")
                            else "1256" if name != "WT_null" else "0"
                        ),
                        "P100": precision_at_k(p, y >= np.log(1.2), 100),
                        "readcount_supported_gain_prevalence": float(
                            frame.readcount_supported_gain[mask].mean()
                        ),
                        "readcount_supported_gain_P20": precision_at_k(
                            p, frame.readcount_supported_gain.to_numpy()[mask], 20
                        ),
                        "predicted_gains_n": int(selected.sum()),
                        "predicted_gain_precision": (
                            float((y[selected] >= np.log(1.2)).mean())
                            if selected.any()
                            else None
                        ),
                        **evaluate(y, p, float(np.log(1.2))),
                    }
                )
        predictions.extend(
            {
                "features": name,
                "id": ident,
                "HD": int(hd),
                "actual": float(y),
                "predicted": float(p),
            }
            for ident, hd, y, p in zip(
                frame.id, frame.HD, frame.target, prediction, strict=True
            )
            if hd >= 3
        )
    pd.DataFrame(rows).to_csv(OUT / "gb1_transfer_metrics.csv", index=False)
    pd.DataFrame(predictions).to_csv(OUT / "gb1_transfer_predictions.csv", index=False)
    (OUT / "gb1_transfer_selection.json").write_text(
        json.dumps(choices, indent=2) + "\n"
    )
    print(pd.DataFrame(rows).round(3).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "features", "compare"])
    args = parser.parse_args()
    torch.set_num_threads(2)
    with threadpool_limits(limits=3):
        {"prepare": prepare, "features": features, "compare": compare}[args.mode]()


if __name__ == "__main__":
    main()
