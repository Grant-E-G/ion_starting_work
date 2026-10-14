"""Retrieve exact public inputs and pinned weights; reject mismatched cached files."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import requests

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "sources/accelerated"
RAW = DATA / "raw"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--models", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((DATA / "source_manifest.json").read_text())
    RAW.mkdir(exist_ok=True)
    for item in manifest["resources"]:
        path = RAW / item["name"]
        if not path.exists() and not args.verify:
            response = requests.get(item["url"], timeout=60)
            response.raise_for_status()
            assert (
                hashlib.sha256(response.content).hexdigest() == item["sha256"]
            ), f"Changed upstream resource: {item['name']}"
            path.write_bytes(response.content)
        assert (
            path.exists() and digest(path) == item["sha256"]
        ), f"Missing or changed: {path}"
    if not args.verify:
        with ZipFile(RAW / "chrimson_supp.zip") as archive:
            name = next(n for n in archive.namelist() if n.endswith(".pdf"))
            (RAW / "chrimson_supp.pdf").write_bytes(archive.read(name))
        with ZipFile(RAW / "kcne1_supp.zip") as archive:
            for key, name in [
                ("MOESM6_ESM.xlsx", "kcne1_scores.xlsx"),
                ("MOESM7_ESM.pdb", "kcne1_complex.pdb"),
                ("MOESM2_ESM.xlsx", "kcne1_ephys_review.xlsx"),
            ]:
                member = next(n for n in archive.namelist() if key in n)
                (RAW / name).write_bytes(archive.read(member))
    if args.models:
        from huggingface_hub import snapshot_download

        for source in [
            DATA / "esm1v_model.json",
            ROOT / "sources/predictive/raw/pretrained_model.json",
        ]:
            meta = json.loads(source.read_text())
            snapshot_download(
                meta["name"],
                revision=meta["revision"],
                allow_patterns=[
                    "config.json",
                    "pytorch_model.bin",
                    "model.safetensors",
                    "vocab.txt",
                    "tokenizer_config.json",
                    "special_tokens_map.json",
                ],
            )
    print(f"Verified {len(manifest['resources'])} exact resources")


if __name__ == "__main__":
    main()
