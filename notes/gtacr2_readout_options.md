# GtACR2 readouts: precedents, catalog products and assay-development gaps

Reviewed October 12, 2026. Scope: a small funding-stage functional membrane-protein engineering POC with a force-multiplier lab partner. Patch clamp is not an entry requirement. No assays were run, products ordered, vendors contacted or local instrument capabilities assumed.

Pricing/capability follow-up: [C5R equipment audit and per-option costs](c5r_gtacr2_pricing.md) identifies the publicly documented CLARIOstar Plus and prices compatible options without waiting for inventory questions. It supersedes this review's unresolved reader identity and older price anchors where newer US/supplier listings were found.

## Decision

**There are credible non-patch-clamp paths worth testing before rejecting GtACR2.** The strongest exact-target bacterial precedent is extracellular pH recording. The most promising automation adaptations are fluorescent extracellular pH and endpoint iodide measurement. Red membrane-potential fluorescence is a useful competing/supporting path. These differ substantially in evidence maturity.

My earlier framing was too narrow: lack of a verified turnkey GtACR2 plate assay does not mean the readout choices are exhausted. It means we should perform a bounded assay-transfer test using available components and established controls, rather than escalate to specialist validation.

Catalog availability means that the reagent or instrument is listed; it does not establish stock, local compatibility, a working GtACR2 assay or a delivered price. A “chloride-channel kit” may measure **iodide**, and a general chloride kit may only measure bulk chloride concentration. Read the actual protocol.

## Comparison

Evidence categories: **exact** = demonstrated using GtACR2 in the specified setting; **adjacent** = demonstrated using another channel, organism or related assay; **vendor** = catalog/protocol capability, not independent GtACR2 validation. Burden ratings are our qualitative estimates for an existing routine bacterial lab.

| Readout | What has been done | Off-the-shelf components | Main transfer issue | Assessment |
|---|---|---|---|---|
| 1. Extracellular pH electrode | **Exact:** GtACR2 in E. coli; light-dependent pH response used as transport proxy [R1] | Logging pH meter/probe, blue light, optical calibration | Washes, dense suspensions, trace stability; low throughput | Best biological reference; feasible if compatible apparatus exists |
| 2. Free extracellular fluorescent pH dye | **Adjacent:** optical pH monitoring in bacterial plates [R2]; HPTS is a commercial membrane-impermeant reporter [R3] | HPTS/pyranine; alternatively free-acid carboxy-SNARF-1; ordinary compatible fluorescence reader | Convert exact GtACR2 pH signal into fluorescence; scattering, buffering, actuation/readout interaction | **Priority plate-transfer candidate** |
| 3. Immobilized optical pH sensor plate | **Vendor:** routine culture pH measurement [R4] | PreSens HydroPlate HP96U; bottom-reading fluorescence | Sensor response and resolution may miss small/fast transport signals | More packaged hardware; assess endpoint sensitivity first |
| 4. Endpoint iodide uptake/efflux | **Vendor:** chloride-channel screening kit [R5]; GtACR anion-permeability precedent supports iodide [R6] | AAT Screen Quest Colorimetric Chloride Channel kit; absorbance reader | Bacterial loading/washing/retention and reagent matrix; uptake must be light/channel dependent | **Priority endpoint candidate**; GtACR2 adaptation unverified |
| 5. MQAE chloride fluorescence | **Adjacent:** live-cell chloride dye and optical opsin transport example [R7, R8] | Dojindo MQAE M024; UV-capable reader or microscope | Bacterial loading, leakage, single-intensity artifacts, spectral separation | Promising if UV optics already exist; more loading work |
| 6. Halide-sensitive YFP quenching | **Adjacent:** functional CFTR screen [R9] | Addgene EYFP H148Q/I152L #25872 [R10]; matching host expression vector | Extra reporter construction; pH effects, reporter excitation, iodide context | Good reusable platform, larger first-pilot setup |
| 7. Ratiometric chloride/pH reporter | **Adjacent:** ClopHensorN separates chloride/pH dynamics [R11] | ClopHensor #25938 [R12]; multi-channel fluorescence | Coexpression, calibration, spectral cross-talk, host context | Better confound resolution; medium/high setup |
| 8. Red membrane-potential dye | **Adjacent:** bacterial E. coli DiSC3(5) measurement [R13] | DiSC3(5) AAT #22076 [R14]; red fluorescence reader | Dye loading/redistribution, respiration, viability and driving force | **Useful supporting or competing screen**; not chloride-specific |
| 9. Packaged bacterial/mammalian voltage kits | **Vendor:** BacLight DiOC2(3), FLIPR voltage kits [R15, R16] | Commercial kits; flow cytometry or kinetic reader as specified | Bacterial kit is flow-oriented; mammalian kit not automatically valid in bacteria | Packaged reagents exist; inspect limitations before selection |
| 10. GtACR2 + genetically encoded voltage imaging | **Exact:** ORCHID measures GtACR2-driven voltage shifts in neurons [R17] | Published constructs/method; voltage reporter plus labeling dye and imaging | Specialized optical acquisition; cellular context and calibration | Genuine non-patch readout precedent, outside minimal partner scope |
| 11. Purified protein/liposome fluorescence | **Adjacent:** GtACR1 flux-associated pyranine signal in vesicles [R18] | Lipids, dyes and reconstitution reagents sold separately | Purification, orientation, reconstitution and leakage QC | Scientifically strong but poor initial partner fit |

The editable inventory is [gtacr2_readout_options.csv](../sources/gtacr2_readout_options.csv). Exact GtACR2 validation of the proposed plate adaptations was not located in this targeted search; this is a search limitation, not proof none exists.

Shareable comparison: [one-page readout PDF](../latex/render/gtacr2_readouts_partner_brief.pdf), generated from [LaTeX source](../latex/gtacr2_readouts_partner_brief.tex). From the repository root, build with `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=latex/render latex/gtacr2_readouts_partner_brief.tex` after creating the render directory. The PDF follows the repository's ignored-render convention; its source is retained.

## The four most useful practical branches

### A. Fluorescent extracellular pH: preserve the existing biological assay

GtACR2 already has a bacterial pH-based functional precedent. Change the detector first, rather than changing both host and biology. HPTS is water-soluble and membrane-impermeant; the vendor describes an excitation ratio around 450/405 nm. Free-acid carboxy-SNARF-1 provides an alternative near-neutral pH reporter with red-shifted emissions [R3]. Use the extracellular form, not an AM-loaded intracellular dye as if it measured the same compartment.

Our proposed adaptation is a plate measurement of the light-dependent pH signal, calibrated in the actual cell/salt/dye matrix. A bacterial culture pH assay is precedent for handling the measurement, **not** proof it detects GtACR2 transport [R2]. Dense cells can scatter light and attenuate both illumination and fluorescence. Dye buffering and matrix-dependent response may change the signal.

HPTS measurement light can activate GtACR2. Either make illumination part of a defined assay exposure or test separated actuation/readout timing; do not assume the measurement is passive. SNARF's shifted detection may help spectral separation, but its exact excitation and any residual GtACR2 activation still need checking. A blank containing dye and cells without GtACR2 tests direct optical/thermal artifacts.

**Why prioritize it:** no second genetically encoded sensor, no intracellular dye loading and a direct connection to the best-supported bacterial phenotype. It is an assay-transfer experiment, not already a validated kit. Successful output would be a reproducible transport-associated pH response with appropriate channel/light/abundance controls.

### B. Iodide endpoint colorimetry: separate stimulation from detection

AAT's Screen Quest kit is a real catalog product, with 96/384-well formats. Its chemistry measures iodide. Its manufacturer protocol includes loading, washing and measurement of efflux medium or uptake after lysis, with absorbance at 630, 380 or 405 nm [R5]. GtACR permeability measurements support iodide as a transported anion [R6]. Thus the concept has both an existing detector and a biologically relevant surrogate, rather than being a speculative chloride dye substitution.

Our proposal is a controlled light-dependent iodide uptake/efflux endpoint, read after stimulation. This avoids needing simultaneous fluorescence and actuation. It does **not** establish chloride-specific improvement if the mutation changes ion selectivity. Report improvement in light-dependent iodide transport under the chosen conditions.

The kit protocol is written for cultured-cell handling, not validated E. coli work. Loading/retention, background carryover, bacterial lysis and sample compatibility must be proven. Three washes can lose ions or introduce noise; dead/leaky cells can produce an apparent transport result. Efflux may avoid lysis detection but still requires successful preloading and clean extracellular background. Vendor detector sensitivity is not whole-cell assay sensitivity.

**Why prioritize it:** a normal absorbance reader and external blue illumination could suffice once biological transfer works. Start with matrix standards/recovery and WT versus empty-vector dark/light tests. Do not purchase a large kit or order variants on the assumption that the catalog protocol already transfers.

### C. Red membrane-potential fluorescence: an orthogonal phenotype

DiSC3(5) has bacterial measurement precedent, including E. coli, and red fluorescence is more separated from blue GtACR2 stimulation [R13, R14]. It can report whether activation changes membrane polarization. We should not assume depolarization: the response depends on the chloride gradient, initial voltage and host physiology.

Our interpretation would be a channel-dependent light-induced membrane-potential phenotype. Changes can also arise from cell damage, respiration, dye redistribution or efflux. Include viability/membrane-integrity controls and an independent depolarization reference. Do not import the pH assay's CCCP condition wholesale: a protonophore used there to facilitate a transport-associated pH signal can collapse the voltage signal here.

**Why include it:** it can support a pH/iodide result with a different detector, or become a screen if a reproducible discriminatory signal emerges. Dye kinetics do not measure millisecond channel gating, and an eventual steady-state voltage plateau may not rank channel conductance.

### D. MQAE: direct chloride-sensitive fluorescence if the reader supports UV

Dojindo sells MQAE, with excitation/emission about 355/460 nm and fluorescence quenched by chloride [R7]. There is optical MQAE precedent for the light-driven chloride **pump** Jaws in mammalian cells [R8]. That supports optogenetic chloride readout feasibility but is not GtACR2 bacterial validation. Jaws is a pump; it must not be relabeled a channel because the article's wording is loose.

MQAE needs suitable optics, successful dye loading/retention and normalization for dye amount and cell matrix. Manufacturer membrane-permeability statements do not prove loading across the E. coli envelope. UV reading, blue emission and actuation require background/sequencing checks. Single-intensity quenching can confound concentration and transport, making a within-preparation change more defensible than uncalibrated between-well fluorescence.

**When to prioritize it:** if UV optics and routine live-cell dye work are already available. Otherwise pH or endpoint iodide is a simpler first interface to investigate.

## Other routes: available, but not automatically simpler

**HydroPlate:** PreSens lists a ready-made pH plate read from below at approximately 485/540 and 485/620 nm. Specifications include response time t90 below 30 seconds, resolution around 0.05 pH at pH 7 and ionic-strength dependence [R4]. This cannot simply replace the published first-10-second GtACR2 slope. It may measure a slower endpoint if the actual signal is large enough. Reading at 485 nm can also activate GtACR2. Verify bottom-read capability; top-reading an ordinary plate is not equivalent.

**YFP/ClopHensor:** engineered halide reporters have strong functional screening precedents. Catalog plasmids are mammalian constructs; bacterial propagation does not make them bacterial expression constructs. They require sensor/target coexpression, appropriate host/vector design and calibration. YFP quenching can be driven by iodide and pH, while ClopHensor adds channels to distinguish pH effects [R9–R12]. These make sense as a reusable second-generation screening platform if chemical detector transfer is unsuccessful or repeated campaigns justify setup.

**BacLight/FLIPR:** BacLight B34950 is sold for bacterial membrane potential by flow cytometry. Its manual specifically warns that the E. coli response is not proportional to proton-gradient intensity [R15]. It is not a ready quantitative plate assay. FLIPR kits are sold for membrane-potential screens with an established mammalian-cell workflow [R16]; they do not imply a required purchase of the FLIPR instrument or prove bacterial compatibility. “Red” is a kit formulation name: read the spectral settings rather than assuming far-red optics.

**ORCHID:** Selfe et al. (2024) combined GtACR2 with Voltron2-ST/JF608 and interleaved actuation with voltage imaging in neurons [R17]. This establishes an exact-target all-optical readout. It was calibrated using electrophysiology, but subsequent optical measurement is possible. It is neither a bacterial plate assay nor an off-the-shelf GtACR2 engineering kit, and voltage-shift magnitude is not an unambiguous conductance metric.

**Liposomes:** Li et al. (2016) demonstrated functional GtACR1 reconstituted in vesicles using pyranine; the protein was expressed/purified from Pichia [R18]. A GtACR2 paper later reports difficulty purifying photoactive GtACR2 from E. coli [R19]. Purchasing lipids and dye does not remove those preparation burdens. Defer this route for the present partner.

## What to buy, and what a catalog price actually tells us

| Component | Catalog | Verified price / status | Practical meaning |
|---|---|---|---|
| HPTS/pyranine | Thermo H348; Sigma H1529 | Catalog listing; price not verified | Free extracellular pH reporter; not a transport kit |
| Free-acid carboxy-SNARF-1 | Thermo C1270 | German storefront: €644.65 online / 1 mg when checked | Alternative pH chemistry; not a US quote |
| Optical pH plate | PreSens HP96U | Quote required | Packaged sensing, compatible bottom-reading fluorescence needed |
| Iodide endpoint kit | AAT 36350 / 36351 | 10 / 100 plate packs; public extracted page has no numerical price | Request small-pilot supply/price before budgeting; minimum purchase matters |
| MQAE | Dojindo M024-10 | **$206 / 50 mg** | Verified US reagent-price anchor; assay not included |
| DiSC3(5) | AAT 22076 | 25 mg listing; quote/checkout price unverified | Red voltage detector, not a GtACR2 kit |
| Halide-sensitive YFP | Addgene 25872 | **$94**; academic/nonprofit only | Mammalian reporter construct; industry access not assumed |
| ClopHensor | Addgene 25938 | **$94**; academic/nonprofit only | Reporter construct, extra expression/calibration work |
| BacLight voltage kit | Thermo B34950 | Spanish storefront: **€538 / kit** when checked | Flow-cytometry product; not a US or plate-assay quote |
| FLIPR potential reagents | Molecular Devices R6136 Red / R6137 evaluation, plus other pack sizes | Vendor lists small packs; numerical price not verified | Established voltage chemistry; host/instrument/optical fit needs checking |

Prices were observed October 12, 2026 and may change; taxes, shipping, stock and recipient restrictions are separate. These are purchase-price anchors, not total experiment budgets. Illumination, verification, culture, washes, abundance/viability controls and analysis still contribute effort. No vendor messages were sent.

## A bounded selection experiment we can supply

Do not develop all options at once. Choose based on the actual reader:

- **Absorbance only:** evaluate iodide colorimetry; retain electrode pH as the best biological reference if already available.
- **Compatible visible fluorescence:** evaluate extracellular pH first; consider red voltage as the second detector if red channels exist.
- **UV fluorescence available:** MQAE becomes a competitive candidate.
- **Bottom-reading fluorescence with matching channels:** sensor plates become an option after checking signal magnitude and response time.

Stage 1 can use chemical standards without engineered cells: calibrate pH or iodide response in representative matrix, check spike recovery/background and compare illuminated versus unilluminated detector blanks. This checks the detector; it does not validate channel function.

Stage 2 uses a bounded control batch: WT, empty vector and one or two established functional variants, with dark/light and relevant chromophore/viability/abundance checks. A published high/low pH mutant is not automatically a high/low iodide or voltage control. Verify its behavior rather than forcing an expected rank. Use independent preparations and record raw traces or sample-processing timestamps.

A suitable readout separates channel/light-dependent signal from background and damage, has reproducible within-assay ranking, and uses operations the partner can repeat. Choose nonsaturated exposure/gradient conditions: a passive channel can dissipate its driving force, making different variants converge at an endpoint. Bigger final pH or voltage shifts do not automatically mean higher conductance. The practical optimization target is assay-specific transport performance, not intrinsic millisecond gating.

Only after this gate passes should four to eight prospective designs be built. We supply the measurement specification, controls and analysis; the partner runs a small fixed workflow. Stop or switch detector if the control batch cannot discriminate reliably within the agreed commissioning effort. No patch-clamp escalation is required by this milestone.

## Evidence links

- **R1:** Kojima et al. (2018), [exact GtACR2 bacterial pH assay](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/). Methods/results checked.
- **R2:** [Bacterial plate pH/oxygen monitoring study](https://journals.asm.org/doi/10.1128/AEM.05838-11); [author manuscript](https://insa-toulouse.hal.science/hal-02129764v1/document). Indexed primary abstract/method statements checked; not GtACR2.
- **R3:** [Manufacturer pH-probe handbook](https://www.thermofisher.com/ca/en/home/references/molecular-probes-the-handbook/ph-indicators/probes-useful-at-near-neutral-ph.html); [SNARF C1270](https://www.thermofisher.com/order/catalog/product/de/de/C1270); [HPTS catalog](https://www.thermofisher.com/order/catalog/product/H348).
- **R4:** [HydroPlate HP96U specifications](https://www.presens.de/products/detail/hydroplate-hp96u).
- **R5:** [Screen Quest iodide kit](https://www.aatbio.com/products/screen-quest-colorimetric-chloride-channel-assay-kit); [manufacturer protocol](https://docs.aatbio.com/products/protocol-and-product-information-sheet-pis/protocol-for-screen-quest-colorimetric-chloride-channel-assay-kit-version-5ce4698184.pdf).
- **R6:** Govorunova et al. (2015), [natural GtACR anion permeability](https://pmc.ncbi.nlm.nih.gov/articles/PMC4764398/). Primary article/indexed results checked.
- **R7:** [Dojindo MQAE specifications and price](https://www.dojindo.com/products/M024/).
- **R8:** [Jaws/MQAE optical transport example, 2019](https://www.nature.com/articles/s41467-019-12374-4). Indexed primary results checked; pump, not GtACR2.
- **R9:** [Functional CFTR/YFP screen](https://pmc.ncbi.nlm.nih.gov/articles/PMC2667356/). Indexed primary methods/results checked.
- **R10:** [Halide-sensitive YFP #25872](https://www.addgene.org/25872/).
- **R11:** Raimondo et al. (2013), [ClopHensorN chloride/pH measurement](https://www.frontiersin.org/journals/cellular-neuroscience/articles/10.3389/fncel.2013.00202/full).
- **R12:** [ClopHensor #25938](https://www.addgene.org/25938/).
- **R13:** [E. coli membrane-potential dye precedent, 2020](https://www.nature.com/articles/s41467-020-16950-x). Indexed primary methods checked.
- **R14:** [DiSC3(5) manufacturer page](https://www.aatbio.com/products/disc3-5-3-3-dipropylthiadicarbocyanine-iodide).
- **R15:** [BacLight B34950 catalog](https://www.thermofisher.com/order/catalog/product/es/en/B34950); [manufacturer manual](https://documents.thermofisher.com/TFS-Assets/LSG/manuals/mp34950.pdf).
- **R16:** [FLIPR voltage reagents](https://www.moleculardevices.com/products/assay-kits/ion-channel/flipr-membrane-potential); [manual](https://www.moleculardevices.com/sites/default/files/en/assets/product-insert/reagents/flipr-membrane-potential-assay-kit-guide.pdf).
- **R17:** Selfe et al. (October 16, 2024), [ORCHID exact-target voltage imaging](https://www.nature.com/articles/s41467-024-53074-y). Methods/results checked.
- **R18:** Li et al. (2016), [functional GtACR1 liposome fluorescence](https://pmc.ncbi.nlm.nih.gov/articles/PMC5207235/). Methods/results checked; not GtACR2.
- **R19:** [Kojima group 2021 report of GtACR2 purification difficulty](https://www.nature.com/articles/s41598-021-94181-w). Primary indexed discussion checked.

This is a targeted assay/product review, not a systematic literature survey. Some publisher/PMC pages blocked full access; checked-content limits are specified. Supplementary assays, reagent lots and local compatibility remain unaudited. Recommendations and transfer tests are our proposals, not claimed published GtACR2 plate protocols.
