"""Summarize measured hardware fit and a six-mutant diagnostic, with exact null."""

import csv
import itertools
import json
from pathlib import Path


def concordance(scores: list[float], labels: tuple[int, ...]) -> float:
    points = []
    for i, j in itertools.combinations(range(len(scores)), 2):
        if labels[i] == labels[j]:
            continue
        product = (scores[i] - scores[j]) * (labels[i] - labels[j])
        points.append(1.0 if product > 0 else 0.5 if product == 0 else 0.0)
    return sum(points) / len(points)


def main() -> None:
    directory = Path("sources/model_benchmarks")
    with Path("sources/gtacr2_2018_diagnostic_labels.csv").open() as source:
        records = list(csv.DictReader(source))
    variants = [r["variant"] for r in records]
    labels = tuple(
        {"lower": -1, "wt_like": 0, "higher": 1}[r["phenotype_class"]] for r in records
    )
    null_labels = set(itertools.permutations(labels))
    summaries = []
    for stem in ["esm2_650m", "esmc_600m", "amplify_350m"]:
        metadata = json.loads((directory / f"{stem}.json").read_text())
        # Use full precision for the tiny functional diagnostic, BF16 for the
        # measured full-scan throughput and adapter feasibility benchmark.
        with (directory / f"{stem}_fp32.csv").open() as source:
            scores = {
                r["variant"]: float(r["masked_log_odds"])
                for r in csv.DictReader(source)
            }
        values = [scores[v] for v in variants]
        observed = concordance(values, labels)
        pvalue = sum(
            concordance(values, p) >= observed - 1e-12 for p in null_labels
        ) / len(null_labels)
        ranked = sorted(variants, key=lambda v: scores[v], reverse=True)
        summaries.append(
            {
                "model": metadata["model"],
                "revision": metadata["revision"],
                "scan_seconds": metadata["scan_seconds"],
                "inference_peak_allocated_gib": metadata[
                    "inference_peak_allocated_gib"
                ],
                "lora_status": metadata["lora_smoke_status"],
                "lora_peak_allocated_gib": metadata.get("lora_peak_allocated_gib"),
                "lora_trainable_parameters": metadata.get("lora_trainable_parameters"),
                "panel_ranking": ranked,
                "panel_scores": dict(zip(variants, values)),
                "gain_rank_of_six": ranked.index("E219Q") + 1,
                "ordinal_concordance_11_pairs": observed,
                "exact_one_sided_permutation_p": pvalue,
                "null_label_assignments": len(null_labels),
                "interpretation": "Diagnostic only; six selected residues from one paper, not generalization validation",
                "diagnostic_precision": "float32",
            }
        )
    (directory / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
