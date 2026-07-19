# Migration runbook

## Local validation

1. Run `python3 run_demo.py`.
2. Review `work/output/audit_summary.json`.
3. Review all records in `work/output/exceptions.csv`.
4. Inspect proposed columns and paths in `normalized_metadata.csv`.
5. Confirm every migrated record is `MATCH` in `reconciliation.csv`.
6. Run `python3 -m unittest discover -s tests -v`.

## Production gates

Before production use, complete a permission inventory, confirm tenant path rules, validate content types and columns in a test library, define manual-review ownership, run a pilot batch, validate search indexing and permissions, schedule the cutover, and retain a rollback source snapshot. Do not remove the legacy source until reconciliation and business sign-off are complete.

