"""Resolve machine-specific paths from the untracked local config.

`config/local_paths.yaml` is gitignored: it is the only place real absolute
paths are allowed to live. `config/local_paths.example.yaml` is the tracked
template and contains placeholders only.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "local_paths.yaml"
EXAMPLE_PATH = REPO_ROOT / "config" / "local_paths.example.yaml"

_MISSING_MSG = (
    "Local path configuration not found: {path}\n"
    "\n"
    "This file is machine-specific and is deliberately not tracked by Git.\n"
    "Create it by copying the tracked template and replacing every\n"
    "<PLACEHOLDER> with a real absolute path for this machine:\n"
    "\n"
    "    cp {example} {path}\n"
    "\n"
    "Then edit {path}. Never commit it."
)


class LocalPathsMissingError(FileNotFoundError):
    """Raised when config/local_paths.yaml has not been created on this machine."""


def config_path() -> Path:
    return CONFIG_PATH


def load_local_paths(path: Path | None = None) -> dict:
    """Load the local path configuration, or fail with an actionable message."""
    cfg_path = Path(path) if path is not None else CONFIG_PATH
    if not cfg_path.is_file():
        raise LocalPathsMissingError(
            _MISSING_MSG.format(path=cfg_path, example=EXAMPLE_PATH)
        )
    with cfg_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{cfg_path} must contain a YAML mapping, got {type(data).__name__}")
    return data


def get(key: str, path: Path | None = None) -> str:
    """Return one configured value, with a clear error if the key is absent."""
    data = load_local_paths(path)
    if key not in data:
        raise KeyError(
            f"'{key}' is not set in {path or CONFIG_PATH}. "
            f"See {EXAMPLE_PATH} for the expected keys."
        )
    return data[key]


def repo_relative(p: Path | str) -> str:
    """Express a path relative to the repo root; run records never store absolutes."""
    resolved = Path(p).resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return resolved.name
