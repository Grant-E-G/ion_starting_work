# Statistical controls for membrane-protein engineering

October 20, 2026. This is the current workflow policy for new analyses. The
[attached proposal](../../sources/statistics/proposed_protocol_2026-10-18.md)
is preserved as source material; its implementation checklist is not a record
of completed work. Existing benchmark artifacts and the OmpF freeze are unchanged.

## Current evidence and risk

The [exposure register](../../sources/statistics/exposure_register.csv) records
existing corpora as development evidence. Numeric checks are E0; functional
analyses of inspected corpora are E1. Historical per-fit train/test separation
is useful but does not undo subsequent human/agent adaptation. None of the
registered corpora currently supplies a protected confirmation panel. The
historical run inventory is incomplete; do not invent an append-only history.

E2 describes a prespecified internal assessment of a fixed choice procedure;
E3 requires an untouched, condition-matched panel and an independent evaluator;
E4 records a prospective physical experiment. These labels describe design and
exposure, not a guarantee of success or statistical validity. A failed prospective
experiment remains prospective evidence. A biological replicate or seed is not
an independent mutation site, parent lineage or scientific replication.

The main current risks are inspected-test reuse, flexible gain definitions,
small numbers of positive groups, many feature/model/ranking comparisons and
selection of a favorable endpoint after looking. Changing seeds, adding nested
CV or adjusting the final selected p-value cannot repair that exposure.

## Workflow for every new analysis

1. Write a claim card from the [template](../../sources/statistics/claim_template.json).
   Specify one primary utility, reference/parent, assay, minimum useful effect,
   constrained tradeoffs, candidate pool, selection algorithm, comparison family,
   failure interpretation and budget. Put all seeds, tuning choices, exact data
   and weight revisions, upstream label exposure and code commit in the hashed
   analysis/provenance attachments. Unknown contamination must remain unknown.
2. Define independence for the deployment claim. Site transfer groups all
   substitutions of each site; parent transfer requires shared-lineage control;
   publication transfer uses connected source components. Paired function and
   surface measurements stay together. Supply precomputed connected-component
   IDs where multiple relations imply overlap; a single arbitrary group column
   does not discover biological dependencies. Fit transforms on training only.
3. Use group-aware inner tuning and outer assessment of the whole selection
   procedure when sample size permits. Report all declared deployment splits.
   Continue to label inspected corpora E1. Before expensive work, run grouped
   synthetic nulls through the entire selection procedure, including choosing
   features, metrics and winners. Preserve intentional leakage controls and
   failures. Permutations require an exchangeability justification.
4. Freeze predictions, partition, analysis and provenance with the audit tool;
   record submission before execution and record failures as well as successes.
   Each changed analysis is a new submission with a deviation/exposure note.
   For computational development, predictions can be frozen after fitting but
   before requesting protected evaluation. E4 predictions must precede outcomes.
5. Evaluate against unchanged measured parent, WT, best available constituent,
   simple chemistry/additivity, sequence and matched physical/random controls
   as appropriate. Compare on the same eligible constructs. Record exclusions,
   censored outcomes and missingness; never silently convert them to zero.
6. Report effect sizes and uncertainty at the biological grouping unit. Include
   candidate-pool size/prevalence, top-k site/parent diversity, independent positive
   groups, paired baseline differences, tradeoff violations and sensitivity to
   leaving out each major cluster. With few positive groups, report insufficient
   support rather than a precise-looking confidence interval. No universal
   positive-count or minimum-effect cutoff is established here; justify it for
   each assay and decision using uncertainty and prospective power simulations.
7. Protected confirmation uses one locked analysis submission per declared
   comparison family. Freeze all tested contrasts, alpha and multiplicity method
   before release. Holm can control a small family of valid tests; it cannot fix
   invalid adaptively selected p-values. Further tuning consumes the panel for
   future confirmation. Ordinary intervals assume the declared sampling/stopping
   plan; repeated interim inspection requires a justified sequential design.
8. Before a lab decision, present the evidence tier, baseline lift, independent
   positive support, uncertainty, workload/cost, and pass/repeat/stop rules.
   Distinguish assay feasibility, an exploratory scientific gamble and a
   confirmatory design. E3 is not mandatory for a small information-generating
   pilot; unvalidated success probability must be stated. Count every assayed
   variant, including failures, and repeat promising results using fresh
   biological preparations. Never expand sample size until significance appears.

## Implemented now and remaining work

Implemented: document precedence, retrospective exposure register, machine-readable
claim template, local hash/freeze/ledger tool and adversarial integrity tests.
The Python standard library keeps this small audit layer compatible with the
existing Python experiment scripts without another scientific dependency stack.

The tool detects declared group overlap, changed frozen artifacts, duplicate
submission/outcome entries and edited ledger entries. It does not verify that
metadata are truthful, inspect training code for leakage, check prediction rows
against candidates, analyze statistical power or compute valid p-values. New
experiment runners do not yet log automatically. Log each executed fit or an
explicitly enumerated batch with a complete per-fit attachment, not only the
winner; registering one selection procedure alone is not a full run ledger.

Local hashes are tamper-evident relative to a separately retained digest; they
are not immutable storage or protection against a writer rewriting the whole
chain, truncating it or creating another ledger. The external evaluator/decision
owner must retain the submitted digest and enforce one release per panel across
claims and sessions. Labels accessible in this workspace cannot be called hidden.
A second agent in the same filesystem is not evaluator isolation.

Next implementation milestones, in order:

- Wire run-start, completion, failure and artifact records into the next chosen
  development runner; preserve its full search and prior exposure.
- Complete Kir architecture-matched random-feature readout comparisons under E1,
  with frozen development endpoints and all results retained. This is unfinished
  scientific work, not required to install this policy.
- Build a group-aware nested selection harness and null-selection stress test
  using the actual group/positive structure. Set a falsifiable false-promotion
  criterion before examining its simulation results. Do not sell a toy null
  simulation as validation of the real adaptive workflow.
- Establish an external evaluator and new panel with restricted label access;
  reserve it before exploration. If unavailable, explicitly stay at E1.
- Write an assay-specific E4 card once C5R workflow and target are chosen,
  including biological replication, sample-size rationale, fixed stopping,
  sequence verification, controls, raw-data schema and all candidate predictions.

No new benchmarks, random-control comparisons, null-selection experiment or
biological experiment were executed in this integration step.

## Methodological basis

[Cawley & Talbot (2010)](https://www.jmlr.org/beta/papers/v11/cawley10a.html)
explain selection-induced optimism even when a model-selection criterion is
estimated by cross-validation. [Blum & Hardt (2015)](https://proceedings.mlr.press/v37/blum15.html)
provide a specific adaptive leaderboard method; rounded feedback alone is not
that method. [Ramdas et al. (2018)](https://proceedings.mlr.press/v80/ramdas18a.html)
study sequential false-discovery control with assumptions on the p-values;
this is not a remedy for an already exposed test. We implement none of those
advanced feedback/FDR mechanisms here. Default to a fixed plan and one release.
