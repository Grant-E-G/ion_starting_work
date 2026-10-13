"""Download primary sources with explicit content checks; preserve condition-audit gaps."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request

from dataset import DATA


def fetch(force: bool = False) -> None:
    urls = {
        "raw/miedema2004.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1304784/",
        "raw/phale1997.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC21228/",
        "raw/pezeshki2009_si.pdf": "https://ars.els-cdn.com/content/image/1-s2.0-S0006349509012405-mmc1.pdf",
        "raw/pezeshki2009.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2756365/",
        "raw/miedema2006.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1367271/",
        "raw/bredin2002.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1222504/",
        "raw/nitrocefin2015.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4518837/",
        "raw/ionization2003.html": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1303675/",
        "raw/phale2001_si.pdf": "https://ndownloader.figshare.com/files/5670807",
        "raw/p02931.json": "https://rest.uniprot.org/uniprotkb/P02931.json",
        "raw/P02931.fasta": "https://rest.uniprot.org/uniprotkb/P02931.fasta",
        "raw/phale2001_si_metadata.json": "https://api.figshare.com/v2/articles/3584901",
    }
    ids = [
        "2OMF",
        "2ZFG",
        "1GFM",
        "1GFO",
        "1GFP",
        "1GFQ",
        "1HXT",
        "1HXU",
        "1HXX",
        "1MPF",
    ]
    for pdb in ids:
        urls[f"structures/{pdb}_assembly1.pdb"] = (
            f"https://files.rcsb.org/download/{pdb}.pdb1"
        )
        urls[f"raw/{pdb}_metadata.json"] = (
            f"https://data.rcsb.org/rest/v1/core/entry/{pdb}"
        )
    manifest = []
    for relative, url in urls.items():
        path = DATA / relative
        status = "cached"
        try:
            if force or not path.exists():
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 OmpF-feasibility-source-audit"},
                )
                with urllib.request.urlopen(request, timeout=30) as response:
                    payload = response.read()
                if relative.endswith(".pdf") and not payload.startswith(b"%PDF"):
                    raise ValueError("Expected PDF; received challenge/non-PDF")
                if relative.endswith(".pdb") and b"ATOM " not in payload:
                    raise ValueError("Expected atomic coordinates")
                if relative.endswith(".html") and b"PMCID" not in payload:
                    raise ValueError(
                        "Expected PMC article; received challenge/non-article"
                    )
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                status = "downloaded"
            payload = path.read_bytes()
            manifest.append(
                {
                    "path": relative,
                    "url": url,
                    "status": status,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                }
            )
        except (OSError, ValueError) as error:
            manifest.append(
                {"path": relative, "url": url, "status": "failed", "error": str(error)}
            )
        print(relative, manifest[-1]["status"], flush=True)
    (DATA / "fetch_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    fetch(args.force)
