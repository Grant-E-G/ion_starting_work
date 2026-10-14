"""Reconstruct pinned input caches and official pretrained weights from the manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request

from data import DATA, RAW

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((DATA / "source_manifest.json").read_text())
    RAW.mkdir(exist_ok=True)
    (DATA / "features").mkdir(exist_ok=True)
    for item in manifest["resources"]:
        if item["status"] != "cached" or not item.get("required_for_execution", False):
            continue
        path = RAW / item["name"]
        if not path.exists():
            request = urllib.request.Request(
                item["url"], headers={"User-Agent": "C5R-research/1.0"}
            )
            path.write_bytes(urllib.request.urlopen(request, timeout=60).read())
        assert (
            hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        ), f"Changed source: {path}"
    meta = manifest["pretrained"]
    (RAW / "pretrained_model.json").write_text(json.dumps(meta, indent=2) + "\n")
    if args.model:
        from transformers import AutoModelForMaskedLM, AutoTokenizer

        AutoModelForMaskedLM.from_pretrained(meta["name"], revision=meta["revision"])
        AutoTokenizer.from_pretrained(meta["name"], revision=meta["revision"])
    print("Verified cached source checksums; model download:", args.model)
