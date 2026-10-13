"""Run frozen-parameter WT and mutant calculations; compare with WT-calibrated baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from physics import ROOT, Config, run


def calculate(
    mode: str,
    spacing: float = 0.15,
    seed: int = 0,
    trimer: bool = False,
    selected_variants: list[str] | None = None,
) -> None:
    variants = json.loads((ROOT / "sources/ompf/variants.json").read_text())
    if selected_variants:
        variants = {v: variants[v] for v in selected_variants}
    for c in [1.0, 0.1]:
        for v in variants:
            config = Config(
                concentration_M=c,
                spacing_nm=spacing,
                electrostatics=mode,
                half_xy_nm=5.25 if trimer else 3.15,
            )
            result = run(
                v + ("_trimer" if trimer else ""),
                config,
                seed,
                ROOT / ("notes/ompf/trimer" if trimer else "notes/ompf/results"),
            )
            print(
                v,
                c,
                mode,
                result["seconds"],
                result["predictions"]["KCl"]["physics_nS"],
                flush=True,
            )


def compare(
    mode: str,
    spacing: float = 0.15,
    seed: int = 0,
    trimer: bool = False,
    allow_subset: bool = False,
    directory: Path | None = None,
    tag: str = "",
) -> tuple[pd.DataFrame, dict]:
    data = pd.read_csv(ROOT / "sources/ompf/measurements.csv")
    data = data[data.evaluation_eligible].copy()
    results = ROOT / ("notes/ompf/trimer" if trimer else "notes/ompf/results")
    if directory is not None:
        results = directory
    suffix = "_trimer" if trimer else ""
    output_suffix = suffix + ("_" + tag if tag else "")
    out = []
    variants = json.loads((ROOT / "sources/ompf/variants.json").read_text())
    formal = {"R": 1, "K": 1, "D": -1, "E": -1}
    for _, row in data.iterrows():
        c = row.molarity_M
        salt = row.salt
        variant = row.variant
        file = results / f"{variant}{suffix}_c{c}_h{spacing}_{mode}_seed{seed}.json"
        if allow_subset and not file.exists():
            continue
        model = json.loads(file.read_text())
        wtmodel = json.loads(
            (results / f"WT{suffix}_c{c}_h{spacing}_{mode}_seed{seed}.json").read_text()
        )
        wt = data[
            (data.study == row.study)
            & (data.variant == "WT")
            & (data.salt == salt)
            & (data.molarity_M == c)
        ].iloc[0]
        obs_ratio = row.conductance_nS / wt.conductance_nS
        predicted = model["predictions"][salt]
        base = wtmodel["predictions"][salt]
        # Charge-only Donnan cylinder with WT six-residue constriction charge +2e, fixed volume 2nm^3.
        # This volume is the published 2004 geometric estimate, not fitted to any mutant.
        pore_res = {16, 42, 82, 113, 117, 132}
        q = 2.0
        for m in variants[variant].split("/") if variants[variant] else []:
            if int(m[1:-1]) in pore_res:
                q += formal.get(m[-1], 0) - formal.get(m[0], 0)
        dn = 1.96 if salt == "KCl" else 1.33
        dc = 2.03

        def donnan(
            charge: float, c: float = c, dn: float = dn, dc: float = dc
        ) -> float:
            u = np.arcsinh(charge / (2 * 2.0 * 0.602214076 * c))
            return float(dn * np.exp(-u) + dc * np.exp(u))

        ratios = {
            "physics": predicted["physics_nS"] / base["physics_nS"],
            "geometry": predicted["geometry_nS"] / base["geometry_nS"],
            "charge": donnan(q) / donnan(2.0),
            "charge_entry": donnan(q - 3.0) / donnan(-1.0),
            "null": 1.0,
        }
        record = row.to_dict()
        record.update(
            observed_ratio=obs_ratio,
            observed_ratio_error=float(
                np.hypot(
                    row.error_nS / wt.conductance_nS,
                    row.conductance_nS * wt.error_nS / wt.conductance_nS**2,
                )
            ),
            formal_pore_charge_e=q,
        )
        for k, r in ratios.items():
            record[k + "_ratio"] = r
            record[k + "_nS"] = r * wt.conductance_nS
        out.append(record)
    frame = pd.DataFrame(out)
    metrics: dict[str, Any] = {}
    for cohort, subset in [
        ("all", frame),
        ("gain_cohort", frame[frame.study == "miedema2004"]),
        ("damage_cohort", frame[frame.study == "phale1997"]),
        ("external_study_challenge", frame[frame.study == "bredin2002"]),
    ]:
        subset = subset[subset.variant != "WT"]
        metrics[cohort] = {}
        if subset.empty:
            metrics[cohort] = {"status": "no_evaluable_mutants"}
            continue
        for model in ["physics", "geometry", "charge", "charge_entry", "null"]:
            error = subset[model + "_ratio"] - subset.observed_ratio
            metrics[cohort][model] = {
                "rows": len(subset),
                "constructs": subset.variant.nunique(),
                "ratio_MAE": float(np.abs(error).mean()),
                "ratio_RMSE": float(np.sqrt(np.mean(error**2))),
                "improvement_hits": int(
                    (
                        (subset.observed_ratio > 1.05)
                        & (subset[model + "_ratio"] > 1.05)
                    ).sum()
                ),
                "improvement_rows": int((subset.observed_ratio > 1.05).sum()),
                "false_improvement_rows": int(
                    (
                        (subset.observed_ratio <= 1.05)
                        & (subset[model + "_ratio"] > 1.05)
                    ).sum()
                ),
            }
    frame.to_csv(
        ROOT
        / f"notes/ompf/comparisons{output_suffix}_{mode}_h{spacing}_seed{seed}.csv",
        index=False,
    )
    (
        ROOT / f"notes/ompf/metrics{output_suffix}_{mode}_h{spacing}_seed{seed}.json"
    ).write_text(json.dumps(metrics, indent=2) + "\n")
    return frame, metrics


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="nonlinear_pb")
    p.add_argument("--spacing", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--compare-only", action="store_true")
    p.add_argument("--trimer", action="store_true")
    p.add_argument("--allow-subset", action="store_true")
    p.add_argument("--directory", type=Path)
    p.add_argument("--tag", default="")
    p.add_argument("--variants", nargs="+")
    args = p.parse_args()
    if not args.compare_only:
        calculate(args.mode, args.spacing, args.seed, args.trimer, args.variants)
    frame, metrics = compare(
        args.mode,
        args.spacing,
        args.seed,
        args.trimer,
        args.allow_subset,
        args.directory,
        args.tag,
    )
    print(json.dumps(metrics, indent=2))
