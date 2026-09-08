"""Run records: the reproducibility receipt every script in this repo must emit.

Each run writes `reports/runs/<UTC-timestamp>_<name>.json` plus a short `.md`
sibling. The record captures enough provenance to answer, months later, "which
code, which environment, which data bytes produced this result?".
"""

from __future__ import annotations

import getpass
import hashlib
import json
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative

RUNS_DIR = REPO_ROOT / "reports" / "runs"

#: Keys every run record must carry. tests/test_runrecord.py asserts on this.
RUN_RECORD_SCHEMA = (
    "run_id",
    "name",
    "utc_timestamp",
    "git_commit",
    "git_dirty",
    "hostname",
    "location",
    "python_version",
    "pip_freeze_sha256",
    "config_snapshot",
    "data_path",
    "data_sha256",
    "output_path",
    "result_summary",
    "passed",
)


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def git_commit() -> str:
    return _git("rev-parse", "HEAD") or "unknown"


def git_dirty() -> bool | None:
    status = _git("status", "--porcelain")
    if status is None:
        return None
    return bool(status.strip())


def pip_freeze_sha256() -> str:
    """SHA-256 of `pip freeze` output: an environment fingerprint, not a lockfile."""
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    if out.returncode != 0:
        return "unavailable"
    return hashlib.sha256(out.stdout.encode("utf-8")).hexdigest()


def detect_location() -> str:
    """Execution-location label: 'sophia' on the ALCF machine, else 'local'."""
    host = socket.gethostname().lower()
    if "sophia" in host or host.startswith("x3"):
        return "sophia"
    return "local"


def write_run_record(
    name: str,
    *,
    result_summary: dict | str,
    passed: bool,
    data_path: Path | str | None = None,
    data_sha256: str | None = None,
    output_path: Path | str | None = None,
    config_snapshot: dict | None = None,
    location: str | None = None,
    runs_dir: Path | str | None = None,
) -> Path:
    """Write the JSON record and its Markdown sibling. Returns the JSON path."""
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    loc = location or detect_location()
    run_id = f"{stamp}_{loc}_{name}"

    if data_path is not None and data_sha256 is None:
        data_sha256 = sha256_file(data_path)

    record = {
        "run_id": run_id,
        "name": name,
        "utc_timestamp": now.isoformat(),
        "git_commit": git_commit(),
        "git_dirty": git_dirty(),
        "hostname": socket.gethostname(),
        "location": loc,
        "user": getpass.getuser(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "pip_freeze_sha256": pip_freeze_sha256(),
        "config_snapshot": config_snapshot or {},
        "data_path": repo_relative(data_path) if data_path is not None else None,
        "data_sha256": data_sha256,
        "output_path": repo_relative(output_path) if output_path is not None else None,
        "result_summary": result_summary,
        "passed": bool(passed),
    }

    target_dir = Path(runs_dir) if runs_dir is not None else RUNS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / f"{stamp}_{loc}_{name}.json"
    json_path.write_text(json.dumps(record, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    _write_markdown(json_path.with_suffix(".md"), record)
    return json_path


def _write_markdown(path: Path, record: dict) -> None:
    summary = record["result_summary"]
    if isinstance(summary, dict):
        summary_block = "\n".join(f"- `{k}`: {v}" for k, v in summary.items())
    else:
        summary_block = str(summary)
    lines = [
        f"# Run record: {record['run_id']}",
        "",
        f"- **Result**: {'PASS' if record['passed'] else 'FAIL'}",
        f"- **UTC timestamp**: {record['utc_timestamp']}",
        f"- **Git commit**: `{record['git_commit']}`",
        f"- **Working tree dirty**: {record['git_dirty']}",
        f"- **Hostname**: {record['hostname']}",
        f"- **Location**: {record['location']}",
        f"- **Python**: {record['python_version']} ({record['platform']})",
        f"- **pip freeze SHA-256**: `{record['pip_freeze_sha256']}`",
        f"- **Data path (repo-relative)**: `{record['data_path']}`",
        f"- **Data SHA-256**: `{record['data_sha256']}`",
        f"- **Output path**: `{record['output_path']}`",
        "",
        "## Config snapshot",
        "",
        "```json",
        json.dumps(record["config_snapshot"], indent=2),
        "```",
        "",
        "## Result summary",
        "",
        summary_block,
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
