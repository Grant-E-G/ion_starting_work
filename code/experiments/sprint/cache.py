"""Retrieve/verify exact scientific inputs; optionally build pinned EvoEF2."""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import tarfile
import zipfile

import requests
from data import DATA, RAW, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    resources = []
    for name in [
        "vep_sources.json",
        "bk_published_sources.json",
        "additional_sources.json",
        "metl_sources.json",
        "metl_weights.json",
        "vep_supplement_sources.json",
        "adrb2_sources.json",
        "adrb2_author_sources.json",
        "chap_sources.json",
        "encoding_audit_sources.json",
        "bk_scan_sources.json",
        "supporting_sources.json",
        "metl_normalization_sources.json",
        "external_bk_sources.json",
        "encom_sources.json",
        "gb1_wu_sources.json",
        "kir_structure_sources.json",
    ]:
        resources.extend(json.loads((DATA / name).read_text())["resources"])
    for item in resources:
        path = DATA / item["path"]
        if not path.exists() and not args.verify:
            response = requests.get(item["url"], timeout=120)
            response.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(response.content)
        assert (
            path.exists() and sha256(path) == item["sha256"]
        ), f"Missing/changed source: {path}"
    supplement = RAW / "adrb2/elife-54895-supp2.xls"
    if not supplement.exists() and not args.verify:
        with zipfile.ZipFile(RAW / "adrb2/supplement.zip") as archive:
            supplement.write_bytes(archive.read(supplement.name))
    assert supplement.exists(), "Run cache retrieval to extract the GPCR supplement"
    if not (RAW / "EvoEF2/src/Main.cpp").exists() and not args.verify:
        with tarfile.open(
            fileobj=io.BytesIO((RAW / "evoef_source.tar.gz").read_bytes())
        ) as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                from pathlib import Path

                relative = Path(*Path(member.name).parts[1:])
                assert not relative.is_absolute() and ".." not in relative.parts
                path = RAW / "EvoEF2" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                assert source is not None
                path.write_bytes(source.read())
    if args.build:
        folder = RAW / "EvoEF2"
        sources = sorted(
            str(p.relative_to(folder)) for p in (folder / "src").glob("*.cpp")
        )
        with (folder / "build.log").open("w") as log:
            subprocess.run(
                ["g++", "-O3", "-o", "EvoEF2", *sources],
                cwd=folder,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=120,
            )
    print(f"Verified {len(resources)} scientific resources")


if __name__ == "__main__":
    main()
