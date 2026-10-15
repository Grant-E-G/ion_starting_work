"""Label-blind falsification of local energy crop sensitivity, not model tuning."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import subprocess
import time

import numpy as np
import pandas as pd
from data import DATA, OUT, load_bk, write_immutable
from energy import bk_variant
from scipy.stats import spearmanr


def main() -> None:
    frame = load_bk()
    frame["order"] = frame.id.map(
        lambda value: hashlib.sha256(f"crop-sensitivity:{value}".encode()).hexdigest()
    )
    tokens = []
    for region in [frame.resN <= 350, frame.resN > 350]:
        tokens.extend(
            frame[region]
            .sort_values("order")
            .drop_duplicates("resN")
            .head(12)
            .id.tolist()
        )
    policy = {
        "mutants": tokens,
        "selection": "First12 distinct sites per TM/CTD region after label-blind SHA256 order, no functional label consulted",
        "radii_A": [12, 20, 28],
        "hypothesis": "Matched local open-minus-closed mutation energies should remain reasonably stable as the artificial environment boundary moves",
        "interpretation": "Numerical sensitivity, not a new functional test or permission to tune radius against held-out mutants",
    }
    write_immutable(
        DATA / "energy_crop_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    rows, resources, failures = [], [], []
    for radius in policy["radii_A"]:
        start = time.perf_counter()

        def run(token: str, radius: float = float(radius)) -> dict | None:
            try:
                return bk_variant(token, radius)
            except (subprocess.SubprocessError, OSError, ValueError) as error:
                failures.append(
                    {
                        "mutation": token,
                        "radius_A": radius,
                        "error": str(error),
                        "interpretation": "Implementation/input failure, not a physical prediction",
                    }
                )
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            values = [value for value in pool.map(run, tokens) if value is not None]
        for value in values:
            rows.append({"radius_A": radius, **value})
        resources.append(
            {
                "radius_A": radius,
                "mutants": len(tokens),
                "seconds": time.perf_counter() - start,
                "workers": 2,
                "cache_used": radius == 20,
            }
        )
        print(radius, resources[-1], flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "energy_crop_features.csv", index=False)
    comparisons = []
    for radius in [12, 28]:
        first = table[table.radius_A == 20].set_index("mutation")
        second = table[table.radius_A == radius].set_index("mutation")
        common = first.index.intersection(second.index)
        first, second = first.loc[common], second.loc[common]
        for key in [
            column for column in table if column.startswith("state_difference_")
        ]:
            p, q = first[key].to_numpy(), second[key].to_numpy()
            comparisons.append(
                {
                    "radius_A": radius,
                    "paired_mutants": len(common),
                    "feature": key,
                    "spearman": (
                        float(spearmanr(p, q).statistic)
                        if np.std(p) > 0 and np.std(q) > 0
                        else None
                    ),
                    "absolute_change_RMS": float(np.sqrt(np.mean((p - q) ** 2))),
                    "reference_RMS": float(np.sqrt(np.mean(p**2))),
                    "sign_agreement": float((np.sign(p) == np.sign(q)).mean()),
                }
            )
    (OUT / "energy_crop_sensitivity.json").write_text(
        json.dumps(
            {
                "resources": resources,
                "failures": failures,
                "comparisons": comparisons,
                "units": "EvoEF2 weighted score units, not calibrated free energy",
                "scope": "24 label-blind mutant/site controls, no functional prediction or radius optimization",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
