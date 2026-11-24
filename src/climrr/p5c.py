"""Work package P5c hotfix (2026-11-24): where the superseded synthesis-agent bytes are held.

The hotfix bumps `litsynth_agent.py` v5.2 -> v5.3 in place (D-073c two-hop wording, post-checks v3.4, item schema v2a for
rung-8 items; D-077). v5.2 never ran. It stays reproducible by its bytes at `BASE_COMMIT` (the work package's base, pushed),
pinned by SHA-256; `materialize_tools` (the P5b mechanism) writes it into a temporary `scripts/litcollect/` beside the working
tree's other tools and `src`, so the v5.2 tests run exactly as before. No model call.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from climrr import litsynth_run2 as s2
from climrr.paths import REPO_ROOT

BASE_COMMIT = "a549ea97875491bc18ad5bdf3a5a2832cb8720ca"
TOOLS_REL = "scripts/litcollect"
HELD = {
    "litsynth_agent.py": "e057c0ff3fecc4a7fe7be29d7aa059a238b750acfaaad3b3a285bd199fedb687",   # v5.2 (P5b; never ran)
}
SIBLINGS = ("softqa_agent.py", "litstatement_agent.py", "litgroup_agent.py", "build_index.py", "run_query.py")


def held_bytes(name: str) -> bytes:
    blob = s2.git_blob(BASE_COMMIT, f"{TOOLS_REL}/{name}")
    if hashlib.sha256(blob).hexdigest() != HELD[name]:
        raise ValueError(f"{name} at {BASE_COMMIT[:7]} differs from its pinned SHA-256 {HELD[name]}")
    return blob


def materialize_tools(*names: str) -> Path:
    """<tmp>/scripts/litcollect/ with `names` as held at BASE_COMMIT and every other sibling tool linked to the working
    tree's; <tmp>/src links to the repository's. Returns the tools directory."""
    root = Path(tempfile.mkdtemp(prefix="p5c_held_tools_"))
    tools = root / "scripts" / "litcollect"
    tools.mkdir(parents=True)
    for n in names:
        (tools / n).write_bytes(held_bytes(n))
    for n in SIBLINGS:
        if n not in names:
            (tools / n).symlink_to(REPO_ROOT / TOOLS_REL / n)
    (root / "src").symlink_to(REPO_ROOT / "src")
    return tools
