# Application-answer evidence

Use these as descriptions of this portfolio demonstration, not as claims about an unperformed client engagement.

## Metadata extraction and custom columns

In a SharePoint legal-data migration demonstration, I built a Python pipeline that inventories legacy files, parses configurable filename and folder conventions, and extracts dates, senders, matter identifiers, document types, and transaction states. It normalizes those values into a migration control table and a CSV manifest designed for SharePoint custom columns. Each record receives a confidence score; ambiguous metadata is routed to manual review rather than uploaded silently. The framework preserves the original path and SHA-256 fingerprint for traceability and post-migration reconciliation.

## Irregular hierarchy and 400-character path limit

I modeled deeply nested client, matter, transaction-attempt, and correspondence folders, including paths over 400 characters. The planner flattens them to a shallow `Legal Matters/<Matter ID>/<short document name>` layout and moves the removed folder context into structured metadata. It sanitizes unsupported characters, enforces a conservative destination-path limit, and resolves collisions with stable source-derived suffixes. The original path remains a metadata field, and checksum reconciliation verifies that flattening did not alter file contents.

