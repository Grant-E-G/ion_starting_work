"""Reproducible source/measurement audit; no pooled heterogeneous ephys labels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "sources/accelerated/raw"
OUT = ROOT / "notes/accelerated"


def main() -> None:
    scores = pd.read_excel(RAW / "kcne1_scores.xlsx")
    scores = scores[scores.mutationType.notna()]
    literature = pd.read_excel(RAW / "kcne1_ephys_review.xlsx")
    patch = literature[
        (literature.Class == "missense") & (literature.PatchData == "yes")
    ]
    # This workbook includes metadata rows and repeated literature observations.
    result = {
        "workbook_observations": len(scores),
        "mutation_types": scores.mutationType.value_counts().to_dict(),
        "functional_categories": scores["Functional Score Category"]
        .value_counts()
        .to_dict(),
        "confident_gain_variants": scores.loc[
            scores["Functional Score Category"] == "Gain", "mutation"
        ].tolist(),
        "paper_assay_limitation": "Known GOF G25V and G60D depleted similarly to WT; authors state assay is underpowered for GOF vs WT.",
        "literature_patch_rows": len(patch),
        "literature_unique_variants": patch.variant.nunique(),
        "literature_papers": patch.PMID.nunique(),
        "patch_systems": patch["Patch System"].value_counts().to_dict(),
        "eligible_primary_gain_benchmark": False,
        "reason": "Growth selection uses KCNQ1-S140G; literature table mixes constructs, voltages, systems and publications. Do not pool or treat repeated rows as independent genotypes.",
    }
    (OUT / "kcne1_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    sets = {
        "scientific_code": sorted((ROOT / "code/experiments/ompf").glob("*.py"))
        + sorted((ROOT / "code/experiments/ompf").glob("requirements*.txt")),
        "source_inputs": sorted(
            p for p in (ROOT / "sources/ompf").rglob("*") if p.is_file()
        ),
        "results": sorted(
            p
            for p in (ROOT / "notes/ompf").rglob("*")
            if p.is_file()
            and not p.name.endswith((".log", ".gz", ".zip", ".tar"))
            and p.name not in ["artifact_manifest.json", "review_bundle_manifest.json"]
        ),
    }
    expected = {
        "scientific_code": "65a906a6a3e98a188e8c06c48727ec54339b6cc30557599fe5fd792660175f83",
        "source_inputs": "ba9e1f22a68da389ed9259e9711cba8beba76b8e1ac4f2ef7a0885eb7194207c",
        "results": "cddce69e3934d96a850d6375de27527e6389923b6166c49ab00e5879a0acc054",
    }
    checked = {}
    for name, paths in sets.items():
        records = "".join(
            str(p.relative_to(ROOT))
            + "\t"
            + hashlib.sha256(p.read_bytes()).hexdigest()
            + "\n"
            for p in paths
        )
        actual = hashlib.sha256(records.encode()).hexdigest()
        checked[name] = {
            "files": len(paths),
            "sha256": actual,
            "matches_freeze": actual == expected[name],
        }
    freeze = {
        "sets": checked,
        "scope": "Exact aggregate verification against notes/ompf_benchmark_freeze.md; read-only, no OmpF model execution.",
    }
    (OUT / "ompf_freeze_verification.json").write_text(
        json.dumps(freeze, indent=2) + "\n"
    )
    assert all(item["matches_freeze"] for item in checked.values()), checked
    print(json.dumps(result, indent=2))
    print(json.dumps(freeze, indent=2))


if __name__ == "__main__":
    main()
