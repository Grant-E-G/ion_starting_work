"""Falsify context/scoring robustness of the small Chrimson retrospective result."""

from __future__ import annotations

import json
import resource
import time

import pandas as pd
import torch
from benchmark import precision_at_k
from components import OUT, ROOT
from independent import inputs
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForMaskedLM, AutoTokenizer


def main() -> None:
    torch.set_num_threads(4)
    cases, audit = inputs()
    _, full, variants, _ = next(x for x in cases if x[0] == "chrimson")
    positions = list(audit["chrimson"]["author_to_sequence_index0"].values())
    lo, hi = min(positions), max(positions)
    contexts = [
        ("deposited_full", full, 0),
        ("resolved_span_with_internal_sequence_retained", full[lo : hi + 1], lo),
    ]
    rows = []
    timings = []
    specs = [
        ("esm2_8m", ROOT / "sources/predictive/raw/pretrained_model.json"),
        ("esm1v_650m", ROOT / "sources/accelerated/esm1v_model.json"),
    ]
    for name, path in specs:
        meta = json.loads(path.read_text())
        model = AutoModelForMaskedLM.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        ).eval()
        tok = AutoTokenizer.from_pretrained(
            meta["name"], revision=meta["revision"], local_files_only=True
        )
        for context, sequence, offset in contexts:
            encoded = tok(sequence, return_tensors="pt")
            start = time.perf_counter()
            with torch.inference_mode():
                wt = model(**encoded).logits[0].numpy()
            masked = {}
            for p in sorted({v["index"] - offset for v in variants}):
                ids = encoded["input_ids"].clone()
                ids[0, p + 1] = tok.mask_token_id
                with torch.inference_mode():
                    masked[p] = (
                        model(input_ids=ids, attention_mask=encoded["attention_mask"])
                        .logits[0, p + 1]
                        .numpy()
                    )
            for strategy in ["masked", "wt_marginal"]:
                for v in variants:
                    p = v["index"] - offset
                    assert sequence[p] == v["wt"]
                    scores = masked[p] if strategy == "masked" else wt[p + 1]
                    prediction = (
                        scores[tok.convert_tokens_to_ids(v["alt"])]
                        - scores[tok.convert_tokens_to_ids(v["wt"])]
                    )
                    rows.append(
                        {
                            "model": name,
                            "context": context,
                            "strategy": strategy,
                            "id": v["id"],
                            "prediction": prediction,
                            "gain": v["gain"],
                            "missing": v["missing"],
                        }
                    )
            timings.append(
                {
                    "model": name,
                    "context": context,
                    "sequence_length": len(sequence),
                    "seconds": time.perf_counter() - start,
                    "peak_rss_MiB_cumulative": resource.getrusage(
                        resource.RUSAGE_SELF
                    ).ru_maxrss
                    / 1024,
                }
            )
        del model, tok
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "context_sensitivity_predictions.csv", index=False)
    metrics = []
    for (model, context, strategy), g in frame.groupby(
        ["model", "context", "strategy"]
    ):
        g = g[~g.missing]
        metrics.append(
            {
                "model": model,
                "context": context,
                "strategy": strategy,
                "n": len(g),
                "precision5": precision_at_k(
                    g.prediction.to_numpy(), g.gain.to_numpy(), 5
                ),
                "auc": roc_auc_score(g.gain, g.prediction),
                "top5": g.nlargest(5, "prediction").id.tolist(),
            }
        )
    pd.DataFrame(metrics).to_csv(OUT / "context_sensitivity_metrics.csv", index=False)
    (OUT / "context_sensitivity_resources.json").write_text(
        json.dumps(timings, indent=2) + "\n"
    )
    print(pd.DataFrame(metrics).to_string(index=False))


if __name__ == "__main__":
    main()
