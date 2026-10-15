"""Mutation-specific pore hydration hypothesis, bounded by published controls.

Reuses already generated EvoEF2 sidechains, copies them by measured C4 rigid
transforms, preserves WT backbones, and applies the published hydration grid.
This is a fixed-backbone/profile approximation, not MD or gating free energy.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import json
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBIO, PDBParser, Superimposer
from Bio.PDB.Residue import Residue
from data import DATA, FEATURES, OUT, RAW, load_bk, write_immutable
from hydration import profile
from scipy.spatial import cKDTree
from scipy.spatial.distance import cdist


def symmetric_model(identifier: str, local_pdb: Path, destination: Path) -> dict:
    parser = PDBParser(QUIET=True)
    source = parser.get_structure(identifier, RAW / f"{identifier}.pdb")
    result = copy.deepcopy(source)
    patch = parser.get_structure("local", local_pdb)[0]["A"]
    backbone = {"N", "CA", "C", "O", "OXT"}
    fits = {}
    for chain_id in "ABCD":
        chain = source[0][chain_id]
        reference = source[0]["A"]
        common = [
            r.id
            for r in reference
            if r.id[0] == " "
            and 20 <= r.id[1] <= 350
            and r.id in chain
            and "CA" in r
            and "CA" in chain[r.id]
        ]
        aligner = Superimposer()
        aligner.set_atoms(
            [chain[i]["CA"] for i in common], [reference[i]["CA"] for i in common]
        )
        rotation, translation = aligner.rotran
        assert np.linalg.det(rotation) > 0.999
        fits[chain_id] = float(aligner.rms)
        assert aligner.rms < 0.5, "C4 replication not justified by WT structures"
        for residue in patch:
            if residue.id[0] != " " or residue.id not in result[0][chain_id]:
                continue
            native = result[0][chain_id][residue.id]
            name = (
                "HIS" if residue.resname in ["HSD", "HSE", "HIP"] else residue.resname
            )
            new = Residue(native.id, name, native.segid)
            # Do not import artificial patch-terminal atoms or move WT backbone.
            for atom in native:
                if atom.name in backbone and atom.element != "H":
                    new.add(atom.copy())
            for atom in residue:
                if atom.name not in backbone and atom.element != "H":
                    added = atom.copy()
                    added.transform(rotation, translation)
                    new.add(added)
            result[0][chain_id].detach_child(native.id)
            result[0][chain_id].add(new)
    writer = PDBIO()
    writer.set_structure(result)
    writer.save(str(destination))
    atoms = [
        atom
        for atom in result.get_atoms()
        if atom.element in ["C", "N", "O", "S"] and atom.parent.id[0] == " "
    ]
    pairs = cKDTree(np.array([atom.coord for atom in atoms])).query_pairs(
        1.5, output_type="ndarray"
    )
    clashes = sum(
        atoms[i].parent.parent.id != atoms[j].parent.parent.id for i, j in pairs
    )
    return {
        "max_C4_fit_RMSD_A": max(fits.values()),
        "interchain_heavy_clashes_below1_5A": int(clashes),
    }


def summarize(path: Path, profile_path: Path | None = None) -> dict[str, float]:
    values, _ = profile("mutant", path)
    if profile_path is not None:
        values.to_csv(profile_path, index=False)
    grid = pd.DataFrame(
        json.loads((RAW / "chap/scripts/heuristic/heuristic_grid.json").read_text())
    )
    query = np.column_stack([values.hydrophobicity, values.radius_A / 10])
    index = cdist(query, grid[["hydrophobicity", "radius"]]).argmin(1)
    energy = grid.energy.to_numpy()[index]
    outside = (
        (query[:, 0] < grid.hydrophobicity.min())
        | (query[:, 0] > grid.hydrophobicity.max())
        | (query[:, 1] < grid.radius.min())
        | (query[:, 1] > grid.radius.max())
    )
    peak = int(energy.argmax())
    return {
        "max_energy": float(energy[peak]),
        "mean_energy": float(energy.mean()),
        "positive_energy_integral_A": float(
            np.trapezoid(np.maximum(energy, 0), values.z_A)
        ),
        "dry_fraction": float((energy > 2.6).mean()),
        "min_radius_A": float(values.radius_A.min()),
        "mean_hydrophobicity": float(values.hydrophobicity.mean()),
        "outside_fraction": float(outside.mean()),
        "peak_outside_grid": float(outside[peak]),
        "search_start_radius_range_A": float(values.start_radius_range_A.max()),
    }


def variant(token: str, save_profiles: bool = False) -> dict:
    folder = OUT / "hydration_mutants" / token
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / "features.json"
    if destination.exists() and (
        not save_profiles
        or all(
            (folder / f"{state}_profile.csv").exists() for state in ["closed", "open"]
        )
    ):
        return json.loads(destination.read_text())
    result: dict = {"id": token}
    start = time.perf_counter()
    for state, identifier in [("closed", "6V3G"), ("open", "6V38")]:
        source = OUT / "evoef/bk_r20" / token
        for kind, number in [("self", 1), ("mutant", 2)]:
            # Self-repacked WT is site-specific and identical across alternative
            # substitutions; cache by site/state without function labels.
            reference_cache = (
                OUT / "hydration_mutants" / f"WT_{token[1:-1]}_{state}.json"
            )
            profile_path = (
                OUT / "hydration_mutants" / f"WT_{token[1:-1]}_{state}.csv"
                if kind == "self"
                else folder / f"{state}_profile.csv"
            )
            if (
                kind == "self"
                and reference_cache.exists()
                and (not save_profiles or profile_path.exists())
            ):
                summary = json.loads(reference_cache.read_text())
            else:
                with tempfile.TemporaryDirectory(dir=folder) as temporary:
                    path = Path(temporary) / "symmetric.pdb"
                    geometry = symmetric_model(
                        identifier, source / f"{state}_Model_{number:04d}.pdb", path
                    )
                    summary = {
                        **summarize(path, profile_path if save_profiles else None),
                        **geometry,
                    }
                if kind == "self":
                    reference_cache.write_text(json.dumps(summary, indent=2) + "\n")
            result.update(
                {f"{state}_{kind}_{key}": value for key, value in summary.items()}
            )
        for key in summary:
            result[f"{state}_delta_{key}"] = (
                result[f"{state}_mutant_{key}"] - result[f"{state}_self_{key}"]
            )
    result["seconds"] = time.perf_counter() - start
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(
        token,
        round(result["closed_delta_max_energy"], 3),
        round(result["open_delta_max_energy"], 3),
        flush=True,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--save-profiles", action="store_true")
    args = parser.parse_args()
    policy = {
        "hypothesis": "Mutation-specific pore hydration, rather than generic folding energy, predicts pore-functional changes",
        "controls": ["A316D", "A316V"],
        "source": "Published Jia2018 contrasting wet/dry mutants; these controls are not independent validation",
        "threshold": "Fixed published grid and original WW interface scale, no gating-label fitting in feature generation",
        "symmetry": "C4 transforms fitted to WT TM backbones; only sidechains copied, native backbone and true termini preserved",
        "domain": "Union of native pore-facing-proxy sites from WT open/closed profiles; remote mutations not assigned invented hydration effects",
        "primary_comparison": "Exclude A316D/V calibration controls; compare with the identical WW hydrophobicity delta and geometry baselines; site/publication holdouts remain fixed",
        "limitations": "Approximate profile extraction, fixed WT backbone, independent-ring rotamer replication, no explicit water/lipid/cofactor/sensor coupling; not a thermodynamic gating free energy",
    }
    write_immutable(DATA / "hydration_policy.json", json.dumps(policy, indent=2) + "\n")
    controls = [variant(token) for token in policy["controls"]]
    gate = (
        controls[0]["closed_delta_max_energy"] < controls[1]["closed_delta_max_energy"]
        and controls[0]["closed_delta_mean_hydrophobicity"]
        < controls[1]["closed_delta_mean_hydrophobicity"]
    )
    (OUT / "hydration_control_gate.json").write_text(
        json.dumps(
            {
                "passes_expected_ordering": bool(gate),
                "controls": controls,
                "scope": "Known physical ordering only, not independent mutant prediction",
            },
            indent=2,
        )
        + "\n"
    )
    if not args.all or not gate:
        print(
            "Control gate",
            gate,
            "no additional mutant scan" if not args.all or not gate else "",
        )
        return
    sites = set()
    for state in ["closed", "open"]:
        sites.update(pd.read_csv(OUT / f"bk_hydration_{state}_residues.csv").site)
    frame = load_bk()
    tokens = frame.loc[frame.resN.isin(sites), "id"].tolist()
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(
            pool.map(lambda token: variant(token, args.save_profiles), tokens)
        )
    pd.DataFrame(results).to_csv(FEATURES / "bk_hydration_mutants.csv", index=False)
    (
        OUT
        / (
            "hydration_profile_scan_resources.json"
            if args.save_profiles
            else "hydration_scan_resources.json"
        )
    ).write_text(
        json.dumps(
            {
                "mutants": len(tokens),
                "native_pore_proxy_sites": sorted(int(s) for s in sites),
                "seconds": time.perf_counter() - start,
                "workers": args.workers,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
