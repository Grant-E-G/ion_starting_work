"""Numerical and provenance checks for accelerated component experiments."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from Bio.PDB import PDBIO, PDBParser
from components import CACHE, ROOT, WW, dynamics, mpnn
from independent import inputs

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "predictive"))
from data import DATA, load_bedbrook, sha


def test_transfer_scale_sign_and_units() -> None:
    assert WW["D"] > WW["A"] > WW["I"]
    assert np.isclose(WW["A"] - WW["I"], 1.62)
    assert WW["W"] < WW["F"]


def test_gnm_rigid_transform_and_conservation() -> None:
    coords = np.array([[i * 3.0, (i % 2) * 1.0, 0.0] for i in range(8)])
    rotation = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    f, a = dynamics(coords)
    g, b = dynamics(coords @ rotation + 12.0)
    assert a["modes"] == b["modes"] == 7
    np.testing.assert_allclose(f, g, rtol=1e-10, atol=1e-10)
    assert a["row_sum_max"] == 0.0


def test_mpnn_rigid_transform(tmp_path: Path) -> None:
    source = ROOT / "sources/predictive/raw/3UG9.pdb"
    structure = PDBParser(QUIET=True).get_structure("template", source)
    rotation = np.array(
        [[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32
    )
    for atom in structure.get_atoms():
        atom.transform(rotation, np.array([10.0, 20.0, 30.0]))
    writer = PDBIO()
    writer.set_structure(structure)
    target = tmp_path / "rotated.pdb"
    writer.save(str(target))
    seq, p, _ = mpnn("original", "A", source)
    seq2, q, _ = mpnn("rotated", "A", target)
    assert seq == seq2
    np.testing.assert_allclose(p, q, atol=2e-4, rtol=2e-4)


def test_chrimson_numbering_and_missingness() -> None:
    cases, audit = inputs()
    _, sequence, variants, _ = next(x for x in cases if x[0] == "chrimson")
    assert len(variants) == 17
    assert sum(v["missing"] for v in variants) == 2
    assert sum(v["gain"] for v in variants) == 2
    for v in variants:
        assert sequence[v["index"]] == v["wt"]
    assert sequence[audit["chrimson"]["author_to_sequence_index0"][176]] == "R"
    # Deposited sequence indices differ from author numbering; direct index use is invalid.
    assert audit["chrimson"]["author_to_sequence_index0"][300] != 299


def test_independent_stability_references() -> None:
    cases, audit = inputs()
    assert audit["pagp"]["template_residue"] == "V"
    assert audit["pagp"]["experimental_reference"] == "A"
    for name, sequence, variants, _ in cases[:2]:
        assert len(variants) == (18 if name == "ompla" else 19)
        assert all(sequence[v["index"]] == "A" for v in variants)
        assert not any(v["alt"] == "A" for v in variants)


def test_old_partitions_and_embedding_alignment() -> None:
    freeze = json.loads((DATA / "freeze.json").read_text())
    assert sha(DATA / "partitions.csv") == freeze["partition_sha256"]
    bed, _ = load_bedbrook()
    path = ROOT / "notes/accelerated/esm1v_bed_embeddings.npz"
    if path.exists():
        with np.load(path) as f:
            assert np.array_equal(f["ids"], bed.id)
            assert f["esm"].shape == (154, 1280)
            assert np.isfinite(f["esm"]).all()


def test_bk_censor_flags_and_strict_site_groups() -> None:
    import pandas as pd

    data = pd.read_csv(CACHE / "bk_data_scores.csv")
    parts = pd.read_csv(ROOT / "sources/accelerated/bk_partitions.csv")
    assert len(data) == 473 and not data.Mutation.duplicated().any()
    assert int(((data["dV[Ca0]"] <= -370) | (data["dV[Ca0]"] >= 300)).sum()) == 28
    p = parts[parts.protocol == "site"]
    groups = [
        set(p.loc[p.split == name, "group"]) for name in ["train", "validation", "test"]
    ]
    assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
    config = json.loads((ROOT / "sources/accelerated/bk_policy.json").read_text())
    assert not any(c.startswith("cov") for c in config["energy_columns"])
    assert "dV[Ca0]" not in config["energy_columns"]
