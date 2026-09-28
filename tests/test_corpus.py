"""Corpus inventory: byte-only reads, stable ids, duplicates, and nothing leaking into Git.

Every test here runs on a synthetic fixture folder built in `tmp_path`. The real
corpus is never touched by the test suite. The fixture files hold valid JSON on
purpose: the point of the read-boundary tests is that valid JSON sits right
there and is still never parsed.
"""

from __future__ import annotations

import ast
import builtins
import json
import os

import pytest

from climrr import corpus
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

ARTIFACTS = REPO_ROOT / "artifacts" / "literature"


@pytest.fixture
def folder(tmp_path):
    root = tmp_path / "00"
    root.mkdir()
    (root / "b.json").write_bytes(b'{"title": "beta"}')
    (root / "a.json").write_bytes(b'{"title": "alpha"}')
    (root / "c.json").write_bytes(b'{"title": "alpha"}')  # same bytes as a.json
    (root / "empty.json").write_bytes(b"")
    (root / "sub").mkdir()
    (root / "sub" / "d.json").write_bytes(b'{"title": "delta"}')
    return root


def build(root):
    return corpus.assign_ids_and_duplicates(corpus.scan(root), "2026-09-28T00:00:00Z")


# --- ids and order -----------------------------------------------------------


def test_ids_follow_sorted_relative_paths(folder):
    entries = build(folder)
    assert [(e["item_id"], e["relative_path"]) for e in entries] == [
        ("LIT-000001", "a.json"),
        ("LIT-000002", "b.json"),
        ("LIT-000003", "c.json"),
        ("LIT-000004", "empty.json"),
        ("LIT-000005", "sub/d.json"),
    ]
    assert all(set(e) == set(corpus.ENTRY_FIELDS) for e in entries)
    assert all(e["config_reference"] == corpus.CONFIG_REFERENCE for e in entries)


def test_ids_and_hashes_are_stable_across_runs(folder):
    first, second = build(folder), build(folder)
    assert first == second
    assert corpus.content_identity(first) == corpus.content_identity(second)


def test_a_changed_path_set_fails_loudly(folder):
    frozen = build(folder)
    (folder / "aa.json").write_bytes(b"{}")
    with pytest.raises(corpus.CorpusChangedError, match="1 path\\(s\\) added"):
        corpus.verify_against_frozen(corpus.scan(folder), frozen)
    (folder / "aa.json").unlink()
    (folder / "b.json").unlink()
    with pytest.raises(corpus.CorpusChangedError, match="1 removed"):
        corpus.verify_against_frozen(corpus.scan(folder), frozen)


def test_changed_bytes_fail_loudly(folder):
    frozen = build(folder)
    (folder / "b.json").write_bytes(b'{"title": "BETA"}')
    with pytest.raises(corpus.CorpusChangedError, match="1 changed"):
        corpus.verify_against_frozen(corpus.scan(folder), frozen)


def test_an_unchanged_folder_verifies(folder):
    corpus.verify_against_frozen(corpus.scan(folder), build(folder))


# --- duplicates, sizes, skipped entries --------------------------------------


def test_exact_byte_duplicates_are_grouped_not_removed(folder):
    entries = build(folder)
    by_path = {e["relative_path"]: e for e in entries}
    assert by_path["a.json"]["duplicate_group"] == "DUP-0001"
    assert by_path["c.json"]["duplicate_group"] == "DUP-0001"
    assert by_path["b.json"]["duplicate_group"] is None
    summary = corpus.summarize(entries)
    assert summary["n_entries"] == 5
    assert summary["n_duplicate_groups"] == 1
    assert summary["n_redundant_copies"] == 1
    assert summary["duplicate_groups"][0]["item_ids"] == ["LIT-000001", "LIT-000003"]


def test_zero_byte_files_are_counted(folder):
    summary = corpus.summarize(build(folder))
    assert summary["n_zero_byte"] == 1
    assert summary["zero_byte_item_ids"] == ["LIT-000004"]


def test_a_symlink_is_skipped_and_its_target_never_opened(folder, tmp_path, monkeypatch):
    outside = tmp_path / "outside.json"
    outside.write_bytes(b"{}")
    os.symlink(outside, folder / "link.json")
    os.symlink(tmp_path, folder / "linkdir")
    opened = []
    real_open = builtins.open
    monkeypatch.setattr(builtins, "open", lambda p, *a, **k: (opened.append(str(p)), real_open(p, *a, **k))[1])
    entries = {e["relative_path"]: e for e in build(folder)}
    assert entries["link.json"]["accessibility"] == "skipped"
    assert entries["link.json"]["sha256"] is None
    assert entries["linkdir"]["accessibility"] == "skipped"
    assert not any(p.endswith("outside.json") or "linkdir" in p for p in opened)


def test_an_archive_is_hashed_but_marked_skipped(folder):
    (folder / "bundle.zip").write_bytes(b"PK\x03\x04not really")
    entry = next(e for e in build(folder) if e["relative_path"] == "bundle.zip")
    assert entry["accessibility"] == "skipped"
    assert entry["skip_reason"].startswith("archive")
    assert entry["sha256"] is not None


# --- the read boundary --------------------------------------------------------


@pytest.mark.parametrize("mode", ["r", "rt", "r+b", "w", "wb", "ab", "rb+"])
def test_the_reader_refuses_every_mode_but_rb(folder, mode):
    with pytest.raises(corpus.CorpusReadRefused):
        corpus._open_corpus_bytes(folder / "a.json", mode)


class _NoDecode(bytes):
    def decode(self, *args, **kwargs):  # noqa: D401
        raise AssertionError("corpus bytes were decoded")


class _SpyHandle:
    def __init__(self, handle):
        self._h = handle

    def read(self, *args):
        return _NoDecode(self._h.read(*args))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._h.close()


def test_a_full_inventory_opens_only_rb_and_never_decodes_or_parses(folder, monkeypatch):
    modes = []
    real_open = builtins.open

    def spy_open(path, mode="r", *args, **kwargs):
        if str(path).startswith(str(folder)):
            modes.append(mode)
            return _SpyHandle(real_open(path, mode, *args, **kwargs))
        return real_open(path, mode, *args, **kwargs)

    def refuse(*args, **kwargs):
        raise AssertionError("json parsing was called during the inventory")

    monkeypatch.setattr(builtins, "open", spy_open)
    monkeypatch.setattr(json, "load", refuse)
    monkeypatch.setattr(json, "loads", refuse)
    entries = build(folder)
    assert len(entries) == 5
    assert modes and set(modes) == {"rb"}
    assert len(modes) == 5  # one open per regular file, no more


def test_the_module_source_cannot_parse_or_decode():
    """Static guard: no JSON/text/PDF import, no decode, one open call."""
    tree = ast.parse((REPO_ROOT / "src" / "climrr" / "corpus.py").read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(node.module or "")])
    }
    assert not imported & {"json", "csv", "pypdf", "pypdfium2", "zipfile", "tarfile", "codecs", "io"}
    called = [
        node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    ]
    for forbidden in ("decode", "read_text", "load", "loads", "readline", "readlines"):
        assert forbidden not in called, forbidden
    assert called.count("open") == 1


# --- the tracked artifacts ----------------------------------------------------


def test_the_tracked_manifest_is_pinned_in_data_manifest():
    data = json.loads((REPO_ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    entry = next(c for c in data["external_corpora"] if c["corpus_id"] == "LITCORPUS-00")
    path = REPO_ROOT / entry["inventory_manifest_path"]
    assert sha256_file(path) == entry["inventory_manifest_sha256"]
    assert sha256_file(REPO_ROOT / entry["inventory_manifest_csv_path"]) == entry["inventory_manifest_csv_sha256"]
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert corpus.content_identity(doc["entries"]) == entry["content_identity_sha256"]
    assert doc["summary"]["n_entries"] == entry["n_files"] == len(doc["entries"])


def test_the_tracked_manifest_has_stable_ids_and_required_fields():
    doc = json.loads((ARTIFACTS / "corpus_manifest.json").read_text(encoding="utf-8"))
    entries = doc["entries"]
    assert [e["item_id"] for e in entries] == [f"LIT-{k:06d}" for k in range(1, len(entries) + 1)]
    assert [e["relative_path"] for e in entries] == sorted(e["relative_path"] for e in entries)
    for e in entries:
        assert set(e) == set(corpus.ENTRY_FIELDS)
        assert e["relative_path"] and e["extension"] is not None
        assert isinstance(e["bytes"], int) and len(e["sha256"]) == 64
        assert not e["relative_path"].startswith("/") and ".." not in e["relative_path"].split("/")


def test_the_corpus_path_appears_in_no_tracked_artifact():
    from climrr.paths import CONFIG_PATH, load_local_paths

    texts = [
        (ARTIFACTS / name).read_text(encoding="utf-8")
        for name in ("corpus_manifest.json", "corpus_manifest.csv")
    ] + [
        (REPO_ROOT / "docs" / "LITERATURE_CORPUS_INVENTORY.md").read_text(encoding="utf-8"),
        (REPO_ROOT / "data" / "manifest.json").read_text(encoding="utf-8"),
    ]
    if CONFIG_PATH.is_file():
        root = load_local_paths().get(corpus.CONFIG_KEY)
        if root and not str(root).startswith("<"):
            parent = os.path.dirname(os.path.normpath(root))
            for text in texts:
                assert str(root) not in text and parent not in text
    for text in texts:
        assert "/" + "Users/" not in text and "/" + "home/" not in text and "/" + "eagle/" not in text
