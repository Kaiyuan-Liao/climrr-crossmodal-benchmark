"""The knowledge staging helper: flat copies, subsets, and failing on a missing file.

Every test stages into `tmp_path`; nothing is written to `refresh_knowledge/`
or to `reports/runs/`.
"""

from __future__ import annotations

import sys

import pytest

from climrr.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import stage_knowledge as sk  # noqa: E402

FILES = ("docs/a.md", "top.md", "artifacts/x/b.md")


@pytest.fixture
def root(tmp_path):
    base = tmp_path / "repo"
    for rel in FILES:
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(f"content of {rel}\n", encoding="utf-8")
    return base


def test_stages_every_file_flat_and_overwrites(root, tmp_path):
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / "a.md").write_text("stale\n", encoding="utf-8")
    staged = sk.stage(sk.select(FILES, None), root, dest)
    assert [s["staged_as"] for s in staged] == ["a.md", "top.md", "b.md"]
    assert sorted(p.name for p in dest.iterdir()) == ["a.md", "b.md", "top.md"]
    assert (dest / "a.md").read_text(encoding="utf-8") == "content of docs/a.md\n"


def test_only_accepts_paths_or_basenames_and_keeps_list_order(root):
    assert sk.select(FILES, "b.md, docs/a.md") == ["docs/a.md", "artifacts/x/b.md"]


def test_only_rejects_a_name_not_on_the_list():
    with pytest.raises(sk.StagingError, match="not on the knowledge list"):
        sk.select(FILES, "a.md,nope.md")
    with pytest.raises(sk.StagingError):
        sk.select(FILES, " , ")


def test_a_missing_file_fails_and_stages_nothing(root, tmp_path):
    (root / "top.md").unlink()
    dest = tmp_path / "out"
    with pytest.raises(sk.StagingError, match="top.md"):
        sk.stage(sk.select(FILES, None), root, dest)
    assert not dest.exists()


def test_a_basename_collision_fails(root, tmp_path):
    (root / "docs" / "top.md").write_text("x\n", encoding="utf-8")
    with pytest.raises(sk.StagingError, match="collision"):
        sk.stage(["top.md", "docs/top.md"], root, tmp_path / "out")


def test_main_end_to_end_in_a_temp_dir(root, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sk, "KNOWLEDGE_FILES", FILES)
    dest, runs = tmp_path / "out", tmp_path / "runs"
    rc = sk.main(["--root", str(root), "--dest", str(dest), "--runs-dir", str(runs), "--only", "top.md"])
    assert rc == 0
    assert [p.name for p in dest.iterdir()] == ["top.md"]
    out = capsys.readouterr().out
    assert "top.md" in out and "Commit:" in out
    assert len(list(runs.glob("*_stage_knowledge.json"))) == 1


def test_main_fails_on_a_missing_file(root, tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "KNOWLEDGE_FILES", FILES + ("gone.md",))
    rc = sk.main(["--root", str(root), "--dest", str(tmp_path / "out"), "--runs-dir", str(tmp_path / "runs")])
    assert rc == 1
    assert not (tmp_path / "out").exists()


def test_the_real_list_exists_and_has_unique_basenames():
    names = [p.rsplit("/", 1)[-1] for p in sk.KNOWLEDGE_FILES]
    assert len(names) == len(set(names))
    assert [f for f in sk.KNOWLEDGE_FILES if not (REPO_ROOT / f).is_file()] == []
