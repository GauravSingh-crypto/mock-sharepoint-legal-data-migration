from pathlib import Path
from tempfile import TemporaryDirectory
import csv
import json
import sqlite3
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from legal_migration.discovery import discover
from legal_migration.generator import generate_dataset
from legal_migration.parser import parse
from legal_migration.pipeline import run_pipeline
from legal_migration.planner import plan, sanitize


class MetadataParsingTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.source = Path(self.temp.name) / "source"
        generate_dataset(self.source)
        self.inventory = discover(self.source)

    def tearDown(self):
        self.temp.cleanup()

    def test_extracts_filename_and_folder_metadata(self):
        source = next(row for row in self.inventory if "Revised-Purchase-Agreement.pdf" in row.filename)
        record = parse(source)
        self.assertEqual(record.client_name, "Acme Corporation")
        self.assertEqual(record.matter_id, "MAT-0042")
        self.assertEqual(record.document_date, "2025-03-18")
        self.assertEqual(record.sender_name, "Jane Smith")
        self.assertEqual(record.document_type, "Agreement")
        self.assertEqual(record.validation_status, "READY")

    def test_missing_sender_requires_review(self):
        source = next(row for row in self.inventory if "Executed-Asset" in row.filename)
        record = parse(source)
        self.assertEqual(record.validation_status, "REVIEW_REQUIRED")
        self.assertIn("sender missing", record.validation_message)

    def test_unparseable_unsupported_and_empty_are_blocked(self):
        selected = [row for row in self.inventory if row.filename == "miscellaneous-document.pdf" or row.extension == ".zip" or row.size_bytes == 0]
        self.assertEqual(len(selected), 3)
        self.assertTrue(all(parse(row).validation_status == "BLOCKED" for row in selected))

    def test_dataset_contains_real_path_limit_case(self):
        self.assertGreater(max(row.path_length for row in self.inventory), 400)


class DestinationPlanningTests(unittest.TestCase):
    def test_sanitize_removes_sharepoint_invalid_characters(self):
        self.assertEqual(sanitize('Question: "Answer"? #1'), "Question-Answer-1")

    def test_all_ready_destinations_are_shallow_safe_and_unique(self):
        with TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            generate_dataset(source)
            records = plan([parse(row) for row in discover(source)])
            ready = [row for row in records if row.validation_status == "READY"]
            destinations = [row.destination_path for row in ready]
            self.assertTrue(all(path is not None and len(path) <= 240 for path in destinations))
            self.assertTrue(all(len(Path(path).parts) == 3 for path in destinations))
            self.assertEqual(len(destinations), len({path.casefold() for path in destinations}))
            self.assertTrue(any(path.endswith(".pdf") and "Question-Answer" in path for path in destinations))


class EndToEndTests(unittest.TestCase):
    def test_pipeline_outputs_and_reconciliation(self):
        with TemporaryDirectory() as temp:
            result = run_pipeline(Path(temp) / "work")
            summary = result["summary"]
            output = result["work_root"] / "output"
            self.assertEqual(summary["files_discovered"], summary["generated_count"])
            self.assertGreater(summary["paths_over_400"], 0)
            self.assertGreater(summary["review_required"], 0)
            self.assertGreater(summary["blocked"], 0)
            self.assertEqual(summary["migrated"], summary["ready"])
            self.assertEqual(summary["checksum_mismatches"], 0)
            self.assertLessEqual(summary["maximum_destination_path"], 240)
            expected = {
                "audit_summary.json", "source_inventory.csv", "normalized_metadata.csv",
                "exceptions.csv", "migration_results.csv", "reconciliation.csv", "demo_summary.md",
            }
            self.assertTrue(expected.issubset({item.name for item in output.iterdir()}))

            with (output / "reconciliation.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            migrated = [row for row in rows if row["migration_status"] == "MIGRATED"]
            self.assertTrue(all(row["integrity_status"] == "MATCH" for row in migrated))

            database = sqlite3.connect(result["work_root"] / "migration.db")
            duplicate_count = database.execute("""
                SELECT COUNT(*) FROM (
                  SELECT LOWER(destination_path), COUNT(*)
                  FROM normalized_documents
                  WHERE destination_path IS NOT NULL
                  GROUP BY LOWER(destination_path) HAVING COUNT(*) > 1
                )
            """).fetchone()[0]
            database.close()
            self.assertEqual(duplicate_count, 0)


if __name__ == "__main__":
    unittest.main()

