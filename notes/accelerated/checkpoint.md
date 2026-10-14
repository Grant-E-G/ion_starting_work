# Accelerated modeling: first feedback checkpoint

**Larger pretrained models and several physical tools are locally executable.
Useful multiobjective mutation selection remains unproven.** The strongest new
functional signal is a retrospective ESM-1v ranking within the September
ChrimsonR paper's selected panel. The strongest new physical software result is
a working, differentiable MemPrO membrane-placement calculation. Neither result
establishes a general optimizer. No final protein/assay/panel was selected, no
hybrid platform was built, and OmpF remained frozen.

[Runnable commands](../../code/experiments/accelerated/README.md),
[20-method survey and primary-source audit](method_survey.md),
[verified source manifest](../../sources/accelerated/source_manifest.json),
[fixed zero-shot evaluation policy](../../sources/accelerated/evaluation_policy.json),
[all new predictions](independent_predictions.csv) and
[exploratory comparisons](comparisons.csv) accompany this checkpoint. Downloaded
sources/weights and generated outputs stay outside Git. This block uses existing
published measurements; it requests no new experimental training data.

## Actual local execution

`nvidia-smi` could not communicate with the driver. This is an access/environment
limitation, not evidence that the founder's RTX 3080 16GB does not exist or is
too small. No CUDA repair campaign was attempted. The installed OpenMM build
listed CPU/Reference platforms. **All measured work below used CPU.**

| Component | Actual measured execution | Observable and limits |
|---|---|---|
| ESM-1v, one 650M checkpoint | 16–18s for 13 masked Chrimson sites; latest process peak ~3,064 MiB. 154 ChR sequence embeddings: **195s**, peak **3,310 MiB**. | Evolutionary compatibility/representations, not photocurrent or kinetics. Checkpoint downloaded in ~22s; do not include this as model inference. |
| ProteinMPNN v48_020 | ~1.2s per template including loading and repeated inference; combined 2-template component run **4.7s**, peak **639 MiB**. | Fixed-backbone unconditional preferences, no functional-state transition. One inference thread used after detecting a repeatability issue with four. |
| Membrane-labelled / ligand-aware MPNN | 16 order seeds: vanilla **2.9s**, global membrane **2.9s**, ligand **9.8s**; cumulative process peak **992 MiB**. | Existing published networks. Ligand parsing retained 176 heteroatoms, including non-retinal context; no validated covalent retinal representation or photochemistry. |
| ProDy GNM | ~0.013s per template; 279/325 positive modes | Relative elastic-network fluctuations, not a mutation-to-gating-energy mapping. Uniform springs. |
| Solvent exposure + experimental transfer scale | Included in the measured 4.7s component run | Fixed monomer exposure and octanol preferences (charged-His table entry, no protonation correction); not an explicit membrane solvation free energy. |
| MemPrO, pinned source/JAX CPU 0.6.0 | 4 starts ×150 iterations: **54.9s**, peak **1,452 MiB**. 12×150: **63.1s**, peak **1,580 MiB**. | Actual implicit neutral-membrane WT placement and pose-energy gradients. No mutant function/energy or atomistic lipid sampling. |
| OpenMM / PDBFixer | Unrepaired force-field assignment failed; bounded repair/preparation timed out at **20s per template**. | A preparation/workflow limitation; no atomistic throughput or predictive result measured. |
| BioEmu / RosettaMP / SaProt | **Not locally executed in this block** | Source/software/evidence assessed; no invented runtime, GPU fit or functional accuracy. |

MemPrO initially ran 4 starts ×20 iterations in 53s and found three placement
clusters. At 150 iterations, 4 and 12 starts each reached a single reported
cluster with best relative potentials −52.105 and −52.248. This is a limited
numerical consistency check, **not a convergence certificate**. Keep the output
in the implementation's relative units; they have not been established here as
experimental folding/gating free energies. The source differentiates pose energy
with `jax.grad`; discrete amino-acid changes and function are not thereby
differentiable. No Boltzmann populations or gating rates were derived.

## Independent-publication checks

The September [ChrimsonR study](https://www.nature.com/articles/s41598-026-66799-1)
provides 17 selected recommendations. Its supplement and Figure 2 identify
15 patchable mutants; R176L/Y261T are not assigned zero currents. Two current
gains, E300G/P, also slow closure. We retrieved full preprint text and supplements,
not just the abstract. Full per-cell data and an exact experimental input FASTA
were not retrieved. We used the deposited 5ZIH sequence plus K176R, with author
numbering mapped through coordinates. **This is a surrogate input** and one
ESM-1v member, not a reproduction of the six-model published procedure.

| Fixed zero-shot score, 15 patchable selected variants | Current-gain precision in top 5 | ROC AUC |
|---|---:|---:|
| WT-null, expected random ties | 0.133 | 0.500 |
| ESM-1v 650M, masked marginal | **2/5** | 1.000 |
| ESM-2 8M, masked marginal | 0/5 | 0.462 |
| ProteinMPNN unconditional | 0/5 | 0.385 |
| Favorable octanol transfer | 1/5 | 0.654 |

ESM-1v ranks G/P above V/L **within the four E300 substitutions**, while 8M,
ProteinMPNN and the transfer scale prefer V/L. This goes beyond merely preferring
the E300 site, but remains only four variants at one site. The perfect AUC is
based on **two positives at that same site**, in an already model-selected
panel. There is no random-mutagenesis denominator and no prospective enrichment
claim. All labels were known during literature review; no model was fitted or
score sign chosen on them.

For a strict no-slower-than-reference closing constraint, neither current gain
qualifies: reported off times are 0.19/0.40s versus 0.06s control. The need to
predict tradeoffs survives the improved current ranking. More permissive
application-specific constraints could change utility; that objective must be
specified before an independent validation.

The [membrane-energy benchmark repository](https://github.com/Graylab/Implicit-Membrane-Energy-Function-Benchmark)
provided 37 non-reference OmpLA/PagP stability observations at **two sites**.
We exclude the unverified OmpLA proline zero entry; PagP's reference is alanine
at benchmark position 104 although the structure contains valine. These are
benchmark transcriptions, not a fresh primary experimental-table audit.
Stabilization is defined as mutant-minus-reference energy below −0.5 kcal/mol.

| Zero-shot method | OmpLA: stabilizing P5 / rank correlation | PagP: stabilizing P5 / rank correlation |
|---|---|---|
| Experimental transfer scale | 0.80 / 0.814 | **1.00 / 0.795** |
| ESM-1v | 0.60 / 0.699 | 1.00 / 0.775 |
| ESM-2 8M | 0.80 / 0.835 | 0.80 / 0.468 |
| ProteinMPNN | 0.80 / 0.633 | 0.60 / 0.432 |

A context/scoring sensitivity check retains both ESM-1v gains in the top five
across full deposited sequence versus the resolved span (internal residues
retained), and masked versus original-style WT-marginal scoring. ESM-1v AUC is
1.00/0.923 for these strategies; 8M P5 is 0/0.20. These are follow-up sensitivity
checks on the same panel, not new validation. [Every combination](context_sensitivity_metrics.csv).
The exact construct remains unresolved.

A simple physical scale contains real signal for this matched auxiliary task.
This neither establishes site transfer nor predicts channel function. It also
shows why a more complex model should earn its extra cost against cheap physics.

## Functional tradeoffs and ablations on the previously inspected panels

These retain the old immutable partitions, but **are exploratory**, not new
independent confirmations. New models use validation utility P10, then MAE to
break ties; test labels do not choose hyperparameters. Missing ChR kinetics
are excluded, not labelled failures. The old-panel joint objective is current
>1.2×the best parent and closing no slower than the slowest parent (50.919ms).

- Across 27 comparisons on ChR/Kir, adding backbone likelihood, transfer or GNM
features to ESM does not establish a reliable useful-gain advantage. On 44 ChR
test sequences with kinetics, ESM current-gain P20 is 0.70, joint current/kinetic
P20 is 0.05 (constant-null expectation: 0.341/0.045); additions leave the joint result at 0.05. MPNN alone has current
P20 0.15 and joint P20 0.10—two joint positives among 20 picks, too few for a
validated advantage. [All comparisons](comparisons.csv).
- A paired three-network Chrimson test using the same upstream scorer and 16
order seeds gives current-gain P5 **0, 0.20, 0** for vanilla, membrane-labelled,
and ligand-aware MPNN. Maximum per-token log-probability SD across orders is
~2.5–2.9. More context and software execution do not automatically improve the
functional objective. [Paired results](context_mpnn_metrics.csv).
- Larger ESM-1v embeddings do **not** improve the old ChR joint test. Current-only
P20: 8M **0.70**, 650M **0.65**. Joint current/kinetic P20: **0.05 vs 0**.
Two-head current/kinetic ranking also fails to improve this. Critically, the
validation set has **zero joint gains**; utility-based selection is uninformative
and falls back to MAE. This is a data/objective-power limitation, not evidence
that larger PLMs universally fail. [Results](larger_model_metrics.csv).
- Projecting transfer preferences/exposure into MemPrO's inferred membrane zone
changes ESM joint P20 **0.05→0.05**, with negligible current error change.
This tests a membrane-zone descriptor, **not mutant MemPrO free energies**.
[Physical ablation](membrane_ablation_metrics.csv).

## Data and numerical failure analysis

The independent KCNE1 supplement contains 2,539 scored entries: 2,320 missense,
98 synonymous and 121 nonsense. Only **N111Q** is confidently classified as a
functional gain. The [authors explain](https://pmc.ncbi.nlm.nih.gov/articles/PMC11138074/)
that the KCNQ1-S140G growth-selection assay is underpowered to separate known
gains from WT. Its literature review has 156 patch-labelled rows, 140 distinct
variant strings and 20 papers, mixing oocyte/CHO/HEK systems; not all strings
are simple independent substitutions. Do not pool these into a homogeneous gain
benchmark. It remains useful for damage/trafficking controls, with direct-current
records requiring publication/condition-level curation.

Seven numerical/provenance tests cover transfer-scale signs, GNM conservation and
rigid-transform invariance, MPNN rigid-transform invariance, Chrimson author
numbering/missingness, independent stability reference states and frozen-partition/
embedding alignment, plus BK censor-flag/site separation. Separate aggregate hashes verify **all 30 frozen OmpF scientific-code files, 209 source inputs and 978 result files** unchanged. A four-thread MPNN repeat check occasionally differed by
~0.039 log-probability; one-thread inference passed repeated controls and is now
used for unconditional scores. Context-network decoding-order variability is
reported separately rather than hidden. HF's ESM-1v warning concerns an unused
contact regression head, not the token likelihood/embedding weights used here.

## Existing BK implementation: next reproduction candidate

[BKpred](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011460)
provides 473 mutation records at 247 sites with gating-voltage shifts near zero
calcium, plus public open/closed Rosetta/MD descriptors. Its four later tested
variants involve sites already represented in training. Importantly, 28 raw
voltage entries sit at censoring flags; the publication also squashes targets.
Treating those flags as exact voltages would produce misleading comparisons.

A fixed-RF check excludes these 28 bounds using the original frozen site split:
257 fitting and 126 test records. No hyperparameters were tuned. “Shift” here
means ≤−50mV or ≥+50mV, **not a proven beneficial neuronal phenotype**.

| Features, same site-held-out test | Negative-shift P10 | Positive-shift P10 | RMSE, raw mV |
|---|---:|---:|---:|
| Null | 0.103 | 0.143 | 62.8 |
| Cheap residue/hydropathy/conservation | 0.20 | **0.50** | 63.5 |
| Precomputed state-energy terms | 0 | 0.30 | 66.0 |
| Cheap + state energies | 0.20 | 0.20 | 65.8 |
| Cheap + energies + geometry | 0.10 | 0.10 | 64.0 |
| Full descriptors including covariance anchors | **0.40** | 0.10 | 61.0 |

The full descriptor tail contains historically function-informed anchor choices,
so it is secondary evidence. Energy additions do not improve this fixed test.
This is **not a reproduction of the paper's learner/transformations**, nor an
indictment of Rosetta or MD. The public data are much better suited to testing
state-sensitive physics than another general architecture proposal. Feature
regeneration cost has not been measured here; fitting these supplied descriptors
took under three seconds, peak ~180MiB. The secondary protocol named
`publication` groups entire source strings and can share individual references
across strings; it is **not strict publication independence** and is not the
primary result above. True reference-connected partitions remain next work.

[Code](../../code/experiments/accelerated/bk_check.py),
[frozen site/source-string partitions](../../sources/accelerated/bk_partitions.csv),
[source-driven censoring policy](../../sources/accelerated/bk_uncensored_policy.json),
[raw-run label-audit diagnostic](bk_metrics.csv),
[uncensored predictions](bk_predictions_uncensored.csv), and
[comparisons](bk_metrics_uncensored.csv) preserve both the initial diagnostic and
its correction. Next block should verify sequence/isoform numbering, reconstruct
paper preprocessing, audit feature-selection leakage and the four later variants,
and compare with PLM baselines before inferring an engineering advantage.


## Recommendation for the next block

**GO for focused component testing; evidence insufficient for a general useful-
mutation optimizer.** No target-level modeling NO-GO follows from the failed
physical descriptors or preparation workflow. The ranked five-method shortlist
is ESM-1v/1b, MemPrO, membrane-/ligand-aware MPNN, RosettaMP and BioEmu; the latter
two still need actual local execution. SaProt 35M is an inexpensive challenger,
and CHAP supplies a more function-directed hydration test when appropriate.

1. **First audit/reproduce the newly identified BKpred functional benchmark**
using its public precomputed features, then compare pretrained sequence scores
under strict site and publication-component holdouts (see above). No new MD is
needed for this discriminating test. In parallel, resolve the Chrimson
input/procedure and run the published consensus.
Use an exact verified sequence and all six checkpoints sequentially. Distinguish
WT-marginal consensus from masked scores. Freeze a current–closing/light-sensitivity
objective and reserve new publication/construct groups and mutation sites. The
current E300 examples are development/sensitivity data now; do not repeatedly
tune against them and call it validation. Seek a gain-rich independent panel
before judging top-k utility. These are competing computational tests, not experimental target commitments.
2. **Test a real membrane-energy mutation mapping on independent stability
sites.** Audit historical calibration overlap first: OmpLA center/aromatic data were
used to determine Franklin weights, so they are not independent validation of
that energy function. [Primary parameterization](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011296).
RosettaMP repacking and depth-dependent energies should beat transfer
scale/ESM on held-out membrane depths or proteins before becoming a functional
filter. WT MemPrO orientation can establish membrane context. Do not fit arbitrary
per-mutant energies or confuse stable folding with favorable gating.
3. **Give BioEmu a narrow ensemble test.** First reproduce an accessible GlpG
conformational observable with pinned dependencies and compare coverage/population
weights with the published MD/structure benchmark. Only then test mutation-induced
changes. For a hydration hypothesis, selectively pair states with CHAP/short
water simulations. Monomer states without lipids or cofactors are not channel
kinetics; no expensive generic simulation infrastructure is justified yet.

The missing evidence most limiting confidence is an independent, adequately
populated **functional-gain-under-tradeoffs** benchmark with verified constructs
and conditions. The larger-model and membrane-tool runs materially reduce the
local-compute uncertainty. They do not yet close that engineering evidence gap.


Final checks: **15 tests passed**, Black/Ruff/mypy passed, 25 exact source resources
verified. Four refit checks reproduced **29,707 prediction rows** with maximum
numerical difference 4.3×10⁻¹⁴. Rows repeat variants across methods and are not
independent experiments. [Validation and code hashes](validation.json).
