"""Falsifiable numerical and parameter checks; never optimize against mutant labels."""

from __future__ import annotations

import argparse
from dataclasses import replace
from typing import Any, cast

from physics import ROOT, Config, run

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=["mesh", "parameters"], default="mesh")
    args = p.parse_args()
    out = ROOT / "notes/ompf" / args.kind
    if args.kind == "mesh":
        for spacing in [0.10, 0.075, 0.05]:
            for c in [1.0, 0.1]:
                for variant in ["WT", "AAA", "EAE", "LEAE", "E117C", "D312N"]:
                    config = Config(
                        spacing_nm=spacing,
                        concentration_M=c,
                        electrostatics="nonlinear_pb",
                    )
                    result = run(variant, config, output=out)
                    print(
                        variant,
                        c,
                        spacing,
                        result["seconds"],
                        result["predictions"]["KCl"]["physics_nS"],
                        flush=True,
                    )
    else:
        configs = [
            ("protein_dielectric_8", {"epsilon_protein": 8.0}),
            ("ion_radius_0075", {"ion_radius_nm": 0.075}),
            ("ion_radius_0125", {"ion_radius_nm": 0.125}),
            ("aperture_12", {"aperture_radius_nm": 1.2}),
            ("aperture_15", {"aperture_radius_nm": 1.5}),
            ("membrane_12", {"membrane_half_nm": 1.2}),
            ("membrane_18", {"membrane_half_nm": 1.8}),
            ("domain_larger", {"half_xy_nm": 3.75, "half_z_nm": 4.65}),
        ]
        for name, changes in configs:
            for c in [1.0, 0.1]:
                for variant in ["WT", "AAA", "EAE", "LEAE", "E117C", "D312N"]:
                    config = replace(
                        Config(concentration_M=c, electrostatics="nonlinear_pb"),
                        **cast(dict[str, Any], changes),
                    )
                    result = run(variant, config, output=out / name)
                    print(
                        name,
                        variant,
                        c,
                        result["seconds"],
                        result["predictions"]["KCl"]["physics_nS"],
                        flush=True,
                    )
