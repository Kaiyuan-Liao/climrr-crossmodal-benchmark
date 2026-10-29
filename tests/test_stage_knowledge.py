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
    dest = tmp_path / "out"
    rc = sk.main(["--root", str(root), "--dest", str(dest), "--only", "top.md"])
    assert rc == 0
    assert [p.name for p in dest.iterdir()] == ["top.md"]
    out = capsys.readouterr().out
    assert "top.md" in out and "Commit:" in out
    assert "Run record" not in out


def test_main_writes_no_run_record(root, tmp_path, monkeypatch):
    """M4-WP3 Phase A.5: staging leaves reports/runs/ untouched and never calls the run-record writer."""
    import ast

    import climrr.runrecord as rr

    calls = []
    monkeypatch.setattr(rr, "write_run_record", lambda *a, **k: calls.append(a))
    monkeypatch.setattr(sk, "KNOWLEDGE_FILES", FILES)
    runs = REPO_ROOT / "reports" / "runs"
    before = sorted(p.name for p in runs.iterdir())
    assert sk.main(["--root", str(root), "--dest", str(tmp_path / "out")]) == 0
    assert sorted(p.name for p in runs.iterdir()) == before
    assert calls == []
    tree = ast.parse((REPO_ROOT / "scripts" / "stage_knowledge.py").read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    assert "write_run_record" not in names


def test_main_fails_on_a_missing_file(root, tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "KNOWLEDGE_FILES", FILES + ("gone.md",))
    rc = sk.main(["--root", str(root), "--dest", str(tmp_path / "out")])
    assert rc == 1
    assert not (tmp_path / "out").exists()


def test_the_real_list_exists_and_has_unique_basenames():
    names = [p.rsplit("/", 1)[-1] for p in sk.KNOWLEDGE_FILES]
    assert len(names) == len(set(names))
    assert [f for f in sk.KNOWLEDGE_FILES if not (REPO_ROOT / f).is_file()] == []


def test_the_list_carries_the_m4_wp3_rulings_and_records():
    for f in ("docs/M4_WP3_CONCEPT_FIRST_GUIDANCE_RULING.md", "docs/M4_WP3_SOURCE_YIELD_GUIDANCE_RULING.md",
              "docs/LITCORPUS01_SHARD_PILOT.md", "docs/LITCORPUS02_PROVENANCE.md",
              "reports/milestones/M4_WP3_REPORT.md", "docs/M4_WP3_WORKING_CORPUS_STAGE2_GUIDANCE_RULING.md"):
        assert f in sk.KNOWLEDGE_FILES


def test_the_list_carries_the_m4_wp4_adjudication_and_m5_wp4_compatibility():
    for f in ("docs/LITERATURE_WP4_ADJUDICATION.md", "docs/M5_WP4_COMPATIBILITY.md"):
        assert f in sk.KNOWLEDGE_FILES


def test_the_list_carries_the_m4_wp1_pilot_and_its_ruling():
    assert "docs/LITERATURE_WP1_PILOT.md" in sk.KNOWLEDGE_FILES
    assert "docs/M4_WP1_REVIEW_M5_WP1_GUIDANCE_RULING.md" in sk.KNOWLEDGE_FILES


def _project_state_knowledge_links() -> list[str]:
    """Repo-relative paths linked in the `## Knowledge files` section of PROJECT_STATE.md."""
    import os
    import re

    text = (REPO_ROOT / "docs" / "PROJECT_STATE.md").read_text(encoding="utf-8")
    section = text.split("\n## Knowledge files\n", 1)[1].split("\n## ", 1)[0]
    return [os.path.normpath(f"docs/{rel}") for rel in re.findall(r"\]\(([^)#]+)\)", section)]


def test_every_knowledge_file_named_in_project_state_is_on_the_list():
    """Track B run 2, Phase A: LITERATURE_WP4_READING.md and DICTIONARY_CONCEPTS.md had been omitted."""
    linked = _project_state_knowledge_links()
    assert linked, "PROJECT_STATE.md has no Knowledge files section"
    assert [f for f in linked if f not in sk.KNOWLEDGE_FILES] == []
    for f in ("docs/LITERATURE_WP4_READING.md", "docs/DICTIONARY_CONCEPTS.md"):
        assert f in sk.KNOWLEDGE_FILES and f in linked


def test_the_list_carries_the_run2_ruling():
    assert "docs/TRACKB_STAGE2_RUN2_GUIDANCE_RULING.md" in sk.KNOWLEDGE_FILES


def test_the_list_carries_the_external_references():
    assert "docs/REFERENCES.md" in sk.KNOWLEDGE_FILES


def test_the_list_carries_the_redesign_document():
    assert "docs/BENCHMARK_REDESIGN_2026-10-29.md" in sk.KNOWLEDGE_FILES


def test_the_list_carries_the_reanchor_ruling():
    """Pilot P1, Phase A: the GUIDANCE re-anchor ruling of 2026-10-29 (D-041)."""
    assert "docs/BENCHMARK_REANCHOR_GUIDANCE_RULING.md" in sk.KNOWLEDGE_FILES
