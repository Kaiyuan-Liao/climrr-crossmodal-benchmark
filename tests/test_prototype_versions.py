"""D-018: P-STATE-1 v2 is a versioned provenance correction; v1 stays immutable."""

from __future__ import annotations

import json

from climrr import compat
from climrr.paths import REPO_ROOT

V1 = compat.prototype_file("P-STATE-1")
V2 = V1.with_name("P-STATE-1.v2.json")
DICT_LINES = (REPO_ROOT / "data" / "metadata" / "dictionary_extracted.txt").read_text(encoding="utf-8").splitlines()


def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_v2_changes_no_climrr_value():
    v1, v2 = _load(V1), _load(V2)
    for key in ("V", "D", "M", "G", "H", "C", "S"):
        assert v2[key] == v1[key], key


def test_v2_declares_its_version_and_points_at_v1():
    v1, v2 = _load(V1), _load(V2)
    assert (v2["schema_version"], v2["version"], v2["supersedes"], v2["amendment"]) == (
        "p0-prototype", 2, "P-STATE-1 v1", "D-018")
    assert v2["v1_record_sha256"] == compat.record_sha256(v1)
    from climrr.checksums import sha256_file
    assert v2["v1_file_sha256"] == sha256_file(V1)


def test_every_window_span_quotes_its_dictionary_line_and_states_the_years():
    v2 = _load(V2)
    for role, expected in (("baseline", (1995, 2004)), ("future", (2085, 2094))):
        per = v2["T"]["per_role"][role]
        assert (per["window"]["start"], per["window"]["end"]) == expected
        joined = " ".join(s["quote"] for s in per["window_spans"])
        for s in per["window_spans"]:
            assert DICT_LINES[s["line"] - 1].strip() == s["quote"]
        assert str(expected[0]) in joined and str(expected[1]) in joined
        assert per["window_status"] == _load(compat.prototype_file("P-CELL-1"))["T"]["per_role"][role]["status"]


def test_the_compat_rules_read_the_v2_windows_and_the_frozen_m5wp1_input_still_names_v1():
    pv = compat.prototype_values(_load(V2))
    assert (pv["time"]["baseline"], pv["time"]["future"]) == ([1995, 2004], [2085, 2094])
    assert compat.prototype_values(_load(V1))["time"]["future"] is None
    frozen = compat.verify_inputs()
    assert [p["prototype_file"] for p in frozen["prototypes"]][-1].endswith("P-STATE-1.json")
