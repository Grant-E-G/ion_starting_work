"""Create an offline review packet; large fields and raw publisher articles stay local."""

from __future__ import annotations

import json
import tarfile

from artifacts import digest, inventory
from physics import ROOT

if __name__ == "__main__":
    candidates = [
        ROOT / "README.md",
        ROOT / ".gitignore",
        ROOT / "math/ompf_physics_slice.md",
    ]
    candidates.extend((ROOT / "code/experiments/ompf").glob("*.py"))
    candidates.extend((ROOT / "code/experiments/ompf").glob("*.txt"))
    candidates.append(ROOT / "code/experiments/ompf/README.md")
    for folder in ["notes/ompf", "sources/ompf"]:
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file() or path.suffix in [".log", ".pyc"]:
                continue
            if path.name in [
                "review_bundle.tar.gz",
                "artifact_manifest.json",
                "review_bundle_manifest.json",
            ]:
                continue
            if folder == "notes/ompf" and path.name.endswith(".dx"):
                continue
            if (
                folder == "notes/ompf"
                and path.name.endswith("_field.npz")
                and str(path.relative_to(ROOT))
                not in [
                    "notes/ompf/trimer/WT_trimer_c0.1_h0.15_nonlinear_pb_seed0_field.npz",
                    "notes/ompf/trimer/EAE_trimer_c0.1_h0.15_nonlinear_pb_seed0_field.npz",
                ]
            ):
                continue
            if (
                folder == "sources/ompf"
                and "raw" in path.parts
                and path.suffix not in [".json", ".md"]
                and path.name != "phale2001_si.pdf"
            ):
                continue
            candidates.append(path)
    candidates = sorted(set(candidates))
    listing = {
        "files": [
            {
                "path": str(p.relative_to(ROOT)),
                "bytes": p.stat().st_size,
                "sha256": digest(p),
            }
            for p in candidates
        ],
        "note": "Prepared arrays, image maps and two plotted fields included; other calculated field arrays and raw articles omitted; the scanned SI input table needed by the dataset builder is included. Analysis refresh works from the bundle; full density audit requires regenerating omitted fields. Full local inventory is separate.",
    }
    manifest = ROOT / "notes/ompf/review_bundle_manifest.json"
    manifest.write_text(json.dumps(listing, indent=2) + "\n")
    with tarfile.open(ROOT / "notes/ompf/review_bundle.tar.gz", "w:gz") as archive:
        for path in [*candidates, manifest]:
            archive.add(path, arcname=str(path.relative_to(ROOT)))
    inventory()
    print(
        "Review files:",
        len(candidates),
        "archive MiB:",
        (ROOT / "notes/ompf/review_bundle.tar.gz").stat().st_size / 2**20,
    )
