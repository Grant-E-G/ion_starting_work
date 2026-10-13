# Nearby applications, larger datasets and stronger-model evidence

October 13, 2026. Modeling-feasibility assessment before choosing the physical target/readout. The user's decision rule is authoritative: insufficient confidence in useful design should trigger a target change, not acceptance of an unsupported experiment.

## Decision

**GtACR2 has not passed the computational-design gate. Move the modeling feasibility test to larger, relevant datasets before advancing its experimental route.** The six-mutant diagnostic is not a complete census of all GtACR2 evidence, but this search did not establish a larger, compatible, training-ready GtACR2 transport dataset. Neither a small-panel failure nor successful GPU execution resolves that gap.

There are credible nearby tasks on which models have useful measured signal. Best immediate computational choices are (1) engineered cation channelrhodopsins, the closest family/application bridge, and (2) Kir2.1 function paired with trafficking, a much larger ion-channel benchmark. These are computational target changes; selecting them does not authorize assuming their mammalian assays fit the current bacterial partner workflow. A physical target must pass both modeling and assay-cost gates.

## Retrieved data, not merely search hits

### Engineered channelrhodopsins: strongest nearby application

Downloaded all four public data tables from [Bedbrook et al. 2019](https://www.nature.com/articles/s41592-019-0583-8). Our file audit found:

- Supplementary Data 2: **154 measured records, 154 distinct protein sequences**, all with finite maximum peak-current values; **128** have finite off-kinetics values. Blue/green/red peak and stationary currents, sequences, alignment, recombination block IDs and cell counts are supplied.
- Supplementary Data 1: 61 literature sequence/current records, with source references. These are heterogeneous and must remain distinct from the matched experimental panel; do not add them blindly to one regression table.
- Supplementary Data 3: 1,133 computationally predicted design records. These are **not** additional measured labels.
- Supplementary Data 4: 323 feature-weight records. These are not variants.

The study began with 102 functionally characterized sequences and prospectively produced improved actuators using Gaussian processes. This establishes nearby functional design feasibility using modest statistical modeling. It does not establish transport prediction for GtACR2: these are engineered cation channelrhodopsins, and the mammalian electrophysiology context differs from the bacterial proxy.

Use photocurrent and kinetics as separate objectives with a functionality constraint. Compare the original sequence/contact Gaussian-process approach with frozen transformer features and supervised adaptation. Favor withheld design rounds or recombination/sequence groups over random row splits. Recover the exact experimental-round mapping from the source before freezing a temporal split. The 154-record table should not be misrepresented as 154 independently sampled prospective examples. Transfer to ACRs needs its own test; family membership alone is insufficient.

### Kir2.1: best larger ion-channel test

[Coyote-Maestas et al. 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9273215/) measured function and surface trafficking separately. The original source tables downloaded locally contain 7,033 function rows and 6,987 surface rows, with standard errors. They include a tagged construct and require numbering/control audit. The pinned ProteinGym reference contains **6,963 function records** and **6,917 trafficking records**. Those are different processed counts, not contradictions or additive datasets.

Function is assessed through a voltage-sensitive dye/flow-cytometry proxy for channel-associated resting membrane potential in mammalian cells. This is biologically closer to excitability than a spectral-property task. Separate abundance/trafficking allows us to test whether a predictor contributes beyond predicting expression. It does not make the published assay turnkey in bacteria or turn a proxy into direct gating kinetics.

Recommended enlarged test: residue-grouped held-out prediction of function, with trafficking as a separate endpoint/confound diagnostic; evaluate learning curves at limited training budgets as well as the full dataset. Require improvement-tail enrichment and calibration, not only overall correlation dominated by damaging mutations. WT/reference anchors, synonymous controls, uncertainties and assay score semantics must be audited before labeling variants gain-of-function.

### KCNE1 and OCT1: strong adjacent functional benchmarks

Pinned ProteinGym metadata supplies **2,315 KCNE1 function records** and **2,339 expression records**, and **10,094 OCT1/SLC22A1 activity records** with **9,803 abundance records**. KCNE1 is a potassium-channel auxiliary subunit; its assay depends on KCNQ1 and mammalian growth selection, not an autonomous bacterial channel. OCT1 is a transporter, not an ion channel; activity uses cytotoxic-substrate uptake selection. Both offer larger function/abundance modeling tests. Neither is an automatic physical-project recommendation.

### Microbial rhodopsin wavelength tuning: nearby, but a different claim

Downloaded the [FLIP2 Rhomax split](https://flip.protein.properties/): **884 records, 878 distinct sequences**, published as derived from 75 parental scaffolds. The file has 584 fitting records, 116 validation records and 184 test records. Six sequence duplicates occur within the fitting partition only; one duplicated sequence has wavelength labels differing by 19 nm. Audit duplicates/conditions and use the supplied held-out-backbone split. This is a useful test of phenotype-specific adaptation and transfer across rhodopsins.

The label is peak absorption wavelength. Successful color tuning would be a real photochemical-property engineering result, but it would not establish improved ion transport. Select this task only if that revised objective is acceptable. Do not enlarge GtACR2 transport training with wavelength labels as though they were measurements of the same property. The FLIP2 authors explicitly report difficulty with unseen-backbone and high-fitness generalization and find simple regressors often competitive with fine-tuned models.

### False shortcuts and lower-priority options

- The ProteinGym EnvZ assay has 1,121 records, but its target sequence is a **60-residue interaction domain**, not the full membrane sensor. It measures pathway specificity through a fluorescent reporter. It cannot demonstrate full membrane-protein engineering by itself.
- Human visual rhodopsin datasets primarily measure surface trafficking, and visual rhodopsin is a GPCR, not a microbial ion channel. Do not use their larger counts to imply same-function channel supervision.
- MscL remains an unconfirmed fallback: this targeted search did not retrieve a comparably convenient larger training table plus compelling model-validation evidence. Lack of retrieval is not evidence no such dataset exists. Do not recommend it solely because its assay might be cheaper.
- The broad search returned some soluble-protein engineering datasets; they were not adopted because the current objective is membrane-protein engineering.

## Does a model beyond the local machine solve the problem?

We downloaded pinned **per-assay** ProteinGym results instead of relying on global leaderboards. Values below are reported Spearman correlations, not local reproductions. They are correlations across measured assay variants; they do not prove gain-over-WT prediction.

| Functional assay | ESM-2 650M | ESM-2 15B | ESM C 600M | xTrimoPGLM 100B INT4 | TranceptEVE L | SaProt 650M |
|---|---:|---:|---:|---:|---:|---:|
| Kir2.1 | 0.382 | 0.388 | 0.383 | 0.334 | 0.335 | 0.371 |
| KCNE1 | 0.525 | 0.380 | 0.564 | 0.514 | 0.634 | 0.642 |
| OCT1 | 0.575 | 0.525 | 0.558 | 0.492 | 0.601 | 0.542 |
| hERG/KCNH2, 200 records | 0.280 | 0.248 | 0.401 | 0.159 | 0.509 | 0.271 |

Source: [ProteinGym zero-shot DMS-level table](https://github.com/OATML-Markslab/ProteinGym/blob/144fe22b07dfaeec2b366f2346203a9838a55b4c/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv). The benchmark ESM C release must not be assumed identical to our current Biohub local checkpoint. Confidence intervals/significance of differences and scoring settings are not established by these rounded values alone.

The [xTrimoPGLM authors](https://github.com/biomap-research/xTrimoPGLM) document 100B INT4 inference on an 80 GB accelerator. That is a concrete heavier model available for evaluation, but its listed nearby-task results do not show a scale-driven rescue. AIDO Protein-RAG 16B has OCT1 activity correlation 0.621 in the same table, compared with 0.575 for ESM-2 650M; on Kir2.1 function it reports 0.336. Retrieval/input resources and release details require audit before considering a paid run. No larger model was executed or paid compute purchased here.

The useful alternatives are often richer **inputs or supervised modeling**, not more backbone parameters. [Kermut](https://github.com/petergroth/kermut) combines ESM-2 650M features, structural information and Gaussian-process regression. Published contiguous-position five-fold results are 0.447 for Kir2.1 function and 0.693 for OCT1 activity. ProteinNPT reports 0.689 on KCNE1 function under that supervised protocol. These results require substantial labeled training sets and are not few-label guarantees; supervised and zero-shot evaluation regimes cannot be treated as a clean causal ablation.

A structure predictor or a generative design model can help impose plausibility constraints, but structure confidence alone does not establish improved current or kinetics. This search identified no larger off-the-shelf model with verified prospective superiority on the exact GtACR2 bacterial transport endpoint. That is an evidence gap, not a claim that sophisticated mechanistic simulations could never help.

## Proposed decision gate

1. **Closest-family test:** audit/prepare the 154-record channelrhodopsin panel; compare literature-style sequence/contact modeling, frozen transformer features and a bounded adapter approach. Preserve prospective rounds where recoverable.
2. **Larger channel test:** use Kir2.1 function/trafficking for residue-grouped validation and low-label learning curves. Evaluate whether a model ranks useful variants better than random/conservation/structure baselines, especially above-reference candidates.
3. **Heavier-model test:** use verified published per-assay results and, where available, per-variant precomputed predictions before paying for cloud inference. A paid model needs a specific assay-level advantage or a clearly testable new input/learning method.
4. **Target selection:** advance a scaffold/phenotype only when modeling evidence and a practical assay both support it. If nearby-channel success does not transfer to ACRs, switch the biological target or explicitly change the engineering phenotype. Do not fund GtACR2 variants on generic sequence plausibility.

The first two are now executable dataset choices, not speculation about what might exist. They have not yet been locally trained/evaluated in this turn. The current result is a retrieved-data audit plus externally reported modeling evidence. It supports enlarging the feasibility benchmark; it does not yet satisfy the gate for a new physical experiment.

## Reproducible artifacts

Source files and provenance: [nearby-modeling directory](../sources/nearby_modeling/README.md). Counts, assay metadata and extracted correlations: [audit.json](../sources/nearby_modeling/audit.json), [assay shortlist](../sources/nearby_modeling/assay_shortlist.csv). Reproduction: `python code/experiments/audit_nearby_datasets.py`. The audit script passed Black and mypy. No author emails, wet-lab commitments, new candidate proposals or paid model calls were made.
