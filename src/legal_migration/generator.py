"""Generate deterministic, synthetic legal document fixtures."""
from pathlib import Path
import shutil


CLIENTS = [
    ("Acme Corporation", "MAT-0042", "Acquisition of Example Holdings"),
    ("Northstar Ventures", "MAT-0081", "Series B Investment"),
    ("Blue River Energy", "MAT-0107", "Asset Purchase"),
]
DOCUMENTS = [
    ("2025-03-18", "Jane-Smith", "Agreement", "Revised-Purchase-Agreement.pdf"),
    ("2025-03-19", "Robert-Lee", "Correspondence", "Counterparty-Comments.docx"),
    ("2025-03-20", "Maria-Garcia", "Financial", "Closing-Funds.xlsx"),
    ("2025-03-21", "Jane-Smith", "Court-Filing", "Regulatory-Submission.pdf"),
]


def _write_mock(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_dataset(source_root: Path) -> int:
    """Create a reproducible hierarchy containing clean and problematic cases."""
    if source_root.exists():
        shutil.rmtree(source_root)
    count = 0
    for client_index, (client, matter_id, matter) in enumerate(CLIENTS, start=1):
        for attempt, status in ((1, "Completed"), (2, "Failed")):
            for date, sender, document_type, description in DOCUMENTS:
                filename = f"{date}__{sender}__{document_type}__{description}"
                folder = source_root / "Clients" / client / f"{matter_id} - {matter}" / f"Attempt {attempt:02d} - {status}"
                _write_mock(folder / filename, f"SYNTHETIC LEGAL DOCUMENT\n{client}\n{matter_id}\n{filename}\n")
                count += 1

    # Deliberate long path: context must move to metadata during flattening.
    long_context = "Historical Due Diligence Materials " + ("and Supporting Evidence " * 3).strip()
    long_folder = source_root / "Clients" / CLIENTS[0][0] / f"{CLIENTS[0][1]} - {CLIENTS[0][2]}" / "Attempt 03 - Active" / long_context / long_context / long_context
    _write_mock(long_folder / "2025-04-01__Alex-Johnson__Agreement__Extremely-Long-Transaction-Agreement-With-Schedules-and-Exhibits.pdf", "SYNTHETIC LONG PATH DOCUMENT\n")
    count += 1

    # Invalid SharePoint characters and a destination collision after sanitizing.
    problem_folder = source_root / "Clients" / CLIENTS[1][0] / f"{CLIENTS[1][1]} - {CLIENTS[1][2]}" / "Attempt 03 - Active"
    _write_mock(problem_folder / "2025-04-02__Sam-Wilson__Correspondence__Question:Answer?.pdf", "SYNTHETIC INVALID NAME A\n")
    _write_mock(problem_folder / "2025-04-02__Sam-Wilson__Correspondence__Question-Answer-.pdf", "SYNTHETIC INVALID NAME B\n")
    count += 2

    # Missing sender is routed to manual review; unparseable file is blocked.
    review_folder = source_root / "Clients" / CLIENTS[2][0] / f"{CLIENTS[2][1]} - {CLIENTS[2][2]}" / "Attempt 01 - Completed"
    _write_mock(review_folder / "2025-04-03____Agreement__Executed-Asset-Purchase-Agreement.pdf", "SYNTHETIC MISSING SENDER\n")
    _write_mock(review_folder / "miscellaneous-document.pdf", "SYNTHETIC UNPARSEABLE DOCUMENT\n")
    count += 2

    # Zero-byte and unsupported files are audit exceptions.
    (review_folder / "2025-04-04__Taylor-Kim__Agreement__Empty-Document.pdf").touch()
    _write_mock(review_folder / "2025-04-05__Taylor-Kim__Archive__Legacy-Export.zip", "SYNTHETIC ARCHIVE\n")
    count += 2
    return count

