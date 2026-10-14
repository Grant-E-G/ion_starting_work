"""Does an executed membrane-placement method improve an old-panel predictor?

Projection of residue transfer preferences into inferred membrane zones. This is
not a mutant MemPrO energy or a transport/gating simulation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from compare import predict
from components import OUT, WW, mapping, template

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "predictive"))
from benchmark import features_for, precision_at_k
from data import DATA, load_bedbrook


def main() -> None:
    bed, _ = load_bedbrook()
    text = (OUT / "mempro_12_150/Rank_1/info_rank_1.txt").read_text().splitlines()
    start = next(
        i for i, s in enumerate(text) if s.startswith("Transmembrane residues")
    )
    sequence, zone = text[start + 1 : start + 3]
    assert len(sequence) == len(zone)
    aligned = str(bed[bed.id == "C1C2"].iloc[0].seq)
    ref = aligned.replace("-", "")
    columns = [i for i, a in enumerate(aligned) if a != "-"]
    match = mapping(ref, sequence)
    _, _, pdb_sequence, _, exposure = template("3UG9")
    assert pdb_sequence == sequence
    rows = []
    for r in bed.itertuples():
        values = np.zeros(4)
        for i, j in match.items():
            a = r.seq[columns[i]]
            if a not in WW:
                continue
            delta = WW[a] - WW[ref[i]]
            tm = float(zone[j] == "T")
            values += np.array(
                [
                    delta * tm * exposure[j],
                    delta * (1 - tm) * exposure[j],
                    float(a in "DEKR") * tm * exposure[j],
                    float(a in "FWY") * tm * exposure[j],
                ]
            )
        rows.append(values / max(len(match), 1))
    x = np.array(rows)
    parts = pd.read_csv(DATA / "partitions.csv")
    p = parts[
        (parts.protocol == "bedbrook_temporal") & (parts.dataset == "bedbrook_current")
    ].set_index("id")
    split = bed.id.map(p.split).to_numpy()
    y = bed.score.to_numpy()
    tau = bed.kinetics_off_y.to_numpy()
    known = np.isfinite(tau) & (tau > 0)
    cap = bed[bed.control].kinetics_off_y.max()
    gain = y > 1.2 * bed[bed.control].score.max()
    joint = gain & known & (tau <= cap)
    train = (split == "train") & known
    val = (split == "validation") & known
    test = (split == "test") & known
    esm = features_for(bed, "bedbrook_current")["esm"]
    table = []
    preds: list[dict] = []
    for name, features in [
        ("membrane_projection", x),
        ("esm", esm),
        ("esm_membrane_projection", np.c_[esm, x]),
    ]:
        predicted, alpha = predict(features, y, train, val, test, joint)
        table.append(
            {
                "method": name,
                "n": int(test.sum()),
                "current_P20": precision_at_k(predicted, gain[test], 20),
                "joint_P20": precision_at_k(predicted, joint[test], 20),
                "mae": float(np.mean(abs(predicted - y[test]))),
                "alpha": alpha,
            }
        )
        preds.extend(
            {"method": name, "id": ident, "prediction": pp}
            for ident, pp in zip(bed.id[test], predicted)
        )
    pd.DataFrame(table).to_csv(OUT / "membrane_ablation_metrics.csv", index=False)
    pd.DataFrame(preds).to_csv(OUT / "membrane_ablation_predictions.csv", index=False)
    (OUT / "membrane_projection_audit.json").write_text(
        json.dumps(
            {
                "mapped": len(match),
                "membrane_zone_residues": zone.count("T"),
                "scope": "WT monomer zone and exposure projection only; no relaxed mutant energies; old inspected test; validation has no joint positives",
            },
            indent=2,
        )
        + "\n"
    )
    print(pd.DataFrame(table).to_string(index=False))


if __name__ == "__main__":
    main()
