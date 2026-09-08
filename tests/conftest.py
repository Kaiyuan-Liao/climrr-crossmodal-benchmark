"""Shared fixtures. Tests never touch the real data file."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

# A tiny synthetic table. The leading zeros in the id column are deliberate:
# they are the property that must survive being read as text.
TINY_CSV = (
    "geoid,name,value_hist\n"
    "01001,Alpha,12.5\n"
    "01003,Beta,13.0\n"
    "06075,Gamma,9.25\n"
)


@pytest.fixture
def tiny_csv(tmp_path: Path) -> Path:
    path = tmp_path / "tiny.csv"
    path.write_text(TINY_CSV, encoding="utf-8", newline="")
    return path


@pytest.fixture
def tiny_manifest(tmp_path: Path, tiny_csv: Path) -> Path:
    import json

    from climrr.checksums import byte_size, sha256_file

    manifest = {
        "manifest_version": 1,
        "files": [
            {
                "filename": "tiny.csv",
                "path": "tiny.csv",
                "sha256": sha256_file(tiny_csv),
                "bytes": byte_size(tiny_csv),
                "row_count": 3,
                "column_count": 3,
            }
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
