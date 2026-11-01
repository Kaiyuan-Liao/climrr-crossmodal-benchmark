#!/usr/bin/env python3
"""Pilot P2b-prep Phase A: paper independence v2 (DR-LIT-IND-1 v2; D-046) from the run-2 evidence tarball.

Reads `litstatements_run2_evidence.tar.gz` (checked against its pinned SHA-256, D-044)
in place, without extracting it: each paper's `result.json` (item id, paper SHA-256) and
the `[SECTION: title]` of its `prompt_user.txt` (the title only; the paper text is not
kept). Checks the 243 papers and their SHA-256 against `papers_meta.json`. Writes
`artifacts/litstatements/run2/independence_v2.json`: per paper the normalized-title hash,
canonical id and basis; the same-SHA-256, possible-duplicate-title and merged groups.
Rules: `src/climrr/litindependence.py`. Deterministic; no model call, no table value.

    python scripts/build_independence_v2.py --tarball <path to litstatements_run2_evidence.tar.gz>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr import litindependence as li  # noqa: E402
from climrr import litstatements_run2 as r2  # noqa: E402
from climrr.checksums import sha256_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

MEMBER = re.compile(r"litstatements/run2/(\d+)/(result\.json|prompt_user\.txt)")


def read_papers(tarball: Path) -> list[dict]:
    found: dict[str, dict] = {}
    with tarfile.open(tarball) as t:
        for m in t.getmembers():
            mm = MEMBER.fullmatch(m.name)
            if not mm:
                continue
            iid, kind = mm.groups()
            text = t.extractfile(m).read().decode("utf-8")
            entry = found.setdefault(iid, {"item_id": iid})
            if kind == "result.json":
                entry["paper_sha256"] = json.loads(text)["paper_sha256"]
            else:
                entry["title"] = r2._title(text)
    return [found[k] for k in sorted(found)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tarball", required=True, type=Path)
    a = ap.parse_args()
    got = sha256_file(a.tarball)
    if got != r2.TARBALL_SHA256:
        raise SystemExit(f"tarball SHA-256 {got} differs from the pin {r2.TARBALL_SHA256} (D-044)")
    papers = read_papers(a.tarball)
    meta = json.loads(r2.PAPERS_META_PATH.read_text(encoding="utf-8"))
    expected = {p["item_id"]: p["paper_sha256"] for p in meta["papers"]}
    observed = {p["item_id"]: p.get("paper_sha256") for p in papers}
    if observed != expected:
        raise SystemExit(f"tarball papers differ from papers_meta.json: {len(observed)} vs {len(expected)} papers")
    indep = li.build(papers)
    r2.write_json(li.INDEPENDENCE_PATH, indep)
    result = {k: indep[k] for k in ("papers_n", "canonical_papers_n", "n_title_section_present", "same_paper_sha256_groups",
                                    "possible_duplicate_title_groups", "merged_groups", "by_basis")}
    result["independence_v2_sha256"] = sha256_file(li.INDEPENDENCE_PATH)
    rec = write_run_record(
        "build_independence_v2", result_summary=result, passed=True, data_path=a.tarball, output_path=li.INDEPENDENCE_PATH,
        config_snapshot={"rule": li.RULE_ID, "decision": li.DECISION, "version": li.VERSION,
                         "title_normalization": indep["title_normalization"], "tarball_sha256": r2.TARBALL_SHA256,
                         "kept_from_prompt_user": "title section only, as a hash", "model_calls": 0},
    )
    print(json.dumps(result, indent=2))
    print(f"run record: {repo_relative(rec)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
