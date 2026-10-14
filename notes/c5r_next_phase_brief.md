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
