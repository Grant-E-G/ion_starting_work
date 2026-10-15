"""Published elastic-network numerical checks before functional interpretation."""

from __future__ import annotations

import json
import time

import numpy as np
from Bio.PDB import PDBIO, PDBParser
from data import OUT
from encom_check import measure, native_inputs
from threadpoolctl import threadpool_limits


def main() -> None:
    native_inputs()
    source = OUT / "encom/closed_native.pdb"
    structure = PDBParser(QUIET=True).get_structure("rotate", source)
    angle = 0.37
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1],
        ]
    )
    for atom in structure.get_atoms():
        atom.transform(rotation, np.array([3, -5, 2]))
    transformed = OUT / "encom/closed_rotated.pdb"
    writer = PDBIO()
    writer.set_structure(structure)
    writer.save(str(transformed))
    start = time.perf_counter()
    first, repeated, rotated = measure(source), measure(source), measure(transformed)
    repeat_error = abs(first["entropy_beta1"] - repeated["entropy_beta1"])
    rotation_error = abs(first["entropy_beta1"] - rotated["entropy_beta1"])
    assert repeat_error < 1e-8
    assert (
        rotation_error < 0.01
    ), "Frame/PDB-rounding sensitivity too large for this component"
    result = {
        "native": first,
        "repeated": repeated,
        "rotated_translated": rotated,
        "repeat_entropy_error": repeat_error,
        "rotation_entropy_error": rotation_error,
        "rotation_includes": "PDB0.001A coordinate rounding after rotation, so not exact symbolic equality",
        "passes_predeclared0_01entropy_tolerance": True,
        "seconds": time.perf_counter() - start,
        "scope": "Numerical consistency of a pseudo-physical component; not membrane functional prediction validation",
    }
    (OUT / "encom_numerical_checks.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()
