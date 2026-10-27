"""Boundary behaviour of the secrets/paths scanner.

Every probe string is assembled from fragments at runtime. The literal forms
must not appear in this file's source, or the scanner would flag its own test
suite -- the same self-reference problem the scanner solves for itself by
exemption. Fragments keep this file scannable and unexempt.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from verify_no_secrets_or_paths import scan_line, scan_text  # noqa: E402

# --- probes, built so this file's source contains no literal match ---
KEY = "sk" + "-abc123"
GH_KEY = "ghp" + "_abcdef123456"
USER_PATH = "/User" + "s/x"
EAGLE_PATH = "/eagl" + "e/ARAIA/kkyliao"
HOME_PATH = "/hom" + "e/kkyliao"
WORD_TOKEN = "tok" + "en"
WORD_PASSWORD = "pass" + "word"

# Benign prose that used to trip the scanner and must not any more.
BENIGN_TASK = "XModBench builds its benchmark around aligned tri-modal instances. Task" + "-specific templates then apply."
BENIGN_TOKENS = "* API keys, " + "tok" + "ens, credentials, or private connection details"


@pytest.mark.parametrize(
    "text",
    [
        KEY,
        f"OPENAI_KEY={KEY}",
        GH_KEY,
        USER_PATH,
        f"repo lives at {USER_PATH}",
        EAGLE_PATH,
        HOME_PATH,
        f"{WORD_PASSWORD}=hunter2",
        f"the {WORD_TOKEN} is stored elsewhere",
        WORD_TOKEN,
    ],
)
def test_forbidden_strings_are_caught(text):
    assert scan_line(text), f"scanner missed a forbidden string: {text!r}"


@pytest.mark.parametrize(
    "text",
    [
        BENIGN_TASK,
        BENIGN_TOKENS,
        "Task" + "-specific",
        "a " + "tok" + "enizer splits text into " + "tok" + "ens",
        "the " + "pass" + "words section of the policy",
        "ri" + "sk-" + "averse planning",
        "compressed upload artifact, not the file size",
    ],
)
def test_benign_prose_is_not_flagged(text):
    assert scan_line(text) == [], f"false positive on benign prose: {text!r}"


def test_user_path_is_matched_case_sensitively():
    """Regression: the pattern was compared against a lowercased line, so the
    capitalised macOS path could never match and the check was silently dead."""
    assert scan_line(USER_PATH), "the macOS user path must be caught"
    labels = scan_line(USER_PATH)
    assert any("user path" in label for label in labels)


def test_key_prefix_must_start_a_token():
    assert scan_line(KEY)
    assert scan_line("a" + KEY) == []
    assert scan_line("9" + KEY) == []
    assert scan_line("(" + KEY)


def test_key_prefix_needs_key_material_after_it():
    assert scan_line("sk" + "- a hyphenated sentence break") == []


def test_credential_words_match_whole_words_only():
    assert scan_line(WORD_TOKEN)
    assert scan_line(WORD_TOKEN + "s") == []
    assert scan_line("sub" + WORD_TOKEN) == []
    assert scan_line(WORD_PASSWORD)
    assert scan_line(WORD_PASSWORD + "s") == []


def test_matching_is_case_insensitive_for_credentials():
    assert scan_line(WORD_PASSWORD.upper())
    assert scan_line(WORD_TOKEN.capitalize())
    assert scan_line(KEY.upper())


def test_scan_text_reports_line_numbers_and_labels():
    text = "\n".join(["clean line", BENIGN_TOKENS, f"{WORD_PASSWORD}=x"])
    hits = scan_text(text)
    assert len(hits) == 1
    lineno, label, snippet = hits[0]
    assert lineno == 3
    assert "credential" in label
    assert snippet.startswith(WORD_PASSWORD)


def test_the_tracked_blueprint_needs_no_exemption():
    """The charter contains 'Task-specific' and an 'API keys, tokens' list.
    Both must pass on their own merits, not via a carve-out."""
    blueprint = REPO_ROOT / "docs" / "BLUEPRINT.md"
    if not blueprint.is_file():
        pytest.skip("docs/BLUEPRINT.md not present in this clone")
    assert scan_text(blueprint.read_text(encoding="utf-8")) == []


# --- the hash-pinned credential-word exemption (D-026; the D-027 ruling added; D-033 the Track C agent) ---

def test_word_exemption_is_exactly_the_delivered_tools_and_the_d027_ruling():
    import verify_no_secrets_or_paths as v

    assert set(v.WORD_EXEMPTIONS) == {
        "scripts/litcollect/survey_driver.py", "scripts/litcollect/probe_alcf_inference.py",
        "scripts/litcollect/softqa_agent.py", "docs/M4_WP4_TRACKB_GUIDANCE_RULING.md"}
    for rel in v.WORD_EXEMPTIONS:
        path = REPO_ROOT / rel
        assert v.word_exempt(path)
        assert any(h[1] == v.WORD_EXEMPTION_LABEL for h in scan_text(path.read_text(encoding="utf-8")))
        assert v.scan_file(path) == []


def test_word_exemption_lapses_when_the_file_changes(tmp_path, monkeypatch):
    import verify_no_secrets_or_paths as v

    rel = "scripts/litcollect/survey_driver.py"
    copy = tmp_path / rel
    copy.parent.mkdir(parents=True)
    copy.write_bytes((REPO_ROOT / rel).read_bytes() + b"\n")
    monkeypatch.setattr(v, "REPO_ROOT", tmp_path.resolve())
    assert not v.word_exempt(copy)
    assert any(h[1] == v.WORD_EXEMPTION_LABEL for h in v.scan_file(copy))


def test_word_exemption_filters_only_the_credential_word(tmp_path, monkeypatch):
    import hashlib

    import verify_no_secrets_or_paths as v

    f = tmp_path / "tool.py"
    f.write_text(f"x = {WORD_TOKEN!r}\ny = {USER_PATH!r}\nz = {KEY!r}\n", encoding="utf-8")
    monkeypatch.setattr(v, "REPO_ROOT", tmp_path.resolve())
    monkeypatch.setattr(v, "WORD_EXEMPTIONS", {"tool.py": hashlib.sha256(f.read_bytes()).hexdigest()})
    labels = [h[1] for h in v.scan_file(f)]
    assert v.WORD_EXEMPTION_LABEL not in labels
    assert len(labels) == 2  # the path and the key prefix are still reported
