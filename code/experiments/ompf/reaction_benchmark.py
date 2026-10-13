"""Test the missing-self-energy hypothesis separately from the original model."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace

from physics import ROOT, Config, run
from reaction import calculate

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--trimer", action="store_true")
    p.add_argument("--stride", type=int, default=3)
    p.add_argument("--spacing", type=float, default=0.15)
    p.add_argument("--variants", nargs="+")
    p.add_argument("--backend", choices=["cpu", "cuda", "cuda32"], default="cpu")
    p.add_argument("--label", default="")
    args = p.parse_args()
    variants = json.loads((ROOT / "sources/ompf/variants.json").read_text())
    if args.variants:
        variants = {v: variants[v] for v in args.variants}
    directory = (
        ROOT
        / f'notes/ompf/reaction/{"trimer" if args.trimer else "monomer"}_h{args.spacing}_s{args.stride}'
    )
    if args.label:
        directory = directory.with_name(directory.name + "_" + args.label)
    config = Config(
        spacing_nm=args.spacing,
        half_xy_nm=5.25 if args.trimer else 3.15,
        electrostatics="nonlinear_pb",
    )
    for v in variants:
        name = v + ("_trimer" if args.trimer else "")
        field = directory / f"{name}_h{args.spacing}_s{args.stride}.npz"
        if not field.exists():
            print(
                json.dumps(
                    {
                        k: v
                        for k, v in calculate(
                            name, config, args.stride, directory, backend=args.backend
                        ).items()
                        if k != "batches"
                    }
                ),
                flush=True,
            )
        for c in [1.0, 0.1]:
            target = (
                directory
                / "predictions"
                / f"{name}_c{c}_h{args.spacing}_nonlinear_pb_seed0.json"
            )
            if target.exists():
                continue
            r = run(
                name,
                replace(config, concentration_M=c),
                output=directory / "predictions",
                self_energy_file=field,
            )
            print(name, c, r["predictions"], flush=True)
