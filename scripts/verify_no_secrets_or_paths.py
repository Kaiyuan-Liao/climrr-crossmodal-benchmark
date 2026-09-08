#!/usr/bin/env python3
"""Pre-commit guard: no absolute machine paths and no credential-shaped strings
may enter tracked files.

Scans every file Git tracks (plus, with --staged, anything staged) for the
forbidden patterns. Absolute paths belong only in the untracked
`config/local_paths.yaml`; the tracked example file uses <PLACEHOLDER> tokens.

This script is excluded from its own scan: it necessarily contains the literal
patterns it searches for. It is the only self-exempt file, and it contains no
real path or credential -- read it to confirm.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

# Patterns are assembled from fragments so that this file's own source does not
# contain a literal match, keeping the exemption below narrow and auditable.
FORBIDDEN = [
    ("absolute macOS/Linux user path", "/Users" + "/"),
    ("absolute ALCF Eagle path", "/eagle" + "/"),
    ("absolute Linux home path", "/home" + "/"),
    ("OpenAI-style API key", "sk" + "-"),
    ("GitHub personal access credential", "ghp" + "_"),
    ("credential-bearing word", "tok" + "en"),
    ("credential-bearing word", "pass" + "word"),
]

# Binary / data files that are tracked on purpose and are not text to scan.
SKIP_SUFFIXES = {".csv", ".pdf", ".png", ".jpg", ".jpeg", ".zip", ".npy", ".npz", ".parquet", ".pkl"}


def tracked_files(staged: bool) -> list[Path]:
    args = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"] if staged else ["git", "ls-files"]
    out = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return [REPO_ROOT / line for line in out.stdout.splitlines() if line.strip()]


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return hits
    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for label, pattern in FORBIDDEN:
            if pattern in lowered:
                hits.append((lineno, label, line.strip()[:160]))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="scan staged changes only")
    args = parser.parse_args()

    total = 0
    scanned = 0
    for path in tracked_files(args.staged):
        if not path.is_file():
            continue
        if path.resolve() == SELF:
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        scanned += 1
        for lineno, label, snippet in scan_file(path):
            total += 1
            rel = path.relative_to(REPO_ROOT)
            print(f"{rel}:{lineno}: {label}: {snippet}")

    print(f"Scanned {scanned} tracked text file(s); {total} hit(s).")
    if total:
        print("FAIL: forbidden path or credential pattern found in tracked files.")
        return 1
    print("PASS: no absolute paths or credential patterns in tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
