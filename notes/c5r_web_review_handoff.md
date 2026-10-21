# C5R web-client review: consolidated source packet

Relative links refer to the original repository. Included documents follow in full; the first document explains precedence.

## Source file: notes/c5r_call_preparation.md

# C5R call preparation and external fact-finding handoff

Prepared October 20, 2026 (America/Los_Angeles). Call expected October 21 or 22; exact date not confirmed.

## Readiness assessment

We have enough material for an independent computational evidence review and for a focused call-preparation investigation. We do not yet have confirmed C5R workflow readiness, matched assay performance, staffing, pricing, or a selected target. The call should resolve those uncertainties before a pilot is scoped.

The existing `notes/sprint/external_review_packet.tar.gz` is a 24 MiB scientific audit packet with code, source/policy manifests, metrics and selected predictions. On October 20, all 381 file entries in its manifest matched the current local files. It omits full prediction caches, raw feature arrays and model weights; it supports documentary/code review, not immediate complete offline reproduction. It contains none of the C5R call-context documents listed below. The new call packet fills that context gap without modifying the frozen scientific packet.

## Objective and scope

Earn a small, reproducible demonstration that computationally proposed sequence changes improve a specified phenotype of a biologically relevant membrane protein. A well-controlled functional proxy can support a bounded startup-stage proof of concept. Neuronal efficacy and specialist electrophysiology are later questions. C5R is envisaged as a force multiplier executing a supplied workflow, not an open-ended assay-development CRO. That operating assumption must be checked on the call.

No target, new variant panel, purchase, or laboratory execution is approved by the scientific reports. Preparing questions does not change that status.

## Which documents govern

1. `notes/funding_stage_poc_scope.md` defines the intended milestone and partner division of work.
2. `notes/sprint/external_review.md` and `notes/sprint/decision_report.md` describe the latest completed computational investigation; the quantitative appendix supplies numbers and caveats.
3. `notes/predictive/decision_report.md` explicitly supersedes the earlier assay-first MscL recommendation. Target selection remains open.
4. `notes/c5r_next_phase_brief.md` and `notes/c5r_experimental_paths.md` supply useful conditional assay alternatives, not a current MscL selection. Existing local workflows can change their ranking.
5. `notes/c5r_gtacr2_pricing.md` contains older public-source capability evidence and planning allowances. Its HPTS-first recommendation is historical, not the current project decision. Prices, availability and present capabilities require verification. The research plan also retains earlier phase statements; do not read every paragraph as current status.

## What the evidence currently supports

Local execution of substantial sequence and physical-feature models is feasible. A general advantage for selecting useful membrane-protein mutations from added mutation-specific physical energies has not been established. BK transfer exposed a known-parent shortcut. Some GB1 physical-pretraining/combination results are positive but depend on existing labels and exploratory analysis. Kir2.1 offers limited, uncertain evidence on function/surface proxies; architecture-matched random-feature readout comparisons remain unrun. These findings do not choose a laboratory target.

Keep separate: mutant improvement over WT versus improvement over a known parent; expression/trafficking versus channel function; bacterial pH or survival versus intrinsic conductance; retrospective prediction versus prospective experimental success. Public hardware documentation does not demonstrate a locally validated assay.

## Questions for C5R, in priority order

1. **Existing workflow:** What live-cell expression and membrane-protein functional assays have you actually run successfully? Could you show an SOP and representative raw WT/background/control traces or culture-level data? Which parts are routine today versus new development?
2. **Materials:** Which relevant hosts, verified plasmids, reference/altered-function controls and reagents are already on hand and usable for this collaboration? Consider MscL, OmpF, GtACR2 and any better-supported existing scaffold. Record exact construct/host identities and access constraints.
3. **Execution responsibility:** Given a supplied protocol and analysis specification, which culture, induction, collection, washing, plating, illumination, measurement and QC steps can you perform? Who owns manual steps, protocol debugging and repeats? What new work would fall back to us?
4. **Measurement headroom:** What effect sizes, background, day-to-day variation and biological replication can your existing workflow resolve? Can it distinguish a modest improvement from abundance, viability, growth or detector artifacts? Ask for existing data before agreeing to new runs.
5. **Specific configuration gaps:** Prior public documentation names CLARIOstar Plus, STARlet and PCR/small-volume preparation equipment. For the actual shortlisted assay, confirm relevant installed modes, kinetics/export and scheduling; separately establish live-bacterial handling, CFU capacity, expression QC or calibrated light/pH measurement as needed. Avoid a generic request for a new reader inventory.
6. **Data delivery:** Can you return unaggregated biological-replicate measurements, plate/sample maps, blanks and controls, sequence/construct IDs, units, timestamps, processing settings, failed samples and protocol deviations? What format and turnaround are routine?
7. **Smallest control demonstration:** Based on existing stocks and SOPs, what is the smallest WT/background/established altered-function comparison you can execute reproducibly? What result would show assay feasibility, and what would trigger a repeat or stop? This is a scoping question, not a request to begin.
8. **Real resource quote:** Separate marginal consumables, sourcing, commissioning, staff hands-on time, instrument access, overnight/calendar time and repeat allowance. What is in kind, billable or unavailable? Who owns the workflow, resulting data and any publication/IP decisions?

## Branches after the call

- An established assay with controls, raw data and a responsible operator: evaluate target relevance and available predictive evidence, then write a bounded control pilot for approval.
- Routine lab steps but no demonstrated functional readout: scope assay transfer explicitly; do not describe it as routine execution or select model-designed variants yet.
- Missing stocks, staff or essential measurement capability: obtain a concrete gap/lead-time/cost account and consider a different existing scaffold.
- A successful assay alone does not validate the predictor. A retrospective predictor alone does not establish the partner's assay readiness.

## Copy/paste prompt for the web-client investigation

I am preparing for a C5R (c5r.net / SciUniverse / Facility-0) call on October 21 or 22, 2026. Read the attached handoff first. Help me determine exactly what to ask C5R to establish whether we can run a small, credible membrane-protein engineering proof of concept with their existing workflows.

Use the document precedence above. Keep target selection open. Do not inherit the older MscL-first or HPTS-first recommendations as decisions. The intended partner executes a supplied workflow; open-ended assay invention and specialist electrophysiology are outside the present milestone. A controlled functional proxy is acceptable if its claim is precise.

First extract our objective, completed evidence, unresolved uncertainties and contradictions in the documents. Then research current primary sources for C5R's demonstrated physical workflows and the most relevant published assay precedents. Distinguish physical execution from simulation, installed hardware from possible model options, published protocols from local validation, and public evidence from assumptions. Cite exact primary-source URLs and dates; mark inaccessible evidence as unverified. Do not convert absence of public documentation into absence of capability. Do not treat old planning prices or benchmark API costs as a lab quote.

Compare MscL survival, OmpF apparent substrate access and GtACR2 transport-associated pH, and consider another scaffold only if a documented existing C5R workflow provides a clear advantage. For each, explain what phenotype the measurement actually supports, available controls, key confounds, new development required and whether useful mutant prediction has supporting evidence. Do not produce an elaborate new simulation architecture or assume we must make a large training dataset.

Deliver: (1) a one-page call agenda with at most eight prioritized questions and why each answer changes a decision; (2) an evidence/unknowns table with source, confidence, who can answer, and consequence; (3) a conditional target/readout decision tree; (4) the minimum raw-data/SOP/examples to request; (5) a draft smallest control-only pilot for the best conditional path, with explicit assumptions, ownership, resource unknowns and proposed pass/repeat/stop criteria; (6) remaining computational review questions, separated from questions C5R can answer. Label proposed thresholds as planning judgments, not measured performance. Ask me only for private context that attached documents and public research cannot resolve. Do not contact anyone, order materials or imply experimental authorization.

## Upload instructions

Start with `c5r_web_review_handoff.md`, which concatenates this guide and the selected source documents. Use `c5r_call_review_packet.zip` if the reviewer can unpack attachments; it contains the same sources as separate files and a SHA-256 manifest. For a deeper code/data audit, additionally supply the existing `notes/sprint/external_review_packet.tar.gz`. This small call packet alone is a document-level handoff, not the full scientific data/code archive.

This preparation audits local artifacts. It does not refresh public websites, supplier prices, private correspondence or C5R's current operating state. Those are explicit tasks for the fact-finding investigation and the call.


---

## Source file: notes/funding_stage_poc_scope.md

# Funding-stage membrane-protein engineering POC

## Authoritative scope correction

The user clarified that this project is part of a developmental system intended to demonstrate meaningful engineering of biologically relevant membrane proteins at the startup-funding stage. The lab partner is a force multiplier for a supplied workflow, not a conventional CRO and not a specialist electrophysiology provider. Costly patch-clamp validation is outside the present timescale and partner capabilities.

This supersedes the earlier recommendation to obtain an external electrophysiology quote. The earlier GtACR2 price ladder describes possible later scientific validation; it is not the current development roadmap. Do not treat neuron-level validation as the entry requirement for this POC.

## The claim to earn

“Our computational design process produced sequence changes that reproducibly improve a specified functional phenotype of a biologically relevant membrane protein in a small, practical experiment.”

This requires verified sequence changes, a functional endpoint, appropriate controls, independent biological replication and an explicit comparison with the reference. It does not require determining single-channel conductance, resolving every mechanism or demonstrating better neurons. If the endpoint is a validated functional proxy, state that scope accurately.

Expression alone supports an expression-engineering claim. Spectral change supports a photochemical-property claim. Neither should be presented as improved ion transport. Expression or trafficking can be meaningful engineering objectives when explicitly chosen, but they answer a different question from channel-function engineering.

## Division of work

- We supply target/construct definitions, evidence-backed readout, predictions and baselines, a bounded panel, controls, analysis specification, data format and a repeat/stop decision.
- The partner executes existing routine culture, handling, measurement and exports data. We do not rely on them to invent the assay, develop specialist expertise or operate a new platform.
- Each additional partner task must justify its contribution to the smallest defensible functional claim.

## Development sequence

1. **Assay fit first:** inventory the partner's actual routine measurement capabilities. Choose a target/readout pair that fits them. No hypothetical apparatus is assumed.
2. **Reproduce a functional distinction:** WT, an established altered-function control and no-protein/background control. Determine whether the readout provides a reproducible ranking before adding predicted variants.
3. **Run a small prospective panel:** roughly four to eight new variants, with predictions and literature-derived baseline frozen before measurements. Retain references in the same batch.
4. **Repeat the strongest result:** fresh culture/expression preparations; report effect size, uncertainty and relevant abundance/growth confounds. One successful variant can support a scaffold-specific pilot; it cannot establish general predictive superiority.
5. **Package the evidence:** verified sequences, source-grounded biological relevance, raw data, reproducible analysis, time/cost account, supported claim and limits. Specialist validation belongs to a later milestone if useful.

Novelty has two distinct roles: a previously unreported functional variant can provide a new biological result; prospective performance beyond a simple engineering heuristic provides evidence for the development system. An agent workflow alone establishes neither.

## GtACR2 under this scope

See [the readout-options review](gtacr2_readout_options.md) for published precedents and catalog products. Multiple non-patch assay transfers deserve evaluation before deferring GtACR2: extracellular fluorescent pH, endpoint iodide measurement and red membrane-potential fluorescence, selected against actual instrument capabilities.

GtACR2 remains biologically relevant, and a controlled bacterial transport-associated phenotype can be a legitimate first engineering result without neuronal experiments. However, the published extracellular-pH assay is not automatically a routine fluorescent plate assay. Its compatibility with the partner is still unresolved. See the sourced [GtACR2 assessment](gtacr2_decision_and_budget.md).

The current gate is whether we can supply a low-effort, reproducible functional readout using the partner's existing capabilities. If yes, target abundance-aware light-dependent transport performance in bacteria; do not claim faster neuronal gating from that assay. If not, defer GtACR2 as the first experimental scaffold and select a biologically relevant membrane protein whose functional assay fits the development system. This is target/readout selection, not a demand for more expensive validation.

No fixed dollar or calendar ceiling has been supplied for the revised scope. Earlier fully paid CRO-like budget ranges should not be represented as the cost of this collaboration. Re-estimate marginal cash, partner hands-on operations, our commissioning work and elapsed time only after assay fit is established.

## Funding-facing wording

“We are demonstrating a repeatable computational-to-experimental loop for functional membrane-protein engineering. Our first milestone is a prospectively designed variant with a reproducible functional improvement in a simple assay that our lab partner can execute. Neuronal validation and specialist electrophysiology are later milestones, not dependencies of this demonstration.”


---

## Source file: notes/sprint/external_review.md

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


---

## Source file: notes/sprint/decision_report.md

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


---

## Source file: notes/sprint/quantitative_results.md

# Quantitative appendix — fixed comparisons

Generated by `report_tables.py` from local prediction/metric files. P20 means tie-aware precision among the top20 (or all available candidates when fewer); it is not correlation. Different datasets/constraints have different benefit definitions. Seeds overlap and are not independent biological replications. No best-test model selection is used to populate these tables.


## BK: exact released features, fixed published RF

445numeric source records; five outerfolds/protocol. WTgeometry/evolution already contains WTstructural/MDinformation. The comparison tests incremental mutation energies. Direction-1 is a leftward>=50mV objective, not a therapeutic benefit.

| protocol | features | direction | pearson | rmse | P20 | prevalence |
| --- | --- | --- | --- | --- | --- | --- |
| publication_component | WT_geometry_evolution | -1 | 0.338 | 51.978 | 0.210 | 0.144 |
| publication_component | WT_geometry_evolution | 1 | 0.338 | 51.978 | 0.190 | 0.111 |
| publication_component | energy_only | -1 | 0.171 | 53.946 | 0.180 | 0.144 |
| publication_component | energy_only | 1 | 0.171 | 53.946 | 0.150 | 0.111 |
| publication_component | geometry_evolution_energy | -1 | 0.237 | 53.189 | 0.190 | 0.144 |
| publication_component | geometry_evolution_energy | 1 | 0.237 | 53.189 | 0.170 | 0.111 |
| publication_component | published_full_secondary | -1 | 0.316 | 52.305 | 0.220 | 0.144 |
| publication_component | published_full_secondary | 1 | 0.316 | 52.305 | 0.230 | 0.111 |
| site | WT_geometry_evolution | -1 | 0.227 | 48.711 | 0.210 | 0.094 |
| site | WT_geometry_evolution | 1 | 0.227 | 48.711 | 0.110 | 0.103 |
| site | energy_only | -1 | 0.105 | 49.612 | 0.130 | 0.094 |
| site | energy_only | 1 | 0.105 | 49.612 | 0.160 | 0.103 |
| site | geometry_evolution_energy | -1 | 0.194 | 48.786 | 0.170 | 0.094 |
| site | geometry_evolution_energy | 1 | 0.194 | 48.786 | 0.100 | 0.103 |
| site | published_full_secondary | -1 | 0.222 | 48.581 | 0.180 | 0.094 |
| site | published_full_secondary | 1 | 0.222 | 48.581 | 0.120 | 0.103 |


## BK: chemical-contact dynamics and finite-range energy

Same259numeric transmembrane variants for every method, fivefolds. Numerically stabilized train-only variance filter; original unstable diagnostics retained separately. Entropy/work are not calibrated gating free energies.

| protocol | features | learner | direction | pearson | rmse | P20 | prevalence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| publication_component | chemistry | ridge | -1 | 0.007 | 84.801 | 0.330 | 0.329 |
| publication_component | chemistry_WTgeometry | ridge | -1 | 0.039 | 85.982 | 0.320 | 0.329 |
| publication_component | geometry_ENCoM | ridge | -1 | 0.031 | 88.152 | 0.330 | 0.329 |
| publication_component | geometry_ENCoM_shuffled_within_site | ridge | -1 | 0.019 | 84.376 | 0.320 | 0.329 |
| publication_component | geometry_EvoEF2 | ridge | -1 | -0.086 | 88.497 | 0.310 | 0.329 |
| publication_component | geometry_EvoEF2_ENCoM | ridge | -1 | -0.083 | 91.269 | 0.270 | 0.329 |
| publication_component | sequence_geometry | ridge | -1 | 0.056 | 87.304 | 0.340 | 0.329 |
| publication_component | sequence_geometry_ENCoM | ridge | -1 | 0.095 | 86.569 | 0.330 | 0.329 |
| site | chemistry | ridge | -1 | 0.017 | 59.167 | 0.160 | 0.118 |
| site | chemistry_WTgeometry | ridge | -1 | 0.035 | 59.773 | 0.140 | 0.118 |
| site | geometry_ENCoM | ridge | -1 | -0.032 | 61.085 | 0.120 | 0.118 |
| site | geometry_ENCoM_shuffled_within_site | ridge | -1 | 0.047 | 59.788 | 0.140 | 0.118 |
| site | geometry_EvoEF2 | ridge | -1 | -0.031 | 60.666 | 0.120 | 0.118 |
| site | geometry_EvoEF2_ENCoM | ridge | -1 | -0.067 | 62.050 | 0.120 | 0.118 |
| site | sequence_geometry | ridge | -1 | -0.058 | 69.554 | 0.130 | 0.118 |
| site | sequence_geometry_ENCoM | ridge | -1 | -0.068 | 69.840 | 0.130 | 0.118 |


## Independent2024 BK publication

Ten novel0Ca genotypes. Four strong leftgains all inheritknownL312A. Increment error measures added substitutions against matchedL312A, where no-change MAE28.25mV is the relevant control.

| family | MAE_mV | left_gain_P3 | left_gain_slope_retained_P3 | increment_over_L312A_MAE_mV |
| --- | --- | --- | --- | --- |
| WT_null | 52.000 | 0.400 | 0.300 | 28.250 |
| known_parent_only | 16.000 | 1.000 | 0.750 | 28.250 |
| chemical_delta | 47.113 | 1.000 | 0.667 | 33.872 |
| chemical_published_energy | 46.480 | 1.000 | 0.667 | 33.245 |
| sequence_delta | 34.621 | 1.000 | 1.000 | 48.348 |
| sequence_published_energy | 34.422 | 1.000 | 1.000 | 48.785 |
| chemical_EvoEF2_joint | 38.156 | 1.000 | 1.000 | 32.731 |
| chemical_EvoEF2_matched_additive | 38.148 | 1.000 | 1.000 | 32.769 |
| sequence_EvoEF2_joint | 35.432 | 1.000 | 1.000 | 52.056 |
| sequence_EvoEF2_matched_additive | 35.332 | 1.000 | 1.000 | 52.074 |


## Physical source pretraining: matched adaptation controls

GFP96labels=64training+32validation; GB11256=1000+256. GFP randomcontrol is architecture-matched, GB1STANDARD is itself physically pretrained without binding-specific targets. Five seeds/protocol when complete; actual fitcount shown.

| dataset | protocol | checkpoint | development_labels_total | pearson | P20 | prevalence | fits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| avgfp | mutation | gfp | 96 | 0.527 | 0.040 | 0.036 | 5 |
| avgfp | mutation | random_gfp | 96 | -0.015 | 0.070 | 0.036 | 5 |
| avgfp | site | gfp | 96 | 0.545 | 0.080 | 0.040 | 5 |
| avgfp | site | random_gfp | 96 | -0.008 | 0.050 | 0.040 | 5 |
| gb1 | mutation | binding | 1256 | 0.885 | 0.830 | 0.143 | 5 |
| gb1 | mutation | binding_control | 1256 | 0.874 | 0.800 | 0.143 | 5 |
| gb1 | site | binding | 1256 | 0.625 | 0.250 | 0.136 | 5 |
| gb1 | site | binding_control | 1256 | 0.471 | 0.130 | 0.136 | 5 |


## GFP: ESM35 frozen/LoRA plus physics

Same96-label budget, fixed five seeds, site/substitution partitions. Bulk fluorescence correlation can improve without a brighter-than-WT selection advantage.

| protocol | mode | physical | pearson | P20 | prevalence | fits |
| --- | --- | --- | --- | --- | --- | --- |
| mutation | frozen | evoef_matched | 0.465 | 0.090 | 0.036 | 5 |
| mutation | frozen | none | 0.070 | 0.030 | 0.036 | 5 |
| mutation | frozen | rosetta | 0.364 | 0.030 | 0.036 | 5 |
| mutation | lora | evoef_matched | 0.465 | 0.085 | 0.036 | 5 |
| mutation | lora | none | 0.093 | 0.040 | 0.036 | 5 |
| mutation | lora | rosetta | 0.339 | 0.025 | 0.036 | 5 |
| site | frozen | evoef_matched | 0.407 | 0.030 | 0.040 | 5 |
| site | frozen | none | 0.150 | 0.030 | 0.040 | 5 |
| site | frozen | rosetta | 0.103 | 0.030 | 0.040 | 5 |
| site | lora | evoef_matched | 0.425 | 0.040 | 0.040 | 5 |
| site | lora | none | 0.162 | 0.020 | 0.040 | 5 |
| site | lora | rosetta | 0.147 | 0.040 | 0.040 | 5 |


## Independent GB1: all four sites withheld

147193measured triples/quadruples, approximately2%WTgains.1256old training/validation labels never touch four tested sites. Empiricalsingles/pairs instead use existing labels at those sites, explicitly a different information regime. No Wu labels fit a model.

| features | n | pearson | P20 | readcount_supported_gain_P20 | predicted_gain_precision |
| --- | --- | --- | --- | --- | --- |
| WT_null | 147193 | 0.000 | 0.020 | 0.018 | NA |
| chemical_summary_ridge | 147193 | 0.236 | 0.400 | 0.350 | 0.256 |
| chemical_summary_extra | 147193 | 0.185 | 0.000 | 0.000 | 0.036 |
| ESM35_actual_delta_ridge | 147193 | 0.161 | 0.000 | 0.000 | 0.033 |
| ESM35_actual_delta_extra | 147193 | 0.155 | 0.050 | 0.050 | 0.030 |
| gb1_binding_attributes_native_ridge | 147193 | 0.102 | 0.000 | 0.000 | 0.013 |
| gb1_binding_attributes_native_extra | 147193 | 0.372 | 0.050 | 0.000 | NA |
| ESM35_gb1_binding_attributes_ridge | 147193 | 0.042 | 0.000 | 0.000 | 0.028 |
| ESM35_gb1_binding_attributes_extra | 147193 | 0.303 | 0.200 | 0.200 | NA |
| gb1_binding_latent_native_ridge | 147193 | 0.113 | 0.050 | 0.000 | NA |
| gb1_binding_latent_native_extra | 147193 | 0.262 | 0.150 | 0.150 | NA |
| gb1_binding_control_attributes_native_ridge | 147193 | 0.064 | 0.250 | 0.250 | 0.083 |
| gb1_binding_control_attributes_native_extra | 147193 | 0.336 | 0.050 | 0.050 | NA |
| ESM35_gb1_binding_control_attributes_ridge | 147193 | 0.073 | 0.000 | 0.000 | 0.056 |
| ESM35_gb1_binding_control_attributes_extra | 147193 | 0.238 | 0.250 | 0.200 | 0.143 |
| gb1_binding_control_latent_native_ridge | 147193 | 0.301 | 0.200 | 0.200 | 0.083 |
| gb1_binding_control_latent_native_extra | 147193 | 0.271 | 0.050 | 0.050 | NA |
| empirical_all_singles | 147193 | 0.436 | 0.950 | 0.950 | 0.668 |
| empirical_all_pairs | 147193 | 0.347 | 0.500 | 0.500 | 0.115 |


## GB1: known component calibration, higher-order extrapolation

All2242existingOlsonsingle/doublelabels are developmentdata; no Wu targetlabels. Same147193measured higher-order test. Beyondparent refers to bestRAW Wu singleparent. Increment ranking uses76additionalpublished singlecontrols; rescue requires allcomponent singles<=WT. Many methods were explored, so individual high scores are leads, not confirmation.

| features | P20 | beyond_parent_P20 | beyond_parent_increment_P20 | rescue_P20 | pearson |
| --- | --- | --- | --- | --- | --- |
| site_additive_ridge | 0.850 | 0.050 | 0.100 | 0.100 | 0.498 |
| site_additive_extra | 0.650 | 0.250 | 0.100 | 0.100 | 0.536 |
| site_pairwise_ridge | 0.750 | 0.700 | 0.600 | 0.450 | 0.548 |
| ESM35_ridge | 0.750 | 0.650 | 0.800 | 0.050 | 0.545 |
| ESM35_extra | 0.900 | 0.200 | 0.100 | 0.000 | 0.423 |
| gb1_binding_attributes_ridge | 0.900 | 0.150 | 0.050 | 0.000 | 0.505 |
| gb1_binding_attributes_extra | 1.000 | 0.000 | 0.100 | 0.100 | 0.517 |
| ESM35_gb1_binding_ridge | 0.800 | 0.050 | 0.050 | 0.100 | 0.564 |
| gb1_binding_latent_ridge | 0.900 | 0.050 | 0.200 | 0.100 | 0.593 |
| gb1_binding_latent_extra | 1.000 | 0.050 | 0.100 | 0.050 | 0.560 |
| gb1_binding_control_attributes_ridge | 0.850 | 0.150 | 0.200 | 0.000 | 0.467 |
| gb1_binding_control_attributes_extra | 1.000 | 0.000 | 0.000 | 0.000 | 0.521 |
| ESM35_gb1_binding_control_ridge | 0.900 | 0.850 | 0.900 | 0.000 | 0.563 |
| gb1_binding_control_latent_ridge | 0.800 | 0.050 | 0.050 | 0.100 | 0.592 |
| gb1_binding_control_latent_extra | 1.000 | 0.050 | 0.100 | 0.100 | 0.556 |
| Hamming_kernel_ridge | 0.850 | 0.500 | 0.500 | 0.500 | 0.601 |


## GB1: what old validation can actually select

Only6of433old validationdoubles exceed their bestsingleparent by20%. Both MSE and conditionalgainAP rules are reported, not a bestWu outcome. This is an exploratory audit of selection rules after inspecting the test.

| family | ranking | selected_by | features | validation_beyond_parent_AP | test_WT_gain_P20 | test_beyond_parent_P20 |
| --- | --- | --- | --- | --- | --- | --- |
| nonphysical | predicted_function | validation_MSE | Hamming_kernel_ridge | 0.095 | 0.850 | 0.500 |
| nonphysical | predicted_function | validation_beyond_parent_AP | site_pairwise_ridge | 0.219 | 0.750 | 0.700 |
| nonphysical | predicted_increment_using76controls | validation_MSE | Hamming_kernel_ridge | 0.127 | 0.850 | 0.500 |
| nonphysical | predicted_increment_using76controls | validation_beyond_parent_AP | site_pairwise_ridge | 0.279 | 0.750 | 0.600 |
| physical | predicted_function | validation_MSE | gb1_binding_latent_ridge | 0.075 | 0.900 | 0.050 |
| physical | predicted_function | validation_beyond_parent_AP | gb1_binding_control_latent_extra | 0.142 | 1.000 | 0.050 |
| physical | predicted_increment_using76controls | validation_MSE | gb1_binding_latent_ridge | 0.079 | 0.900 | 0.200 |
| physical | predicted_increment_using76controls | validation_beyond_parent_AP | ESM35_gb1_binding_control_ridge | 0.081 | 0.900 | 0.900 |


## GB1: exceed measured doubleparents

137321constructs with allproperparent measurements;562(0.409%) exceed the bestWT/single/doubleparent by20%. Parent-aware scoring explicitly uses measured parentcontrols; plainpredicted_function does not.

| features | ranking | n | positive_n | P20 | P100 | AP |
| --- | --- | --- | --- | --- | --- | --- |
| components/ESM35_gb1_binding_control_ridge | predicted_function | 137321 | 562 | 0.550 | 0.520 | 0.206 |
| components/ESM35_gb1_binding_control_ridge | predicted_increment_using_measured_pairs | 137321 | 562 | 0.650 | 0.540 | 0.195 |
| components/ESM35_ridge | predicted_function | 137321 | 562 | 0.300 | 0.320 | 0.141 |
| components/ESM35_ridge | predicted_increment_using_measured_pairs | 137321 | 562 | 0.200 | 0.330 | 0.124 |
| components/Hamming_kernel_ridge | predicted_function | 137321 | 562 | 0.300 | 0.240 | 0.181 |
| components/Hamming_kernel_ridge | predicted_increment_using_measured_pairs | 137321 | 562 | 0.250 | 0.370 | 0.169 |
| components/gb1_binding_latent_ridge | predicted_function | 137321 | 562 | 0.000 | 0.130 | 0.076 |
| components/gb1_binding_latent_ridge | predicted_increment_using_measured_pairs | 137321 | 562 | 0.000 | 0.080 | 0.065 |
| components/site_pairwise_ridge | predicted_function | 137321 | 562 | 0.550 | 0.370 | 0.217 |
| components/site_pairwise_ridge | predicted_increment_using_measured_pairs | 137321 | 562 | 0.500 | 0.340 | 0.210 |
| empirical_all_pairs | predicted_function | 137321 | 562 | 0.350 | 0.310 | 0.106 |
| empirical_all_pairs | predicted_increment_using_measured_pairs | 137321 | 562 | 0.400 | 0.280 | 0.093 |
| empirical_all_singles | predicted_function | 137321 | 562 | 0.000 | 0.000 | 0.024 |
| empirical_all_singles | predicted_increment_using_measured_pairs | 137321 | 562 | 0.000 | 0.000 | 0.021 |


## Kir2.1: Joint regression

Same1494held-out native-site pairedfunction/trafficking constructs;287pointjoint gains and47SE-supported jointgains. Budgetfull=3881training+1414validation;1256=1000+256. Labels are HEK voltage-dye/surface proxies, not conductance or neuronal efficacy.3BWTcontext and650actualmutant representations differ; not a pure model-size experiment.

| budget | features | P20 | supported_P20 | prevalence | supported_prevalence |
| --- | --- | --- | --- | --- | --- |
| full | WT_null | 0.192 | 0.031 | 0.192 | 0.031 |
| full | chemistry_conservation_ridge | 0.100 | 0.000 | 0.192 | 0.031 |
| full | chemistry_conservation_extra | 0.250 | 0.000 | 0.192 | 0.031 |
| full | WTgeometry_chemistry_ridge | 0.150 | 0.000 | 0.192 | 0.031 |
| full | WTgeometry_chemistry_extra | 0.100 | 0.000 | 0.192 | 0.031 |
| full | esm2_35m_ridge | 0.250 | 0.050 | 0.192 | 0.031 |
| full | esm1v_650m_ridge | 0.350 | 0.000 | 0.192 | 0.031 |
| full | global1d_attributes_ridge | 0.200 | 0.000 | 0.192 | 0.031 |
| full | global1d_attributes_extra | 0.150 | 0.000 | 0.192 | 0.031 |
| full | global1d_latent_ridge | 0.250 | 0.050 | 0.192 | 0.031 |
| full | global3d_attributes_ridge | 0.500 | 0.100 | 0.192 | 0.031 |
| full | global3d_attributes_extra | 0.250 | 0.050 | 0.192 | 0.031 |
| full | global3d_latent_ridge | 0.400 | 0.000 | 0.192 | 0.031 |
| full | global3d_attributes_shuffled_within_site_ridge | 0.250 | 0.100 | 0.192 | 0.031 |
| full | global3d_attributes_shuffled_within_site_extra | 0.050 | 0.000 | 0.192 | 0.031 |
| full | esm650_global3d_attributes_ridge | 0.250 | 0.000 | 0.192 | 0.031 |
| 1256 | WT_null | 0.192 | 0.031 | 0.192 | 0.031 |
| 1256 | chemistry_conservation_ridge | 0.150 | 0.000 | 0.192 | 0.031 |
| 1256 | chemistry_conservation_extra | 0.175 | 0.050 | 0.192 | 0.031 |
| 1256 | WTgeometry_chemistry_ridge | 0.100 | 0.000 | 0.192 | 0.031 |
| 1256 | WTgeometry_chemistry_extra | 0.250 | 0.050 | 0.192 | 0.031 |
| 1256 | esm2_35m_ridge | 0.150 | 0.050 | 0.192 | 0.031 |
| 1256 | esm1v_650m_ridge | 0.300 | 0.050 | 0.192 | 0.031 |
| 1256 | global1d_attributes_ridge | 0.300 | 0.050 | 0.192 | 0.031 |
| 1256 | global1d_attributes_extra | 0.300 | 0.000 | 0.192 | 0.031 |
| 1256 | global1d_latent_ridge | 0.400 | 0.100 | 0.192 | 0.031 |
| 1256 | global3d_attributes_ridge | 0.150 | 0.000 | 0.192 | 0.031 |
| 1256 | global3d_attributes_extra | 0.200 | 0.050 | 0.192 | 0.031 |
| 1256 | global3d_latent_ridge | 0.300 | 0.050 | 0.192 | 0.031 |
| 1256 | global3d_attributes_shuffled_within_site_ridge | 0.300 | 0.100 | 0.192 | 0.031 |
| 1256 | global3d_attributes_shuffled_within_site_extra | 0.150 | 0.000 | 0.192 | 0.031 |
| 1256 | esm650_global3d_attributes_ridge | 0.200 | 0.050 | 0.192 | 0.031 |


## Kir2.1: Gain classification

Same1494held-out native-site pairedfunction/trafficking constructs;287pointjoint gains and47SE-supported jointgains. Budgetfull=3881training+1414validation;1256=1000+256. Labels are HEK voltage-dye/surface proxies, not conductance or neuronal efficacy.3BWTcontext and650actualmutant representations differ; not a pure model-size experiment.

| budget | features | P20 | supported_P20 | prevalence | supported_prevalence |
| --- | --- | --- | --- | --- | --- |
| full | training_prior | 0.192 | 0.031 | 0.192 | 0.031 |
| full | chemistry_conservation_logistic | 0.100 | 0.000 | 0.192 | 0.031 |
| full | chemistry_conservation_extra | 0.150 | 0.050 | 0.192 | 0.031 |
| full | WTgeometry_chemistry_logistic | 0.100 | 0.000 | 0.192 | 0.031 |
| full | WTgeometry_chemistry_extra | 0.200 | 0.050 | 0.192 | 0.031 |
| full | esm2_35m_logistic | 0.050 | 0.050 | 0.192 | 0.031 |
| full | esm1v_650m_logistic | 0.350 | 0.050 | 0.192 | 0.031 |
| full | global1d_attributes_logistic | 0.100 | 0.000 | 0.192 | 0.031 |
| full | global1d_attributes_extra | 0.150 | 0.000 | 0.192 | 0.031 |
| full | global1d_latent_logistic | 0.350 | 0.100 | 0.192 | 0.031 |
| full | global3d_attributes_logistic | 0.100 | 0.000 | 0.192 | 0.031 |
| full | global3d_attributes_extra | 0.150 | 0.000 | 0.192 | 0.031 |
| full | global3d_latent_logistic | 0.150 | 0.000 | 0.192 | 0.031 |
| full | global3d_attributes_shuffled_within_site_logistic | 0.150 | 0.000 | 0.192 | 0.031 |
| full | global3d_attributes_shuffled_within_site_extra | 0.300 | 0.150 | 0.192 | 0.031 |
| full | esm650_global3d_attributes_logistic | 0.400 | 0.050 | 0.192 | 0.031 |
| 1256 | training_prior | 0.192 | 0.031 | 0.192 | 0.031 |
| 1256 | chemistry_conservation_logistic | 0.150 | 0.050 | 0.192 | 0.031 |
| 1256 | chemistry_conservation_extra | 0.250 | 0.050 | 0.192 | 0.031 |
| 1256 | WTgeometry_chemistry_logistic | 0.050 | 0.000 | 0.192 | 0.031 |
| 1256 | WTgeometry_chemistry_extra | 0.400 | 0.050 | 0.192 | 0.031 |
| 1256 | esm2_35m_logistic | 0.000 | 0.000 | 0.192 | 0.031 |
| 1256 | esm1v_650m_logistic | 0.250 | 0.050 | 0.192 | 0.031 |
| 1256 | global1d_attributes_logistic | 0.300 | 0.100 | 0.192 | 0.031 |
| 1256 | global1d_attributes_extra | 0.250 | 0.050 | 0.192 | 0.031 |
| 1256 | global1d_latent_logistic | 0.450 | 0.250 | 0.192 | 0.031 |
| 1256 | global3d_attributes_logistic | 0.300 | 0.000 | 0.192 | 0.031 |
| 1256 | global3d_attributes_extra | 0.300 | 0.000 | 0.192 | 0.031 |
| 1256 | global3d_latent_logistic | 0.200 | 0.000 | 0.192 | 0.031 |
| 1256 | global3d_attributes_shuffled_within_site_logistic | 0.150 | 0.000 | 0.192 | 0.031 |
| 1256 | global3d_attributes_shuffled_within_site_extra | 0.250 | 0.150 | 0.192 | 0.031 |
| 1256 | esm650_global3d_attributes_logistic | 0.350 | 0.100 | 0.192 | 0.031 |


## Kir2.1: 3B joint regression

Same1494held-out native-site pairedfunction/trafficking constructs;287pointjoint gains and47SE-supported jointgains. Budgetfull=3881training+1414validation;1256=1000+256. Labels are HEK voltage-dye/surface proxies, not conductance or neuronal efficacy.3BWTcontext and650actualmutant representations differ; not a pure model-size experiment.

| budget | features | P20 | supported_P20 | prevalence | supported_prevalence |
| --- | --- | --- | --- | --- | --- |
| full | WT_null | 0.192 | 0.031 | 0.192 | 0.031 |
| full | ESM3B_LLR_ridge | 0.250 | 0.100 | 0.192 | 0.031 |
| full | ESM3B_LLR_extra | 0.200 | 0.000 | 0.192 | 0.031 |
| full | ESM3B_WTcontext_ridge | 0.450 | 0.000 | 0.192 | 0.031 |
| full | ESM3B_WTcontext_global3d_ridge | 0.350 | 0.000 | 0.192 | 0.031 |
| 1256 | WT_null | 0.192 | 0.031 | 0.192 | 0.031 |
| 1256 | ESM3B_LLR_ridge | 0.250 | 0.050 | 0.192 | 0.031 |
| 1256 | ESM3B_LLR_extra | 0.300 | 0.100 | 0.192 | 0.031 |
| 1256 | ESM3B_WTcontext_ridge | 0.300 | 0.050 | 0.192 | 0.031 |
| 1256 | ESM3B_WTcontext_global3d_ridge | 0.300 | 0.050 | 0.192 | 0.031 |


## Kir2.1: 3B gain classification

Same1494held-out native-site pairedfunction/trafficking constructs;287pointjoint gains and47SE-supported jointgains. Budgetfull=3881training+1414validation;1256=1000+256. Labels are HEK voltage-dye/surface proxies, not conductance or neuronal efficacy.3BWTcontext and650actualmutant representations differ; not a pure model-size experiment.

| budget | features | P20 | supported_P20 | prevalence | supported_prevalence |
| --- | --- | --- | --- | --- | --- |
| full | training_prior | 0.192 | 0.031 | 0.192 | 0.031 |
| full | ESM3B_LLR_logistic | 0.200 | 0.100 | 0.192 | 0.031 |
| full | ESM3B_LLR_extra | 0.250 | 0.100 | 0.192 | 0.031 |
| full | ESM3B_WTcontext_logistic | 0.400 | 0.050 | 0.192 | 0.031 |
| full | ESM3B_WTcontext_global3d_logistic | 0.250 | 0.000 | 0.192 | 0.031 |
| 1256 | training_prior | 0.192 | 0.031 | 0.192 | 0.031 |
| 1256 | ESM3B_LLR_logistic | 0.150 | 0.100 | 0.192 | 0.031 |
| 1256 | ESM3B_LLR_extra | 0.250 | 0.000 | 0.192 | 0.031 |
| 1256 | ESM3B_WTcontext_logistic | 0.250 | 0.150 | 0.192 | 0.031 |
| 1256 | ESM3B_WTcontext_global3d_logistic | 0.300 | 0.150 | 0.192 | 0.031 |


## ADRB2: independent membrane tradeoff

920fixed native-core testmutants, only5activitygains and1jointgain. Five training subsamples share this SINGLE testpartition. No modeljointgainP20improvement demonstrated; loweventcount limits interpretation.

| features | learner | objective | P20 | AP | prevalence |
| --- | --- | --- | --- | --- | --- |
| WT_null | NA | gain_under_constraints | 0.001 | 0.001 | 0.001 |
| WT_null | NA | response_gain | 0.005 | 0.005 | 0.005 |
| cheap | extra | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| cheap | extra | response_gain | 0.000 | 0.010 | 0.005 |
| cheap | ridge | gain_under_constraints | 0.000 | 0.006 | 0.001 |
| cheap | ridge | response_gain | 0.000 | 0.011 | 0.005 |
| esm1v_650m | ridge | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| esm1v_650m | ridge | response_gain | 0.010 | 0.018 | 0.005 |
| esm1v_650m_metl_global3d_two_state | ridge | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| esm1v_650m_metl_global3d_two_state | ridge | response_gain | 0.000 | 0.019 | 0.005 |
| esm2_3b | ridge | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| esm2_3b | ridge | response_gain | 0.010 | 0.014 | 0.005 |
| esm2_3b_metl_global3d_two_state | ridge | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| esm2_3b_metl_global3d_two_state | ridge | response_gain | 0.020 | 0.023 | 0.005 |
| metl_global3d_two_state | extra | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| metl_global3d_two_state | extra | response_gain | 0.000 | 0.009 | 0.005 |
| metl_global3d_two_state | ridge | gain_under_constraints | 0.000 | 0.002 | 0.001 |
| metl_global3d_two_state | ridge | response_gain | 0.010 | 0.016 | 0.005 |


## Actual local resources

Sharedload, not isolated hardware benchmarks. GPUallocator peaks are perprocess, not total boardusage. Setup inclusion differs by file and is explicit in sourceJSON; ENCoM reusesalreadygenerated sidechains.

| artifact | variants_or_sites | seconds | GPU_allocated_MiB | CPU_peak_child_MiB |
| --- | --- | --- | --- | --- |
| bk_esm2_3b_resources.json | 247 | 295.355 | 6066.372 | NA |
| kir_esm2_3b_resources.json | 428 | 63.958 | 5599.010 | NA |
| avgfp_metl_avgfp_local_resources.json | 13920 | 23.564 | 197.121 | NA |
| gb1_transfer_gb1_binding_resources.json | 149361 | 56.252 | 185.840 | NA |
| gb1_transfer_gb1_binding_control_resources.json | 149361 | 52.194 | 185.807 | NA |
| kir_transfer_global1d_resources.json | 6789 | 81.298 | 584.270 | NA |
| kir_transfer_global3d_resources.json | 6789 | 82.131 | 600.379 | NA |
| kir_transfer_esm1v_650m_resources.json | 6789 | 572.626 | 4161.813 | NA |
| bk_evoef_r20_resources.json | 473 | 1412.498 | NA | 298.777 |
| encom_resources.json | 274 | 1787.908 | NA | NA |


---

## Source file: notes/predictive/decision_report.md

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


---

## Source file: notes/c5r_next_phase_brief.md

# C5R: choose a control study before designing variants

Collaborator decision brief · 13 October 2026 · [Detailed paths and evidence](c5r_experimental_paths.md)

**Recommend: E. coli MscL → osmotic-shock protection → paired shock/mock CFU
survival. Conditional on existing stocks and routine plating. No option currently
passes both local assay readiness and predictive validity. All model-selected
new variants remain NO-GO.** OmpF conductance is frozen; no further tuning.

Rankings assume no target-specific assay already runs at C5R. An established
local workflow should take priority over rebuilding the nominally simpler one.

| Rank / exact phenotype–measurement | Workload and cost uncertainty | Predictor / neuronal relevance |
|---|---|---|
| **1 MscL:** protection across a defined osmotic-shock range; dilution-corrected **CFU(shock)/CFU(mock)** with a basal-fitness constraint | MJF455 ΔmscL ΔmscS; WT EcMscL and matched empty vector. Culture, timed dilution, plating/counting; no purification or special optics. Lowest consumable complexity; total cost unresolved if stocks/staff absent. | **NO-GO for designs.** Tension-gating physics is tractable; mutation-to-gating-to-survival prediction unvalidated. Mechanosensory/sonogenetic relevance is meaningful; bacterial survival does not predict neuronal efficacy. |
| **2 OmpF:** increased apparent **nitrocefin access**, measured by initial hydrolysis absorbance at matched density/porin/enzyme capacity | Porin-controlled K-12 host, periplasmic reporter, WT/vector; enzyme-capacity, supernatant leakage, viability and abundance controls. Medium setup/manual QC; host/reporter cost uncertainty substantial. | **NO-GO for designs.** Needs substrate-specific entry/efflux/reporter model and matched mutant data. Ion conductance is not this endpoint. Low direct neuronal relevance. |
| **3 GtACR2:** larger expression-normalized initial light-dependent **extracellular pH-rise slope** under fixed conditions | BL21(DE3), bacterial target/controls, retinal, washes, expression QC, calibrated blue light and fast pH logging. Highest setup/transfer uncertainty; published bacterial precedent exists. | **NO-GO for designs.** Photocycle/transport/host coupling unvalidated. Highest direct optogenetic relevance; pH is a transport proxy, not chloride conductance or neuronal inhibition. |

**Confirmed publicly:** CLARIOstar Plus, liquid handling and PCR/small-volume
incubation equipment. **Not confirmed:** target stocks, live-bacterial SOPs,
CFU capacity, expression QC, or calibrated light/pH apparatus. The reader does
not establish these workflows. No dollar estimate or purchase is proposed.

**Smallest pilot, only if materials/workflow already exist:** WT MscL rescue
and empty vector in the same deletion host; mock/intermediate/strong shock;
three independent cultures per construct on two assay days. Twelve cultures,
36 split-condition samples plus technical plating. Plan roughly 3–4 calendar
days including overnight steps; C5R must confirm labor and scheduling.

**Proposed assay gate:** ≥10× WT/vector survival under strong shock on each day;
countable CFUs with detection limits; viable mock controls without a consistent
WT penalty. At intermediate shock, WT survival 0.2–0.8 and biological SD ≤0.10
absolute provide headroom and repeatability. These are proposed thresholds,
not results or a power calculation. Passing permits an assay-feasibility GO;
**new designs still require a frozen predictor that beats simple baselines on
held-out known mutants, including useful gains and leakage penalties**.

**C5R response needed:** (1) Which matched strains/constructs and target SOPs
already exist? (2) Is timed shock/CFU work routine, and who handles manual steps?
(3) What expression QC and raw culture-level data can be returned? (4) Does an
existing OmpF or calibrated GtACR2 workflow change the ranking?

If materials are absent, first obtain the existing-stock/SOP/control-data
inventory; **do not order variants or start spending**. What remains unproven:
local execution, modest-gain sensitivity, mutant prediction and neuronal transfer.

Primary evidence: [MscL CFU methods/SI](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0137994),
[abundance/survival data](https://www.rpgroup.caltech.edu/mscl_survival/main.html),
[nitrocefin controls](https://cmdr.ubc.ca/bobh/method/nitrocefin-assay-on-whole-cells-for-outer-membrane-permeability-assessment/),
[GtACR2 bacterial assay](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/),
[C5R equipment](https://c5r.net/sciuniverse/suites/pcr-recovery/).


---

## Source file: notes/c5r_experimental_paths.md

# C5R experimental-path audit

Prepared 2026-10-13 (Pacific time). Purpose: choose an executable control study,
not launch a variant campaign. Recommendations and acceptance thresholds below
are planning judgments, not measured C5R performance or vendor quotations.
The [one-page brief](c5r_next_phase_brief.md) is the collaborator handoff.

**No combination currently passes both predictive modeling and local assay
feasibility.** Recommend **E. coli MscL → osmotic-shock protection → paired
shock/mock colony-forming-unit survival**, conditional on existing strain,
construct and culture/plating capability. This is a control-only assay gate.
Model-selected new variants remain NO-GO. No new simulator, mutant orders,
purchases, lab contacts or assay execution occurred in this phase.

The [OmpF freeze record](ompf_benchmark_freeze.md) preserves the conductance
benchmark. None of its code, physics, labels or results was refined here.
Solute permeability is a distinct proposed benchmark; conductance accuracy
would not validate it. Earlier GtACR2 readout/budget notes remain historical
explorations, not evidence that a plate assay or predictor has been validated.

## Existing workflow evidence and ranking assumptions

C5R publicly documents a CLARIOstar Plus, Hamilton STARlet and thermocycler in
its [physical PCR workflow](https://c5r.net/sciuniverse/suites/pcr-recovery/), and
small-volume incubation equipment in its
[cell-free sfGFP workflow](https://c5r.net/sciuniverse/suites/cfps-sfgfp/).
The [reader manufacturer](https://www.bmglabtech.com/en/clariostar-plus/)
specifies absorbance and fluorescence capability. Those are confirmed public
facts. They do not establish a live-bacterial workflow, incubator capacity,
sterile plating, membrane-expression QC, centrifuge access, stock strains,
light calibration or a logging pH probe. A heater-shaker module is not evidence
of an established shaking-flask bacterial culture workflow.

| Priority if starting from ordinary bacterial-lab capability | Setup dependencies | Routine manual workload | Cost uncertainty | Predictive status | Neuronal relevance |
|---|---|---|---|---|---|
| **1. MscL survival** | Specific deletion host + matched rescue/vector, culture/plating | Timed dilution, serial dilution, plating, colony counting | Lowest consumable complexity; medium/high total uncertainty if stocks/staff absent | NO-GO for useful mutant selection; tractable gating hypothesis, survival mapping unvalidated | Medium: mechanosensitive/sonogenetic connection; bacterial survival does not predict neuronal efficacy |
| **2. OmpF nitrocefin access** | Porin-controlled host, periplasmic reporter, enzyme/leakage/porin QC | Culture/washes, kinetic plate read, disruption and leakage controls | Medium/high: host/reporter setup and QC may dominate | NO-GO for substrate-matched selection; no transfer from ion model | Low: outer-membrane porin engineering develops methods rather than a neuronal actuator |
| **3. GtACR2 pH response** | Expression construct, retinal, low-temperature expression, calibrated light + fast pH recording | Culture/harvest/washes, dark stabilization, timed illumination, expression QC | High: optical setup, expression transfer and miniaturization | NO-GO for improved transport selection; no validated photocycle-to-bacterial-readout model | Highest: exact optogenetic target; bacterial pH proxy does not establish neuronal inhibition |

These are conditional workload rankings, not dollar estimates. An already
working C5R OmpF or GtACR2 assay can outrank a new MscL host. No current stock,
calendar commitment, staff-hour quote or dollar budget was obtained. Use an
existing SOP and controls first; acquire nothing on this document's assumptions.

## Path 1 — OmpF solute permeability

**Exact phenotype:** increased initial nitrocefin access in intact bacteria at
matched cell density, OmpF abundance and periplasmic enzyme capacity, without
increased leakage or loss of viability. Report an **apparent substrate-access
phenotype**, not ion conductance or an intrinsic permeability coefficient.

**Measurement:** kinetic nitrocefin hydrolysis absorbance, blank-corrected and
compared with disrupted-cell enzyme capacity and cell-free supernatant activity.
Use the early linear window, checking substrate/enzyme limitation and cell
scattering. A [primary 96-well study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4518837/)
establishes the bacterial optical readout and identifies efflux/destabilization
confounds. Its full text was archived and inspected in the prior phase; live
web retrieval currently returned a challenge page. The
[Hancock laboratory protocol](https://cmdr.ubc.ca/bobh/method/nitrocefin-assay-on-whole-cells-for-outer-membrane-permeability-assessment/)
provides intact/disrupted/supernatant controls. A plate adaptation and its
normalization still require validation at C5R.

**Host/constructs and controls:** proposed nonpathogenic K-12-derived
ΔompF ΔompC host with a fixed periplasmic beta-lactamase reporter; matched empty
porin vector versus full-length WT ompF retaining the native signal peptide.
Reporter choice, vector compatibility and a suitable available host are unresolved.
Hold efflux background fixed and document remaining permeability routes.
Include substrate/media blanks, enzyme-capacity control, supernatant leakage,
viability and outer-membrane OmpF abundance. A permeabilized-cell control tests
assay headroom, not better porin design. R132A is a literature solute-uptake
candidate, **not an established nitrocefin gain control**; do not import its
cefepime behavior into this assay. The original
[Bredin study](https://doi.org/10.1042/bj3630521) distinguishes the substrates
and measurements; its radioactive assay is not the proposed reader workflow.

**Wet-lab work:** sequence-verified existing stocks; culture/expression;
cell-density matching and washes; separate intact, disrupted and supernatant
samples; kinetic readout; QC. No purified protein or reconstitution is required
for this proposed path. Host/reporter construction, fractionation and enzyme
calibration are substantial one-time tasks if not already routine. Plate reads
can be automated; culture handling, disruption and QC should be treated as
manual until C5R confirms otherwise.

**Prediction strategy:** a new nitrocefin-specific free-energy/diffusion model,
including steric cross-section, solute orientation/charge and relevant loop
states. A reduced permeability hypothesis uses
`P ∝ [∫ exp(W(z)/kT)/D(z) dz]⁻¹`, with a consistently defined PMF including
confinement entropy. Couple entry flux to measured reporter kinetics and fixed
efflux; compare with steric/charge and WT-null baselines. Static pore size or
ligand docking alone does not validate a translocation barrier. Local models
are candidate calculations, not benchmarked predictions in this phase.

**Source data and validation gap:** frozen WT structures and sequence are
available; earlier mutation/solute studies contain mixed uptake, swelling and
susceptibility endpoints. No condition-matched nitrocefin mutant gain benchmark
has been established here. [PoreDesigner](https://pmc.ncbi.nlm.nih.gov/articles/PMC6131167/)
is an identified published solute-selectivity design precedent, but its complete
assay/SI transfer was not audited in this phase; it is not counted as validation
of this bacterial reporter phenotype. Conductance labels and antibiotic MICs
cannot substitute for matched entry-rate labels.

**Failure modes/status:** reporter saturation, extracellular enzyme, efflux,
compensatory porins, altered abundance, envelope stress and drug-specific
binding. **Assay: conditional feasibility; not locally demonstrated. Predictor:
NO-GO for new designs.**

## Path 2 — MscL osmotic-response function

**Exact phenotype:** greater survival over a specified rapid hypoosmotic-shock
range at matched expression, while preserving mock-shock viability. Lower
opening tension alone is not the desired phenotype: inappropriate leak can
reduce fitness. Primary endpoint is
`S = CFU_shock / CFU_mock`, correcting dilution and plated volume.

**Host/constructs and known controls:** E. coli **MJF455 (ΔmscL ΔmscS)**,
sequence-verified WT EcMscL in the published pB10b expression backbone and its
matched empty vector. This host is osmotically fragile; it is not a deletion
of every mechanosensitive channel. The complete
[2015 primary methods and SI](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0137994)
use paired high-osmolarity/mock versus water downshock and CFU counting, and
show that both increased and decreased channel sensitivity can impair viability.
Its 113 cysteine variants and chemical modifications are not 678 independent
sequence mutants. A later mechanism-disambiguation arm can use MJF367, which
retains MscS. That second host is not needed for the first WT/vector assay gate.

**Measurement and work:** start from the existing published-style CFU workflow,
not a new optical kit. Requires media/salt, compatible selection and induction
reagents, sterile water, pipettes/tubes, agar, culture/incubation and manual
colony counts. Grow, normalize density, impose matched timed shock/mock
conditions, dilute, plate and count after incubation. No retinal, purification,
light setup or electrophysiology is required for this endpoint. An OD recovery
curve measures lag/growth as well as survival and is not a replacement for CFU.
An [older fluorescence screen](https://pubmed.ncbi.nlm.nih.gov/11557017/)
provides adjacent throughput precedent, but was checked at abstract level here;
its full methods would need review before adoption. Live/dead dye entry can
also confound an assay of a large open pore.

**Prediction strategy:** a reduced tension-gating model with
`ΔG(γ) = ΔG₀ − γ ΔA` and
`P_open = 1 / [1 + exp(ΔG/kT)]`, extended only if evidence requires substates.
[Bilayer-elasticity theory](https://pmc.ncbi.nlm.nih.gov/articles/PMC384697/)
is locally tractable and explains membrane dependence, but does not supply
validated mutation-to-ΔG₀ values. A closed homolog structure is not a validated
open EcMscL ensemble. Survival also needs channel abundance, opening/closure
rates, shock delivery, osmolyte release and leak/lysis—not just P_open.
A channel can open earlier yet protect worse. No calculation was run here.

**Source data and gap:** the
[author's abundance–survival study](https://www.rpgroup.caltech.edu/mscl_survival/main.html)
links processed data/code at
[the research repository](https://github.com/rpgroup-pboc/mscl_survival) and
[Zenodo](https://doi.org/10.5281/zenodo.1252524).
It supports testing abundance/shock confounds, not learning mutant improvements
from WT alone. The
[2003 mutational-library paper](https://authors.library.caltech.edu/5943/)
and the 2015 SI are candidate phenotype sources; exact strain/construct,
expression and shock conventions must be harmonized before making a held-out
benchmark. The 2003 supplements were not audited here. Hold out mutation sites
and gain mechanisms, not repeated shock points from the same construct.
Compare a physical predictor with abundance-only, simple hydrophobicity/site
and WT-null baselines; retain a separate basal-fitness constraint.

**Neuronal relevance:** a
[primary neuronal study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5897719/)
provides mechanosensitization precedent. This gives a relevant membrane-actuator
connection, not a transfer guarantee from bacterial osmoprotection to neuronal
ultrasound response. Cell context, delivery and leak/toxicity need separate tests.

**Failure modes/status:** saturation at complete WT rescue; variable shock
speed; expression-dependent protection; both GOF leakage and LOF failure;
plating/recovery artifacts; membrane composition. **Assay: strongest established
simple workflow, conditional on C5R stocks/capability. Predictor: NO-GO for useful
mutant selection; a focused validation hypothesis is available.**

## Path 3 — GtACR2 bacterial light-gated transport

**Exact phenotype:** a larger channel/light-dependent initial extracellular
pH-rise slope under fixed illumination, ionic conditions and chromophore supply,
normalized for cell density and target abundance. This is a **transport-associated
pH proxy**; GtACR2 is a passive light-gated channel, not a demonstrated chloride
pump. A pH result alone does not quantify chloride flux, intrinsic conductance
or neuronal inhibition.

**Established experiment:** the
[2018 full primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/)
uses BL21(DE3), pET22b carrying GtACR2 residues 1–266 with a C-terminal His tag,
retinal-supported expression, washed suspensions and calibrated blue light.
It reads the first 10 seconds of pH rise with CCCP and normalizes to western-blot
abundance. E159Q/D230N are lower-response controls; E219Q is a reported gain.
The [2017 full paper](https://www.nature.com/articles/srep41879)
provides WT, empty vector and R84E higher-response precedent. It also identifies
unresolved retinal incorporation/spectral differences. The 2018 simulated
construct is longer than its experimental construct; do not silently mix them.

**Required components/work:** existing verified bacterial target/control
plasmids, BL21(DE3), compatible growth/induction supplies, all-trans retinal,
CCCP, cold-temperature expression, centrifugation/washes, cell-density readout,
fast logging pH probe, temperature control, blue illumination and an optical
power measurement; expression QC. Harvesting, repeated washes, dark baseline
stabilization and optical alignment are manual. Published expression is
large-volume; smaller culture/suspension scale is a transfer experiment, not a
proven low-effort protocol. None of the specialized setup is publicly confirmed
at C5R. No new construct purchase or platform is proposed before inventory review.

**Controls:** WT/vector light and dark; target without retinal; matrix/light
blank; CCCP dependence; membrane integrity/viability; comparable abundance;
known high/low controls only if already available. Use initial slopes rather
than a saturated endpoint. Keep chromophore occupancy and photon exposure
explicit; protein band intensity does not establish equal photoactive protein.

A fluorescent pH plate adaptation could use the documented reader, but dense
cells scatter light and reading illumination can activate the channel. That
adaptation adds a detector-transfer gate. It is not the first choice when an
existing electrode workflow is available, and no commercial dye makes it
validated automatically. An orthogonal anion-specific measurement is needed
before attributing an improved pH proxy to increased chloride transport.

**Prediction strategy/data:** a retinal/protonation-aware light-state occupancy
model coupled to open-state anion transport and bacterial electrochemical/pH
response. Static folding or protein-language-model scores omit photon-dependent
gating and host coupling. The two papers offer controls and small retrospective
mutant panels, not an independent broad useful-gain benchmark. No new dataset
extraction, photochemistry simulation or model tuning was performed; the
previous small diagnostic label table is not promoted to validation. Full
QM/MM or enhanced-sampling claims are outside this phase. **Assay: exact-target
literature precedent, C5R transfer unverified. Predictor: NO-GO for designs.**

## Recommended smallest control-only pilot and decision gates

**First evidence step:** ask C5R which strains, matched constructs and existing
SOPs actually exist. If MJF455/WT/empty-vector stocks or routine CFU capability
are absent, do not order them automatically. Prefer an already-running path;
otherwise the immediate task is obtaining an existing protocol/control dataset
and confirming access, not purchasing variants.

If the MscL controls are available, use **only WT rescue and matched empty
vector**, each with mock, intermediate and strong downshock. Fix the published
workflow's expression and shock timing; choose the intermediate condition to
leave headroom rather than maximize WT rescue. Use three independent cultures
per construct on each of two assay days, splitting each culture across the
three conditions: **12 cultures, 36 condition samples**, plus appropriate
technical plating replicates. Culture preparations are biological units;
dilution spots and shock points are not extra independent replicates. Existing
sequence/QC records and density/induction logs accompany raw CFU counts.

Planning estimate, **only with stocks and a routine workflow ready:** two assay
days plus overnight growth/counting, roughly three to four calendar days with
overlapping preparation. Colony counting and timing dominate manual work.
This is not a C5R labor commitment. No special detector consumable is required;
no dollar or staff-hour estimate is defensible before stock/SOP confirmation.

Proposed gates, to agree before execution (not published universal standards):

- Strong shock: WT/vector survival ratio at least **10× on each day**, with
countable CFUs and an explicit detection-limit treatment; never divide by an
unqualified zero. Mock-shock cultures must remain viable without a consistent
WT expression penalty.
- Intermediate shock: WT survival **0.2–0.8**, leaving improvement headroom;
within-condition biological survival SD **≤0.10 absolute**, with the WT/vector
ordering consistent across days. If the desired engineering gain is smaller
than the measured variability, this pilot has not established enough precision.
- Report all culture-level values, day effects, mock CFUs, dilutions and
counting limits. These six cultures per construct do not establish formal power
for subtle future gains. Add independent cultures based on the observed variance
before a smaller-effect claim.

For the strong-shock decision, compare the per-day means of culture-level
log10 survival: WT minus vector must be at least 1. If counts are below
detection, use explicit bounds and require the conservative bound to pass;
do not manufacture finite ratios with an undisclosed pseudocount.

Passing these criteria establishes a usable, repeatable **assay window**. It
does not establish sensitivity to every beneficial mutant, an intrinsic gating
threshold, or model validity. Before **model-selected new variants**, require a
separate frozen predictor to beat the simple baselines on held-out,
condition-matched known mutants, including useful protection improvements and
leakage penalties. WT-versus-null discrimination alone is insufficient. An
available established partial-function control is a useful next assay check,
but acquiring one is not part of this smallest pilot or authorization to spend.

**Computational decision:** GO for a bounded audit of existing MscL phenotype
data and assay/model alignment; NO-GO for using any of the three proposed
predictors to select new variants. No simulator implementation follows from
this document alone.

**Remaining unproven:** local material/workflow readiness; sensitivity to modest
useful gains; mutation-to-function prediction; and transfer to neuronal membrane
performance. Thus the immediate recommendation is a conditional MscL assay
pilot plus evidence audit, while all prospective model-guided design remains
NO-GO. A failing control window should trigger a project/workflow change rather
than another round of generic modeling infrastructure.

## Questions for C5R — send with the brief, not automatically

1. Which of these are already stocked with verified sequences: MJF455 plus WT
MscL/matched vector; a porin-controlled host plus periplasmic reporter; or
BL21(DE3) plus GtACR2/known control constructs? Existing SOP/control data can
change the ranking.
2. Is culture, timed osmotic dilution, sterile plating and CFU counting routine?
Who performs the manual steps, with what calendar availability and existing
consumables? No new equipment or purchase is presumed.
3. What membrane-expression/abundance QC is already workable, and can C5R return
raw culture-level counts/traces with induction, density, timing and day metadata?
4. If OmpF or GtACR2 already has a workflow, can its SOP and controls be shared?
For OmpF, include enzyme-capacity/leakage controls; for GtACR2, include calibrated
light/pH recording, retinal and expression controls. The reader identity is
already known; assay-specific capability is the outstanding issue.


---

## Source file: notes/c5r_gtacr2_pricing.md

# GtACR2 readouts priced against C5R's public capabilities

October 12, 2026. Public-source equipment audit and marginal-cash planning. No purchases, vendor messages or C5R messages were made. Public information is used directly; unanswered inventory questions are not a reason to pause this assessment.

## Recommendation

**Start with HPTS extracellular pH on C5R's documented CLARIOstar Plus. Add inexpensive red membrane-potential dye as a second detector if the first control assay works.** Keep iodide endpoint colorimetry as the next route if fluorescent pH is confounded. There is no reason to budget a new plate reader or ask whether they have one: their own physical-task equipment appendix identifies it.

A detector-only check can be under $200 in materials, using existing reader access. A control-only bacterial pilot is approximately **$725–1,675 for HPTS**, before staff time, tax/shipping and any new illumination. These are planning allowances, not experimentally established costs. If dedicated light/calibration equipment must be purchased, add roughly **$1,500–2,000 once**, shared by subsequent readouts. Obtaining reproducible functional expression remains a biological dependency, not a plate-reader purchase problem.

See the [one-page priced partner brief](../latex/render/c5r_gtacr2_pricing_brief.pdf), [editable option costs](../sources/c5r_gtacr2_prices.csv) and [public-capability register](../sources/c5r_public_capabilities.csv). This updates the earlier [readout comparison](gtacr2_readout_options.md); the older specialist/CRO budget is not the present milestone.

Build the brief from its [LaTeX source](../latex/c5r_gtacr2_pricing_brief.tex) using `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=latex/render latex/c5r_gtacr2_pricing_brief.tex` from the repository root. Rendered artifacts are ignored; source is retained. In the CSV, a zero price accompanied by a quote-only/unknown term is a calculation placeholder for a known subtotal, not a free product.

## What the internet establishes about C5R

The intended company is **C5R at c5r.net**, with Facility-0 and SciUniverse; unrelated clinical-research organizations and similarly named products are excluded.

| Public evidence | Conclusion | Boundary |
|---|---|---|
| Physical PCR-recovery equipment appendix names CLARIOstar Plus, Hamilton STARlet and INHECO ODTC [C1] | Reader, automated liquid handling and thermocycling are documented in physical runs | Successful calibrated assay execution is a separate question |
| Physical sfGFP cell-free task lists heater-shaker, temperature-control modules and electronic pipettes [C2] | Small-volume preparation/incubation work has documented infrastructure | Cell-free GFP is not proof of functional membrane-protein expression |
| C5R describes a harness combining equipment control with human instructions [C3] | A supplied workflow with some manual operations fits the stated operating model | Do not assume every operation is automated |

The manufacturer describes CLARIOstar Plus configurations with fluorescence, kinetic/ratiometric measurements, bottom reading and UV/visible absorbance. The documented model can cover HPTS, MQAE and red dyes; exact installed optical selections/modules are not exposed in C5R's appendix [C4]. We therefore price **existing reader access at $0 capital**, with configurations listed as bounded technical conditions, not ask the user to repeat an equipment inventory.

C5R's record proves a physical fluorescence readout; it does not individually prove its installed absorbance module, full tunable optics, bottom-read access, injectors or an optogenetic illuminator. I found no verified public evidence of a suitable flow cytometer, neuron-imaging system, patch rig, pH logger, bacterial culture/centrifugation workflow or current specialist capacity in the inspected sources. Absence from these pages does not imply absence from the facility. Small bacterial/mammalian labs mentioned in the handoff remain private-context claims, not newly verified public facts.

The public Hamilton-only simulation tasks are not used as evidence of physical equipment ownership; the physical PCR appendix is. C5R's benchmark dollar columns explicitly cover model/API inference, not lab or labor prices. They are not experimental service quotes.

## Public purchase prices

These are complete-pack purchase prices, not prorated chemical consumption. US prices are used when found. A directory price is identified separately from a current supplier/storefront listing.

| Readout / component | Public price found | Source quality and implications |
|---|---:|---|
| **HPTS/pyranine** | **$25/100 mg; $50/500 mg; $75/1 g** | AbMole M55389 manufacturer listing [P1]; same reporter class as the earlier H348 option |
| **Carboxy-SNARF-1, free acid** | **$522/1 mg** | Fisher US C1270 listing [P2]; replaces the previous euro-only anchor; not the AM ester |
| **DiSC3(5)** | **$55/25 mg** | APExBIO A4672 supplier listing [P3]; a cheaper source than the previously listed AAT product |
| **MQAE** | **$206/50 mg** | Dojindo M024-10 direct US listing [P4] |
| **Screen Quest iodide kit** | **$846/10-plate pack** | Biocompare listing for AAT 36350 [P5]; current AAT page lists the pack but hides a numerical price [P6]. Indicative, not a confirmed checkout quote |
| **HydroPlate HP96U** | **Quote-only; no defensible public numerical price located** | PreSens direct listing [P7]. Retain an explicit unknown rather than invent a plate price |
| **Halide-sensitive YFP / ClopHensor** | **$94 per academic/nonprofit plasmid** | Addgene #25872 / #25938 [P8, P9]. Company access is not established; this is a reference price, not an eligible company purchase |
| **BacLight bacterial voltage kit** | **$378/kit** | Thermo US B34950 direct listing [P10]; replaces the previous euro anchor; flow-cytometry workflow |
| **FLIPR voltage reagent family** | **$804 displayed by US official store** | Multiple selectable SKUs share the listing [P11]. Exact association with the desired small Red kit is not exposed in the retrieved view; $804 is a family-price anchor, not a verified R6136 quote |
| **ORCHID labeling dye** | **JF608 supplier product is enquiry-only** | Promega lists an early-access JF608 kit [P12]; matching the published reagent/preparation needs care |
| **Liposome mini-extruder set** | **$1,355.66** | VWR current Avanti 610023 set listing [P13]. Old Avanti PDFs show much lower historical prices and are not used as current quotes |
| **pH meter price anchor** | **$419.99–544.99** | Hanna HI2620/HI2621 family [P14]; fast trace/probe suitability still needs validation |

Do not confuse detector availability with validated GtACR2 performance. No supplier listing above claims the complete proposed bacterial GtACR2 assay. Stock indications are page observations, not reserved stock. Tax, shipping, negotiated account prices and lead times are separate.

## Comparable control-pilot budgets for each option

Use one common biological panel: **WT + established higher/lower functional controls + empty vector**, independently prepared, before new designs. The published control ranking applies to its source assay; it is not guaranteed in iodide or voltage measurements.

Let **B = $700–1,550** for shared bacterial preparation and controls. Our planning decomposition is $300–700 for verified control constructs/source material, $150–350 for host/expression/chromophore/culture supplies, $150–300 for abundance/viability/calibration-control consumables, and $100–200 for routine labware/buffers. These are allowances, not vendor quotes. Reuse/donated stocks can lower cash; commissioning failures can raise it. Basic bacterial expression and cell collection must be available or supplied separately; no new incubator or centrifuge is included.

The table uses existing CLARIOstar access, in-kind staff, and **already available/borrowed compatible illumination**. New light hardware is added once afterward. Readout-specific extra supplies cover additional processing/calibration beyond B, with estimates deliberately distinguished from listed reagent prices.

| Option | Readout purchase / allowance | Extra supplies allowance | Comparable control-pilot cash, excluding new light | Our estimate of extra assay-development burden |
|---|---:|---:|---:|---|
| **HPTS fluorescent pH** | $25 | $0–100 | **$725–1,675** | Low/medium; approximately 2–6 extra hands-on hours for detector/optical checks |
| **SNARF fluorescent pH** | $522 | $50–150 | **$1,272–2,222** | Low/medium; approximately 2–6 h, different spectral tradeoff |
| **DiSC3(5) voltage** | $55 | $50–150 | **$805–1,755** | Medium; approximately 4–10 h for loading/background/viability checks |
| **MQAE chloride** | $206 | $50–150 | **$956–1,906** | Medium; approximately 6–12 h for dye-loading/retention/calibration |
| **Iodide endpoint kit** | $846 indicative | $100–250 | **$1,646–2,646** | Medium; approximately 4–12 h for loading/wash/retention/matrix transfer |
| **HydroPlate pH** | Unknown Q_H | $50–150 | **Q_H + $750–1,700** | Low/medium handling; signal resolution and response time are critical |
| **YFP reporter in bacterial host** | $150–400 construct/source allowance | $250–600 | **$1,100–2,550** | Medium/high; approximately 12–30 h beyond common preparation |
| **ClopHensor reporter in bacterial host** | $250–500 construct/source allowance | $300–800 | **$1,250–2,850** | High; approximately 16–40 h for coexpression and calibration |
| **BacLight kit** | $378 | $100–200 | **$1,178–2,128**, plus any flow-facility access | Poor current fit; kit's validated workflow is flow cytometry, not the documented reader |
| **FLIPR voltage chemistry adapted to bacteria** | $804 family-price allowance | $200–500 | **$1,704–2,854**, desired SKU price unresolved | Medium/high; bacterial transfer unverified. Existing mammalian assay would be a different budget |
| **ORCHID neuronal imaging** | JF608 and imaging access quote-only | $1,000–3,000 provisional constructs/culture/calibration supplies | **Not fully priceable: quotes + $1,000–3,000 supplies** | Outside the minimal scope; documented plate reader is not a neuronal voltage-imaging facility |
| **Purified protein/liposome fluorescence** | $1,355.66 extruder set | $800–2,000 reconstitution supplies + $1,500–4,000 expression/purification allowance | **$3,655.66–7,355.66**, before new light or missing purification equipment | High; functional GtACR2 purification/reconstitution is itself substantial development |
| **Electrode pH** | $600–1,200 complete measurement-setup allowance | $100–250 | **$1,400–3,000** | Low/medium if setup works; lower throughput; no suitable C5R logger publicly verified |

The hour allowances are engineering estimates, not measured work or C5R staffing quotes. They exclude ordinary culture/incubation waiting, common construct work and open-ended commissioning. Reporter allowances do not verify company access to published constructs; obtain legitimately accessible materials through the authorized sourcing path. Exact assay success and sample-size adequacy remain unknown.

For company reporter construction, the $94 academic price is deliberately **not** used as the complete budget. Extra host/vector work is priced. For ORCHID and liposomes, the bacterial B allowance is not applied: their preparation is different. It would be misleading to call the dye/extruder price the price of those assays.

## Shared light/calibration cost: one purchase, not one per assay

C5R's public pages do not establish a controlled blue actuation setup or optical power meter. Price that gap explicitly:

| Component | Public price or allowance |
|---|---:|
| Thorlabs M470L5 mounted blue LED | **$261.20** listing [L1] |
| Compatible current driver | **$300–500 estimate**; exact current product price unresolved |
| Driver power supply | **$30–50 estimate** |
| Thorlabs PM16-120 USB optical meter | **$743.59** distributor listing [L2] |
| Holder/geometry/attenuation/fixture supplies | **$100–200 estimate** |
| Subtotal | **$1,434.79–1,754.79**, before shipping/tax/integration |

Reserve **$1,500–2,000** as a rounded cash allowance for this research-grade bench setup. It is not a turnkey 96-well illuminator quote. Demonstrate uniformity/timing in the intended small sample layout and avoid buying or building a plate-wide optical robot for a four-control pilot. A calibrated borrowed fixture removes most of this cash; no such access is assumed.

A cheaper assembled LED fixture may work, but its delivered price and calibration are not verified here. Do not substitute an uncalibrated consumer blue lamp while claiming a measured light-dose improvement. CLARIOstar excitation can potentially serve as a defined stimulus in some assays, but that requires validation of dose/timing; instrument presence alone does not establish equivalence to the published continuous illumination.

Thus **HPTS + DiSC3(5) in one shared control batch** is approximately **$830–1,880** with existing light: B + $25 + $55 + $50–250 additional detector-specific supplies. With the shared new-light allowance it becomes roughly **$2,330–3,880**. This is much closer to the funding-stage scope than the previous specialist-validation ladder.

## Cheapest concrete next step, using known capability

Proceed with a supplied CLARIOstar detector-check specification, not an inventory follow-up. HPTS has a $25 small-pack anchor; adding the $55 voltage dye is only $80 in headline reagent purchases. A **$100–200 detector-only allowance** can cover small chemical standards/matrix checks and routine plate supplies, assuming basic stocks and reader access. It establishes measurement compatibility, not functional channel engineering.

After detector checks, the control-batch gate is light/channel-dependent signal with growth/abundance/membrane-integrity controls and independent preparations. Then a four-design prospective batch can add roughly **$700–1,500 in estimated DNA/repeat-culture consumables**, plus any new selected readout purchase. Do not count this as a guaranteed result or fixed turnkey turnaround.

The most important unresolved operational items are functional membrane expression, cell collection/washing, cooler expression conditions where needed, and illumination. We can continue source/construct and analysis preparation without answers. If live facility configuration is made available later, inspect it directly rather than asking the user to identify already documented hardware.

## Source register

- **C1:** [C5R physical PCR-recovery task, equipment appendix](https://c5r.net/sciuniverse/suites/pcr-recovery/).
- **C2:** [C5R physical cell-free sfGFP task, equipment appendix](https://c5r.net/sciuniverse/suites/cfps-sfgfp/).
- **C3:** [C5R operating model](https://c5r.net/); [benchmark scope/cost definitions](https://c5r.net/sciuniverse/).
- **C4:** [CLARIOstar Plus manufacturer specifications](https://www.bmglabtech.com/en/clariostar-plus/).
- **P1:** [AbMole HPTS M55389](https://www.abmole.com/products/8-hydroxypyrene-1-3-6-trisulfonic-acid.html).
- **P2:** [Fisher C1270 free-acid SNARF](https://www.fishersci.com/shop/products/molecular-probes-snarf-5-and-6-carboxy-snarf-1/C1270).
- **P3:** [APExBIO A4672 DiSC3(5)](https://www.apexbt.com/disc3-5.html).
- **P4:** [Dojindo MQAE](https://www.dojindo.com/products/M024/).
- **P5:** [Biocompare AAT 36350 directory price](https://www.biocompare.com/25138-Assay-Kit/18002095-Screen-Quest-Colorimetric-Chloride-Channel-Assay-Kit/). Search-indexed listing checked; direct page encountered an access error.
- **P6:** [AAT direct iodide-kit listing](https://www.aatbio.com/products/screen-quest-colorimetric-chloride-channel-assay-kit).
- **P7:** [PreSens HydroPlate](https://www.presens.de/products/detail/hydroplate-hp96u).
- **P8/P9:** [YFP #25872](https://www.addgene.org/25872/); [ClopHensor #25938](https://www.addgene.org/25938/).
- **P10:** [Thermo US BacLight B34950](https://www.thermofisher.com/order/catalog/product/B34950).
- **P11:** [Official FLIPR reagent storefront](https://shop.moleculardevices.com/collections/assay-kits/products/flipr-membrane-potential-assay-kit).
- **P12:** [Promega Janelia HaloTag ligands/JF608](https://www.promega.com/products/protein-detection/protein-labeling/janelia-fluor-halotag-ligands/).
- **P13:** [VWR Avanti extruder set](https://www.vwr.com/us/en/product/NA1741992/mini-extruder-kits-avanti-polar-lipids).
- **P14:** [Hanna pH meter family](https://hannainst.com/ph-orp-simple-benchtop-meter/).
- **L1:** [Thorlabs mounted LEDs, M470L5 listing](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=2692&partnumber=MWWHLP2).
- **L2:** [Volition Thorlabs PM16-120 listing](https://www.govolition.com/product/V40-PM16-120).

Prices/configurations can change. Public inventories describe recorded work, not guaranteed present-day availability. Scientific assay precedents and transfer limitations are in the linked readout review. Unknown public prices are retained explicitly, so this report does not imply every option has a complete supplier quote. No specialist milestone is imposed on the current POC.


---

## Source file: sources/c5r_public_capabilities.csv

capability,item,evidence_class,source_url,observed_scope,planning_use,unverified_boundary,checked_date
Fluorescence plate reader,BMG CLARIOstar Plus,Physical task equipment appendix,https://c5r.net/sciuniverse/suites/pcr-recovery/,Named in physical PCR cleanup and fluorescence quantification task,Zero new reader capital in compatible assays,Installed optional modules and present schedule not enumerated,2026-10-12
Liquid handling,Hamilton Microlab STARlet 173021,Physical task equipment appendix,https://c5r.net/sciuniverse/suites/pcr-recovery/,Named in physical task,Existing routine liquid handling infrastructure,Bacterial handling scripts and all movement integrations not verified,2026-10-12
Thermocycler,INHECO ODTC 96 Left 8100100,Physical task equipment appendix,https://c5r.net/sciuniverse/suites/pcr-recovery/,On deck PCR instrument listed,No new PCR machine capital,Not evidence of cloning or sequencing success,2026-10-12
Preparation incubation,Opentrons Heater-Shaker and INHECO CPAC,Physical task equipment appendix,https://c5r.net/sciuniverse/suites/cfps-sfgfp/,Small volume cell-free reaction preparation,Existing preparation and incubation equipment,Not verified low temperature bacterial expression workflow,2026-10-12
Temperature control,Opentrons Temperature Module GEN2,Physical task equipment appendix,https://c5r.net/sciuniverse/suites/cfps-sfgfp/,Reagent cooling listed,Existing small volume stock handling,Not proof of a refrigerated shaking culture incubator,2026-10-12
Reader model features,Kinetic ratiometric fluorescence and optional configurations,Manufacturer specifications,https://www.bmglabtech.com/en/clariostar-plus/,Model supports broad wavelengths and bottom reading with configuration choices,Assess HPTS MQAE and red dye fit without buying new reader,C5R installed configuration not fully identified,2026-10-12
Operating model,Equipment control plus human instructions,Company primary page,https://c5r.net/,Facility harness description,Supply bounded manual and machine workflow,Not a CRO staffing or price commitment,2026-10-12
Not publicly verified,Culture centrifugation actuation flow and neuronal imaging,Search limitation,https://c5r.net/sciuniverse/,Not established in inspected sources,Keep missing steps explicit without pausing for user questions,Absence of evidence is not evidence of absence,2026-10-12
