# C5R OmpF physics feasibility decision

**Decision: NO-GO for selecting new mutants for a C5R ion-conductance engineering
experiment with the present model. GO for local computational feasibility;
CONDITIONAL GO for a bounded validation study or an assay-aligned permeability
project.** The hardware is sufficient. The unresolved gates are predictive
transfer, independent evidence of useful mutant selection, and a practical
assay for the modeled observable.

This report records an autonomous session beginning 2026-10-13 18:16:50 UTC,
within a six-hour allowance. No purchases, collaborator contact or wet-lab work
occurred. Work used the local laptop, public literature and cached structures.
The external brief requested an easier, literature-rich scaffold before GtACR2.
OmpF was investigated first; no photochemistry, folding-model training, full
MD trajectory or differentiable design platform was attempted.

## What now exists

An executable WT-structure-derived model reconstructs the biological trimer,
repairs specified side-chain mutations, assigns atomic partial charges, solves
three-dimensional nonlinear electrostatics and computes reduced linear-response
ion transport. Geometry, charge and WT-null baselines accompany its predictions.
Numerical tests, mesh/parameter/preparation sensitivities, a separate dielectric
reaction-energy correction, actual CPU/GPU resource records and additional-site
challenge results are saved. The model generates conductance predictions rather
than just structural plausibility scores.

Start with the [reproduction instructions](../../code/experiments/ompf/README.md),
[measurement manifest](../../sources/ompf/measurement_manifest.json),
[measurement table](../../sources/ompf/measurements.csv),
[structure manifest](../../sources/ompf/structure_manifest.json),
[equations](../../math/ompf_physics_slice.md),
[literature audit](literature_audit.md) and
[assay assessment](assay_feasibility.md).
The [artifact manifest](artifact_manifest.json) identifies exact local files
and checksums. The [portable review bundle](review_bundle.tar.gz) includes code, prepared inputs,
image maps, principal analysis inputs and reports without most large field
arrays or raw publisher articles. Prepared coordinate/charge arrays are reproducibility fixtures:
regenerating hydrogen placement is not guaranteed bitwise identical.

## Evidence and benchmark boundaries

The archived table contains **72 observations**, not 72 independent proteins.
There are **25 eligible scalar observations: six WT references and 19 mutant
comparisons covering 14 distinct mutant constructs**. Another six measurements
capture multiple conductance populations for WT/D127N/D127K; these are a separate
state-resolved challenge. Three topology/disulfide cases have audited conditions
but are unsupported by this point-mutant implementation. Together these make
34 method-audited archived observations. The remaining 38 have incomplete
conditions or experimental uncertainty and are excluded from scalar scoring.

| Source | Archived rows | Use here | Important limitation |
|---|---:|---|---|
| Miedema 2004 | 12 | Four WT references, eight gain comparisons, three mutant constructs | Matched zero-voltage trimer slope; temperature/error-statistic definition absent |
| Phale 1997 | 11 | WT + seven point-mutant challenges; three excluded topology/redox cases | Finite-voltage channel events; 1 mM calcium not modeled |
| Bredin 2002 | 5 | WT + four additional scalar mutant challenges | Finite-voltage closure events; exact n/error-statistic definition absent |
| Phale 2001 SI | 35 | Archived only | Main-paper condition footnotes unavailable; many earlier data reused |
| Pezeshki 2009 | 3 | Archived only; NQRRR modeled diagnostically | Conductance pH/error not established; simulated results are not experimental labels |
| Miedema D127 2006 | 6 | Separate state-resolved challenge | Population means cannot be pooled without population weights |

The strongest observable match is [Miedema 2004 Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC1304784/):
zero-voltage slope over ±25 mV, symmetric 0.1/1 M NaCl or KCl, pH7.4,
20 mM HEPES/NMDG, PE:PC 8:2 bilayers. These are **trimer conductances**.
[Phale 1997](https://pmc.ncbi.nlm.nih.gov/articles/PMC21228/) and
[Bredin 2002](https://doi.org/10.1042/bj3630521) resolve individual-channel
closure steps under different conditions; they test approximate transfer, not
an identically conditioned target.

Primary-source checks caught consequential errors. Bredin's table assigns
880 pS to K16A and 800 pS to K16D; a later discussion misattributes the gain.
The [2009 paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2756365/) has empty
experimental conductance cells for several simulated mutants. Its factor 5.6
is a simulated current ratio, not an observed mutant gain. Its SI contains
simulated MD values. The simulations used 1 V, versus experimental comparisons
at 50 mV, with limited trajectory sampling. These entries were not turned into
independent benchmark measurements.

The [D127 primary study](https://doi.org/10.1007/s00249-006-0084-4) reports
multiple dominant conductance populations under otherwise useful zero-slope
conditions. Selecting the highest D127N population would manufacture a scalar
genotype gain. Counts from selected traces are not unbiased population weights.
We retain every state and compare scalar predictions to their reported range.

Full local archives are available for the main PMC sources and scanned Phale SI.
Bredin's complete PDF and the D127 PDF were read through the browser; local PDF
retrieval failed, so exact transcriptions/method audits are saved instead.
Phale 2001's accessible SI refers to unavailable main-paper conditions. A public
repository download returned an authorization barrier; it was not bypassed.
No abstract was treated as a complete benchmark. Source URLs, hashes, table
locations, gaps and exclusions are recorded individually.

All predictions begin with **WT 2OMF**; biological assembly MODEL records are
symmetry copies, not a conformational ensemble. The mature sequence is 340
residues; UniProt P02931 is a 362-residue precursor with a 22-residue signal
peptide. Every mutation is checked against the mature numbering. Experimental
mutant structures are manifested as reserved diagnostics, never inputs to
mutant prediction. A newer WT structure, 2ZFG, is reserved too and has a missing
residue. Several archived structures have different mutations than a casual
filename interpretation would suggest; 1HXX is Y106F, not WT.

## Model, calibration and status of validation

AMBER14/PDBFixer adds side chains and nominal-pH hydrogens. Restrained OpenMM
minimization repairs local geometry while strongly holding backbone/unchanged
heavy atoms. GBn2 is used for this repair only. It is neither a validated
folding predictor nor a membrane conformational ensemble.

Using an experimental WT scaffold isolates the function-model question from
folding-model quality. Sequence transformers provide sequence priors, while
AlphaFold-family predictors provide structural hypotheses; neither output alone
validates an ion-conductance objective. This session did not benchmark folding
accuracy. The restrained mutant repair also does not predict large backbone
rearrangements. Those limitations remain separate from the numerical field solve.

The principal continuum model uses protein/membrane/water dielectric constants
4/2/78.5, temperature 298.15 K, a 0.10 nm ion-access probe, a prescribed membrane
slab and apertures, charge-conserving atom deposition and harmonic dielectric
faces. A nonlinear PB solve gives equilibrium potential. Separate weighted
transport solves compute small-voltage conductance with reservoir boundaries
and lateral no-flux conditions. This is reduced equilibrium transport in a
frozen background, not a full dynamic self-consistent PNP/MD simulation.
The linearized PB alternative is diagnostic because aqueous potentials exceed
the weak-potential regime. No mutant-specific diffusion coefficient is fitted.

The geometry baseline uses the identical accessible mesh with zero potential.
Two fixed Donnan charge baselines differ by whether an entrance-charge convention
is included; neither is selected after seeing labels. The null predicts WT.
A 5% gain threshold is a descriptive point-estimate screen, not a confidence
claim or an experimentally justified universal cutoff.

One optional common mobility multiplier is fitted to WT 1 M KCl; other WT
conditions then test absolute transfer. The ratio tables instead normalize
mutants to WT within each study/condition. This cancels a reference scale and
must not be confused with successful prediction of absolute conductance.
A separately labeled two-WT diagnostic additionally fits an effective sodium
mobility; it is a calibrated phenomenological diagnostic, not a recovered
microscopic mechanism.

**Validation status:** the initial tables are retrospective. Mutant labels were
not optimized by a regression loss, but model development was informed by known
failures. The dielectric-image correction was investigated after ordinary PB
missed known gains. Consequently its improved results are architecture-informed
retrospective comparisons, not an untouched independent test. Bredin and D127
are additional-study challenges, not blinded prospective experiments. An explicit
model snapshot preceded extraction of the later state table, but this does not
make a targeted literature challenge preregistered. There are **zero genuinely
prospective mutant predictions validated experimentally**.

## Results: useful gains, ranking and transfer

Errors below are absolute errors in mutant/WT ratio. Repeated salts and
concentrations on the same construct are correlated; the eight matched gain
observations represent only three constructs. No p-value, confidence interval
or cross-validation claim is made.

| Matched gain cohort, full trimer | Ratio MAE | Ratio RMSE | Point gains detected (>5%) |
|---|---:|---:|---:|
| WT null | 0.3804 | 0.4683 | 0/8 |
| Local charge baseline | 0.3770 | 0.5072 | 4/8 |
| Geometry, 0.15 nm grid | 0.2664 | 0.3631 | 8/8 |
| Ordinary nonlinear PB, 0.15 nm | 0.1594 | 0.1908 | 4/8 |
| Ordinary nonlinear PB, 0.075 nm | 0.1871 | 0.2177 | 4/8 |
| PB + dielectric image, 0.15 nm | 0.1240 | 0.1494 | 8/8 |
| PB + dielectric image, 0.10 nm | 0.1139 | 0.1247 | 8/8 |
| Image + crowding, v=0.03 nm³, 0.15 nm | 0.1286 | 0.1551 | 8/8 |
| Image + crowding, v=0.10 nm³, 0.15 nm | 0.1510 | 0.1767 | 8/8 |

The original ordinary-PB result is materially inadequate: it predicts decreases
for EAE and LEAE in 1 M NaCl despite measured gains. Refining its grid does not
rescue that result. A dielectric reaction-energy penalty has a falsifiable
physical motivation: ions near low-dielectric protein/membrane interfaces pay
an insertion cost missing from ordinary PB. Its unscreened Green-function
approximation improves the known gain cohort without fitting mutant mobility.
The combined crowding sensitivity does not improve on image-only results.
It is retained as a negative diagnostic rather than selected as a new model.

![Corrected-model gain comparisons](figures/image_gain_predictions.png)

Across all 19 scalar mutant comparisons, full-trimer image MAE is **0.1165**,
versus geometry **0.1888** and null **0.2347**. However this aggregate mixes
observables and is not sufficient to establish design utility. On the four
Bredin challenges, image MAE **0.1126** is essentially null MAE **0.1128**,
and the reported K16A gain is not detected at the descriptive 5% threshold.
The seven Phale damage cases give image MAE **0.1100**, versus null **0.1378**;
damage detection alone does not meet the engineering objective.

Geometry already calls all eight matched known gains. To test the stronger
selection claim, [candidate-choice comparisons](ranking_choices.csv) record
which mutant each method would choose. At 0.1 M KCl, the reported means favor
AAA (1.32 nS) over EAE (1.23 nS), but the image model favors EAE; geometry favors
AAA. In NaCl, LEAE is the higher-mean choice and both methods choose it. At
1 M KCl the EAE/AAA experimental difference is only 0.03 nS, below the reported
dispersions, so exact mean-ranking agreement is weak evidence. Error-statistic
definitions are incomplete; these are descriptive comparisons. The quantitative
error improvement is encouraging, but it has not established better engineering
choices than geometry on an independent useful-gain family.

**Absolute calibration transfer fails.** After fitting only WT 1 M KCl to
4.20 nS, the coarse image model predicts WT 0.1 M KCl about 1.360 nS instead
of 0.820, WT 0.1 M NaCl about 0.931 instead of 0.500, and WT 1 M NaCl about
3.179 instead of 2.390. Fine-grid image results do not remove this mismatch.
Per-condition WT normalization conceals it if shown alone.

![Absolute WT transfer](figures/absolute_WT_transfer.png)

There is also an exact representation constraint. The current sodium and
potassium ions share the same equilibrium/transport field and differ only in
fixed bulk diffusion. For nonnegative cation/anion contributions,
**0.678571 ≤ G(NaCl)/G(KCl) ≤ 1**. The measured WT 1 M ratio is **0.569048**.
Even an informal upper ratio using the reported dispersions is about 0.608;
this is not a confidence interval, but it illustrates the scale of mismatch.
All present grid/image/crowding variants obey the same bound. Thus a larger
folding model or finer mesh cannot fix this chemical representation. The bound
alone does not disprove within-salt relative predictions, which need their own
independent tests. Fitting an effective sodium mobility to a second WT datum
improves selected sodium ratios but leaves substantial potassium gain errors
and is not independent validation.

**The additional-site challenge exposes a second weakness.** WT in the D127
study is 0.710 nS. Reported D127N populations are 0.675, 0.717 and 0.787 nS;
D127K populations are 0.593 and 0.690 nS. Full-trimer ordinary predictions,
normalized to this study's WT, are 0.648 and 0.591 nS. Image predictions are
**0.609 and 0.506 nS**, respectively, below every reported population mean.
The correction that helped the original gain family worsens this challenge.
Range compatibility would still not predict state probabilities. Near-pH
protonation and conformational substates are plausible missing physics, not
parameters justified for fitting to these five means.

![D127 state challenge](figures/D127_state_challenge.png)

## Numerical checks and actual resource use

The numerical test suite checks charge deposition and units, Ohmic and
concentration limits, charge-sign/Boltzmann behavior, harmonic dielectric
interfaces, manufactured-solution convergence, PB screening, closed channels,
Gauss-law balance, crowding derivatives/packing bounds, image suppression and
zero image energy in homogeneous dielectric. **13 tests passed** in the final
recorded suite; four fresh WT/EAE ordinary/image solves reproduce archived
conductances within 2.31e-9 nS for the fixed fixtures; see [validation record](validation.json).

An independent APBS3.0 homogeneous screened-charge comparison gives relative
field L2 difference **0.06791%** away from the source core. This verifies a
limited electrostatic problem, not protein dielectric geometry or biological
conductance. A planar dielectric-image calculation approaches its analytic
limit as the box is enlarged, with remaining finite-boundary error explicitly
recorded. Image maps use sampled sources, nearest interpolation, smoothing and
spatial truncation. These approximations are not a converged molecular PMF. In particular, grid
agreement of a few conductance ratios does not establish convergence of local
ion occupancy: the image model's maximum implied single-species concentration
is about 51.9 M at 0.15 nm and 84.7 M at 0.10 nm in the tested gain subset.
That is a warning about the point-ion/mean-field representation, not a measured
physical concentration. The two combined crowding sensitivities enforce finite
packing but still reach about 37.6 and 16.2 M; neither rescues independent
prediction. These diagnostics are retained rather than concealed.

Initial minority-ion transport solves passed a generic linear-solver tolerance
but had unacceptable plane-current differences (up to about 4.68%). Those
failures are archived. The solver now checks flux conservation against every
plane and the Dirichlet energy, tightens tolerance adaptively, and raises on
failure. The final recorded maximum plane spread across saved runs is
**9.71e-5 relative, below 0.01%**. This numerical repair does not constitute
experimental validation. An early image-density diagnostic omitted the penalty;
derived metadata was audited from saved fields without changing conductance.

The ordinary-model parameter study separately varied ion-access radius,
protein dielectric, aperture, slab thickness and domain size. For monomer EAE
in 1 M NaCl, predicted ratios remain about 0.938–0.963 across these perturbations,
versus the measured 1.117. Thus the original sign failure is not resolved by
these modest geometry/dielectric adjustments. This study did not establish
parameter robustness of the later image model; its tested sensitivities are
grid/source sampling, precision and crowding.

Two preparation initializations change mutant/WT ratios by at most **0.02352**
in this narrow check. They are not a backbone/rotamer ensemble or a calibrated
uncertainty distribution. Isolated-monomer PROPKA places D127 pKa near 7.59,
while the repair assumes a conventional deprotonated Asp. The estimate excludes
membrane context and is not ground truth, but the sensitivity is especially
relevant at experimental pH7.4. Protein dynamics, LPS/lipid chemistry, ion-specific
hydration/binding, salt activities and calcium effects remain absent.

| Actually executed calculation | Recorded scale/resource | Interpretation |
|---|---|---|
| Restrained EAE trimer repair | 15,117 atoms; 17.0 s; whole-device peak 252 MiB including display | OpenMM CUDA works; no MD trajectory benchmark |
| Fine monomer continuum solve | 2,629,027 grid nodes; runs about 108–213 s; peak process RSS 2,792 MiB | Local CPU/RAM sufficient; concurrent wall times |
| WT full-trimer image map, 0.10 nm, float64 | 1,836 sampled sources; 1,634 s; peak GPU allocated 1,909 MiB | Executed on the actual 16 GiB RTX 3080 Laptop |
| Same WT map, float32 | 677 s; peak GPU allocated 1,008 MiB | Different contention/warm-up; not a controlled universal speedup |
| Fine float32/64 map agreement | Max field difference 2.31e-5 kT | Backend approximation checked; not physical-model validation |

The CPU and CUDA Green operators were compared on identical point sources;
float64 differences were near numerical roundoff. CPU PDE runs use SciPy/AMG;
GPU acceleration is optional for the repeated Green solves. Timings and RSS
are actual records, not forecasts. RSS is process-lifetime high-water; sampled
whole-device memory includes display activity. No cloud spend or energy bill
was measured. Repeated cached copies are not independent benchmarks.

## Wet-lab bridge and next decision

C5R's documented CLARIOstar Plus and automation make optical bacterial assays
plausible, but they do not measure individual-channel conductance. Purification,
bilayer reconstitution and electrophysiology are not a demonstrated cheap,
low-effort C5R loop. Public inventory silence does not prove that equipment is
absent. No prices or laboratory readiness were invented.

A controlled intact-cell nitrocefin assay is a plausible lower-cost **different
objective**: kinetic plate readings can test solute permeability, with reporter
enzyme capacity, leakage, viability, efflux and porin abundance controls.
Sugar-growth or proteoliposome swelling are alternatives with their own burdens.
Higher ion conductance does not imply higher permeability to an antibiotic or
sugar; primary OmpF literature supplies counterexamples. The present ion model
has no nitrocefin/sugar objective and cannot claim to optimize those assays.
See the [assay feasibility assessment](assay_feasibility.md) for sources and
which equipment/stock/labor assumptions remain unverified.

The next investment should be a small falsifiable gate, not a design platform:

1. **For ion conductance:** obtain an independent, single-state gain cohort in
one fixed salt/pH/concentration, with full methods and a practical access route
to the conductance assay. Freeze the model and comparison rules before reading
its labels. Require better useful-gain selection than geometry/null, including
non-improvers. D127 is already evidence against treating a single fixed structure
and protonation assignment as generally sufficient.
2. **For a reader-based C5R project:** first validate an assay-aligned known
permeability control against WT and empty vector with the necessary controls.
Only then choose a substrate-specific physical observable and benchmark it.
This may change the target/observable rather than add complexity to an ion model.
3. **For further computation:** resolve a single mechanism with evidence, such
as whether WT-only ion-specific free energies/mobilities transfer to an untouched
mutant set, or whether independently assigned D127 protonation/states explain
its populations. Merely fitting extra parameters to already seen mutants is
not a passing gate. Full differentiable MD or a larger protein transformer does
not presently resolve either missing experimental evidence or assay alignment.

We materially reduced uncertainty: local physical calculations are practical;
a simple geometry baseline is surprisingly competitive for gain selection;
the image correction improves one retrospective family but does not generalize
reliably; and the affordable assay likely requires a different functional
objective. That supports continuing tightly scoped feasibility work while
withholding a claim of a validated protein-engineering loop.
