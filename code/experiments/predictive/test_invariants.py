"""Leakage, numbering, and gain-selection invariants with meaningful failure cases."""

import numpy as np
import pandas as pd
from benchmark import precision_at_k
from data import DATA, kir_reference, load_bedbrook, load_kir


def test_null_ties_do_not_use_sorted_labels():
    gains = np.array([False] * 90 + [True] * 10)
    assert precision_at_k(np.zeros(100), gains, 10) == 0.1
    assert precision_at_k(np.zeros(100), gains[::-1], 10) == 0.1


def test_top_boundary_fractional_ties():
    assert np.isclose(
        precision_at_k(
            np.array([3.0, 2.0, 2.0, 1.0]), np.array([True, True, False, False]), 2
        ),
        0.75,
    )


def test_native_numbering_and_tag_exclusion():
    tagged, native = kir_reference()
    assert len(tagged) == len(native) + 8
    rows, audit = load_kir()
    assert not rows.tagged_position.between(116, 123).any()
    assert audit["function"]["nonsynonymous_rows"] == 6963
    assert audit["surface"]["nonsynonymous_rows"] == 6917
    assert all(native[p - 1] == w for p, w in zip(rows.position, rows.wt))


def test_partitions_disjoint_and_construct_unique():
    p = pd.read_csv(DATA / "partitions.csv")
    assert not p[["protocol", "dataset", "id"]].duplicated().any()
    for _, frame in p.groupby(["protocol", "dataset"]):
        a = set(frame[frame.split == "train"].group)
        b = set(frame[frame.split == "test"].group)
        assert not a.intersection(b)


def test_bedbrook_has_only_measured_unrounded_labels():
    rows, audit = load_bedbrook()
    assert len(rows) == 154
    assert audit["maximum_rounding_difference_nA"] <= 0.0051
    assert (rows.max_peak >= 0).all()


def test_tension_units_and_state_limits():
    from mscl import KT_PN_NM, state_current

    assert np.isclose(KT_PN_NM, 4.1164049935)
    assert np.allclose(state_current(np.zeros(3), np.zeros(3)), 0.3375)
    wt = state_current(np.array([45.6, 47.0, 52.0]), np.array([14.8, 15.7, 20.0]))
    assert wt[0] < 1e-18
    assert np.all(np.diff(wt) >= 0)
    assert wt[-1] > 0.99


def test_component_holdout_excludes_close_homologs():
    from scipy.spatial.distance import cdist

    rows, _ = load_bedbrook()
    part = pd.read_csv(DATA / "partitions.csv")
    part = part[part.protocol == "bedbrook_cluster90"].merge(rows, on=["dataset", "id"])
    a = np.array([[ord(c) for c in s] for s in part[part.split == "train"].seq])
    b = np.array([[ord(c) for c in s] for s in part[part.split == "test"].seq])
    assert cdist(a, b, metric="hamming").min() > 0.10


def test_original_mutation_headers_confirm_tagged_coordinate_system():
    import re

    from Bio.SeqUtils import seq1
    from data import RAW

    tagged, _ = kir_reference()
    headers = re.findall(
        r"_([A-Z]{3})(\d+)([A-Z]{3})", (RAW / "kir_mutations.fa").read_text()
    )
    assert len({int(p) for _, p, _ in headers}) == 394
    assert all(tagged[int(p) - 1] == seq1(w.title()) for w, p, _ in headers)
