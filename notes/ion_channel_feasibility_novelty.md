# Ion-channel optimization: feasibility and novelty

Assessment: October 12, 2026. Literature assessment; no model inference or experimental validation.

Follow-up: the [GtACR2-specific decision and budget](gtacr2_decision_and_budget.md) develops concrete conditional experiments and supersedes this initial report's blanket recommendation of no physical experiment. It also adds May 2026 GtACR2 gating prior art. No laboratory commitment has been made.

**GtACR2: CONDITIONAL GO for computational investigation; NO-GO for an immediate low-effort wet-lab batch.**

**E. coli MscL: CONDITIONAL GO as a functional workflow benchmark; NO-GO as the current proof of neuronal optimization.**

**Fallback: none selected. First physical experiment: none recommended yet.** These decisions concern project readiness, not whether the proteins can be engineered.

## Scope and recommendation

The user's current request is feasibility and novelty, with modeling later. This supersedes the inherited handoff's demand for immediate inference and candidate designs. Keep that document for traceability, but treat its claims about Mentat, C5R, Tom, hardware, cash and commitments as unverified context. Nothing was sent to anyone.

Channel engineering is scientifically feasible; whether a cheap predictive process can deliver a useful functional change remains unresolved. Recommend GtACR2 as the strategic research track because it connects to neural inhibition. Retain MscL only if a bacterial workflow demonstration is independently valuable. Neither currently supports a wet-lab commitment.

## Feasibility

| Question | E. coli MscL | GtACR2 |
|---|---|---|
| Evidenced bacterial endpoint | Osmotic-challenge survival using fluorescent viability [1] | Light-induced extracellular pH response as an indirect transport readout [3] |
| Interpretation | Controlled functional phenotype; not quantitative gating tension | Controlled transport proxy; not single-channel conductance or neuronal kinetics |
| Main dependencies | Suitable host, verified constructs, compatible viability measurement | Functional expression, retinal, controlled illumination, time-resolved pH measurement, abundance controls |
| Relative commissioning burden | Lower, but not proven turnkey locally | Higher; plate-reader adaptation not validated here |
| Neural relevance | No defined neuronal benefit in this project | Plausible optical inhibition; targeting and chloride gradients matter [4] |
| Computational readiness | Mutational literature; comparable labels not yet curated | Small bacterial panel plus electrophysiology in other contexts |

MscL's 2001 screen modified the Live/Dead BacLight assay to distinguish established gain- and loss-of-function phenotypes [1]. The 2003 work already combined random mutagenesis and functional screening [2]. These establish precedent, not local assay readiness. Interpretation must separate baseline growth, channel abundance, host mechanosensitive channels and membrane damage. Channel abundance itself affects osmotic survival, as examined in the Phillips laboratory's research supplement [9]. An improved survival result alone is insufficient evidence for a specified gating-threshold change.

The 2018 GtACR2 study used residues 1–266 of accession KP171709, a His-tagged pET22b construct in BL21(DE3), retinal, liter-scale expression, washed dense cells, calibrated blue illumination, CCCP conditions and western-blot normalization. Its endpoint was the initial pH slope. E219Q enhancement and E159Q/D230N reductions are published observations, not proposed new designs [3]. **Inference:** reproducing or miniaturizing this workflow involves appreciable commissioning unless the laboratory already runs it. An LED substitution would require equivalence checks. A fluorescent plate-reader adaptation is not established by this paper.

A bacterial transport proxy cannot establish millisecond neuronal kinetics. Soma targeting already improves GtACR performance and addresses axonal excitation [4]; bacterial transport does not test those features. Later neuronal benefit requires a specified optical-inhibition objective and direct validation. Neither increased firing speed nor improved biological computation follows from greater bacterial transport.

## Novelty

| Level | Current assessment | Evidence needed |
|---|---|---|
| Protein variant | Unknown until sequence and phenotype are specified | Exact construct, numbering and comparison with published variants |
| Predictive method | Off-the-shelf scoring/agent orchestration alone offers little novelty | Generalization beyond frozen residue/structure heuristics |
| Engineering loop | Small-budget reproducibility may be useful; novelty unproven | Prospective gain per experiment, including failures and all labor |
| Neural computing | No demonstrated contribution yet | Better performance on a defined neuronal/network task against existing tools |

Bedbrook et al. (2019) trained Gaussian-process models on 102 functionally characterized channelrhodopsins and produced ChRger variants with improved photocurrent/light sensitivity and neuronal validation. This directly precedes the broad idea of ML-guided channelrhodopsin improvement. The paper links training data and code [5].

The neural comparator cannot be only WT GtACR2: ZipACR already supports fast selective spike inhibition [6], while Aion provides prolonged reversible silencing [7]. These serve different temporal objectives; faster is not universally better.

An additional collision missing from the handoff is Yokoyama et al. (April 10, 2026): GtACR1/GtACR2 chimeras, photocurrent/kinetic measurements in HEK cells, mutation analysis and molecular dynamics. Its V109/I170 results use defined chimeric backgrounds and numbering; do not automatically transfer them to WT GtACR2 [8].

Rhobot-Screen (August 6, 2026) integrates mutagenesis, cloning/expression and screening. Its bacterial demonstration measured Gloeobacter rhodopsin absorption maxima; the animal-rhodopsin extension measured GPCR signaling. Neither demonstrates improved GtACR2 ion conductance. Future adaptation to transport is not validation of that adaptation. Its custom robotic platform also does not establish inexpensive manual feasibility [10].

**Candidate contribution:** accurately predict a specified channel-function change with little target-specific data, outperform a frozen literature heuristic at equal candidate budget, and publish a reproducible prospective test with cost, effort and failures. This is a research hypothesis, not a confirmed novelty claim. One small batch can support a preliminary result, not general superiority of an agent or transfer across families.

## Decision sensitivity and economics

If a partner already runs a validated MscL assay, MscL becomes the preferred practical benchmark. If the host is unavailable or construct generation is out of scope, that advantage shrinks. Without controlled illumination and pH measurement, GtACR2 remains unsuitable for the proposed bacterial batch. If neural relevance is mandatory, ease alone does not justify MscL. No fallback has been shown here to satisfy both objectives.

Dollar costs, hands-on hours and turnaround are unknown. Budget host/construct acquisition, DNA construction and sequencing, assay consumables, abundance controls, equipment gaps, commissioning and repeat work separately. One plate is not a labor estimate; zero cash to one organization is not zero resource cost.

The smallest conditional physical step would reproduce the selected assay with WT, an established functional control and no-channel control, plus unchallenged/dark conditions as appropriate. It contains zero new designs and establishes assay readiness, not novelty. It is not a current laboratory commitment.

A later agent comparison should freeze identical phenotype, construct, allowed evidence and candidate budgets, deduplicate designs, and use one shared blinded batch. Few candidates per method make this a pilot, not a statistically persuasive leaderboard. Success would establish assay-specific design capability, not better neurons or biological computation.

## Five prepared capability questions

1. Do you already run an osmotic-survival channel assay, and in which host?
2. Do you already measure controlled light-induced pH responses in bacteria?
3. Can you obtain/build and sequence-confirm the exact constructs with an existing workflow?
4. Can you measure abundance independently and return replicate-level numerical data?
5. What existing capacity, incremental materials budget and turnaround could you offer?

These questions were not sent. No collaborator capability is assumed from unanswered questions.

## Modeling entry point and limitations

Next, without collaborator time: retrieve exact sequences and numerical phenotype tables, separate assay contexts, audit numbering/abundance controls, and count independent labels before selecting a model. ChRger's linked data are a useful reference benchmark; success on them would not validate GtACR2 prediction. Freeze naive and literature/structure baselines before scoring. Use held-out residues, constructs or studies where possible. A tiny focused panel cannot establish broad generalization. Record pretrained-data exposure separately from evaluation leakage.

Confidence: high in broad prior-art overlap; moderate in relative assay burden; low in local feasibility, model accuracy and narrow novelty. This was a targeted primary-literature review through October 12, 2026, not an exhaustive systematic or patent search. Some PMC pages encountered browser checks; publisher articles/primary abstracts provided alternatives. Raw data, supplements, full sequence provenance and licenses have not been audited. No model scores or validated designs are claimed.

## Primary evidence

1. Maurer & Dougherty (2001), *A high-throughput screen for MscL channel activity and mutational phenotyping*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/11557017/). DOI: 10.1016/S0005-2736(01)00390-X. Abstract checked; full protocol not audited.
2. Maurer & Dougherty (2003), *Generation and evaluation of a large mutational library from E. coli MscL*. [PubMed](https://pubmed.ncbi.nlm.nih.gov/12670944/). DOI: 10.1074/jbc.M302892200. Abstract checked; labels not extracted.
3. Kojima et al. (2018), *Mutational analysis of the conserved carboxylates of ACR2 expressed in E. coli*. [Full article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6194965/). Methods/results checked; supplement not extracted.
4. Mahn et al. (2018), *High-efficiency optogenetic silencing with soma-targeted anion-conducting channelrhodopsins*. [Publisher PDF](https://www.nature.com/articles/s41467-018-06511-8.pdf). DOI: 10.1038/s41467-018-06511-8. Abstract checked.
5. Bedbrook et al. (October 14, 2019), *Machine learning-guided channelrhodopsin engineering enables minimally invasive optogenetics*. [Publisher](https://www.nature.com/articles/s41592-019-0583-8); [linked code](https://github.com/fhalab/channels). DOI: 10.1038/s41592-019-0583-8. Abstract/data availability checked; data/code not run.
6. Govorunova et al. (March 3, 2017), *The expanding family of natural anion channelrhodopsins reveals large variations in kinetics, conductance, and spectral sensitivity*. [Publisher](https://www.nature.com/articles/srep43358). DOI: 10.1038/srep43358. Abstract checked.
7. Rodriguez-Rozada et al. (July 9, 2022), *Aion is a bistable anion-conducting channelrhodopsin that provides temporally extended and reversible neuronal silencing*. [Publisher](https://www.nature.com/articles/s42003-022-03636-x). DOI: 10.1038/s42003-022-03636-x. Results checked.
8. Yokoyama et al. (April 10, 2026), *Val109 and Ile170 contribute to channel function in Guillardia theta-derived anion channelrhodopsins*. [Publisher](https://www.nature.com/articles/s41598-026-46487-w). DOI: 10.1038/s41598-026-46487-w. Methods/results checked; supplement not extracted.
9. Phillips laboratory, *MscL Abundance & Survival*, [research supplement](https://www.rpgroup.caltech.edu/mscl_survival/supplement.html). Consulted for abundance/survival confounding, not mutation prediction labels.
10. Nagata et al. (August 6, 2026), *Rhobot-Screen: an integrated robotic platform for functional screening of rhodopsin variants*. [Publisher](https://link.springer.com/article/10.1186/s12915-026-02691-8). DOI: 10.1186/s12915-026-02691-8. Endpoints/methods checked; source data not extracted.
