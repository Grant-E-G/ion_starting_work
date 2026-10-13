# Reproduce the OmpF feasibility slice

This is a structure-derived electrostatics/transport prototype, not a protein
language model or folding predictor. Start with the decision report in
`notes/ompf/decision_report.md` and equations in `math/ompf_physics_slice.md`.
Python is used for the existing SciPy, OpenMM and PDBFixer scientific stack.

## Environment

Tested with Python 3.10.9 on this Ubuntu laptop. Use an isolated environment:

```bash
python3 -m venv /tmp/ompf-venv
/tmp/ompf-venv/bin/pip install -r code/experiments/ompf/requirements-cuda.txt
```

The CUDA requirement pins the NVRTC version used successfully with driver
560.35.05 on the 16 GiB RTX 3080 Laptop GPU. The CPU-only requirements suffice
for all field/transport calculations and analysis using the saved prepared
structures. Preparation also accepts `--platform CPU`, but the initial duplicate
CPU preparation was stopped after GPU preparation succeeded; no completed CPU
preparation speed is claimed. Downloading sources/packages needs internet;
calculating from cached artifacts does not.

## Source and measurement audit

```bash
python code/experiments/ompf/fetch.py
python code/experiments/ompf/dataset.py
```

`fetch.py` uses caches by default, records URLs/hashes, and rejects non-PDF
challenge pages. `--force` refreshes files deliberately. `dataset.py` recreates
hand-audited tables and verifies mutation numbering against the mature sequence.
Raw scanned SI requires visual checking. Bredin 2002 full text was accessible
through the browser but its local PDF download returned HTTP403; the exact table
transcription and methods audit are saved separately. Missing method conditions
are exclusions, not guessed values. Supplemental rows reused from earlier papers
are not independent measurements. Six WT observations are calibrations; 19
eligible mutant rows describe 14 distinct constructs. Only the Miedema 2004
zero-voltage slope cohort directly matches the computed observable.

## Prepare and calculate

```bash
OPENMM_CPU_THREADS=4 OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/prepare.py
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/benchmark.py --mode nonlinear_pb
OPENMM_CPU_THREADS=4 OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/prepare.py --trimer
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/benchmark.py --trimer
```

Preparation starts exclusively from WT 2OMF, assigns AMBER14 charges, adds
hydrogens for nominal pH7.4 and repairs mutated side chains with strong restraints
on backbone/unchanged heavy atoms. It is not a validated folding procedure or
an exhaustive rotamer ensemble. Biological assembly MODEL records are converted
into three chains, not interpreted as alternative conformations.

The full-trimer comparison is the preferred physical scaffold. The monomer
calculation quantifies the cheaper approximation. Both use nonlinear PB and
linear-response transport with a common diffusion assumption for every mutant.
No mutant-specific mobility is fitted. Comparisons contain observed and modeled
mutant/WT ratios, a geometry baseline, two fixed charge baselines and a WT null.
A 5% gain flag refers to the point estimate, not statistical significance.

Use saved predictions without recomputing:

```bash
python code/experiments/ompf/benchmark.py --compare-only --trimer
python code/experiments/ompf/calibration.py
python code/experiments/ompf/summarize.py
python code/experiments/ompf/plots.py
```

The single global calibration is WT 1M KCl; other WT conditions test transfer.
Condition-normalized comparisons cancel a reference scale and must not be
presented as absolute-condition prediction success.

## Numerical and uncertainty checks

```bash
OPENBLAS_NUM_THREADS=1 python -m pytest code/experiments/ompf/test_physics.py -q
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/sensitivity.py --kind mesh
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/sensitivity.py --kind parameters
```

The grid study uses predeclared WT, AAA, EAE, LEAE, E117C and D312N subsets at
0.10, 0.075 and 0.05 nm. Full-trimer gain subsets at 0.15/0.10/0.075 nm are
recorded in their own results directory. Parameter studies vary dielectric,
probe radius, aperture, membrane thickness and box size without selecting a
best label fit. Two preparation initializations quantify only that narrow
source of variation. `run_summary.csv` records actual times and process-lifetime
RSS peaks; rerun in isolation for uncontended timing.

Additional APBS inputs/output and `apbs_check.py` independently verify a uniform-
dielectric screened charge. APBS3.0 was unpacked from Ubuntu packages into `/tmp`,
without system installation. With a normal APBS install, run `apbs point.in`
inside `notes/ompf/apbs`, then `apbs_check.py`. APBS emits `point_potential-PE0.dx`
in the tested build. This check does not validate molecular dielectric surfaces.

`physics.py` supports an unfitted lattice-gas ion-volume sensitivity through
`Config(ion_volume_nm3=...)`; results for 0.03/0.10 nm³ are under `sterics`.
These runs test whether dilute mean-field crowding changes conclusions. They are
not a retrospectively selected improved model. Numerical tests verify the
screening derivative, zero-volume limit, density bound and Gauss law.

For code checks use Black one file at a time in restricted sandboxes, Ruff,
and `mypy --ignore-missing-imports --follow-imports skip` on this directory.
Cached structures and JSON/CSV tables are reproducibility inputs/results; large
field arrays can be regenerated. No wet lab, purchases, contacts, folding-model
training, MD trajectory or prospective experiment is claimed.

## Dielectric-image model and final diagnostics

For the optional GPU Green-function backend, install the pinned Torch CUDA stack:

```bash
pip install -r code/experiments/ompf/requirements-torch-cuda.txt
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/reaction_benchmark.py --trimer --backend cuda32
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/reaction_benchmark.py --trimer --spacing 0.1 --variants WT AAA EAE LEAE --backend cuda32
```

The default image calculation is CPU and uses the same operators. These commands
reuse existing image maps and predictions, so remove/move a selected result
folder explicitly if recalculation is intended. Do not overwrite archived
fixtures casually. The float32 backend was verified against float64 on WT;
using a different GPU/software environment may change solver details.

Combined image/crowding sensitivities and the separate multistate challenge:

```bash
OPENBLAS_NUM_THREADS=1 python code/experiments/ompf/combined_sensitivity.py
OPENBLAS_NUM_THREADS=1 OPENMM_CPU_THREADS=4 python code/experiments/ompf/diagnostic_challenge.py --backend cuda32
OPENBLAS_NUM_THREADS=1 OPENMM_CPU_THREADS=4 python code/experiments/ompf/diagnostic_challenge.py --trimer --backend cuda32
```

The diagnostic helper creates D127N/D127K fixtures only when absent, reserves
NQRRR for the condition-incomplete diagnostic, and never inserts multistate
means into scalar comparison metrics. Recompute WT image/ordinary references
first if rebuilding without the caches. The crowding script recalculates its
small sensitivity set using existing image maps; no mutant label fitting occurs.

Refresh the principal analyses/figures from saved predictions in one command:

```bash
OPENBLAS_NUM_THREADS=1 MPLCONFIGDIR=/tmp/ion-mpl python code/experiments/ompf/refresh.py
python code/experiments/ompf/artifacts.py
```

`refresh.py` performs no PDE calculations. It regenerates measurements,
comparisons, WT calibrations, the salt-representation check, state challenge,
ranking, summaries and standalone PNG/PDF figures. Source fetching is separate
because some methods were accessed through browser-only full texts. Local raw
PDF availability is recorded honestly in the literature audit.

`artifacts.py` hashes the current artifact set. Optional `--audit-density`
recomputes derived density diagnostics from saved fields and normalizes image
source paths; it does not change conductance predictions or timings. The
recorded original audit is in `notes/ompf/checks/density_metadata_audit.json`.
Running the audit again will replace that audit record, so preserve it first
if studying the original corrections. New physical runs record the prepared
input SHA256; earlier runs rely on the final fixture manifest and regeneration
checks rather than claiming a hash was recorded at execution time.

There are 72 archived observations. Only 25 form the scalar benchmark; the
D127 six-row state table is separate, and excluded SI/incomplete-condition rows
remain visible. The model selection was retrospective. Neither point-gain
counts nor fitted WT scales are independent predictive validation.

Prepared fixtures are the exact coordinate/charge inputs. PDBFixer hydrogen
placement can vary on regeneration even with nominal seeds. Computational
field solves are deterministic within numerical tolerance for fixed fixtures;
use the exported validation and numerical records to interpret differences.
The entire local artifact set is about 1 GiB, mostly compressed field arrays.
A portable review bundle retains prepared inputs, image maps, two plotted fields,
code, tables, figures and reports. Other calculated fields and raw publisher
articles are omitted; the scanned supporting table required by the dataset
builder is included. Analysis refresh works from the bundle; the full density
audit requires the complete local fields or their regeneration. Create it with
`python code/experiments/ompf/review_bundle.py`.



Downloaded raw sources/structures, prepared coordinate fixtures, calculated
outputs, figures and the review archive are ignored by Git and remain on disk.
Git retains the code, review documents, curated measurement/variant tables,
reference sequence and provenance manifests. Exact previously prepared inputs
are available in the local workspace and portable review archive; a fresh clone
must fetch sources and prepare/calculate them before refreshing analyses.
Re-preparation can vary as described above, so an exact archived-result replay
requires the saved fixtures rather than just a fresh clone. The portable review
archive includes the inputs and two plotted fields needed for analysis refresh.
