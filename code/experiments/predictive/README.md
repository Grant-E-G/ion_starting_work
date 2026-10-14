# Executed predictive feasibility benchmarks

Start with [the quantitative decision report](../../../notes/predictive/decision_report.md).
This code is separate from the frozen OmpF benchmark. Python uses the existing
scientific/pretrained-model ecosystem; no new simulation platform is built.
No wet-lab request, paid compute, purchases or prospective variants are involved.

## Reproduce

Tested on Python 3.10.9, CPU; GPU unavailable in this execution environment.

```bash
python3 -m venv /tmp/c5r-predict
/tmp/c5r-predict/bin/pip install -r code/experiments/predictive/requirements.txt
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 MPLCONFIGDIR=/tmp/c5r-mpl
/tmp/c5r-predict/bin/python code/experiments/predictive/cache.py --model
/tmp/c5r-predict/bin/python code/experiments/predictive/data.py
/tmp/c5r-predict/bin/python code/experiments/predictive/features.py
/tmp/c5r-predict/bin/python code/experiments/predictive/benchmark.py
/tmp/c5r-predict/bin/python code/experiments/predictive/mscl.py
/tmp/c5r-predict/bin/python code/experiments/predictive/analyze.py
/tmp/c5r-predict/bin/python code/experiments/predictive/plots.py
/tmp/c5r-predict/bin/python -m pytest code/experiments/predictive/test_invariants.py -q
```

The first cache command uses public network resources and verifies hashes.
Subsequent steps use cached inputs, including the pinned official ESM-2 8M
checkpoint. The existing `sources/nearby_modeling` publisher tables are inputs;
not newly generated labels. Source availability/licensing remains governed by
the original papers and repositories; public access is not a blanket commercial
license. No third-party research pickle is loaded or executed.

`data.py` refuses to change the tracked frozen partition file. Normal reruns
recreate the same splits and audit while preserving the original freeze timestamp.
The executable model candidates and grids are in `benchmark.py`; hyperparameters
and the primary model choice use validation MAE. Test scores do not choose them.
MscL's separate deterministic leave-site-out protocol is a small diagnostic with
no hyperparameter search, not a statistically powered design benchmark.

To refresh analyses from existing predictions, run only `analyze.py` and
`plots.py`. Tied predictions receive fractional expected top-k precision rather
than benefiting from source row ordering. No measured test trafficking enters
a function model; oracle surface stratification is explicitly diagnostic.

## What is included

- Raw measured data audit: 154 ChR sequences; 6,963 Kir function and 6,917
trafficking substitutions after exact tag/control handling. MscL has three
mutation genotypes/two sites with direct thermodynamic parameters.
- Held-out generation, sequence-component, site and contiguous-region tests.
- WT/null, training mean, physicochemical/conservation/geometry regressions,
sequence and ESM-feature ridge, gradient boosting, and ChR GPs.
- Paired physical-descriptor ablations, group bootstrap diagnostics, uncertainty
coverage, measured-noise sensitivities, and current/kinetics tradeoffs.
- Local actual held-out predictions, selected hyperparameters, resources and
figures. `sources/predictive/results_manifest.json` hashes the recorded artifacts.

Feature caveats matter: Kir uses native WT context without the constant FLAG
tag, and a fixed chicken Kir2.2 forced-open mutant template (6M84), not a WT
mouse Kir2.1 experimental structure. ESM Kir encoding is a cheap context plus
substitution approximation. ChR structure uses all fixed 3UG9 nonlocal contacts,
not the paper's label-selected contact weights. Coarse charge/packing descriptors
are not mutant gating-energy or transport simulations. MscL's single global
hydration coefficient is fit on other sites; per-mutant energies are never fit
on the held-out mutant.

## Recorded artifacts and checks

Code, source manifest, manually audited MscL measurements, partition files and
reports are intended for Git. Raw downloads, pretrained/feature caches, and
`notes/predictive` generated outputs are ignored and retained locally. A fresh
checkout must reconstruct them. Exact hashes identify the current recorded
results; timing fields and floating-point details can vary across machines.
No source labels or OmpF files are overwritten by this workflow.

Use Black one file at a time in restricted environments. Checks:

```bash
ruff check --target-version py310 code/experiments/predictive
mypy --ignore-missing-imports --follow-imports skip code/experiments/predictive
```

Eight meaningful tests cover source-coordinate verification, tag exclusions,
construct grouping, strict component separation, null/tie selection, measured
label provenance and tension/occupancy limits. These are implementation tests,
not prospective validation. Bootstrap intervals are exploratory and conditional
on the sampled library; multiple comparisons and homolog dependence remain.
