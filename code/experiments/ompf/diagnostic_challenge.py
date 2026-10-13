"""Reproduce separately audited state challenge; excluded from scalar score tables."""

from __future__ import annotations

import argparse
from dataclasses import replace

from physics import ROOT, Config, run
from prepare import prepare
from reaction import calculate

DIAGNOSTIC_MUTATIONS = {"D127N": "D127N", "D127K": "D127K", "NQRRR": "D113N/E117Q"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trimer", action="store_true")
    parser.add_argument("--platform", choices=["CPU", "CUDA"], default="CUDA")
    parser.add_argument("--backend", choices=["cpu", "cuda", "cuda32"], default="cpu")
    args = parser.parse_args()
    config = Config(
        half_xy_nm=5.25 if args.trimer else 3.15, electrostatics="nonlinear_pb"
    )
    directory = ROOT / (
        "notes/ompf/reaction/state_challenge_trimer"
        if args.trimer
        else "notes/ompf/reaction/state_challenge"
    )
    for variant, mutations in DIAGNOSTIC_MUTATIONS.items():
        if args.trimer and variant == "NQRRR":
            continue
        name = variant + ("_trimer" if args.trimer else "")
        if not (ROOT / f"sources/ompf/prepared/{name}_seed0.npz").exists():
            prepare(name, mutations, 0, trimer=args.trimer, platform_name=args.platform)
        concentration = 1.0 if variant == "NQRRR" else 0.1
        cfg = replace(config, concentration_M=concentration)
        image = directory / f"{name}_h0.15_s3.npz"
        if not image.exists():
            calculate(name, config, 3, directory, backend=args.backend)
        for model, energy in [("ordinary", None), ("image", image)]:
            prediction = (
                directory
                / model
                / f"{name}_c{concentration}_h0.15_nonlinear_pb_seed0.json"
            )
            if not prediction.exists():
                run(name, cfg, output=directory / model, self_energy_file=energy)
        print("Cached challenge", name)
