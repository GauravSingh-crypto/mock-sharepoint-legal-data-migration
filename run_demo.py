#!/usr/bin/env python3
"""Run the complete local SharePoint migration simulation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from legal_migration.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline(ROOT / "work", reset=True)
    print(result["summary_markdown"])

