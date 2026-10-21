# Local statistical audit records

Read [the workflow](../../../notes/statistics/workflow.md). These checks are a
local integrity aid, not a statistical evaluator or authorization mechanism.
Run from the repository root with Python 3.10+; no runtime dependencies.

Copy `sources/statistics/claim_template.json` to a new claim JSON, fill every
placeholder, and supply actual artifact paths relative to the repository root.
The partition CSV has one row per construct, split membership and all declared
group IDs. Relations with shared ancestry/publications need precomputed connected
components. Every declared grouping column is enforced separately across splits.
Use appropriate groups for the claim; do not impose site separation when the
stated deployment regime intentionally predicts new substitutions at known sites.

```bash
python code/checks/statistics/audit.py validate claim.json
python code/checks/statistics/audit.py freeze claim.json --output submission.json
python code/checks/statistics/audit.py record submission.json --ledger ledger.jsonl --event submitted --detail 'Run IDs, commit, seeds and budget recorded in hashed analysis'
# Execute the declared work; preserve stderr and failures.
python code/checks/statistics/audit.py record submission.json --ledger ledger.jsonl --event completed --detail 'Result artifact path/hash and all run IDs'
python code/checks/statistics/audit.py check submission.json
python code/checks/statistics/audit.py verify-ledger ledger.jsonl
python -m unittest discover -s code/checks/statistics -v
```

Use `failed` for an execution failure and `deviation` for a subsequent correction.
The submission file is created exclusively and cannot be overwritten by `freeze`.
Send its digest to the independent evaluator before protected outcomes; they must
retain it and track all submissions to the same panel. External immutability,
truthful declarations, complete logging and label isolation are not enforced here.
For E4 also have the decision owner retain the freeze before biological outcomes.
