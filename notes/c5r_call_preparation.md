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
