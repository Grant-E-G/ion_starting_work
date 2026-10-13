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
