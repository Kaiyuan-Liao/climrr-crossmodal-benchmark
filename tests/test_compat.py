"""M5-WP1: frozen inputs, compatibility rules on synthetic fixtures, and the real matrix's shape.

The rule tests use **synthetic claims** against the real prototype records, so
the positive path is exercised even though the real claim set may never reach
it. No test here asserts how many real pairs are compatible (ruling action 14,
criterion 18).
"""

from __future__ import annotations

import copy
import json

import pytest

from climrr import compat


def _frozen() -> dict:
    return json.loads(compat.INPUTS_PATH.read_text(encoding="utf-8"))


# --- Phase A: frozen inputs -----------------------------------------------------


def test_the_frozen_inputs_still_match_every_referenced_record():
    compat.verify_inputs()


def test_the_freeze_pins_27_claims_3_prototypes_and_81_pairs():
    f = _frozen()
    assert (f["n_claims"], f["n_prototypes"], f["n_pairs"]) == (27, 3, 81)
    assert len({c["claim_id"] for c in f["claims"]}) == 27
    assert [p["prototype_id"] for p in f["prototypes"]] == list(compat.PROTOTYPE_IDS)
    assert all(c["claim_validation_status"] == "single_reader_provisional" for c in f["claims"])


def test_a_changed_claim_record_fails_the_freeze():
    tampered = copy.deepcopy(_frozen())
    tampered["claims"][0]["claim_record_sha256"] = "0" * 64
    with pytest.raises(compat.FreezeError):
        compat.verify_inputs(tampered)


def test_a_changed_prototype_record_fails_the_freeze():
    tampered = copy.deepcopy(_frozen())
    tampered["prototypes"][2]["prototype_record_sha256"] = "0" * 64
    with pytest.raises(compat.FreezeError):
        compat.verify_inputs(tampered)


def test_record_hash_ignores_key_order_but_not_content():
    assert compat.record_sha256({"a": 1, "b": "x"}) == compat.record_sha256({"b": "x", "a": 1})
    assert compat.record_sha256({"a": 1}) != compat.record_sha256({"a": 2})
