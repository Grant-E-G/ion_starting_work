# Agent Brief: Computational Viability of Membrane-Protein Engineering for Mentat × C5R

**Date:** October 12, 2026  
**Status:** Research + computational proof-of-concept; no experimental commitment  
**Owner:** Mentat Biotechnology  
**Decision:** Choose a first, exceptionally low-effort bacterial membrane-protein design/test project between **GtACR2 / closely related microbial rhodopsins** and **E. coli MscL**, or recommend **neither**.

## 1. Mission

Determine whether modern off-the-shelf protein models and agent tooling can **predict useful, experimentally testable functional changes in a membrane protein** well enough to justify a tiny C5R collaboration. Do not merely produce speculative mutation lists or a literature review. Produce a **reproducible computational demonstration**, an evidence-based assessment of prior art, and a specific recommendation for the first physical experiment.

The eventual scientific goal is **engineering neuronal membrane properties to improve their usefulness for biological computation**—for example, controllable excitability, response kinetics, reliability, or operating speed. The near-term milestone is **not** to demonstrate a better neuron: it is to validate a cheap functional membrane-protein design loop that could plausibly transfer to neuronal work later.

C5R also benchmarks frontier AI agents. The same small assay should ideally evaluate our integrated design stack alongside general-purpose frontier-agent designs **without multiplying their wet-lab workload**. A model leaderboard is a secondary benefit; engineering function is primary.

## 2. Non-negotiable constraints

1. **Treat Mentat's MEA, FPGA/controller, and electrophysiology system as unavailable for at least 30 days.** No dependency on that hardware in the initial experiment.
2. **No neuronal or mammalian culture in Phase 0.** Neuronal validation is a future continuation, not a promise for the first month.
3. **Cash cost to Mentat should ideally be $0.** For a non-customer collaboration, C5R has explicitly said it currently has very little bandwidth unless the work is low effort to get running. Assume they will not develop a new assay or fund special equipment merely because it is scientifically interesting.
4. **Our agent/computational work absorbs complexity.** Supply evidence, candidate selection, source sequences, assay requirements, controls, analysis code, and an agent-comparison format. C5R's role should be limited to a pre-existing or nearly turnkey bacterial workflow and returning measured data.
5. **One small physical batch**, ideally WT + established controls + ~4–8 genuinely informative designs, with reasonable replicates. Do not confuse “one plate” with “low labor”: cloning, verification, expression, challenge/illumination, and data QC all count.
6. **Real channel function is required.** Do not score mere protein expression, fluorescence, spectral shift, or bacterial fitness as proof of changed ion-channel function without validated linkage and controls.
7. **No invented capability.** Distinguish (a) publicly documented equipment, (b) what Tom confirmed verbally (small bacterial and mammalian labs, currently serving a customer), and (c) everything C5R must still verify. A published lab assay is not automatically turnkey at C5R.
8. **Keep the eventual neuronal utility explicit.** An easy bacterial result that cannot plausibly inform a useful neuronal membrane phenotype is strategically weak even if it is good PR.
9. **Default to existing open-source models, cheap inference, and public data.** Do not train a foundation model or build an elaborate VS Code extension before showing a simple retrospective predictive signal.
10. **Preserve uncertainty and negative findings.** A well-supported “neither is suitable right now” is a successful outcome.

## 3. Candidate hypotheses (to test, not assume)

### A. *E. coli* MscL: easiest possible experiment?

- Protein: mechanosensitive channel of large conductance (MscL).
- Intended design variable: functional gating propensity, not simply expression or bacterial survival.
- Published **fluorescence-based assay** distinguishes gain- versus loss-of-function MscL phenotypes by measuring bacterial survival following osmotic downshock. This is **an indirect functional proxy** and needs the right strain/background and controls.
- Advantages: native bacterial channel; relatively small; extensive mutational literature; likely inexpensive endpoint; no optical actuator necessary.
- Dangers: osmotic-survival phenotype can be affected by growth, host background, other mechanosensitive channels, and membrane health; predictable shifts in quantitative gating threshold may not be inferable from available data; **MscL is not an obvious neuronal engineering component**, and introducing pore leakiness could be harmful.
- Novelty risk: mutational screening and gating engineering are old. Newness, if any, lies in demonstrably **rapid, low-data, model-assisted functional engineering**, not in making MscL mutants.

**Agent must test:** Can available mutation labels and computational scores separate known GOF, WT-like, and LOF variants **on held-out evidence**, and is the resulting bacterial assay truly easy for C5R to run?

### B. GtACR2 / ACR2: strongest bridge to neural actuation?

- Protein: anion-conducting channelrhodopsin-2 from *Guillardia theta* (confirm exact protein accession, nomenclature, and construct). **Do not conflate it with cation channelrhodopsin-2 (CrChR2).**
- Intended design variables: ion-transport functionality, kinetic behavior, light sensitivity, or other trait that might carry into a neuronal phenotype.
- Strong starting point: peer-reviewed work expressed GtACR2/ACR2 and mutants in *E. coli*, measured light-driven anion transport, and found mutations with substantially changed transport phenotypes.
- **Critical caveat:** That bacterial study uses a **light-driven extracellular pH change** as an indirect transport measurement, not an established simple fluorescent well assay. Assess whether a genuinely low-touch **plate-reader-compatible functional assay** exists, rather than silently substituting fluorescence, absorption spectrum, or protein yield for transport.
- Advantages: same channel family already useful as a neuronal optogenetic actuator/inhibitor; direct biological continuity if neuron work becomes affordable.
- Dangers: needs light delivery and retinal-dependent functional expression; ion transport might require pH/ion-specific readout and tricky controls; spectral/photochemical effects can confound measured fluorescence; trafficking and cellular chloride reversal potentials can make bacteria-to-neuron translation misleading. Existing soma-targeted GtACR2 work already addresses neuronal trafficking/axonal excitation.
- **Strategic caveat:** A light-gated anion channel is chiefly a silencing tool; it does **not** automatically improve intrinsic computation, maximum neuronal firing rate, or electrical-stimulation response. State precisely what neuronal benefit would eventually be hypothesized and what additional optical hardware/control it would require.

**Agent must test:** Is there a genuinely inexpensive **functional ion-transport assay** for this exact channel that C5R could execute with its existing equipment? Can we computationally rank mutations on that phenotype, rather than on expression/stability alone?

### C. Closely related microbial rhodopsin: allowed fallback, with honesty

If GtACR2 is impractical, consider **one** microbial rhodopsin with a better established bacterial functional assay and useful transfer path to neural engineering. Explicitly distinguish **ion pumps from ion channels**. Do not select a proton pump merely because it gives a flashy optical/spectral readout and then claim to have engineered channel gating or improved neurons.

Examples of alternate phenotype classes: transport under illumination, wavelength response, desensitization. A wavelength shift alone is a protein-property demonstration, **not evidence of improved neuronal computation**.

## 4. Required research: prior art and real novelty

Search primary literature, supplements, repositories, patent/industry signals when relevant, and public datasets **through October 2026**. Record source URLs/DOIs, publication dates, and exact supported claims. Cover:

- MscL: prior saturation/random mutagenesis, high-throughput functional screens, known GOF/LOF mutations, training-ready sequence–phenotype data, structure/gating modeling, and newer ML protein design.
- GtACR2 and other anion channelrhodopsins: bacterial expression and ion-transport assays; function-changing mutants; neuronal silencing, membrane trafficking and targeting, kinetics, and improvements already achieved.
- ML-engineered channelrhodopsins (notably ChRger); other engineered opsins; which functional targets and neuron-level outcomes have already been achieved.
- Rhobot-Screen (2026): exactly what is automated and **what was actually measured**. In its main bacterial demonstration the endpoint is **absorption maximum/color tuning of Gloeobacter rhodopsin**, not proof of AI-designed improvement in GtACR2 ion conductance.
- Whether anyone already demonstrated a closed design–build–test–learn loop for the **same protein family, phenotype, and readout**; differentiate autonomous protein engineering in general from this precise target.
- Existing sequence–phenotype resources, including raw/supplementary tables; whether measurements across papers are comparable; construct differences and mutation-numbering traps.

**Judge novelty separately at four levels:**

| Level | Question |
|---|---|
| Protein variant | Is the proposed functional change or residue already well studied? |
| Predictive method | Is our off-the-shelf/model ensemble merely reapplying established methods? |
| Experimental engineering loop | Does this actually offer a new speed/cost/reproducibility demonstration? |
| Mentat strategic capability | Does it advance a credible route to engineered neural-computing wetware, beyond generic optogenetics? |

Do **not** treat “no paper found” as proof of novelty. Report confidence and search limitations. Make no IP or patentability claims without appropriate qualification.

## 5. Required research: feasibility at C5R

For each target, find the **best evidenced** bacterial readout and fill this matrix. Mark anything unverified as *unknown*.

| Field | Questions |
|---|---|
| Directness | Does readout measure channel transport/gating, or merely growth, viability, localization, spectral response? |
| Link to neuron phenotype | Does shifting this readout plausibly transfer to neurons? In what direction and under what conditions? |
| Host/construct | Is the exact construct publicly available? Does it need specialized host strains/plasmids? |
| Physical requirements | Plate reader mode, illumination/excitation, temperature control, shaker, optics, sensors, sterile handling, construct confirmation? |
| Consumables | Reagent classes, dyes, retinal, DNA construction/verification, plates, controls; realistic incremental cost ranges and sources |
| Labor and turnaround | Human operations, incubation/outsourcing/waiting times, assay commissioning burden, repeatability |
| Controls/confounds | WT, known GOF/LOF, no-channel, no-light, no-chromophore, host viability, expression/abundance, non-specific fluorescence effects, as relevant |
| Data | Raw numerical export, units, dynamic range, biological replicates, variance and power limitations |
| C5R fit | **Can their existing bacterial lab/plate reader actually do this?** What must we ask Tom? |

**Hard gate:** If the nearest published assay requires nontrivial apparatus, labor, or a new development effort, classify it **not turnkey**. Propose a less burdensome fallback. Avoid treating a 96-well format in a paper as proof that C5R can run it cheaply.

## 6. Computational proof of concept (mandatory)

Produce **working local code** where feasible, not just a plan. Time-box the prototype; a humble validated baseline is more valuable than a sophisticated unvalidated pipeline.

1. **Retrieve and provenance-check** exact WT protein sequences, relevant structures (experimental preferred), numbering conventions, and known labeled variants. Save accession IDs and links. Prefer curated UniProt/PDB entries and supplementary experimental datasets.
2. Build a clean table of **observed mutation → measured phenotype**, with study, host, construct, assay, units, expression controls, and confidence. Separate **activity** from **protein abundance**, and binary classifications from quantitative measurements.
3. Establish simple baselines first: known residue/structure/conservation heuristics; published mutation rules; and a random/naive baseline. Do not count known published variants as novel computational predictions.
4. Run one manageable pre-trained protein language model (e.g., ESM-2 small/medium or ESM-1v if feasible) to score variants. Optionally add an MSA score or structure-aware model if the costs and quality justify it. **PLM likelihood usually measures sequence plausibility, not the sign/magnitude of a desired gating or transport change.** Do not relabel a plausibility score as predicted channel function.
5. **Retrospective validation:** withhold a meaningful subset of published mutation–phenotype examples by **source paper, residue, or sequence cluster when feasible**, to limit memorization and leakage. Evaluate directional classification, rank correlation, and top-k enrichment against baselines. Include uncertainty or report when sample sizes make validation meaningless. Random train/test splits of closely related variants are insufficient evidence of generalization.
6. Check runtime, CPU/GPU/memory requirements, dependencies, API fees, model licenses, and how comfortably the solution fits a VS Code + agent workflow. Favor CLI/Python scripts with documented invocation and machine-readable outputs over UI work.
7. If the signal is promising, generate a **research-only shortlist** of a few candidate variant hypotheses plus WT/known controls. Record rationale, likely mechanism, novelty of each mutation, construct numbering, model disagreement, and low-confidence risks. **Do not call these designs validated improvements.**
8. Define how a general-purpose frontier agent would receive an **identical task brief**, with a bounded number of candidates, no access to withheld evaluation labels, and a common scoring rule. This is a future optional comparison; do not spend C5R labor on model-specific protocols.

If full local inference is impractical, produce a reproducible stub + honest resource estimate and complete the literature/data/assay evaluation. Never invent model scores, dataset accuracy, or successful runs.

### Useful metrics (only where appropriate)

- **Prediction:** sign accuracy / balanced accuracy for known GOF vs LOF, Spearman correlation for continuous phenotypes, baseline-adjusted top-k enrichment, confidence intervals; report sample count and leakage risk.
- **Experimental promise:** expected dynamic range and assay variance, replication feasibility, independent functional control, time from sequence to measurement.
- **Project economics:** marginal consumables, hands-on labor, **new equipment requirement**, turnaround including DNA acquisition, repeatability, and what C5R already owns.
- **Downstream utility:** whether an actually superior variant could be transferred to neurons, with what additional gene delivery, optical control, or electrophysiology dependencies.

## 7. Decision framework and stopping rules

First apply these **gates**, before ranking by scientific excitement:

- **G1 — Real functional assay:** Literature supports a measurable ion-channel/ion-transport phenotype in bacteria, with controls.
- **G2 — Low lab burden:** C5R could plausibly run it as one small standardized experiment with existing capabilities. Unknowns are clearly itemized; no quiet assumption of a new platform.
- **G3 — Computational signal:** Some evidence the proposed stack can discriminate functional variants better than a trivial prior-art heuristic, **or** a rigorously specified experiment can test this uncertainty cheaply.
- **G4 — Neural relevance:** Outcome has a credible, specific path to an improved neuronal behavior, not just a prettier protein.
- **G5 — Financing/time:** No dependency on Mentat hardware, minimal Mentat cash and hands-on wet-lab time, no customer-like experimental commitment imposed on C5R.

Then rank passing candidates on **novelty, neuronal usefulness, assay simplicity, probability of C5R saying yes, computational tractability, publicity/story value, and repeatability**. Provide a sensitivity analysis: how does the winner change if C5R lacks illumination hardware or will not do construct generation?

**Stop / pivot conditions:**

- If GtACR2 has no workable functional assay compatible with existing C5R equipment, **do not** rescue it by substituting absorption/spectral data while still claiming transport engineering.
- If MscL's phenotype is easy but neural relevance is too weak for Mentat, classify it as a **workflow/agent demo**, not a wetware-computing proof point.
- If neither provides meaningful predictive validation, report that and suggest the smallest next computational experiment or a justified alternative scaffold.
- If zero-cash work would require substantial unpaid new assay development from C5R, label the collaboration **unlikely in its current form**.

## 8. Deliverables and file layout

Create a compact repository or folder with at least:

```text
membrane-protein-viability/
  README.md                  # one-command reproduction and current status
  reports/
    decision.md              # 1–2 pages: recommendation, runner-up, hard blockers
    prior_art.md             # sourced novelty analysis, with dates and claim scope
    assay_feasibility.md     # reality check for C5R including labor/consumables
    computational_results.md# actual runs, baselines, uncertainties, failure modes
    questions_for_c5r.md    # at most 5 concrete yes/no/capability questions for Tom
  data/
    sources.csv              # DOI/URL, date, claim, evidence type
    proteins.fasta           # verified accession IDs and source references
    variants.csv             # evidence-backed phenotypes, no invented measurements
    assay_matrix.csv         # side-by-side comparison
    candidate_hypotheses.csv# optional, only if justified
  src/                       # reproducible fetching/scoring/evaluation scripts
  requirements.txt           # pinned or documented versions
```

`decision.md` must start with **GO / CONDITIONAL GO / NO-GO** for **GtACR2**, **MscL**, and any selected fallback. It must identify exactly **one proposed first experiment** (or explicitly recommend no experiment), with a high-level workflow, ≤8 new variants, controls, evidence that the proposed readout measures function, estimated incremental cost/labor, and an explicit list of items needing C5R confirmation.

Conclude with:

1. **The simplest credible experiment** C5R could do, without our hardware or neurons.
2. **The lowest-effort agent-comparison design** that shares the same wet-lab batch.
3. **What success would and would not establish** for actual neuron improvement, novelty, and fundraising.
4. **One short paragraph / 3-sentence feasibility summary** suitable to send Tom *after* technical review; do not write a long promotional pitch.
5. A recommended **next step that costs $0 and requires no C5R time**, if the evidence is insufficient.

**Quality bar:** A scientifically skeptical collaborator should be able to verify every key claim from a source, reproduce any computational numbers, and immediately spot the expensive or uncertain wet-lab step. This should be usable for a real go/no-go decision, not a polished proposal that assumes the answer is yes.

## 9. Seed references (starting points, not the complete search)

1. **Maurer & Dougherty (2001)**, *A high-throughput screen for MscL channel activity and mutational phenotyping*. Fluorescent viability after osmotic challenge; indirect phenotype. DOI: [10.1016/S0005-2736(01)00390-X](https://doi.org/10.1016/S0005-2736(01)00390-X).
2. **Maurer & Dougherty (2003)**, *Generation and evaluation of a large mutational library from E. coli MscL*. Mutational gating/fitness prior art. [PubMed](https://pubmed.ncbi.nlm.nih.gov/12670944/).
3. **Kojima et al. (2018)**, *Mutational analysis of the conserved carboxylates of anion channelrhodopsin-2 (ACR2) expressed in Escherichia coli and their roles in anion transport*. Direct precedent for GtACR2 bacterial functional study; assay follows extracellular pH response under illumination. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/).
4. **Mahn et al. (2018)**, *High-efficiency optogenetic silencing with soma-targeted anion-conducting channelrhodopsins*. Neuronal trafficking and axonal excitation caveats. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6175909/).
5. **Bedbrook et al. (2019)**, *Machine learning-guided channelrhodopsin engineering enables minimally invasive optogenetics*. Strong prior art for model-guided improved opsins with neuron validation. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6858556/).
6. **Nagata et al. (2026)**, *Rhobot-Screen: an integrated robotic platform for functional screening of rhodopsin variants*. Automated rhodopsin mutagenesis and 96-well screening; bacterial demonstration primarily spectral λmax, not GtACR2 ion flux. [Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13445694/).
7. **Meta ESM repositories**: [ESM project](https://github.com/facebookresearch/esm), [zero-shot variant prediction examples](https://github.com/facebookresearch/esm/tree/main/examples/variant-prediction). Check maintenance, compatibility, licenses, and availability of lighter checkpoints; this original repository is archived.

## 10. Work order

**Pass 1 — evidence and gates:** Resolve scaffold identity, prior-art collisions, assays, available datasets, and C5R's likely setup work. Produce a provisional comparison before investing in model infrastructure.

**Pass 2 — smallest runnable computation:** Obtain verified sequences/phenotypes; run simple baselines and one accessible PLM; validate against held-out measurements if enough data exist. Record exactly what ran and what did not.

**Pass 3 — decision and handoff:** Update recommendation based on the actual results, identify the smallest candidate panel only if defensible, and produce the five or fewer questions needed to let C5R accept or decline with almost no research on their end.

Do not wait for additional instructions where a reasonable assumption can be labeled and tested. Prioritize **decision quality and force multiplication** over framework building.
