"""Audited functional rows and immutable label-blind partitions, before model fitting."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import seq1
from scipy.sparse.csgraph import connected_components
from scipy.spatial.distance import pdist, squareform

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "sources/predictive/raw"
OUT = ROOT / "notes/predictive"
DATA = ROOT / "sources/predictive"
AA = "ACDEFGHIKLMNPQRSTVWY"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_label_source(path: Path) -> None:
    manifest = json.loads((DATA / "source_manifest.json").read_text())
    relative = str(path.relative_to(ROOT))
    expected = manifest["source_labels"].get(relative)
    if expected is None:
        expected = next(
            item["sha256"]
            for item in manifest["resources"]
            if item["name"] == path.name
        )
    assert sha(path) == expected, f"Refusing changed source labels: {path}"


def kir_reference() -> tuple[str, str]:
    tagged = str(Seq((RAW / "kir_dna.fa").read_text().strip()).translate())
    native = str(next(SeqIO.parse(RAW / "kir_P35561.fasta", "fasta")).seq)
    assert tagged[:115] + tagged[123:] == native
    assert tagged[115:123] == "DYKDDDDK"
    return tagged, native


def load_kir() -> tuple[pd.DataFrame, dict]:
    tagged, native = kir_reference()
    frames = []
    audit = {}
    for endpoint in ["function", "surface"]:
        source = ROOT / f"sources/nearby_modeling/kir2_{endpoint}_mod.csv"
        verify_label_source(source)
        frame = pd.read_csv(source)
        frame["alt"] = frame.mutation.map(seq1)
        frame["tagged_position"] = frame.position.astype(int)
        frame["wt"] = [tagged[p - 1] for p in frame.position]
        frame["position"] = np.where(
            frame.position > 123, frame.position - 8, frame.position
        )
        tag = frame.tagged_position.between(116, 123)
        controls = frame[(frame.wt == frame.alt) & ~tag]
        anchor = float(controls[endpoint + "_score"].median())
        frame["score"] = frame[endpoint + "_score"] - anchor
        frame["se"] = frame[endpoint + "_SE"]
        frame["control"] = (frame.wt == frame.alt) & ~tag
        frame = frame[~tag].copy()
        frame["id"] = [
            f"{w}{p}{m}" for w, p, m in zip(frame.wt, frame.position, frame.alt)
        ]
        frame["dataset"] = "kir_" + endpoint
        frame["sequence"] = ""
        assert all(native[p - 1] == w for p, w in zip(frame.position, frame.wt))
        assert not frame.id.duplicated().any()
        audit[endpoint] = {
            "raw_rows": len(pd.read_csv(source)),
            "excluded_flag_rows": int(tag.sum()),
            "same_amino_acid_controls": len(controls),
            "control_median": anchor,
            "control_score_sd": float(controls[endpoint + "_score"].std()),
            "nonsynonymous_rows": int((~frame.control).sum()),
            "independent_mutation_sites": int(frame[~frame.control].position.nunique()),
            "source_sha256": sha(source),
            "native_sequence_length": len(native),
            "tagged_sequence_length": len(tagged),
        }
        frames.append(
            frame[
                [
                    "dataset",
                    "id",
                    "position",
                    "tagged_position",
                    "wt",
                    "alt",
                    "score",
                    "se",
                    "control",
                    "sequence",
                ]
            ]
        )
    return pd.concat(frames, ignore_index=True), audit


def load_bedbrook() -> tuple[pd.DataFrame, dict]:
    source = ROOT / "sources/nearby_modeling/bedbrook2019_data2.csv"
    verify_label_source(source)
    verify_label_source(RAW / "bedbrook_ephys.csv")
    publisher = pd.read_csv(source)
    publisher["id"] = publisher.ChR_name.str.split(" ").str[0]
    author = pd.read_csv(RAW / "bedbrook_ephys.csv")
    frame = publisher.merge(
        author, left_on="id", right_on="chimera", validate="one_to_one"
    )
    assert len(frame) == len(publisher) == 154
    assert (frame.Aligned_amino_acid_sequence == frame.seq).all()
    assert np.max(abs(frame["max_peak (nA)"] - frame.max_peak)) <= 0.0051
    frame["control"] = frame.id.isin(["C1C2", "CsChrim", "CheRiff"])
    reference = float(frame[frame.control].max_peak.max())
    frame["score"] = frame.max_peak
    frame["se"] = np.nan  # Cell counts are not standard errors.
    frame["sequence"] = frame.seq.str.replace("-", "", regex=False)
    assert frame.sequence.nunique() == len(frame)
    frame["dataset"] = "bedbrook_current"
    frame["position"] = -1
    audit = {
        "measured_sequences": len(frame),
        "independent_sequences": frame.sequence.nunique(),
        "rounds": frame.groupby("gen").size().to_dict(),
        "reference_best_parent_nA": reference,
        "gain_threshold_nA": 1.2 * reference,
        "unrounded_author_labels": True,
        "maximum_rounding_difference_nA": float(
            np.max(abs(frame["max_peak (nA)"] - frame.max_peak))
        ),
        "excluded_data3": "1133 model-predicted designs are not measured labels",
        "excluded_data4": "label-selected feature weights are not used to choose features",
        "source_sha256": sha(source),
        "author_table_sha256": sha(RAW / "bedbrook_ephys.csv"),
    }
    return frame, audit


def prepare() -> None:
    OUT.mkdir(exist_ok=True)
    kir, ka = load_kir()
    bed, ba = load_bedbrook()
    rows = []
    for name in ["kir_site_hash", "kir_contiguous"]:
        for r in kir.itertuples():
            if r.control:
                split = "reference"
            elif name == "kir_site_hash":
                bucket = (
                    int(
                        hashlib.sha256(
                            f"C5R-20261013:{r.position}".encode()
                        ).hexdigest()[:8],
                        16,
                    )
                    % 10
                )
                split = (
                    "train" if bucket < 6 else "validation" if bucket < 8 else "test"
                )
            else:
                split = (
                    "train"
                    if r.position <= 195
                    else "validation" if r.position <= 293 else "test"
                )
            rows.append(
                {
                    "protocol": name,
                    "dataset": r.dataset,
                    "id": r.id,
                    "group": str(r.position) if not r.control else "WT_reference",
                    "split": split,
                }
            )
    encoded = np.array([[ord(x) for x in s] for s in bed.seq])
    distances = squareform(pdist(encoded, metric="hamming"))
    _, groups = connected_components(distances <= 0.10, directed=False)
    counts = sorted([(int((groups == g).sum()), g) for g in set(groups)], reverse=True)
    group_split = {g: "validation" for _, g in counts}
    group_split[counts[0][1]] = "train"
    group_split[counts[1][1]] = "test"
    for name in [
        "bedbrook_temporal",
        "bedbrook_temporal_purge95",
        "bedbrook_cluster90",
    ]:
        train = bed.gen <= 2
        val = bed.gen.between(4, 7)
        test = bed.gen >= 9
        for i, r in enumerate(bed.itertuples()):
            split = (
                "train" if train.iloc[i] else "validation" if val.iloc[i] else "test"
            )
            if (
                name == "bedbrook_temporal_purge95"
                and split != "test"
                and (
                    distances[i, test].min() <= 0.05
                    or (split == "train" and distances[i, val].min() <= 0.05)
                )
            ):
                split = "purged"
            if name == "bedbrook_cluster90":
                split = group_split[groups[i]]
            if r.control:
                split = "reference"
            rows.append(
                {
                    "protocol": name,
                    "dataset": "bedbrook_current",
                    "id": r.id,
                    "group": (
                        f"component90_{groups[i]}"
                        if name.endswith("cluster90")
                        else r.id
                    ),
                    "split": split,
                }
            )
    partitions = pd.DataFrame(rows)
    path = DATA / "partitions.csv"
    content = partitions.to_csv(index=False)
    if path.exists():
        assert path.read_text() == content, "Refusing to modify frozen partitions"
    else:
        path.write_text(content)
    config = {
        "timestamp_UTC": datetime.now(timezone.utc).isoformat(),
        "partition_sha256": sha(path),
        "policy": "Retrospective computational holdout frozen before model tuning; not new prospective experiments. All repeated construct observations stay together.",
        "kir_gain": "Score minus pooled same-AA reference median >0.3; conservative label additionally score-1.96*reportedSE>0.3. Assay-score improvement, not necessarily therapeutic benefit.",
        "bedbrook_gain": "Max measured peak photocurrent >1.2 times best measured parent; recombination variants, not isolated point mutations.",
        "label_policy": "Measured surface score never used as function input; paired surface labels for post-evaluation confound diagnostics only.",
        "model_plan": {
            "ridge_alpha": [1.0, 10.0, 100.0],
            "gp_length": [0.5, 1.0, 2.0],
            "gp_noise": [0.03, 0.15],
            "selection": "Validation MAE; no test-label hyperparameter selection",
            "uncertainty": "Validation residual intervals and GP variance are assessed empirically; selection/refit effects mean no automatic calibrated confidence guarantee",
        },
        "primary_metrics": [
            "ratio_or_score_MAE",
            "Spearman",
            "precision_at_10",
            "precision_at_20",
            "gain_enrichment",
            "robust_gain_precision",
            "gain_recall",
        ],
        "reference_policy": "Same-AA Kir controls and three Bedbrook parents are reserved reference/calibration observations, never split as different independent mutants.",
    }
    freeze = DATA / "freeze.json"
    if not freeze.exists():
        freeze.write_text(json.dumps(config, indent=2) + "\n")
    assert json.loads(freeze.read_text())["partition_sha256"] == sha(path)
    audit = {
        "kir": ka,
        "bedbrook": ba,
        "partition_counts": partitions.groupby(["protocol", "dataset", "split"])
        .size()
        .reset_index(name="rows")
        .to_dict("records"),
    }
    (OUT / "dataset_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    prepare()
