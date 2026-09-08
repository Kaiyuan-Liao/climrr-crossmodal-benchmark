"""Streaming SHA-256 and byte size for files of arbitrary size."""

from __future__ import annotations

import hashlib
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path | str, chunk_size: int = CHUNK_SIZE) -> str:
    """Return the lowercase hex SHA-256 of a file, read in streaming chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def byte_size(path: Path | str) -> int:
    """Return the size of a file in bytes."""
    return Path(path).stat().st_size


def file_fingerprint(path: Path | str, chunk_size: int = CHUNK_SIZE) -> dict:
    """Return {'sha256': ..., 'bytes': ...} for a file."""
    return {"sha256": sha256_file(path, chunk_size=chunk_size), "bytes": byte_size(path)}
