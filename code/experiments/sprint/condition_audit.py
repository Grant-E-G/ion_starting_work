"""Recover assay-control context without altering BK labels or partitions."""

from __future__ import annotations

import json
import re

import pandas as pd
from bs4 import BeautifulSoup
from data import OUT, RAW, ROOT, load_bk


def main() -> None:
    frame = load_bk()
    workbook = ROOT / "sources/accelerated/raw/bk_data_BK_mutations.xlsx"
    complete = pd.read_excel(workbook, sheet_name="data_complete")
    assert not complete.duplicated(["Mutation", "Species"]).any()
    selected = complete[
        [
            "Mutation",
            "Species",
            "[Ca0]/M",
            "WTV1/2[Ca0]/mV",
            "MTV1/2[Ca0]/mV",
            "dV[Ca0]",
            "Source(s)",
        ]
    ]
    merged = frame[
        ["id", "Mutation", "Species", "target", "censored", "Source(s)"]
    ].merge(
        selected,
        on=["Mutation", "Species"],
        validate="one_to_one",
        suffixes=("_training", "_complete"),
    )
    assert len(merged) == len(frame) == 473 and merged["[Ca0]/M"].notna().all()
    primary = BeautifulSoup((RAW / "bk_V236A_primary.xml").read_text(), "xml")
    table = primary.find("table-wrap", id="tbl1")
    measurements = {}
    for row in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) >= 4 and re.fullmatch(r"[A-Z]\d+[A-Z]", cells[1]):
            measurements[cells[1]] = float(cells[2].split()[0].replace("−", "-"))
    confirmations = []
    for row in merged.itertuples(index=False, name=None):
        values = dict(zip(merged.columns, row, strict=True))
        ident = values["id"]
        first_source = re.findall(r"\d+", str(values["Source(s)_complete"]))[0]
        matches = (
            first_source == "8"
            and ident in measurements
            and abs(values["MTV1/2[Ca0]/mV"] - measurements[ident]) <= 1.1
        )
        confirmations.append(matches)
    merged["auxiliary_context"] = [
        "beta1_confirmed_table1_match" if value else "not_audited_unknown"
        for value in confirmations
    ]
    merged["primary_beta1_mutant_control_mV"] = merged.id.map(measurements).where(
        merged.auxiliary_context == "beta1_confirmed_table1_match"
    )
    merged.to_csv(OUT / "bk_assay_conditions.csv", index=False)
    finite = ~merged.censored
    difference = abs(merged.loc[finite, "dV[Ca0]"] - merged.loc[finite, "target"])
    result = {
        "variants": len(merged),
        "species": merged.Species.value_counts().to_dict(),
        "confirmed_beta1_rows": int(sum(confirmations)),
        "unknown_auxiliary_context": int(len(merged) - sum(confirmations)),
        "beta1_mutants": merged.loc[confirmations, "id"].tolist(),
        "nominal_calcium_nonzero": int((merged["[Ca0]/M"] > 0).sum()),
        "nominal_calcium_above10nM": merged.loc[
            merged["[Ca0]/M"] > 1e-8, ["id", "[Ca0]/M"]
        ].to_dict("records"),
        "WT_control_Vhalf_mV_range": [
            float(merged["WTV1/2[Ca0]/mV"].min()),
            float(merged["WTV1/2[Ca0]/mV"].max()),
        ],
        "training_vs_complete_numeric_label_max_difference": float(difference.max()),
        "labels_within10mV_of50mV_boundary": int(
            ((abs(abs(merged.target) - 50) <= 10) & finite).sum()
        ),
        "exact50mV_labels": int((abs(merged.target) == 50).sum()),
        "provenance": "Primary Hoshi2013 JGP DOI10.1085/jgp.201311061 Table1 explicitly hSlo1+hbeta1, zero intracellularCa; released workbook data_complete entries match13 mutant control values to within rounding and use WT160mV",
        "V236A": "Raw released target-50mV derives from control MT110 vs WT160mV; primary beta1 table MT110.8+/-1.1. BKpredTable2 reports-38+/-1mV. The pooled genotype label is not a unique assay-independent functional constant; exact explanation of Table2 difference remains unresolved.",
        "limitations": "Unknown context is not alpha-alone. Other source papers/construct splice backgrounds, lipids, Mg and temperature not fully audited. Shared human WT sequence/structure is an approximation for the mouse/rat records. Context mismatch limits interpretation of weak results; it does not prove a physical-model family failure.",
        "preservation": "No existing labels, features, test partitions or OmpF artifacts modified",
    }
    (OUT / "bk_condition_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
