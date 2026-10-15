"""Scientific failure checks: grouping, scoring, mutation maps and energetics."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bk_audit import ENERGY_COLUMNS, PUBLISHED_COLUMNS
from data import (
    DATA,
    RAW,
    constants,
    load_bk,
    load_vep,
    publication_components,
    vep_split,
)
from energy import ENGINE, score
from metrics import grouped_bootstrap, precision_at_k, site_diverse_precision
from vep import adjacency, integer_sequences, lookups


def test_tie_precision_and_direction() -> None:
    assert precision_at_k(
        np.zeros(10), np.array([True] * 3 + [False] * 7), 5
    ) == pytest.approx(0.3)
    assert precision_at_k(np.arange(10), np.array([False] * 8 + [True] * 2), 2) == 1
    assert precision_at_k(-np.arange(10), np.array([True] * 2 + [False] * 8), 2) == 1


def test_publication_transitive_closure() -> None:
    groups, _ = publication_components(pd.Series(["1, 2", "2, 3", "3, 4", "5"]))
    assert groups[0] == groups[1] == groups[2] != groups[3]


def test_site_diversity_null_and_ties() -> None:
    sites = np.array([1, 1, 1, 2])
    positives = np.array([True, False, False, True])
    assert site_diverse_precision(np.zeros(4), positives, sites, 2) == pytest.approx(
        2 / 3
    )
    assert site_diverse_precision(np.arange(4), positives, sites, 1) == 1


def test_bk_outer_partitions() -> None:
    frame = load_bk()
    assert frame.censored.sum() == 28
    parts = pd.read_csv(DATA / "bk_partitions.csv")
    for _, rows in parts.groupby(["protocol", "seed"]):
        assert rows.id.is_unique and set(rows.id) == set(frame.id)
        assert rows.groupby("group").split.nunique().max() == 1
    for _, rows in parts.groupby("protocol"):
        assert rows[rows.split == "test"].id.value_counts().eq(1).all()


@pytest.mark.parametrize("name", ["pab1", "avgfp"])
def test_vep_strict_group_exclusion(name: str) -> None:
    frame, sequence, offset = load_vep(name)
    for protocol in ["site", "mutation"]:
        split = vep_split(frame, name, protocol, 42, offset)
        groups = {}
        for part in ["train", "validation", "test"]:
            selected = frame[split == part]
            groups[part] = (
                {p for ms in selected.parsed for _, p, _ in ms}
                if protocol == "site"
                else {m for v in selected.id for m in v.split(",")}
            )
        assert not groups["train"] & groups["test"]
        assert not groups["validation"] & groups["test"]
        assert not groups["train"] & groups["validation"]
    values = integer_sequences(frame.head(10), sequence, offset)
    assert values.shape == (10, len(sequence))


def test_energy_lookup_mutation_numbering_and_null() -> None:
    frame, sequence, offset = load_vep("pab1")
    lookup, rmsf, present = lookups("pab1")
    table = pd.read_csv(RAW / "VEP/data/pab1/ddG.tsv", sep="\t")
    aa = "ACDEFGHIKLMNPQRSTVWY"
    for row in table.itertuples(index=False, name=None):
        token = row[-1]
        index = int(token[1:-1]) - offset
        assert sequence[index] == token[0]
        assert np.allclose(lookup["rosetta"][index, aa.index(token[-1])], row[:-1])
        assert present[index, aa.index(token[-1])]
    assert np.all(
        lookup["rosetta"][np.arange(len(sequence)), [aa.index(a) for a in sequence]]
        == 0
    )
    assert len(rmsf) == len(sequence)
    assert {m for v in frame.id for m in v.split(",")} <= set(table.mutation)


def test_graph_normalization() -> None:
    graph = adjacency("pab1")
    assert graph.shape == (len(constants()["pab1"]["wt_aa"]),) * 2
    assert np.all(graph >= 0) and np.allclose(np.diag(graph), 0)
    assert np.allclose(graph.sum(axis=1), 1)


def test_paired_bootstrap_identity() -> None:
    y: np.ndarray = np.arange(40).astype(float)
    result = grouped_bootstrap(
        y, y, y, np.repeat(np.arange(10), 4), 30, 1, repetitions=100
    )
    assert result["P20_difference_interval"] == [0, 0, 0]
    assert result["RMSE_difference_interval"] == [0, 0, 0]


def test_published_evoef_energy_accounting(tmp_path: Path) -> None:
    source = RAW / "VEP/data/pab1/pab1_rosetta_model.pdb"
    first, second = score(source, tmp_path), score(source, tmp_path)
    assert first == second
    # The executable prints each component rounded to 0.01 units.
    total = sum(value for key, value in first.items() if key != "Total")
    assert abs(first["Total"] - total) <= 0.5


def test_full_scans_and_exact_WT_null() -> None:
    frame = load_bk()
    scans = pd.concat(
        [pd.read_csv(path) for path in (RAW / "bkpred/data/scans").glob("*.csv")]
    ).set_index("Mutation")
    assert scans.index.is_unique
    assert np.array_equal(
        scans.loc[frame.id, PUBLISHED_COLUMNS].to_numpy(),
        frame[PUBLISHED_COLUMNS].to_numpy(),
    )
    native = scans.loc[[token[:-1] + token[0] for token in frame.id]]
    assert np.max(abs(native[ENERGY_COLUMNS].to_numpy())) == 0


def test_independent_GPCR_grouping_and_reference() -> None:
    from data import OUT

    frame = pd.read_csv(OUT / "adrb2_measurements.csv")
    assert frame.id.is_unique and frame.groupby("site").split.nunique().max() == 1
    assert not set(frame.loc[frame.split == "train", "site"]) & set(
        frame.loc[frame.split == "test", "site"]
    )
    audit = json.loads((OUT / "adrb2_data_audit.json").read_text())
    assert audit["normalization_error"] < 1e-10
    assert all(row["normalized_WT"] > 1.4 for row in audit["controls"])
    # Published scores normalized to frameshifts are not relative-to-WT scores.
    assert frame.loc[frame.joint_gain, "gain"].all()


def test_evoef_self_repacking_repeat_and_fixed_backbone(tmp_path: Path) -> None:
    from Bio.PDB import PDBParser
    from Bio.SeqUtils import seq1

    source = RAW / "VEP/data/pab1/pab1_rosetta_model.pdb"
    parser = PDBParser(QUIET=True)
    native = parser.get_structure("native", source)[0]
    chain = next(iter(native))
    first = next(r for r in chain if r.id[0] == " ")
    token = f"{seq1(first.resname)}{chain.id}{first.id[1]}{seq1(first.resname)};"
    mutations = tmp_path / "mutants.txt"
    mutations.write_text(token + "\n" + token + "\n")
    subprocess.run(
        [
            str(ENGINE),
            "--command=BuildMutant",
            f"--pdb={source}",
            f"--mutant_file={mutations}",
        ],
        cwd=tmp_path,
        capture_output=True,
        check=True,
        timeout=30,
    )
    models = sorted(tmp_path.glob("*_Model_*.pdb"))
    assert len(models) == 2 and score(models[0], tmp_path) == score(models[1], tmp_path)
    repacked = parser.get_structure("repacked", models[0])[0]
    for original in native.get_atoms():
        residue = original.parent
        if residue.id[0] == " " and original.name in ["N", "CA", "C", "O"]:
            replacement = repacked[residue.parent.id][residue.id][original.name]
            assert np.max(abs(original.coord - replacement.coord)) <= 0.0011


def test_evoef_long_directory_does_not_change_energy(tmp_path: Path) -> None:
    source = RAW / "VEP/data/pab1/pab1_rosetta_model.pdb"
    long = tmp_path / ("long_directory_" * 9)
    long.mkdir()
    assert len(str(long / source.name)) > 100
    assert score(source, tmp_path) == score(source, long)


def test_independent_gb1_uses_raw_measurements() -> None:
    source = pd.read_csv(RAW / "gb1_wu2016/result/Mutfit", sep="\t")
    valid = (
        source.mut.str.fullmatch("[ACDEFGHIKLMNPQRSTVWY]{4}") & source.I20fitRaw.notna()
    )
    frame = source[valid]
    wt = pd.read_csv(RAW / "gb1_wu2016/result/WTcount", sep="\t").iloc[0]
    expected = (frame.IGG20 / wt.IGG20) / (frame.Input / wt.Input)
    assert len(frame) == 149361 and np.allclose(frame.I20fitRaw, expected, atol=1e-10)
    # The processed single-mutant score reuses old-assay measurements; it must
    # never be mistaken for an independent experimental validation label.
    singles = frame[frame.HD == 1]
    assert not np.allclose(singles.I20fit, singles.I20fitRaw)
    partition = DATA / "gb1_transfer_training_partitions.csv"
    if partition.exists():
        rows = pd.read_csv(partition)
        assert len(rows) == 1256 and rows.id.is_unique
        for ident in rows.id:
            assert all(
                int(token[1:-1]) not in [38, 39, 40, 53] for token in ident.split(",")
            )


def test_zero_anchor_rejects_nearconstant_roundoff_features() -> None:
    from bk import select_model

    values = np.linspace(-1, 1, 24)
    x = np.column_stack([values, 3 + np.arange(24) * 1e-14])
    y = 2 * values
    train, validation = np.arange(18), np.arange(18, 24)
    model, choice = select_model(
        "ridge",
        x,
        y,
        train,
        validation,
        1729,
        anchor_zero=True,
        criterion="mse",
        stable_features=True,
    )
    p = model.predict(x[validation]) - model.predict(np.zeros((1, 2)))[0]
    assert np.max(abs(p - y[validation])) < 0.5
    assert choice["zero_anchor_validation"]
    assert model.named_steps["variancethreshold"].get_support().tolist() == [
        True,
        False,
    ]


def test_four_site_parent_lookup_ignores_token_order() -> None:
    frame, _, _ = load_vep("gb1")
    canonical = {
        ",".join(sorted(ident.split(","))): value
        for ident, value in zip(frame.id, frame.target, strict=True)
    }
    assert len(canonical) == len(frame)
    # Original tables sort these tokens by string, not residue number.
    assert "D39S,V38S" in canonical
    assert canonical[",".join(sorted(["V38S", "D39S"]))] == canonical["D39S,V38S"]
