"""Pre-D-025 state for frozen historical artifacts (M4-WP2 terms, M5-WP2 inputs).

D-025 changed `data/metadata/concept_map.yaml` and `src/climrr/compat.py` after
those artifacts were frozen. The artifacts stay as written; their recorded hashes
are checked against the files as committed at the M4-WP3 reviewed head.
"""

from __future__ import annotations

import hashlib
import subprocess

from climrr.paths import REPO_ROOT

PRE_D025_COMMIT = "6b2b5a6"
PRE_D025_CONCEPT_MAP_SHA256 = "6ec6b081658e82b5fba4171bcd3135f69ce71710a7a515f32cac83404ebd3664"


def committed_sha256(rel: str, commit: str = PRE_D025_COMMIT) -> str:
    blob = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=REPO_ROOT, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()
