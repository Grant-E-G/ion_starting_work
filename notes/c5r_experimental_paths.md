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
