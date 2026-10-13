# GtACR2: decision, experimental options and budget

October 12, 2026. Primary-literature review and proposed study design. No model scores, new variants, laboratory results, collaborator commitments or supplier quotes are claimed.

## Partner-fit correction

The user clarified that the partner is a lab-automation AI startup and challenged light-controlled patch clamp as an impractical default. **The direct pilot remains a scientifically strong test, but is no longer the recommended default task for this partner.** It is an external-validation option only if an established provider can accept the scope. Do not ask the startup to acquire a rig, train operators, or commission optically enabled automated electrophysiology for this project.

For this partner, the decision is: perform the data/construct audit first; consider a bounded bacterial control-only pilot only if its existing apparatus supports the published readout; otherwise defer GtACR2 wet-lab work. DNA construction/expression could be a partner contribution, but does not by itself demonstrate functional optimization. A fluorescence or absorbance plate reader is not sufficient evidence of transport-assay readiness. The published bacterial pH workflow is also a commissioning risk, not an automatic automation-friendly fallback.

The earlier direct-pilot recommendation below is conditional on access to an experienced existing electrophysiology facility, not on the startup building that capability. Price tiers remain illustrative scopes rather than evidence of partner fit. For a split collaboration, quote startup construct work and external functional validation separately, including handoff/QC costs. **If low setup effort at the startup is a hard requirement and neither validated bacterial transport nor external functional validation is available, GtACR2 is a no-go for the immediate collaboration.** This is a practicality judgment; it does not negate scientific feasibility.

## The conclusion to communicate

**GtACR2 is a credible engineering target with established functional assays. The practical first proof of improved channel performance is light-controlled whole-cell electrophysiology in an existing mammalian-cell setup. Bacterial testing can establish a transport-associated phenotype at lower materials cost, but cannot establish better neuronal inhibition or faster channel closing.**

Recommend a staged GO: select a functional objective and assess data now; obtain a capped quote for a direct electrophysiology pilot before building variants. If only bacterial infrastructure is available, either run a bounded control-only transport pilot or seek an existing electrophysiology service. Do not commission a new fluorescent plate assay simply to make the project appear cheap.

This replaces the earlier blanket recommendation of no physical experiment with **a concrete conditional experiment**. Actual execution still depends on facility acceptance, construct access and agreement on scope. The scientific feasibility is established; local readiness and prediction success are not.

## What we are optimizing

GtACR2 is a light-gated anion channel. The proposed use is more precise optical inhibition of neuronal activity. It requires optical control; it does not by itself increase intrinsic neuronal firing speed or demonstrate improved biological computation. Native GtACR2, engineered soma-targeted GtACR2 (stGtACR2), and the bacterial truncated expression construct are different experimental objects.

**Recommended provisional objective:** faster cessation of inhibitory current after light-off, while preserving useful current at a fixed low light level. The alternative is lower light requirement for sustained inhibition while preserving acceptable recovery time. Select one before modeling; do not collapse both into an undefined “better channel.”

A proposal for the first objective is a 30% reduction in time to 10% residual photocurrent, with at least 80% of reference stationary current density retained at preselected light intensity and voltage. These are **project decision thresholds**, not published attainable improvements. Pilot variability determines sample size and whether these thresholds are sensible. Reconfirm apparent winners with fresh constructs/cultures before claiming success.

Three quantities must remain distinct:

- **Practical actuator performance:** current density and light requirement in the selected cellular context.
- **Channel kinetics:** light-off decay, activation, desensitization and recovery under specified voltage, temperature and pulse conditions.
- **Intrinsic conductance:** whole-cell current combines surface-channel number, conductance and open probability. Greater whole-cell current alone cannot identify which factor improved. Surface abundance controls help, but do not resolve every mechanism.

## The evidence that fixes the scope

| Evidence | What it establishes | Consequence |
|---|---|---|
| Kojima et al., 2017 [S1] | Bacterial functional expression; R84 substitutions change the light-induced pH transport-associated signal | Published substitutions are controls/heuristics, not novel predictions |
| Kojima et al., 2018 [S2] | GtACR2 core in E. coli; extracellular pH slope with CCCP and abundance normalization; established functional mutants | Bacterial assay is a controlled indirect transport proxy; not patch clamp |
| Mahn et al., 2018 [S3] | Soma targeting improves neuronal GtACR use and reduces axonal excitation | Later neuron tests should compare against stGtACR2, not only native WT |
| Sineshchekov et al., May 2026 [S4] | GtACR2 closing depends strongly on holding voltage; mutational/photochemical characterization | Specify voltage and pulse history; a single-condition result is narrow |
| Yokoyama et al., April 2026 [S5] | Functional GtACR1/2 chimeras, point mutants, HEK patch clamp and MD | There is recent direct engineering prior art; chimera numbering cannot be assumed to match WT |
| Bedbrook et al., 2019 [S6] | ML-guided channelrhodopsin improvement with functional and neuronal validation | “AI improves an opsin” is already established |

S4 was missing from the previous assessment. Its primary abstract is accessible; the full article/supplement was not audited here. S5 says datasets are available from the author on request, so a fully public training-ready dataset must not be assumed.

The potentially new contribution is **prospective prediction of a specified functional improvement beyond a frozen literature heuristic at a small experiment budget**. Exact variant novelty remains open until candidates exist and undergo a residue/construct/phenotype search. No patentability claim is made.

## Sliding scale: what money and effort buy

**All prices below are USD planning estimates, not quotes.** Materials-only prices assume donated staff time and access to the required equipment. Paid-project prices value preparation/analysis labor at an assumed $75/hour, electrophysiology at $150/hour, and add 25% contingency. No new laboratory, patch rig or automation platform is included. Each row is a standalone project scope, not the extra price after the preceding row. The ideal scope includes screening and follow-up; do not sum the rows.

| Level | Experiment / work | Materials only | Paid-project planning range | Human time and elapsed time* | Defensible output |
|---|---|---:|---:|---|---|
| 0 — define and audit | Exact construct/phenotype data audit; frozen baselines and evaluation plan | $0–300 | $0–300 cash if we do the work | 12–24 research hours; 2–5 working days | Model-ready specification or documented data gap; no new biology |
| 1 — bacterial readiness | WT + published high/low controls + empty vector; no new designs | $500–1,500 | $2,500–6,000 | 20–40 hours; 2–4 weeks | Whether this lab can reproduce the controlled transport proxy |
| 2 — bacterial design pilot | Level-1 controls + four future designs; independently prepared cultures | $1,500–3,500 | $6,000–12,000 | 40–80 hours; 3–6 weeks | New variants change an abundance-aware transport proxy; neuronal benefit unresolved |
| 3 — direct channel pilot | HEK cells: WT + two future designs + mock; approximately 24 usable recordings | $1,000–2,500 | $5,000–10,000 | 20–40 preparation hours + 8–16 recording hours; 3–6 weeks | Direct initial current/kinetic comparison; candidate signal, not definitive optimization |
| 4 — stronger channel POC | HEK cells: six future designs + WT + published comparator + mock; approximately 108 usable recordings including confirmation | $2,000–5,000 | $13,000–26,000 | 40–80 preparation hours + 36–64 recording hours; 6–10 weeks | Replicated channel-function claim in defined conditions; independent hit confirmation |
| 5 — ideal neural-relevance POC | Two design rounds, 12–24 total new designs, HEK screening/confirmation, then 2–3 finalists in neurons | $6,000–16,000 | $40,000–80,000 | 120–240 preparation hours + 120–200 recording hours; 12–24 weeks | Prospective design-loop evidence plus improved inhibition in a specified neuronal preparation |

*Time assumes established workflows and trained staff. Procurement permissions, core queues, construct failures, culture maturation and commissioning can extend it. These are not turnaround guarantees. Level 0's human effort is not monetized in the cash column; at the same labor assumption it would represent $900–1,800 before contingency.

**These are two branches, not a mandatory staircase.** If mammalian electrophysiology exists, jump from 0 to 3. Levels 1 and 2 are justified when bacterial capabilities already fit, when transport is the actual objective, or when their value exceeds commissioning costs. Level 3 can cost less than developing level 2 despite measuring function more directly.

### What is and is not priced

Verified public anchors, checked October 12, 2026:

- Addgene's actual #67877 page lists the mammalian GtACR2-EYFP plasmid at **$94**, and restricts it to academic/nonprofit recipients [P1]. Its generic help page still lists $89, so use the actual item/checkout price, not the older generic value. The stGtACR2 #105669 page also says unavailable to industry [P2]. Who orders matters. Check legitimate sourcing/terms early; do not assume another laboratory's eligibility transfers to a company.
- Twist lists fragments in the 0.5–1.8 kb range at **$0.07/base**; approximately 800 bases would be $56 before assembly, verification, shipping and sequence-specific fees. It also lists clonal-gene/vector options [P3]. This is a DNA anchor, not the cost of a validated functional expression construct.
- Georgia Tech lists **$150/hour external whole-cell patch clamp** [P4]. This does not establish availability, optogenetic compatibility, commercial eligibility, included culture work or a GtACR2 service quote.
- A vendor lists a basic pH benchtop meter at approximately **$420–545** [P5]. This only anchors the price of a meter: response time, logging cadence, probe geometry and performance in dense cell suspensions must meet the assay. It is not a validated equipment recommendation.

Example level-3 midpoint: $1,750 materials + 30 preparation/analysis hours × $75 + 12 recording hours × $150 = $5,800; with 25% contingency, **$7,250**. Do not count a technician twice if the recording rate already includes them. Local staff/facility quotations replace both assumed rates.

Materials allowances cover routine DNA verification, culture and assay supplies, basic expression/abundance controls and small procurement/shipping costs. They are allocations, not a purchase bill. Level 5 includes an allowance for neuron culture/delivery; custom viral production or premium human-neuron supplies may exceed it. Computational work/model API or GPU spending beyond the initial allowance is separate. The paid ranges use established academic/core-like economics; commercial fully managed services can exceed them.

For bacterial work missing only measurement/illumination components, reserve a **separate provisional $1,000–4,000 equipment allowance** and additional commissioning time; get a component-specific quote before approving it. This allowance is an estimate, not evidence the setup will work. If a new mammalian culture capability, new patch rig or training program is needed, the level-3 price no longer applies. Use a qualified existing facility and obtain a quote rather than treating equipment acquisition as a pilot consumable.

Editable inputs and exact calculations are in [the budget table](../sources/gtacr2_budget_scenarios.csv). Amounts from the formula are planning values with false precision removed in the communication ranges above.

## The smallest credible bacterial route

Purpose: decide whether the laboratory can measure a channel-associated transport phenotype reproducibly. This is readiness testing, not a novelty demonstration.

Use the published bacterial construct context: GtACR2 residues 1–266 associated with KP171709, a suitable bacterial expression backbone and abundance tag. Obtain/verify the actual coding sequence before ordering; neither a mammalian vector's bacterial propagation nor its antibiotic resistance means it expresses GtACR2 in E. coli. A mammalian tagged construct cannot silently substitute for the published bacterial one.

Proposed pilot panel: WT, E219Q as the published higher-signal control, E159Q as the published lower-signal control, and empty vector. The 2018 work used extracellular pH response with controlled light, CCCP conditions and western-blot abundance normalization [S2]. These substitutions are controls with source/numbering verification required, not engineering suggestions claimed as new.

The lab would prepare independently expressed cultures, verify chromophore-dependent expression, record light-on/off pH traces, measure abundance independently and check viability/background. Include dark/no-channel conditions, conditions with and without CCCP, and a chromophore-negative diagnostic control. Anion-dependence checks should follow the established assay context; the supervising laboratory selects compatible substitutions. Capture raw pH/time/light traces, sample density, temperature, expression measurements, culture IDs and failed preparations.

Suggested scope: three independent cultures per protein-bearing construct, with repeat traces treated as technical measurements rather than new biological replicates. Before designs, WT must separate from background and the established controls must behave consistently with their documented directions. A failed readiness test means the assay did not work locally; it does not prove GtACR2 cannot be engineered.

**Bound commissioning:** quote a fixed control-only attempt with a maximum number of repeat preparations. Do not promise free assay development. Keep manual trace recording if it works; a plate format is unnecessary for a four-design pilot. A fluorescent pH/chloride readout is an assay-development proposal until validated against the existing functional assay, including optical and pH cross-talk. It is not automatically the minimum.

If level 1 passes, level 2 adds four future predictions, randomized/blinded alongside the same controls, with predicted direction and primary scoring frozen in advance. A confirmed difference would support only the proxy-specific claim. Fresh-culture replication and direct electrophysiology would still be required for a stronger channel claim.

## The smallest direct channel route: recommended first design test

Use a laboratory already experienced in HEK culture and whole-cell patch clamp, with calibrated blue illumination under recording control. Purchase service time if that avoids commissioning. No neurons, MEA or FPGA are required for this stage. Choose a constitutive mammalian promoter and matched sequence/tag/backbone across WT and designs; neuron-specific or Cre-dependent catalog vectors are not automatically suitable for this assay.

1. **Freeze the brief.** WT plus two candidate variants selected later, and mock-transfected cells. Declare the objective, predicted direction, voltages, light conditions, analysis and failure rules before unblinding. If only WT is ready, commissioning can start with WT/mock before a variant order.
2. **Build and verify.** Supply the facility with confirmed plasmids, identities blinded where feasible, and enough preparation information to reproduce transfection. Keep tags, DNA dose, promoter and preparation comparable.
3. **Record function directly.** Collect light-evoked currents, peak/stationary current density, empirical light-off decay, light-dose response and repeated-pulse recovery. Use calibrated irradiance and specified wavelength/temperature; log pulse history. Check current–voltage behavior and chloride-dependent reversal for WT and putative hits. A nonresponsive mutant cannot be ranked as successfully fast-closing.
4. **Replicate across preparations.** Planning target: six usable cells per group, spread over at least three independent transfection days. At approximately two to three usable recordings per hour, 24 cells need roughly 8–12 recording hours; reserve up to 16. This throughput is an assumption for an experienced operator, not a published guarantee.
5. **Return auditable results.** Per-cell traces/metadata, seal/series-resistance and stability exclusions, day labels, abundance/localization checks, prespecified comparisons and uncertainty. Total fluorescence only locates expressing cells; it is not proof of functional improvement or surface abundance.

This pilot can identify a direct functional signal worth following. Six cells/group is not automatically powered to conclude a 30% improvement. If confidence intervals remain broad, the outcome is inconclusive and the next quote is based on observed variation. Cells within a transfection day are nested observations, not independent experiment days.

In level 4, expand to six designs and three comparator/control groups. One illustrative allocation is eight usable cells/group for screening (72 total), then 12 fresh cells each for WT and two hits (36 total), spread over independent preparations. This totals 108; adjust allocation and confirmatory sample size from the pilot rather than distributing every measurement uniformly. Allocate detailed voltage/light characterization to the best candidates. A published comparator must be relevant to the endpoint and same construct context; bacterial E219Q success is not assumed to transfer into HEK cells. Include a frozen heuristic-selected candidate within the design budget if comparing prediction approaches.

Optically enabled automated patch clamp is a plausible larger-panel alternative. Primary studies show channelrhodopsin measurements on that platform [S7]. An automated patch instrument without the correct illumination/analysis workflow does not establish local readiness. For two designs, commissioning automation can be worse value than manual recording; seek a quote only from a facility that already offers the required optical workflow.

## How we would do it ideally

**Ideal for a proof of concept means a rigorous prospective design loop plus neuronal validation, not purchasing a platform or starting an animal program.**

First, curate exact GtACR2 constructs and comparable sequence–phenotype data. Separate bacterial proxy labels from HEK currents and kinetics. Establish literature/structure rules, naive baselines and held-out evaluation. A pretrained sequence score is not automatically a directional kinetics predictor. If available labels cannot support generalization testing, call the first prospective batch a test of that uncertainty.

Second, run two bounded design rounds totaling roughly 12–24 new variants. Mix model-selected, heuristic-selected and exploration variants within a fixed budget, keeping predictions prospective. Use direct HEK electrophysiology with voltage/light dependence, surface-localization checks and sufficient independent preparations. Select candidates from a current–speed–light tradeoff rather than declaring a winner from one number. Keep a fixed independent validation set; a second round's retraining data must not double as its final test.

Third, rebuild/sequence-confirm the best two or three hits and repeat on fresh days, preferably blinded or with a second operator. Freeze the statistical comparisons and adjust for candidate selection/multiple comparisons. Choose confirmatory sample sizes from the pilot, including day-to-day variation. A negative result or uncertain gain is a valid stop point.

Fourth, transfer confirmed hits into the same neuronal targeting/trafficking context as the reference and test cultured neurons against stGtACR2. Measure inhibition probability versus light dose, release from inhibition after light-off, spontaneous/dark excitability, rebound and unintended excitation. Specify neuronal identity and maturation; test the native chloride context, using a chloride-preserving recording approach where necessary rather than concluding native inhibition from a dialyzed chloride gradient. Soma targeting and chloride-distribution concerns have direct precedent [S3, S8]. A fast-spike-inhibition objective also merits a relevant fast-actuator comparator, such as ZipACR, rather than only a weak native-WT reference [S9].

Fifth, only after improved inhibition is confirmed, assess a neural-computing task: for example temporal masking/reset precision at matched light budget, with matched cultures and baseline activity. A neuron inhibition result is a tool improvement; a task-level result is the evidence needed to claim a computing benefit. This fifth step is **outside the level-5 budget**, which ends at neuron-level validation. It needs its own hardware/task specification and quote. No in-vivo work is needed for the stated proof of concept.

## How to present it to the lab partner

Share [the one-page PDF](../latex/render/gtacr2_partner_brief.pdf), backed by this report and the editable CSV. Start with the scientific question, then select the existing-infrastructure branch and a bounded budget. Use three explicit outcome labels: assay works locally; direct functional candidate improves; neuron inhibition improves. Do not present these as the same result.

The PDF is generated from [its LaTeX source](../latex/gtacr2_partner_brief.tex). Build from the repository root with `mkdir -p latex/render`, then `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=latex/render latex/gtacr2_partner_brief.tex`. Rendered artifacts follow the repository convention and are ignored by git; the source is retained.

Suggested message:

> GtACR2 is an established engineering target, and we want to test one precise current/kinetics improvement prospectively. If you already have light-controlled patch clamp, the smallest direct pilot is WT plus two designs and mock, roughly $5k–10k with paid time, or $1k–2.5k in materials with in-kind staff/equipment. If your setup is bacterial only, a $500–1.5k materials control pilot can establish a transport proxy, but we would keep its claim limited and decide on electrophysiology separately.

This is a draft to review, not a sent message. Rather than asking the partner to design the entire study, request a quote on one specified scope, with construct preparation, usable recordings, optical calibration, raw data and one repeat/stop policy itemized.

Five decisions settle the next action:

1. Bacterial-only, existing HEK/optical patch clamp, or external optogenetic electrophysiology access?
2. Faster release from inhibition or lower light requirement for sustained inhibition?
3. Who supplies sequence-confirmed constructs, and can they legitimately obtain the desired reference materials?
4. What cash ceiling and in-kind hours can be committed to the first bounded pilot?
5. Which pilot results trigger stop, repeat or the next tier?

Without answers, the default recommendation is level 0 now and a **level-3 quote**, not an assumption of free wet-lab capability.

## Sources and verification limits

See [the evidence register](../sources/gtacr2_sources.csv) for dates, URLs, checked content and claim boundaries. Main scientific sources:

- **S1:** Kojima et al. (2017), *An inhibitory role of Arg-84 in anion channelrhodopsin-2 expressed in Escherichia coli*. [Primary abstract](https://pubmed.ncbi.nlm.nih.gov/28150799/).
- **S2:** Kojima et al. (2018), *Mutational analysis of the conserved carboxylates of ACR2 expressed in E. coli*. [Full article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/).
- **S3:** Mahn et al. (2018), *High-efficiency optogenetic silencing with soma-targeted anion-conducting channelrhodopsins*. [Publisher PDF](https://www.nature.com/articles/s41467-018-06511-8.pdf).
- **S4:** Sineshchekov et al. (May 15, 2026 online), *Blue- versus green-absorbing anion channelrhodopsins ... differ fundamentally in gating mechanisms*. [Primary abstract](https://pubmed.ncbi.nlm.nih.gov/42139291/). DOI: 10.1073/pnas.2519786123. Full text/supplement not audited.
- **S5:** Yokoyama et al. (April 10, 2026), *Val109 and Ile170 contribute to channel function in Guillardia theta-derived anion channelrhodopsins*. [Publisher](https://www.nature.com/articles/s41598-026-46487-w).
- **S6:** Bedbrook et al. (2019), *Machine learning-guided channelrhodopsin engineering enables minimally invasive optogenetics*. [Publisher](https://www.nature.com/articles/s41592-019-0583-8).
- **S7:** Govorunova et al. (2022), *Biophysical characterization of light-gated ion channels using planar automated patch clamp*. [Primary article](https://www.frontiersin.org/journals/molecular-neuroscience/articles/10.3389/fnmol.2022.976910/full).
- **S8:** Messier et al. (2018), *Targeting light-gated chloride channels to neuronal somatodendritic domain reduces their excitatory effect in the axon*. [Primary abstract](https://pubmed.ncbi.nlm.nih.gov/30091701/).
- **S9:** Govorunova et al. (2017), *The expanding family of natural anion channelrhodopsins ...*. [Publisher](https://www.nature.com/articles/srep43358).
- **P1:** [Addgene #67877: actual item, eligibility, price](https://www.addgene.org/67877/).
- **P2:** [Addgene #105669: targeting construct and eligibility](https://www.addgene.org/105669/).
- **P3:** [Twist gene synthesis: current public price schedule](https://www.twistbioscience.com/products/genes?tab=overview).
- **P4:** [Georgia Tech external patch-clamp service rate](https://research.gatech.edu/bio/research/core-facilities/neuroscience-core/service-fees).
- **P5:** [Hanna basic pH meter: price anchor only](https://hannainst.com/ph-orp-simple-benchtop-meter/).

The source evidence supports feasibility and prior-art scope; study designs, throughput, labor estimates, budgets and success thresholds are our proposed assumptions. Procurement carts, legal eligibility, local capacity and actual service quotes remain unchecked. Literature search is targeted, not exhaustive. Exact sequence files and all numerical datasets will be audited in the modeling phase. No prior agent's organizational claims are relied on.
