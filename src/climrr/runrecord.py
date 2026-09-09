"""Run records: the reproducibility receipt every script in this repo must emit.

Each run writes `reports/runs/<UTC-timestamp>_<name>.json` plus a short `.md`
sibling. The record captures enough provenance to answer, months later, "which
code, which environment, which data bytes produced this result?".
"""

from __future__ import annotations

import getpass
import hashlib
import importlib
import importlib.metadata
import json
import platform
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT, repo_relative

RUNS_DIR = REPO_ROOT / "reports" / "runs"
REQUIREMENTS_PATH = REPO_ROOT / "requirements.txt"

#: Distribution name -> import name, for the few where they differ.
_IMPORT_NAME = {"pyyaml": "yaml"}

_PIN_RE = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*==\s*([^\s#]+)")

#: Keys every run record must carry. tests/test_runrecord.py asserts on this.
RUN_RECORD_SCHEMA = (
    "run_id",
    "name",
    "utc_timestamp",
    "git_commit",
    "git_dirty",
    "untracked_files",
    "hostname",
    "location",
    "python_version",
    "pinned_libraries",
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
    """True when **tracked** files have uncommitted changes.

    Untracked files are deliberately excluded. The question a run record has to
    answer is "did the code that ran differ from the commit?", and a stray log
    or scratch file sitting beside the checkout does not change that. Counting
    it as dirty makes the flag fire so often that it stops meaning anything.
    Untracked files are reported separately by untracked_file_count().
    """
    status = _git("status", "--porcelain", "--untracked-files=no")
    if status is None:
        return None
    return bool(status.strip())


def untracked_file_count() -> int | None:
    """How many untracked files sit in the working tree.

    Informational, not a cleanliness verdict: data/raw/FullData.csv is
    gitignored by design (D-005) and so is not counted here.
    """
    status = _git("status", "--porcelain", "--untracked-files=all")
    if status is None:
        return None
    return sum(1 for line in status.splitlines() if line.startswith("??"))


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


def read_pins(requirements_path: Path | str | None = None) -> list[tuple[str, str]]:
    """Parse `name==version` pins out of requirements.txt, in file order.

    Anything that is not an exact `==` pin is ignored: an unpinned requirement
    has no version to check a run against.
    """
    path = Path(requirements_path) if requirements_path is not None else REQUIREMENTS_PATH
    if not path.is_file():
        return []
    pins: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            continue
        match = _PIN_RE.match(line)
        if match:
            pins.append((match.group(1), match.group(2)))
    return pins


def _installed_version(dist_name: str) -> str:
    """The version this interpreter actually has, preferring the imported module.

    D-007 asks for the *imported* `__version__`, because that is what the code
    ran against; `importlib.metadata` is the fallback for a distribution whose
    module exposes no `__version__` attribute.
    """
    module_name = _IMPORT_NAME.get(dist_name.lower(), dist_name.replace("-", "_"))
    try:
        module = importlib.import_module(module_name)
    except Exception:  # noqa: BLE001 -- any import failure is "not importable"
        module = None
    if module is not None:
        version = getattr(module, "__version__", None)
        if isinstance(version, str) and version:
            return version
    try:
        return importlib.metadata.version(dist_name)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"
    except Exception:  # noqa: BLE001
        return "unavailable"


def pinned_libraries(requirements_path: Path | str | None = None) -> list[dict]:
    """Per pinned library: the version requirements.txt asks for and the one in use.

    `matches_pin` is the load-bearing field. A False here means the profile was
    produced under a different parsing/profiling stack than the one D-007 pins,
    which is a defect to escalate rather than a note to file.
    """
    return [
        {
            "name": name,
            "pinned_version": pinned,
            "imported_version": (installed := _installed_version(name)),
            "matches_pin": installed == pinned,
        }
        for name, pinned in read_pins(requirements_path)
    ]


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
        "untracked_files": untracked_file_count(),
        "hostname": socket.gethostname(),
        "location": loc,
        "user": getpass.getuser(),
        "python_version": platform.python_version(),
        "pinned_libraries": pinned_libraries(),
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


def _format_pins(pins: list[dict] | None) -> str:
    if not pins:
        return "none recorded"
    parts = []
    for pin in pins:
        flag = "" if pin.get("matches_pin") else f" (PIN MISMATCH, pinned {pin['pinned_version']})"
        parts.append(f"`{pin['name']}=={pin['imported_version']}`{flag}")
    return ", ".join(parts)


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
        f"- **Working tree dirty (tracked files)**: {record['git_dirty']}",
        f"- **Untracked files present**: {record['untracked_files']}",
        f"- **Hostname**: {record['hostname']}",
        f"- **Location**: {record['location']}",
        f"- **Python**: {record['python_version']} ({record['platform']})",
        f"- **pip freeze SHA-256**: `{record['pip_freeze_sha256']}`",
        f"- **Pinned libraries (D-007)**: {_format_pins(record.get('pinned_libraries'))}",
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
