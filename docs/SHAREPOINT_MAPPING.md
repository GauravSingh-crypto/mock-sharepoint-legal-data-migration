# SharePoint information architecture and mapping

## Proposed library

`Legal Matters` uses a shallow `<matter ID>/<document>` structure. Client and transaction context is represented as columns rather than deeply nested folders.

| Normalized field | Proposed SharePoint column | Type |
|---|---|---|
| `client_name` | Client | Managed metadata or text |
| `matter_id` | Matter ID | Required indexed text |
| `matter_name` | Matter Name | Text |
| `document_date` | Document Date | Date |
| `sender_name` | Sender | Person or text after identity review |
| `document_type` | Document Type | Choice/content type |
| `attempt_number` | Transaction Attempt | Number |
| `attempt_status` | Transaction Status | Choice |
| `source_path` | Original Source Path | Multiple lines of text |
| `original_sha256` | Source Fingerprint | Text |

## AI and search readiness

Consistent matter IDs, document types, dates, and transaction states allow Microsoft Search and permission-aware Copilot experiences to filter and retrieve content more reliably. AI readiness also requires correct permissions, sensitivity/retention controls, successful indexing, and representative search validation; metadata alone does not guarantee answer quality.

