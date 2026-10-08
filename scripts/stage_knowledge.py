#!/usr/bin/env python3
"""Stage the COORDINATOR / GUIDANCE knowledge files into `refresh_knowledge/`.

Copies every file in `KNOWLEDGE_FILES` --- or, with `--only a,b,c`, the named
subset of it --- into `refresh_knowledge/` at the repository root, flat, under
its original basename, overwriting what is there. Then prints what was staged
and the current commit, so the uploaded set can be tied to a commit.

**The COORDINATOR maintains `KNOWLEDGE_FILES`** (see `CLAUDE.md`). If any file on
the list is missing, nothing is copied and the run fails: a partial refresh
would look complete. `refresh_knowledge/` is gitignored; it is a staging area,
not evidence.

`--only` takes repo-relative paths or basenames from the list, comma-separated.
A name that is not on the list is an error, not a silent skip.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from climrr.checksums import sha256_file  # noqa: E402
from climrr.runrecord import git_commit, git_dirty, write_run_record  # noqa: E402

#: Maintained by the COORDINATOR. Repo-relative paths; basenames must be unique.
KNOWLEDGE_FILES = (
    "docs/BLUEPRINT.md",
    "CLAUDE.md",
    "docs/PROJECT_STATE.md",
    "docs/DECISION_LOG.md",
    "docs/MENTOR_BRIEF.md",
    "docs/METADATA_QUESTIONS.md",
    "docs/PILOT_SUBSET.md",
    "docs/MENTOR_EXAMPLES.md",
    "docs/PHENOMENON_PROTOTYPES.md",
    "docs/PHENOMENON_ASSUMPTIONS.md",
    "docs/GROUP_MEETING_2026-09-14.md",
    "artifacts/profiles/hierarchy_checks.md",
    "docs/LITERATURE_QUERY_SCOPE.md",
    "docs/LITERATURE_CORPUS_INVENTORY.md",
    "docs/M1_WP3B_GUIDANCE_RULING.md",
    "docs/M4_WP0_GUIDANCE_RULING.md",
    "docs/M4_WP0_REVIEW_MERGE_WP1_GUIDANCE_RULING.md",
    "docs/LITERATURE_WP1_PILOT.md",
    "docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md",
    "docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md",
    "docs/BRIDGE_ELIGIBILITY.md",
    "docs/LITERATURE_WP2_CANDIDATES.md",
    "docs/LITERATURE_WP1B_ADJUDICATION.md",
)

DEST_DIR = REPO_ROOT / "refresh_knowledge"


class StagingError(RuntimeError):
    """A requested or listed file is missing, unknown, or collides."""


def select(files: tuple[str, ...], only: str | None) -> list[str]:
    """The list, or the `--only` subset of it, in list order."""
    if only is None:
        return list(files)
    wanted = [w.strip() for w in only.split(",") if w.strip()]
    if not wanted:
        raise StagingError("--only was given but names no file")
    by_name = {Path(f).name: f for f in files}
    picked, unknown = set(), []
    for w in wanted:
        if w in files:
            picked.add(w)
        elif w in by_name:
            picked.add(by_name[w])
        else:
            unknown.append(w)
    if unknown:
        raise StagingError(f"not on the knowledge list: {', '.join(unknown)}")
    return [f for f in files if f in picked]


def stage(selected: list[str], root: Path, dest: Path) -> list[dict]:
    """Copy `selected` from `root` into `dest`, flat. Checks everything first."""
    names = [Path(f).name for f in selected]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise StagingError(f"basename collision in the list: {', '.join(dupes)}")
    missing = [f for f in selected if not (root / f).is_file()]
    if missing:
        raise StagingError(f"missing, nothing staged: {', '.join(missing)}")
    dest.mkdir(parents=True, exist_ok=True)
    staged = []
    for f in selected:
        target = dest / Path(f).name
        shutil.copyfile(root / f, target)
        staged.append({"source": f, "staged_as": target.name, "sha256": sha256_file(target)})
    return staged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default=None, help="comma-separated subset of the list")
    parser.add_argument("--dest", type=Path, default=DEST_DIR, help=argparse.SUPPRESS)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--runs-dir", type=Path, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        staged = stage(select(KNOWLEDGE_FILES, args.only), args.root, args.dest)
    except StagingError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    commit, dirty = git_commit(), git_dirty()
    for item in staged:
        print(f"  {item['source']}")
    print(f"Staged {len(staged)} file(s) into {args.dest.name}/")
    print(f"Commit: {commit}{' (tracked files modified)' if dirty else ''}")

    record = write_run_record(
        "stage_knowledge",
        result_summary={"n_staged": len(staged), "staged": staged, "subset": args.only or "all"},
        passed=True,
        config_snapshot={"dest": args.dest.name, "only": args.only},
        runs_dir=args.runs_dir,
    )
    print(f"Run record: {record.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
