# Existing methods: accelerated survey, 14 October 2026

These methods predict different observables. A structure, sequence likelihood,
folding energy, state population and ion current are not interchangeable labels.
“Local plausible” below is an installation/resource assessment, not a measured
throughput claim. Actual execution measurements are in the checkpoint report.

| Method / published implementation | Information and experimentally supported scope | Weights / local requirements / principal limitation | This block |
|---|---|---|---|
| [ESM-1b/1v efficient evolution](https://github.com/brianhie/efficient-evolution) | Evolutionary substitution preferences; September ChrimsonR functional engineering | Public 650M checkpoints. Original method is ESM-1b + five ESM-1v members. Sequence plausibility is not an objective-specific gain prediction. | **One ESM-1v 650M member executed on CPU**, compared with 8M and physical descriptors. |
| [ESM-2](https://github.com/facebookresearch/esm) | Masked sequence likelihood and representations; broad variant-effect benchmarks | Public 8M–15B weights; model size is a testable choice, not a fixed platform decision. | Existing 8M features and new zero-shot checks. |
| [SaProt](https://github.com/westlake-repl/SaProt) | Sequence + Foldseek structural alphabet; mutation-effect prediction | Public 35M/650M/1.3B weights; requires trustworthy structure tokens and confidence masking. | Surveyed; **35M is a good next cheap ablation**. No membrane-function gain demonstrated here. |
| [ProteinMPNN](https://github.com/dauparas/ProteinMPNN) | Backbone-conditioned sequence compatibility; experimentally validated protein designs | Public ~1.66M checkpoint, CPU feasible. Successful fold/design evidence does not validate channel gain ranking. | Official implementation/weights executed, probability/repeat checks. |
| [LigandMPNN + membrane-labelled MPNN](https://github.com/dauparas/LigandMPNN) | Atomic ligand context, or global/per-residue membrane labels | Public small checkpoints. Retinal covalent linkage, PIP2, oligomer state and protein modifications need explicit input audits. | Vanilla/global-label/ligand variants executed in paired tests. |
| [BioEmu](https://github.com/microsoft/bioemu) | Approximate monomer conformational ensembles; soluble-protein state/stability benchmarks | Public checkpoints; AF2/MSA embeddings, additional first-use downloads. No explicit membrane, tension, light cycle or multimer model. | Documentation and membrane benchmark audited; **no local sampling timing claimed**. |
| [RosettaMP / Franklin2019/2023](https://github.com/Graylab/Implicit-Membrane-Energy-Function-Benchmark) | Implicit membrane solvation, packing, electrostatics; experimental membrane stability/orientation benchmarks | Existing CPU protocols, rotamer repacking and optional relaxation. Check applicable distribution licence before industrial use. Stability is an auxiliary endpoint; OmpLA data were used in calibration and cannot serve as independent validation of Franklin energies. | Retrieved independent OmpLA/PagP data; Rosetta itself **not run**. |
| [PPM 3.0](https://oprlm.org/ppm_server3_cgopm) | Transfer-energy minimization; membrane orientation, thickness and curvature | Authors offer Linux source. Not an ion transport or mutation-to-gating model. | Surveyed. No local binary/runtime measured. |
| [MemPrO](https://github.com/ShufflerBardOnTheEdge/MemPrO) | Martini-derived coarse membrane placement/curvature energy | Python ≥3.11, JAX CPU 0.6.0 specifically; isolated Python 3.11 environment used. Orientation validation is not mutant function validation. | **Pinned source executed on CPU**, 20/150 iteration and start-grid checks; no function claims. |
| [CHAP](https://github.com/channotation/chap) | Pore geometry, hydrophobicity and trajectory water density / dewetting barriers | CPU C++/GROMACS dependencies; hydration needs water trajectories. Wetting is necessary in some pores, not sufficient for conduction. | Surveyed as a selective physical discriminator. No new pore simulation. |
| [APBSmem / PDB2PQR](https://pmc.ncbi.nlm.nih.gov/articles/PMC4527966/) | Membrane continuum electrostatics, insertion/protonation energetics | Local PB solvers; charges, dielectric boundary, protonation and cofactor parameterization matter. Does not supply gating kinetics. | Surveyed. **Frozen OmpF work not rerun or extended.** |
| [ProDy GNM/ANM](https://github.com/prody/ProDy) | Elastic-network fluctuations and collective directions | CPU, no weights. Uniform springs have no mutation-specific energy mapping; mutation-property interactions here are supervised descriptors. | ProDy GNM executed; conservation/positive-mode checks. |
| [Wimley–White experimental transfer scales](https://blanco.biomol.uci.edu/reprints/jmb_tm_helices.pdf) + solvent exposure | Measured residue transfer preferences; a cheap solvation hypothesis | No weights/GPU. Octanol is not a bilayer. Exposure-weighted score omits orientation, protonation, relaxation and lipid headgroups. | Executed with Biopython Shrake–Rupley; independent stability ranking and functional ablations. |
| [OpenMM](https://docs.openmm.org/latest/userguide/application/02_running_sims.html) | Atomistic forces, sampling and free-energy building blocks | CPU supported; requires complete parameterized assemblies, lipids/cofactors and appropriate sampling. Energy minimization cannot establish functional improvement. | Installed, platforms enumerated, actual template preparation checked; see compatibility failures. |
| [GROMACS + Martini](https://manual.gromacs.org/current/reference-manual/special/free-energy-implementation.html) | Explicit/coarse lipids, tension, hydration, umbrella/alchemical free energies | Local CPU/GPU engines; mutation transformations and open/closed thermodynamic cycle require convergence checks. Large scope without a discriminating hypothesis. | Surveyed; no new general MD pipeline. |
| [EVmutation](https://marks.hms.harvard.edu/evmutation/downloads.html) | Potts sequence couplings; mutation-effect benchmarks | Public code; needs deep, appropriate MSA or existing fitted family parameters. | Surveyed; current tiny paralog alignment is insufficient for a serious test. |
| [GEMME](https://academic.oup.com/mbe/article/36/11/2604/5548199) | Fast evolutionary/epistatic sequence constraints | CPU; family MSA quality and depth are critical, not a pretrained physical simulator. | Surveyed; useful stronger evolutionary control. |
| [PoreDesigner](https://github.com/maranasgroup/PoreDesigner) | IPRO optimization of pore constriction/chemistry with experimentally tested water/solute separations | Public repo exposes PoreAnalyzer; full workflow README requires CHARMM/GAMS licences and contacting authors. **Not an immediately downloadable complete no-cost optimizer.** | Full paper and repository audited only; no contact, purchase or OmpF redesign. |
| [BKpred](https://github.com/enordquist/bkpred) | Open/closed-state Rosetta energy differences + WT MD descriptors + random forests; measured gating-voltage shifts and later experiments | Public labels/features/scripts; historical covariance-anchor selection uses functional knowledge; censored voltage labels and target squashing need audit. | **Precomputed-feature site-holdout stress test executed**; no local MD/Rosetta generation claimed. |
| [MeMDLM](https://arxiv.org/abs/2410.16735) | Membrane-sequence generation using masked diffusion | Generation/physicochemical plausibility is not calibrated mutation-function prediction. | Surveyed; low priority until a specific functional benchmark is specified. |

Five selected approaches: **ESM-1b/1v consensus**, **MemPrO membrane context**,
**membrane-/ligand-aware MPNN**, **RosettaMP membrane stability**, and **BioEmu
ensembles**. SaProt 35M is a useful additional cheap challenger; CHAP supplies
a targeted hydration test when a state/permeation hypothesis warrants it. This is
an ordering of computational tests, not an experimental target commitment.
Sequence and inverse-folding models are cheap screening candidates; physical
and ensemble models should be invoked
only for a phenotype-specific, falsifiable hypothesis. No hybrid architecture
was built in this block.

## Three requested studies: evidence audit

**ChrimsonR:** [published 8 September 2026](https://www.nature.com/articles/s41598-026-66799-1),
with a May preprint and retrievable [full-text/supplements](https://pmc.ncbi.nlm.nih.gov/articles/PMC13192664/).
Seventeen recommendations include two unpatchable constructs; Figure 2 contains
15 mutants. E300G/P improve sustained current but slow closure. The supplement
provides mutation identities and a plasmid map, not a full per-cell measurement
matrix or verified input FASTA. The prose reverses the ESM ensemble composition;
author code defaults to one ESM-1b and five ESM-1v. Our single-member, surrogate-
sequence masked-marginal test is **not a reproduction of the published selector**.
The selected panel cannot estimate enrichment over random mutations. This is
nevertheless direct functional engineering evidence worth pursuing.

**BioEmu:** the [August 2026 membrane benchmark](https://www.biorxiv.org/content/10.64898/2026.08.08.743655v1.full)
reports plausible GlpG/rhomboid gate states but different population weights from
MD and incomplete landscape coverage. Its reported ~40 min/1,000 samples is a
published measurement, not this machine's performance. Code is monomer-only and
omits membrane conditions; samples are not kinetics, light-driven states or
calibrated mutant gating free energies. The [benchmark implementation](https://github.com/microsoft/bioemu-benchmarks)
warns of numerical comparability changes across dependency versions. Next test:
reproduce one accessible conformational observable with pinned dependencies,
then ask whether mutation-induced population shifts match independent data.

**PoreDesigner:** [the primary study](https://www.nature.com/articles/s41467-018-06097-1)
reports designed OmpF water/solute separation constructs and independent MD
checks. Water permeability/selectivity through reconstituted pores is distinct
from ion conductance or whole-cell uptake. Public-code availability does not
cover the full licensed design stack. It supplies evidence that physical design
can work for a constrained observable, not evidence that our frozen conductance
model should be revisited. No OmpF implementation/results were changed.
