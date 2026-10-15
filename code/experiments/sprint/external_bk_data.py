"""Independent2024 BK patch-clamp data, exact conditions/WT and overlap audit."""

from __future__ import annotations

import hashlib
import json
import re

import pandas as pd
from Bio import SeqIO
from bs4 import BeautifulSoup
from data import DATA, OUT, RAW, load_bk, write_immutable


def main() -> None:
    article = BeautifulSoup((RAW / "bk_external2024.html").read_bytes(), "html.parser")
    table = next(
        table for table in article.find_all("table") if "L312A" in table.get_text()
    )
    source = load_bk().set_index("id", drop=False)
    sequence = str(next(SeqIO.parse(RAW / "6V3G.fasta", "fasta")).seq)
    rows = []
    wt = {}
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 4:
            continue
        label = cells[0].get_text("", strip=True).replace("\xa0", " ")
        label = re.sub(r"\s+", "", label)
        condition = re.search(r"\((\d+).*?Ca", label)
        if condition is None:
            continue
        calcium = int(condition[1])
        numbers = [
            [
                float(number)
                for number in re.findall(
                    r"-?\d+(?:\.\d+)?", cell.get_text(" ", strip=True).replace("−", "-")
                )
            ]
            for cell in cells[1:]
        ]
        if label.startswith("Slo1("):
            wt[calcium] = (
                numbers[0][0],
                numbers[0][1],
                numbers[1][0],
                numbers[1][1],
                int(numbers[2][0]),
            )
            continue
        match = re.fullmatch(r"Slo1([A-Z]\d+[A-Z](?:/[A-Z]\d+[A-Z])*)\(.*", label)
        if match is None:
            continue  # Chimeras and non-native protein backgrounds are not variants.
        tokens = sorted(match[1].split("/"), key=lambda value: int(value[1:-1]))
        assert all(sequence[int(token[1:-1]) - 1] == token[0] for token in tokens)
        ident = ",".join(tokens)
        rows.append(
            {
                "id": ident,
                "source_expression": label,
                "calcium_uM": calcium,
                "mutant_Vhalf_mV": numbers[0][0],
                "mutant_Vhalf_reported_SEM_mV": numbers[0][1],
                "mutant_z_apparent": numbers[1][0],
                "mutant_z_reported_SEM": numbers[1][1],
                "patches": int(numbers[2][0]),
                "single_training_overlap": ident in source.index,
                "known_constituents": ",".join(
                    token for token in tokens if token in source.index
                ),
            }
        )
    frame = pd.DataFrame(rows)
    assert len(frame[frame.calcium_uM == 0]) == 12
    for calcium, (mean, error, z, z_error, n) in wt.items():
        mask = frame.calcium_uM == calcium
        frame.loc[mask, "WT_Vhalf_mV"] = mean
        frame.loc[mask, "WT_Vhalf_reported_SEM_mV"] = error
        frame.loc[mask, "WT_z_apparent"] = z
        frame.loc[mask, "WT_z_reported_SEM"] = z_error
        frame.loc[mask, "WT_patches"] = n
    frame["target_mV"] = frame.mutant_Vhalf_mV - frame.WT_Vhalf_mV
    frame["gating_shift50"] = frame.target_mV <= -50
    frame["shift_with_slope_retained"] = frame.gating_shift50 & (
        frame.mutant_z_apparent >= 0.8 * frame.WT_z_apparent
    )
    primary = frame[(frame.calcium_uM == 0) & ~frame.single_training_overlap]
    policy = {
        "publication": "Transmembrane determinants of voltage-gating differences between BK(Slo1) and Slo3 channels,2024,PMC11309983,Table1",
        "experimental_construct": "Human Slo1 GenBankAAB65837 in pcDNA6, HEK293 cells, inside-out patches; point variants only, chimeras excluded",
        "primary": "Zero intracellularCa, subtract matched WT169+/-3mV; exclude exact genotype overlap with473trainingmutants",
        "test_genotypes": primary.id.tolist(),
        "overlap_controls": frame.loc[
            (frame.calcium_uM == 0) & frame.single_training_overlap, "id"
        ].tolist(),
        "other_conditions": "25uM calcium multi-mutants retained in manifest, never graded as zeroCa functional predictions",
        "utility": "Leftward shift>=50mV, secondary apparent Boltzmann slope>=80%matchedWT; no clinical benefit claim and apparentz is not totalgatingcharge",
        "strong_baseline": "Known-parent-only prediction uses only pre2023trainingconstituents; unknown constituents are not treated as measured neutral singles",
        "limitation": "Small targeted panel: four gain combinations share L312A. Success recognizing that parent is insufficient to show prediction of new improvements; no combo improves matched L312A by>=10mV.",
        "status": "Independent-publication retrospective evaluation; source labels read during curation, no external labels used for fitting/model tuning",
    }
    write_immutable(
        DATA / "external_bk_policy.json", json.dumps(policy, indent=2) + "\n"
    )
    content = frame.to_csv(index=False)
    (OUT / "external_bk_measurements.csv").write_text(content)
    write_immutable(
        DATA / "external_bk_measurement_hash.json",
        json.dumps(
            {
                "sha256": hashlib.sha256(content.encode()).hexdigest(),
                "constructs_zeroCa": 12,
                "new_genotypes_zeroCa": len(primary),
                "new_gating_shifts": int(primary.gating_shift50.sum()),
                "new_shifts_slope_retained": int(
                    primary.shift_with_slope_retained.sum()
                ),
                "mutations": sorted(
                    {token for ident in frame.id for token in ident.split(",")},
                    key=lambda value: (int(value[1:-1]), value[-1]),
                ),
            },
            indent=2,
        )
        + "\n",
    )
    print(
        primary[
            ["id", "target_mV", "mutant_z_apparent", "known_constituents"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
