"""Read-only source discovery and fingerprinting."""
from hashlib import sha256
from pathlib import Path
from .models import SourceFile


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover(source_root: Path) -> list[SourceFile]:
    records = []
    for path in sorted(item for item in source_root.rglob("*") if item.is_file()):
        relative = path.relative_to(source_root)
        digest = file_hash(path)
        records.append(SourceFile(
            source_id=digest[:16] + f"-{len(records):04d}",
            source_path=relative.as_posix(),
            filename=path.name,
            extension=path.suffix.lower(),
            size_bytes=path.stat().st_size,
            path_length=len(relative.as_posix()),
            directory_depth=len(relative.parts) - 1,
            sha256=digest,
        ))
    return records

