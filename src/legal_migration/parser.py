"""Extract and normalize legal metadata from paths and filenames."""
from pathlib import PurePosixPath
import re
from .models import SourceFile, MigrationRecord

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MATTER_PATTERN = re.compile(r"^(?P<id>MAT-\d{4})\s+-\s+(?P<name>.+)$")
ATTEMPT_PATTERN = re.compile(r"^Attempt\s+(?P<number>\d+)\s+-\s+(?P<status>Active|Failed|Completed)$", re.I)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx"}


def _title(value: str) -> str:
    return re.sub(r"[-_]+", " ", value).strip().title()


def parse(record: SourceFile) -> MigrationRecord:
    parts = PurePosixPath(record.source_path).parts
    client = parts[1] if len(parts) > 1 and parts[0] == "Clients" else None
    matter_match = next((MATTER_PATTERN.match(part) for part in parts if MATTER_PATTERN.match(part)), None)
    attempt_match = next((ATTEMPT_PATTERN.match(part) for part in parts if ATTEMPT_PATTERN.match(part)), None)
    filename_parts = PurePosixPath(record.filename).stem.split("__", 3)
    filename_match = (
        filename_parts
        if len(filename_parts) == 4
        and DATE_PATTERN.match(filename_parts[0])
        and filename_parts[2]
        and filename_parts[3]
        else None
    )

    matter_id = matter_match.group("id") if matter_match else None
    matter_name = matter_match.group("name") if matter_match else None
    attempt_number = int(attempt_match.group("number")) if attempt_match else None
    attempt_status = attempt_match.group("status").title() if attempt_match else None
    document_date = filename_match[0] if filename_match else None
    sender = _title(filename_match[1]) if filename_match and filename_match[1] else None
    document_type = _title(filename_match[2]) if filename_match else None

    score = sum((
        0.15 if client else 0,
        0.20 if matter_id else 0,
        0.15 if attempt_number is not None else 0,
        0.15 if document_date else 0,
        0.10 if sender else 0,
        0.15 if document_type else 0,
        0.10 if record.extension in ALLOWED_EXTENSIONS else 0,
    ))
    reasons = []
    if not filename_match:
        reasons.append("filename pattern not recognized")
    if not sender:
        reasons.append("sender missing")
    if record.extension not in ALLOWED_EXTENSIONS:
        reasons.append("unsupported extension")
    if record.size_bytes == 0:
        reasons.append("zero-byte file")
    if not matter_id:
        reasons.append("matter ID missing")

    if not filename_match or record.size_bytes == 0 or record.extension not in ALLOWED_EXTENSIONS or score < 0.60:
        status = "BLOCKED"
    elif not sender or score < 0.85:
        status = "REVIEW_REQUIRED"
    else:
        status = "READY"

    return MigrationRecord(
        source_id=record.source_id,
        source_path=record.source_path,
        original_filename=record.filename,
        client_name=client,
        matter_id=matter_id,
        matter_name=matter_name,
        document_date=document_date,
        sender_name=sender,
        document_type=document_type,
        attempt_number=attempt_number,
        attempt_status=attempt_status,
        original_sha256=record.sha256,
        parsing_confidence=round(score, 2),
        destination_path=None,
        validation_status=status,
        validation_message="; ".join(reasons) if reasons else "validated",
    )
