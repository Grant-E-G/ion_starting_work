"""Compact measurement/structure provenance and local artifact inventory."""

from __future__ import annotations

import json

import pandas as pd
from data import DATA, OUT, RAW, constants, load_bk, sha256


def main() -> None:
    datasets = []
    for name, info in constants().items():
        folder = RAW / "VEP/data" / name
        label = folder / f"{name}.tsv"
        datasets.append(
            {
                "dataset": name,
                "labels": str(label.relative_to(DATA)),
                "label_sha256": sha256(label),
                "sequence": info["wt_aa"],
                "sequence_length": len(info["wt_aa"]),
                "mutation_index_offset": info["wt_ofs"],
                "structure": str((RAW / "VEP" / info["pdb_fn"]).relative_to(DATA)),
                "structure_sha256": sha256(RAW / "VEP" / info["pdb_fn"]),
                "physical_features": "Released mutant-minus-WT Rosetta8terms and WT RMSF; EvoEF2 newly generated matched-repacking deltas where present",
                "functional_scope": {
                    "gb1": "mRNA-display IgG binding enrichment; WT counts independently reconstructed; gain>=1.2WT",
                    "avgfp": "log10fluorescence relative to supplied WT; gain>=0.1log10",
                    "pab1": "Published functional fitness proxy; WT improvement reference unverified here",
                    "ube4b": "Published functional fitness proxy; WT improvement reference unverified here",
                    "bgl3": "Published functional fitness proxy; WT improvement reference unverified here",
                }[name],
            }
        )
    bk = load_bk()
    datasets.append(
        {
            "dataset": "BKpred",
            "mutants": len(bk),
            "unique_sites": int(bk.resN.nunique()),
            "numeric_records": int((~bk.censored).sum()),
            "censor_flags": int(bk.censored.sum()),
            "phenotype": "Published deltaVhalf mV at nominal zeroCa, voltage-fit endpoints partly extrapolated; not channel conductance",
            "WT": "Human structural reference, mixed source species339mouse/133human/1rat; auxiliary/isoform context incompletely resolved",
            "structure_states": {"closed": "6V3G chainA", "open": "6V38 chainA"},
            "structure_hashes": {p: sha256(RAW / f"{p}.pdb") for p in ["6V3G", "6V38"]},
            "normalization": "RawmV for new numeric regression; original published target200tanh(mV/200) reproduced separately",
            "numbering": "All473WT residue identities aligned to common human reference; full source isoform/background equivalence not established",
            "controls": "WT-zero anchoring; known-source/site means;13verifiedbeta1measurements; matchedWTrepacking; source-connected publication groups",
            "detail": "notes/sprint/bk_published_data_audit.json and bk_condition_audit.json",
        }
    )
    for name, filename, details in [
        (
            "ADRB2",
            "adrb2_measurements.csv",
            {
                "phenotype": "CRE/cAMPwhole-cell signaling proxy at0/.15/.625/5uMisoproterenol, two biological repeats; includes expression effects",
                "WT": "Percondition/perrepeat synonymouscontrolmean; Norm1isnotWT",
                "numbering": "CanonicalP07550; authorFASTAomitsinitialM/endsstop; native positions verified",
                "structures": "2RH1chainA and3SN6chainR common272native residues, fusion/engineered/missingresidues excluded",
                "quality": "Atleast3barcodes per repeat/condition plus published finitePCV<1",
                "benefit": "Bothrepeat>=1.2WTactivity; jointbasal<=1.2WTandsaturated>=.8WT",
                "independence": "Independent new membrane observable; five training subsamples share ONE fixed testsitepartition, not five independent test sets",
            },
        ),
        (
            "BKexternal2024",
            "external_bk_measurements.csv",
            {
                "phenotype": "InsideoutHEK293humanSlo1voltagegating at0/25uMCa, apparentBoltzmannslope",
                "WT": "AAB65837 first1056residuesidenticalto1065structuralreference; allmutationwindowsidentical, divergentCterminaltailunmodeled",
                "primary": "10novel0Ca genotypes;2oldsinglecontrols andhighCaexcluded",
                "benefit": "Fourleftgain>=50allinheritL312A;3retainslope>=.8WT; compareincrementtomatchedL312A, notWTalone",
                "provenance": "PMC11309983Table1, sources/sprint/external_bk_sources.json",
            },
        ),
        (
            "GB1Wu2016",
            "gb1_transfer_measurements.csv",
            {
                "phenotype": "mRNA-displaymediumIgGenrichment; experimentalconditiontransferfromOlsonnotexactlyequivalent",
                "WT": "VDGV counts92735input/338346selected",
                "data": "OriginalauthorsMutfitI20fitRaw, canonicalAAandinput>=10; neverimputedregression_missing; processedI20fitsinglesreuseOlsonsoexcluded",
                "test": "Hamming3/4only, fourzero-basedsites38/39/40/53excludedfromalltrainandval",
                "uncertainty": "ReadcountPoissonsecondarysupportonly, no biologicalreplication/multiplicitycertificate",
            },
        ),
    ]:
        path = OUT / filename
        if path.exists():
            frame = pd.read_csv(path)
            datasets.append(
                {
                    "dataset": name,
                    "measurements": str(path.relative_to(DATA.parent.parent)),
                    "measurement_sha256": sha256(path),
                    "rows": len(frame),
                    **details,
                }
            )
    kir = OUT / "kir_transfer_measurements.csv"
    if kir.exists():
        paired = pd.read_csv(kir)
        datasets.append(
            {
                "dataset": "Kir2.1 paired function/surface",
                "measurements": "notes/sprint/kir_transfer_measurements.csv",
                "measurement_sha256": sha256(kir),
                "rows": len(paired),
                "phenotype": "HEK voltage-dye function and surface-expression proxies, WT-reference median normalized; not direct conductance",
                "structure": "AF-P35561-F1-model_v6 exact native sequence, predicted WT monomer",
                "structure_sha256": sha256(RAW / "kir_af.pdb"),
                "partition": "Unchanged sources/predictive/partitions.csv; same construct/site assignment for both endpoints",
                "unfinished": "Six architecture-matched random feature caches generated; functional readouts not evaluated",
            }
        )
    result = {
        "session": "2026-10-14 six-hour sprint",
        "datasets": datasets,
        "source_manifests": "sources/sprint/*sources.json and model/weight manifests",
        "frozen_OmpF": "NoOmpFcode,dataorresultchanges; existing accelerated/audit.py checks frozen hashes",
        "interpretation": "All results retrospective. Newly explored model families on inspected corpora are exploratory; no target selected or new biological experiments.",
    }
    (DATA / "benchmark_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    inventory = []
    for pattern in [
        "*metrics*.csv",
        "*predictions*.csv",
        "*resources*.json",
        "*audit*.json",
        "*policy*.json",
        "*numerical*.json",
        "*uncertainty*.json",
    ]:
        for path in sorted(OUT.glob(pattern)):
            inventory.append(
                {
                    "path": str(path.relative_to(DATA.parent.parent)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    (OUT / "artifact_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(
        len(datasets), "measurementdatasets;", len(inventory), "hashedoutputartifacts"
    )


if __name__ == "__main__":
    main()
