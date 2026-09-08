"""Checksum helpers: correctness, streaming behaviour, and size reporting."""

from __future__ import annotations

import hashlib

import pytest

from climrr.checksums import byte_size, file_fingerprint, sha256_file


def test_sha256_matches_hashlib(tiny_csv):
    expected = hashlib.sha256(tiny_csv.read_bytes()).hexdigest()
    assert sha256_file(tiny_csv) == expected


def test_sha256_is_chunk_size_invariant(tiny_csv):
    """A streaming digest must not depend on how the stream was chunked."""
    whole = sha256_file(tiny_csv)
    assert sha256_file(tiny_csv, chunk_size=1) == whole
    assert sha256_file(tiny_csv, chunk_size=7) == whole
    assert sha256_file(tiny_csv, chunk_size=1 << 20) == whole


def test_sha256_of_empty_file(tmp_path):
    empty = tmp_path / "empty.bin"
    empty.write_bytes(b"")
    assert sha256_file(empty) == hashlib.sha256(b"").hexdigest()
    assert byte_size(empty) == 0


def test_single_byte_change_changes_digest(tmp_path, tiny_csv):
    altered = tmp_path / "altered.csv"
    altered.write_bytes(tiny_csv.read_bytes().replace(b"12.5", b"12.6"))
    assert sha256_file(altered) != sha256_file(tiny_csv)


def test_byte_size(tiny_csv):
    assert byte_size(tiny_csv) == len(tiny_csv.read_bytes())


def test_file_fingerprint_shape(tiny_csv):
    fp = file_fingerprint(tiny_csv)
    assert set(fp) == {"sha256", "bytes"}
    assert fp["sha256"] == sha256_file(tiny_csv)
    assert fp["bytes"] == byte_size(tiny_csv)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        sha256_file(tmp_path / "does_not_exist.csv")
