"""Create shallow, deterministic, SharePoint-safe destinations."""
from hashlib import sha256
from pathlib import PurePosixPath
import re
from .models import MigrationRecord

INVALID = re.compile(r'["*:<>?/\\|#%]')
MULTI_SEPARATOR = re.compile(r"[-_ ]+")


def sanitize(value: str, limit: int = 80) -> str:
    value = INVALID.sub("-", value)
    value = MULTI_SEPARATOR.sub("-", value).strip("-. ")
    return value[:limit].rstrip("-. ") or "Document"


def plan(records: list[MigrationRecord], max_path: int = 240) -> list[MigrationRecord]:
    destinations: dict[str, str] = {}
    for record in records:
        if record.validation_status != "READY":
            continue
        original = PurePosixPath(record.original_filename)
        match_description = re.match(r"^\d{4}-\d{2}-\d{2}__[^_]*__[^_]+__(.+)\.[^.]+$", original.name)
        description = match_description.group(1) if match_description else original.stem
        short_name = sanitize(description, 72)
        attempt = f"ATT{record.attempt_number:02d}" if record.attempt_number is not None else "ATT00"
        filename = f"{record.document_date}_{short_name}_{attempt}{original.suffix.lower()}"
        destination = PurePosixPath("Legal Matters", record.matter_id or "UNASSIGNED", filename).as_posix()
        key = destination.casefold()
        if key in destinations and destinations[key] != record.source_id:
            suffix = sha256(record.source_path.encode("utf-8")).hexdigest()[:6].upper()
            destination = PurePosixPath(destination).with_stem(PurePosixPath(destination).stem + "_" + suffix).as_posix()
            key = destination.casefold()
        if len(destination) > max_path:
            suffix = sha256(record.source_path.encode("utf-8")).hexdigest()[:8].upper()
            filename = f"{record.document_date}_Document_{attempt}_{suffix}{original.suffix.lower()}"
            destination = PurePosixPath("Legal Matters", record.matter_id or "UNASSIGNED", filename).as_posix()
            key = destination.casefold()
        if len(destination) > max_path:
            record.validation_status = "BLOCKED"
            record.validation_message = "planned destination exceeds safe path limit"
            continue
        record.destination_path = destination
        destinations[key] = record.source_id
    return records

