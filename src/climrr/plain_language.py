"""Plain-language phrases for the graded text of an item (D-060, D-061, D-062; mentor 2026-11-13; work package P3a).

`data/metadata/benchmark/plain_language_v1.yaml` is pinned by SHA-256 in `data/manifest.json`; `load` reads it only when
its bytes match the pin. `quantity` gives a family's plain quantity phrase (no threshold), `hedge` the hedge words for an
evidence strength (D-062: >= 2 independent papers or a review -> "research shows / has shown"; one paper -> "research
suggests"; never "one study"), and `model_view` the block the seed packets v4 hand the synthesis agent.

No model call; no column interpreted.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry
from climrr.paths import REPO_ROOT

PLAIN_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "plain_language_v1.yaml"
#: v1a (P3a hotfix, D-053b): the fire-weather quantity "fire-weather danger (how hot, dry and windy conditions favour fire)"
#: and the family's `never_write` words; read by the seed packets v4a. v1 stays the evidence for packets v4.
PLAIN_V1A_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "plain_language_v1a.yaml"


def load(path: Path = PLAIN_PATH, manifest_path: Path = MANIFEST_PATH) -> dict:
    path = Path(path)
    pin = load_entry(path.name, manifest_path)["sha256"]
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    return dict(yaml.safe_load(path.read_text(encoding="utf-8")), sha256=pin)


def quantity(family: str, plain: dict | None = None) -> str:
    return (plain or load())["families"][family]["quantity"]


def hedge(strength: str, plain: dict | None = None) -> list[str]:
    """The hedge words a sentence resting on groups of `strength` uses (D-062)."""
    return list((plain or load())["hedges"][strength])


def model_view(family: str, scenario: str, horizon: str, plain: dict | None = None) -> dict:
    """The phrases a packet's graded text must use, for its pattern's family, scenario and horizon. `never_write`: the
    hedge words never used, then (v1a) the family's own `never_write` words."""
    plain = plain or load()
    fam = plain["families"][family]
    return {"version": plain["version"], "quantity": fam["quantity"], "quantity_short": fam["quantity_short"],
            "scenario": plain["scenario"][scenario], "horizon": plain["horizon"][horizon],
            "hedge_multi_source_or_review": plain["hedges"]["multi_source_supported"],
            "hedge_single_source": plain["hedges"]["single_source_supported"],
            "never_write": list(plain["hedges"]["never"]) + list(fam.get("never_write") or [])}
