#!/usr/bin/env python3
"""Pre-commit guard: no absolute machine paths and no credential-shaped strings
may enter tracked files.

Scans every file Git tracks (plus, with --staged, anything staged) for the
forbidden patterns. Absolute paths belong only in the untracked
`config/local_paths.yaml`; the tracked example file uses <PLACEHOLDER> markers.

This script is excluded from its own scan: it necessarily contains the literal
patterns it searches for. It is the only self-exempt file, and it contains no
real path or credential -- read it to confirm.

One narrow, hash-pinned exemption (Track B Stage 2a, owner decision recorded in
D-026): the two delivered ALCF tools in `WORD_EXEMPTIONS` read an access value
from an environment variable whose name contains the credential word, and must
stay byte-identical to the files delivered. For exactly those paths, and **only
while each file's SHA-256 equals the pinned value**, hits of the
"credential-bearing word" rule are not reported. Every other rule --- absolute
paths, key prefixes --- still applies to them, and any change to either file
makes the exemption lapse, so the word hits return and the scan fails.

Extended under the same terms (owner decision recorded in D-027) to the GUIDANCE
ruling `docs/M4_WP4_TRACKB_GUIDANCE_RULING.md`, which uses the credential word
in its ordinary sense ("scenario-<word> retrieval") and must stay byte-identical
to the ruling as delivered.

Matching rules
--------------
Absolute paths are matched **case-sensitively, as literal substrings**, because
that is how they are actually spelled on disk.

Credential-shaped strings are matched **case-insensitively with boundaries**,
so that ordinary prose does not trip the guard:

- key prefixes must start a token, so "Task-specific" is not an API key;
- credential words must appear whole, so "API keys, tokens, credentials" is
  not a leaked credential but a standalone "token" still is.

A guard that cries wolf gets switched off, which is a worse outcome than the
false positives it was avoiding.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()

# Absolute machine paths: literal, case-sensitive substrings.
# Assembled from fragments so this file's own source holds no literal match.
FORBIDDEN_PATHS = [
    ("absolute macOS/Linux user path", "/User" + "s/"),
    ("absolute ALCF Eagle path", "/eagl" + "e/"),
    ("absolute Linux home path", "/hom" + "e/"),
]

# Credential-shaped strings: case-insensitive, boundary-anchored regexes.
# A key prefix must begin a token and be followed by key material; a credential
# word must stand alone rather than sit inside a longer word.
FORBIDDEN_PATTERNS = [
    ("OpenAI-style API key", re.compile(r"(?<![A-Za-z0-9])" + "sk" + r"-[A-Za-z0-9]", re.IGNORECASE)),
    ("GitHub personal access credential", re.compile(r"(?<![A-Za-z0-9])" + "ghp" + r"_[A-Za-z0-9]", re.IGNORECASE)),
    ("credential-bearing word", re.compile(r"\b" + "tok" + r"en\b", re.IGNORECASE)),
    ("credential-bearing word", re.compile(r"\b" + "pass" + r"word\b", re.IGNORECASE)),
]

# Hash-pinned exemption from the credential-word rule only (D-026, D-027). Path -> SHA-256.
WORD_EXEMPTION_LABEL = "credential-bearing word"
WORD_EXEMPTIONS = {
    "scripts/litcollect/survey_driver.py": "e1fb664c98e4ff866bb348c8930bfc1b9243957441b8a19ea0893e0b711af4cd",
    "scripts/litcollect/probe_alcf_inference.py": "79181c48981c709b49b90d78fc8aaddffaf12d2f1bb0591b9a9daa3aad438c66",
    "docs/M4_WP4_TRACKB_GUIDANCE_RULING.md": "ae4129d3a16c5b4d9b60422b5ef37022b21b441c8d60affc0bf793ffab246402",
}

# Binary / data files that are tracked on purpose and are not text to scan.
SKIP_SUFFIXES = {".csv", ".pdf", ".png", ".jpg", ".jpeg", ".zip", ".npy", ".npz", ".parquet", ".pkl"}


def tracked_files(staged: bool) -> list[Path]:
    args = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"] if staged else ["git", "ls-files"]
    out = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return [REPO_ROOT / line for line in out.stdout.splitlines() if line.strip()]


def scan_line(line: str) -> list[str]:
    """Return the labels of every forbidden pattern present in one line."""
    labels = []
    for label, literal in FORBIDDEN_PATHS:
        if literal in line:
            labels.append(label)
    for label, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(line):
            labels.append(label)
    return labels


def scan_text(text: str) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for label in scan_line(line):
            hits.append((lineno, label, line.strip()[:160]))
    return hits


def word_exempt(path: Path) -> bool:
    """True iff `path` is in WORD_EXEMPTIONS and its bytes still hash to the pinned value."""
    try:
        rel = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return False
    pinned = WORD_EXEMPTIONS.get(rel)
    return pinned is not None and hashlib.sha256(path.read_bytes()).hexdigest() == pinned


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    hits = scan_text(text)
    if word_exempt(path):
        hits = [h for h in hits if h[1] != WORD_EXEMPTION_LABEL]
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
