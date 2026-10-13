"""Last constitutive sensitivity: fixed image maps with unfitted ion-volume bounds."""

from __future__ import annotations

from physics import ROOT, Config, run

if __name__ == "__main__":
    for volume in [0.03, 0.1]:
        for c in [1.0, 0.1]:
            for v in ["WT", "AAA", "EAE", "LEAE"]:
                field = (
                    ROOT
                    / f"notes/ompf/reaction/trimer_h0.15_s3/{v}_trimer_h0.15_s3.npz"
                )
                r = run(
                    v + "_trimer",
                    Config(
                        half_xy_nm=5.25,
                        concentration_M=c,
                        electrostatics="nonlinear_pb",
                        ion_volume_nm3=volume,
                    ),
                    output=ROOT / f"notes/ompf/combined/v{volume}",
                    self_energy_file=field,
                )
                print(
                    volume,
                    v,
                    c,
                    r["predictions"]["KCl"]["physics_nS"],
                    r["density_diagnostics"],
                    flush=True,
                )
