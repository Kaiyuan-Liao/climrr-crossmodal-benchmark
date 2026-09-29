#!/usr/bin/env python3
"""M4-WP1 Phase B: the JSON structure actually encountered in the ten sampled files.

For each item in the frozen `artifacts/literature/wp1_sample.json`: verify the
file's SHA-256 against the frozen corpus manifest (fail closed), decode it, and
record its structure --- top-level type, keys in order, value types, string
lengths in code points, nesting. **No string's content is written or read for
meaning here.** Then the union of top-level keys, and which files deviate from
the majority top-level key sequence.

Writes `artifacts/literature/wp1_schema_observed.json`. The run record cites
the sample's SHA-256.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litingest  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import get as get_local_path  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

LIT = REPO_ROOT / "artifacts" / "literature"
SAMPLE = LIT / "wp1_sample.json"
MANIFEST = LIT / "corpus_manifest.json"
OUT = LIT / "wp1_schema_observed.json"


def load_sample() -> tuple[dict, str]:
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    if sha256_file(MANIFEST) != sample["corpus_manifest_sha256"]:
        raise litingest.IntegrityError("corpus manifest changed since the sample was frozen")
    return sample, sha256_file(SAMPLE)


def main() -> int:
    sample, sample_sha = load_sample()
    root = Path(get_local_path("literature_corpus_root"))
    items = []
    for item in sample["items"]:
        doc, failure = litingest.read_verified(root / item["relative_path"], item["sha256"])
        entry = {"item_id": item["item_id"], "sha256": item["sha256"], "bytes": item["bytes"]}
        if failure is not None:
            entry.update(parse_status="parse_failure", parse_failure=failure)
        else:
            entry.update(
                parse_status="parsed",
                top_level_type=litingest.type_name(doc),
                top_level_keys=list(doc) if isinstance(doc, dict) else None,
                structure=litingest.describe(doc),
            )
            if not isinstance(doc, dict):
                entry["parse_status"] = "parse_failure"
                entry["parse_failure"] = "top level is not a JSON object"
        items.append(entry)

    parsed = [i for i in items if i["parse_status"] == "parsed"]
    sequences = Counter(tuple(i["top_level_keys"]) for i in parsed)
    # A "majority" sequence exists only if more than half the parsed files share it.
    top, top_n = sequences.most_common(1)[0] if sequences else ((), 0)
    majority, majority_n = (top, top_n) if top_n * 2 > len(parsed) else (None, 0)
    union: list[str] = []
    for i in parsed:
        for k in i["top_level_keys"]:
            if k not in union:
                union.append(k)
    key_presence = {k: sum(k in i["top_level_keys"] for i in parsed) for k in union}
    deviating = (
        [i["item_id"] for i in parsed if tuple(i["top_level_keys"]) != majority]
        if majority is not None else [i["item_id"] for i in parsed]
    )
    value_types = Counter(
        c["type"] for i in parsed for c in i["structure"]["children"]
    )
    max_depth = max(
        (1 + (c["type"] in ("object", "array")) for i in parsed for c in i["structure"]["children"]),
        default=0,
    )

    result = {
        "artifact": "M4-WP1 observed JSON structure",
        "sample_path": repo_relative(SAMPLE),
        "sample_sha256": sample_sha,
        "corpus_manifest_sha256": sample["corpus_manifest_sha256"],
        "note": "Structure only: types, key order, string lengths in code points. No string content is recorded.",
        "n_items": len(items),
        "n_parsed": len(parsed),
        "n_parse_failure": len(items) - len(parsed),
        "top_level_key_union_in_first_seen_order": union,
        "top_level_key_presence": key_presence,
        "majority_rule": "a top-level key sequence shared by more than half of the parsed files",
        "majority_top_level_key_sequence": list(majority) if majority is not None else None,
        "n_matching_majority": majority_n,
        "items_deviating_from_majority": deviating,
        "n_distinct_top_level_key_sequences": len(sequences),
        "top_level_value_types": dict(value_types),
        "max_nesting_depth": max_depth,
        "distinct_top_level_key_sequences": [
            {"keys": list(k), "n_items": n,
             "item_ids": [i["item_id"] for i in parsed if tuple(i["top_level_keys"]) == k]}
            for k, n in sequences.most_common()
        ],
        "items": items,
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  parsed {len(parsed)} of {len(items)}; key union {union}")
    print(f"  distinct key sequences: {len(sequences)}; majority: {list(majority) if majority else 'none'}")
    print(f"  value types: {dict(value_types)}; max nesting depth {max_depth}")
    print(f"  deviating: {deviating or 'none'}")
    record = write_run_record(
        "wp1_schema",
        result_summary={
            "sample_sha256": sample_sha,
            "n_parsed": len(parsed),
            "parse_failures": [i["item_id"] for i in items if i["parse_status"] != "parsed"] or "none",
            "top_level_key_union": union,
            "majority_top_level_key_sequence": list(majority) if majority else "none",
            "n_distinct_top_level_key_sequences": len(sequences),
            "items_deviating_from_majority": deviating or "none",
            "top_level_value_types": dict(value_types),
        },
        passed=True,
        data_path=SAMPLE,
        data_sha256=sample_sha,
        output_path=OUT,
        config_snapshot={"corpus_root": "config/local_paths.yaml:literature_corpus_root",
                         "sample": repo_relative(SAMPLE)},
    )
    print(f"Run record: {repo_relative(record)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
