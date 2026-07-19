"""SQLite control database and CSV exports."""
from __future__ import annotations
from dataclasses import fields
from pathlib import Path
import csv
import sqlite3
from .models import SourceFile, MigrationRecord


SCHEMA = """
CREATE TABLE source_inventory (
  source_id TEXT PRIMARY KEY, source_path TEXT, filename TEXT, extension TEXT,
  size_bytes INTEGER, path_length INTEGER, directory_depth INTEGER, sha256 TEXT
);
CREATE TABLE normalized_documents (
  source_id TEXT PRIMARY KEY, source_path TEXT, original_filename TEXT,
  client_name TEXT, matter_id TEXT, matter_name TEXT, document_date TEXT,
  sender_name TEXT, document_type TEXT, attempt_number INTEGER,
  attempt_status TEXT, original_sha256 TEXT, parsing_confidence REAL,
  destination_path TEXT, validation_status TEXT, validation_message TEXT
);
CREATE TABLE migration_results (
  source_id TEXT PRIMARY KEY, migration_status TEXT, destination_path TEXT,
  destination_sha256 TEXT, integrity_status TEXT, error_message TEXT
);
"""


def initialize(path: Path) -> sqlite3.Connection:
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    return connection


def save_inventory(connection: sqlite3.Connection, records: list[SourceFile]) -> None:
    names = [field.name for field in fields(SourceFile)]
    connection.executemany(
        f"INSERT INTO source_inventory ({','.join(names)}) VALUES ({','.join('?' for _ in names)})",
        [[getattr(record, name) for name in names] for record in records],
    )
    connection.commit()


def save_normalized(connection: sqlite3.Connection, records: list[MigrationRecord]) -> None:
    names = [field.name for field in fields(MigrationRecord)]
    connection.executemany(
        f"INSERT INTO normalized_documents ({','.join(names)}) VALUES ({','.join('?' for _ in names)})",
        [[getattr(record, name) for name in names] for record in records],
    )
    connection.commit()


def export_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)


def query_dicts(connection: sqlite3.Connection, sql: str) -> list[dict]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(sql)]
