# Accelerated existing-method checks

Read [the checkpoint report](../../../notes/accelerated/checkpoint.md) and
[method/source audit](../../../notes/accelerated/method_survey.md) first. OmpF is
frozen. No prospective panel, experimental target or hybrid platform is selected.

GPU execution is now verified: see [the measured GPU check](../../../notes/accelerated/gpu_access.md)
and [root agent instructions](../../../AGENTS.md) for the sandbox workaround,
isolated CUDA environment and `gpu_check.py` reproduction command. The CPU
environment below remains unchanged.

Python is used here to invoke published Python models and scientific libraries.
The code extends the existing audited loaders and immutable partitions from
`../predictive`; it does not change that benchmark's inputs or results.

Use the prior predictive environment, plus the pinned additions in
`requirements-additional.txt`. Example executable environment from this run:
`/tmp/c5r-predict/bin/python`. These paths are conveniences, not requirements.
From the repository root:

```bash
python code/experiments/predictive/cache.py --model
python code/experiments/accelerated/cache.py --models
OPENBLAS_NUM_THREADS=4 python code/experiments/accelerated/components.py
OPENBLAS_NUM_THREADS=4 python code/experiments/accelerated/compare.py
OPENBLAS_NUM_THREADS=4 python code/experiments/accelerated/independent.py
OPENBLAS_NUM_THREADS=4 python code/experiments/accelerated/context_mpnn.py
OPENBLAS_NUM_THREADS=4 python code/experiments/accelerated/larger_model.py
OPENMM_CPU_THREADS=4 python code/experiments/accelerated/openmm_check.py
pytest -q code/experiments/accelerated/test_components.py
```

`components.py` uses one PyTorch thread for reproducible unconditional MPNN
scores; other ESM and context-scoring tests use four. Checkpoint weights load
with `weights_only=True`. `context_mpnn.py` imports the upstream implementation
but does not execute third-party pickled output files. The small membrane-labelled
and ligand-aware checkpoints are distinct from a membrane physical simulator.

`larger_model.py` caches embeddings locally. Delete only its generated
`notes/accelerated/esm1v_bed_embeddings.npz` if explicitly measuring uncached
feature extraction again. Cached fitting is not an inference benchmark.

MemPrO is isolated because it requires Python ≥3.11 and JAX CPU **0.6.0**.
Use `uv venv --python 3.11 /tmp/c5r-mempro`, then install the exact dependencies
in `requirements-mempro.txt` there. The source/force field are hash checked by
`cache.py`; the wrapper assembles an unmodified local package from those files.
No whole-system conda/CUDA changes are needed:

```bash
python code/experiments/accelerated/membrane_check.py --python /tmp/c5r-mempro/bin/python --starts 4 --iterations 150
python code/experiments/accelerated/membrane_check.py --python /tmp/c5r-mempro/bin/python --starts 12 --iterations 150
```

MemPrO runs have a 180s cap. OpenMM preparation runs have a 20s per-template cap;
the observed failures/timeouts are retained, not replaced by successful toy
simulations. No atomistic functional prediction follows from these smoke tests.
Generated structures, downloaded code/weights, features and prediction tables
are ignored by Git; small policies, provenance, code and reports are tracked.
`source_manifest.json` rejects changed cached inputs; `evaluation_policy.json`
records zero-shot targets and exclusions before new-model predictions.

The Chrimson labels are qualitative paper-level current gains, on a selected
panel with two missing/unpatchable constructs. The input is a PDB-derived
surrogate, not a verified fusion construct. The stability tables are experimental
benchmark transcriptions at two sites, not channel-function observations. Existing
Bedbrook/Kir tests have already been inspected: new comparisons on them are
exploratory, regardless of preserved data partitions.

The late BK check uses **published precomputed** Rosetta/MD features:

```bash
python code/experiments/accelerated/audit.py
python code/experiments/accelerated/bk_check.py --uncensored
python code/experiments/accelerated/membrane_ablation.py
python code/experiments/accelerated/sensitivity.py
```

Its censoring correction excludes extreme flag labels while preserving the
original partitions. The raw run is retained as a label-audit diagnostic. The
historical `publication` protocol groups source strings and is not a strict
publication-connected holdout. See the explicit policy/report limitations.
