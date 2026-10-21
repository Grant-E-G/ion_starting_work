# Statistical firewall for autonomous membrane-protein engineering

Version: 2026-10-18. Status: proposed governance protocol; not implemented or validated. Applies to computational benchmarks, externally published labels, physical simulations, and eventual C5R experiments.

## Goal

Let an autonomous agent explore thousands of computational hypotheses at low cost without promoting adaptively selected performance into unjustified claims about mutation-function prediction. A model can be interesting without being confirmed. Repeated exploratory checks are encouraged but must be recorded.

## 1. Evidence levels

- **E0 engineering:** installs, unit tests, numeric convergence, simulation stability, force/energy checks. No claim about experimental phenotype.
- **E1 exploratory:** training, repeated development-set evaluation, retrospective analysis of previously inspected benchmarks, literature-selected variants, and any benchmark with labels seen or used in human/agent decisions.
- **E2 internally validated:** a fixed pipeline evaluated once under a prespecified grouped/nested analysis; independence, leak risks, and confidence limits disclosed. Nested CV does not erase prior exploration across many agent sessions on the same corpus.
- **E3 externally confirmed:** frozen pipeline + endpoint + predictions evaluated once on a genuinely untouched, condition-matched independent panel by an evaluator who has not supplied labels or performance feedback during development. Disclose public-pretraining overlap and prior exposure.
- **E4 prospective:** before biological outcomes exist, lock candidate sequences, reference/parent, prediction intervals, target assay/conditions, expected outcomes, controls, and analysis. Then run the physical experiment and evaluate every assayed candidate. Replicate independently where feasible.

Never promote E1 to E3 just by changing seeds, reshuffling the same observations, or calling a model "zero-shot" after seeing outcomes. Public independent publications can serve as external retrospective checks only when analysis plans and exposure histories make their independence credible.

## 2. Threat model and independence

Count biological independence at the level appropriate for the scientific claim. Track `protein_family`, `scaffold`, `construct`, `parent_lineage`, `mutation_site_set`, `assay`, `laboratory`, `publication`, `experiment_day`, `biological_replicate` and `measurement`.

For single mutant site transfer, group all substitutions at a site. For combination prediction, group shared parents, linked constituent combinations and recombination lineages. For assay transfer, hold out entire protocols/labs, not randomly separated readouts. For publication transfer, group connected references/underlying datasets, not citation strings. Keep functional and trafficking readouts on the same variants in the same split. Each split must correspond to an explicit deployment scenario.

Report total rows, unique constructs, independent sites, independent parents, independent studies, unique *positive* sites/parents, and measured control groups. If there are 20 positives at one site, do not present them as 20 independent gain mechanisms.

## 3. Role separation and test access

- **Explorer (agent):** unrestricted work on E0/E1 corpora; may run many methods, benchmark physics, and inspect failures.
- **Evaluator (separate trusted process/person):** keeps E3 labels and scorer inaccessible to Explorer, receives an immutable prediction artifact, computes prespecified output once, and stores raw outcomes and audit log.
- **Decision owner:** authorizes a prospective small experiment only after seeing evidence tier, comparison to baseline, uncertainty and biological cost.

A hidden holdout is not hidden when labels are in the agent's accessible filesystem or logs. A separate agent prompt is not a security boundary. Use access permissions / isolated evaluator or obtain a genuinely new independent panel. If secure isolation is unavailable, use the result as E1 and explicitly report this limitation.

For any adaptive re-evaluation of a protected test, use a deliberate information-release mechanism (e.g. a tested reusable-holdout/leaderboard method such as Ladder) with its stated assumptions, or mark the set as consumed. Simply releasing rounded accuracy is not a mathematically justified reusable-holdout implementation.

## 4. Predeclared claim cards

Before requesting E3 evaluation or a biological panel, write a machine-readable claim card:

- hypothesis ID, date and git commit; dataset/label/structure/weights hashes, access history
- exact construct, WT or measured parent, phenotype, assay conditions and directional desirability
- single *primary* utility function, constrained tradeoffs (kinetics, expression, basal leak, toxicity)
- clinically/biologically meaningful minimum effect or decision threshold and how set
- candidate pool definition and acquisition/selection process
- target generalization regime (same site, new sites, new parent, new family, new assay)
- frozen model selection procedure, random seed, evaluation budget, baselines
- performance statistic, resampling unit, one-sided/two-sided decision, intervals
- multiplicity family and adjustment, treatment of missing/censored outcomes
- minimum positive-site/parent support needed to interpret top-k claims
- results that would count as a failure; any permitted deviation procedure

After seeing protected outcomes, amendments create a new exploratory claim, not a revised confirmation.

## 5. Evaluation hierarchy

- **Development:** use nested *group-aware* CV where sample size permits: inner folds tune models; outer folds assess the entire choice procedure. Use multiple predeclared deployment splits rather than cherry-picking the most favorable. Already inspected old benchmarks are E1 even when rerun with nested CV.
- **Protected confirmation:** submit ONE locked output per claim. Report outcome for every primary endpoint, all baselines, negative controls and missingness. Any further adaptation consumes the test for future claims unless a formally controlled reusable feedback protocol is used.
- **Prospective lab:** preserve the full candidate list before measurement, not just successful variants; include independent WT/parent, empty vector as relevant, positive and negative assay controls and repeated preparations. Treat expression/trafficking/survival as distinct endpoints.

Prioritize baselines: unchanged measured parent, WT-null, best measured available constituent, additivity/low-order epistasis, simple physicochemical descriptors, strong pretrained sequence score, and compute-matched/random-initialized physical architecture.

## 6. Model-selection and multiplicity policy

Arbitrary E1 exploration does not spend formal alpha but can never yield confirmatory p-values about the selected winner. Track counts of model families, featurizations, metrics, datasets, optimizer objectives and analytic decisions as an analysis multiverse.

At E3, predeclare a small set of primary comparisons and control familywise false positives when a single claim can authorize real lab cost (e.g. Holm-adjusted p-values or simultaneous confidence intervals for predeclared tests). For many prespecified independent biological discoveries, consider Benjamini-Hochberg FDR under its applicable dependence assumptions; use a dependence-robust method when needed. Neither BH nor Holm makes a p-value valid if the evaluator, labels, hypotheses, or stopping rule have already been adaptively exposed.

Online FDR procedures such as SAFFRON address sequential *valid* p-values and require their mathematical assumptions. They are not a substitute for keeping a test independent of ongoing model development. Similarly, conventional confidence intervals and p-values can fail under optional stopping; for lab experiments monitored after each replicate use a prespecified sequential design, alpha-spending or anytime-valid confidence sequence/e-process with assumptions checked.

## 7. Uncertainty and reporting

Always show effect sizes and uncertainty, not just p-values or top-k metrics. Compare methods on the *same* candidate groups, use paired group-level resampling (site, parent, lab, publication as appropriate), and report the number of independent resampling clusters. With very few clusters use transparent sensitivity analyses / leave-one-cluster-out; no precise-looking bootstrap intervals. Account for label SE and between-lab heterogeneity without treating repeated replicates as extra mutation variants.

For top-k selection report: k, candidate pool/prevalence, unique sites/parents among top k and among true positives, hit rate, paired lift over each baseline, calibration and selection-specific uncertainty. AUC=1 on two positives at one site is not a cross-site success. Distinguish gain versus WT, gain versus best available parent, and application-specific joint gain. Show tradeoff and failure counts.

Conformal or Bayesian predictive intervals are optional supplements. Standard conformal coverage requires appropriate exchangeability and proper calibration split; it is not a guaranteed confidence statement for mutations chosen adaptively far outside a training distribution. Bayesian posteriors are conditional on chosen models and assumptions; selecting the most optimistic posterior across many methods is not cured merely by being Bayesian.

## 8. Complete audit ledger

Append-only machine-readable ledger for EVERY executed run, including negative results, with:

`run_id, timestamp, agent_session, git_sha, hypothesis_id, model_family, architecture_id, pretrained_weights_sha, source_data_sha, structures_sha, phenotype, label_definition, target_population, source_exposure, split_id, split_grouping, evaluation_tier, evaluator_id, preregistration_sha, metric_schema_sha, random_seed, compute_cost, success_or_failure, stderr_location, prediction_artifact_sha, parent_control, positive_control, negative_control, comparison_family_id, decision_status`.

All failed runs, timeouts, dataset exclusions, unit corrections, manuscript-selected labels, and post-hoc parameter changes are preserved. Record why models were abandoned. Track paper-level and source-code-level upstream contamination, including experimental assays used in physical-pretraining target generation and in large-model fine-tuning where auditable; unknown is not the same as absent.

## 9. Automated integrity tests

Implement CI tests that fail when: group leakage occurs; a publication-connected component spans training and protected test; preprocessing/normalization fitted on protected data; assay surrogate substituted for endpoint; a test set is renamed to "validation"; multiple metrics silently switch priority; labels are reclassified after peeking without a new hypothesis; identical sequences have conflicting numbering; missing/censored variants treated as zero; physics-pretrained checkpoints contain held-out experimental labels; multiple rounds report the best without the trial count; random seed manipulations improve test without preregistration; a frozen experiment's predictions/analysis are edited after submission.

Construct synthetic null data with the *real observed grouping structure* and run the complete model-selection pipeline repeatedly to estimate false-promotion frequency (a simulation-based diagnostic, not universal proof of frequentist control). Include shuffled physical features, randomized labels at exchangeable group units, random/architecture-matched embeddings, and intentionally leaky splits to verify detectors.

## 10. Promotion and lab authorization

Never allow an E0/E1 result alone to be summarized as "predictive membrane-protein engineering succeeded." Accept a zero-shot external functional signal only within its demonstrated mutation site/parent/assay support.

A prospective lab pilot may still be rational under uncertainty: distinguish **assay setup/measurement feasibility**, **exploratory scientific gamble**, and **confirmatory design**. Each has different evidential standards. If the goal is a first exploratory small panel, prelock design predictions, controls, endpoint and costs and be transparent that probability of success is unvalidated. Do not automatically forbid low-cost information-generating experiments merely because E3 data do not exist.

Before spending, decision owner receives a single summary: evidence tier, exact scientific claim, valid independent positive groups, comparison to simple baselines, uncertainty/false-promotion checks, expected lab workload, and predeclared success/failure interpretation.

## 11. Immediate implementation order

1. Retrospectively classify all OmpF, ChR/ChrimsonR, BK, Kir, METL and GB1 benchmarks E0/E1/E2 honestly with exposure history and correct biological units. Do not retroactively upgrade them.
2. Implement append-only audit logging and immutable claim cards; validate record hashes and grouping.
3. Complete the Kir random-architecture controls and benchmark under development-tier designation, retaining failed hypotheses.
4. Build a trusted isolated evaluation interface and reserve at least one new, not-yet-inspected functional panel if available; otherwise report that independent confirmation is unavailable.
5. Use grouped nested CV for future methods development and run null-selection stress tests on the entire adaptive selection pipeline.
6. Before any lab order or C5R assay, freeze a complete prospective variant-ranking and analysis card.

## Key methodological literature

- Dwork et al. (2015), The Reusable Holdout, Science. https://pubmed.ncbi.nlm.nih.gov/26250683/
- Blum & Hardt (2015), The Ladder. https://proceedings.mlr.press/v37/blum15
- Cawley & Talbot (2010), On Over-Fitting in Model Selection. https://www.jmlr.org/papers/v11/cawley10a.html
- Varma & Simon (2006), Bias in error estimation when using cross-validation for model selection. https://link.springer.com/article/10.1186/1471-2105-7-91
- ProteinGym benchmark design/split caution. https://pmc.ncbi.nlm.nih.gov/articles/PMC10723403/
- Benjamini & Hochberg (1995), FDR. https://academic.oup.com/jrsssb/article/57/1/289/7035855
- Ramdas et al. (2018), SAFFRON. https://proceedings.mlr.press/v80/ramdas18a.html
- Howard et al. (2021), Confidence Sequences. https://doi.org/10.1214/20-AOS1991
- Simonsohn, Simmons & Nelson (2020), Specification Curve Analysis. https://www.nature.com/articles/s41562-020-0912-z
