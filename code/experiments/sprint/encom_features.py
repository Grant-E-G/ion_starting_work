"""Existing ENCoM chemical-contact dynamics as a distinct cheap physical signal.

Mutation-sensitive entropy and harmonic work along the known WT state motion.
All parameters fixed at published defaults; no MD, no per-mutant fitted energies.
"""

from __future__ import annotations

import concurrent.futures
import functools
import hashlib
import json
import os
import time

import numpy as np
import pandas as pd
from Bio.PDB import PDBIO, PDBParser
from Bio.PDB.Chain import Chain
from Bio.PDB.Model import Model
from Bio.PDB.Residue import Residue
from Bio.PDB.Structure import Structure
from data import DATA, FEATURES, OUT, load_bk, write_immutable
from encom_check import measure, native_inputs
from threadpoolctl import threadpool_limits


@functools.lru_cache(maxsize=1)
def references() -> tuple[dict, dict]:
    structures = {
        state: PDBParser(QUIET=True).get_structure(
            state, OUT / f"encom/{state}_native.pdb"
        )[0]["A"]
        for state in ["closed", "open"]
    }
    coordinates = {
        state: np.array([residue["CA"].coord for residue in chain])
        for state, chain in structures.items()
    }
    assert [r.id for r in structures["closed"]] == [r.id for r in structures["open"]]
    displacements = {}
    for state, other in [("closed", "open"), ("open", "closed")]:
        first, second = coordinates[state], coordinates[other]
        left, _, right = np.linalg.svd(
            (second - second.mean(0)).T @ (first - first.mean(0))
        )
        rotation = left @ right
        if np.linalg.det(rotation) < 0:
            left[:, -1] *= -1
            rotation = left @ right
        aligned = (second - second.mean(0)) @ rotation + first.mean(0)
        displacements[state] = aligned - first
    return structures, displacements


def model_from_patch(state: str, patch_path, destination) -> None:
    structures, _ = references()
    native = structures[state]
    patch = PDBParser(QUIET=True).get_structure("patch", patch_path)[0]["A"]
    structure, model, chain = Structure("model"), Model(0), Chain("A")
    backbone = {"N", "CA", "C", "O", "OXT"}
    for original in native:
        candidate = patch.child_dict.get(original.id, original)
        name = (
            "HIS" if candidate.resname in ["HSD", "HSE", "HIP"] else candidate.resname
        )
        residue = Residue(original.id, name, original.segid)
        for atom in original:
            if atom.name in backbone and atom.element != "H":
                residue.add(atom.copy())
        for atom in candidate:
            if atom.name not in backbone and atom.element != "H":
                residue.add(atom.copy())
        # Native residue order and backbone coordinates are never reordered.
        chain.add(residue)
    model.add(chain)
    structure.add(model)
    writer = PDBIO()
    writer.set_structure(structure)
    writer.save(str(destination))


def evaluate(ident: str) -> dict:
    folder = OUT / "encom_models" / hashlib.sha256(ident.encode()).hexdigest()[:12]
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / "features.json"
    if destination.exists():
        return json.loads(destination.read_text())
    features: dict = {"id": ident}
    _, displacement = references()
    compound = "," in ident
    source = OUT / ("external_bk_energy" if compound else "evoef/bk_r20") / ident
    mutant_index = len(ident.split(",")) + 2 if compound else 2
    for state in ["closed", "open"]:
        summaries = {}
        for kind, index in [("self", 1), ("mutant", mutant_index)]:
            path = folder / f"{state}_{kind}.pdb"
            model_from_patch(state, source / f"{state}_Model_{index:04d}.pdb", path)
            key = hashlib.sha256(path.read_bytes()).hexdigest()
            cache = OUT / "encom_cache" / f"{state}_{key}.json"
            cache.parent.mkdir(exist_ok=True)
            if cache.exists():
                summary = json.loads(cache.read_text())
            else:
                summary = measure(path, displacement[state])
                temporary = cache.with_name(f"{cache.stem}_{os.getpid()}.tmp")
                temporary.write_text(json.dumps(summary, indent=2) + "\n")
                temporary.replace(cache)
            summaries[kind] = summary
        for name in [
            "entropy_beta1",
            "entropy_rigid_rotor",
            "low20_mean_log_eigenvalue",
            "harmonic_transition_work",
        ]:
            features[f"{state}_delta_{name}"] = (
                summaries["mutant"][name] - summaries["self"][name]
            )
    for name in [
        "entropy_beta1",
        "entropy_rigid_rotor",
        "low20_mean_log_eigenvalue",
        "harmonic_transition_work",
    ]:
        features[f"state_difference_{name}"] = (
            features[f"open_delta_{name}"] - features[f"closed_delta_{name}"]
        )
    destination.write_text(json.dumps(features, indent=2) + "\n")
    return features


def worker(ident: str) -> dict:
    with threadpool_limits(limits=1):
        try:
            return evaluate(ident)
        except (ValueError, AssertionError, KeyError, OSError) as error:
            return {"id": ident, "error": str(error)}


def main() -> None:
    native_inputs()
    structures, _ = references()
    sites = {residue.id[1] for residue in structures["closed"]}
    old = load_bk()
    tokens = old.loc[old.resN.isin(sites) & ~old.censored, "id"].tolist()
    external = pd.read_csv(OUT / "external_bk_measurements.csv")
    tokens = list(
        dict.fromkeys([*tokens, *external.id.tolist(), "A316D", "A316V", "I233V"])
    )
    policy = {
        "hypothesis": "Chemical-contact normal modes may add collective-motion/entropy information absent from finite-range fixed-backbone potential energies",
        "method": "Published NRGten1.2.9ENCoMdefaults, beta1, no parameter tuning",
        "domain": "Common273residue monomer TM region20-350; CA/backbone fixed, mutant/WTself sidechains grafted from existing EvoEF2; no missing loop invented",
        "features": "Mutant-minus-matched-self entropy(beta1 and releasedrigidrotor), low20log-eigenvalues, harmonic deformation work along Kabsch-aligned WT open/closed motion, plus state contrasts",
        "units": "Pseudo-physical ENCoM units, not calibrated gating free energy, population or kinetics",
        "tests": "Six rigid modes, positive remaining spectrum, symmetricHessian, rigidtranslationnull",
        "limitations": "Monomer, no membrane/cofactors/voltage/RCKdomains, truncated/missingloops, fixedbackboneharmonic approximation. Functional evaluation restricted to the same TMeligiblecohort for all methods.",
        "mutants": tokens,
        "validation": "Original immutable site/publication groups; independent2024panel alreadyinspected, so newmethod is exploratory, not a freshblindtest",
    }
    write_immutable(DATA / "encom_policy.json", json.dumps(policy, indent=2) + "\n")
    start = time.perf_counter()
    before = len(list((OUT / "encom_cache").glob("*.json")))
    rows = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        for i, result in enumerate(pool.map(worker, tokens), 1):
            rows.append(result)
            if i % 20 == 0 or i == len(tokens):
                pd.DataFrame(rows).to_csv(FEATURES / "bk_encom.csv", index=False)
                print(
                    "ENCoM",
                    i,
                    len(tokens),
                    "elapsed",
                    round(time.perf_counter() - start, 1),
                    flush=True,
                )
    (OUT / "encom_resources.json").write_text(
        json.dumps(
            {
                "requested_genotypes": len(tokens),
                "completed_genotypes": sum("error" not in row for row in rows),
                "seconds": time.perf_counter() - start,
                "processes": 2,
                "threads_per_process": 1,
                "new_structure_evaluations": len(
                    list((OUT / "encom_cache").glob("*.json"))
                )
                - before,
                "upstream_sidechain_cost": "AlreadygeneratedEvoEF2sidechains reused; not included in this walltime",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
