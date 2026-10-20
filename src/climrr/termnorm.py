"""Track B orthographic normalization of model-proposed terms (D-027, ruling B4).

Applies the frozen `data/metadata/litcollect/normalization_table_v1.yaml` and
nothing else: `>`, `<`, degree notation and `%` become words; every other
character is left as it is. No semantic paraphrase, stemming, abbreviation
expansion or synonym inference. The original term is always returned beside
the normalized one, with the ids of the rules that fired.

Not wired into `survey_driver.py` (the driver is unchanged in the bookkeeping
package); run 2 is where it will be applied.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from climrr.paths import REPO_ROOT

TABLE_PATH = REPO_ROOT / "data" / "metadata" / "litcollect" / "normalization_table_v1.yaml"


def load_table(path: Path = TABLE_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _replace(term: str, match: str, word: str) -> str:
    out, i = "", 0
    while True:
        j = term.find(match, i)
        if j < 0:
            return out + term[i:]
        out += term[i:j]
        after = term[j + len(match):]
        left = " " if out and out[-1].isalnum() else ""
        right = " " if after and after[0].isalnum() else ""
        out += left + word + right
        i = j + len(match)


def normalize(term: str, table: dict | None = None) -> dict:
    """`{"original", "normalized", "rule_ids"}` for one term under the table."""
    table = table or load_table()
    text, fired = term, []
    for rule in table["rules"]:
        for form in rule["forms"]:
            if form["match"] in text:
                text = _replace(text, form["match"], form["replace"])
                if rule["id"] not in fired:
                    fired.append(rule["id"])
    return {"original": term, "normalized": text, "rule_ids": fired}
