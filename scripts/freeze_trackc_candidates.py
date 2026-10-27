#!/usr/bin/env python3
"""Freeze the Track C paper list: the 100 + 143 LITCORPUS-02 place candidates (D-030, D-033).

Reads the two frozen place-candidate lists under
`artifacts/literature/litcorpus02/place_candidates/` after checking each against
the SHA-256 recorded in `place_candidates.json`, and writes
`data/metadata/softqa/trackc_candidates_v1.json`: a JSON list of
`{"item_id", "arm"}` --- `fire_weather_v1` first, then `extreme_heat_v1`, each in
its list's order --- the `--candidates` input of `scripts/litcollect/softqa_agent.py`.

No paper is opened. The 20 papers already read in M4-WP4
(`artifacts/literature/wp4_sample.json`) stay in; the script checks that all 20
are present and reports them (they are recorded in `data/manifest.json`). An
item in both arms, or a changed list, stops the build.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.checksums import sha256_file  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

PLACE_DIR = REPO_ROOT / "artifacts" / "literature" / "litcorpus02" / "place_candidates"
WP4_SAMPLE = REPO_ROOT / "artifacts" / "literature" / "wp4_sample.json"
OUT = REPO_ROOT / "data" / "metadata" / "softqa" / "trackc_candidates_v1.json"
ARMS = ("fire_weather_v1", "extreme_heat_v1")


def build() -> tuple[list[dict], dict]:
    meta = json.loads((PLACE_DIR / "place_candidates.json").read_text(encoding="utf-8"))
    records, inputs = [], {}
    for arm in ARMS:
        a = meta["arms"][arm]
        path = PLACE_DIR / a["list"]
        got = sha256_file(path)
        if got != a["list_sha256"]:
            raise SystemExit(f"{path.name}: SHA-256 {got} != recorded {a['list_sha256']}")
        ids = [ln.strip() for ln in path.read_text(encoding="ascii").splitlines() if ln.strip()]
        if len(ids) != a["candidates"] or len(set(ids)) != len(ids):
            raise SystemExit(f"{path.name}: {len(ids)} ids ({len(set(ids))} distinct), expected {a['candidates']}")
        inputs[path.relative_to(REPO_ROOT).as_posix()] = got
        records += [{"item_id": i, "arm": arm} for i in ids]
    ids = [r["item_id"] for r in records]
    if len(set(ids)) != len(ids):
        raise SystemExit("an item is in both arms")
    sample = json.loads(WP4_SAMPLE.read_text(encoding="utf-8"))["selected"]
    in_list = {(r["item_id"], r["arm"]) for r in records}
    missing = [s["lit2_id"] for s in sample if (s["item_id"], s["arm"]) not in in_list]
    if missing:
        raise SystemExit(f"already-read papers missing from the list: {missing}")
    already_read = [{"item_id": s["item_id"], "lit2_id": s["lit2_id"], "arm": s["arm"]} for s in sample]
    inputs[WP4_SAMPLE.relative_to(REPO_ROOT).as_posix()] = sha256_file(WP4_SAMPLE)
    return records, {"inputs": inputs, "already_read": already_read}


def render(records: list[dict]) -> str:
    return "[\n" + ",\n".join("  " + json.dumps(r) for r in records) + "\n]\n"


def main() -> int:
    records, info = build()
    OUT.write_text(render(records), encoding="utf-8")
    summary = {"n_candidates": len(records),
               "per_arm": {arm: sum(r["arm"] == arm for r in records) for arm in ARMS},
               "n_already_read": len(info["already_read"]),
               "output_sha256": sha256_file(OUT)}
    print(json.dumps(summary, indent=2))
    write_run_record(
        "freeze_trackc_candidates",
        result_summary=summary,
        passed=True,
        data_path=PLACE_DIR / "place_candidates.json",
        output_path=OUT,
        config_snapshot={"input_sha256": info["inputs"], "already_read": info["already_read"]},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
