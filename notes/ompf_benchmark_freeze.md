# OmpF benchmark freeze — C5R next phase

Freeze recorded UTC: 2026-10-14T02:23:47.108973+00:00. Baseline Git commit: `cfd8064eb467c7c0e904f453dab0f56039d89f1d`.

The founder has accepted the independent review's NO-GO for prospective OmpF
ion-conductance design. The benchmark is retained as a technical milestone.
This phase does not change its code, prepared coordinates, data labels,
physical parameters, calibration rules, metrics or interpretation. No further
image-energy, crowding or mesh refinement against these mutants is authorized
by this phase. No new model fitting or OmpF benchmark reruns were performed.

The frozen interpretation is in [the original decision report](ompf/decision_report.md):
72 archived observations; 25 eligible scalar observations including six WT
references and 19 mutant comparisons over 14 distinct mutant constructs;
D127 populations remain a separate challenge. Retrospective improvement on one
gain family does not establish independent useful selection. Cross-salt
representation, additional-site transfer, occupancy/protonation, and direct
conductance-assay readiness remain limitations. No prospective success is claimed.

A solute-permeability proposal is a new target–phenotype benchmark. The frozen
ion-conductance scores provide no validated predictor for that observable.

## Snapshot checksums

The aggregate checksum is SHA256 of sorted relative-path + TAB + file SHA256
records, joined by newline, including a final newline. Scientific-code paths
are sorted Python files followed by sorted requirements files. The results
set excludes logs, archives and the two generated inventory manifests. The
individual inventory already in `notes/ompf/artifact_manifest.json` is retained
unchanged as a historical artifact, rather than regenerated during this freeze.

| Set | Files | Bytes | Aggregate SHA256 |
|---|---:|---:|---|
| scientific_code | 30 | 129,991 | `65a906a6a3e98a188e8c06c48727ec54339b6cc30557599fe5fd792660175f83` |
| source_inputs | 209 | 54,692,860 | `ba9e1f22a68da389ed9259e9711cba8beba76b8e1ac4f2ef7a0885eb7194207c` |
| results | 978 | 974,569,042 | `cddce69e3934d96a850d6375de27527e6389923b6166c49ab00e5879a0acc054` |

Key archived artifacts:

- `notes/ompf/artifact_manifest.json`: `c1e074d7ee5544e34534633491a5104b474d308de90c19f2a7c837ecaf7910f5`
- `notes/ompf/review_bundle.tar.gz`: `5fb51de55d3d71db1d66612642c047e5938c4893438e622092c279db89f7c50e`
- `sources/ompf/measurements.csv`: `466f578a1cc29926ca5f034e051c3c1d1084c249c4ec76551e486d1f69bf5c57`
- `sources/ompf/structure_manifest.json`: `748aa0d6aa1b32b1bd86c4e3da9573878904065bef70ad803903b821da6be93d`
- `math/ompf_physics_slice.md`: `3375b78eb7ec65cb87c09901bd6324f65eea78b52c2f72475817f9724db87acb`

Git intentionally excludes downloaded/prepared data and generated results.
Those files remain in the local workspace. The existing portable review archive
includes prepared inputs and compact results, but omits most computed fields.
This records a policy freeze and exact checksums; it is not an off-machine backup
or a claim that ignored data are committed to Git. Preserve the local data and
archive when moving the project. No files were deleted or overwritten.
