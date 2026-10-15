# External review brief — C5R predictive-physics sprint

The founder wants an independent assessment before authorizing the next large
compute block. This planned six-hour sprint was interrupted by token exhaustion;
new experiments are stopped and completed artifacts have been cleaned up. The
scientific objective is unchanged: select useful membrane-protein modifications
using existing models and public data, without creating a large new experimental
training set. Local hardware is an RTX3080Laptop16GB. OmpF remains frozen. No
experimental target, variant panel, purchase or C5R laboratory request is approved.

Please review the [decision report](decision_report.md),
[quantitative appendix](quantitative_results.md), and
[reproduction instructions](../../code/experiments/sprint/README.md). These
summarize actual predictions, not an architecture proposal. The accompanying
review archive contains code, source/policy manifests, metric tables, selected
prediction slices and numerical-check records. Large raw caches and weights are
excluded; their provenance/retrieval information is retained.

## What was actually done

- Audited Barethiya2026's five released functional datasets and physical features;
  implemented an executable CNN/GCN port, repaired source encoding problems,
  tested grouped splits, physical ablations and published architecture settings.
  This is **not** an exact reproduction of the paper's original split scores.
- Recovered BKpred's exact473 row identities/30 input columns/target transform;
  reproduced random-split performance; tested numeric445-record site/publication
  holdouts. Corrected the released plotting function's MAE/RMSE naming mismatch.
- Generated cheap matched-WT mutation energies using native EvoEF2; executed
  source-only METL physical checkpoints, ENCoM/NRGten dynamics and approximate
  pore hydration. Tested numerical behavior and stronger nonphysical controls.
- Used GPU ESM8/35/150M, ESM-1v650M and ESM-2 3B; actual-mutant embeddings,
 35M frozen/LoRA adaptation, published-style METL adaptation and gain classifiers.
  The1297 neural fits include overlapping seeds/configurations; they are not1297
  independent validations.
- Added independent BK2024 genotypes, ADRB2 repeated signaling data and a raw-count
  reconstruction of Wu2016 GB1. Reused prior frozen Kir2.1 paired-function/surface
  partitions for additional physical-pretraining/sequence comparisons.

## Findings that deserve scrutiny

1. **BK mutation-energy increment is not established.** Withheld-site fixed-RF
   correlation changes0.227→0.194 and left-shift P20 0.21→0.17 when exact released
   energies are added to WT geometry/evolution. That baseline already has WT
   physical information. Source conditions/species/auxiliary subunits are mixed.
   ENCoM on a matched259-record TMD cohort does not beat geometry or shuffled
   controls after fixing a near-constant-feature numerical failure.
2. **Known parents explain impressive apparent gains.** In10 independent BK
   genotypes, four large left shifts all inherit L312A. Known-parent-only MAE is
   16mV; transferred sequence/energy models do worse and fail to predict added
   modifications better than no change from the matched parent.
3. **Physical pretraining has real but limited positive controls.** GB1 binding-
   pretrained versus matched standard-physics adaptation gives site-held-out
   P20 0.25 versus0.13 at1000+256 labels. GFP bulk correlation improves more
   consistently than brighter-than-WT selection.
4. **Independent GB1 higher-order selection is information-dependent.** All four
   sites withheld from training: physical readouts do not beat a chemistry
   baseline. Given2242 existing component measurements, kernel/sequence/physical
   readouts can select gains. A validation-MSE-selected physical latent readout
   has90%WT-gain P20 but0% for beating the best measured double parent; the
   validation-selected sequence kernel has30%. An exploratory sequence+physical
   readout reaches55% on that harder endpoint,65% with measured-parent-aware
   ranking. Its selection-rule audit has only six validation positives and was
   developed after inspecting the test. These are leads, not confirmatory claims.
5. **Membrane tradeoffs remain difficult.** ADRB2 native-core tests contain only
   five activity gains/one constrained gain. Kir site tests have1494 variants,
   287point joint gains and47 approximate-SE-supported gains. At1256 labels,
   adding physical attributes to a650M sequence classifier changes joint P20
   0.25→0.35; the paired site-bootstrap difference interval includes zero.
   Proxy gains are not measured intrinsic currents or neuronal efficacy.

## Important limits and unfinished work

- All results are retrospective. New model families and follow-up utility rules
  on inspected corpora are exploratory even where coefficient/hyperparameter
  fitting uses only development labels. Many comparisons were made without a
  global multiplicity correction.
- Six architecture-matched random Kir1D/3D feature caches were generated at three
  fixed seeds. **Their functional readout comparisons were not run.** This is the
  clearest unfinished attribution test; random-feature generation alone proves
  nothing about physical-pretraining utility.
- METL physical targets are standardized separately per PDB; normalized state
  subtraction is not calibrated free energy. EvoEF2 lacks explicit lipids and
  backbone adaptation. ENCoM is a truncated monomer harmonic descriptor, not a
  gating barrier. The pore extractor is approximate, not native CHAP/MD.
- BK endpoint censor flags and assay heterogeneity limit labels. GFP/GB1 WT
  references were verified; other soluble top-decile metrics are not WT gains.
  Wu's processed single scores reuse Olson labels; raw independently measured
  values were used instead. Kir function/surface are distinct proxies and SE
  filters omit full reference/biological uncertainty.
- Numerical bugs and failed approximations are explicitly separated from model-
  family limitations. Original unstable diagnostics remain available and must
  not be pooled into cleaned comparisons.

## Requested review output

Please give a short decision memo answering:

1. Which reported physics increments survive the actual controls, data access,
   validation selection and phenotype definitions? Identify unsupported claims
   or implementation/data issues, with filenames where possible.
2. Is the strongest GB1 result evidence for a reusable physical predictor,
   target-specific empirical calibration, or a test-aware selection artifact?
3. Does Kir's physical-pretraining signal justify a membrane follow-up, and which
   random/sequence/geometry controls are necessary before that claim?
4. Recommend **one** next computational experiment with a falsifiable hypothesis,
   frozen evaluation, success/failure gate and bounded local resource budget.
   Prioritize useful parent-relative mutations and functional tradeoffs.
5. Specify the minimum missing evidence. Do not recommend a large integrated
   simulator, repeat OmpF tuning, choose a laboratory target, or request materials.

The current recommendation is conditional continuation of predictive validation,
with source-only physical pretraining as the leading method class and strong
sequence/kernel/parent controls. It is not a prospective membrane-design GO and
not a fundamental NO-GO for physics-based engineering.
