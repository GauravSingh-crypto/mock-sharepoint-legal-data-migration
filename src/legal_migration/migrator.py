"""Local SharePoint-library simulation and checksum reconciliation."""
from pathlib import Path
import shutil
import sqlite3
from .discovery import file_hash
from .models import MigrationRecord


def migrate(connection: sqlite3.Connection, source_root: Path, destination_root: Path, records: list[MigrationRecord]) -> None:
    destination_root.mkdir(parents=True, exist_ok=True)
    for record in records:
        if record.validation_status != "READY" or not record.destination_path:
            connection.execute(
                "INSERT INTO migration_results VALUES (?, ?, ?, ?, ?, ?)",
                (record.source_id, "SKIPPED", record.destination_path, None, "NOT_APPLICABLE", record.validation_message),
            )
            continue
        try:
            source = source_root / record.source_path
            destination = destination_root / record.destination_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            destination_hash = file_hash(destination)
            integrity = "MATCH" if destination_hash == record.original_sha256 else "MISMATCH"
            connection.execute(
                "INSERT INTO migration_results VALUES (?, ?, ?, ?, ?, ?)",
                (record.source_id, "MIGRATED", record.destination_path, destination_hash, integrity, None),
            )
        except OSError as error:
            connection.execute(
                "INSERT INTO migration_results VALUES (?, ?, ?, ?, ?, ?)",
                (record.source_id, "FAILED", record.destination_path, None, "NOT_VERIFIED", str(error)),
            )
    connection.commit()

