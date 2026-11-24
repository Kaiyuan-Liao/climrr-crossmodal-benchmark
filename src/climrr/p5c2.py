"""Work package litsynth v5.4 (2026-11-24; D-075a): where the superseded synthesis-agent bytes are held.

The work package bumps `litsynth_agent.py` v5.3 -> v5.4 in place (rung-8 answer shape v2, post-checks v3.5). v5.3 **ran**
(Polaris `litsynth/infra_run1`, 2026-11-24, packets v1a; run 1, superseded). It stays reproducible by its bytes at
`BASE_COMMIT` (the work package's base, pushed), pinned by SHA-256; `materialize_tools` (the P5b mechanism) writes it into a
temporary `scripts/litcollect/` beside the working tree's other tools and `src`, so the v5.3 tests run exactly as before.
No model call.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from climrr import litsynth_run2 as s2
from climrr.paths import REPO_ROOT

BASE_COMMIT = "b860658873bd4d80ae9500587e23b18d4778c387"
TOOLS_REL = "scripts/litcollect"
HELD = {
    "litsynth_agent.py": "1be4ba2a6aec418b2729f6d165a3ed159208a0d31b786ad92413d7d195f43edd",   # v5.3 (P5c hotfix; ran: infra run 1)
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
    root = Path(tempfile.mkdtemp(prefix="p5c2_held_tools_"))
    tools = root / "scripts" / "litcollect"
    tools.mkdir(parents=True)
    for n in names:
        (tools / n).write_bytes(held_bytes(n))
    for n in SIBLINGS:
        if n not in names:
            (tools / n).symlink_to(REPO_ROOT / TOOLS_REL / n)
    (root / "src").symlink_to(REPO_ROOT / "src")
    return tools
