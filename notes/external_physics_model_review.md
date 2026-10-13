# External review brief: physics-based membrane-protein design feasibility

Prepared October 13, 2026. **Self-contained handoff to an independent reviewer.** The requester will supply your feedback to the implementing agent before model construction proceeds. This document includes the project context, current assessment, mathematical proposals and complete source register; repository access is not required.

## Review assignment

Act as a skeptical computational biophysics reviewer. Determine whether a small, locally executable physics-based model can predict a useful membrane-protein functional change well enough to support a bounded engineering experiment. Recommend exactly one first model/scaffold/observable combination, or a computational no-go. Challenge the assumptions and literature interpretations below rather than treating our preferred architecture as settled.

Distinguish numerical verification, agreement with another simulator, calibration to known measurements, genuinely withheld experimental validation, and prospective mutant-design evidence. Be especially precise about the variable and observable of every claimed gradient. We need an executable scientific recommendation, not a broad list of tools or an investor pitch.

If you have literature access, verify the strongest claims against primary papers and supplements. Identify missing studies, contradictory findings and inaccessible evidence explicitly. Do not invent runtime, accuracy, data availability, model capabilities or laboratory readiness. No author contact, paid compute, purchasing or external messages are requested.

## Project purpose and constraints

We are developing a computational-to-experimental membrane-protein engineering workflow at startup-funding stage. The eventual strategic interest is useful control of neuronal membrane behavior for biological computation. The immediate milestone is a real, reproducible functional protein-engineering result; neurons and task-level biological-computing validation are later milestones.

The desired eventual statement is: a supplied computational design process proposed sequence changes that reproducibly improve a specified functional phenotype in a small, practical experiment. Expression alone is an expression-engineering result; wavelength change is a photochemical-property result; neither automatically demonstrates improved ion transport. A well-controlled functional proxy is acceptable if its claim is bounded accurately.

The lab partner is a lab-automation startup acting as a force multiplier for a supplied workflow, not a CRO or specialist assay-development service. Our side must absorb modeling, assay specification, candidate selection and analysis work. Earlier project work considered bacterial GtACR2 transport readouts using publicly documented plate-reader/automation equipment, but assay compatibility remains unresolved. Do not assume patch clamp, mammalian/neuron work, a new platform, donated unlimited labor or free assay development. Prior expensive electrophysiology roadmaps were superseded and are not the immediate scope.

First physical design panels have been discussed as roughly four to eight new variants plus shared references/controls, with fresh-preparation confirmation of a promising result. Initial work may be one-shot rather than a completed adaptive design loop; scaling depends on cash and time. Repeated experiments must be economical. No final cash ceiling, calendar ceiling, biological success threshold or compute allocation has been committed for this physics phase. Do not convert provisional panel sizes into fixed power calculations.

**The user's decision rule:** modeling feasibility must be established before returning to target/readout selection. If we cannot have defensible confidence in useful design on a target within available resources, change the target or explicitly revise the phenotype. Do not accept a speculative GtACR2 experiment simply because an assay looks inexpensive. A negative feasibility result is useful.

## Local hardware and execution context

- NVIDIA GeForce RTX 3080 Laptop GPU with **16,384 MiB VRAM**; approximately 31 GiB host-visible RAM.
- User-provided host driver: 560.35.05; advertised CUDA compatibility: 12.6. Advertised compatibility is not an installed-toolkit version.
- Restricted agent execution initially could not access the GPU. Elevated execution subsequently verified GPU access and successfully ran models; this is not a host-driver fault.
- A temporary CUDA-enabled Python environment used PyTorch 2.6.0+cu126, with Transformers, xformers and adapter tooling. Nothing establishes GROMACS/OpenMM/JAX/DMFF readiness or production membrane-system compatibility yet.
- No MD throughput, PME performance, enhanced-sampling runtime, QM/MM runtime or differentiable physical-model memory has been measured. Protein-transformer speed is not a valid MD benchmark.
- Local compute is preferred. A significantly heavier model or simulation could be worth considering if it has a specific demonstrated advantage; no paid compute is currently committed. Separate a local demonstration from any proposed cloud escalation.

## What has happened before this review

The first investigated scaffold was **GtACR2**, an anion channelrhodopsin, not cation ChR2. Its immediate bacterial phenotype candidate was an abundance-aware light-driven transport-associated proxy. Gating speed and neuronal inhibition cannot be inferred directly from that assay. Bacterial truncated constructs, native GtACR2 and soma-targeted neuronal constructs are distinct objects.

Off-the-shelf protein-transformer feasibility was examined before the physical-model architecture was proposed. ESM-2 650M, ESM C 600M and AMPLIFY 350M each scored all 5,054 single substitutions in the 266-residue GtACR2 core on the local GPU. Full scans took about 6–9 seconds and BF16 inference peak allocations were about 0.69–1.23 GiB. Three-step synthetic rank-8 LoRA checks passed; they demonstrated execution/memory fit, not functional learning. No phenotype fine-tuning or new improved variant was produced.

On six selected substitutions from the 2018 bacterial study, none of the three models ranked the higher-activity E219Q first. FP32 rescoring placed it fourth, fourth and fifth respectively. All placed damaging D230N last but ranked reduced-activity E159Q above E219Q. This was a diagnostic of raw sequence-likelihood scoring, **not** a representative benchmark, a complete census of GtACR2 data, or proof that sequence models cannot help. Sequence plausibility and directional function are different objectives.

A subsequent data search retrieved:

- Bedbrook et al. 2019 engineered cation-channelrhodopsin tables: 154 measured distinct sequences with peak currents; 128 finite off-kinetics entries. The study initially used 102 functionally characterized sequences and Gaussian-process modeling. A separate 1,133-record table contains predicted designs, not extra measured labels.
- Kir2.1 function and trafficking source tables: about 7,000 records each. The mammalian tagged construct and processed-data numbering require audit. ProteinGym contains 6,963 functional records and 6,917 trafficking records for this study.
- FLIP2 Rhomax: 884 records, 878 distinct sequences, absorption-wavelength labels. This is a possible alternate property-engineering task, not transport supervision.
- Published ProteinGym correlations for nearby assays, including 15B/100B models. Larger backbone size did not consistently improve performance. Those were externally reported results, not local functional validation; overall correlation does not establish above-reference hit selection.

We then distinguished sequence modeling, structure prediction, inverse folding, phenotype-supervised prediction and physical simulation. AlphaFold supplies structural hypotheses; high coordinate confidence does not establish current or kinetics. Physics itself has sampling, parameterization and extrapolation problems, so it also requires withheld validation.

## User-proposed architecture

1. A folding/structure model, such as AlphaFold, supplies protein structures.
2. A physics-based model simulates the relevant function.
3. An optimizer selects mutants using the system as its evaluator/objective.

The user believes steps 1–2 can be assessed computationally within reason and recognizes that outside-distribution performance is difficult. Our clarification is that computational consistency is useful verification, but functional validation still requires independent experimental reference measurements. We should use existing published data before committing to new experiments.

Our current proposal adds explicit **functional states and environment** between folding and function. Candidate model chain:

`sequence → state-specific structures/topologies → physical energies/diffusion/rates → functional observable with uncertainty → discrete mutation selection`.

A predicted resting conformation does not automatically supply a conducting pore, membrane assembly, protonation pattern, lipid dependence, photointermediates, state populations or transition rates. A model valid for an already open pore should not be presented as predicting the entire actuator response.

## Provisional proposal to challenge

The most promising provisional first architecture is **conventional atomistic simulation as a reference/calibration tool plus a reduced differentiable transport model as the inner objective**. A PMF/diffusion-based permeation model or constrained electrodiffusion solver could be cheaper to differentiate and evaluate than repeated long trajectories. A Markov/photocycle model is useful only if mutation-dependent transition rates can be supplied credibly.

Possible calibration scaffolds, not selected physical targets:

- Gramicidin A: small ion-permeation precedent with reduced free-energy/friction dynamics; limited equivalence to full neuronal-channel engineering.
- A high-conductance bacterial porin such as one used in published CompEL work: possible direct transport benchmark; exact structure, mutant controls, parameter files and assay conditions remain to be chosen.
- Aquaporin/AqpZ/GlpF: water permeability may avoid photocycle complexity; different function and strategic claim.
- MscL: membrane-tension/hydration gating may offer a physical objective, but physiological kinetics and neuronal relevance remain problematic.
- GtACR1/GtACR2 or C1C2: strongest optogenetic continuity, but chromophore chemistry, protonation and appropriate open states increase burden. Adjacent models cannot silently substitute for exact-scaffold validation.

Do not preserve this shortlist if a better scaffold has experimentally grounded state models and useful mutant data. Also consider whether a gradient-free bounded optimizer is more defensible initially: differentiability is desirable, not a reason to accept a poor functional approximation.

## Assumption register

| ID | Assumption or unresolved claim | Current status | Review needed |
|---|---|---|---|
| A1 | A useful first phenotype can be separated from complete channel gating | Proposed scope reduction | Choose the phenotype and explain what it excludes |
| A2 | Relevant conducting/conformational states are available | Unresolved and target-dependent | Identify actual structures, state evidence and missing transitions |
| A3 | Force-field chemistry is accurate enough for useful mutant differences | Unresolved; strong sensitivity evidence | Assess ions, water, polarization, lipids, protonation and chromophores |
| A4 | One/few collective coordinates adequately describe permeation | Approximation, not established universally | Identify correlated ions, slow protein motion and projection failures |
| A5 | Effective diffusion/friction can be estimated and transferred between mutants | Unresolved | Specify estimation, uncertainty and recalculation requirements |
| A6 | A reduced model predicts function better than simple geometric/electrostatic heuristics | Untested | Define equal-budget baselines and withheld comparisons |
| A7 | Physical gradients can guide discrete mutation selection | Proposed bridge, not demonstrated here | Specify which derivative exists and how it maps to chemistry/topology changes |
| A8 | Reweighting reference trajectories gives adequate mutant sensitivity | Conditional on ensemble overlap | Require overlap/effective-sample-size checks and resampling policy |
| A9 | Local membrane simulation is fast enough to support repeated design evaluation | Unmeasured | Propose a representative benchmark rather than asserting ns/day |
| A10 | Existing experimental labels permit independent validation | Partly supported nearby; exact-target gap | Identify exact measurements, conditions, controls and grouping |
| A11 | A single-channel prediction maps to the eventual inexpensive assay | Unresolved | Separate abundance, host physiology and detector effects |
| A12 | A calibrated parameter set transfers without mutant-specific refitting | Required for the intended prediction claim, unproven | Freeze calibration and test withheld variants/conditions |
| A13 | The architecture supports beneficial improvement rather than merely damage detection | Unproven | Evaluate above-reference selection and uncertainty |
| A14 | A computational calibration scaffold is also an appropriate final biological target | Not assumed | Separate software calibration, engineering scaffold and neural relevance |

## Specific scientific hazards to examine

The source search is targeted, not systematic or exhaustive. Some findings were inspected primarily through abstracts/documentation; supplements, trajectories, experimental conditions and prospective-validation claims need stronger audit before implementation. A source-register entry means it is relevant, not that its claims are endorsed. We have not independently reproduced any physical result.

Particular hazards include circular force-field calibration; fitting WT while claiming mutant generalization; wrong channel state; mismatched experimental ionic/membrane conditions; ion dehydration/polarization errors; insufficient independent events; altered kinetics under biased/coarse-grained sampling; invalid one-dimensional reduction; missing multi-ion correlations; confounded abundance/current; and an optimizer exploiting the model rather than improving the molecule.

Differentiating energy to obtain forces is not differentiating a functional design objective. Event counts, hard bins, remeshing, particle insertion/exchange and changing sequence topology can obstruct gradients. A formally differentiable finite simulation can have poor long-time gradient estimates. Equilibrium reweighting does not determine transition rates. Multiple predicted structures are not automatically a Boltzmann ensemble. Free-energy barriers require dynamical prefactors to become rates.

Keep **physics calibration parameters fixed during protein design** unless they represent a physically defined mutation transformation. Freely changing force-field charges to maximize current would optimize the simulator. Alchemical paths require correct actual end states and appropriate electrostatic/topology treatment.

## Requested reviewer response

Please return a self-contained review with:

1. **Verdict:** GO, conditional GO, or no-go for a local physics-based functional-design prototype; separately assess an exact GtACR2 route.
2. **Corrections:** major factual/mathematical errors, overstated evidence, missing assumptions and contradictory primary sources. Distinguish confirmed problems from your uncertainty.
3. **One first build:** exact scaffold/construct, phenotype, structural states, physical method and reason it is preferable to the alternatives. If none is defensible, identify the smallest evidence-gathering step that could change that conclusion.
4. **Gradient contract:** the observable, differentiated variable, estimator/solver, noise treatment, discrete-mutation bridge, and whether the gradient capability is published, mathematically inferred or newly proposed.
5. **Resource assessment:** exact system size where available, parameter/software requirements, local benchmark to run, expected dominant cost and any justified heavier-compute escalation. Mark estimates as estimates.
6. **Validation plan:** concrete published WT/control/mutant measurements, input availability, calibration/test separation, numerical checks, physical uncertainty, sensible pass/fail criteria and competing baselines. Separate a solver demonstration from functional prediction and prospective engineering.
7. **Implementation plan:** smallest milestones, required artifacts and explicit stop/pivot conditions. Identify which steps are ready to implement and which depend on unavailable evidence.

For each claim of predictive success, identify whether it is mechanistic interpretation, fit/calibration, genuinely held-out prediction or prospective design. If quoting model quality, give the actual observable, number of independent proteins/mutants, experimental context and split. Do not infer a percentage of correct improvements from rank correlation.

## Proposed implementation gates after review

These gates are proposals for you to revise, not predetermined approval criteria:

- **G0 — Inputs:** verified construct/state/chemistry, reproducible initial system and usable independent functional reference data.
- **G1 — Numerical verification:** units, conservation, equilibrium/limiting cases, mesh/time-step convergence, energy/force agreement where relevant, and gradient-versus-finite-difference checks.
- **G2 — Physical calibration:** reproduce a bounded WT/control observable with uncertainty and fixed experimental conditions; report parameters selected against that data.
- **G3 — Withheld validation:** predict altered-function mutants or conditions without retuning. Compare against simple structure/conservation/lookup baselines and report uncertainty and failures.
- **G4 — Design usefulness:** show useful ranking or improvement-tail selection at a small equal evaluation budget; validate any relaxed/alchemical proposal at actual discrete end states.
- **G5 — Experimental fit:** only after the computational gates, revisit a low-burden target/readout and prospective confirmation design.

We will build and validate the physics model after the requester supplies this independent review. No new physical model implementation is claimed in this handoff.

## Appendices

Appendix A reproduces the current physics-model search assessment. Appendix B supplies the proposed mathematical objectives and assumptions. Appendix C includes all source-register entries with direct external URLs. Their recommendations are provisional and are the subject of this review.


## Appendix A: physics-model search assessment


October 13, 2026. Targeted primary-literature and implementation search. No simulations, runtime benchmarks or new mutant predictions were performed. References and evidence limits are recorded in [the source register](#appendix-c-source-register).

### Findings and decision relevance

Physics-based functional models exist, but there is no single simulator that turns any folded membrane protein into a reliable functional prediction. The strongest direct functional examples concern permeation through an already conducting pore, water permeability, and selected mutant/state comparisons. Predicting complete gating or transport cycles adds a difficult state/rate problem. Gradients are best established for force-field parameters, reduced-model parameters and equilibrium observables; this is not the same as validated gradients of functional improvement with respect to amino-acid sequence.

For the proposed fold → function → optimizer system, prioritize a **hybrid functional model**: atomistic calculations establish or calibrate state-specific energies, diffusion and geometry; a reduced transport/kinetic solver provides the cheap objective and sensitivities. Validate the sequence-to-physical-parameter step separately. This is our proposed architecture, not an established turnkey membrane-protein design method.

### Functional-model taxonomy

| Model | Functional observable | What must be supplied | Differentiability status | Principal limitation |
|---|---|---|---|---|
| Explicit atomistic MD under voltage / CompEL | Ionic current, conductance, selectivity, reversal potential | Conducting structure, membrane, ions, force field, voltage/concentration protocol | Forces derive from energy gradients; standard permeation-count workflows are not end-to-end mutation optimizers | Event statistics, force-field error, channel-state validity and long sampling |
| Brownian/Langevin ion dynamics | Current and selectivity in a reduced pore representation | Effective electrostatics/PMF, diffusion/friction, bath boundaries | Smooth forces support pathwise derivatives in a suitable implementation; event counting/boundaries require special treatment | Implicit solvent/protein and missing collective effects; noisy trajectory gradients |
| Poisson–Nernst–Planck (PNP) / reduced electrodiffusion | Steady current, I–V response, ionic concentration | Geometry, charge, dielectric and diffusion profiles, boundary conditions | Implicit/adjoint gradients mathematically available under regularity; no validated sequence-design pipeline identified | Mean-field approximations can fail in narrow, correlated multi-ion pores |
| PMF + diffusion / reduced transport | Permeation barriers, flux and selectivity estimates | Sampled free-energy profile and diffusion/friction along a defensible coordinate | Reduced solver can be differentiated; obtaining accurate parameter-dependent profiles is the harder upstream step | Reaction-coordinate quality, multi-ion effects and uncertain diffusion |
| Hydrophobic wetting/dewetting | Conducting-state plausibility and water-entry energetics | Pore geometry, chemistry, water sampling | Equilibrium sensitivities/smoothed observables plausible; CHAP itself is not a demonstrated autodiff transport optimizer | A wetted pore need not conduct the intended ion; not a quantitative gating-time model |
| Free-energy/alchemical state comparisons | Relative binding or open/closed-state stability | Matched states and mutation topologies, reliable sampling | Thermodynamic derivatives and reweighting available for continuous coupling parameters | Relative equilibrium stability does not determine rates or absolute conductance |
| Markov/master-equation/photocycle models | Open probability, transient current, recovery/closing behavior | State graph, rates, conductance per state, stimulus dependence | Rate sensitivities and ODE gradients demonstrated; often inexpensive | Sequence-to-rate map is absent unless supplied by physics or measurements |
| QM/MM photochemistry | Retinal excitation/isomerization, proton-transfer mechanisms, spectra | Electronic model, chromophore/protein states and environment | Some energy derivatives exist; nonadiabatic trajectories/whole photocycle are a separate problem | Specialized parameters, expensive sampling, multiple electronic/protonation states |
| Transporter adaptive MD + MSM | State populations/transitions and cycle mechanisms | Extensive transitions, substrate/ion occupancy, state definition | Reduced transition model differentiable once parameterized; raw clustering/counts not automatically so | Mechanism/state discovery is not automatically validated turnover-rate prediction |

### Primary functional precedents

**CompEL — Kutzner et al. 2011.** [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC3175076/) and [current GROMACS implementation](https://manual.gromacs.org/documentation/current/reference-manual/special/comp-electrophys.html). A charge/concentration imbalance drives sustained ionic flux, enabling experimental-style current/voltage comparisons. This is a functional simulator, not just structural relaxation. Its double-membrane setup and stochastic crossing statistics add cost. Conducting-state calculations do not establish a channel's open probability or light-off kinetics. The ion/water exchange protocol contains discrete operations; naïve autodiff of its implementation would not resolve them.

**Reduced permeation — Jäger, Koslowski and Wolf 2022.** [dcTMD + Langevin conductance paper](https://pubmed.ncbi.nlm.nih.gov/34928150/). Gramicidin A serves as a test system: targeted atomistic sampling produces effective free-energy/friction information; reduced Langevin dynamics predicts I–V characteristics. Particularly relevant to a multiscale objective. This is not a universal membrane-channel model or a published differentiable sequence optimizer. Gramicidin is a useful small calibration system, not equivalent to engineering a full neuronal channel.

**Aquaporins — Zhu, Tajkhorshid and Schulten 2004.** [AQP1 permeability study](https://pubmed.ncbi.nlm.nih.gov/14695248/) and [collective-diffusion model](https://pubmed.ncbi.nlm.nih.gov/15601094/). These provide functional permeability estimators from atomistic water dynamics, with experimental comparison for AQP1. Equilibrium water permeability is a potentially simpler physics milestone than rhodopsin gating, although correlated dynamical observables still need valid gradients and sampling. Aquaporins are water channels, not optical actuators; no local assay fit is assumed.

**Channelrhodopsin mutant/state comparison — Prignano et al. 2024.** [C1C2 WT/N297D metadynamics study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11379304/). Combines electrophysiology with ion-permeation PMFs in two modeled open states; examines altered Na/Ca selectivity. The protocol uses eight walkers for each state/ion/protein system and explicit chromophore/protonation-state modeling. Strong adjacent mechanistic precedent, but principally a known-mutant explanation and state-dependent barrier analysis, not proof of prospective ranking across a mutant library or light-off-rate prediction.

**Force-field accuracy remains a central risk — Hui et al. 2025.** [Potassium-channel polarization study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12130843/). Conductance predictions change substantially with electronic-continuum corrections and force-field details. Experimental I–V agreement improves across NaK2K, TRAAK and MthK, but parameters are explored/adjusted and the authors do not claim one universal patch. Freeze calibration before withheld-mutant testing; reproducing a quantity used to select parameters is not independent validation. This paper is a reason to audit physical-model error, not to abandon physical models.

**MscL tension-dependent gating.** [2012 WT/G22N MD](https://pmc.ncbi.nlm.nih.gov/articles/PMC3508910/) and [2026 WT/Q65 variants](https://pmc.ncbi.nlm.nih.gov/articles/PMC13174807/) connect applied membrane stress/pulling, hydration and open-like conformations with functional mutants. They offer mechanical gating hypotheses, but imposed force/tension trajectories must not be equated with physiological opening-time predictions. A reduced free-energy-versus-tension model is an attractive candidate objective only after calibration.

**GtACR1 and rhodopsin photochemistry.** [GtACR1 2023 MD](https://www.mdpi.com/2227-9717/11/2/510) studies opening and chloride-pathway energetics; [ChR2 QM/MM + MD, 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5889620/) models early photocycle events with spectral checks; [C1C2 QM/MM photodynamics, 2019](https://doi.org/10.1002/cptc.201800185) addresses initial photoreaction time components. These are adjacent mechanisms, not a verified full GtACR2 sequence-to-functional-phenotype simulator. Ordinary ground-state MD cannot simply replace photochemistry. GtACR2 bacterial pH slopes additionally depend on abundance and host physiology, beyond a single-channel model.

**Gating and transporter kinetics.** [2025 ion-channel parameter inference](https://pmc.ncbi.nlm.nih.gov/articles/PMC11904632/) explicitly solves sensitivity equations for likelihood gradients in a stochastic gating model. [ChR2 photocycle models, 2009](https://doi.org/10.1111/j.1751-1097.2008.00460.x) provide stimulus-to-current models. These support differentiable rates-to-current computation, not sequence-to-rates prediction. [LeuT MSM, 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5675527/) studies ion/substrate-dependent conformational states; it does not establish a ready-made sequence-to-turnover model.

### Differentiable implementations and evidence boundaries

**DMFF (2023).** [Paper](https://doi.org/10.1021/acs.jctc.2c01297), [repository](https://github.com/deepmodeling/DMFF). JAX-based differentiable force fields and estimators for energies, free energies and ensemble averages. A credible component for continuous parameter sensitivity/calibration. A working differentiable force field does not establish correct long-time channel dynamics or a mutant-design objective. Porting a production membrane system requires auditing supported interactions and matching energies/forces to the reference engine.

**JAX MD.** [Primary methods paper](https://arxiv.org/abs/1912.04232), [repository](https://github.com/jax-md/jax-md). Differentiable simulation infrastructure; not a turnkey, experimentally validated membrane-channel conductance package. Infrastructure capability should be separated from functional validation.

**Molly.jl and differentiable protein MD.** [2024 disordered-protein force-field study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10966991/), [implementation documentation](https://juliamolsim.github.io/Molly.jl/dev/differentiable/). Demonstrates parameter optimization through simulation and discusses reversible differentiation and gradient stability. Its validation target is not membrane-channel current or mutant gating. Stochastic gradients need repeat-run and finite-difference checks.

**DiffTRe (2021).** [Primary paper](https://www.nature.com/articles/s41467-021-27241-4). Differentiable equilibrium trajectory reweighting avoids backpropagation through every MD step. Demonstrations include water and diamond models, not protein-channel mutant design. It provides a promising route for equilibrium free-energy/occupancy objectives when reference and perturbed ensembles overlap; it does not supply transport rates from equilibrium weights alone. Effective sample size and resampling are essential.

**Differentiable particle-field membrane simulation (2024).** [Primary paper](https://doi.org/10.1021/acs.jcim.4c00564). Demonstrates gradient-based lipid force-field fitting and membrane-property checks. This is actual membrane-related differentiation, but lipid structure/pressure/density properties are not membrane-protein function. Coarse-grained accelerated dynamics need not preserve physical kinetic times.

**Dynamical-observable gradients (2025).** [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11742923/) extends differentiable potential refinement to time-correlation-based properties and discusses growing gradient noise. Important for permeability/friction objectives, but not direct evidence of stable gradients for long protein gating events.

**Alchemical mutation free energies.** [Hv1 study](https://www.nature.com/articles/s41598-020-70369-4) calculates mutation-dependent ligand-binding free energies with explicit coupling parameters. This is a real mutation-to-energetics precedent, but the endpoint is binding, not intrinsic channel transport. Evaluating a thermodynamic cycle for open versus closed states is a proposed extension here, not demonstrated by that paper.

I did not identify a published, turnkey, experimentally validated chain of continuous sequence optimization → folded channel → differentiable physics → improved GtACR2 function. A nearby gradient-through-AF2 sequence-design paper [soluble membrane-protein analogues, 2024](https://doi.org/10.1038/s41586-024-07601-y) is relevant to sequence relaxation, but its optimization is structural and must not be counted as differentiating through physical channel transport.

### What can be differentiated, exactly?

Record the derivative's variable and observable for every proposal:

1. `dU/dcoordinates`: forces. Standard MD already uses this; it is not a gradient of design success.
2. `d(expected observable)/dphysical parameters`: potentially useful for calibration, sensitivity or controlled alchemical changes. Equilibrium and dynamical derivatives are different.
3. `d(current)/dPMF`, `d(current)/ddiffusion`, `d(current trace)/drates`: useful reduced-model sensitivities, with established numerical methods or direct derivations.
4. `d(objective)/dsequence`: residues are discrete, change topology/protonation and can change functional states. Continuous relaxations and alchemical paths are tools for proposals, not guarantees that the relaxed optimum corresponds to a viable mutant.

Avoid freely changing calibrated force-field parameters to maximize function: that would optimize the simulator rather than the protein. Keep physics calibration separate from design variables. Large mutation changes can destroy overlap for reweighting or invalidate a previously derived reduced state model.

Direct crossing counts and hard bins are discontinuous. Smooth density/flux observables can help, but must be checked against the real measured quantity. Pathwise derivatives through stochastic dynamics require a defined noise treatment; mathematically existing finite-trajectory derivatives may be high-variance or fail to approximate derivatives of long-time steady observables. Adjoint methods are not a universal fix for chaos or rare-event sampling.

### Recommended computational feasibility route

Start with an experimentally benchmarked conducting pore or water channel, rather than full GtACR2 photogating. Candidate **calibration systems**, not selected wet-lab targets: gramicidin for a small permeation model; a high-conductance bacterial porin for transport; aquaporin/GlpF for water permeability. Choose exact systems from available structures, parameter files, raw functional controls and mutation data. Neural relevance differs and remains part of later target selection.

Use conventional GPU MD as the reference, and a reduced PMF/electrodiffusion or kinetic model as the differentiable inner objective. First reproduce boundary-condition/limiting-case behavior and check gradients against finite differences. Then test physical calibration on WT and compare blinded known variants without recalibration. Only then evaluate whether gradients lead to better discrete proposals than finite-budget enumeration/heuristics.

Local cost estimates remain qualitative: reduced one-dimensional transport or small ODE models are likely inexpensive; membrane MD needs a representative system benchmark; multi-window/multi-walker sampling, complete gating, transporter turnover and QM/MM can dominate cost. No ns/day or wall-time claim for this RTX 3080 is justified by literature alone.

For GtACR2, the smallest plausible physical question is state-specific anion permeation in a justified conducting model. Predicting light-off kinetics from sequence requires additional state energetics, transition pathways and photochemical validation. A successful permeation benchmark would not establish the latter or predict the bacterial proxy without a host/readout model.

The optimization mathematics and assumptions are sketched in [the reduced-objective note](#appendix-b-mathematical-objectives). This search recommends a testable model hierarchy, not committing to an assay or declaring physical-model feasibility already established.


## Appendix B: mathematical objectives


October 13, 2026. Proposed modeling scaffold, not a validated protein-function predictor. Literature context: [physics-model assessment](#appendix-a-physics-model-search-assessment).

### One-dimensional steady permeation

Let z range from 0 to L. Let rho(z) be the linear ion density, D(z)>0 a diffusion coefficient, and W(z;theta) a potential of mean force including the applied electrical energy and any consistent geometric entropy convention. Under a dilute, overdamped, single-coordinate approximation,

\[
J=-D(z)\left[\partial_z\rho+\beta\rho\partial_z W\right],\qquad \beta=(k_BT)^{-1}.
\]

For fixed boundary densities, integrating the stationary equation gives

\[
J(\theta)=\frac{\rho(0)e^{\beta W(0;\theta)}-\rho(L)e^{\beta W(L;\theta)}}{\int_0^L e^{\beta W(z;\theta)}D(z;\theta)^{-1}\,dz},\qquad I=qJ.
\]

J has units of particles/time because rho is particles/length. Boundary densities must be mapped consistently from bath concentrations and pore cross-section. Variable area can be folded into an entropic potential with corresponding boundary conventions; it must not be silently omitted.

This provides differentiable dependence on discretized W and positive D. A constant shift of W cancels and cannot be treated as a design improvement. Lowering a single barrier is not automatically sufficient: binding wells, entry density and friction matter. Stable exponential quadrature and positive-parameter representations are required numerically.

This model does not capture correlated multi-ion knock-on, an unreliable reaction coordinate, or changing protein states. Accurate gradients through this formula do not prove accurate permeation predictions or supply the upstream sequence-to-W/D map.

### Implicit electrodiffusion sensitivities

For a discretized steady PDE with residual R(u,theta)=0, let the objective be O(u,theta). If the boundary-constrained Jacobian R_u is invertible,

\[
\frac{du}{d\theta}=-R_u^{-1}R_\theta.
\]

An adjoint lambda solving R_u^T lambda=O_u^T yields

\[
\frac{dO}{d\theta}=O_\theta-\lambda^T R_\theta.
\]

This is our mathematical route for differentiating a suitable PNP/reduced transport solve, not evidence that a particular published channel solver exposes these derivatives or predicts mutants. Discontinuous remeshing, hard molecular boundaries, nonunique solutions and missing correlations require separate treatment.

### Equilibrium observable gradients

For a fixed-topology canonical distribution proportional to exp[-beta U_theta(x)] and observable A_theta(x),

\[
\partial_\theta\langle A\rangle=\langle\partial_\theta A\rangle-\beta\operatorname{Cov}(A,\partial_\theta U).
\]

The identity motivates equilibrium reweighting and free-energy derivatives without differentiating a whole trajectory. Reference samples must cover the perturbed ensemble. It does not by itself give a derivative of a transport coefficient or transition rate. For mutation alchemy, shared/dual topology and proper dummy-atom/end-state treatment are necessary.

### State populations and kinetics

With two equilibrium states and DeltaG=G_open-G_closed,

\[
P_{open}=\frac{1}{1+e^{\beta\Delta G}},\qquad \partial_\theta P_{open}=-\beta P_{open}(1-P_{open})\partial_\theta\Delta G.
\]

This equilibrium formula must not be applied unmodified to a driven photocycle. For state probabilities p and a continuous-time generator Q(theta,stimulus),

\[
\dot p=Q^T p,\qquad I(t)=N\sum_s p_s(t)i_s(V,\theta).
\]

ODE sensitivities differentiate the stimulus-to-current model. Protein sequence does not automatically specify Q. Barrier energies alone do not determine absolute rates without prefactors and a defensible reaction-coordinate/dynamical model. State-dependent detailed balance must be applied only where thermodynamically appropriate, accounting for driving.

### Design objective and validation

Use a phenotype-specific objective, for example expected desired-ion flux subject to unintended leakage/selectivity and protein-viability constraints. Distinguish simulation calibration parameters from allowed protein design variables. Candidate gain must exceed uncertainty due to sampling and physical-model assumptions; penalizing uncertainty is a decision rule, not a substitute for validation.

Gradients over physical parameters can guide where to perturb. Discrete mutation proposals still require actual end-state structures, correct topology/chemistry, new sampling and independent functional evaluation. Compare that proposal mechanism with enumeration or a simple heuristic at the same evaluation budget.


## Appendix C: source register

These 29 entries include papers and software documentation. They record scope and limitations; they are not 29 independent validations.

### P01 — Computational Electrophysiology: The Molecular Dynamics of Ion Channel Permeation and Selectivity in Atomistic Detail (2011)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC3175076/).

Role: functional simulation. Observable: current and selectivity. Gradient status: not a demonstrated end-to-end mutation gradient. Evidence boundary: conducting-state protocol and selected experimental comparisons.

### P02 — GROMACS computational electrophysiology documentation (current)

[Primary source or official documentation](https://manual.gromacs.org/documentation/current/reference-manual/special/comp-electrophys.html).

Role: implementation. Observable: current conductance selectivity reversal potential. Gradient status: discrete exchange and event-count workflow. Evidence boundary: software capability not universal functional validation.

### P03 — Tests of Continuum Theories as Models of Ion Channels II (2000)

[Primary source or official documentation](https://openresearch-repository.anu.edu.au/items/1d061e91-45a0-49c0-8d73-7edbe612d7cb).

Role: model limitation. Observable: PNP versus Brownian-dynamics conductance. Gradient status: implicit sensitivities are a proposed numerical route. Evidence boundary: mean-field breakdown in narrow model pores.

### P04 — Testing the Applicability of Nernst-Planck Theory in Ion Channels (2011)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC3121742/).

Role: reduced transport. Observable: conductance and concentration profiles. Gradient status: reduced equations potentially differentiable. Evidence boundary: profile accuracy and reduced approximations matter.

### P05 — Predicting Ion Channel Conductance via Dissipation-Corrected Targeted Molecular Dynamics and Langevin Equation Simulations (2022)

[Primary source or official documentation](https://pubmed.ncbi.nlm.nih.gov/34928150/).

Role: hybrid functional model. Observable: gramicidin I-V response. Gradient status: no sequence-gradient validation identified. Evidence boundary: abstract supports reduced functional model rather than arbitrary-protein prediction.

### P06 — Theory and simulation of water permeation in aquaporin-1 (2004)

[Primary source or official documentation](https://pubmed.ncbi.nlm.nih.gov/14695248/).

Role: functional simulation. Observable: osmotic water permeability. Gradient status: no design gradients demonstrated. Evidence boundary: experimental permeability comparison for selected system.

### P07 — Collective diffusion model for water permeation through microscopic channels (2004)

[Primary source or official documentation](https://pubmed.ncbi.nlm.nih.gov/15601094/).

Role: reduced functional estimator. Observable: equilibrium-to-osmotic permeability. Gradient status: dynamical observable needs gradient method. Evidence boundary: not a validated sequence optimizer.

### P08 — CHAP: A Versatile Tool for the Structural and Functional Annotation of Ion Channel Pores (2019)

[Primary source or official documentation](https://doi.org/10.1016/j.jmb.2019.06.003).

Role: pore annotation. Observable: pore hydration and geometry. Gradient status: no native autodiff optimizer established. Evidence boundary: not quantitative current or closing kinetics.

### P09 — Metadynamics simulations reveal mechanisms of Na+ and Ca2+ transport in two open states of the channelrhodopsin chimera C1C2 (2024)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11379304/).

Role: mutant-state mechanism. Observable: ion permeation PMF and selectivity. Gradient status: no published sequence gradient demonstrated. Evidence boundary: known-mutant mechanistic comparison with electrophysiology rather than library prospective prediction.

### P10 — Effective polarization in potassium channel simulations: Ion conductance occupancy voltage response and selectivity (2025)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12130843/).

Role: functional simulation and calibration. Observable: I-V and selectivity. Gradient status: parameter dependence studied rather than autodiff design. Evidence boundary: force-field tuning complicates claims of independent prediction.

### P11 — The gating mechanism of the bacterial mechanosensitive channel MscL revealed by molecular dynamics simulations (2012)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC3508910/).

Role: mechanical gating. Observable: opening under membrane tension and mutant hydration. Gradient status: no sequence gradient demonstrated. Evidence boundary: imposed stress and restricted energetics not validated general kinetics.

### P12 — Opening threshold and kinetics of the MscL mechanosensitive channel are regulated by its periplasmic loop (2026)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC13174807/).

Role: mechanical gating mutant comparison. Observable: tension-dependent opening. Gradient status: not autodiff sequence design. Evidence boundary: open-like response under imposed stimuli not a universal sequence-to-rate map.

### P13 — The Mechanism of Channel Opening of Anion Channelrhodopsin GtACR1: A Molecular Dynamics Simulation (2023)

[Primary source or official documentation](https://www.mdpi.com/2227-9717/11/2/510).

Role: adjacent ACR mechanism. Observable: opening and chloride pathway energetics. Gradient status: no demonstrated mutation-gradient objective. Evidence boundary: GtACR1 is not GtACR2 and mechanism does not establish prospective ranking.

### P14 — Retinal isomerization and water-pore formation in channelrhodopsin-2 (2018)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5889620/).

Role: photochemistry and state modeling. Observable: spectra and preopen pore formation. Gradient status: energy derivatives not full functional design gradients. Evidence boundary: preopen water pore is not ion conduction or closing rate.

### P15 — QM/MM Photodynamics of Retinal in the Channelrhodopsin Chimera C1C2 with OM3/MRCI (2019)

[Primary source or official documentation](https://doi.org/10.1002/cptc.201800185).

Role: photochemistry. Observable: initial photoreaction time components. Gradient status: no end-to-end mutant transport gradients established. Evidence boundary: initial photochemistry not whole channel photocycle.

### P16 — Parameter inference for stochastic reaction models of ion channel gating from whole-cell voltage-clamp data (2025)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11904632/).

Role: kinetic inference. Observable: current trace likelihood. Gradient status: rate-parameter sensitivity equations. Evidence boundary: experimental inference does not supply sequence-to-rate prediction.

### P17 — Photocycles of Channelrhodopsin-2 (2009)

[Primary source or official documentation](https://doi.org/10.1111/j.1751-1097.2008.00460.x).

Role: photocycle kinetic model. Observable: light-driven state occupancy and photocurrent. Gradient status: smooth ODE parameter gradients possible. Evidence boundary: phenomenological rates need measurements or independent physics.

### P18 — Structure and Dynamics Study of LeuT Using the Markov State Model and Perturbation Response Scanning Reveals Distinct Ion Induced Conformational States (2017)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC5675527/).

Role: transporter state dynamics. Observable: ion-substrate-dependent states. Gradient status: reduced transition models differentiable after parameterization. Evidence boundary: not a complete validated sequence-to-turnover model.

### P19 — DMFF: An Open-Source Automatic Differentiable Platform for Molecular Force Field Development and Molecular Dynamics Simulation (2023)

[Primary source or official documentation](https://doi.org/10.1021/acs.jctc.2c01297).

Role: differentiable infrastructure. Observable: energies free energies ensemble averages. Gradient status: automatic differentiation implemented. Evidence boundary: force-field development is not demonstrated membrane-protein functional design.

### P20 — DMFF official implementation (current)

[Primary source or official documentation](https://github.com/deepmodeling/DMFF).

Role: differentiable infrastructure. Observable: JAX force fields. Gradient status: implemented parameter and coordinate derivatives. Evidence boundary: production membrane-system compatibility needs audit.

### P21 — JAX M.D.: A Framework for Differentiable Physics (2020)

[Primary source or official documentation](https://arxiv.org/abs/1912.04232).

Role: differentiable infrastructure. Observable: particle simulation. Gradient status: automatic differentiation implemented. Evidence boundary: not turnkey membrane-channel functional predictor.

### P22 — JAX MD official implementation (current)

[Primary source or official documentation](https://github.com/jax-md/jax-md).

Role: differentiable infrastructure. Observable: particle dynamics. Gradient status: autodiff GPU infrastructure. Evidence boundary: local membrane runtime unmeasured.

### P23 — Learning neural network potentials from experimental data via Differentiable Trajectory Reweighting (2021)

[Primary source or official documentation](https://www.nature.com/articles/s41467-021-27241-4).

Role: equilibrium gradient method. Observable: thermodynamic structural and mechanical observables. Gradient status: reweighting gradients demonstrated. Evidence boundary: water and diamond demonstrations with ensemble-overlap requirements not mutant channel rates.

### P24 — Differentiable simulation to develop molecular dynamics force fields for disordered proteins (2024)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC10966991/).

Role: protein parameter optimization. Observable: disordered-protein ensemble properties. Gradient status: trajectory differentiation demonstrated. Evidence boundary: not membrane current or mutation design validation.

### P25 — Molly.jl differentiable simulation documentation (current)

[Primary source or official documentation](https://juliamolsim.github.io/Molly.jl/dev/differentiable/).

Role: differentiable implementation. Observable: force-field parameters and simulation objectives. Gradient status: reverse-mode and reversible methods documented. Evidence boundary: gradient repeatability and functional compatibility require testing.

### P26 — Learning Force Field Parameters from Differentiable Particle-Field Molecular Dynamics (2024)

[Primary source or official documentation](https://doi.org/10.1021/acs.jcim.4c00564).

Role: membrane parameter optimization. Observable: lipid density and membrane properties. Gradient status: differentiable fitting demonstrated. Evidence boundary: lipid-property validation not membrane-protein transport.

### P27 — Refining potential energy surface through dynamical properties via differentiable molecular simulation (2025)

[Primary source or official documentation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11742923/).

Role: dynamical gradient method. Observable: time-correlation properties. Gradient status: trajectory and reweighting methods with gradient-noise discussion. Evidence boundary: not demonstrated gradients for long channel gating.

### P28 — Insights on small molecule binding to the Hv1 proton channel from free energy calculations with molecular dynamics simulations (2020)

[Primary source or official documentation](https://www.nature.com/articles/s41598-020-70369-4/).

Role: mutation alchemy. Observable: relative ligand-binding free energies. Gradient status: continuous alchemical coupling. Evidence boundary: not prediction of native channel conductance or open-closed equilibrium.

### P29 — Computational design of soluble and functional membrane protein analogues (2024)

[Primary source or official documentation](https://doi.org/10.1038/s41586-024-07601-y).

Role: sequence optimization adjacent evidence. Observable: structure-guided sequence design. Gradient status: gradient through AlphaFold input sequence demonstrated. Evidence boundary: not a physics-based ion transport objective.
