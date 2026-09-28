"""Read-only, byte-level inventory of the external literature corpus (M4-WP0, ruling §4).

The corpus lives outside the repository, at the path configured as
`literature_corpus_root` in the untracked `config/local_paths.yaml`. Nothing
from it is copied in. What enters the repository is a manifest: for every file
a stable id, its relative path, basename, extension, size, SHA-256, duplicate
group and accessibility status.

The read boundary, enforced in code
-----------------------------------

The ruling's boundary is

    No document content parsing, text extraction, PDF rendering, metadata
    extraction, or semantic inspection. Byte-level access for hashing and
    inventory operations only.

so **exactly one function in this module opens a corpus file**:
`_open_corpus_bytes`, which refuses every mode except `"rb"`. Its only caller,
`hash_corpus_file`, streams the bytes into SHA-256 and a byte counter and
discards them. This module imports no JSON, text, PDF or archive library, never
decodes bytes, and never reads a file's name for meaning --- a test checks the
source for each of those. The files are JSON; that fact is known from their
extension and is never confirmed by looking.

Stable ids
----------

`LIT-000001`, ... are assigned by sorting the relative paths (POSIX form,
code-point order) --- **once**. The first run writes the manifest. Every later
run re-walks the folder, re-hashes every file, and **verifies** against the
frozen manifest without rewriting it: if the set of paths has changed, or any
file's bytes have, it raises `CorpusChangedError` naming what differs. Ids are
never re-assigned silently. Re-freezing a changed corpus is a decision, made by
deleting the manifest in a commit that says why.

What is skipped
---------------

A symbolic link (to a file or a directory) is never followed and never opened:
it is inventoried with `accessibility: skipped`. So is anything that is not a
regular file. An archive (`.zip`, `.tar`, `.gz`, ...) is a regular file and is
hashed as bytes, but is marked `skipped` because it is not expanded. A file
that cannot be opened is `unreadable`. Any entry that is not `ok` is a finding
to report, not to repair.
"""

from __future__ import annotations

import hashlib
import os
import stat
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

CONFIG_KEY = "literature_corpus_root"
CONFIG_REFERENCE = "config/local_paths.yaml:literature_corpus_root"
CHUNK_SIZE = 1024 * 1024
ID_PREFIX = "LIT-"
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar"}

READ_POLICY = (
    "Byte-level reads only, for SHA-256 and size. No file is decoded, parsed, "
    "rendered or inspected; no filename is read for meaning. Symlinks are not "
    "followed; archives are not expanded."
)
ID_RULE = (
    "LIT-NNNNNN assigned once, in code-point order of the POSIX relative path; "
    "frozen thereafter. A re-run verifies against the frozen manifest and fails "
    "if the path set or any file's bytes changed."
)

ENTRY_FIELDS = (
    "item_id",
    "relative_path",
    "basename",
    "extension",
    "bytes",
    "sha256",
    "duplicate_group",
    "accessibility",
    "skip_reason",
    "inventory_utc",
    "config_reference",
)


class CorpusReadRefused(PermissionError):
    """Something asked to open a corpus file other than as raw bytes."""


class CorpusChangedError(RuntimeError):
    """The corpus no longer matches its frozen manifest."""


def _open_corpus_bytes(path: Path, mode: str = "rb"):
    """The only place a corpus file is opened. Raw bytes, or nothing."""
    if mode != "rb":
        raise CorpusReadRefused(
            f"corpus files may be opened only as raw bytes ('rb'), not {mode!r}"
        )
    return open(path, mode)  # noqa: SIM115 -- the caller closes it


def hash_corpus_file(path: Path, chunk_size: int = CHUNK_SIZE) -> tuple[str, int]:
    """(SHA-256, byte count) of one regular file. The bytes are discarded."""
    digest = hashlib.sha256()
    n = 0
    with _open_corpus_bytes(path, "rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
            n += len(chunk)
    return digest.hexdigest(), n


def _classify_entry(path: Path) -> tuple[str, str | None]:
    """('ok' | 'skipped' | 'unreadable', reason) from lstat alone --- no open."""
    try:
        st = os.lstat(path)
    except OSError as exc:
        return "unreadable", f"lstat failed: {type(exc).__name__}"
    if stat.S_ISLNK(st.st_mode):
        return "skipped", "symbolic link: not followed"
    if stat.S_ISDIR(st.st_mode):
        return "skipped", "directory"
    if not stat.S_ISREG(st.st_mode):
        return "skipped", "not a regular file"
    if path.suffix.lower() in ARCHIVE_EXTENSIONS:
        return "skipped", "archive: hashed as bytes, not expanded"
    return "ok", None


def walk(root: Path) -> list[tuple[str, Path]]:
    """Every entry under `root` as (POSIX relative path, path), sorted. No link followed.

    Symlinked directories appear as entries themselves and are not descended.
    """
    root = Path(root)
    found: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        here = Path(dirpath)
        for name in list(dirnames):
            if (here / name).is_symlink():
                dirnames.remove(name)
                found.append((str(PurePosixPath((here / name).relative_to(root))), here / name))
        for name in filenames:
            found.append((str(PurePosixPath((here / name).relative_to(root))), here / name))
    found.sort(key=lambda item: item[0])
    return found


def scan(root: Path) -> list[dict]:
    """Walk and hash. Entries in sorted-path order, without ids or timestamps."""
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise NotADirectoryError("the configured corpus root is not a real directory")
    entries = []
    for rel, path in walk(root):
        accessibility, reason = _classify_entry(path)
        sha, size = None, None
        if accessibility == "ok" or (reason or "").startswith("archive"):
            try:
                sha, size = hash_corpus_file(path)
            except OSError as exc:
                accessibility, reason = "unreadable", f"open failed: {type(exc).__name__}"
        entries.append(
            {
                "relative_path": rel,
                "basename": PurePosixPath(rel).name,
                "extension": PurePosixPath(rel).suffix,
                "bytes": size,
                "sha256": sha,
                "accessibility": accessibility,
                "skip_reason": reason,
            }
        )
    return entries


def assign_ids_and_duplicates(entries: list[dict], inventory_utc: str) -> list[dict]:
    """Stable ids by position in sorted-path order; DUP-NNNN groups by first member."""
    out = []
    for k, entry in enumerate(entries, start=1):
        out.append({"item_id": f"{ID_PREFIX}{k:06d}", **entry})
    members: dict[str, list[str]] = defaultdict(list)
    for entry in out:
        if entry["sha256"] is not None:
            members[entry["sha256"]].append(entry["item_id"])
    groups = sorted((ids for ids in members.values() if len(ids) > 1), key=lambda ids: ids[0])
    label = {item: f"DUP-{g:04d}" for g, ids in enumerate(groups, start=1) for item in ids}
    return [
        {
            field: (
                label.get(entry["item_id"]) if field == "duplicate_group"
                else inventory_utc if field == "inventory_utc"
                else CONFIG_REFERENCE if field == "config_reference"
                else entry[field]
            )
            for field in ENTRY_FIELDS
        }
        for entry in out
    ]


def content_identity(entries: list[dict]) -> str:
    """SHA-256 of `relative_path \\t sha256 \\t bytes \\n` per entry, in id order.

    Independent of timestamps and of JSON formatting, so anyone holding the
    folder can recompute it. The manifest file's own SHA-256 pins the frozen
    record; this pins the folder.
    """
    digest = hashlib.sha256()
    for e in entries:
        digest.update(f"{e['relative_path']}\t{e['sha256']}\t{e['bytes']}\n".encode("utf-8"))
    return digest.hexdigest()


def summarize(entries: list[dict]) -> dict:
    sizes = sorted(e["bytes"] for e in entries if e["bytes"] is not None)
    dup: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        if e["duplicate_group"]:
            dup[e["duplicate_group"]].append(e)
    groups = [
        {
            "duplicate_group": g,
            "sha256": members[0]["sha256"],
            "bytes": members[0]["bytes"],
            "n_members": len(members),
            "item_ids": [m["item_id"] for m in members],
        }
        for g, members in sorted(dup.items())
    ]
    median = None
    if sizes:
        mid = len(sizes) // 2
        median = sizes[mid] if len(sizes) % 2 else (sizes[mid - 1] + sizes[mid]) / 2
    return {
        "n_entries": len(entries),
        "by_accessibility": dict(sorted(Counter(e["accessibility"] for e in entries).items())),
        "by_extension": dict(sorted(Counter(e["extension"] for e in entries).items())),
        "total_bytes": sum(sizes),
        "min_bytes": sizes[0] if sizes else None,
        "median_bytes": median,
        "max_bytes": sizes[-1] if sizes else None,
        "n_zero_byte": sum(1 for s in sizes if s == 0),
        "zero_byte_item_ids": [e["item_id"] for e in entries if e["bytes"] == 0],
        "n_unique_sha256": len({e["sha256"] for e in entries if e["sha256"]}),
        "n_duplicate_groups": len(groups),
        "n_items_in_duplicate_groups": sum(g["n_members"] for g in groups),
        "n_redundant_copies": sum(g["n_members"] - 1 for g in groups),
        "duplicate_groups": groups,
    }


def verify_against_frozen(fresh: list[dict], frozen_entries: list[dict]) -> None:
    """Raise CorpusChangedError unless path set, sizes and hashes all match."""
    old = {e["relative_path"]: e for e in frozen_entries}
    new = {e["relative_path"]: e for e in fresh}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(
        p for p in set(old) & set(new)
        if (old[p]["sha256"], old[p]["bytes"], old[p]["accessibility"])
        != (new[p]["sha256"], new[p]["bytes"], new[p]["accessibility"])
    )
    if added or removed or changed:
        raise CorpusChangedError(
            "The corpus no longer matches its frozen manifest: "
            f"{len(added)} path(s) added, {len(removed)} removed, {len(changed)} changed "
            f"(first: added {added[:3]}, removed {removed[:3]}, changed {changed[:3]}). "
            "Ids are not re-assigned. Stop and escalate."
        )
