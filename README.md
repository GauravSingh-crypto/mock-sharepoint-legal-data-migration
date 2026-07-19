# SharePoint Legal Data Migration Demo

A zero-runtime-dependency Python and SQLite proof of concept for auditing an irregular legal-document hierarchy, extracting business metadata from filenames and folders, flattening paths safely, simulating migration into a SharePoint-style library, and reconciling file integrity.

This is a synthetic portfolio project. It contains no client information and does not claim to be a production migration.

## What it demonstrates

- Read-only discovery with SHA-256 source fingerprints
- Identification of paths over SharePoint's 400-character decoded-path limit
- Metadata extraction for client, matter, transaction attempt, date, sender, and document type
- Confidence-based routing to automatic approval, manual review, or blocked status
- Shallow, deterministic, SharePoint-safe destination planning
- Collision resolution without losing the original source context
- SQLite control tables and SQL audit queries
- Local migration simulation and checksum reconciliation
- Standard-library `unittest` coverage

## Quick start

Requires Python 3.9 or newer. No package installation, Docker, cloud account, or SharePoint tenant is needed.

```bash
python3 run_demo.py
python3 -m unittest discover -s tests -v
```

Generated files are written under `work/`, which is intentionally ignored by Git.

## Pipeline

```text
Synthetic legacy hierarchy
          ↓
Read-only discovery + SHA-256 inventory
          ↓
Path and data-quality audit
          ↓
Filename/folder metadata parsing
          ↓
Confidence scoring + exception routing
          ↓
Safe shallow destination planning
          ↓
Local SharePoint-library simulation
          ↓
Checksum and metadata reconciliation
```

The original hierarchy may encode client, matter, transaction attempt, and status in deeply nested folders. The planned destination uses a shallow path such as:

```text
Legal Matters/MAT-0042/2025-03-18_Revised-Purchase-Agreement_ATT02.pdf
```

The removed path context is retained in `normalized_metadata.csv`, including the complete original path.

## Generated evidence

| Output | Purpose |
|---|---|
| `work/migration.db` | SQLite source, normalized, and migration control tables |
| `source_inventory.csv` | Immutable source inventory and fingerprints |
| `audit_summary.json` | Path risks and pipeline totals |
| `normalized_metadata.csv` | Proposed SharePoint columns and destinations |
| `exceptions.csv` | Manual-review and blocked records |
| `migration_results.csv` | Per-file execution results |
| `reconciliation.csv` | Source-to-destination checksum evidence |
| `demo_summary.md` | Human-readable result summary |

## SQL inspection

If the optional `sqlite3` command-line program is installed:

```bash
sqlite3 work/migration.db < sql/audit_summary.sql
sqlite3 work/migration.db < sql/reconciliation.sql
```

Python itself includes the SQLite library, so the demo does not depend on this CLI.

## Safety model

- Discovery does not change source files.
- Only `READY` records are copied.
- Ambiguous metadata is placed in a review queue.
- Unsupported and zero-byte files are blocked.
- Original paths and checksums are retained for traceability.
- Destination names are deterministic, sanitized, length-checked, and collision-safe.
- The demo destination is local; a production transfer adapter would use a reviewed Microsoft migration tool or API.

See the [testing guide](docs/TESTING_GUIDE.md), [architecture](docs/ARCHITECTURE.md), [SharePoint mapping](docs/SHAREPOINT_MAPPING.md), [runbook](docs/MIGRATION_RUNBOOK.md), and [application answers](docs/APPLICATION_ANSWERS.md).
