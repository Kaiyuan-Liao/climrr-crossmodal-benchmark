"""Work package P5a (2026-11-23): where the superseded tool bytes are held, and the LITCORPUS-03 identity as received.

P5a bumps three tracked tools in place: `run_query.py` v3 -> v4 (opt-in lexicon mode), `litstatement_agent.py` v3 -> v4
(infra arm) and `litsynth_agent.py` v4.1 -> v5 (scope marking, question forms). The superseded files stay reproducible by
their bytes at `BASE_COMMIT` (the work package's base, pushed), each pinned by SHA-256; `materialize_tools` writes them into
a temporary `scripts/litcollect/` beside the working tree's other tools and `src`, so the tests of the earlier versions run
exactly as before. No model call; no table value.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from climrr import litsynth_run2 as s2
from climrr.paths import REPO_ROOT

BASE_COMMIT = "986232cf48fb03c12eb3e84c825caf022f739c2f"
TOOLS_REL = "scripts/litcollect"
#: The superseded bytes at BASE_COMMIT.
HELD = {
    "run_query.py": "5f56ee49f0da675f49ef490b506c030b307c693032e8be9097e499cf1c64030d",          # v3 (D-026)
    "litstatement_agent.py": "fd0e1dc391d46c691ab3b0b0d0190ba009f47a6e69e0eb6f0ececec441b6a9ea",  # v3 (pilot P2a)
    "litsynth_agent.py": "f41c0b9537912779076bfac81e1341f94e07bd87723177cc583350ce164d33d7",      # v4.1 (P3b; run 5)
}
SIBLINGS = ("softqa_agent.py", "litstatement_agent.py", "litgroup_agent.py", "build_index.py", "run_query.py")

#: D-070, as supplied by Alvi (2026-11-23); verified on Eagle at transfer, never in Git.
LITCORPUS03 = {
    "corpus_id": "LITCORPUS-03",
    "file": "critical_infrastructure_judged_relevant.tar.gz",
    "sha256": "6c6e21c2b07cfa0ef6a4098b19a0335949d3bf68a9a97d9f16b5f7904791ec76",
    "stated_size": "750 MB",
    "stated_files": 89497,
    "layout": "kept/<last two digits>/<id>.json",
    "selection": "external_model_judged",
    "eagle_location": "climrr-litcollect/sources/critical_infrastructure_v1/",
    "decision": "D-070",
}


def held_bytes(name: str) -> bytes:
    blob = s2.git_blob(BASE_COMMIT, f"{TOOLS_REL}/{name}")
    if hashlib.sha256(blob).hexdigest() != HELD[name]:
        raise ValueError(f"{name} at {BASE_COMMIT[:7]} differs from its pinned SHA-256 {HELD[name]}")
    return blob


def materialize_tools(*names: str) -> Path:
    """<tmp>/scripts/litcollect/ with `names` as held at BASE_COMMIT and every other sibling tool linked to the working
    tree's; <tmp>/src links to the repository's. Returns the tools directory."""
    root = Path(tempfile.mkdtemp(prefix="p5a_held_tools_"))
    tools = root / "scripts" / "litcollect"
    tools.mkdir(parents=True)
    for n in names:
        (tools / n).write_bytes(held_bytes(n))
    for n in SIBLINGS:
        if n not in names:
            (tools / n).symlink_to(REPO_ROOT / TOOLS_REL / n)
    (root / "src").symlink_to(REPO_ROOT / "src")
    return tools


#: P5a hotfix (2026-11-23): inventory_corpus.py v1 ran on Polaris (2026-11-24 00:33 UTC, the LITCORPUS-03 inventory whose
#: figures are in docs/LITCORPUS03_PROVENANCE.md §4) and was then replaced by v1.1; its bytes are held at the hotfix's base
#: commit (pushed). The other tools the hotfix bumps (run_query v4, litstatement_agent v4, litsynth_agent v5) never ran.
HOTFIX_BASE_COMMIT = "600c8887cb1bc27969c71de51c0040b125927dd9"
HELD_HOTFIX = {
    "inventory_corpus.py": "98ac67acf042ba488b17d7eea88e47a148ba3ab0b7aa2bf7d7c6a8f59e27bf81",   # v1 (P5a; ran on Polaris)
}


def held_bytes_hotfix(name: str) -> bytes:
    blob = s2.git_blob(HOTFIX_BASE_COMMIT, f"{TOOLS_REL}/{name}")
    if hashlib.sha256(blob).hexdigest() != HELD_HOTFIX[name]:
        raise ValueError(f"{name} at {HOTFIX_BASE_COMMIT[:7]} differs from its pinned SHA-256 {HELD_HOTFIX[name]}")
    return blob


#: P5a hotfix 2 (D-070b): run_query.py v4.1 ran on Polaris (2026-11-24 04:30 UTC, `runs/infra_lexicon_v2`, DR-CAND-INFRA-2;
#: the v2 diagnostic in docs/P5_INFRA_IMPACT_DESIGN.md §3b) and was then replaced by v4.2 (--rule DR-CAND-INFRA-3); its
#: bytes are held at the hotfix-2 base commit (pushed).
HOTFIX2_BASE_COMMIT = "9890a003847691913632f6d2cf667d6c887b2e4d"
HELD_HOTFIX2 = {
    "run_query.py": "819f223dc4739079e0b5d6fc7a3c2f5bd38078315d9f168b8ad79b7cf843dc42",   # v4.1 (P5a hotfix; ran on Polaris)
}


def held_bytes_hotfix2(name: str) -> bytes:
    blob = s2.git_blob(HOTFIX2_BASE_COMMIT, f"{TOOLS_REL}/{name}")
    if hashlib.sha256(blob).hexdigest() != HELD_HOTFIX2[name]:
        raise ValueError(f"{name} at {HOTFIX2_BASE_COMMIT[:7]} differs from its pinned SHA-256 {HELD_HOTFIX2[name]}")
    return blob
