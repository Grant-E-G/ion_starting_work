# Local protein-transformer feasibility benchmark

Completed October 13, 2026. Scope: choose plausible local model/adaptation routes before committing to GtACR2 experiments. No experimental candidates or improved proteins are claimed.

## Decision

**Local inference and adapter tuning are feasible for all three models. No model earns selection as an unadapted predictor of improved GtACR2 bacterial transport.** Keep ESM C 600M and ESM-2 650M as comparative backbones; AMPLIFY 350M is the lowest-memory adaptation candidate. Hardware does not currently justify switching proteins. The unresolved constraint is phenotype supervision and evaluation.

The benchmark uses the actual NVIDIA GeForce RTX 3080 Laptop GPU with 16 GB VRAM. GPU access works with execution outside the agent sandbox. The earlier failed nvidia-smi check reflected restricted execution, not a host driver failure. No host driver or system Python configuration was changed. Python dependencies and model caches are under /tmp/ion-model-venv, /tmp/ion-uv-cache and /tmp/ion-hf-cache.

## What ran

Three official checkpoints, pinned to revisions in the raw metadata:

- [ESM-2 650M](https://huggingface.co/facebook/esm2_t33_650M_UR50D), 651,043,254 parameters.
- [ESM C 600M](https://huggingface.co/biohub/ESMC-600M), 575,036,992 parameters. This is the current Biohub checkpoint, not an assumed identical replacement for the older EvolutionaryScale release.
- [AMPLIFY 350M](https://huggingface.co/chandar-lab/AMPLIFY_350M), 354,008,667 parameters.

Reference: NCBI KP171709.1 translated CDS AKN63095.1, first 266 residues. Input SHA-256 is recorded. Every residue token was checked against the input sequence, including the single leading special-token offset. All models use the same 266-residue input, batch size one, and masked-marginal mutation scoring:

`score(i, a) = log P(a | sequence with i masked) - log P(WT_i | sequence with i masked)`.

For each position, one masked forward pass scores all 19 alternative amino acids. The full scan therefore uses 266 forward passes to score 5,054 single substitutions per model. This avoids treating each substitution as a separate inference call. Full scans used BF16. The six published substitutions were independently rescored in FP32 to check precision sensitivity.

Models ran sequentially. Ten warmed, synchronized forward passes measured latency. Full-scan timing includes score extraction and Python overhead, but excludes model loading and downloads. CUDA memory numbers are PyTorch peak allocations/reservations, not total device occupancy or CPU RAM. These are bounded measurements at one sequence length/batch size; they are not universal throughput claims or optimized maximum-batch benchmarks. Attention backends differ across implementations, so speed compares the actual local implementations rather than isolating architecture.

## Measured hardware results

| Model | BF16 full scan | Median forward | Inference peak allocated | LoRA peak allocated | LoRA trainable parameters |
|---|---:|---:|---:|---:|---:|
| ESM-2 650M | 8.75 s | 32.1 ms | 1.23 GiB | 1.65 GiB | 1,351,680 |
| ESM C 600M | 6.08 s | 22.4 ms | 1.09 GiB | 1.46 GiB | 1,327,104 |
| AMPLIFY 350M | 6.83 s | 25.6 ms | 0.69 GiB | 0.95 GiB | 983,040 |

FP32 inference also passed, with peak allocated memory of 2.52, 2.20 and 1.34 GiB respectively. BF16 changes some close rankings: ESM-2 puts E219Q third in the diagnostic in BF16 and fourth in FP32. Use FP32 rescoring for close finalist comparisons; absolute score differences between models are not calibrated functional differences.

AMPLIFY required a compatibility fix: its upstream rotary positional table is an unregistered tensor that remained on the meta device under the installed Transformers loader. The benchmark recomputes that table using the exact upstream function. Reviewed official remote-code dependencies were used; no model architecture or checkpoint weights were modified. The script retains the fix explicitly.

## Functional diagnostic

Labels come from the [2018 GtACR2 bacterial study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/): E9Q/E56Q/E64Q were described as WT-like, E159Q/D230N lower, and E219Q higher after expression normalization. Textual rounded activity ratios were retained where reported; unavailable numerical values were left blank. No figure values or error bars were invented.

| Model | E219Q rank among six, FP32 | Ordinal concordance | Exact one-sided permutation probability |
|---|---:|---:|---:|
| ESM-2 650M | 4 | 5/11 | 0.65 |
| ESM C 600M | 4 | 6/11 | 0.50 |
| AMPLIFY 350M | 5 | 6/11 | 0.50 |

Concordance counts correct ordering across the 11 pairs with different categorical phenotypes; tied scores receive half credit. Within-class pairs are excluded. Random ranking has expected concordance 0.5 and gives the sole higher-activity mutant rank one with probability 1/6. Exact permutation enumeration uses the 60 distinct assignments of one higher, three WT-like and two lower labels. These probabilities are descriptive diagnostic null comparisons, not independent biological replication or prospective validation.

All three models rank D230N last, but rank E159Q above the higher-activity E219Q. Thus the scores capture one damaging substitution but fail to reliably order this panel by transport improvement. A rule taken from this paper can recover its labels by construction; that is a literature lookup, not an independently evaluated engineering predictor. A random split of these six examples would not fix this limitation.

**This is a diagnostic on six deliberately selected residues from one source, not a representative held-out benchmark.** It cannot establish model superiority, impossibility of design, or performance on other channels. Pretraining exposure to related sequences is not audited. There is only one higher-activity example; training and validating a supervised transformer on this panel would give misleading confidence.

## Fine-tuning feasibility

All models passed three AdamW updates with rank-8 LoRA on attention query/value projections, learning rate 1e-4 and seed 17. The synthetic task reconstructs one masked residue in WT. Loss decreased and finite updates completed. Updates were discarded and no fine-tuned checkpoint was saved. This establishes execution/memory feasibility at batch one, not learned transport prediction. It is not a training-speed estimate for a whole curated dataset, and larger batches, longer proteins, additional heads and other adapter targets change memory use.

Full-backbone training, supervised phenotype heads, family adaptation and multi-seed learning curves were not run. They remain legitimate options. Conventional full training also needs gradient and optimizer state storage; adapter memory figures must not be presented as full-fine-tuning memory. A smaller trainable backbone may beat a larger frozen one, but this diagnostic does not decide that comparison.

The next scientific gate is a data audit for a specified phenotype. Do not pool bacterial pH slopes, HEK photocurrents, closing kinetics and expression as one label. The [2026 GtACR chimera paper](https://www.nature.com/articles/s41598-026-46487-w) states underlying datasets are available by request; its construct differences require explicit mapping. No author was contacted.

If compatible labels permit grouped evaluation, compare frozen representations plus a regularized predictor against LoRA and a sequence/structure heuristic using identical source/residue splits. If labels remain this sparse, either pursue explicitly hypothesis-driven structure-constrained design with prospective uncertainty, or compare a better-labeled scaffold. Unlabeled family adaptation is technically possible but cannot supply the missing directional phenotype supervision.

## Artifacts and reproduction

- [GPU benchmark script](../code/experiments/benchmark_protein_models.py).
- [Summary script](../code/experiments/summarize_protein_benchmarks.py).
- [Pinned environment](../code/experiments/protein_benchmark_requirements.txt).
- [Reference sequence](../sources/gtacr2_reference.fasta).
- [Source-grounded diagnostic labels](../sources/gtacr2_2018_diagnostic_labels.csv).
- [Machine-readable summary](../sources/model_benchmarks/summary.json).
- Per-model full-scan CSVs and runtime JSONs in `sources/model_benchmarks/`; `_fp32` artifacts cover 114 substitutions at the six diagnostic positions.

Run from the repository root in a CUDA-enabled environment. Install `torch==2.6.0` and `xformers==0.0.29.post3` from the CUDA 12.6 PyTorch wheel index, then remaining pinned dependencies. The temporary environment already contains these packages. For exact checkpoint reproduction, pass `--revision` using the corresponding recorded SHA:

```bash
HF_HOME=/tmp/ion-hf-cache /tmp/ion-model-venv/bin/python code/experiments/benchmark_protein_models.py facebook/esm2_t33_650M_UR50D /tmp/esm2_repeat --revision 08e4846e537177426273712802403f7ba8261b6c
HF_HOME=/tmp/ion-hf-cache /tmp/ion-model-venv/bin/python code/experiments/benchmark_protein_models.py biohub/ESMC-600M /tmp/esmc_repeat --revision fcc9d36f5fff97d9bb69a36e3252de61cc78c968
HF_HOME=/tmp/ion-hf-cache /tmp/ion-model-venv/bin/python code/experiments/benchmark_protein_models.py chandar-lab/AMPLIFY_350M /tmp/amplify_repeat --revision 223e35e4e2074fadfdc1617f3451b14fa5ace1c8
```

Add `--precision float32 --panel-only --no-training` for diagnostic rescoring. Warm loading will differ from first-download time. Scripts passed Black and mypy. No biological experiment, validated mutant, model-superiority claim, remote paid compute or system-driver modification resulted.
