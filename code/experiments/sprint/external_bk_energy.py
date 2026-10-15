"""Matched-environment nonadditive physical features for the external BK panel.

All target sites, including WT identities, are explicitly specified in every
BuildMutant line. WT, single constituents and joint mutant share the same crop
and repacking-site mask; crop/repacking differences are not called epistasis.
"""

from __future__ import annotations

import concurrent.futures
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from data import FEATURES, OUT, RAW
from energy import ENGINE, bk_variant, score


def crop(source: Path, destination: Path, tokens: list[str]) -> None:
    model = PDBParser(QUIET=True).get_structure("native", source)[0]
    centers = [model["A"][(" ", int(token[1:-1]), " ")]["CA"].coord for token in tokens]
    keep = {
        (chain.id, residue.id[1])
        for chain in model
        for residue in chain
        if residue.id[0] == " "
        and "CA" in residue
        and any(
            np.linalg.norm(residue["CA"].coord - center) <= 20 for center in centers
        )
    }
    lines = [
        line
        for line in source.read_text().splitlines()
        if line.startswith("ATOM") and (line[21], int(line[22:26])) in keep
    ]
    destination.write_text("\n".join(lines) + "\nEND\n")


def compound(ident: str) -> dict:
    destination = OUT / "external_bk_energy" / ident
    destination.mkdir(parents=True, exist_ok=True)
    cache = destination / "features.json"
    if cache.exists():
        return json.loads(cache.read_text())
    tokens = ident.split(",")
    assert len(tokens) > 1
    variants = [[token[:-1] + token[0] for token in tokens]]
    for index in range(len(tokens)):
        variants.append(
            [
                token if i == index else token[:-1] + token[0]
                for i, token in enumerate(tokens)
            ]
        )
    variants.append(tokens)
    mutfile = destination / "mutants.txt"
    mutfile.write_text(
        "\n".join(
            ",".join(f"{token[0]}A{token[1:-1]}{token[-1]}" for token in variant) + ";"
            for variant in variants
        )
        + "\n"
    )
    state_values = {}
    start = time.perf_counter()
    for state, identifier in [("closed", "6V3G"), ("open", "6V38")]:
        template = destination / f"{state}.pdb"
        crop(RAW / f"{identifier}.pdb", template, tokens)
        process = subprocess.run(
            [
                str(ENGINE),
                "--command=BuildMutant",
                f"--pdb={template.name}",
                f"--mutant_file={mutfile.name}",
            ],
            cwd=destination,
            capture_output=True,
            text=True,
            check=True,
            timeout=180,
        )
        (destination / f"{state}_build.log").write_text(process.stdout + process.stderr)
        energies = [
            score(destination / f"{state}_Model_{i + 1:04d}.pdb", destination)
            for i in range(len(variants))
        ]
        keys = list(energies[0])
        joint = {key: energies[-1][key] - energies[0][key] for key in keys}
        additive = {
            key: sum(row[key] - energies[0][key] for row in energies[1:-1])
            for key in keys
        }
        state_values[state] = {"joint": joint, "matched_additive": additive}
    result: dict = {
        "mutation": ident,
        "mutations": len(tokens),
        "seconds": time.perf_counter() - start,
    }
    for kind in ["joint", "matched_additive"]:
        for key in state_values["closed"][kind]:
            result[f"{kind}_{key}"] = (
                state_values["open"][kind][key] - state_values["closed"][kind][key]
            )
    result["epistasis_Total"] = result["joint_Total"] - result["matched_additive_Total"]
    cache.write_text(json.dumps(result, indent=2) + "\n")
    print(
        ident, "nonadditive stateTotal", round(result["epistasis_Total"], 3), flush=True
    )
    return result


def main() -> None:
    frame = pd.read_csv(OUT / "external_bk_measurements.csv")
    tokens = sorted({token for ident in frame.id for token in ident.split(",")})
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        atomic = list(pool.map(lambda token: bk_variant(token, 20), tokens))
    pd.DataFrame(atomic).to_csv(FEATURES / "external_bk_evoef_atomic.csv", index=False)
    ids = frame.loc[frame.id.str.contains(","), "id"].unique().tolist()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        combined = list(pool.map(compound, ids))
    pd.DataFrame(combined).to_csv(
        FEATURES / "external_bk_evoef_compounds.csv", index=False
    )
    (OUT / "external_bk_energy_resources.json").write_text(
        json.dumps(
            {
                "atomic_mutants": len(tokens),
                "compound_genotypes": len(ids),
                "seconds": time.perf_counter() - start,
                "workers": 2,
                "repacking": "WT/singles/joint on identical20A union crop and the same explicit design-site list",
                "scope": "Fixed-backbone unmodified EvoEF2 potential; subunitA mutated in a local tetramer environment, not a full homotetramer mutation/gating free energy; no calcium, voltage or lipids",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
