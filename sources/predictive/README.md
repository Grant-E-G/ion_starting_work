# Predictive benchmark inputs

`source_manifest.json` records public source URLs, retrieval status and SHA256
checksums, including the pinned pretrained checkpoint. `freeze.json` and
`partitions.csv` preserve the pre-tuning main test assignments and gain criteria.
`mscl2005_gating.csv` manually transcribes primary Table I; missing WT-substate
SDs remain missing, and trace/state counts do not inflate independent mutants.
`mscl_partitions.csv` records its two-site transfer diagnostic.

Raw downloads and derived feature arrays are ignored. They remain locally and
are recreated with `code/experiments/predictive/cache.py` and `features.py`.
Labels from `sources/nearby_modeling` remain unchanged. See the experiment README
and quantitative report for semantic limits, failures and exact commands.
