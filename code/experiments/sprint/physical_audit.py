"""Cross-approximation agreement, not experimental energy validation.

Tests whether cheap surrogates even retain published mutation-specific energy
ordering. Different force fields, structures and normalizations prevent treating
these comparisons as calibrated physical-energy accuracy.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import FEATURES, OUT, RAW, load_bk
from scipy.stats import spearmanr
from vep import energy_components


def main() -> None:
    text = (RAW / "metl/README.md").read_text()
    terms = (
        text.split("These models will output a length 55 vector", 1)[1]
        .split("```", 2)[1]
        .strip()
        .splitlines()
    )
    assert len(terms) == 55 and terms[0] == "total_score"
    index = {term: i for i, term in enumerate(terms)}
    rows: list[dict] = []

    def compare(
        dataset: str,
        label: str,
        first: np.ndarray,
        second: np.ndarray,
        sites: np.ndarray,
    ) -> None:
        assert np.isfinite(first).all() and np.isfinite(second).all()
        groups = pd.DataFrame({"first": first, "second": second, "site": sites})
        residual = groups[["first", "second"]] - groups.groupby("site")[
            ["first", "second"]
        ].transform("mean")
        for scope, p, q in [
            ("raw", first, second),
            (
                "within_site_centered",
                residual["first"].to_numpy(),
                residual["second"].to_numpy(),
            ),
        ]:
            rho = (
                float(spearmanr(p, q).statistic)
                if np.std(p) > 1e-12 and np.std(q) > 1e-12
                else None
            )
            rows.append(
                {
                    "dataset": dataset,
                    "comparison": label,
                    "scope": scope,
                    "mutants": len(first),
                    "sites": len(np.unique(sites)),
                    "spearman": rho,
                }
            )

    pairs = [
        ("fa_atr", 0),
        ("fa_rep", 1),
        ("fa_elec", 2),
        ("fa_sol", 3),
        ("fa_dun", 6),
        ("ddG", 7),
    ]
    for name, family in [
        ("avgfp", "avgfp_local"),
        ("pab1", "pab1_local"),
        ("gb1", "gb1_binding"),
        ("gb1", "gb1_binding_control"),
    ]:
        rosetta = pd.read_csv(RAW / f"VEP/data/{name}/ddG.tsv", sep="\t").set_index(
            "mutation"
        )
        evo = pd.read_csv(FEATURES / f"{name}_evoef.csv").set_index(
            "mutation", drop=False
        )
        controls = pd.read_csv(FEATURES / f"{name}_evoef_self.csv")
        self_map = {
            token[1:-1]: value
            for token, value in zip(
                controls.mutation, energy_components(controls), strict=True
            )
        }
        values = energy_components(evo)
        values -= np.stack([self_map[token[1:-1]] for token in evo.index])
        evo_values = pd.DataFrame(values, index=evo.index)
        for term, component in pairs:
            common = rosetta.index.intersection(evo.index)
            compare(
                name,
                f"Rosetta_{term}__EvoEF2_component{component}_matched",
                rosetta.loc[common, term].to_numpy(),
                evo_values.loc[common, component].to_numpy(),
                np.array([int(token[1:-1]) for token in common]),
            )
        path = FEATURES / f"{name}_metl_{family}.npz"
        if not path.exists():
            continue
        with np.load(path) as arrays:
            ids = pd.Index(arrays["ids"])
            single = np.array(["," not in token for token in ids])
            common = ids[single].intersection(rosetta.index)
            order = ids.get_indexer(common)
            attributes = arrays["attributes_native"][order]
        for term in [
            "fa_atr",
            "fa_rep",
            "fa_sol",
            "fa_elec",
            "fa_dun",
            "pro_close",
            "ref",
            "ddG",
        ]:
            target = "total_score" if term == "ddG" else term
            compare(
                name,
                f"Rosetta_{term}__METL_{family}_{target}",
                rosetta.loc[common, term].to_numpy(),
                attributes[:, index[target]],
                np.array([int(token[1:-1]) for token in common]),
            )
    bk = load_bk()
    with np.load(FEATURES / "bk_metl_global3d.npz") as arrays:
        order = pd.Index(arrays["ids"]).get_indexer(bk.id)
        for term in ["score", "fa_atr", "fa_rep", "fa_elec", "fa_sol", "fa_dun"]:
            target = "total_score" if term == "score" else term
            compare(
                "bk",
                f"Published_state_{term}__METL_state_{target}",
                bk[term].to_numpy(),
                arrays["state_difference"][order, index[target]],
                bk.resN.to_numpy(),
            )
    evo_bk = pd.read_csv(FEATURES / "bk_evoef_r20.csv").set_index("mutation").loc[bk.id]
    compare(
        "bk",
        "Published_state_score__EvoEF2_state_Total",
        bk.score.to_numpy(),
        evo_bk.state_difference_Total.to_numpy(),
        bk.resN.to_numpy(),
    )
    pd.DataFrame(rows).to_csv(OUT / "physical_cross_approximation.csv", index=False)
    (OUT / "physical_cross_approximation_scope.json").write_text(
        json.dumps(
            {
                "scope": "Agreement among approximations only, not independent experimental energy validation",
                "differences": "Barethiya minmax-normalized Rosetta features; METL normalized source targets on its own structures; matched EvoEF2 weighted potential changes; BK published membrane terms vs protein-only approximations",
                "centering": "Within-site centering tests substitution-specific ordering beyond a site mean; singleton sites contribute zero centered differences",
                "caveat": "Source physical pretraining can include related synthetic variants; correlation is not a held-out source-energy generalization claim. No kcal/mol accuracy claimed.",
            },
            indent=2,
        )
        + "\n"
    )
    print("Compared", len(rows), "energy/representation pairs")


if __name__ == "__main__":
    main()
