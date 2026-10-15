"""Fixed-prediction site-cluster uncertainty, diversity and structure-confidence.

These are conditional retrospective diagnostics, not calibrated prospective CIs.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from data import OUT, RAW
from metrics import precision_at_k, site_diverse_precision


def paired_interval(
    a: np.ndarray, b: np.ndarray, target: np.ndarray, site: np.ndarray
) -> list[float]:
    rng = np.random.RandomState(1729)
    unique = np.unique(site)
    members = [np.flatnonzero(site == value) for value in unique]
    values = []
    for _ in range(1000):
        index = np.concatenate(
            [members[i] for i in rng.randint(len(members), size=len(members))]
        )
        values.append(
            precision_at_k(a[index], target[index], 20)
            - precision_at_k(b[index], target[index], 20)
        )
    bounds: np.ndarray = np.asarray(np.quantile(values, [0.025, 0.5, 0.975]))
    return bounds.tolist()


def main() -> None:
    frame = pd.read_csv(OUT / "kir_transfer_measurements.csv").set_index("id")
    structure = PDBParser(QUIET=True).get_structure("WT", RAW / "kir_af.pdb")[0]["A"]
    confidence = {r.id[1]: float(r["CA"].bfactor) for r in structure}
    summaries = []
    contrasts = []
    pairs = [
        ("esm650_global3d_attributes_ridge", "esm1v_650m_ridge"),
        ("global3d_attributes_ridge", "WTgeometry_chemistry_ridge"),
        ("global3d_attributes_ridge", "global1d_attributes_ridge"),
        ("global3d_attributes_ridge", "global3d_attributes_shuffled_within_site_ridge"),
    ]
    for method, filename in [
        ("regression", "kir_transfer_predictions.csv"),
        ("classification", "kir_classifier_predictions.csv"),
    ]:
        path = OUT / filename
        if not path.exists():
            continue
        data = pd.read_csv(path)
        for (protocol, budget), block in data.groupby(["protocol", "budget"]):
            lookup = {}
            for name, part in block.groupby("features"):
                part = part.set_index("id")
                truth = frame.loc[part.index]
                score = (
                    part.joint_score.to_numpy()
                    if method == "regression"
                    else part.score.to_numpy()
                )
                target = truth.joint_gain.to_numpy()
                supported = truth.supported_joint_gain.to_numpy()
                sites = truth.position.to_numpy()
                quality = np.array([confidence[value] for value in sites])
                lookup[name] = (part.index, score, target, supported, sites)
                for label, mask in [
                    ("all", np.ones(len(part), bool)),
                    ("pLDDT_at_least70", quality >= 70),
                    ("pLDDT_below70", quality < 70),
                ]:
                    if mask.sum() < 20:
                        continue
                    summaries.append(
                        {
                            "method": method,
                            "protocol": protocol,
                            "budget": budget,
                            "features": name,
                            "subset": label,
                            "n": int(mask.sum()),
                            "sites": len(np.unique(sites[mask])),
                            "point_joint_prevalence": float(target[mask].mean()),
                            "point_joint_P20": precision_at_k(
                                score[mask], target[mask], 20
                            ),
                            "point_joint_site_diverse_P10": site_diverse_precision(
                                score[mask], target[mask], sites[mask], 10
                            ),
                            "supported_prevalence": float(supported[mask].mean()),
                            "supported_P20": precision_at_k(
                                score[mask], supported[mask], 20
                            ),
                            "supported_site_diverse_P10": site_diverse_precision(
                                score[mask], supported[mask], sites[mask], 10
                            ),
                        }
                    )
            actual_pairs = (
                pairs
                if method == "regression"
                else [
                    (a.replace("_ridge", "_logistic"), b.replace("_ridge", "_logistic"))
                    for a, b in pairs
                ]
            )
            for first, second in actual_pairs:
                if first not in lookup or second not in lookup:
                    continue
                ids, a, target, supported, site = lookup[first]
                other, b, _, _, _ = lookup[second]
                assert ids.equals(
                    other
                ), "Prediction row order must match for paired uncertainty"
                for label, truth in [
                    ("point_joint_gain", target),
                    ("SE_supported_joint_gain", supported),
                ]:
                    contrasts.append(
                        {
                            "method": method,
                            "protocol": protocol,
                            "budget": budget,
                            "first": first,
                            "second": second,
                            "label": label,
                            "test_n": len(a),
                            "sites": len(np.unique(site)),
                            "P20_first": precision_at_k(a, truth, 20),
                            "P20_second": precision_at_k(b, truth, 20),
                            "difference95_cluster_interval": paired_interval(
                                a, b, truth, site
                            ),
                        }
                    )
    pd.DataFrame(summaries).to_csv(OUT / "kir_selection_diagnostics.csv", index=False)
    result = {
        "comparisons": contrasts,
        "scope": "1000paired native-site bootstrap samples of fixed predictions; no refitting or adjustment for many model comparisons; not a prospective uncertainty guarantee. Score-SE filters omit full control/assay uncertainty. Confidence bins fixed atAFpLDDT70, not tuned to gains.",
    }
    (OUT / "kir_physics_uncertainty.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(len(summaries), "diagnosticrows", len(contrasts), "pairedintervals")


if __name__ == "__main__":
    main()
