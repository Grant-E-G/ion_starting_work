"""Wild-type-only mutant construction, charge assignment and restrained side-chain repair."""

from __future__ import annotations

import argparse
import io
import json
import random
import time
from pathlib import Path

import numpy as np
from openmm import (
    Context,
    CustomExternalForce,
    LangevinIntegrator,
    LocalEnergyMinimizer,
    Platform,
    unit,
)
from openmm.app import ForceField, NoCutoff, PDBFile
from pdbfixer import PDBFixer

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "sources/ompf/prepared"
THREE = dict(
    zip(
        "ARNDCQEGHILKMFPSTWYV",
        [
            "ALA",
            "ARG",
            "ASN",
            "ASP",
            "CYS",
            "GLN",
            "GLU",
            "GLY",
            "HIS",
            "ILE",
            "LEU",
            "LYS",
            "MET",
            "PHE",
            "PRO",
            "SER",
            "THR",
            "TRP",
            "TYR",
            "VAL",
        ],
    )
)
RADII = {"H": 0.120, "C": 0.170, "N": 0.155, "O": 0.152, "S": 0.180}


def prepare(
    variant: str,
    mutations: str,
    seed: int = 0,
    source: str = "2OMF",
    trimer: bool = False,
    platform_name: str = "CUDA",
) -> dict:
    start = time.perf_counter()
    random.seed(seed)
    np.random.seed(seed)
    platform = Platform.getPlatformByName(platform_name)
    print(f"Preparing {variant}: side chains and hydrogens", flush=True)
    lines = (
        (ROOT / f"sources/ompf/structures/{source}_assembly1.pdb")
        .read_text()
        .splitlines()
    )
    atoms = []
    chain_index = 0
    for line in lines:
        if line.startswith("ENDMDL"):
            if not trimer:
                break
            atoms.append("TER")
            chain_index += 1
        if line.startswith("ATOM") and line[16] in (" ", "A"):
            atoms.append(line[:16] + " " + line[17:21] + "ABC"[chain_index] + line[22:])
    fixer = PDBFixer(
        pdbfile=io.StringIO("\n".join(atoms) + "\nEND\n"), platform=platform
    )
    if mutations:
        changes = [
            f"{THREE[m[0]]}-{int(m[1:-1])}-{THREE[m[-1]]}" for m in mutations.split("/")
        ]
        for chain in fixer.topology.chains():
            fixer.applyMutations(changes, chain.id)
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findMissingAtoms()
    fixer.addMissingAtoms(seed=seed)
    fixer.addMissingHydrogens(pH=7.4)
    ff = ForceField("amber14-all.xml", "implicit/gbn2.xml")
    system = ff.createSystem(fixer.topology, nonbondedMethod=NoCutoff, constraints=None)
    restraint = CustomExternalForce("0.5*k*((x-x0)^2+(y-y0)^2+(z-z0)^2)")
    for param in ["k", "x0", "y0", "z0"]:
        restraint.addPerParticleParameter(param)
    xyz = np.array(fixer.positions.value_in_unit(unit.nanometer))
    mutated = {int(m[1:-1]) for m in mutations.split("/") if m}
    atomlist = list(fixer.topology.atoms())
    for a, pos in zip(atomlist, xyz):
        # Backbone and unchanged atoms anchored; changed side chains can repair clashes.
        k = (
            20000.0
            if a.element.symbol != "H"
            and (int(a.residue.id) not in mutated or a.name in ("N", "CA", "C", "O"))
            else 20.0
        )
        restraint.addParticle(a.index, [k, *pos])
    system.addForce(restraint)
    integrator = LangevinIntegrator(
        298 * unit.kelvin, 1 / unit.picosecond, 0.001 * unit.picoseconds
    )
    integrator.setRandomNumberSeed(seed + 1)
    print(f"Preparing {variant}: restrained minimization", flush=True)
    context = Context(
        system,
        integrator,
        platform,
        (
            {"Precision": "mixed", "DeterministicForces": "true"}
            if platform_name == "CUDA"
            else {"Threads": "4"}
        ),
    )
    context.setPositions(fixer.positions)
    before = (
        context.getState(getEnergy=True)
        .getPotentialEnergy()
        .value_in_unit(unit.kilojoule_per_mole)
    )
    LocalEnergyMinimizer.minimize(context, 10.0, 150)
    state = context.getState(getPositions=True, getEnergy=True)
    after = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    relaxed = np.array(state.getPositions(asNumpy=True).value_in_unit(unit.nanometer))
    # Constant reference placement, never recenter individual mutant side chains.
    reference = np.array(
        [
            a
            for a in xyz[
                [
                    a.index
                    for a in atomlist
                    if a.name == "CA" and int(a.residue.id) in (42, 82, 113, 117, 132)
                ]
            ]
        ]
    ).mean(0)
    # Use WT anchor saved once to ensure all designs have identical membrane placement.
    wt_name = "WT_trimer" if trimer else "WT"
    if source == "2OMF" and variant != wt_name:
        reference = np.load(OUT / f"{wt_name}_seed0.npz")["origin"]
    if trimer and variant != wt_name:
        apertures = np.load(OUT / f"{wt_name}_seed0.npz")["apertures"]
    else:
        apertures = np.array(
            [
                xyz[
                    [
                        a.index
                        for a in atomlist
                        if a.residue.chain.id == chain.id
                        and a.name == "CA"
                        and int(a.residue.id) in (42, 82, 113, 117, 132)
                    ]
                ].mean(0)[:2]
                - reference[:2]
                for chain in fixer.topology.chains()
            ]
        )
    chargeforce = next(
        f for f in system.getForces() if f.__class__.__name__ == "NonbondedForce"
    )
    charges = np.array(
        [
            chargeforce.getParticleParameters(i)[0].value_in_unit(
                unit.elementary_charge
            )
            for i in range(len(atomlist))
        ]
    )
    radii = np.array([RADII[a.element.symbol] for a in atomlist])
    heavy = np.array([a.element.symbol != "H" for a in atomlist])
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{variant}_seed{seed}.npz"
    np.savez_compressed(
        path,
        xyz=relaxed - reference,
        charges=charges,
        radii=radii,
        heavy=heavy,
        residue=np.array([int(a.residue.id) for a in atomlist]),
        origin=reference,
        apertures=apertures,
    )
    with path.with_suffix(".pdb").open("w") as f:
        PDBFile.writeFile(fixer.topology, state.getPositions(), f)
    result = {
        "platform": platform.getName(),
        "variant": variant,
        "mutations": mutations,
        "source": source,
        "seed": seed,
        "atoms": len(atomlist),
        "chains": len(list(fixer.topology.chains())),
        "total_charge_e": float(charges.sum()),
        "energy_before_kJmol": before,
        "energy_after_kJmol": after,
        "heavy_rms_displacement_nm": float(
            np.sqrt(np.mean(np.sum((relaxed[heavy] - xyz[heavy]) ** 2, axis=1)))
        ),
        "seconds": time.perf_counter() - start,
        "forcefield": "AMBER14 + GBn2 for repair only; AMBER partial charges retained",
        "path": str(path.relative_to(ROOT)),
    }
    path.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")
    del context, integrator
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trimer", action="store_true")
    parser.add_argument("--platform", default="CUDA", choices=["CUDA", "CPU"])
    args = parser.parse_args()
    variants = json.loads((ROOT / "sources/ompf/variants.json").read_text())
    for v, m in variants.items():
        if args.variant and v != args.variant:
            continue
        print(
            json.dumps(
                prepare(
                    v + ("_trimer" if args.trimer else ""),
                    m,
                    args.seed,
                    trimer=args.trimer,
                    platform_name=args.platform,
                )
            ),
            flush=True,
        )
