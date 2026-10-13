# Ion-channel optimization proof of concept

Updated October 13, 2026. Current phase: modeling feasibility before revisiting target/readout choice.

The [local protein-model benchmark](protein_model_benchmark.md) compares ESM-2 650M, ESM C 600M and AMPLIFY 350M on the user's RTX 3080 16 GB. All pass local inference and adapter optimization. None provides convincing direct likelihood-to-transport ranking on the six-mutant diagnostic. Next determine whether compatible phenotype data supports directional prediction and fine-tuning; model choice and GtACR2 selection remain open. The original feasibility-first statement below describes the prior phase.

## Question and current decision

The [physics-based membrane-function search](physics_based_membrane_function.md) evaluates the user's fold → physical function → optimizer architecture. Direct MD has functional precedents; reduced transport/kinetic objectives and differentiable force fields are potential components. Differentiability of parameters is distinct from validated gradients of mutant function. Assess a bounded reference functional simulation and reduced-objective gradients before building a sequence optimizer; no physical simulation has yet run.

The [model taxonomy and evidence requirements](protein_model_taxonomy_and_evidence.md) qualifies all model comparisons: coordinate prediction, evolutionary sequence plausibility and assay-specific phenotype prediction are different tasks. Published correlations are screening evidence, not validated engineering capability. Require grouped evaluation, realistic label budgets and above-reference selection before model/target acceptance.

The [nearby dataset/model audit](nearby_modeling_datasets.md) now governs the computational gate: GtACR2 has not passed useful-design feasibility. Retrieved channelrhodopsin and Kir2.1 data support larger tests; published assay-level results include heavier models and supervised alternatives. Demonstrate modeling signal on relevant larger datasets and test transfer before returning to the physical target/readout decision. Do not accept an unsupported GtACR2 experiment merely because its assay can be made inexpensive.

The [funding-stage scope correction](funding_stage_poc_scope.md) governs this project: demonstrate meaningful engineering of a biologically relevant membrane protein with a simple supplied workflow. The partner is a force multiplier, not a CRO. Patch clamp and external specialist validation are outside the current milestone. Choose the target/readout pair to fit actual routine capabilities; a controlled functional proxy can be sufficient for a correctly bounded POC claim.

The [multiple-readout investigation](gtacr2_readout_options.md) identifies fluorescent extracellular pH and endpoint iodide colorimetry as priority GtACR2 assay-transfer candidates, with red membrane-potential fluorescence as a supporting/competing route. Match these to the actual reader before selecting one bounded control pilot. These are plausible adaptations, not completed or verified assays.

The [public C5R audit and pricing](c5r_gtacr2_pricing.md) identifies a physical CLARIOstar Plus, STARlet and on-deck thermocycler. Use documented hardware without asking redundant inventory questions. Current recommendation: HPTS detector/controlled bacterial pilot, then a cheap red-voltage supporting route; retain iodide colorimetry as an alternative. Price shared biological preparation and illumination separately from readout reagents.

Can a small reproducible design process predict a useful ion-channel functional change beyond established engineering heuristics, with a practical experimental burden?

See [the initial sourced assessment](ion_channel_feasibility_novelty.md) and the more detailed [GtACR2 decision and budget](gtacr2_decision_and_budget.md). GtACR2 remains a candidate because of its biological relevance, conditional on a practical functional readout. E. coli MscL remains an alternative workflow scaffold. The immediate task is target/readout fit for routine partner capabilities; the earlier specialist-validation budget is background for a later stage.

The [inherited handoff](membrane_protein_computational_viability_agent_brief.md) is background. Organizational capabilities, conversations, financing and commitments in it remain unverified. The user's feasibility-first instruction takes precedence over its immediate modeling requirements.

## Intended contribution

Limited-data prediction of a specified functional phenotype, demonstrated prospectively against frozen literature/structure heuristics at equal candidate budget. Agent orchestration alone is not the contribution. Eventual neuronal utility needs a defined task and comparison with existing actuators.

## Next phase, before model selection

1. Select one endpoint and assay context.
2. Retrieve exact source sequences, construct definitions and numerical phenotype tables; audit numbering and abundance controls.
3. Count independent residues/constructs/studies and determine whether meaningful held-out validation is possible.
4. Freeze naive and literature/structure baselines before scoring.
5. Evaluate a manageable pretrained model only after defining the prediction target; sequence plausibility is not automatically directional function.
6. Advance to candidate hypotheses only if data quality and retrospective signal justify them; preserve negative findings.

No models were run or optimized variants proposed during the feasibility phase.
