"""Neuronal proxy/tradeoff test of physical source pretraining, no new labels.

Reuse the previous audited Kir2.1 measurements and frozen site/region partitions.
WT AF model is prospective-designer-accessible; no mutant experimental structures.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import time

import numpy as np
import pandas as pd
import torch
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from data import DATA, FEATURES, OUT, RAW, ROOT, write_immutable
from metrics import precision_at_k
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


def original():
    spec = importlib.util.spec_from_file_location(
        "audited_kir_data", ROOT / "code/experiments/predictive/data.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare() -> tuple[pd.DataFrame, str]:
    source = original()
    both, audit = source.load_kir()
    _, sequence = source.kir_reference()
    a = both[(both.dataset == "kir_function") & ~both.control].rename(
        columns={"score": "function", "se": "function_se"}
    )
    b = both[(both.dataset == "kir_surface") & ~both.control].rename(
        columns={"score": "surface", "se": "surface_se"}
    )
    frame = a[["id", "position", "wt", "alt", "function", "function_se"]].merge(
        b[["id", "surface", "surface_se"]], on="id", validate="one_to_one"
    )
    native = PDBParser(QUIET=True).get_structure("WT", RAW / "kir_af.pdb")[0]["A"]
    residues = [r for r in native if r.id[0] == " "]
    assert "".join(seq1(r.resname) for r in residues) == sequence
    frame["gain"] = frame.function > 0.3
    frame["joint_gain"] = frame.gain & (frame.surface >= -0.3)
    frame["supported_joint_gain"] = (
        frame.function - 1.96 * frame.function_se > 0.3
    ) & (frame.surface - 1.96 * frame.surface_se >= -0.3)
    parts = ROOT / "sources/predictive/partitions.csv"
    policy = {
        "hypothesis": "Physical source-pretrained packing descriptors should improve function-gain selection while retaining trafficking beyond larger actual-mutant sequence models",
        "labels": "Existing audited Coyote-Maestas2022 pairedmouseKir2.1 function/surface Enrich2 proxies; same-AAreference medians; not intrinsic conductance/current",
        "training": "Existing public labels only; all budget variants share frozen test partitions. Full development or train1000+val256 label-blind prefixes seed1729. No new biological data",
        "partition_sha256": hashlib.sha256(parts.read_bytes()).hexdigest(),
        "source_label_audit": audit,
        "function_gain": ">.3 relative assay-score margin, not percentage current",
        "surface_constraint": ">=-.3 relative score; secondary both lower score-1.96SEbounds satisfy. Approximate filters, not joint/multiplicity-adjusted biological confidence",
        "WT_structure": "AF-P35561-F1-model_v6 monomer, exactnative428AA, no experimental mutant structure; no membrane, lipids, tetramer or explicit open/closed energy",
        "construct": "Experimental FLAG insertion removed for native modeling; constanttag effects/interactions unmodeled",
        "models": "Frozen source-only globalMETL1D/3D physical checkpoints; ESM35/650 actual-mutant-minusWT mean embeddings; train-onlyRidgealpha1/10/100/1000 or ExtraTrees300leaf2/8; validationMSEsum of two standardized endpoint errors",
        "physics_controls": "WT predicted-confidence/contactdensity/radialdepth plus chemistry; within-site shuffled3Dphysicalattributes seed1729; concatenations with actual650sequence",
        "rankings": "Function-only; joint score=min((predfunc-.3)/valresidualSDfunc,(predsurface+.3)/valresidualSDsurface)",
        "status": "New model family on previously inspected Kir benchmark, exploratory; no target/assay/panel selected",
    }
    write_immutable(
        DATA / "kir_transfer_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    frame.to_csv(OUT / "kir_transfer_measurements.csv", index=False)
    return frame, sequence


def features() -> None:
    sys.path.insert(0, str(RAW / "metl"))
    import metl
    from metl_check import CHECKPOINTS
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    frame, sequence = prepare()
    sequences = [sequence]
    for row in frame.itertuples():
        assert sequence[row.position - 1] == row.wt
        sequences.append(
            sequence[: row.position - 1] + row.alt + sequence[row.position :]
        )
    for key in ["global1d", "global3d", "esm2_35m", "esm1v_650m"]:
        path = FEATURES / f"kir_transfer_{key}.npz"
        if path.exists():
            continue
        torch.cuda.reset_peak_memory_stats()
        start = time.perf_counter()
        if key.startswith("global"):
            model, encoder = metl.get_from_checkpoint(
                str(RAW / "metl/weights" / CHECKPOINTS[key])
            )
            model.eval().to("cuda")
            encoded = encoder.encode_sequences(sequences)
            captured: list[torch.Tensor] = []

            def capture(_module, _inputs, output, captured=captured):
                captured.append(output.detach())

            hook = model.model.avg_pooling.register_forward_hook(capture)
            outputs = []
            hidden = []
            for i in range(0, len(encoded), 16):
                captured.clear()
                with torch.inference_mode():
                    batch = torch.tensor(encoded[i : i + 16], device="cuda")
                    prediction = (
                        model(batch, pdb_fn=str(RAW / "kir_af.pdb"))
                        if key == "global3d"
                        else model(batch)
                    )
                outputs.append(prediction.cpu().numpy())
                hidden.append(captured[0].cpu().numpy())
            hook.remove()
            values = np.concatenate(outputs)
            latent = np.concatenate(hidden)
            np.savez_compressed(
                path,
                ids=frame.id.to_numpy(dtype=str),
                attributes=values[1:] - values[:1],
                latent=latent[1:] - latent[:1],
            )
        else:
            meta = json.loads((DATA / f"{key}_model.json").read_text())
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
            outputs = []
            for i in range(0, len(sequences), 8):
                batch = tokenizer(
                    sequences[i : i + 8], return_tensors="pt", padding=True
                ).to("cuda")
                with torch.inference_mode(), torch.autocast(
                    "cuda", dtype=torch.float16, enabled=key == "esm1v_650m"
                ):
                    hidden = (
                        model.esm(**batch)
                        .last_hidden_state[:, 1 : len(sequence) + 1]
                        .float()
                        .mean(1)
                    )
                outputs.append(hidden.cpu().numpy())
            values = np.concatenate(outputs)
            np.savez_compressed(
                path,
                ids=frame.id.to_numpy(dtype=str),
                pooled_delta=values[1:] - values[:1],
            )
        torch.cuda.synchronize()
        result = {
            "method": key,
            "variants": len(frame),
            "seconds": time.perf_counter() - start,
            "peak_allocated_MiB": torch.cuda.max_memory_allocated() / 2**20,
            "precision": "FP32weights/FP16autocast" if key == "esm1v_650m" else "FP32",
            "device": torch.cuda.get_device_name(),
            "scope": "Shared local load, setup andserializationincluded; no training",
        }
        (OUT / f"kir_transfer_{key}_resources.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(result, flush=True)
        del model
        torch.cuda.empty_cache()


def feature_blocks(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    native = PDBParser(QUIET=True).get_structure("WT", RAW / "kir_af.pdb")[0]["A"]
    residues = list(native)
    xyz = np.array([r["CA"].coord for r in residues])
    distance = np.linalg.norm(xyz[:, None] - xyz[None], axis=-1)
    geometry = np.column_stack(
        [
            np.array([r["CA"].bfactor for r in residues]),
            (distance < 8).sum(1) - 1,
            np.linalg.norm(xyz - xyz.mean(0), axis=1),
        ]
    )
    with np.load(ROOT / "sources/predictive/features/kir.npz") as old:
        order = pd.Index(old["ids"]).get_indexer(frame.id)
        assert (order >= 0).all()
        cheap = np.column_stack([old["properties"][order], old["conservation"][order]])
    # Explicitly separate same-method structural information from inherited
    # homolog-based geometry; all new structure-derived features share AF WT.
    shape = geometry[frame.position.to_numpy() - 1]
    base = np.column_stack([cheap, shape])
    blocks = {"chemistry_conservation": cheap, "WTgeometry_chemistry": base}
    for key in ["esm2_35m", "esm1v_650m", "global1d", "global3d"]:
        with np.load(FEATURES / f"kir_transfer_{key}.npz") as arrays:
            assert np.array_equal(arrays["ids"], frame.id)
            if key.startswith("esm"):
                blocks[key] = np.column_stack([base, arrays["pooled_delta"]])
            else:
                blocks[f"{key}_attributes"] = np.column_stack(
                    [base, arrays["attributes"]]
                )
                blocks[f"{key}_latent"] = np.column_stack([base, arrays["latent"]])
                if key == "global3d":
                    physical = arrays["attributes"].copy()
                    rng = np.random.RandomState(1729)
                    for site in frame.position.unique():
                        where = np.flatnonzero(frame.position.to_numpy() == site)
                        physical[where] = physical[rng.permutation(where)]
                    blocks["global3d_attributes_shuffled_within_site"] = (
                        np.column_stack([base, physical])
                    )
                    blocks["esm650_global3d_attributes"] = np.column_stack(
                        [blocks["esm1v_650m"], arrays["attributes"]]
                    )
    for path in sorted(FEATURES.glob("kir_transfer_random*_s*.npz")):
        with np.load(path) as arrays:
            assert np.array_equal(arrays["ids"], frame.id)
            key = path.stem.removeprefix("kir_transfer_")
            blocks[key + "_latent"] = np.column_stack([base, arrays["latent"]])
    extra = FEATURES / "kir_esm2_3b.npz"
    if extra.exists():
        from data import AA

        with np.load(extra) as arrays:
            position = frame.position.to_numpy() - 1
            wt = np.array([AA.index(a) for a in frame.wt])
            alt = np.array([AA.index(a) for a in frame.alt])
            llr = (
                arrays["masked_logp"][position, alt]
                - arrays["masked_logp"][position, wt]
            )
            context = np.column_stack(
                [
                    base,
                    arrays["wt_hidden"][position],
                    arrays["aa_embedding"][alt] - arrays["aa_embedding"][wt],
                    llr,
                ]
            )
            blocks["ESM3B_LLR"] = np.column_stack([base, llr])
            blocks["ESM3B_WTcontext"] = context
            blocks["ESM3B_WTcontext_global3d"] = np.column_stack(
                [context, blocks["global3d_attributes"][:, base.shape[1] :]]
            )
    return blocks


def compare(feature_pattern: str = ".*", tag: str = "") -> None:
    frame, _sequence = prepare()
    blocks = {
        name: x
        for name, x in feature_blocks(frame).items()
        if re.fullmatch(feature_pattern, name)
    }
    suffix = "_" + tag if tag else ""
    if tag:
        write_immutable(
            DATA / f"kir_run_{tag}.json",
            json.dumps(
                {
                    "tag": tag,
                    "features": feature_pattern,
                    "definition": (
                        "3BWTcontext+AAembeddingdelta+maskedLLR; source3BFP16, actual650autocastFP16. Different representation protocols, not a causal puremodelsizecomparison"
                        if tag == "3b"
                        else "Frozen architecture-matched random1D/3D latent features at three predeclared seeds versus physical source-pretrained latent features"
                    ),
                    "physical": (
                        "Same55global3DATtributes appended; no new experimental labels or partitions"
                        if tag == "3b"
                        else "Same source architecture, same frozen partitions and budgets; no physicalpretraining in randomcontrols"
                    ),
                },
                indent=2,
            )
            + "\n",
        )
    parts = pd.read_csv(ROOT / "sources/predictive/partitions.csv")
    parts = parts[parts.dataset == "kir_function"]
    y = frame[["function", "surface"]].to_numpy()
    rows: list[dict] = []
    predictions: list[dict] = []
    choices: list[dict] = []
    for protocol, part in parts.groupby("protocol"):
        split = frame.id.map(part.set_index("id").split).to_numpy()
        for budget in ["full", "1256"]:
            train, val, test = [
                np.flatnonzero(split == label)
                for label in ["train", "validation", "test"]
            ]
            rng = np.random.RandomState(1729)
            if budget == "1256":
                train = rng.permutation(train)[:1000]
                val = rng.permutation(val)[:256]
            devmean = y[train].mean(0)
            spread = np.maximum(y[train].std(0), 1e-6)
            z = (y - devmean) / spread
            output = {
                "WT_null": (np.zeros((len(test), 2)), np.maximum(y[val].std(0), 1e-6))
            }
            for name, x in blocks.items():
                for learner in (["ridge", "extra"] if x.shape[1] <= 200 else ["ridge"]):
                    start = time.perf_counter()
                    options = []
                    for setting in (
                        [1, 10, 100, 1000] if learner == "ridge" else [2, 8]
                    ):
                        model = (
                            make_pipeline(StandardScaler(), Ridge(alpha=setting))
                            if learner == "ridge"
                            else ExtraTreesRegressor(
                                n_estimators=300,
                                min_samples_leaf=setting,
                                max_features="sqrt",
                                random_state=1729,
                                n_jobs=3,
                            )
                        )
                        model.fit(x[train], z[train])
                        pv = model.predict(x[val])
                        loss = float(np.mean((pv - z[val]) ** 2))
                        options.append((loss, setting, model, pv))
                    loss, setting, model, pv = min(options, key=lambda item: item[0])
                    prediction = model.predict(x[test]) * spread + devmean
                    error_scale = np.maximum(((pv - z[val]) * spread).std(0), 1e-6)
                    output[f"{name}_{learner}"] = (prediction, error_scale)
                    choices.append(
                        {
                            "protocol": protocol,
                            "budget": budget,
                            "features": name,
                            "learner": learner,
                            "validation_standardized_MSE": loss,
                            "setting": setting,
                            "seconds": time.perf_counter() - start,
                        }
                    )
            for name, (prediction, scale) in output.items():
                for objective in ["function", "joint"]:
                    score = (
                        prediction[:, 0]
                        if objective == "function"
                        else np.minimum(
                            (prediction[:, 0] - 0.3) / scale[0],
                            (prediction[:, 1] + 0.3) / scale[1],
                        )
                    )
                    labels = (
                        frame.gain.to_numpy()[test]
                        if objective == "function"
                        else frame.joint_gain.to_numpy()[test]
                    )
                    supported = (
                        (
                            frame.function.to_numpy()
                            - 1.96 * frame.function_se.to_numpy()
                            > 0.3
                        )[test]
                        if objective == "function"
                        else frame.supported_joint_gain.to_numpy()[test]
                    )
                    rows.append(
                        {
                            "protocol": protocol,
                            "budget": budget,
                            "features": name,
                            "objective": objective,
                            "train_n": len(train),
                            "validation_n": len(val),
                            "test_n": len(test),
                            "prevalence": float(labels.mean()),
                            "P20": precision_at_k(score, labels, 20),
                            "P50": precision_at_k(score, labels, 50),
                            "AP": float(average_precision_score(labels, score)),
                            "supported_prevalence": float(supported.mean()),
                            "supported_P20": precision_at_k(score, supported, 20),
                            "function_RMSE": float(
                                np.sqrt(np.mean((prediction[:, 0] - y[test, 0]) ** 2))
                            ),
                            "surface_RMSE": float(
                                np.sqrt(np.mean((prediction[:, 1] - y[test, 1]) ** 2))
                            ),
                        }
                    )
                predictions.extend(
                    {
                        "protocol": protocol,
                        "budget": budget,
                        "features": name,
                        "id": ident,
                        "actual_function": float(a),
                        "actual_surface": float(b),
                        "predicted_function": float(c),
                        "predicted_surface": float(d),
                        "joint_score": float(
                            min((c - 0.3) / scale[0], (d + 0.3) / scale[1])
                        ),
                    }
                    for ident, (a, b), (c, d) in zip(
                        frame.id[test], y[test], prediction, strict=True
                    )
                )
            pd.DataFrame(rows).to_csv(
                OUT / f"kir_transfer_metrics{suffix}.csv", index=False
            )
            pd.DataFrame(predictions).to_csv(
                OUT / f"kir_transfer_predictions{suffix}.csv", index=False
            )
            (OUT / f"kir_transfer_choices{suffix}.json").write_text(
                json.dumps(choices, indent=2) + "\n"
            )
            print(protocol, budget, "completed", flush=True)


def classify(feature_pattern: str = ".*", tag: str = "") -> None:
    frame, _sequence = prepare()
    blocks = {
        name: x
        for name, x in feature_blocks(frame).items()
        if re.fullmatch(feature_pattern, name)
    }
    suffix = "_" + tag if tag else ""
    if tag:
        write_immutable(
            DATA / f"kir_run_{tag}.json",
            json.dumps(
                {
                    "tag": tag,
                    "features": feature_pattern,
                    "definition": (
                        "3BWTcontext+AAembeddingdelta+maskedLLR; source3BFP16, actual650autocastFP16. Different representation protocols, not a causal puremodelsizecomparison"
                        if tag == "3b"
                        else "Frozen architecture-matched random1D/3D latent features at three predeclared seeds versus physical source-pretrained latent features"
                    ),
                    "physical": (
                        "Same55global3DATtributes appended; no new experimental labels or partitions"
                        if tag == "3b"
                        else "Same source architecture, same frozen partitions and budgets; no physicalpretraining in randomcontrols"
                    ),
                },
                indent=2,
            )
            + "\n",
        )
    policy = {
        "hypothesis": "Utility-specific classification may improve joint-gain ranking where bulk regression does not; test incremental physics on the same frozen partitions",
        "label": "Pointfunction>.3 and surface>=-.3; secondary score-1.96SEboth constraints, not simultaneous calibratedconfidence",
        "models": "Class-balancedLogisticC.01/.1/1/10; ExtraTrees300leaf2/8 when<=200features",
        "selection": "ValidationAP then logloss; no test/hyperparameter reuse from regression",
        "budgets": "Same full versus1000train+256val prefixes as regression, seed1729",
        "scope": "Exploratory modeling on previously inspected Kir corpus; never a prospective result",
    }
    write_immutable(
        DATA / "kir_gain_classifier_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    parts = pd.read_csv(ROOT / "sources/predictive/partitions.csv")
    parts = parts[parts.dataset == "kir_function"]
    target = frame.joint_gain.to_numpy()
    supported = frame.supported_joint_gain.to_numpy()
    rows = []
    predictions: list[dict] = []
    choices = []
    for protocol, part in parts.groupby("protocol"):
        split = frame.id.map(part.set_index("id").split).to_numpy()
        for budget in ["full", "1256"]:
            train, val, test = [
                np.flatnonzero(split == label)
                for label in ["train", "validation", "test"]
            ]
            rng = np.random.RandomState(1729)
            if budget == "1256":
                train = rng.permutation(train)[:1000]
                val = rng.permutation(val)[:256]
            outputs = {"training_prior": np.full(len(test), target[train].mean())}
            for name, x in blocks.items():
                for learner in (
                    ["logistic", "extra"] if x.shape[1] <= 200 else ["logistic"]
                ):
                    start = time.perf_counter()
                    options = []
                    for setting in (
                        [0.01, 0.1, 1, 10] if learner == "logistic" else [2, 8]
                    ):
                        model = (
                            make_pipeline(
                                StandardScaler(),
                                LogisticRegression(
                                    C=setting,
                                    class_weight="balanced",
                                    solver="liblinear",
                                    max_iter=1000,
                                    random_state=1729,
                                ),
                            )
                            if learner == "logistic"
                            else ExtraTreesClassifier(
                                n_estimators=300,
                                min_samples_leaf=setting,
                                max_features="sqrt",
                                class_weight="balanced",
                                random_state=1729,
                                n_jobs=3,
                            )
                        )
                        model.fit(x[train], target[train])
                        pv = model.predict_proba(x[val])[:, 1]
                        ap = float(average_precision_score(target[val], pv))
                        loss = float(log_loss(target[val], pv))
                        options.append((-ap, loss, setting, model))
                    neg_ap, loss, setting, model = min(
                        options, key=lambda item: item[:2]
                    )
                    outputs[f"{name}_{learner}"] = model.predict_proba(x[test])[:, 1]
                    choices.append(
                        {
                            "protocol": protocol,
                            "budget": budget,
                            "features": name,
                            "learner": learner,
                            "validation_AP": -neg_ap,
                            "validation_logloss": loss,
                            "setting": setting,
                            "seconds": time.perf_counter() - start,
                        }
                    )
            for name, score in outputs.items():
                rows.append(
                    {
                        "protocol": protocol,
                        "budget": budget,
                        "features": name,
                        "train_n": len(train),
                        "validation_n": len(val),
                        "test_n": len(test),
                        "prevalence": float(target[test].mean()),
                        "P20": precision_at_k(score, target[test], 20),
                        "P50": precision_at_k(score, target[test], 50),
                        "AP": float(average_precision_score(target[test], score)),
                        "supported_prevalence": float(supported[test].mean()),
                        "supported_P20": precision_at_k(score, supported[test], 20),
                        "supported_AP": float(
                            average_precision_score(supported[test], score)
                        ),
                    }
                )
                predictions.extend(
                    {
                        "protocol": protocol,
                        "budget": budget,
                        "features": name,
                        "id": ident,
                        "joint_gain": bool(gain),
                        "supported_joint_gain": bool(secure),
                        "score": float(pr),
                    }
                    for ident, gain, secure, pr in zip(
                        frame.id[test],
                        target[test],
                        supported[test],
                        score,
                        strict=True,
                    )
                )
            pd.DataFrame(rows).to_csv(
                OUT / f"kir_classifier_metrics{suffix}.csv", index=False
            )
            pd.DataFrame(predictions).to_csv(
                OUT / f"kir_classifier_predictions{suffix}.csv", index=False
            )
            (OUT / f"kir_classifier_choices{suffix}.json").write_text(
                json.dumps(choices, indent=2) + "\n"
            )
            print(protocol, budget, "completed", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["prepare", "features", "compare", "classify"])
    p.add_argument("--feature-pattern", default=".*")
    p.add_argument("--tag", default="")
    args = p.parse_args()
    torch.set_num_threads(2)
    with threadpool_limits(limits=3):
        if args.mode in ["compare", "classify"]:
            {"compare": compare, "classify": classify}[args.mode](
                args.feature_pattern, args.tag
            )
        else:
            {"prepare": prepare, "features": features}[args.mode]()


if __name__ == "__main__":
    main()
