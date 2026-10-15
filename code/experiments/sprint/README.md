# Mutation-effect physics sprint — 14 October 2026

Read the [decision report](../../../notes/sprint/decision_report.md) before using
these predictions. This directory contains executable falsification experiments,
not a validated prospective design platform. OmpF remains frozen.

## Environment and inputs

The tested interpreters are `/tmp/c5r-predict/bin/python` (CPU analysis and ENCoM)
and `/tmp/c5r-gpu/bin/python` (CUDA PyTorch). Their exact installed package lists
are `requirements-cpu-lock.txt` and `requirements-gpu-lock.txt`. Python 3.10.9,
PyTorch 2.6.0, CUDA wheel cu124, host NVIDIA driver 560.35.05; 16 GB RTX 3080
Laptop. GPU commands need host device visibility; the repository's root
[AGENTS.md](../../../AGENTS.md) documents the verified execution workaround.
Do not reinstall a driver to fix sandbox device visibility.

For a fresh environment, install the scientific dependencies from the locks;
use the PyTorch cu124 wheel index for the GPU torch wheel. Install `nrgten==1.2.9`
and `pyvcon==1.0.2` **with `--no-deps` after the scientific stack**: their historical
metadata otherwise downgrades NumPy. The actual numerical stack was tested here.
A lock is an observed environment, not a claim that every historical upstream
version constraint is mutually satisfiable. METL is loaded from its pinned source
files under the downloaded `raw/metl` directory, not an unrelated PyPI package.

All commands below run from the repository root. For example:

```bash
CPU=/tmp/c5r-predict/bin/python
GPU=/tmp/c5r-gpu/bin/python
$CPU code/experiments/sprint/cache.py --verify
$CPU code/experiments/sprint/data.py
$CPU code/experiments/sprint/bk_audit.py
```

`cache.py` without `--verify` retrieves exact hashed scientific inputs; `--build`
compiles the unmodified pinned EvoEF2 C++ source with g++ -O3. Source manifests in
`sources/sprint` record URLs, hashes and revisions. ESM model manifests pin
Hugging Face revisions; inference scripts retrieve those weights automatically.
METL source-only checkpoints and source files are in the scientific manifests.
Downloaded files, features, coordinates and result CSVs are intentionally ignored.
Compact policies, expected partition hashes, source manifests, code and Markdown
reports are versionable. Do not add thousands of generated data files to Git.

## Experiments and commands

Each script has `--help`. Frozen CSV partitions and their expected hashes are
created by the data preparation; reruns refuse changed policies. Source labels,
censor handling, numbering and target scales are audited before new fitting.

| Question | Executable |
|---|---|
| Reproduce published BK RF, recover exact30 features, identify MAE/RMSE distinction | `bk.py --reproduce`; `bk_audit.py`; `bk_matched.py` |
| Group-aware sequence/physics/Ridge/RF/GP comparisons | `bk.py`; `kernels.py`; `boosted.py` |
| WT-zero constraints and publication/site shortcut baselines | `bk_nullaware.py`; `bk_shortcuts.py` |
| Assay/species/auxiliary-subunit provenance | `condition_audit.py`; `condition_compare.py` |
| Actual pretrained masked features and mutant embeddings | `sequence.py`; `mutant_embeddings.py` |
| Modern Barethiya CNN/GCN port, repaired masked AAIndex, S2 configuration | `vep.py` |
| Cheap native C++ local repacking and matched-WT energy changes | `energy.py`; `energy_sensitivity.py` |
| Physical source-pretrained METL features and adaptation | `metl_check.py`; `metl_finetune.py` |
| ESM35 frozen/LoRA adaptation and physical feature ablation | `finetune.py` |
| Gain-specific classification rather than damage-dominated regression | `gain_classifier.py`; `classify.py` |
| True WT-gain thresholds and combination/parent controls | `tabular.py`; `combinations.py`; `physical_readouts.py` |
| Independent GPCR function and tradeoff benchmark | `adrb2_data.py`; `adrb2_features.py`; `adrb2_compare.py` |
| Independent2024 BK multi-mutant publication/known-parent controls | `external_bk_data.py`; `external_bk_energy.py`; `external_bk_sequence.py`; `external_bk_compare.py` |
| Approximate pore hydration vs full hydropathy/geometry profiles | `hydration.py`; `hydration_mutants.py`; `hydration_compare.py` |
| Chemical-contact collective dynamics / numerical invariants | `encom_check.py`; `encom_numerics.py`; `encom_features.py`; `encom_compare.py` |
| Independent four-site binding assay, measured data only | `gb1_transfer.py prepare/features/compare` |
| Paired cluster uncertainty and physical surrogate agreement | `uncertainty.py`; `physical_audit.py` |
| Aggregate results with verified WT benefit scopes | `collect.py` |

Representative GPU comparisons, after cached features exist:

```bash
$GPU code/experiments/sprint/vep.py --datasets avgfp pab1 --architectures cnn gcn --features sequence rosetta_rmsf evoef_matched_rmsf --aaindex-mode mutation
$GPU code/experiments/sprint/vep.py --datasets avgfp pab1 --architectures cnn gcn --features sequence rosetta_rmsf esm2_35m esm2_35m_rosetta_rmsf --aaindex-mode mutation --published --epochs 500
$GPU code/experiments/sprint/finetune.py --dataset avgfp --modes frozen lora --features none rosetta evoef_matched --train-limit 64 --validation-limit 32 --epochs 40
$GPU code/experiments/sprint/metl_finetune.py --dataset avgfp --checkpoints gfp random_gfp --train-limit 64 --validation-limit 32 --validation-stride 5 --epochs 500 --unfreeze-epoch 250
$GPU code/experiments/sprint/metl_finetune.py --dataset gb1 --checkpoints binding binding_control --train-limit 1000 --validation-limit 256 --validation-stride 5 --epochs 500 --unfreeze-epoch 250
```

`metl_finetune` uses the published head-first/then-unfreeze schedule, but new
strict partitions, train-only target standardization and capped label budgets.
It is a method port, not exact reproduction of the authors' split-level scores.
Random GFP weights are initialized with the upstream constructor. GB1 STANDARD
is a physically pretrained matched control, **not** an untrained model.

Independent tests and dynamics, in dependency order:

```bash
$CPU code/experiments/sprint/adrb2_data.py
$GPU code/experiments/sprint/adrb2_features.py --help
$CPU code/experiments/sprint/adrb2_compare.py --objective potency --tag strong
$CPU code/experiments/sprint/external_bk_data.py
$CPU code/experiments/sprint/external_bk_energy.py
$GPU code/experiments/sprint/external_bk_sequence.py
$CPU code/experiments/sprint/external_bk_compare.py
$CPU code/experiments/sprint/encom_check.py
$CPU code/experiments/sprint/encom_numerics.py
$CPU code/experiments/sprint/encom_features.py
$CPU code/experiments/sprint/encom_compare.py
$CPU code/experiments/sprint/external_bk_compare.py --encom
$CPU code/experiments/sprint/gb1_transfer.py prepare
$GPU code/experiments/sprint/gb1_transfer.py features
$CPU code/experiments/sprint/gb1_transfer.py compare
$CPU code/experiments/sprint/collect.py
```

`encom_features` expects the already generated BK/external EvoEF2 patches. Its
273-residue transmembrane monomer lacks RCK domains, lipid, voltage and tetramer
coupling. ENCoM entropy and harmonic work are descriptors in pseudo-physical
units; neither is a calibrated activation free energy. All comparisons use the
same eligible cohort. Never compare a subset correlation to the full445 table.

Hydration's optional `--profiles --stable` removes train-only near-constant
columns before scaling. Original unstabilized predictions remain preserved;
the alternative tests a numerical failure, not a newly fitted physical law.

## Reading outputs without overclaiming

- `neural_cases.csv` identifies encoding, model configuration, actual training
  **plus validation** label count, physical method, best epoch and benefit scope.
  `gb1_WT_gain_metrics.csv` corrects historical percentile-based tabular metrics
  against verified WT. Historical source result files remain unchanged.
- BK primary comparisons use uncensored raw mV, fixed source-connected or
  withheld-site partitions. Original random-split squashed targets are a
  separate reproduction. A left shift alone is not a measured multi-objective
  neuronal improvement. Whole-assay context is partly unresolved.
- GFP benefit means WT-normalized log10 fluorescence>=0.1. GB1 benefit means
  verified WT-normalized enrichment>=1.2. Pab1/Bgl3/Ube4b percentile metrics are
  **not** claimed as WT improvements.
- P20 averages test folds, with fractional tie handling. Pooled out-of-fold
  ranking can differ from the mean of fold rankings. Use site-diverse metrics
  to detect many selected substitutions at one known hotspot.
- `paired_uncertainty.json` bootstraps fixed paired predictions by the actual
  site/publication clusters. It does not refit, correct hundreds of comparisons,
  or certify prospective interval coverage. Earlier `bk_bootstrap_local.json`
  has an obsolete publication-cluster calculation; do not use it.
- The corrected S2 ESM cases contain `_rawLLR`; earlier S2 ESM cases used a
  tenfold LLR scaling and are retained as diagnostics. `_maskedAA` is the
  repaired published mutation-masked encoding; `full` is a different control.
- METL normalizes physical targets separately per PDB. Subtracting WT removes
  means but not different standard deviations. Concatenated state descriptors
  are interpretable as features; subtracting outputs is not a common-unit
  physical energy without original state normalizers.
- Never load function-finetuned METL checkpoints for these benchmarks: they
  would leak experimental labels. Source-only physical pretraining may still
  cover related mutant sequences, which limits claims about physical OOD.

Validation commands:

```bash
$CPU -m pytest code/experiments/sprint/test_invariants.py -q
$CPU -m ruff check code/experiments/sprint --target-version py310
$CPU -m mypy code/experiments/sprint --ignore-missing-imports --follow-imports skip
$CPU code/experiments/accelerated/audit.py
```

Runtime measurements reflect shared local load, not isolated speed records.
There are no new biological experiments or genuinely prospective predictions.
MD, full electromechanics and a large multi-fidelity simulator were not built.

## Interrupted-session handoff

The founder stopped new experiments after token exhaustion. All benchmark
workers have exited. Six random Kir1D/3D latent caches (seeds1729/2718/3141)
were generated, but **their readouts have not been evaluated**. Do not interpret
missing random-control comparison CSVs as a negative result. The next approved
block can evaluate them with `kir_transfer.py compare/classify --tag random
--feature-pattern 'global[13]d_latent|random.*_latent'`; that work was not run
during cleanup.

Later sprint scripts include `kir_transfer.py` (paired function/surface proxy
and3B baseline), `kir_random_features.py`, `kir_analysis.py`,
`gb1_components.py` (existing component-label calibration and Hamming kernel),
`gb1_component_selection.py` (old-validation utility selection),
`gb1_transfer_utility.py --parent-order 2` (same-assay proper-parent controls),
`encom_motion_checks.py`, `energy_repro.py`, `report_tables.py` and `figures.py`.
Kir reuses the prior audited `code/experiments/predictive/data.py`, its source
manifest/caches and existing `sources/nearby_modeling` label tables. These are
additional inputs to a fresh reproduction, not downloaded by sprint/cache alone.
The review packet is a code/results handoff, not a complete weight/raw-data
redistribution or a standalone copy of the frozen OmpF benchmark.
