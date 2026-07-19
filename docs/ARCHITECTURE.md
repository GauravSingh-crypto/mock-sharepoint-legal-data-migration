# Architecture

## 1. Purpose

This project demonstrates how a senior data engineer can convert an irregular legal-document hierarchy into a controlled, searchable, SharePoint-ready dataset. It focuses on the highest-risk migration work: inventory, path analysis, metadata extraction, normalization, exception handling, deterministic flattening, and integrity reconciliation.

The implementation runs locally with Python and SQLite so reviewers can validate the logic without Docker, Microsoft 365 credentials, or a SharePoint tenant.

## 2. System context

```text
Legacy file share / Google Drive export
                  |
                  v
       Local migration framework
       - discovery and fingerprinting
       - metadata normalization
       - quality and exception controls
       - destination planning
       - execution and reconciliation
                  |
                  v
      SharePoint document library
      simulated locally in this demo
```

The demo generates synthetic PDF, DOCX, and XLSX placeholders. No real legal or client information is included.

## 3. Processing flow

```text
Synthetic dataset generator
            |
            v
Read-only source discovery ----------> source_inventory
            |
            v
Path and file-quality audit
            |
            v
Filename + folder parser ------------> normalized_documents
            |
            v
Confidence and exception routing
       /         |          \
    READY   REVIEW_REQUIRED  BLOCKED
       |         |             |
       v         +-------> exceptions.csv
Destination planner
       |
       v
Local transfer simulation -----------> migration_results
       |
       v
SHA-256 reconciliation --------------> reconciliation.csv
```

Only `READY` records cross the transfer boundary. Records needing human judgment remain visible in the exception queue, and unsafe records are blocked.

## 4. Component responsibilities

| Component | Responsibility |
|---|---|
| `run_demo.py` | Minimal executable entry point |
| `generator.py` | Generates deterministic legal records and deliberate edge cases |
| `discovery.py` | Inventories source files and calculates SHA-256 fingerprints without modifying them |
| `models.py` | Defines the source and migration domain records |
| `parser.py` | Extracts client, matter, transaction, date, sender, and document-type metadata |
| `planner.py` | Produces shallow, sanitized, length-checked, collision-safe destinations |
| `database.py` | Creates SQLite control tables and portable CSV reports |
| `migrator.py` | Simulates transfer and calculates destination fingerprints |
| `pipeline.py` | Orchestrates every stage and produces summary evidence |
| `sql/` | Contains independent audit and reconciliation queries |
| `tests/` | Validates individual rules and the full pipeline |

## 5. Data model

### `source_inventory`

The immutable source control table contains:

- Stable source identifier
- Original relative path and filename
- Extension and size
- Path length and directory depth
- SHA-256 source fingerprint

### `normalized_documents`

The transformation and planning table contains:

- Client and legal matter context
- Document date, sender, and document type
- Transaction attempt and status
- Parsing confidence
- Proposed SharePoint destination
- Validation status and explanation
- Original path and source fingerprint for traceability

### `migration_results`

The execution control table contains:

- Migration status
- Destination path
- Destination fingerprint
- Integrity result
- Execution error, if any

The three tables provide source-to-destination lineage without relying on folder names after migration.

## 6. Metadata extraction

The filename convention used by the synthetic dataset is:

```text
YYYY-MM-DD__Sender__Document-Type__Description.extension
```

Folder paths provide client, matter, transaction attempt, and attempt status. Parsing rules intentionally avoid guessing when required structure is absent.

Confidence is based on successfully extracted business fields and supported file types. Critical missing values can force manual review even when the overall score is high.

## 7. Path-flattening strategy

An irregular source path such as:

```text
Clients/Acme Corporation/MAT-0042 - Acquisition of Example Holdings/
Attempt 02 - Failed/Correspondence/.../Revised-Purchase-Agreement.pdf
```

becomes:

```text
Legal Matters/MAT-0042/2025-03-18_Revised-Purchase-Agreement_ATT02.pdf
```

The hierarchy is not discarded. Client, matter, transaction attempt, transaction status, and original path are stored as structured metadata.

Destination planning applies:

1. SharePoint-invalid character replacement
2. Repeated-separator normalization
3. Descriptive filename shortening
4. Stable transaction-attempt suffixes
5. Deterministic hash suffixes for collisions
6. A conservative 240-character destination limit

## 8. Safety and data-quality controls

- Source discovery is read-only.
- Source files are fingerprinted before migration.
- Unsupported file types and zero-byte files are blocked.
- Unrecognized naming patterns are blocked.
- Missing critical metadata is routed to manual review.
- Only approved records are transferred.
- Destination paths are length-checked before transfer.
- Destinations are checked case-insensitively for collisions.
- Destination fingerprints are compared with source fingerprints.
- Original paths remain available for audit and rollback investigation.

## 9. Idempotency and repeatability

The synthetic input and output names are deterministic. Destination names derive from normalized business identifiers and source context. Collision suffixes derive from source paths rather than timestamps or processing order.

The local demonstration recreates `work/` on every run and produces the same counts and validation results. A production implementation would preserve batch state and skip records whose source fingerprint and verified destination have not changed.

## 10. SharePoint information architecture

The proposed `Legal Matters` library uses stable matter IDs for shallow organization. Business meaning moves into indexed SharePoint columns such as Client, Matter ID, Document Date, Sender, Document Type, Transaction Attempt, and Transaction Status.

This supports library views, Microsoft Search, retention controls, and permission-aware Copilot retrieval more effectively than deep, inconsistent folders. Copilot readiness still requires tenant-specific permission, sensitivity, retention, indexing, and oversharing reviews.

## 11. Production integration boundary

The demo uses `shutil.copy2` as a local transfer adapter. This is intentionally isolated from discovery, transformation, planning, and reconciliation.

For production, the transfer layer could be replaced with:

- Microsoft SharePoint Migration Tool
- Microsoft Migration Manager
- ShareGate
- PnP tooling
- Microsoft Graph upload sessions

The selected tool would transfer file bytes and apply approved metadata. The Python framework would continue to own inventory, normalization, exception decisions, manifests, batch controls, and reconciliation.

## 12. Production extensions

A production delivery would add:

- Local-share and Google Drive permission inventory
- Microsoft Entra ID group mapping
- SharePoint site-column and content-type provisioning
- Checkpointed batches, throttling, and retry policies
- Cutover and delta-migration handling
- Search-index verification
- Sensitivity and retention configuration
- Operational dashboards and alerting
- Business-owner review and sign-off workflow
- Recovery and rollback procedures

## 13. Validation

The automated suite verifies metadata extraction, review and blocking rules, real source paths over 400 characters, invalid-character sanitization, shallow destinations, uniqueness, generated evidence, migrated counts, and SHA-256 integrity.

Follow [TESTING_GUIDE.md](TESTING_GUIDE.md) to reproduce the complete validation.
