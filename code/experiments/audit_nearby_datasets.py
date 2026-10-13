"""Audit retrieved membrane-protein data and extract published benchmark results."""

import csv
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def main() -> None:
    directory = Path("sources/nearby_modeling")
    measured = read_csv(directory / "bedbrook2019_data2.csv")
    with gzip.open(directory / "rhomax_by_wild_type.csv.gz", "rt") as source:
        rhomax = list(csv.DictReader(source))
    report: dict[str, Any] = {
        "bedbrook2019": {
            "measured_records": len(measured),
            "unique_sequences": len({r["Amino_acid_sequence"] for r in measured}),
            "finite_peak_current_records": sum(
                math.isfinite(float(r["max_peak (nA)"])) for r in measured
            ),
            "finite_off_kinetics_records": sum(
                bool(r["kinetics_off"])
                and r["kinetics_off"].lower() != "nan"
                and math.isfinite(float(r["kinetics_off"]))
                for r in measured
            ),
            "literature_records_data1": len(
                read_csv(directory / "bedbrook2019_data1.csv")
            ),
            "predicted_not_measured_records_data3": len(
                read_csv(directory / "bedbrook2019_data3.csv")
            ),
            "feature_weights_not_variants_records_data4": len(
                read_csv(directory / "bedbrook2019_data4.csv")
            ),
        },
        "rhomax": {
            "rows": len(rhomax),
            "unique_sequences": len({r["sequence"] for r in rhomax}),
            "train_excluding_validation": sum(
                r["set"] == "train" and r["validation"] == "False" for r in rhomax
            ),
            "validation": sum(r["validation"] == "True" for r in rhomax),
            "test": sum(r["set"] == "test" for r in rhomax),
            "phenotype": "peak absorption wavelength, not ion transport",
        },
        "kir2_original_tables": {
            name: {
                "rows": len(read_csv(directory / name)),
                "columns": list(read_csv(directory / name)[0]),
            }
            for name in ["kir2_function_mod.csv", "kir2_surface_mod.csv"]
        },
    }
    sequence_counts = Counter(r["sequence"] for r in rhomax)
    report["rhomax"]["duplicate_sequences"] = [
        {
            "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
            "records": [
                {
                    "target": r["target"],
                    "split": "validation" if r["validation"] == "True" else r["set"],
                }
                for r in rhomax
                if r["sequence"] == sequence
            ],
        }
        for sequence, count in sequence_counts.items()
        if count > 1
    ]
    reference = read_csv(directory / "proteingym_reference.csv")
    relevant = [
        r
        for r in reference
        if any(
            prefix in r["DMS_id"]
            for prefix in [
                "KCNE1_",
                "KCNJ2_",
                "KCNH2_",
                "S22A1_",
                "SCN5A_",
                "ENVZ_",
                "OPSD_",
            ]
        )
    ]
    fields = [
        "DMS_id",
        "DMS_total_number_mutants",
        "seq_len",
        "selection_assay",
        "region_mutated",
        "title",
    ]
    with (directory / "assay_shortlist.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(relevant)
    zero_shot = {
        r["DMS ID"]: r
        for r in read_csv(directory / "proteingym_zero_shot_spearman.csv")
    }
    supervised = {
        r["DMS_id"]: r
        for r in read_csv(directory / "proteingym_supervised_contiguous_spearman.csv")
    }
    models = [
        "ESM2 (650M)",
        "ESM2 (3B)",
        "ESM2 (15B)",
        "ESM-C (600M)",
        "TranceptEVE L",
        "SaProt (650M)",
        "xTrimoPGLM-100B-int4",
        "AIDO Protein-RAG (16B)",
    ]
    report["published_results_not_local_runs"] = [
        {
            "assay": r["DMS_id"],
            "records_in_reference": int(r["DMS_total_number_mutants"]),
            "zero_shot_spearman": {m: float(zero_shot[r["DMS_id"]][m]) for m in models},
            "supervised_contiguous_spearman": {
                m: float(supervised[r["DMS_id"]][m])
                for m in [
                    "One-Hot Encodings",
                    "ESM-1v Embeddings",
                    "Kermut",
                    "ProteinNPT",
                ]
            },
        }
        for r in relevant
    ]
    (directory / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
    manifest = []
    for path in sorted(directory.iterdir()):
        if path.suffix in {".csv", ".gz"} and path.name != "assay_shortlist.csv":
            manifest.append(
                {
                    "file": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    (directory / "file_checksums.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k != "published_results_not_local_runs"
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
