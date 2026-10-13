# Local protein-model feasibility

October 13, 2026. Feasibility assessment; no candidate design commitment. The completed [GPU model benchmark](protein_model_benchmark.md) supersedes the initial hardware-access uncertainty below: elevated execution can use the host GPU, and three models passed inference and adapter checks.

The user clarified that modeling feasibility comes before revisiting GtACR2 assay fit. Establish hardware access, model capabilities and phenotype supervision before expanding execution. Serious engineering means auditable directional hypotheses and evaluation, rather than model size or throughput alone.

## Hardware evidence

PCI enumeration identifies NVIDIA GA104M, GeForce RTX 3080 Mobile / Max-Q (device 10de:249c). User-supplied host nvidia-smi confirms 16,384 MiB VRAM, driver 560.35.05 and advertised CUDA compatibility 12.6, with 64 MiB occupied at that snapshot. This establishes a working host GPU driver, not the installed CUDA toolkit or PyTorch compatibility. The current agent execution environment exposes no /dev/nvidia*, /dev/dri or /dev/dxg, and its nvidia-smi cannot communicate with the driver. This is an agent-environment access limitation. Host-visible RAM is approximately 31 GiB. Do not change drivers during feasibility work.

## Model fit and scientific fit

[ESM-2](https://huggingface.co/facebook/esm2_t6_8M_UR50D) provides 8M, 35M, 150M, 650M, 3B and 15B checkpoints. For 650M parameters, FP32 weights alone require about 2.6 GB decimal; FP16 weights about 1.3 GB. These are arithmetic lower bounds, not peak VRAM estimates. Runtime tensors, loading copies and batch size must be accounted for. A 266-residue sequence with small batches makes 650M inference a plausible candidate for either listed GPU configuration, subject to actual CUDA visibility and measurement. Full fine-tuning has substantially different memory needs; it is not the default proposal. Frozen representations plus a small supervised model are the first option if compatible labels exist.

Masked sequence log odds measure evolutionary plausibility. They do not directly predict increased transport, faster closure or improved light sensitivity. Structural features can constrain hypotheses but a static structure cannot establish gating kinetics. Broad generation without phenotype supervision does not resolve this gap.

## Work already executed before scope correction

Retrieved KP171709.1 translated CDS AKN63095.1 from NCBI; the bacterial construct uses residues 1–266. CPU-only ESM-2 8M, 35M and 650M six-mutation checks were launched; the 650M check completed before cancellation could take effect. No full mutation scan or training was run. Dependencies/model caches are under /tmp. Scores reside in sources/gtacr2_esm* scores CSVs. The script code/experiments/gtacr2_scores.py supports reproduction; these outputs are diagnostic sequence scores, not validated phenotype predictions. Black and mypy passed. No GPU benchmark or peak-memory measurement exists.

The [2018 bacterial study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/) supplies six selected single-mutant measurements. The [2026 chimera study](https://www.nature.com/articles/s41598-026-46487-w) uses another construct/context and offers datasets by request. They cannot silently be pooled into one training target. Neither a small six-mutant check nor a failure on it establishes general model superiority or impossibility of GtACR2 design.

## Required feasibility decision

1. Installed VRAM is confirmed at 16 GB. Establish whether the intended Python runtime can access CUDA; agent sandbox access is a separate issue.
2. Audit exact same-endpoint labels and independent residues/constructs, including accessible supplements; distinguish categorical labels, rounded ratios and raw observations.
3. Specify the transformer's role: plausibility filter, frozen features for directional prediction, or conditional generation. Only the second has a direct supervised phenotype objective here; the third still needs a trustworthy evaluator.
4. Compare a fixed low-complexity model with sequence/structure heuristics using residue/source-grouped evaluation. With very sparse labels, classify it as hypothesis-driven design and report uncertainty instead of a trained functional predictor.
5. Revisit GtACR2 assay economics only after deciding whether this target supports defensible computational design. Compare alternative scaffolds on phenotype data and assay fit together, rather than choosing the cheapest inference model.

Current decision: GPU inference and rank-8 adapter optimization passed for ESM-2 650M, ESM C 600M and AMPLIFY 350M. A 3B model has about 6 GB of FP16 weights alone and remains an unbenchmarked escalation. Direct sequence-likelihood ranking failed to supply convincing directional signal on the six-mutant diagnostic. See the completed benchmark for measurements and limits; target-specific supervised adaptation remains conditional on better phenotype data.
