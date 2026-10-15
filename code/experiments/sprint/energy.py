"""Published EvoEF2 local repacking: mutation-specific energy components/cost.

Uses the unmodified MIT-licensed C++ implementation. No MD or fitted mutant
energies. Soluble-protein energy model; membrane transfer is not included.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import resource
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from data import FEATURES, OUT, RAW, constants, load_bk

ENGINE = RAW / "EvoEF2/EvoEF2"


def score(pdb: Path, folder: Path) -> dict[str, float]:
    # Upstream stores --pdb in a100-character C buffer. Stage identical bytes
    # with a short local filename; long repository/compound paths can otherwise
    # corrupt memory. Do not modify the published scientific engine.
    with tempfile.NamedTemporaryFile(dir=folder, suffix=".pdb") as staged:
        staged.write(pdb.read_bytes())
        staged.flush()
        process = subprocess.run(
            [
                str(ENGINE),
                "--command=ComputeStability",
                f"--pdb={Path(staged.name).name}",
            ],
            cwd=folder,
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
    result = {
        key: float(value)
        for key, value in re.findall(
            r"^([A-Za-z][A-Za-z0-9_]*)\s*=\s*([-+\d.eE]+)\s*$",
            process.stdout,
            re.MULTILINE,
        )
    }
    assert len(result) >= 60 and "Total" in result, process.stdout[-2000:]
    assert all(np.isfinite(list(result.values())))
    return result


def standardize(name: str, destination: Path) -> list[str]:
    info = constants()[name]
    source = RAW / "VEP" / info["pdb_fn"]
    chain = next(iter(PDBParser(QUIET=True).get_structure(name, source)[0]))
    residues = [r for r in chain if r.id[0] == " " and "CA" in r]
    assert "".join(seq1(r.resname) for r in residues) == info["wt_aa"]
    mapping = {r.id[1]: i + 1 for i, r in enumerate(residues)}
    lines = []
    for line in source.read_text().splitlines():
        if line.startswith("ATOM") and int(line[22:26]) in mapping:
            lines.append(
                line[:21] + "A" + f"{mapping[int(line[22:26])]:4d}" + line[26:]
            )
    destination.write_text("\n".join(lines) + "\nEND\n")
    table = pd.read_csv(RAW / f"VEP/data/{name}/ddG.tsv", sep="\t")
    assert table.mutation.is_unique
    return table.mutation.tolist()


def run_chunk(
    name: str, chunk: int, tokens: list[str], template: Path, offset: int
) -> list[dict]:
    folder = OUT / "evoef" / name / f"chunk_{chunk:04d}"
    folder.mkdir(parents=True, exist_ok=True)
    cached = folder / "features.json"
    if cached.exists():
        return json.loads(cached.read_text())
    mutfile = folder / "mutants.txt"
    mutfile.write_text(
        "\n".join(f"{v[0]}A{int(v[1:-1]) - offset + 1}{v[-1]};" for v in tokens) + "\n"
    )
    start = time.perf_counter()
    process = subprocess.run(
        [
            str(ENGINE),
            "--command=BuildMutant",
            f"--pdb={template}",
            f"--mutant_file={mutfile}",
        ],
        cwd=folder,
        capture_output=True,
        text=True,
        check=True,
        timeout=600,
    )
    (folder / "build.log").write_text(process.stdout + process.stderr)
    build_seconds = time.perf_counter() - start
    baseline = score(template, folder)
    rows = []
    for i, token in enumerate(tokens):
        pdb = folder / f"{template.stem}_Model_{i + 1:04d}.pdb"
        assert pdb.exists(), list(folder.glob("*.pdb"))
        values = score(pdb, folder)
        rows.append(
            dict(
                mutation=token,
                **{key: value - baseline[key] for key, value in values.items()},
            )
        )
        # Coordinates are disposable; immutable input/commands/features reproduce them.
        pdb.unlink()
    elapsed = time.perf_counter() - start
    (folder / "resources.json").write_text(
        json.dumps(
            {
                "mutations": len(tokens),
                "build_seconds": build_seconds,
                "total_seconds": elapsed,
            },
            indent=2,
        )
        + "\n"
    )
    cached.write_text(json.dumps(rows, indent=2) + "\n")
    return rows


def vep(name: str, workers: int, limit: int, self_controls: bool = False) -> None:
    folder = OUT / "evoef" / (name + "_self" if self_controls else name)
    folder.mkdir(parents=True, exist_ok=True)
    template = folder / "template.pdb"
    tokens = standardize(name, template)
    if self_controls:
        tokens = sorted({v[:-1] + v[0] for v in tokens})
    if limit:
        tokens = tokens[:limit]
    start = time.perf_counter()
    chunks = [tokens[i : i + 32] for i in range(0, len(tokens), 32)]
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(
                run_chunk,
                name + "_self" if self_controls else name,
                i,
                block,
                template,
                constants()[name]["wt_ofs"],
            )
            for i, block in enumerate(chunks)
        ]
        for future in concurrent.futures.as_completed(futures):
            rows.extend(future.result())
            print(name, "completed", len(rows), "/", len(tokens), flush=True)
    table = pd.DataFrame(rows).set_index("mutation").loc[tokens].reset_index()
    table.to_csv(
        FEATURES
        / f"{name}_evoef{'_self' if self_controls else ''}{'_pilot' if limit else ''}.csv",
        index=False,
    )
    receipt = {
        "dataset": name,
        "mutations": len(tokens),
        "wall_seconds": time.perf_counter() - start,
        "workers": workers,
        "peak_child_rss_MiB": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        / 1024,
        "scope": "Published EvoEF2 BuildMutant, ten hardcoded sequential local rotamer optimization cycles; mutant-minus-fixed-input energy components; no membrane term, no backbone relaxation or thermodynamic ensemble",
        "feature_baseline": "Fixed input structure, not per-site self-repacked reference; self-mutation control reported separately",
    }
    (
        OUT
        / f"{name}_evoef_resources{'_self' if self_controls else ''}{'_pilot' if limit else ''}.json"
    ).write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt), flush=True)


def bk_local_template(
    source: Path, destination: Path, position: int, radius: float
) -> None:
    """State-dependent local tetramer environment, preserving original numbering."""
    structure = PDBParser(QUIET=True).get_structure("bk", source)[0]
    center = structure["A"][(" ", position, " ")]["CA"].coord
    keep = {
        (c.id, r.id[1])
        for c in structure
        for r in c
        if r.id[0] == " "
        and "CA" in r
        and np.linalg.norm(r["CA"].coord - center) <= radius
    }
    lines = [
        line
        for line in source.read_text().splitlines()
        if line.startswith("ATOM") and (line[21], int(line[22:26])) in keep
    ]
    destination.write_text("\n".join(lines) + "\nEND\n")


def bk_variant(token: str, radius: float) -> dict:
    folder = OUT / "evoef" / f"bk_r{radius:g}" / token
    folder.mkdir(parents=True, exist_ok=True)
    cached = folder / "features.json"
    if cached.exists():
        return json.loads(cached.read_text())
    result: dict = {"mutation": token}
    start = time.perf_counter()
    for state, identifier in [("closed", "6V3G"), ("open", "6V38")]:
        template = folder / f"{state}.pdb"
        bk_local_template(RAW / f"{identifier}.pdb", template, int(token[1:-1]), radius)
        native = score(template, folder)
        # Same environment is repacked for WT and mutant; self subtraction removes
        # a large local relaxation contribution unrelated to changing residue type.
        mutfile = folder / f"{state}_mutants.txt"
        mutfile.write_text(
            f"{token[0]}A{token[1:-1]}{token[0]};\n{token[0]}A{token[1:-1]}{token[-1]};\n"
        )
        process = subprocess.run(
            [
                str(ENGINE),
                "--command=BuildMutant",
                f"--pdb={template}",
                f"--mutant_file={mutfile}",
            ],
            cwd=folder,
            capture_output=True,
            text=True,
            check=True,
            timeout=180,
        )
        (folder / f"{state}_build.log").write_text(process.stdout + process.stderr)
        wt, mutant = [
            score(folder / f"{state}_Model_{i:04d}.pdb", folder) for i in [1, 2]
        ]
        for key in mutant:
            result[f"{state}_{key}"] = mutant[key] - wt[key]
            result[f"{state}_self_{key}"] = wt[key] - native[key]
    for key in native:
        result[f"state_difference_{key}"] = (
            result[f"open_{key}"] - result[f"closed_{key}"]
        )
    result["seconds"] = time.perf_counter() - start
    cached.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["bk", *constants()], required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--radius", type=float, default=20.0)
    parser.add_argument("--self-controls", action="store_true")
    args = parser.parse_args()
    FEATURES.mkdir(exist_ok=True)
    if args.dataset != "bk":
        vep(args.dataset, args.workers, args.limit, args.self_controls)
        return
    frame = load_bk()
    tokens = frame.id.tolist()[: args.limit or len(frame)]
    start = time.perf_counter()
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(bk_variant, token, args.radius) for token in tokens]
        for future in concurrent.futures.as_completed(futures):
            rows.append(future.result())
            print("BK", len(rows), len(tokens), flush=True)
    pd.DataFrame(rows).set_index("mutation").loc[tokens].reset_index().to_csv(
        FEATURES / f"bk_evoef_r{args.radius:g}{'_pilot' if args.limit else ''}.csv",
        index=False,
    )
    receipt = {
        "mutations": len(tokens),
        "radius_angstrom": args.radius,
        "wall_seconds": time.perf_counter() - start,
        "workers": args.workers,
        "peak_child_rss_MiB": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        / 1024,
        "scope": "Local CA-radius tetramer patch, subunit A mutation, matched self-repacked WT, two experimental states; soluble energy with missing lipids/cofactors and artificial patch termini; not physical gating free energy",
    }
    (
        OUT
        / f"bk_evoef_r{args.radius:g}_resources{'_pilot' if args.limit else ''}.json"
    ).write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
