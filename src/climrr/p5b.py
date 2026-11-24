"""Work package P5b (2026-11-23): where the superseded tool bytes are held.

P5b bumps two tracked tools in place: `litgroup_agent.py` v3 -> v3.1 (the impact prompt variant, D-075) and
`litsynth_agent.py` v5.1 -> v5.2 (rung-8 wording, D-073b, D-075). v3 is the file grouping run 2 ran (source commit
`7676e53`, unchanged until `BASE_COMMIT`); v5.1 never ran. Both stay reproducible by their bytes at `BASE_COMMIT` (the work
package's base, pushed), each pinned by SHA-256; `materialize_tools` writes them into a temporary `scripts/litcollect/`
beside the working tree's other tools and `src`, so the tests of the earlier versions run exactly as before. No model call.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from climrr import litsynth_run2 as s2
from climrr.paths import REPO_ROOT

BASE_COMMIT = "157e49d5135cbdb6c15cc4aee4ad286351e75061"
TOOLS_REL = "scripts/litcollect"
HELD = {
    "litgroup_agent.py": "e094aa5cbd4b981042fe07f165afc5d83ba77000ca718f185bcecee325d845f4",   # v3 (D-051; grouping run 2)
    "litsynth_agent.py": "8ff71879c234375299e74a7c7f1d8777f47d86350f3ccf218ed6910bc5aa1a43",   # v5.1 (P5a hotfix; never ran)
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
    root = Path(tempfile.mkdtemp(prefix="p5b_held_tools_"))
    tools = root / "scripts" / "litcollect"
    tools.mkdir(parents=True)
    for n in names:
        (tools / n).write_bytes(held_bytes(n))
    for n in SIBLINGS:
        if n not in names:
            (tools / n).symlink_to(REPO_ROOT / TOOLS_REL / n)
    (root / "src").symlink_to(REPO_ROOT / "src")
    return tools
