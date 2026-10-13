# Protein-model taxonomy and evidence requirements

October 13, 2026. This qualifies the previous nearby-dataset/model assessment: published benchmark associations identify methods to investigate; they do not establish useful prospective design or justify a target automatically.

## Classify by learning target, inputs and validation

Architecture, parameter count and publication date are insufficient classifications. Record (1) what observations trained the model, (2) the prediction target, (3) inference inputs, (4) adaptation labels, and (5) evaluation conditions. Categories overlap: a sequence language model can supply representations to a folding model or a phenotype predictor.

| Family | Examples | Typical training information / target | Output and relevance |
|---|---|---|---|
| Sequence language models | ESM-2, ESM C, AMPLIFY, ProGen | Natural sequences; masked-token reconstruction or next-token prediction | Representations and sequence probabilities. Useful priors/features; not a calibrated directional transport predictor. |
| Evolutionary/homology models | EVE, EVmutation, MSA/retrieval methods | Related aligned sequences; evolutionary compatibility/covariation | Mutation compatibility. Needs homolog coverage and tests against assay-specific phenotypes. |
| Structure prediction | AlphaFold2/Multimer, AlphaFold3, ESMFold | Structural coordinates plus sequence/evolutionary information; some pipelines also use predicted structures for training | Predicted coordinates and confidence. Useful for mapping residues and constraining hypotheses. Does not directly predict current or closing rate. |
| Structure-conditioned sequence design | ProteinMPNN, ESM-IF1 | Backbone geometry and compatible sequences | Sequence proposals/scores for a backbone. Fold compatibility does not establish channel function. |
| Phenotype-supervised predictors | Sequence/contact Gaussian processes, Kermut, transformer plus a trained phenotype head | Measured sequence–phenotype observations, often combined with pretrained features | Predictions for a specified assay. Most directly aligned with the task but limited by labels, confounds and extrapolation. |
| Mechanistic simulation | Molecular dynamics, enhanced sampling, photochemical calculations | Physical models/parameters and initialized molecular systems rather than only statistical sequence labels | Dynamics/energetics conditional on modeling assumptions. Potentially relevant to gating but expensive, specialized and sampling-limited. |

ESM3 and similar multimodal generators span categories. Conditional generation still needs independent functional evaluation. Structure-aware variant scorers such as SaProt are distinct from structure predictors and are not automatically phenotype-supervised.

## AlphaFold specifics

[AlphaFold2](https://www.nature.com/articles/s41586-021-03819-2) integrates sequence alignment/template information with a learned structure-prediction system. [AlphaFold3](https://www.nature.com/articles/s41586-024-07487-w) extends prediction to biomolecular complexes, including ligands and nucleic acids, with diffusion-based coordinate generation. Neither is simply a larger version of the masked protein models benchmarked locally.

ESMFold combines a protein language-model representation with a structure-prediction component. It belongs in the folding category despite the ESM name. Conversely, AlphaMissense is an AlphaFold-derived variant-pathogenicity system, not a folding result interpreted as current. Its [official implementation](https://github.com/google-deepmind/alphamissense) supplies precomputed human predictions but not trained weights for arbitrary new targets.

For GtACR2, a credible retinal-pocket/pore structure is useful, but conductance and closing depend on conformational states, their populations and transitions, chromophore photochemistry and assay conditions. Predicting a plausible conformation does not determine those quantities. Multiple generated structures are not automatically a thermodynamic or kinetic ensemble. A model can assign high structural confidence to WT and a damaging mutant; similar coordinates do not establish equal function. The [AlphaFold DB FAQ](https://www.alphafold.ebi.ac.uk/faq) explicitly cautions against expecting destabilizing mutations to produce unfolded predictions. pLDDT is local coordinate confidence, not predicted fitness or engineering benefit.

## Where evidence can mislead

- Wrong label: expression, growth proxy, wavelength, current and gating kinetics measure different things. Correlation with one does not certify another.
- Wrong generalization: random splits can put substitutions at the same residue or near-identical recombination constructs on both sides. Residue/source/round/backbone grouping should match the intended next experiment.
- Too much training data: performance after training on thousands of mutants does not establish a cheap four-to-eight-variant design loop. Require learning curves at plausible label budgets.
- Damage-dominated scoring: a strong overall correlation can be driven by catastrophic loss-of-function and have little ability to find better-than-reference variants. Report improved-tail enrichment and uncertainty separately.
- Model/selection tuning on the test set: feature selection, adaptation, hyperparameter search and choosing among backbones must occur within training/validation only. Reserve an untouched final evaluation.
- Data exposure: distinguish supervised label leakage from exposure to related sequences during pretraining. They are different risks and need separate audits. Check homolog identity, dates, source overlap and released model/scoring versions.
- Pseudoreplication: thousands of rows can describe one protein, few parent blocks or shared preparations. Uncertainty should respect relevant grouping and assay noise.
- Unequal resources: structure/MSA/retrieval models use additional information. Compare identical evaluation splits and disclose inputs, labels, ensembles and compute.
- Proxy optimization: model-guided searches can exploit prediction errors; rescoring with the same model or a related folding model is not independent functional confirmation.

Publication venue, model age and parameter count are not substitutes for these checks. Older methods are valid baselines if their task assumptions fit; newer methods need the same scrutiny. [FLIP2](https://flip.protein.properties/) provides explicit nonrandom generalization splits and reports simple methods often competitive with fine-tuned language models, supporting this evaluation approach rather than a blanket conclusion about any model.

## Consequence for this project

The previous local work established hardware fit and exposed a weak six-mutant likelihood diagnostic. The nearby audit established data availability and some externally reported associations. Neither established a locally validated engineering predictor. The quoted Spearman correlations are rank association, not a percentage of correctly predicted improvements.

Before choosing a model/scaffold, freeze one phenotype and intended generalization task; audit independent labels and assay controls; compare literature, conservation and regularized sequence/contact baselines against frozen and adapted language models under nested grouped evaluation. Measure improvement-tail selection at equal small candidate budget and low-label learning curves. Structural models contribute constraints/features whose added predictive value must be tested, not an automatic score for better function.

A method passes only if it supplies usable signal for the intended design decision beyond the baseline and with uncertainty compatible with the experiment budget. If none does, change the scaffold/phenotype or report computational no-go. There is no current claim that AlphaFold, any large language model or the enlarged datasets have already passed this gate.
