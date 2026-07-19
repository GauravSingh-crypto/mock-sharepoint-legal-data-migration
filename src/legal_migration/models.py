"""Domain records shared by migration stages."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SourceFile:
    source_id: str
    source_path: str
    filename: str
    extension: str
    size_bytes: int
    path_length: int
    directory_depth: int
    sha256: str

    def as_dict(self):
        return asdict(self)


@dataclass
class MigrationRecord:
    source_id: str
    source_path: str
    original_filename: str
    client_name: Optional[str]
    matter_id: Optional[str]
    matter_name: Optional[str]
    document_date: Optional[str]
    sender_name: Optional[str]
    document_type: Optional[str]
    attempt_number: Optional[int]
    attempt_status: Optional[str]
    original_sha256: str
    parsing_confidence: float
    destination_path: Optional[str]
    validation_status: str
    validation_message: str

    def as_dict(self):
        return asdict(self)

