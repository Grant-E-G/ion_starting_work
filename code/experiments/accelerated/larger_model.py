"""CPU ESM-1v embeddings versus 8M on the old ChR panel; exploratory only."""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from components import OUT, ROOT
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from transformers import AutoModelForMaskedLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "predictive"))
from benchmark import precision_at_k
from data import DATA, load_bedbrook


def main() -> None:
    torch.set_num_threads(4)
    b, _ = load_bedbrook()
    start = time.perf_counter()
    path = OUT / "esm1v_bed_embeddings.npz"
    if not path.exists():
        meta = json.loads((ROOT / "sources/accelerated/esm1v_model.json").read_text())
        model = AutoModelForMaskedLM.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        ).eval()
        tok = AutoTokenizer.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        )
        reps = []
        t = time.perf_counter()
        for i, s in enumerate(b.sequence):
            enc = tok(s, return_tensors="pt")
            with torch.inference_mode():
                h = model(**enc, output_hidden_states=True).hidden_states[-1]
            reps.append(h[0, 1 : len(s) + 1].mean(0).numpy())
            if i % 30 == 0:
                print(i, time.perf_counter() - t, flush=True)
        np.savez_compressed(path, ids=b.id.to_numpy(dtype=str), esm=np.array(reps))
        (OUT / "esm1v_embedding_resources.json").write_text(
            json.dumps(
                {
                    "inference_seconds": time.perf_counter() - t,
                    "total_seconds": time.perf_counter() - start,
                    "variants": len(b),
                    "parameters": sum(p.numel() for p in model.parameters()),
                    "peak_rss_MiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    / 1024,
                    "device": "CPU",
                    "threads": 4,
                },
                indent=2,
            )
            + "\n"
        )
        del model, tok
    with np.load(path) as f:
        xlarge = f["esm"]
        assert np.array_equal(f["ids"], b.id)
    with np.load(DATA / "features/bedbrook.npz") as f:
        xsmall = f["esm"]
        assert np.array_equal(f["ids"], b.id)
    parts = pd.read_csv(DATA / "partitions.csv")
    p = parts[
        (parts.protocol == "bedbrook_temporal") & (parts.dataset == "bedbrook_current")
    ].set_index("id")
    split = b.id.map(p.split).to_numpy()
    current = np.log1p(b.score.to_numpy())
    tau = b.kinetics_off_y.to_numpy()
    known = np.isfinite(tau) & (tau > 0)
    kinetics = np.log(np.maximum(np.nan_to_num(tau, nan=1.0), 1e-10))
    limit = 1.2 * float(b[b.control].score.max())
    cap = float(b[b.control].kinetics_off_y.max())
    gain = b.score.to_numpy() > limit
    joint = gain & (tau <= cap) & known
    train = (split == "train") & known
    val = (split == "validation") & known
    test = (split == "test") & known
    results = []
    preds = []
    for name, x in [("esm2_8m", xsmall), ("esm1v_650m", xlarge)]:
        scaler = StandardScaler().fit(x[train])
        z = scaler.transform(x)
        options = []
        for alpha in [1.0, 10.0, 100.0]:
            mc = Ridge(alpha=alpha, solver="lsqr", tol=1e-7).fit(
                z[train], current[train]
            )
            mt = Ridge(alpha=alpha, solver="lsqr", tol=1e-7).fit(
                z[train], kinetics[train]
            )
            pc = mc.predict(z)
            pt = mt.predict(z)
            sc = max(float(np.std(pc[val] - current[val])), 1e-6)
            st = max(float(np.std(pt[val] - kinetics[val])), 1e-6)
            utility = np.minimum((pc - np.log1p(limit)) / sc, (np.log(cap) - pt) / st)
            options.append(
                (
                    -precision_at_k(utility[val], joint[val], 10),
                    float(np.mean(abs(np.expm1(pc[val]) - b.score.to_numpy()[val]))),
                    alpha,
                    utility,
                    pc,
                    pt,
                )
            )
        _, _, alpha, u, pc, pt = min(options, key=lambda q: q[:3])
        for ranking, scores in [("current_only", pc), ("current_kinetics", u)]:
            results.append(
                {
                    "model": name,
                    "ranking": ranking,
                    "n": int(test.sum()),
                    "current_gain_prevalence": float(gain[test].mean()),
                    "joint_prevalence": float(joint[test].mean()),
                    "current_P20": precision_at_k(scores[test], gain[test], 20),
                    "joint_P20": precision_at_k(scores[test], joint[test], 20),
                    "joint_P5": precision_at_k(scores[test], joint[test], 5),
                    "alpha": alpha,
                    "validation_joint_positives": int(joint[val].sum()),
                    "evidence": "exploratory inspected old test",
                }
            )
            for i in np.flatnonzero(test):
                preds.append(
                    {
                        "model": name,
                        "ranking": ranking,
                        "id": b.id.iloc[i],
                        "score": scores[i],
                        "predicted_current_nA": np.expm1(pc[i]),
                        "predicted_tau_ms": np.exp(pt[i]),
                        "current_nA": b.score.iloc[i],
                        "tau_ms": tau[i],
                        "joint_gain": joint[i],
                    }
                )
    pd.DataFrame(results).to_csv(OUT / "larger_model_metrics.csv", index=False)
    pd.DataFrame(preds).to_csv(OUT / "larger_model_predictions.csv", index=False)
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    main()
