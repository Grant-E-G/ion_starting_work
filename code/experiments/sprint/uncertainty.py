"""Paired uncertainty and site-diverse selection on fixed BK predictions.

No feature selection or fitting. Publication resampling uses true connected
references, fixing the obsolete first-run site-cluster diagnostic.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from data import OUT, load_bk, publication_components
from metrics import grouped_bootstrap, precision_at_k, site_diverse_precision


def main() -> None:
    native = load_bk().set_index("id", drop=False)
    publication, components = publication_components(native["Source(s)"])
    native["publication_component"] = publication
    results: list[dict] = []
    diversity: list[dict] = []

    def compare(
        name: str, frame: pd.DataFrame, first: str, second: str, key: str = "features"
    ) -> None:
        for protocol, rows in frame.groupby("protocol"):
            p = rows[rows[key] == first]
            q = rows[rows[key] == second]
            if not len(p) or not len(q):
                continue
            joined = p.merge(
                q, on="id", suffixes=("_first", "_second"), validate="one_to_one"
            )
            assert np.allclose(joined.actual_first, joined.actual_second)
            actual = joined.actual_first.to_numpy()
            a, b = joined.predicted_first.to_numpy(), joined.predicted_second.to_numpy()
            sites = native.loc[joined.id, "resN"].to_numpy()
            group = (
                native.loc[joined.id, "publication_component"].to_numpy()
                if protocol == "publication_component"
                else sites
            )
            for direction in [1, -1]:
                positive = direction * actual >= 50
                results.append(
                    {
                        "comparison": name,
                        "protocol": protocol,
                        "first": first,
                        "second": second,
                        "direction": direction,
                        "n": len(joined),
                        "pooled_OOF_P20_first": precision_at_k(
                            direction * a, positive, 20
                        ),
                        "pooled_OOF_P20_second": precision_at_k(
                            direction * b, positive, 20
                        ),
                        "site_diverse_P10_first": site_diverse_precision(
                            direction * a, positive, sites, 10
                        ),
                        "site_diverse_P10_second": site_diverse_precision(
                            direction * b, positive, sites, 10
                        ),
                        **grouped_bootstrap(
                            actual,
                            a,
                            b,
                            group,
                            direction * 50,
                            direction,
                            repetitions=2000,
                        ),
                    }
                )

    matched = pd.read_csv(OUT / "bk_matched_predictions.csv")
    matched = matched[
        (matched.handling == "uncensored")
        & (matched.target == "raw")
        & (matched.protocol != "published_random")
    ]
    compare(
        "Published fixed RF: incremental audited energy",
        matched,
        "geometry_evolution_energy",
        "WT_geometry_evolution",
    )
    null = pd.read_csv(OUT / "bk_null_predictions.csv")
    null = null[null.protocol != "published_random"]
    compare(
        "WT anchoring without energy",
        null,
        "WT_geometry_evolution_WTanchor",
        "WT_geometry_evolution",
    )
    compare(
        "Energy after WT anchoring",
        null,
        "geometry_evolution_energy_WTanchor",
        "WT_geometry_evolution_WTanchor",
    )
    regression = pd.read_csv(OUT / "bk_predictions_metl.csv")
    for learner in ["ridge", "rf"]:
        selected = regression[regression.learner == learner]
        for first, second in [
            ("esm2_35m_mutant_audited_energy", "esm2_35m_mutant"),
            ("esm2_35m_mutant_metl_global3d_state", "esm2_35m_mutant"),
            ("esm1v_650m_sequence_audited_energy", "esm1v_650m_sequence"),
        ]:
            compare(f"Sequence baseline {learner}", selected, first, second)
    for filename in [
        "bk_classification_predictions.csv",
        "bk_classification_predictions_3b.csv",
    ]:
        table = pd.read_csv(OUT / filename)
        table["site"] = table.id.map(native.resN)
        for keys, rows in table.groupby(
            ["protocol", "seed", "objective", "features", "learner"]
        ):
            protocol, seed, objective, feature, learner = keys
            score, positive = (
                rows.probability_uncalibrated.to_numpy(),
                rows.actual.to_numpy(),
            )
            diversity.append(
                {
                    "protocol": protocol,
                    "fold": int(seed),
                    "objective": objective,
                    "features": feature,
                    "learner": learner,
                    "n": len(rows),
                    "sites": int(rows.site.nunique()),
                    "P20": precision_at_k(score, positive, 20),
                    "site_diverse_P10": site_diverse_precision(
                        score, positive, rows.site.to_numpy(), 10
                    ),
                }
            )
    (OUT / "paired_uncertainty.json").write_text(
        json.dumps(
            {
                "comparisons": results,
                "scope": "Exploratory paired cluster bootstrap of pooled fixed OOF scores. These intervals do not refit learners, correct adaptive multiple comparisons, or establish prospective coverage. Pooled P20 differs from mean fold P20.",
                "publication_components": len(components),
                "obsolete": "Do not use first bk_bootstrap_local.json publication intervals: that old worker resampled sites instead of publication components.",
            },
            indent=2,
        )
        + "\n"
    )
    pd.DataFrame(diversity).to_csv(
        OUT / "bk_site_diverse_classification.csv", index=False
    )
    print(
        "Completed",
        len(results),
        "paired comparisons and",
        len(diversity),
        "site-diverse evaluations",
    )


if __name__ == "__main__":
    main()
