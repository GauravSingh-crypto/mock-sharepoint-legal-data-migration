# Local Testing Guide

This guide explains how to run and validate the SharePoint legal-data migration demonstration from a clean terminal session. The demo uses synthetic data and does not connect to a real SharePoint tenant.

## Prerequisites

- macOS, Linux, or Windows with a terminal
- Python 3.9 or newer
- Optional: the `sqlite3` command-line utility for direct SQL inspection

The core demo uses only the Python standard library. It does not require Docker, a virtual environment, a cloud account, or package installation.

## 1. Open the project directory

```bash
cd /Users/gauravsingh/Desktop/Toptal3/Gaurav-singh-1/toptal-projects-demo/mock-sharepoint-legal-data-migration
```

## 2. Confirm the current location

```bash
pwd
```

The result should end with:

```text
toptal-projects-demo/mock-sharepoint-legal-data-migration
```

## 3. Confirm the Python version

```bash
python3 --version
```

Python 3.9 or newer is required.

## 4. Inspect the project files

```bash
find . -maxdepth 3 -type f | sort
```

## 5. Run the complete demonstration

```bash
python3 run_demo.py
```

Expected summary:

```text
Files discovered: 31
Source paths over 400 characters: 1
Maximum source path length: 514
Automatically approved: 27
Manual review required: 1
Blocked: 3
Successfully migrated: 27
Checksum mismatches: 0
Maximum planned destination path: 108
```

The command recreates the `work/` directory on every run, ensuring a deterministic demonstration.

## 6. Run all automated tests

```bash
python3 -m unittest discover -s tests -v
```

Expected ending:

```text
Ran 7 tests
OK
```

The tests validate metadata extraction, exception routing, path-length handling, filename sanitization, destination uniqueness, migration outputs, and checksum reconciliation.

## 7. Read the human-readable summary

```bash
cat work/output/demo_summary.md
```

## 8. Read the machine-readable audit report

```bash
cat work/output/audit_summary.json
```

## 9. Inspect the deeply nested source hierarchy

```bash
find work/sample_data/legacy_share -type f | head -20
```

The source contains client, matter, transaction-attempt, and status context encoded in folders and filenames.

## 10. Inspect the flattened destination hierarchy

```bash
find work/sample_data/sharepoint_simulation -type f | head -20
```

Destinations should follow this pattern:

```text
Legal Matters/MAT-0042/2025-03-18_Revised-Purchase-Agreement_ATT01.pdf
```

## 11. Inspect the source inventory

```bash
head -10 work/output/source_inventory.csv
```

The inventory includes original paths, extensions, sizes, path lengths, directory depths, and SHA-256 fingerprints.

## 12. Query paths longer than 400 characters

The most reliable check uses SQLite:

```bash
sqlite3 work/migration.db "SELECT path_length, source_path FROM source_inventory WHERE path_length > 400;"
```

Expected: one record with a path length of 514.

If the optional `sqlite3` program is unavailable, read the summary instead:

```bash
cat work/output/audit_summary.json
```

## 13. Inspect normalized SharePoint metadata

```bash
head -10 work/output/normalized_metadata.csv
```

Important columns include client, matter, document date, sender, document type, transaction attempt and status, confidence score, original path, and planned destination.

## 14. Inspect exceptions

```bash
cat work/output/exceptions.csv
```

Expected exception categories:

- One missing-sender record requiring manual review
- One zero-byte file that is blocked
- One unsupported ZIP file that is blocked
- One unrecognized filename that is blocked

## 15. Inspect migration execution results

```bash
head -10 work/output/migration_results.csv
```

Only records with `READY` validation status are copied to the simulated SharePoint library.

## 16. Inspect checksum reconciliation

```bash
head -10 work/output/reconciliation.csv
```

Every migrated record should have:

```text
MIGRATED,MATCH
```

## 17. Confirm zero checksum mismatches

```bash
grep -c MISMATCH work/output/reconciliation.csv
```

Expected output:

```text
0
```

Some shells return a nonzero command status when `grep` finds no matches. The printed count of `0` is the expected validation result.

## 18. Run the complete audit SQL

```bash
sqlite3 work/migration.db < sql/audit_summary.sql
```

Expected output includes:

```text
31|2919|1|514|4.1
BLOCKED|3
READY|27
REVIEW_REQUIRED|1
```

## 19. Run the reconciliation SQL

```bash
sqlite3 work/migration.db < sql/reconciliation.sql
```

Expected output:

```text
MIGRATED|MATCH|27
SKIPPED|NOT_APPLICABLE|4
```

## 20. Confirm destination path safety

```bash
sqlite3 work/migration.db "SELECT destination_path FROM normalized_documents WHERE LENGTH(destination_path) > 240;"
```

Expected: no output.

## 21. Confirm destination uniqueness

```bash
sqlite3 work/migration.db "SELECT LOWER(destination_path), COUNT(*) FROM normalized_documents WHERE destination_path IS NOT NULL GROUP BY LOWER(destination_path) HAVING COUNT(*) > 1;"
```

Expected: no output.

## 22. Confirm the migrated file count

```bash
find work/sample_data/sharepoint_simulation -type f | wc -l
```

Expected output:

```text
27
```

## 23. Verify repeatability

```bash
python3 run_demo.py
```

The result should match the first demonstration run.

## 24. Run the tests after regeneration

```bash
python3 -m unittest discover -s tests -v
```

Expected ending:

```text
Ran 7 tests
OK
```

## Validation checklist

- [ ] Python is version 3.9 or newer.
- [ ] The demo reports 31 discovered files.
- [ ] At least one source path exceeds 400 characters.
- [ ] The maximum destination path is no longer than 240 characters.
- [ ] Manual-review and blocked records appear in `exceptions.csv`.
- [ ] Exactly 27 approved files are migrated.
- [ ] All migrated files have matching SHA-256 fingerprints.
- [ ] No planned destination is duplicated.
- [ ] All seven automated tests pass.

