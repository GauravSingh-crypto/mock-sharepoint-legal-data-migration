"""Orchestrate and report the complete demonstration."""
from pathlib import Path
import json
import shutil
from .database import initialize, save_inventory, save_normalized, export_csv, query_dicts
from .discovery import discover
from .generator import generate_dataset
from .migrator import migrate
from .parser import parse
from .planner import plan


def run_pipeline(work_root: Path, reset: bool = True) -> dict:
    if reset and work_root.exists():
        shutil.rmtree(work_root)
    source_root = work_root / "sample_data" / "legacy_share"
    destination_root = work_root / "sample_data" / "sharepoint_simulation"
    reports = work_root / "output"
    reports.mkdir(parents=True, exist_ok=True)

    generated_count = generate_dataset(source_root)
    inventory = discover(source_root)
    normalized = plan([parse(record) for record in inventory])

    connection = initialize(work_root / "migration.db")
    save_inventory(connection, inventory)
    save_normalized(connection, normalized)
    migrate(connection, source_root, destination_root, normalized)

    source_rows = [record.as_dict() for record in inventory]
    normalized_rows = [record.as_dict() for record in normalized]
    exception_rows = [row for row in normalized_rows if row["validation_status"] != "READY"]
    migration_rows = query_dicts(connection, "SELECT * FROM migration_results ORDER BY source_id")
    reconciliation_rows = query_dicts(connection, """
        SELECT n.source_id, n.source_path, n.destination_path, n.original_sha256,
               m.destination_sha256, m.migration_status, m.integrity_status
        FROM normalized_documents n JOIN migration_results m USING (source_id)
        ORDER BY n.source_path
    """)
    export_csv(reports / "source_inventory.csv", source_rows)
    export_csv(reports / "normalized_metadata.csv", normalized_rows)
    export_csv(reports / "exceptions.csv", exception_rows, list(normalized_rows[0]))
    export_csv(reports / "migration_results.csv", migration_rows)
    export_csv(reports / "reconciliation.csv", reconciliation_rows)

    summary = query_dicts(connection, """
        SELECT
          (SELECT COUNT(*) FROM source_inventory) AS files_discovered,
          (SELECT COUNT(*) FROM source_inventory WHERE path_length > 400) AS paths_over_400,
          (SELECT MAX(path_length) FROM source_inventory) AS maximum_source_path,
          (SELECT COUNT(*) FROM normalized_documents WHERE validation_status = 'READY') AS ready,
          (SELECT COUNT(*) FROM normalized_documents WHERE validation_status = 'REVIEW_REQUIRED') AS review_required,
          (SELECT COUNT(*) FROM normalized_documents WHERE validation_status = 'BLOCKED') AS blocked,
          (SELECT COUNT(*) FROM migration_results WHERE migration_status = 'MIGRATED') AS migrated,
          (SELECT COUNT(*) FROM migration_results WHERE integrity_status = 'MISMATCH') AS checksum_mismatches,
          (SELECT MAX(LENGTH(destination_path)) FROM normalized_documents) AS maximum_destination_path
    """)[0]
    summary["generated_count"] = generated_count
    (reports / "audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    markdown = "\n".join([
        "# Demo migration summary",
        "",
        f"- Files discovered: {summary['files_discovered']}",
        f"- Source paths over 400 characters: {summary['paths_over_400']}",
        f"- Maximum source path length: {summary['maximum_source_path']}",
        f"- Automatically approved: {summary['ready']}",
        f"- Manual review required: {summary['review_required']}",
        f"- Blocked: {summary['blocked']}",
        f"- Successfully migrated: {summary['migrated']}",
        f"- Checksum mismatches: {summary['checksum_mismatches']}",
        f"- Maximum planned destination path: {summary['maximum_destination_path']}",
    ])
    (reports / "demo_summary.md").write_text(markdown + "\n", encoding="utf-8")
    connection.close()
    return {"summary": summary, "summary_markdown": markdown, "work_root": work_root}

