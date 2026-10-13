# What the primary sources actually support

The benchmark distinguishes archived numbers from measurements with adequate
methods. Its primary matched observable is symmetric-salt, zero-voltage trimer
slope conductance. Mature numbering uses 2OMF residues1–340 and precursor+22.

| Source | Evidence obtained | Use and limitation |
|---|---|---|
| [Miedema2004](https://pmc.ncbi.nlm.nih.gov/articles/PMC1304784/) | Complete primary HTML, exact Table2, methods and model assumptions | Matched gain cohort. Three constructs, repeated NaCl/KCl conditions; unspecified temperature precision and error statistic |
| [Phale1997](https://pmc.ncbi.nlm.nih.gov/articles/PMC21228/) | Full primary HTML, Table1 caption and current-trace interpretation | Finite-voltage monomer challenge; 1mM calcium not represented in the monovalent prototype; event n is not independent culture n |
| [Bredin2002](https://doi.org/10.1042/bj3630521) | Original eight-page PDF read through browser; local abstract HTML; saved table/methods audit | Four additional constructs. High-voltage closure steps differ from zero-slope G. Local PDF retrieval failed |
| [Phale2001 SI](https://ndownloader.figshare.com/files/5670807) | All four scanned pages viewed; TableS1 means/errors transcribed; file checksum verified against Figshare | Thirty-four mutants plus WT, many reused older measurements. Main Table2 condition footnotes remain unverified; excluded from scalar evaluation |
| [Pezeshki2009](https://pmc.ncbi.nlm.nih.gov/articles/PMC2756365/) | Complete primary HTML, table cell boundaries, locally downloaded full supplement | Three experimental conductances stored separately; conductance pH and uncertainties incomplete. Simulation-only cells never become experimental data |
| [D127 study2006](https://doi.org/10.1007/s00249-006-0084-4) | Complete author-hosted ten-page PDF read through browser; exact Table1 and methods audit saved | Two new genotypes, five conductance subpopulations. A separate state-resolved challenge, not five independent mutant targets or a selectively chosen gain |
| [Miedema2007](https://pmc.ncbi.nlm.nih.gov/articles/PMC1779923/) | Complete primary HTML, methods and figures/captions | LECE gains are measured at pH9 and mostly plotted. Not pooled into pH7.4 benchmark or converted to invented exact values |

A legal university deposit of the 2001 paper was located through open-access
metadata. Its current content endpoint returned HTTP401; the download page
returned HTML. The full paper was not obtained, and no authentication bypass,
purchase or author/library contact was attempted. The supplementary conditions
therefore remain a real gap despite the “open access” metadata label.

The 2009 Table1 contains blank experimental G cells for NQAAA, RRRRR+EE and
DEERE. Flattened text juxtaposes simulated conductances and ion-current ratios;
for example 5.6 is not an experimental DEERE conductance. Its supplement's TableS1
also contains calculated MD conductances, not experimental observations.
The paper compares MD at1V with experiments at50mV, discusses nonlinear simulated
I–V curves and limited10ns sampling, and estimates around20% simulation variability.
These are useful detailed-model results with explicit qualifications, not evidence
that small mutant gains can be selected reliably from one trajectory.

A 2003 discussion assigns a roughly7% NaCl conductance increase to K16D. The
original 2002 table places880pS on K16A and800pS on K16D versus820pS WT. We use
the original table. This is a specific attribution discrepancy, not a general
judgment about the literature.

Published DFT/PNP descriptions estimate mobilities from observed conductances and
in some cases assign different mobilities to different mutant proteins. Those fits
cannot establish an independent test of mutation-transfer prediction. Our model
uses the same mobility assumptions across mutants, reports one-WT-calibration
transfer separately, and never fits a mutant-specific diffusion coefficient.

The D127 paper warns against reducing a genotype to a single conformation: it
reports multiple dominant conductance populations, including a higher-than-WT
D127N population alongside lower/near-WT populations. Counts and states are kept;
no unbiased mixture weights or unconditional genotype mean are invented. Its
findings also make protonation and conformational-state assumptions relevant to
any structure-derived objective.

All experimental mutant PDBs are marked as reserved diagnostics. Biological-assembly
MODEL records encode symmetry copies, not independent molecular conformations.
2ZFG is a higher-resolution WT with residue27 unresolved; 1HXX is Y106F, not WT.
No experimental mutant coordinates were used as a prospective-design input.
