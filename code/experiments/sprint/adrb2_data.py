"""Independent GPCR benchmark: exact controls, conditions and structure masks."""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd
from Bio import SeqIO
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from data import DATA, OUT, RAW, write_immutable

BASE = RAW / "adrb2"
CONDITIONS = [0.0, 0.15, 0.625, 5.0]


def wt_sequence() -> str:
    canonical = str(next(SeqIO.parse(BASE / "P07550.fasta", "fasta")).seq)
    author = str(next(SeqIO.parse(BASE / "repo/data/ADRB2_prot.fasta", "fasta")).seq)
    assert author[:-1] == canonical[1:] and author.endswith("*")
    return canonical


def structure_inputs(sequence: str) -> tuple[set[int], dict]:
    selected = {}
    audit = {}
    for state, identifier in [("closed", "2RH1"), ("open", "3SN6")]:
        structure = PDBParser(QUIET=True).get_structure(
            identifier, BASE / f"{identifier}.pdb"
        )[0]
        matches = {}
        for chain in structure:
            matches[chain.id] = {
                r.id[1]
                for r in chain
                if r.id[0] == " "
                and "CA" in r
                and 0 < r.id[1] <= len(sequence)
                and seq1(r.resname) == sequence[r.id[1] - 1]
            }
        chosen = max(matches, key=lambda key: len(matches[key]))
        assert len(matches[chosen]) > 250
        selected[state] = matches[chosen]
        audit[state] = {
            "pdb": identifier,
            "chain": chosen,
            "exact_native_matches": len(matches[chosen]),
            "excluded": "Fusion residues, unresolved sites and engineered non-WT residues",
        }
    common = selected["closed"] & selected["open"]
    for state, identifier in [("closed", "2RH1"), ("open", "3SN6")]:
        chain_id = audit[state]["chain"]
        lines = []
        for line in (BASE / f"{identifier}.pdb").read_text().splitlines():
            if (
                line.startswith("ATOM")
                and line[21] == chain_id
                and int(line[22:26]) in common
            ):
                lines.append(line[:21] + "A" + line[22:])
        (OUT / f"adrb2_{state}.pdb").write_text("\n".join(lines) + "\nEND\n")
    return common, audit


def prepare() -> None:
    policy = {
        "phenotype": "Forskolin-normalized CRE/cAMP signaling proxy, not direct receptor current/affinity; cannot separate expression and signaling potency",
        "reference": "Authors' synonymous-control means for each condition and biological repeat; no assumption DMS_score=1 is WT",
        "conditions_uM": CONDITIONS,
        "primary": ">=20% higher response at 0.15uM isoproterenol in BOTH biological repeats",
        "joint": "Primary gain AND basal signal <=120% WT AND 5uM saturated response >=80% WT in both repeats",
        "quality": "At least3 barcodes in both repeats for all4 conditions and finite relative propagated SD<1 in published supplement",
        "split": "All variants/conditions/barcodes at one native site kept together; SHA256(ADRB2-20261014:site) mod10:0-5 train,6-7 validation,8-9 test",
        "ranking": "Current-only predicted log2 EC50 response; joint score=min(activity-log2(1.2),log2(1.2)-basal,emax-log2(0.8))",
        "primary_comparison": "Common native residue sites resolved identically in both WT structural templates; no fusion or non-WT residue used",
        "interpretation": "Point-estimate replicate-consistent gains; not a biological-replicate significance certificate. Only two biological replicates; synonymous controls have compositional caveats noted by original authors.",
        "model_selection": "Validation only, test partitions unchanged; no tuning cutoff to observed gains",
    }
    write_immutable(DATA / "adrb2_policy.json", json.dumps(policy, indent=2) + "\n")
    sequence = wt_sequence()
    common, structural = structure_inputs(sequence)
    replicate = pd.read_csv(BASE / "repo/output/lib-med.csv.gz")
    scalars = pd.read_csv(BASE / "repo/output/scalars.csv")
    syn = scalars[scalars.Variant == "Synon"][
        ["Condition", "Repeat", "Scale_Mean", "Scale_SD", "Scale_N"]
    ]
    indel = scalars[scalars.Variant == "Indel"][
        ["Condition", "Repeat", "Scale_Mean"]
    ].rename(columns={"Scale_Mean": "Indel_mean"})
    replicate = replicate.merge(
        syn, on=["Condition", "Repeat"], validate="many_to_one"
    ).merge(indel, on=["Condition", "Repeat"], validate="many_to_one")
    replicate["relative_WT"] = replicate.Mean / replicate.Scale_Mean
    reconstructed = (
        replicate.assign(Norm=replicate.Mean / replicate.Indel_mean)
        .groupby(["Condition", "Pos", "AA"])
        .Norm.mean()
        .reset_index()
    )
    supplement = pd.read_excel(BASE / "elife-54895-supp2.xls")
    merged = supplement.merge(
        reconstructed,
        on=["Condition", "Pos", "AA"],
        suffixes=("_published", "_reconstructed"),
        validate="one_to_one",
    )
    error = float(abs(merged.Norm_published - merged.Norm_reconstructed).max())
    assert len(merged) == len(supplement) and error < 1e-10
    # Establish assay noise / reference reliability from controls, not mutant labels.
    controls = syn.merge(indel, on=["Condition", "Repeat"], validate="one_to_one")
    controls["normalized_WT"] = controls.Scale_Mean / controls.Indel_mean
    controls.to_csv(OUT / "adrb2_controls.csv", index=False)
    rows = []
    excluded: list[dict] = []
    for (position, alt), group in replicate.groupby(["Pos", "AA"], sort=True):
        position = int(position)
        assert 2 <= position <= len(sequence) and sequence[position - 1] != alt
        if len(group) != 8:
            excluded.append(
                {
                    "id": f"{sequence[position - 1]}{position}{alt}",
                    "reason": "Missing condition/repeat",
                    "observations": len(group),
                }
            )
            continue
        values = {
            (float(r.Condition), int(r.Repeat)): float(r.relative_WT)
            for r in group.itertuples()
        }
        if not all(value > 0 and np.isfinite(value) for value in values.values()):
            excluded.append(
                {
                    "id": f"{sequence[position - 1]}{position}{alt}",
                    "reason": "Nonpositive/nonfinite WT-relative activity",
                    "observations": len(group),
                }
            )
            continue
        published = supplement[(supplement.Pos == position) & (supplement.AA == alt)]
        quality = bool(
            (group.N >= 3).all()
            and len(published) == 4
            and np.isfinite(published.PCV).all()
            and (published.PCV < 1).all()
        )
        basal, activity, emax = [
            np.log2(np.mean([values[(condition, r)] for r in [1, 2]]))
            for condition in [0.0, 0.15, 5.0]
        ]
        gain = all(values[(0.15, r)] >= 1.2 for r in [1, 2])
        quiet = all(values[(0.0, r)] <= 1.2 for r in [1, 2])
        capacity = all(values[(5.0, r)] >= 0.8 for r in [1, 2])
        bucket = (
            int(
                hashlib.sha256(f"ADRB2-20261014:{position}".encode()).hexdigest()[:8],
                16,
            )
            % 10
        )
        rows.append(
            {
                "id": f"{sequence[position - 1]}{position}{alt}",
                "site": position,
                "alt": alt,
                "basal": basal,
                "activity": activity,
                "emax": emax,
                "gain": gain,
                "joint_gain": gain and quiet and capacity,
                "quality": quality,
                "structure_eligible": position in common,
                "split": (
                    "train" if bucket < 6 else "validation" if bucket < 8 else "test"
                ),
                "rep1_activity_WT": values[(0.15, 1)],
                "rep2_activity_WT": values[(0.15, 2)],
                "rep1_basal_WT": values[(0.0, 1)],
                "rep2_basal_WT": values[(0.0, 2)],
                "rep1_emax_WT": values[(5.0, 1)],
                "rep2_emax_WT": values[(5.0, 2)],
            }
        )
    pd.DataFrame(excluded).to_csv(OUT / "adrb2_exclusions.csv", index=False)
    frame = pd.DataFrame(rows)
    assert frame.id.is_unique
    frame.to_csv(OUT / "adrb2_measurements.csv", index=False)
    # Generated partitions/data remain ignored, but a compact expected hash
    # guards reproducibility and prevents accidental reassignment.
    partitions = frame[["id", "site", "split", "quality", "structure_eligible"]].to_csv(
        index=False
    )
    (OUT / "adrb2_partitions.csv").write_text(partitions)
    config = {
        "partition_sha256": hashlib.sha256(partitions.encode()).hexdigest(),
        "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
        "states": structural,
        "common_residue_sites": sorted(common),
        "conditions_uM": CONDITIONS,
        "supplement_reconstruction_max_error": error,
        "scope": policy["phenotype"],
    }
    write_immutable(DATA / "adrb2_manifest.json", json.dumps(config, indent=2) + "\n")
    audit = {
        "mutants": len(frame),
        "quality_mutants": int(frame.quality.sum()),
        "primary_structural_mutants": int(
            (frame.quality & frame.structure_eligible).sum()
        ),
        "common_structure_sites": len(common),
        "controls": controls.to_dict("records"),
        "label_counts_primary": frame[frame.quality & frame.structure_eligible]
        .groupby("split")[["gain", "joint_gain"]]
        .agg(["sum", "count"])
        .to_string(),
        "normalization_error": error,
        "warning": "cAMP/CRE transcription proxy mixes expression and intrinsic signaling; original synonymous controls have compositional caveats; no target commitment",
    }
    (OUT / "adrb2_data_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    prepare()
