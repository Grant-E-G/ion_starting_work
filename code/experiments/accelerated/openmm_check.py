"""Actual force-field compatibility test; not a gating/conductance prediction."""

from __future__ import annotations

import io
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

import openmm as mm
from openmm import app, unit
from pdbfixer import PDBFixer

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "notes/accelerated"
RAW = ROOT / "sources/predictive/raw"


def main(case_name: str | None = None) -> None:
    start = time.perf_counter()
    result = {
        "version": mm.__version__,
        "platforms": [
            mm.Platform.getPlatform(i).getName()
            for i in range(mm.Platform.getNumPlatforms())
        ],
    }
    ff = app.ForceField("amber14-all.xml", "implicit/obc2.xml")
    cases = []
    for name in ([case_name] if case_name else ["3UG9", "6M84"]):
        t = time.perf_counter()
        pdb = app.PDBFile(str(RAW / f"{name}.pdb"))
        model = app.Modeller(pdb.topology, pdb.positions)
        # Explicit monomer-only smoke test, not physiological assembly or membrane setup.
        remove = [
            a
            for c in model.topology.chains()
            for r in c.residues()
            for a in r.atoms()
            if c.index != 0
            or r.name
            not in {
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
            }
        ]
        model.delete(remove)
        case = {
            "template": name,
            "retained_atoms": model.topology.getNumAtoms(),
            "scope": "first chain protein only; aqueous GB implicit solvent, no lipids or retinal; compatibility only",
        }
        try:
            buffer = io.StringIO()
            app.PDBFile.writeFile(model.topology, model.positions, buffer)
            buffer.seek(0)
            fixer = PDBFixer(pdbfile=buffer)
            fixer.findMissingResidues()
            fixer.missingResidues = (
                {}
            )  # Do not invent long unresolved loops for this smoke test.
            fixer.findNonstandardResidues()
            fixer.replaceNonstandardResidues()
            fixer.findMissingAtoms()
            case["missing_heavy_atoms_before_repair"] = sum(
                len(v) for v in fixer.missingAtoms.values()
            )
            fixer.addMissingAtoms(seed=1729)
            model = app.Modeller(fixer.topology, fixer.positions)
            model.addHydrogens(
                ff, pH=7.0, platform=mm.Platform.getPlatformByName("CPU")
            )
            system = ff.createSystem(
                model.topology, nonbondedMethod=app.NoCutoff, constraints=app.HBonds
            )
            integrator = mm.VerletIntegrator(0.001 * unit.picoseconds)
            context = mm.Context(
                system,
                integrator,
                mm.Platform.getPlatformByName("CPU"),
                {"Threads": "4"},
            )
            context.setPositions(model.positions)
            before = (
                context.getState(getEnergy=True)
                .getPotentialEnergy()
                .value_in_unit(unit.kilojoules_per_mole)
            )
            mm.LocalEnergyMinimizer.minimize(context, maxIterations=20)
            after = (
                context.getState(getEnergy=True)
                .getPotentialEnergy()
                .value_in_unit(unit.kilojoules_per_mole)
            )
            case.update(
                status="executed",
                initial_kJ_mol=before,
                minimized_kJ_mol=after,
                particles=system.getNumParticles(),
            )
            del context, integrator
        except (ValueError, RuntimeError, KeyError) as e:
            case.update(status="incompatible_after_bounded_repair", error=str(e))
        case["seconds"] = time.perf_counter() - t
        cases.append(case)
    result.update(
        cases=cases,
        total_seconds=time.perf_counter() - start,
        peak_rss_MiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
    )
    (OUT / "openmm_compatibility.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        cases = []
        for name in ["3UG9", "6M84"]:
            start = time.perf_counter()
            try:
                completed = subprocess.run(
                    [sys.executable, __file__, name],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=True,
                )
                cases.extend(json.loads(completed.stdout)["cases"])
            except subprocess.TimeoutExpired:
                cases.append(
                    {
                        "template": name,
                        "status": "repair_timeout_20s",
                        "seconds": time.perf_counter() - start,
                        "scope": "bounded PDBFixer + implicit-solvent preparation; no production simulation or functional inference",
                    }
                )
            except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
                cases.append(
                    {
                        "template": name,
                        "status": "execution_error",
                        "error": str(error),
                        "seconds": time.perf_counter() - start,
                    }
                )
        result = {
            "version": mm.__version__,
            "platforms": [
                mm.Platform.getPlatform(i).getName()
                for i in range(mm.Platform.getNumPlatforms())
            ],
            "cases": cases,
        }
        (OUT / "openmm_compatibility.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(json.dumps(result, indent=2))
