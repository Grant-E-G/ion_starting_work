"""Independent native C++ mutant-build reproducibility and backbone checks."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time

import numpy as np
from Bio.PDB import PDBParser
from data import OUT, constants
from energy import ENGINE, score, standardize


def main() -> None:
    start = time.perf_counter()
    root = OUT / "energy_repeat"
    root.mkdir(exist_ok=True)
    tokens = standardize("pab1", root / "native.pdb")
    token = tokens[0]
    offset = constants()["pab1"]["wt_ofs"]
    position = int(token[1:-1]) - offset + 1
    records: list[dict] = []
    for repeat in range(3):
        folder = root / f"repeat{repeat}"
        folder.mkdir(exist_ok=True)
        (folder / "template.pdb").write_bytes((root / "native.pdb").read_bytes())
        (folder / "mutants.txt").write_text(f"{token[0]}A{position}{token[-1]};\n")
        process = subprocess.run(
            [
                str(ENGINE),
                "--command=BuildMutant",
                "--pdb=template.pdb",
                "--mutant_file=mutants.txt",
            ],
            cwd=folder,
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
        (folder / "build.log").write_text(process.stdout + process.stderr)
        path = folder / "template_Model_0001.pdb"
        chain = PDBParser(QUIET=True).get_structure("mutant", path)[0]["A"]
        native = PDBParser(QUIET=True).get_structure("native", folder / "template.pdb")[
            0
        ]["A"]
        names = ["N", "CA", "C", "O"]
        errors = []
        for residue in native:
            for name in names:
                if name in residue and name in chain[residue.id]:
                    errors.append(
                        float(
                            np.linalg.norm(
                                residue[name].coord - chain[residue.id][name].coord
                            )
                        )
                    )
        atoms = [
            line for line in path.read_text().splitlines() if line.startswith("ATOM")
        ]
        records.append(
            {
                "repeat": repeat,
                "ATOM_record_sha256": hashlib.sha256(
                    "\n".join(atoms).encode()
                ).hexdigest(),
                "maximum_backbone_displacement_A": max(errors),
                "energy_Total": score(path, folder)["Total"],
            }
        )
    assert len({row["ATOM_record_sha256"] for row in records}) == 1
    assert all(row["maximum_backbone_displacement_A"] < 1e-6 for row in records)
    assert len({row["energy_Total"] for row in records}) == 1
    result = {
        "mutation": token,
        "independent_processes": records,
        "seconds": time.perf_counter() - start,
        "conclusion": "Tested nativeBuildMutant greedy path deterministic and fixed-backbone; repeatability is not force-field accuracy or conformational-ensemble uncertainty",
        "source": "Unmodified pinnedEvoEF2,10greedyrotameriterations; other engine design commands have random paths and are not tested by this result",
    }
    (OUT / "energy_repeat_numerics.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
