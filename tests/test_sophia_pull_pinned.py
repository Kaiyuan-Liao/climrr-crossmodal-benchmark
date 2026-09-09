"""`scripts/sophia_pull_pinned.sh` must explain the run-record collision, not just abort.

The collision is real and was hit in practice: a run record generated on Sophia
is untracked there, but once it has been copied back and committed from the
authoring clone it is *tracked* in the next pinned commit --- so checking that
commit out would overwrite it, and git refuses. Correctly. The script's job is to
say which files collided, whether the pinned commit already carries the identical
bytes, and what to remove --- and to remove nothing itself.

These tests build a throwaway origin and execution clone on disk, so the failure
is produced by real git rather than by a mocked error string.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sophia_pull_pinned.sh"

RECORD = "reports/runs/20260909T015712Z_sophia_profile_fulldata.json"

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is required")


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True, timeout=60
    )
    return result.stdout.strip()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def clones(tmp_path):
    """An origin, an authoring clone with two commits, and an execution clone.

    Returns (execution clone path, commit A, commit B). Commit B adds a run
    record; the execution clone sits on commit A.
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "--initial-branch=main", str(origin)],
        check=True,
        capture_output=True,
    )

    author = tmp_path / "author"
    subprocess.run(
        ["git", "clone", str(origin), str(author)], check=True, capture_output=True
    )
    _git(author, "config", "user.email", "test@example.invalid")
    _git(author, "config", "user.name", "Test")

    _write(author / "reports" / "runs" / ".gitkeep", "")
    _git(author, "add", "-A")
    _git(author, "commit", "-m", "first")
    commit_a = _git(author, "rev-parse", "HEAD")

    _write(author / RECORD, '{"run_id": "copied back", "passed": true}\n')
    _git(author, "add", "-A")
    _git(author, "commit", "-m", "add the sophia run record")
    commit_b = _git(author, "rev-parse", "HEAD")
    _git(author, "push", "origin", "main")

    execution = tmp_path / "execution"
    subprocess.run(
        ["git", "clone", str(origin), str(execution)], check=True, capture_output=True
    )
    _git(execution, "checkout", "--detach", commit_a)
    return execution, commit_a, commit_b


def _run(execution: Path, commit: str):
    return subprocess.run(
        ["bash", str(SCRIPT), commit],
        cwd=execution,
        capture_output=True,
        text=True,
        timeout=120,
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "CLIMRR_REPO_ROOT": str(execution)},
    )


def test_a_clean_pull_still_succeeds(clones):
    execution, _commit_a, commit_b = clones
    result = _run(execution, commit_b)
    assert result.returncode == 0, result.stderr
    assert _git(execution, "rev-parse", "HEAD") == commit_b
    assert (execution / RECORD).is_file()


def test_an_identical_copied_back_record_is_named_with_an_rm_command(clones):
    """The exact situation Kaiyuan hit: the record here is what the commit tracks."""
    execution, _commit_a, commit_b = clones
    _write(execution / RECORD, '{"run_id": "copied back", "passed": true}\n')

    result = _run(execution, commit_b)

    assert result.returncode != 0, "the checkout must still fail; git's refusal stands"
    output = result.stdout + result.stderr
    assert RECORD in output, "the colliding file must be named"
    assert "BYTE-IDENTICAL" in output
    assert f"rm -f {RECORD}" in output, "the exact removal command must be given"
    assert "Nothing has been deleted" in output


def test_the_script_deletes_nothing_itself(clones):
    execution, commit_a, commit_b = clones
    _write(execution / RECORD, '{"run_id": "copied back", "passed": true}\n')

    _run(execution, commit_b)

    assert (execution / RECORD).is_file(), "the script must never remove a file"
    assert _git(execution, "rev-parse", "HEAD") == commit_a, "HEAD must not have moved"


def test_a_differing_file_is_flagged_as_unsafe_to_delete(clones):
    """A local file that is *not* what was committed must not be waved away."""
    execution, _commit_a, commit_b = clones
    _write(execution / RECORD, '{"run_id": "something else entirely"}\n')

    result = _run(execution, commit_b)

    output = result.stdout + result.stderr
    assert "DIFFER" in output
    assert "Do not delete them" in output
    assert f"rm -f {RECORD}" not in output, "a differing file must not be offered for removal"


def test_local_modifications_to_tracked_files_are_still_refused_first(clones):
    """The pre-existing dirty-tree guard is unchanged and still fires before checkout."""
    execution, _commit_a, commit_b = clones
    (execution / "reports" / "runs" / ".gitkeep").write_text("dirty\n", encoding="utf-8")

    result = _run(execution, commit_b)

    assert result.returncode == 1
    assert "pull-only" in result.stderr
