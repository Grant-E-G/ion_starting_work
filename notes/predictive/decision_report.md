# Predictive feasibility: executed benchmarks

This modeling result supersedes the previous assay-first MscL recommendation.
**Target selection remains open.** No assay or prospective variant panel is
selected. The OmpF benchmark was not changed or rerun.

**There is evidence for selecting higher-photocurrent recombinations within the
Bedbrook parent library, and for predicting Kir2.1 trafficking-score gains.
There is not yet convincing evidence of a generally useful neuronal mutation
optimizer.** The tested structural descriptors improve some regression errors,
but do not demonstrate a reliable gain-selection advantage over sequence-only
methods. A global MscL hydration-to-gating mapping fails a small site-transfer
check; that rejects this approximation, not mechanistic modeling or MscL itself.

These are actual local predictions: [all held-out predictions](predictions.csv),
[91 model/protocol comparisons](metrics.csv),
[validation-selected models](validation_selected_models.csv),
[paired physics ablations](paired_physics_ablations.json),
[failure examples](failure_examples.csv), and
[MscL predictions](mscl_site_holdout.csv).
[Runnable code and instructions](../../code/experiments/predictive/README.md),
[frozen partitions](../../sources/predictive/partitions.csv) and
[source manifest](../../sources/predictive/source_manifest.json) reproduce them.
Generated data remain local/ignored; code, partitions, provenance and this report
are retained in Git.

## What the data actually measure

| Dataset | Usable observations | Label and independence |
|---|---:|---|
| Bedbrook 2019 | 154 measured distinct aligned protein cores; 3 parental references, 151 recombinations | Whole-cell voltage-clamp peak photocurrent, nA; cell means, not intrinsic unitary conductance. No current SE supplied in these tables. Recombination variants, not 151 independent point mutations. |
| Kir2.1 function | 6,963 nonsynonymous substitutions at 391 native sites, plus 22 same-amino-acid reference rows | FACS voltage-dye membrane-potential proxy, Enrich2 score and reported SE. Not direct gating/conductance. |
| Kir2.1 surface | 6,917 substitutions at 391 sites, plus 22 reference rows | Surface-antibody/FACS trafficking phenotype. Not channel function. Paired function/surface data are never counted as independent proteins. |
| MscL 2005 | WT plus 3 mutant genotypes at only 2 mutation sites | State-occupancy-derived energies/areas from patch clamp. Multiple states, traces and reconstructed tension points are not extra independent mutants. |

[Bedbrook's primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6858556/)
and its pinned research repository provide matched measured sequences and an
explicit author `gen` field. All 154 publisher sequences match the author table;
current differences are rounding, at most 0.004967 nA. We use the unrounded
means. The current label is the maximum across the supplied color conditions,
not a single-wavelength current at equal photon flux; no arbitrary-wavelength
or intrinsic-conductance improvement follows. Supplementary Data3's 1,133 predicted designs are **not labels**; Data4's
label-selected weights are **not feature-selection inputs**. The 61 heterogeneous
literature records in Data1 are not pooled into the matched panel.

The [Kir2.1 paper](https://doi.org/10.7554/eLife.76903) describes mouse Kir2.1,
single-copy HEK expression and FLIPR Blue function sorting. The complete primary
PDF was retrieved. Translating the original construct and checking mutation
headers establishes the inserted eight-residue FLAG tag at tagged positions
116–123. Removing 48 tag-region rows and 22 same-AA controls from each raw table
exactly recovers the 6,963/6,917 nonsynonymous counts. Native positions above the
tag shift by eight. This avoids training on the tag as if it were native Kir.
The paper describes 20 reference positions; the supplied tables contain 22
same-AA rows. We preserve this discrepancy rather than inventing replication.

Kir gains mean score minus pooled reference median >0.3; this is a predefined
assay-score margin, not a percentage conductance change. The conservative
label additionally requires score −1.96×reported SE >0.3. These are approximate
filters, not validated simultaneous confidence intervals. Reference variation
is itself material: function-control SD 0.244, surface-control SD 0.403.
Greater hyperpolarization is not inherently therapeutic benefit.

The [MscL source](https://pmc.ncbi.nlm.nih.gov/articles/PMC2217497/) supplies
exact Table I energy/area values and methods. All three mutants were historically
selected for GOF gating, which can be toxic; they are not protective-survival
gain labels. The broader 2003 phenotype library was identified, but its exact
supplements were not retrieved; the correct public author PDF returned HTTP403. The 1999 G22 scan covers 19 substitutions at
one site; scanned figures were not converted into invented numbers. The 2015
cysteine/chemical-modification screen is not hundreds of independent sequence
mutants. The [2013 chimera/interface study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3593973/)
adds direct pressure-threshold and dwell-time data across orthologs, chimeras
and single-site substitutions; its exact SI table was not retrieved, and those
records were not silently pooled with the 2005 state energies. These remain
data limitations, not a target-level rejection.

## Frozen validation and executable models

Partitions were frozen before main-model fitting/tuning. They are retrospective
computational holdouts, not new prospective experiments. All observations of a
construct stay together. Same-AA Kir references and the three ChR parents are
reserved calibration controls, never scattered into independent test examples.

- **Bedbrook generation split:** 78 fitting sequences from author generations
1–2; 21 validation sequences from generations 4–7; 52 tests from 9–10. This is
our analyst-defined generation split, not a reproduction of the authors'
original train/test evaluation or independently timestamped trial.
- **95%-identity-purged generation split:** 53 fitting, 18 validation, 52 tests;
remove near neighbors of tests and training neighbors of validation. This
remains recombination within the same three parents.
- **90%-identity connected components:** 85 fitting, 12 validation, 54 tests;
no train/test pair exceeds 90% aligned identity. Only one test sequence clears
the gain margin. These are components within one recombinant library, not
unseen natural-protein families.
- **Kir site holdout:** deterministic native-site hashing; 3,984/1,441/1,538
function rows and 3,948/1,440/1,529 surface rows in fit/validation/test.
- **Kir region transfer:** fit native sites ≤195, validate 196–293, test 294–392;
1,835 function and 1,830 surface test substitutions. All substitutions at a
withheld site move together, and both assays use the same site assignment.

Models include WT-null, training mean, hydrophobicity/charge/volume regression,
conservation/BLOSUM regression, nominal geometry, coarse physical descriptors,
sequence ridge, frozen ESM-2 8M features, gradient-boosted trees, and ChR Gaussian
processes. Ridge penalties and GP length/noise choices use **validation MAE only**;
there is no test-based winner selection. GP hyperparameters are fixed-grid
fits, not foundation training. Full model tables expose results, including
models with good ranks that were not selected by the predefined criterion.

ESM-2 is pinned to revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`.
ChR inputs are aligned cores with gaps removed. Kir uses native sequence context,
WT residue embeddings, substitution embeddings and masked-marginal scores;
we do not recompute every complete mutant's embedding. This is an inexpensive
pretrained-feature baseline, not ESM-family performance at its ceiling.
Pretraining sequence overlap was not comprehensively audited.

Conservation here uses a small human KCNJ paralog alignment for Kir and three
parental sequences for ChR, not a deep ortholog MSA. Stronger evolutionary
baselines remain untested.

The structural experiment uses all nonlocal 3UG9 C-alpha contacts below 0.8 nm,
without Data4 selection. Kir uses a fixed **6M84 chicken Kir2.2 forced-open
K62W/G178D homolog**, 77.4% mapped identity, not WT mouse Kir2.1. Features include
contact density, nominal packing, hydrophobic contacts and screened residue-charge
terms under fixed assumptions. They omit explicit lipids/PIP2, state free energies,
protein relaxation and quaternary electrostatics. These are coarse physical
hypotheses, not simulated mutant currents. Their failure cannot reject physics
models generally.

## Useful-gain selection, not just correlation

A ChR gain is peak current >1.2×the best measured parent, threshold **1.18196 nA**.
P20 below is expected precision among the top 20, including fractional treatment
of ties. A constant/null model gets the background prevalence, never a favorable
ordering from input rows. Kir's conservative P20 uses the reported-SE filter;
ChR has no equivalent supplied measurement SE.

| Test / validation-selected model | Test n | Gain prevalence | Spearman | P20 | Conservative P20 |
|---|---:|---:|---:|---:|---:|
| ChR later generations / ESM ridge | 52 | 28.8% | 0.789 | **65%** | SE unavailable |
| ChR purged generations / sequence+structure GP | 52 | 28.8% | 0.672 | **60%** | SE unavailable |
| ChR component holdout / sequence GP | 54 | 1.9% | −0.178 | **0%** | SE unavailable |
| Kir function, unseen sites / sequence+structure trees | 1,538 | 25.7% | 0.318 | **30%** | **10%** |
| Kir function, region transfer / conservation | 1,835 | 30.7% | 0.305 | **55%** | **25%** |
| Kir surface, unseen sites / sequence+structure trees | 1,529 | 40.9% | 0.346 | **87.5%** | **73.8%** |
| Kir surface, region transfer / WT null | 1,830 | 48.1% | 0 | 48.1% expected ties | 26.0% expected ties |

![Gain selection](figures/gain_selection.png)

On the ChR generation test, ESM ridge captures **13 of 15 gains among its top
20**, and 8/10 among its top ten. Conservation gets 10/20, sequence ridge 12/20,
and a sequence GP 13/20. Thus a large foundation or new physical simulator is
not necessary to see signal here. ESM-versus-conservation paired bootstrap
P20 improvement is +0.15 with exploratory interval **[−0.05,+0.35]**;
MAE improves by 0.176 nA. The ranking improvement over cheaper methods remains
uncertain. The later sequences were selected by the original study's engineering
process, so this is an enriched panel, not an unbiased future search space.

The component split loses ranking and misses its single gain. That is a real
transfer failure but a weak statistical test of gain precision, with only one
positive. It does not prove ChR design cannot work. The 95% purge retains some
ranking signal; no result demonstrates transfer to a new opsin backbone or ACR2.

A stricter **exploratory** utility check asks for a current gain and off-kinetics
no slower than the slowest parent (50.919 ms). Among 44 temporal-test sequences
with measured kinetics, only two meet both constraints; current-only ESM ranking
has **5% joint P20**. Eight missing kinetics are not counted as failures. This
is a tradeoff diagnostic, not a preregistered universal definition of usefulness:
slower closure can be acceptable for some applications. It shows why higher
current alone must not be marketed as general neuronal improvement.

Kir's function rankings are much less reassuring. Some unselected models reach
60% point-gain P20, but selection by validation MAE does not recover that behavior
reliably. After adding the observed WT-control spread to the noise filter,
function-gain prevalence falls to 2.3%, and selected-model P20 is only 5%.
Trafficking remains a stronger auxiliary task (63.8% P20 with that extra filter),
which must not be counted as a successful function predictor. In an oracle
post-evaluation subset with near-WT measured surface scores, selected function
P20 is 45% against 28.4% prevalence; measured test trafficking never entered
training. This is a confound diagnostic, not an executable selection rule.

## Does physics help?

[Paired ablations](paired_physics_ablations.json) compare the same learner with
and without structural descriptors. Bootstrap resamples Kir sites; temporal ChR
resamples constructs, conditional on their related library. Multiple comparisons,
related sequences and small tails prevent confirmatory significance claims.

- ChR ESM ridge + structure changes P20 **65%→70%**, but worsens MAE
**0.472→0.519 nA**. The P20 difference interval is [−0.05,+0.15].
Sequence GP + structure stays **65%→65%**, with negligible error change.
- Kir function ESM ridge + structure improves MAE **0.455→0.446**, while
P20 worsens **45%→40%**. Trees improve error slightly but P20 drops
**60%→30%**; gain-tail improvement is not established.
- Kir trafficking trees + structure improve MAE **1.579→1.341 score units**
(about 15%), with paired error-difference interval [−0.331,−0.152]. However
P20 changes only **85%→87.5%**, with interval [−0.300,+0.150]. Structure helps
bulk phenotype prediction here; reliable additional gain selection is unproved.

MscL explicitly tests a mutation-to-parameter mapping, not arbitrary per-mutant
energies. WT energies/areas calibrate the model; one global hydropathy coefficient
shifts wetted-state energies, optionally adding one global volume-area coefficient.
Withhold G22 when fitting V23T/D, then withhold V23 when fitting G22N. Average
energy error increases **29.2→52.6 kT** versus WT-null; reconstructed equilibrium
current error increases **0.177→0.268** (hydration only), or **0.229** with area.
A fit can improve a particular current curve while predicting the wrong state
energies/areas through compensation. Only three mutant genotypes/two sites exist;
no protective-benefit precision or statistical generalization claim is possible.

![MscL parameter transfer](figures/mscl_mapping_failure.png)

The limiting issue differs by task: coarse descriptor/state approximation for
ChR/Kir; uncertain proxy/gain labels for Kir function; and an unvalidated
mutation-to-energy/area mapping plus sparse data for MscL. No expensive MD
infrastructure was built, and none of these failures is a model-family NO-GO.

## Uncertainty, compute and the next decision

Nominal 90% ChR intervals cover only **73.1%** of generation-test labels and
**67.3%** after the purge. GP intervals can be worse. Most models make zero
lower-bound gain calls, or only one, despite positive rank enrichment. Residual
intervals reuse model-selection validation data and are not guaranteed conformal
intervals. A successful top-k ranking is not calibrated certainty about an
individual unmeasured sequence.

All runs used CPU because CUDA was unavailable in this execution environment.
ESM feature extraction took **29.8 s for Kir and 5.7 s for ChR**. The initial recorded
91-case fitting/validation searches sum to **9.1 s**, excluding imports,
feature extraction, source retrieval and file handling; model-process peak RSS
was **425.7 MiB**. These are measured small-model runs, not a large-model or
GPU benchmark. Eight tests verify numbering, immutable group separation,
null/tied ranking, label provenance and tension/occupancy limits. All **89,570 held-out prediction rows** were reproduced exactly from cached
features on refitting. See [the validation record](validation.json) and
[initial resource measurements](first_run_resources.json); source-label hashes
are checked before loading.

Ranked computational shortlist:

| Rank | Protein / observable | Computational status | Eventual minimal measurement |
|---|---|---|---|
| **1** | Cation-ChR recombinations / peak photocurrent with an explicit kinetic tradeoff | **Conditional modeling GO within the measured parent library.** Strongest direct functional evidence; family transfer and multiobjective utility unproven. | Peak current and off-kinetics under controlled light/voltage, initially electrophysiology. An optical voltage proxy could reduce later screening cost only after calibration against these endpoints. |
| **2** | Kir2.1 / trafficking, with function assessed separately | **Auxiliary phenotype modeling GO; useful function evidence insufficient.** Surface gains are predictable, not a substitute for channel performance. | Surface abundance plus matched voltage-dye function; selected controls need direct current confirmation. Small-panel optical measurement need not repeat an entire DMS/NGS campaign. |
| **3** | MscL / tension-dependent gating with a leak constraint | **Specific global mapper failed; target-level evidence insufficient.** Do not choose it because survival can be cheap. | P_open versus calibrated tension and basal leak. Cheap osmotic survival would be a distinct downstream phenotype requiring a validated mapping. |

No combination yet demonstrates predictive viability, neuronal utility and an
inexpensive validated assay together. ChR is the best **next computational task**
on predictive evidence and direct neuronal relevance; its direct validation is
not inherently inexpensive. This does not select an assay, target commitment or
variant panel.

**The most informative next computational experiment:** freeze a joint
current/kinetics objective at specified illumination and an evaluation set with enough genuinely improved
sequences in an independently collected recombination round or new parental
component. Compare sequence-only GP/ESM with a targeted structure-contact
ablation, select models by validation utility rather than generic MAE, and test
rank precision plus uncertainty under the predefined transfer split. Use the
current study's training data to develop this; do not retune against these test
results and call that a new confirmation. If such data cannot be retrieved,
state the power/coverage limit rather than declaring a target-level NO-GO.

The most confidence-limiting missing evidence is an independent, sufficiently
populated useful-gain test with matched conditions and tradeoffs—not GPU capacity
or the failure of a single simulator. Larger pretrained models, richer physical
models and better losses remain possibilities; this session neither tests nor
rules out their ceilings.
