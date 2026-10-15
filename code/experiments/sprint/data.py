"""Audited public-data loaders and label-blind, immutable grouped partitions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "sources/sprint"
RAW = DATA / "raw"
OUT = ROOT / "notes/sprint"
FEATURES = DATA / "features"
AA = "ACDEFGHIKLMNPQRSTVWY"
SEEDS = [10, 24, 36, 42, 56]


def constants() -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location(
        "vep_constants", RAW / "VEP/code/constants.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DATASETS


def mutations(variant: str) -> list[tuple[str, int, str]]:
    result = []
    for token in variant.split(","):
        match = re.fullmatch(r"([A-Z])(\d+)([A-Z])", token)
        if match is None:
            raise ValueError(f"Unsupported substitution: {token}")
        wt, position, alt = match.groups()
        if wt not in AA or alt not in AA or wt == alt:
            raise ValueError(f"Noncanonical or null substitution: {token}")
        result.append((wt, int(position), alt))
    assert len({p for _, p, _ in result}) == len(result)
    return result


def load_vep(name: str) -> tuple[pd.DataFrame, str, int]:
    info = constants()[name]
    sequence, offset = info["wt_aa"], info["wt_ofs"]
    frame = pd.read_csv(RAW / f"VEP/data/{name}/{name}.tsv", sep="\t")
    assert frame.variant.is_unique
    parsed = [mutations(v) for v in frame.variant]
    for ms, number in zip(parsed, frame.num_mutations, strict=True):
        assert len(ms) == number
        for wt, position, _ in ms:
            assert 0 <= position - offset < len(sequence)
            assert sequence[position - offset] == wt, (name, wt, position)
    frame["parsed"] = parsed
    frame["id"] = frame.variant
    # Do not silently call unspecified enrichment units "benefit over WT".
    # Only avGFP publishes a WT-normalized score in these exact tables.
    frame["target"] = frame.score_wt_norm if name == "avgfp" else frame.score
    assert np.isfinite(frame.target).all()
    return frame, sequence, offset


def load_bk() -> pd.DataFrame:
    old = ROOT / "sources/accelerated/raw"
    frame = pd.read_csv(old / "bk_data_scores.csv")
    source = pd.read_excel(
        old / "bk_data_BK_mutations.xlsx", sheet_name="training_data"
    ).dropna(subset=["Mutation"])
    frame = frame.merge(
        source[["Mutation", "Species", "Source(s)"]],
        on=["Mutation", "Species"],
        validate="one_to_one",
    )
    assert len(frame) == 473 and frame.Mutation.is_unique
    frame["id"] = frame.Mutation
    frame["parsed"] = [mutations(v) for v in frame.Mutation]
    frame["target"] = frame["dV[Ca0]"]
    frame["censored"] = (frame.target <= -370) | (frame.target >= 300)
    return frame


def publication_components(sources: pd.Series) -> tuple[list[str], list[list[str]]]:
    """Join whole source strings sharing any individual reference, transitively."""
    records = [set(re.findall(r"\d+", str(value))) for value in sources]
    assert all(records), "Missing publication identifiers"
    parent = {token: token for record in records for token in record}

    def find(token: str) -> str:
        while parent[token] != token:
            parent[token] = parent[parent[token]]
            token = parent[token]
        return token

    for record in records:
        first = min(record)
        for token in record:
            parent[find(token)] = find(first)
    groups: dict[str, list[str]] = {}
    for token in sorted(parent):
        groups.setdefault(find(token), []).append(token)
    names = {key: "+".join(sorted(tokens)) for key, tokens in groups.items()}
    return [names[find(min(record))] for record in records], list(groups.values())


def write_immutable(path: Path, content: str) -> None:
    manifest_path = DATA / "partition_hashes.json"
    if path.suffix == ".csv" and manifest_path.exists():
        expected = json.loads(manifest_path.read_text()).get(path.name)
        if expected is not None:
            assert (
                hashlib.sha256(content.encode()).hexdigest() == expected["sha256"]
            ), f"Partition hash mismatch: {path}"
    if path.exists():
        assert path.read_text() == content, f"Refusing to replace frozen {path}"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def prepare() -> None:
    OUT.mkdir(exist_ok=True)
    FEATURES.mkdir(exist_ok=True)
    rows: list[dict[str, Any]] = []
    audit: dict[str, Any] = {"vep": {}, "bk": {}}
    for name in constants():
        frame, sequence, offset = load_vep(name)
        unique = sorted({token for v in frame.variant for token in v.split(",")})
        for seed in SEEDS:
            for protocol, groups in [
                ("site", list(range(len(sequence)))),
                ("mutation", unique),
            ]:
                shuffled = np.random.RandomState(seed).permutation(len(groups))
                split: np.ndarray = np.full(len(groups), "train", dtype="U10")
                split[shuffled[int(0.70 * len(groups)) : int(0.85 * len(groups))]] = (
                    "validation"
                )
                split[shuffled[int(0.85 * len(groups)) :]] = "test"
                rows.extend(
                    {
                        "dataset": name,
                        "protocol": protocol,
                        "seed": seed,
                        "group": str(group),
                        "split": part,
                    }
                    for group, part in zip(groups, split, strict=True)
                )
        audit["vep"][name] = {
            "rows": len(frame),
            "sites": len(sequence),
            "offset": offset,
            "unique_substitutions": len(unique),
            "mutations": frame.num_mutations.value_counts().sort_index().to_dict(),
            "target": (
                "WT-normalized log fluorescence"
                if name == "avgfp"
                else "published enrichment/function score; WT threshold not independently verified"
            ),
        }
    group_frame = pd.DataFrame(rows)
    write_immutable(DATA / "vep_group_partitions.csv", group_frame.to_csv(index=False))
    bk = load_bk()
    pub, components = publication_components(bk["Source(s)"])
    bk_rows = []
    for protocol, groups in [
        ("site", bk.resN.astype(str).tolist()),
        ("publication_component", pub),
    ]:
        for fold, (fit, test) in enumerate(GroupKFold(5).split(bk, groups=groups)):
            local_groups = np.array(groups)[fit]
            train_local, val_local = next(
                GroupShuffleSplit(
                    n_splits=1, test_size=0.2, random_state=1729 + fold
                ).split(fit, groups=local_groups)
            )
            split = np.full(len(bk), "test", dtype="U10")
            split[fit[train_local]] = "train"
            split[fit[val_local]] = "validation"
            for ident, group, part in zip(bk.id, groups, split, strict=True):
                bk_rows.append(
                    {
                        "dataset": "bk",
                        "protocol": protocol,
                        "seed": fold,
                        "id": ident,
                        "group": group,
                        "split": part,
                    }
                )
    write_immutable(
        DATA / "bk_partitions.csv", pd.DataFrame(bk_rows).to_csv(index=False)
    )
    audit["bk"] = {
        "rows": len(bk),
        "uncensored": int((~bk.censored).sum()),
        "sites": bk.resN.nunique(),
        "publication_components": components,
        "component_sizes": pd.Series(pub).value_counts().to_dict(),
        "scope": "Near-zero-calcium signed gating shifts; not therapeutic benefit; mixed species/conditions",
    }
    (OUT / "data_audit.json").write_text(
        json.dumps(audit, indent=2, default=int) + "\n"
    )
    policy = {
        "seeds": SEEDS,
        "vep_group_fractions": [0.70, 0.15, 0.15],
        "mixed_group_variants": "purged entirely",
        "bk": "5 outer GroupKFold; inner grouped 20% validation; censor flags excluded from primary regression",
        "benefit": "avGFP target >0.1 log10 fluorescence above WT; BK signed shifts <=-50 or >=50 mV are direction objectives, not therapeutic benefits; other VEP targets ranked by training-only 90th percentile, not asserted WT gains",
        "model_selection": "validation only; outer test never selects features, hyperparameters, stopping or score sign",
        "scope": "New retrospective comparison partitions, not published split reproduction or prospective validation",
    }
    write_immutable(
        DATA / "evaluation_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    print(json.dumps(audit, indent=2, default=int))


def vep_split(
    frame: pd.DataFrame, name: str, protocol: str, seed: int, offset: int
) -> np.ndarray:
    groups = pd.read_csv(DATA / "vep_group_partitions.csv", dtype={"group": str})
    selected = groups[
        (groups.dataset == name) & (groups.protocol == protocol) & (groups.seed == seed)
    ]
    mapping = selected.set_index("group").split.to_dict()
    parts = []
    for ident, parsed in zip(frame.variant, frame.parsed, strict=True):
        tokens = (
            [str(position - offset) for _, position, _ in parsed]
            if protocol == "site"
            else ident.split(",")
        )
        values = {mapping[token] for token in tokens}
        parts.append(values.pop() if len(values) == 1 else "purged")
    return np.array(parts)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    prepare()
