"""The M4-WP1 deterministic sample (D-016): every 190th item of the frozen manifest.

The rule reads **only** the frozen corpus manifest --- item ids and duplicate
groups. It never opens a corpus file, and nothing about a file's name, title,
topic or content can influence it:

    Take LIT-000001, then every 190th item by numeric id (LIT-000191,
    LIT-000381, ...), until ten items are taken. If a selected item is the
    *later* member of an exact-byte duplicate group, skip to the next id and
    record the skip; the continuing step is counted from the rule's position,
    not from the substitute.

The sample is for workflow validation. It is not representative of the corpus
and must never be described as such.
"""

from __future__ import annotations

SAMPLE_SIZE = 10
STEP = 190
START = 1

RULE_TEXT = (
    "Every 190th LIT item by numeric id, starting at LIT-000001 "
    "(LIT-000001, LIT-000191, LIT-000381, ...), ten items. If a selected item is "
    "the later member of an exact-byte duplicate group, skip to the next id and "
    "record the skip; later positions stay on the 190-step grid. Derived from "
    "the frozen corpus manifest alone; no file is opened."
)


def _later_duplicates(entries: list[dict]) -> set[str]:
    """Ids that are not the first (lowest-id) member of their duplicate group."""
    first: dict[str, str] = {}
    later: set[str] = set()
    for e in sorted(entries, key=lambda e: e["item_id"]):
        group = e.get("duplicate_group")
        if not group:
            continue
        if group in first:
            later.add(e["item_id"])
        else:
            first[group] = e["item_id"]
    return later


def draw(entries: list[dict]) -> dict:
    """The ten sampled ids and every skip, from manifest entries alone."""
    ids = [e["item_id"] for e in sorted(entries, key=lambda e: e["item_id"])]
    number = {i: int(i.split("-")[1]) for i in ids}
    by_number = {n: i for i, n in number.items()}
    later = _later_duplicates(entries)
    chosen: list[str] = []
    skips: list[dict] = []
    for k in range(SAMPLE_SIZE):
        n = START + k * STEP
        if n not in by_number:
            raise ValueError(f"rule position {n} is past the end of the manifest ({len(ids)} items)")
        while by_number[n] in later or by_number[n] in chosen:
            skips.append({"rule_position": START + k * STEP, "skipped": by_number[n],
                          "reason": "later member of an exact-byte duplicate group"})
            n += 1
            if n not in by_number:
                raise ValueError("ran off the end of the manifest while skipping")
        chosen.append(by_number[n])
    return {"item_ids": chosen, "skips": skips}
