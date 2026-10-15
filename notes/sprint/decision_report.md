# Physics-informed mutation prediction: six-hour computational sprint

**Interrupted sprint, frozen for external review.** The planned six-hour block hit the token limit; cleanup and handoff were completed at the founder’s request. No new experiments were started during cleanup.

Local execution is feasible: source-pretrained physical models, native C++ mutant
repacking, chemical-contact dynamics, sequence models up to 3B parameters and
35M-model adaptation all ran on this computer. **A general advantage for selecting
useful membrane-protein mutations from added mutation-specific physical energies
has not been established.** There are narrower positive results for physical
pretraining and existing-data combination design. These justify further
controlled prediction experiments, not a large integrated simulator or a new
biological variant panel. No experimental target is selected. OmpF is unchanged.

The [quantitative appendix](quantitative_results.md) contains fixed comparisons;
[code and reproduction instructions](../../code/experiments/sprint/README.md),
[measurement/structure manifest](../../sources/sprint/benchmark_manifest.json),
[source manifests](../../sources/sprint/) and local prediction CSVs provide the
audit trail. These are retrospective results. There are no new biological
experiments or genuinely prospective engineering successes.

## What was reproduced and what was repaired

[Barethiya et al.2026](https://doi.org/10.1371/journal.pcbi.1013728) was investigated
through its released code, five complete functional tables, structures, Rosetta
features, RMSF and supplementary architecture settings. All substitution WT
identities and offsets were checked. The released encoder has a syntax error
and a 20-row AAIndex/21-symbol indexing mismatch. Its modified AAIndex path also
masks unchanged residues, unlike the original upstream encoder. The executable
PyTorch port repairs those issues, implements CNN/GCN families and released S2
settings/initializers, and separately tests full versus mutation-masked encoding.
Corrected published-configuration ESM runs use raw LLR; older scaled-LLR runs are
preserved as diagnostics. New grouped splits, limited label budgets and framework
differences mean this is **a method port, not an exact reproduction of paper
split-level performance**. Rosetta features were retrieved, not recomputed with
licensed Rosetta. Cheap new energies came from unmodified EvoEF2.

[BKpred](https://doi.org/10.1371/journal.pcbi.1011460) received an exact input audit:
all473 released row identities, 30 selected columns, train-only standardization
and the target transform `200*tanh(raw_mV/200)` were recovered. Stored mean random-
split correlation was0.703; local fixed-seed reproduction was0.712. The released
plotting function named `rmse` actually computes MAE: stored mean MAE is31.88,
while conventional RMSE is47.63, on the squashed target scale. This is a metric
naming correction, not proof of misconduct. Random tests contain many mutations
at sites already represented in training, so they do not answer unseen-site
design feasibility.

[METL](https://doi.org/10.1038/s41592-025-02776-2) supplied a particularly useful
existing implementation: source-only models trained to predict physical scores.
**Function-finetuned released weights were excluded** to avoid experimental-label
leakage. Global1D/3D, protein-local, binding-specific and matched standard-physics
checkpoints ran locally. GFP architecture-matched random controls and published
head-first/unfreeze adaptation were tested. The original preprocessing normalizes
physical targets separately per PDB. WT subtraction removes means but does not
remove different standard deviations: open-minus-closed outputs are descriptors,
not common-unit gating free energies. This limits interpretation, not their use
as supervised features.

Other executable methods included native EvoEF2, published ENCoM/NRGten,
CHAP's published hydration grid with an explicitly approximate pore extractor,
Ridge/RF/ExtraTrees, Gaussian-process and mutation-kernel baselines, gain-specific
classifiers, actual-mutant ESM representations, masked-marginal ESM8/35/150M,
ESM-1v650M and ESM-2 3B, and ESM35 LoRA. Each substantial implementation tested a
specific feature or generalization hypothesis; no general simulator was built.

## Main quantitative findings

**1. Released BK mutation energies do not improve strict functional selection
over the matched WT-structure/evolution baseline.** Primary new regression uses
445 numeric records after28 endpoint/placeholder flags (`<=-370` or `>=300mV`)
are excluded. Flags are a released-value handling rule, not a reconstruction of
every original voltage trace. Five site folds and five source-connected
publication folds were frozen. Publication grouping has only20 components,
including one with277 variants.

| Fixed published RF, raw mV | WT geometry/evolution | Add exact16 mutation-energy terms |
|---|---:|---:|
| Withheld-site correlation |0.227|0.194|
| Withheld-site RMSE, mV |48.71|48.79|
| Withheld-site left-shift P20 |0.21|0.17|
| Withheld-site right-shift P20 |0.11|0.10|
| Publication-held-out correlation |0.338|0.237|
| Publication-held-out left-shift P20 |0.21|0.19|

The baseline already contains WT physical/MD descriptors. This result rejects an
**incremental mutation-energy advantage in this comparison**, not the usefulness
of all structural information. WT-zero anchoring changes rankings and sometimes
helps a cheaper model more than added energy. Pooled out-of-fold rankings and
unweighted mean-fold P20 can disagree; they are not interchanged in reporting.
Site-diverse ranking and paired cluster intervals reveal substantial uncertainty.

Data context matters. The source pools339 mouse,133 human and1 rat record;
WT Vhalf controls span80–206.5mV. Thirteen labels were traced to explicitly
beta1-containing channels in the [primary Hoshi study](https://doi.org/10.1085/jgp.201311061),
not verified alpha-alone measurements. Two nominal zero-Ca records have appreciable
nonzero calcium. Unknown auxiliary/isoform context remains unknown. V236A also has
an unresolved difference between source-control subtraction and BKpred's table.
A genotype's pooled voltage shift is not an assay-independent constant.

**2. An independent BK panel exposes a known-parent shortcut.** The
[2024 primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11309983/) supplies10
novel zero-Ca genotypes after overlap controls/high-Ca conditions are separated.
All four large leftward shifts inherit known L312A. A known-parent-only predictor
has16mV MAE, versus34.6mV for the transferred650M sequence readout and35.4mV when
new joint EvoEF2 energies are appended. Against the matched L312A parent,
no-change MAE is28.25mV; sequence and sequence+energy errors are48.35 and52.06mV.
Normal-mode features do not resolve this failure. Large WT-relative changes do
not demonstrate useful prediction of the added modifications. Missing standalone
constituent measurements prevent claiming experimental epistasis.

**3. Physical pretraining helps some soluble controls, but gain selection and
transfer remain harder than damage prediction.** With1000 training+256 validation
labels, binding-pretrained METL improves GB1 withheld-site correlation0.471→0.625
and WT-gain P20 0.13→0.25 over its matched standard-physics checkpoint. These are
five-seed retrospective positive controls, not membrane validation. At64+32 GFP
labels, physical pretraining markedly improves bulk fluorescence correlation over
random initialization, while brighter-than-WT selection is much less convincing.
Adding EvoEF2 features to ESM35 often improves correlation without a consistent
P20 advantage; LoRA does not reliably solve the gain tail.

The independent [Wu GB1 assay](https://doi.org/10.7554/eLife.16965) is a stronger
extrapolation check:147,193 measured triples/quadruples, never imputed scores.
Its processed single-mutant column reuses older Olson measurements, so raw
`I20fitRaw` was reconstructed from original counts and used throughout.
With all four sites absent from training/validation, physical readouts do not beat
a simple chemistry baseline. With all2242 existing component single/double
measurements available, sequence kernels and some physical-assisted readouts can
select higher-order improvements. The dependence on existing site-specific
information is substantial.

![Parent-aware selection](figures/parent_aware_selection.png)

All bars use the same137,321 constructs with complete raw parent controls.
A physical latent readout selected by older-assay validation MSE achieves90%
WT-gain P20 but0% P20 for exceeding the best measured double parent. A sequence
kernel selected by validation MSE achieves30% on that harder endpoint. An
exploratory sequence+standard-physics readout reaches55%, or65% when ranked by
predicted increment using measured parent controls. The parent-aware selection
rule has only **six positive validation examples** and was investigated after
the test had been inspected. This is a lead to replicate, not a confirmed general
physics advantage. Its zero rescue precision also contrasts with the kernel's
ability to find some improvements when lower-order components are individually
unhelpful. Full results and selection-rule audits are retained, including
unfavorable physical readouts.

**4. New membrane tradeoff tests are informative, not platform validation.**
[ADRB2](https://doi.org/10.7554/eLife.54895) provides matched repeated signaling
measurements at four agonist concentrations. Its published normalized value1 is
a frameshift reference, not WT. We reconstructed scores and normalized against
synonymous controls. In the resolved-native-core test there are920 mutants,
only5 replicate-consistent activity gains and1 joint gain after basal/capacity
constraints. Larger sequence models and METL descriptors do not establish useful
joint-gain selection. This is an underpowered gain gate, not a GPCR/physics NO-GO.
Whole-cell cAMP signaling also combines receptor abundance and signaling.

[Kir2.1](https://doi.org/10.7554/eLife.76903) adds6789 paired function/surface
variants under the previous frozen site/region partitions. Native mouse sequence
and experimental FLAG numbering were reverified. A public exact-sequence WT
AlphaFold model supplies designer-accessible geometry; no mutant experimental
structure is used. The models omit the FLAG insertion, tetramer, lipids and an
explicit gating landscape. Function is a voltage-dye proxy, surface is an
expression phenotype, and a0.3-score gain is not30% more conductance.

For1494 withheld-site tests,287 clear the point joint-gain definition, while47
clear the approximate score−1.96SE filters. At1000+256 labels, adding physical
attributes to a650M sequence classifier changes point joint P20 0.25→0.35 and
SE-supported P20 0.05→0.10. The paired site-bootstrap point-gain difference
interval is[−0.05,+0.20]. The corresponding regression comparison changes
0.30→0.20. Six Kir architecture-matched random representations were generated, but their functional readout comparisons were **not run** before the interruption. This attribution test remains open. Shuffled-feature controls and the pending random-architecture comparisons are essential:
isolated improvements do not yet identify a stable physical advantage. A3B
sequence model also ran locally, providing a stronger representation check;
its WT-context protocol differs from actual-mutant650M inference.

## Numerical and resource evidence

- EvoEF2 matched WT self-repacking is necessary: repacking offsets can dominate
  small mutation differences. Three independent native builds produced identical
  coordinates/energies in the tested case, with unchanged backbone. A20Å crop
  agrees closely with28Å within this6Å-cutoff engine (state-total Spearman0.9974).
  This is finite-engine convergence, not convergence of membrane electrostatics.
  A12Å-case segmentation fault and a native100-character filename-buffer failure
  were identified as implementation failures; short-path staging fixes the latter.
- ENCoM evaluated274 genotypes in1788s using two CPU workers and reused sidechains.
  Six rigid modes, positive remaining spectrum, Hessian symmetry, rigid-translation
  null, repeatability and coordinate-frame checks pass. Harmonic work scales with
  displacement squared. Approximately14% of closed entropy changes are smaller
  than the tested coordinate-rounding sensitivity. Known-state motion has3.15Å
  RMS/8.79Å maximum displacement, so harmonic work is not an activation barrier.
  On the same259 numeric TMD variants, stabilized unseen-site Ridge left-shift
  P20 is0.14 for chemistry×WT geometry,0.12 with ENCoM, and0.14 with shuffled
  ENCoM. This particular descriptor has not earned further refinement here.
- Near-constant columns caused enormous WT-anchored Ridge predictions. A
  train-only, label-independent variance filter removes that numerical failure;
  original outputs are retained. Stabilization does not create a functional
  advantage. The approximate hydration model likewise distinguishes known wet/dry
  controls but does not beat full geometry/hydropathy inputs on its small matched
  pore cohort. It is not a native CHAP or explicit-water MD reproduction.
- Actual RTX3080Laptop16GB measurements include:3B Kir masked inference64s,
  ~5599MiB allocated;149,361 GB1 physical binding predictions56s/~186MiB;
  Kir6789 global physical predictions~82s/~600MiB;473 two-state EvoEF2 mutants
  1412s/two workers/~299MiB peak child RSS. Shared load and setup inclusion vary
  and are recorded per workload. GPU access works through host device visibility,
  documented in [AGENTS.md](../../AGENTS.md). A paired650M autocast probe measured
  ~1.9× speedup with<1% mutation-delta vector error in two tested cases; it does
  not certify unchanged functional rankings.

## Decision and next implementation

**GO for inexpensive feature generation and further predictive falsification.
Evidence is insufficient for a prospective membrane-variant selector.** A failed
fixed-backbone energy mapping, harmonic descriptor or hydration approximation is
not a fundamental limitation of physics-based engineering.

The strongest practical method class is **source-only physical pretraining used
as a calibrated feature/representation**, with strong sequence, statistical
kernel, empirical-parent and random-architecture controls. Mechanism-matched
pretraining sometimes helps, but direct physical scores and normalized state
contrasts should not become optimizer objectives without demonstrated functional
calibration. Native EvoEF2 is a cheap additional descriptor; it has not shown
reliable incremental utility here. Existing BKpred inputs remain a reproducible
benchmark, not a reason to refine the same BK test indefinitely. The tested
ENCoM/hydration approximations should be parked for this observable.

For neuronal relevance, **Kir2.1 paired function/trafficking and cation-ChR
photocurrent/kinetics remain computational candidates**, with different limits:
Kir has extensive public data but proxy/constraint uncertainty; the prior ChR
recombination benchmark has direct current evidence but limited family transfer
and no validated cheap optical replacement. BK is useful for direct gating
benchmarks but currently weak for mutation selection under heterogeneous assay
contexts. No target passes both predictive utility and an inexpensive confirmed
C5R validation path in this sprint.

The next implementation should be a **small, frozen prediction challenge**:
carry the sequence-only, physical-pretrained and architecture-matched controls
into an untouched, condition-controlled membrane dataset with actual beneficial
variants and matched expression/function constraints. Measure parent-relative
improvement, conservative gain precision, site diversity and uncertainty before
adding a simulator. The most limiting missing evidence is independent,
well-controlled useful membrane-function gains—not the ability to execute larger
models or generate more energy columns. Existing public component measurements
can support combination design; performance with those labels must not be sold
as design without target-specific functional information.

A minimal eventual experiment would need matched functional change and the
relevant tradeoff: Kir current/voltage response plus surface abundance; ChR
photocurrent plus off-kinetics under controlled illumination; BK voltage curves
plus gating/leak constraints. No laboratory work, purchasing, C5R requests or
variant orders were initiated.
