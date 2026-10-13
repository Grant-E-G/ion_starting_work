# C5R assay feasibility: OmpF

**Direct single-channel conductance: NO-GO as a demonstrated cheap bacterial
plate-reader loop. Whole-cell solute permeability: CONDITIONAL GO as a different
observable requiring its own predictive model.**

C5R's [physical PCR equipment appendix](https://c5r.net/sciuniverse/suites/pcr-recovery/)
documents a CLARIOstar Plus, Hamilton STARlet, thermocycler and heater-shaker.
The [reader manufacturer](https://www.bmglabtech.com/en/clariostar-plus/)
specifies kinetic absorbance and fluorescence modes. Those are real resources;
this assessment does not assume a new reader purchase. No electrophysiology
amplifier, bilayer rig or established OmpF reconstitution workflow is documented
in the cited public equipment evidence. Absence from that evidence is not proof
that equipment is absent from the lab.

| Observable | Fit to resources | Main burden/confound | Decision |
|---|---|---|---|
| Purified OmpF single-channel slope conductance | Requires electrophysiology beyond the documented reader | Purification, reconstitution, manual bilayer formation, channel identification | No demonstrated inexpensive C5R route |
| Intact-cell nitrocefin hydrolysis | Kinetic visible absorbance fits the documented reader | Periplasmic enzyme, efflux, abundance, leakage and alternative porins | Plausible low-cost readout after controlled host/reporter setup; not conductance |
| Growth on a limiting sugar/maltodextrin | Reader and heater-shaker are suitable in principle | Native sugar transporters, metabolism, abundance and envelope stress | Useful cheap functional screen; substrate-specific and indirect |
| Purified-protein liposome sugar swelling | Absorbance readout is compatible | Protein purification and reproducible proteoliposomes dominate effort | More controlled permeability assay; not automatically low effort |
| Optical ion flux in proteoliposomes | Fluorescence readout may be compatible | Channel count, orientation, ion gradients, dye calibration and purification | Ensemble flux, not single-channel G; establish a transfer relation first |

A [primary E. coli assay study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4518837/)
uses 96-well kinetic nitrocefin absorbance with periplasmic beta-lactamase.
A [laboratory protocol](https://cmdr.ubc.ca/bobh/method/nitrocefin-assay-on-whole-cells-for-outer-membrane-permeability-assessment/)
compares intact cells, disrupted cells and cell-free supernatant. These controls
address enzyme availability and leakage. The study also identifies nitrocefin
as an efflux substrate: an initial slope is not automatically a porin-only
permeability constant. A plate adaptation of the latter cuvette protocol would
need validation; its existence does not establish that C5R stocks the reporter
strain, substrate or cell-disruption apparatus.

The low-effort part is taking the optical readings. The one-time work is a
controlled nonpathogenic E. coli host, identical expression cassettes carrying
the native signal peptide, a suitable reporter, and confirmation that folded
OmpF reaches the outer membrane. The mature mutation numbering must be shifted
by 22 in the precursor coding sequence. Endogenous OmpF/OmpC or LamB can obscure
attribution. Equivalent expression and viability cannot be inferred from an
increased optical signal. No strain construction or wet-lab work was performed
in this session.

**Conductance cannot be used as a surrogate permeability objective.** The
[original Bredin 2002 study](https://doi.org/10.1042/bj3630521) measures both
ion-channel behavior and solute uptake, with different outcomes across mutants.
Its radioactive cefepime method is not a cheap reader assay. The Phale
[supporting tables](https://ndownloader.figshare.com/files/5670807) likewise show
NQAAA with lower ion conductance than WT but much larger disaccharide swelling
responses. Main-paper normalization/condition details are unavailable here, so
these supporting numbers are mechanistic counterexamples, not a new quantitative
cross-assay calibration.

A [2026 primary OMV study](https://www.nature.com/articles/s41467-026-75817-9)
provides another permeability approach, but its quantitative method uses NMR
and vesicle preparation. It does not establish a low-effort C5R ion-conductance
assay. We should not mistake the word “vesicle” for a ready-made optical workflow.

The smallest useful bridge experiment is **assay validation before new designs**:
WT, an appropriate known solute-permeability control, and an empty-vector control;
independent cultures; intact-cell readout accompanied by enzyme-capacity,
supernatant leakage, viability and outer-membrane abundance checks. First ask
whether the known control separates reproducibly from WT after normalization.
Only then benchmark a solute-specific transport objective. The current monovalent
ion model provides no prediction for nitrocefin or sugar permeability, so it
cannot legitimately select that control or claim success on that assay.

No purchases, contacts, price quotes or wet-lab execution occurred. No dollar
budget is invented. Marginal plate-reader measurements could be inexpensive
with existing stocks and staff, while host/reporter construction and purification
may dominate total cost. A direct conductance design loop remains blocked by
assay readiness even if the computation is cheap.
