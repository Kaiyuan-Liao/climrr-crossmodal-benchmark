"""Grouping agent `scripts/litcollect/litgroup_agent.py` v2 and its input partitions (pilot P2b; D-048, D-049).

Runs the agent end to end against a local mock chat-completions server on three synthetic
partitions: a clean grouping, one whose reply repeats an id (the partition fails and writes no
group), and one whose label carries a digit no member has (the group fails, the partition
passes). v2: every group and singleton carries `claim_about`; a value outside the enum fails
that record only. Checks that the model sees local ids and sentences only (no statement id, no paper
id), strengths under D-046, group numbering, restart, and the pins.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from climrr import litgroups as lgr
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

TOOLS = REPO_ROOT / "scripts" / "litcollect"
AGENT = TOOLS / "litgroup_agent.py"
AGENT_SHA256 = "09edaa4e09826af7d9abf79714dc72bc4e98a5e5c9712e587bd00cbfea22f961"
TEMPLATE_SHA256 = "ac135f00570d75f487c7bd414a662a18c271861afa5f026e3e17b3c4fb752ae7"
#: The filled system prompts (template with each arm's family phrase), recorded in D-049.
FILLED_SHA256 = {"extreme_heat_v1": "2c4a1dd0fa2c89db0096878f01c0be02e0e731df5f99f6580bdb4cb9356df311",
                 "fire_weather_v1": "1134a3083df2cd7d340d741b93e598455b8799c839389b3f9b1f634c54e4b7c7"}


def _meta(sid, paper, role="core_candidate", pt="own_finding", canon=None):
    return {"statement_id": sid, "paper_item_id": paper, "canonical_paper": canon or paper, "evidence_role": role,
            "passage_type": pt, "direction": "unspecified", "region_class": "other"}


PARTS = [
    {"partition_id": "extreme_heat_v1.driver", "arm": "extreme_heat_v1", "family_phrase": lgr.FAMILY_PHRASE["extreme_heat_v1"],
     "statement_type": "driver", "split_by": [], "n_statements": 4,
     "statements": [{"local_id": "S001", "sentence": "Humidity raises the heat index."},
                    {"local_id": "S002", "sentence": "Higher humidity increases heat index values."},
                    {"local_id": "S003", "sentence": "Urban surfaces store heat."},
                    {"local_id": "S004", "sentence": "Moist air raises the heat index."}],
     "meta": {"S001": _meta("LS-7001-01", "7001"), "S002": _meta("LS-7002-01", "7002", "cited_candidate"),
              "S003": _meta("LS-7003-01", "7003", "background_consensus_candidate", "background"),
              "S004": _meta("LS-7005-01", "7005", canon="7001")}},           # a duplicate of 7001 under D-046
    {"partition_id": "extreme_heat_v1.caveat", "arm": "extreme_heat_v1", "family_phrase": lgr.FAMILY_PHRASE["extreme_heat_v1"],
     "statement_type": "caveat", "split_by": [], "n_statements": 2,
     "statements": [{"local_id": "S001", "sentence": "Models disagree."}, {"local_id": "S002", "sentence": "Data are sparse."}],
     "meta": {"S001": _meta("LS-7004-01", "7004"), "S002": _meta("LS-7004-02", "7004")}},
    {"partition_id": "fire_weather_v1.driver", "arm": "fire_weather_v1", "family_phrase": lgr.FAMILY_PHRASE["fire_weather_v1"],
     "statement_type": "driver", "split_by": [], "n_statements": 2,
     "statements": [{"local_id": "S001", "sentence": "Dry fuels raise fire danger."}, {"local_id": "S002", "sentence": "Wind raises fire danger."}],
     "meta": {"S001": _meta("LS-8001-01", "8001", pt="review_synthesis"), "S002": _meta("LS-8002-01", "8002", "background_consensus_candidate", "background")}},
]
REPLIES = {
    "extreme_heat_v1.driver": {"groups": [{"label": "Humidity raises the heat index.", "member_ids": ["S001", "S002"], "rationale": "Same driver.",
                                           "claim_about": "hazard_change_mechanism"},
                                          {"label": "Moist air raises the heat index.", "member_ids": ["S004"], "rationale": "x",
                                           "claim_about": "heat_mechanism"}],                    # outside the enum
                               "singletons": [{"id": "S003", "claim_about": "impact_or_exposure"}]},
    "extreme_heat_v1.caveat": {"groups": [{"label": "Uncertainty.", "member_ids": ["S001", "S002"], "rationale": "x", "claim_about": "other"}],
                               "singletons": [{"id": "S002", "claim_about": "other"}]},
    "fire_weather_v1.driver": {"groups": [{"label": "3 factors raise fire danger.", "member_ids": ["S001", "S002"], "rationale": "x",
                                           "claim_about": "hazard_change_mechanism"}], "singletons": []},
}


class _Mock:
    def __init__(self):
        self.calls: list[tuple[str, str, dict]] = []
        mock = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                system, user = body["messages"][0]["content"], body["messages"][1]["content"]
                mock.calls.append((system, user, body))
                pid = next(p["partition_id"] for p in PARTS if p["family_phrase"] in system and p["statements"][0]["sentence"] in user)
                out = json.dumps({"choices": [{"message": {"role": "assistant", "content": json.dumps(REPLIES[pid])},
                                               "finish_reason": "stop"}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/v1"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()


def _cmd(parts, out, url):
    return [sys.executable, str(AGENT), "--partitions", str(parts), "--out", str(out), "--base-url", url, "--model", "mock-model",
            "--source-commit", "abc1234", "--backoff", "0,0,0"]


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    pytest.importorskip("duckdb")
    base = tmp_path_factory.mktemp("litgroup")
    parts, out = base / "partitions.jsonl", base / "out"
    parts.write_text("".join(json.dumps(p) + "\n" for p in PARTS), encoding="utf-8")
    env = {**os.environ, "TOK" + "EN": "test-value"}
    mock = _Mock()
    first = subprocess.run(_cmd(parts, out, mock.url) + ["--limit", "1"], env=env, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    n_first = len(mock.calls)
    second = subprocess.run(_cmd(parts, out, mock.url), env=env, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    groups = [json.loads(x) for x in (out / "groups.jsonl").read_text().splitlines()]
    yield {"out": out, "mock": mock, "n_first": n_first, "groups": groups, "summary": json.loads((out / "summary.json").read_text())}
    mock.server.shutdown()


def _agent():
    pytest.importorskip("duckdb")
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location("litgroup_agent_v1", AGENT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_agent_is_pinned():
    assert sha256_file(AGENT) == AGENT_SHA256


def test_the_system_prompt_is_the_ruling_text():
    a = _agent()
    assert a.GENERATOR_VERSION == "litgroup_agent v2"
    assert hashlib.sha256(a.SYSTEM_PROMPT_TEMPLATE.encode("utf-8")).hexdigest() == TEMPLATE_SHA256
    for arm, h in FILLED_SHA256.items():
        assert hashlib.sha256(a.system_prompt(lgr.FAMILY_PHRASE[arm]).encode("utf-8")).hexdigest() == h
    assert a.CLAIM_ABOUT == ("hazard_change_mechanism", "hazard_definition_or_measurement", "impact_or_exposure", "method_or_data", "other")
    for c in a.CLAIM_ABOUT:
        assert f"- {c}: " in a.SYSTEM_PROMPT_TEMPLATE
    assert ("hazard_change_mechanism: why or how the hazard quantity itself changes — e.g. humidity, temperature, circulation, "
            "land surface") in a.SYSTEM_PROMPT_TEMPLATE
    assert a.SYSTEM_PROMPT_TEMPLATE.startswith("You are grouping sentences that each state a general claim about <family>.")
    assert a.SYSTEM_PROMPT_TEMPLATE.endswith("Every input id appears exactly once.")
    assert "/eagl" + "e/" not in AGENT.read_text(encoding="utf-8") and "/User" + "s/" not in AGENT.read_text(encoding="utf-8")


def test_the_model_sees_local_ids_and_sentences_only(run):
    assert run["n_first"] == 1 and len(run["mock"].calls) == 3                     # restart skipped the finished partition
    for system, user, body in run["mock"].calls:
        assert body["temperature"] == 0 and body["max_tokens"] == 6000 and "<family>" not in system
        assert "LS-" not in user and not any(p in user for p in ("7001", "7002", "7003", "7004", "7005", "8001", "8002"))
        assert user.startswith("SENTENCES (") and "S001: " in user


def test_a_clean_partition_yields_groups_singletons_and_d046_strengths(run):
    g = {x["group_id"]: x for x in run["groups"]}
    a, b, c = g["LG-extreme_heat_v1-driver-001"], g["LG-extreme_heat_v1-driver-002"], g["LG-extreme_heat_v1-driver-003"]
    assert a["member_ids"] == ["LS-7001-01", "LS-7002-01"] and a["evidence_strength"] == "multi_source_supported"
    assert b["kind"] == "group" and b["checks"]["single_member"] and b["evidence_strength"] == "single_source_supported"
    assert c["kind"] == "singleton" and c["label"] is None and c["evidence_strength"] == "background_only"
    assert a["status"] == "deterministic_pass" and a["model"] == "mock-model" and len(a["prompt_hash"]) == 64
    assert a["claim_about"] == "hazard_change_mechanism" and c["claim_about"] == "impact_or_exposure" and c["status"] == "deterministic_pass"


def test_a_claim_about_outside_the_enum_fails_that_record_only(run):
    g = {x["group_id"]: x for x in run["groups"]}
    b = g["LG-extreme_heat_v1-driver-002"]
    assert b["claim_about"] == "heat_mechanism" and b["status"] == "deterministic_fail" and b["checks"]["failed"] == ["claim_about_pass"]
    s = run["summary"]
    assert s["claim_about_fail"] == 1 and s["by_claim_about"]["hazard_change_mechanism"] == 2 and s["by_claim_about"]["impact_or_exposure"] == 1
    assert s["groups_label_fail"] == 1                                       # the fire label digit only, not the claim failure


def test_a_repeated_id_fails_the_partition_and_writes_no_group(run):
    r = json.loads((run["out"] / "extreme_heat_v1.caveat" / "result.json").read_text())
    assert r["status"] == "deterministic_fail" and r["checks"]["duplicate_ids"] == ["S002"] and r["groups"] == []
    assert not any(x["partition_id"] == "extreme_heat_v1.caveat" for x in run["groups"])
    assert run["summary"]["partitions_fail"][0]["partition_id"] == "extreme_heat_v1.caveat"


def test_a_label_digit_absent_from_members_fails_the_group_only(run):
    [g] = [x for x in run["groups"] if x["partition_id"] == "fire_weather_v1.driver"]
    assert g["status"] == "deterministic_fail" and g["checks"]["label_digits_not_in_members"] == ["3"]
    assert g["evidence_strength"] == "review_supported"
    assert run["summary"]["partitions_pass"] == 2


def test_raw_text_is_kept(run):
    r = json.loads((run["out"] / "extreme_heat_v1.driver" / "result.json").read_text())
    assert r["raw_response"].startswith("{") and r["finish_reason"] == "stop"
    assert (run["out"] / "extreme_heat_v1.driver" / "response.json").is_file()


# --- partitions ---------------------------------------------------------------------------------


def test_an_oversized_partition_splits_by_direction_then_region_then_chunks():
    ids = [f"LS-{i:04d}-01" for i in range(300)]
    direction = {i: ("increase" if n < 100 else "unspecified") for n, i in enumerate(ids)}
    region = {i: ("other" if n < 250 else "global") for n, i in enumerate(ids)}
    parts = lgr.split_partition(ids, direction, region)
    assert [(lab, len(p)) for lab, p in parts] == [(["direction=increase"], 100),
                                                   (["direction=unspecified", "region_class=global"], 50),
                                                   (["direction=unspecified", "region_class=other", "chunk=1of2"], 75),
                                                   (["direction=unspecified", "region_class=other", "chunk=2of2"], 75)]
    assert sorted(i for _, p in parts for i in p) == sorted(ids)


def test_the_frozen_partitions():
    parts = [json.loads(x) for x in lgr.PARTITIONS_PATH.read_text(encoding="utf-8").splitlines()]
    assert len(parts) == 11 and sum(p["n_statements"] for p in parts) == 747
    assert max(p["n_statements"] for p in parts) <= lgr.MAX_PARTITION
    assert [p["partition_id"] for p in parts if p["split_by"]] == ["extreme_heat_v1.mechanism.increase", "extreme_heat_v1.mechanism.unspecified"]
    for p in parts:
        assert set(p["statements"][0]) == {"local_id", "sentence"}
        assert [s["local_id"] for s in p["statements"]] == sorted(p["meta"])
        assert all(s["sentence"].strip() for s in p["statements"])
    # self-contained for the Polaris run: every entering statement once, with its id and sentence, at the pinned hash
    ids = [m["statement_id"] for p in parts for m in p["meta"].values()]
    assert len(ids) == len(set(ids)) == 747
    summary = json.loads(lgr.PARTITIONS_SUMMARY_PATH.read_text(encoding="utf-8"))
    assert sha256_file(lgr.PARTITIONS_PATH) == summary["partitions_file"]["sha256"]
