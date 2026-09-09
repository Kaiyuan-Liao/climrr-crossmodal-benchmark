"""Fail-closed verification of a data file against `data/manifest.json`.

D-005 moved the pin on the raw bytes from the commit SHA to the manifest hash,
and D-006 made that permanent. The consequence is this module: **no script may
read the raw table before its SHA-256 has been checked against the manifest**,
and a missing or mismatched file must fail rather than skip.

If a recomputed hash ever differs from the manifest, that is a defect to
escalate --- never a manifest to update.
"""

from __future__ import annotations

import json
from pathlib import Path

from climrr.checksums import byte_size, sha256_file
from climrr.paths import REPO_ROOT

MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"


class ManifestMismatchError(RuntimeError):
    """Raised when a file's bytes do not match the manifest entry pinning them."""


def load_entry(filename: str, manifest_path: Path | str | None = None) -> dict:
    path = Path(manifest_path) if manifest_path is not None else MANIFEST_PATH
    with path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    for entry in manifest.get("files", []):
        if entry.get("filename") == filename:
            return entry
    raise KeyError(f"No manifest entry for '{filename}' in {path}")


def verify_file(
    data_path: Path | str,
    manifest_path: Path | str | None = None,
) -> dict:
    """Verify one file against its manifest entry, or raise.

    Returns `{'sha256': ..., 'bytes': ...}` for the verified file so the caller
    can record the values it actually read rather than the ones it expected.
    """
    data_path = Path(data_path)
    entry = load_entry(data_path.name, manifest_path)

    if not data_path.is_file():
        raise ManifestMismatchError(
            f"Required data file is absent: {data_path.name}\n"
            "It is pinned by SHA-256 in data/manifest.json and transferred out of "
            "band (D-005). Verification fails closed rather than skipping."
        )

    observed_sha = sha256_file(data_path)
    observed_bytes = byte_size(data_path)
    problems = []
    if observed_sha != entry.get("sha256"):
        problems.append(f"sha256: manifest {entry.get('sha256')!r}, observed {observed_sha!r}")
    if observed_bytes != entry.get("bytes"):
        problems.append(f"bytes: manifest {entry.get('bytes')!r}, observed {observed_bytes!r}")
    if problems:
        raise ManifestMismatchError(
            f"{data_path.name} does not match data/manifest.json:\n  "
            + "\n  ".join(problems)
            + "\nStop. This is a defect to escalate, not a manifest to update."
        )
    return {"sha256": observed_sha, "bytes": observed_bytes}
