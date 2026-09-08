"""Local-path config loading and its failure message."""

from __future__ import annotations

import pytest

from climrr.paths import EXAMPLE_PATH, LocalPathsMissingError, load_local_paths, repo_relative


def test_missing_config_raises_with_actionable_message(tmp_path):
    missing = tmp_path / "local_paths.yaml"
    with pytest.raises(LocalPathsMissingError) as excinfo:
        load_local_paths(missing)
    message = str(excinfo.value)
    assert str(missing) in message
    assert "local_paths.example.yaml" in message


def test_loads_a_mapping(tmp_path):
    cfg = tmp_path / "local_paths.yaml"
    cfg.write_text("location: local\nscratch_dir: /tmp/scratch\n", encoding="utf-8")
    assert load_local_paths(cfg)["location"] == "local"


def test_non_mapping_config_is_rejected(tmp_path):
    cfg = tmp_path / "local_paths.yaml"
    cfg.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_local_paths(cfg)


def test_example_config_is_tracked_and_uses_placeholders():
    text = EXAMPLE_PATH.read_text(encoding="utf-8")
    assert EXAMPLE_PATH.is_file()
    assert "<LOCAL_REPO_ROOT>" in text


def test_repo_relative_strips_the_repo_root():
    assert repo_relative("data/raw/FullData.csv") == "data/raw/FullData.csv"


def test_repo_relative_falls_back_to_basename_outside_the_repo(tmp_path):
    outside = tmp_path / "elsewhere.csv"
    outside.write_text("x", encoding="utf-8")
    assert repo_relative(outside) == "elsewhere.csv"
