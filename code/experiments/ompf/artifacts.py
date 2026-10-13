"""Audit cached arrays and create a portable checksum inventory; never refit predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from physics import ROOT, Config, ion_density_factor


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def audit_density() -> dict[str, Any]:
    corrected = []
    checked = 0
    for path in (ROOT / "notes/ompf").rglob("*.json"):
        record = json.loads(path.read_text())
        if (
            not isinstance(record, dict)
            or "predictions" not in record
            or "config" not in record
        ):
            continue
        field_path = path.with_name(path.stem + "_field.npz")
        if not field_path.exists():
            raise FileNotFoundError(field_path)
        config = Config(**record["config"])
        with np.load(field_path) as field:
            water = field["water"]
            potential = field["potential"].ravel()[water.ravel()]
        source = record.get("self_energy_source")
        image = None
        if source:
            source_path = Path(source)
            if not source_path.is_absolute():
                source_path = ROOT / source_path
            with np.load(source_path) as energy:
                image = energy["self_energy"].ravel()[water.ravel()]
            record["self_energy_source"] = str(source_path.resolve().relative_to(ROOT))
        maximum = config.concentration_M * max(
            float(ion_density_factor(potential, z, config, image).max())
            for z in [1, -1]
        )
        prior = record.get("density_diagnostics", {}).get(
            "maximum_implied_ion_molarity"
        )
        if prior is None or not np.isclose(prior, maximum, rtol=1e-12, atol=1e-12):
            corrected.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "prior": prior,
                    "corrected": maximum,
                }
            )
            record["density_diagnostics"] = {
                "maximum_implied_ion_molarity": maximum,
                "note": "Recomputed from saved field and consistent image/crowding formula; no PDE or conductance recomputation",
            }
        checked += 1
        path.write_text(json.dumps(record, indent=2) + "\n")
    result = {
        "checked_predictions": checked,
        "corrected_derived_metadata": corrected,
        "note": "Derived density diagnostics only; transport predictions and original measured timings unchanged",
    }
    (ROOT / "notes/ompf/checks/density_metadata_audit.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    return result


def inventory() -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for folder in ["code/experiments/ompf", "sources/ompf", "notes/ompf"]:
        for path in sorted((ROOT / folder).rglob("*")):
            if (
                not path.is_file()
                or path.suffix in [".pyc", ".log"]
                or "__pycache__" in path.parts
            ):
                continue
            if path.name in ["artifact_manifest.json", "review_bundle.tar.gz"]:
                continue
            entries.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
    for name in ["README.md", ".gitignore", "math/ompf_physics_slice.md"]:
        path = ROOT / name
        entries.append(
            {"path": name, "bytes": path.stat().st_size, "sha256": digest(path)}
        )
    result = {
        "files": entries,
        "total_bytes": sum(e["bytes"] for e in entries),
        "note": "Hashes of exact local artifacts. Download provenance is in source manifests. Logs and generated caches excluded; no commit/push or prospective experiment claimed.",
    }
    (ROOT / "notes/ompf/artifact_manifest.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-density", action="store_true")
    args = parser.parse_args()
    if args.audit_density:
        result = audit_density()
        print(
            "Checked",
            result["checked_predictions"],
            "density records; corrected",
            len(result["corrected_derived_metadata"]),
        )
    result = inventory()
    print(
        "Inventoried", len(result["files"]), "files and", result["total_bytes"], "bytes"
    )
