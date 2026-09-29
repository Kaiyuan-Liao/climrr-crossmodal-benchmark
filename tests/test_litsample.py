"""The M4-WP1 sample: re-derived from the frozen manifest and the rule alone."""

from __future__ import annotations

import json

import pytest

from climrr import litsample
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

LIT = REPO_ROOT / "artifacts" / "literature"


def _entries(n, dup_pairs=()):
    entries = [{"item_id": f"LIT-{k:06d}", "duplicate_group": None} for k in range(1, n + 1)]
    for g, (a, b) in enumerate(dup_pairs, start=1):
        entries[a - 1]["duplicate_group"] = entries[b - 1]["duplicate_group"] = f"DUP-{g:04d}"
    return entries


def test_the_frozen_sample_is_re_derived_from_the_manifest_and_rule_alone():
    manifest = json.loads((LIT / "corpus_manifest.json").read_text(encoding="utf-8"))
    sample = json.loads((LIT / "wp1_sample.json").read_text(encoding="utf-8"))
    assert sample["corpus_manifest_sha256"] == sha256_file(LIT / "corpus_manifest.json")
    drawn = litsample.draw(manifest["entries"])
    assert drawn["item_ids"] == sample["item_ids"] == [
        "LIT-000001", "LIT-000191", "LIT-000381", "LIT-000571", "LIT-000761",
        "LIT-000951", "LIT-001141", "LIT-001331", "LIT-001521", "LIT-001711",
    ]
    assert drawn["skips"] == sample["skips"] == []
    assert litsample.draw(manifest["entries"]) == drawn  # two runs, same ids


def test_the_later_member_of_a_duplicate_group_is_skipped_and_recorded():
    # LIT-000191 duplicates LIT-000010, so position 191 moves to 192.
    drawn = litsample.draw(_entries(1900, dup_pairs=[(10, 191)]))
    assert drawn["item_ids"][1] == "LIT-000192"
    assert drawn["item_ids"][2] == "LIT-000381"  # the grid does not shift
    assert drawn["skips"] == [{"rule_position": 191, "skipped": "LIT-000191",
                               "reason": "later member of an exact-byte duplicate group"}]


def test_the_first_member_of_a_duplicate_group_is_kept():
    drawn = litsample.draw(_entries(1900, dup_pairs=[(191, 500)]))
    assert "LIT-000191" in drawn["item_ids"] and drawn["skips"] == []


def test_a_manifest_too_short_for_ten_positions_fails():
    with pytest.raises(ValueError):
        litsample.draw(_entries(1000))
