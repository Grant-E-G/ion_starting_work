"""Create provenance-aware OmpF conductance records; no inferred missing values."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "sources/ompf"


def build() -> None:
    rows: list[dict] = []

    def add(
        study: str,
        variant: str,
        mutations: str,
        salt: str,
        molarity: float,
        mean: float,
        error: float | None,
        n: int | None,
        unit: str,
        conditions: str,
        eligible: bool = True,
        error_type: str = "SD",
    ) -> None:
        rows.append(
            {
                "measurement_id": f"{study}_{variant}_{salt}_{molarity}",
                "study": study,
                "variant": variant,
                "mutations": mutations,
                "salt": salt,
                "molarity_M": molarity,
                "conductance_nS": mean,
                "error_nS": error,
                "error_type": error_type,
                "n": n,
                "reporting_unit": unit,
                "pH": 7.4,
                "temperature_K": "",
                "conditions": conditions,
                "split": (
                    "wt_calibration" if variant == "WT" else "retrospective_holdout"
                ),
                "evaluation_eligible": eligible,
            }
        )

    mutations = {
        "WT": "",
        "AAA": "R42A/R82A/R132A",
        "EAE": "R42E/R82A/R132E",
        "LEAE": "K16L/R42E/R82A/R132E",
    }
    # Exact Table 2 means, dispersions and n, cross-checked against saved full text.
    for salt, c, records in [
        (
            "NaCl",
            0.1,
            [("WT", 0.50, 0.04, 5), ("EAE", 0.80, 0.03, 8), ("LEAE", 0.92, 0.05, 5)],
        ),
        (
            "NaCl",
            1.0,
            [("WT", 2.39, 0.09, 8), ("EAE", 2.67, 0.03, 6), ("LEAE", 2.84, 0.07, 5)],
        ),
        (
            "KCl",
            0.1,
            [("WT", 0.82, 0.07, 11), ("AAA", 1.32, 0.04, 9), ("EAE", 1.23, 0.04, 9)],
        ),
        (
            "KCl",
            1.0,
            [("WT", 4.20, 0.12, 17), ("AAA", 4.58, 0.10, 11), ("EAE", 4.61, 0.17, 9)],
        ),
    ]:
        for v, g, e, n in records:
            add(
                "miedema2004",
                v,
                mutations[v],
                salt,
                c,
                g,
                e,
                n,
                "trimer",
                "symmetric; 20 mM HEPES/NMDG; PE:PC 8:2 in decane; slope -25 to +25 mV",
                error_type="reported_plus_minus_not_explicitly_defined",
            )
    # Primary Table 1: event count is not biological replicate count. Conditions include calcium.
    for v, g, e, n in [
        ("WT", 0.84, 0.06, 156),
        ("S272A", 0.76, 0.02, 173),
        ("E296L", 0.66, 0.04, 87),
        ("E296A", 0.78, 0.03, 67),
        ("E296Q", 0.78, 0.03, 63),
        ("D312N", 0.60, 0.03, 137),
        ("A333C", 0.81, 0.03, 50),
        ("E117C", 0.68, 0.02, 97),
        ("del116-120", 0.17, 0.03, 90),
        ("E117C_A333C", 0.71, 0.02, 159),
        ("E117C_A333C_reduced", 0.57, 0.01, 52),
    ]:
        mut = v.replace("_reduced", "").replace("_", "/")
        add(
            "phale1997",
            v,
            "" if v == "WT" else mut,
            "NaCl",
            1.0,
            g,
            e,
            n,
            "monomer",
            "symmetric; 10 mM Tris-HCl; 1 mM CaCl2; unit inferred from resolved single-step closure trace; voltage regime not zero-slope",
            eligible=not ("del" in v or "A333C_" in v or "E117C_A333C" in v),
        )
    # External-study challenge, obtained after the initial model was fixed.
    # Above-threshold monomer closure steps differ from our zero-voltage linear response.
    for v, g, e in [
        ("WT", 0.820, 0.050),
        ("K16A", 0.880, 0.120),
        ("K16D", 0.800, 0.110),
        ("R132A", 0.710, 0.100),
        ("R132D", 0.640, 0.050),
    ]:
        add(
            "bredin2002",
            v,
            "" if v == "WT" else v,
            "NaCl",
            1.0,
            g,
            e,
            None,
            "monomer",
            "symmetric; 10 mM HEPES; asolectin; room temperature; monomer closure steps above critical voltage; 30-50 events, exact n unreported",
            error_type="reported_plus_minus_not_explicitly_defined",
        )
    # Exact experimental column of 2009 Table 1, kept separate from its simulations.
    # Supplement specifies pH6 for selectivity, not explicitly for each conductance.
    for v, mut, g in [
        ("WT", "", 4.0),
        ("AAA", "R42A/R82A/R132A", 4.2),
        ("NQRRR", "D113N/E117Q", 1.8),
    ]:
        add(
            "pezeshki2009",
            v,
            mut,
            "KCl",
            1.0,
            g,
            None,
            None,
            "trimer",
            "Table1: 22C and 1M KCl; full open state; conductance buffer/pH not explicitly assigned; methods compare experiments at 50mV with MD at 1V",
            eligible=False,
            error_type="not_reported",
        )
        rows[-1]["pH"] = ""
        rows[-1]["temperature_K"] = 295.15
    # Full-method external challenge with multiple dominant conductance populations.
    # Do not select the highest state or silently average unknown population weights.
    for v, mut, g, e, n, state in [
        ("WT", "", 0.710, 0.006, 14, "reference"),
        ("D127N", "D127N", 0.675, 0.009, 8, "population1"),
        ("D127N", "D127N", 0.717, 0.010, 8, "population2"),
        ("D127N", "D127N", 0.787, 0.026, 5, "population3"),
        ("D127K", "D127K", 0.593, 0.016, 6, "population1"),
        ("D127K", "D127K", 0.690, 0.010, 5, "population2"),
    ]:
        add(
            "miedema_d127_2006",
            v,
            mut,
            "KCl",
            0.1,
            g,
            e,
            n,
            "trimer",
            "symmetric; 20mM HEPES/NMDG pH7.4; PE:PC8:2 in decane; slope -10 to +10mV; multiple dominant protein subpopulations, weights not assumed",
            eligible=False,
            error_type="reported_plus_minus_not_explicitly_defined",
        )
        rows[-1]["measurement_id"] += "_" + state
        rows[-1]["measurement_state"] = state
    # Table S1, scanned supporting PDF. Condition footnotes refer to main Table 2,
    # which was not obtained; preserve records but do not silently pool them.
    si = [
        ("WT", 0.84, 0.06),
        ("D113C", 0.70, 0.04),
        ("D113G", 0.80, 0.06),
        ("E117Q", 0.64, 0.02),
        ("E117C", 0.68, 0.02),
        ("D113N/E117Q", 0.40, 0.02),
        ("R42C", 0.78, 0.07),
        ("R82C", 0.76, 0.06),
        ("R132P", 0.77, 0.04),
        ("NQAAA", 0.64, 0.04),
        ("Y102F", 0.77, 0.03),
        ("Y106F", 0.76, 0.03),
        ("V18K", 0.75, 0.01),
        ("G131K", 0.76, 0.03),
        ("V18K/G131K", 0.75, 0.02),
        ("E296Q", 0.78, 0.03),
        ("E296A", 0.78, 0.03),
        ("E296L", 0.66, 0.04),
        ("E296M", 0.70, 0.04),
        ("D312N", 0.60, 0.03),
        ("S272A", 0.76, 0.02),
        ("E117C/A333C", 0.71, 0.02),
        ("del116-120", 0.17, 0.03),
        ("del109-114", 0.50, 0.05),
        ("E71A", 0.65, 0.02),
        ("E71Q", 0.73, 0.07),
        ("D74A", 0.82, 0.02),
        ("D74N", 0.85, 0.03),
        ("R100A", 0.76, 0.02),
        ("R100S", 0.74, 0.02),
        ("E71A/R100A", 0.78, 0.02),
        ("E71A/R100S", 0.74, 0.02),
        ("E71Q/R100A", 0.78, 0.02),
        ("E71Q/R100S", 0.74, 0.02),
        ("del69-77", 0.76, 0.04),
    ]
    for v, g, e in si:
        mut = {"WT": "", "NQAAA": "R42A/R82A/D113N/E117Q/R132A"}.get(v, v)
        add(
            "phale2001_si",
            v,
            mut,
            "unverified",
            float("nan"),
            g,
            e,
            None,
            "unverified",
            "Table S1 manual transcription; main Table 2 conditions unavailable; overlaps 1997 data, not independent",
            eligible=False,
            error_type="unverified_plus_minus",
        )
    for r in rows:
        r.setdefault("measurement_state", "")
        r["observable_alignment"] = (
            "matched_zero_voltage_slope"
            if r["study"] == "miedema2004"
            else (
                "finite_voltage_challenge"
                if r["study"] in ("phale1997", "bredin2002")
                else "conditions_unverified"
            )
        )
    for r in rows:
        if r["study"] == "phale2001_si":
            r["condition_status"] = "main_condition_footnotes_unavailable"
            r["exclusion_reason"] = (
                "unverified_conditions; some rows reused from earlier studies"
            )
        elif r["study"] == "pezeshki2009":
            r["condition_status"] = (
                "concentration_temperature_verified; conductance_pH_unspecified"
            )
            r["exclusion_reason"] = (
                "conductance_pH_not_explicit; experimental_uncertainty_absent"
            )
        elif r["study"] == "miedema_d127_2006":
            r["condition_status"] = (
                "matched_zero_slope_protocol_verified; multi_state_outcome"
            )
            r["exclusion_reason"] = (
                "multiple_subpopulations; no unconditional genotype mean without weights"
            )
            r["observable_alignment"] = (
                "matched_zero_voltage_slope_multiple_populations"
            )
        else:
            r["condition_status"] = (
                "audited_primary_methods; temperature_precision_limited"
            )
            r["exclusion_reason"] = (
                ""
                if r["evaluation_eligible"]
                else "deletion_or_disulfide_topology_not_implemented"
            )
        if not r["evaluation_eligible"]:
            r["split"] = (
                "excluded_condition_gap"
                if r["study"] in ("phale2001_si", "pezeshki2009")
                else "excluded_unsupported_topology"
            )
        if r["study"] == "miedema_d127_2006":
            r["condition_status"] = (
                "matched_zero_slope_protocol_verified; multi_state_outcome"
            )
            r["exclusion_reason"] = (
                "multiple_subpopulations; no unconditional genotype mean without weights"
            )
            r["observable_alignment"] = (
                "matched_zero_voltage_slope_multiple_populations"
            )
            r["split"] = "separate_set_valued_external_challenge"
        r["construct_independence_group"] = r["mutations"] or "WT"
    structure_by_variant = {
        "D113G": "1GFM",
        "R132P": "1GFO",
        "R42C": "1GFP",
        "R82C": "1GFQ",
        "NQAAA": "1HXT",
        "V18K/G131K": "1HXU",
        "Y106F": "1HXX",
        "G119D": "1MPF",
    }
    for r in rows:
        r["design_structure_input"] = "2OMF WT only"
        r["experimental_mutant_structure_pdb"] = structure_by_variant.get(
            r["variant"], ""
        )
        r["experimental_mutant_structure_role"] = (
            "reserved_diagnostic_only"
            if r["experimental_mutant_structure_pdb"]
            else "not_located_in_this_audit"
        )
    si_metadata = json.loads((DATA / "raw/phale2001_si_metadata.json").read_text())
    si_file = si_metadata["files"][0]
    assert (
        hashlib.md5((DATA / "raw/phale2001_si.pdf").read_bytes()).hexdigest()
        == si_file["computed_md5"]
    )
    out = DATA / "measurements.csv"
    with out.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    variants = {"WT": ""}
    for r in rows:
        if r["evaluation_eligible"]:
            assert variants.get(r["variant"], r["mutations"]) == r["mutations"]
            variants[r["variant"]] = r["mutations"]
    (DATA / "variants.json").write_text(json.dumps(variants, indent=2) + "\n")
    parser = PDBParser(QUIET=True)
    structures = []
    wtseq = ""
    wt_structure = parser.get_structure("wt", DATA / "structures/2OMF_assembly1.pdb")
    wt_residues = {
        r.id[1]: seq1(r.resname)
        for r in next(wt_structure.get_chains())
        if r.id[0] == " "
    }
    for p in sorted((DATA / "structures").glob("*_assembly1.pdb")):
        s = parser.get_structure(p.stem, p)
        rr = [r for r in next(s.get_chains()) if r.id[0] == " "]
        seq = "".join(seq1(r.resname) for r in rr)
        if p.name.startswith("2OMF"):
            wtseq = seq
        structures.append(
            {
                "pdb": p.name[:4],
                "path": str(p.relative_to(ROOT)),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "models": len(s),
                "assembly_encoding": "three MODEL records are biological symmetry copies, not independent conformations",
                "resolution_A": json.loads(
                    (DATA / f"raw/{p.name[:4]}_metadata.json").read_text()
                )["rcsb_entry_info"]["resolution_combined"],
                "unresolved_mature_residues": sorted(
                    set(range(1, 341)) - {r.id[1] for r in rr}
                ),
                "experimental_mutations": [
                    f"{wt_residues[r.id[1]]}{r.id[1]}{seq1(r.resname)}"
                    for r in rr
                    if r.id[1] in wt_residues
                    and wt_residues[r.id[1]] != seq1(r.resname)
                ],
                "protein_residues_first_chain": len(rr),
                "sequence": seq,
                "role": (
                    "design_template"
                    if p.name.startswith("2OMF")
                    else "reserved_structural_diagnostic"
                ),
            }
        )
    u = json.loads((DATA / "raw/p02931.json").read_text())
    assert u["sequence"]["value"][22:] == wtseq
    (DATA / "mature_reference.fasta").write_text(
        ">2OMF_chain_A mature_OmpF UniProt_P02931_23-362\n" + wtseq + "\n"
    )
    for v, muts in variants.items():
        for m in muts.split("/") if muts else []:
            assert wtseq[int(m[1:-1]) - 1] == m[0], (v, m)
    (DATA / "structure_manifest.json").write_text(
        json.dumps(structures, indent=2) + "\n"
    )
    provenance = {
        "critical_table_audit": "2009 Table 1 has blank experimental conductances for NQAAA, RRRRR+EE and DEERE; Bredin2002 Table1 assigns 880pS to K16A and 800pS to K16D, contrary to a 2003 discussion calling K16D a 7% gain; trust primary table",
        "numbering": "mature 2OMF 1-340; UniProt P02931 precursor = mature +22",
        "sources": {
            "miedema_d127_2006": {
                "url": "https://doi.org/10.1007/s00249-006-0084-4",
                "full_text_url": "https://ftp.rush.edu/users/molebio/Bob_Eisenberg/Reprints/2006/D127mutants_EurBiophysJ%20July%202006.pdf",
                "table": "1",
                "verified": "complete primary PDF, methods and state-resolved table",
                "warning": "reported multiple dominant conductance populations; no scalar genotype mean chosen or pooled",
            },
            "pezeshki2009": {
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2756365/",
                "si_url": "https://ars.els-cdn.com/content/image/1-s2.0-S0006349509012405-mmc1.pdf",
                "table": "1 experimental column",
                "verified": "full text, exact empty cells and downloaded supplement",
                "warning": "22C/1MKCl given; pH6 explicitly assigned to selectivity, conductance pH not stated; missing experimental G uncertainties; main simulations use1V vs experiments50mV",
            },
            "bredin2002": {
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1222504/",
                "full_text_url": "https://scispace.com/pdf/alteration-of-pore-properties-of-escherichia-coli-ompf-3e6psfwu6m.pdf",
                "doi": "10.1042/bj3630521",
                "table": "1 p525",
                "verified": "full eight-page PDF via browser extraction; local abstract HTML",
                "warning": "local PDF download returned 403; finite-voltage events, no zero-voltage slope; exact n and error statistic missing",
            },
            "miedema2004": {
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC1304784/",
                "table": "2",
                "verified": "full text and Table 2",
                "warning": "temperature not specified; error statistic not explicitly defined",
            },
            "phale1997": {
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC21228/",
                "table": "1",
                "verified": "full text, caption, trace",
                "warning": "conductance event counts; calcium and voltage differ from 2004",
            },
            "phale2001_si": {
                "url": "https://ndownloader.figshare.com/files/5670807",
                "doi": "10.1021/bi010046k.s001",
                "table": "S1 pp1-2",
                "verified": "scanned SI viewed and manually transcribed",
                "warning": "main-paper condition footnotes unavailable; excluded from primary validation",
            },
        },
        "hashes": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (DATA / "raw").iterdir()
            if p.is_file()
        },
        "exclusions": [
            "deletions",
            "disulfide double mutants",
            "PhoE different scaffold",
            "SI unverified conditions",
            "calcium/selectivity not modeled",
        ],
        "split_policy": "All WT calibrations; all eligible mutant labels retrospective holdout. Labels already known; not a blinded or prospective trial. Conditions repeated on same constructs are not independent targets.",
    }
    (DATA / "measurement_manifest.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )
    print(
        f'{len(rows)} measurements; {len(variants)} executable variants; {sum(r["evaluation_eligible"] for r in rows)} condition-audited evaluation rows'
    )


if __name__ == "__main__":
    build()
