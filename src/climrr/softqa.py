"""Soft-QA candidate records (D-029, D-033): load and validate the frozen schema; map Track C agent output onto it.

`data/metadata/softqa/candidate_schema_v1.json` is the frozen record schema: the
seven field groups of the GUIDANCE guardrail ruling
(`docs/TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md`), field for field, plus two
supplementary blocks --- `agent_record` (the generator's output verbatim) and
`mapping` (what is still pending, and which agent values the schema vocabulary
refused). Table-side and human-review fields are null until their stage.

`validate` checks a record against the schema with a small built-in validator
(the subset of JSON Schema 2020-12 the schema uses; no new dependency) and then
`consistency_errors` checks the lifecycle rules the schema cannot express ---
e.g. a `deterministic_pass` with a failed mechanical check. `map_trackc` turns one
`scripts/litcollect/softqa_agent.py` candidate into a schema record: the agent's
`proposal`, `evidence`, `concept_hit`, `place_hit` and `pre_review_checks` fill
the fields they correspond to; everything the agent did not produce stays null,
and `mapping.pending_stages` names the stage that will fill it.

Nothing here calls a model, reads table values, or touches the concept map,
column statuses or compatibility rules.

**Track C run on Polaris** (the agent is tracked byte-identical to the delivered
file, so its invocation is documented here rather than in its own docstring).
`$CLIMRR_REPO` is a checkout of the pinned commit; run from the litcollect root
so `index/…` and `softqa/run1` stay relative and no absolute path lands in any
output (the Track B convention); the ALCF inference credential is in the
environment variable the agent's `main` reads, as for the Track B driver:

    cd "$LITCOLLECT_ROOT_POLARIS"
    PYTHONPATH="$CLIMRR_REPO/src" python "$CLIMRR_REPO/scripts/litcollect/softqa_agent.py" \\
        --candidates "$CLIMRR_REPO/data/metadata/softqa/trackc_candidates_v1.json" \\
        --units "$CLIMRR_REPO/data/metadata/softqa/units_definitions_v1.json" \\
        --qa-types "$CLIMRR_REPO/data/metadata/softqa/qa_types_v1.json" \\
        --index index/full_705k_v2_filtered --out softqa/run1 \\
        --source-commit "$(git -C "$CLIMRR_REPO" rev-parse HEAD)"

Defaults: Metis `gpt-oss-120b`, temperature 0, `--max-chars 90000` (a longer
paper is truncated and flagged). Restartable: a paper with `result.json` is
skipped; `candidates.jsonl` and `summary.json` are rebuilt from every
`result.json` at the end of each invocation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

SOFTQA_DIR = REPO_ROOT / "data" / "metadata" / "softqa"
SCHEMA_PATH = SOFTQA_DIR / "candidate_schema_v1.json"
SCHEMA_VERSION = "softqa_candidate_v1"
MAPPER_VERSION = "softqa.map_trackc v1"

GROUPS = ("candidate_identity", "paper_provenance", "table_provenance", "soft_link",
          "generation_controls", "deterministic_validation", "human_review")

#: The ruling's status lifecycle: main path, then side exits.
LIFECYCLE = ("llm_candidate", "deterministic_pass", "human_review", "accepted",
             "rejected_pre_review", "needs_second_review", "needs_adjudication",
             "rejected_human", "accepted_after_edit")
VALID_FINAL = ("accepted", "accepted_after_edit")

#: Stage names used in `mapping.pending_stages`.
STAGE_TABLE = "table_computation (deterministic; after the candidate structure is frozen)"
STAGE_AUDIT = "c_g_t_s_d_audit (deterministic matrix, recorded for audit only)"
STAGE_HUMAN = "human_review (docs/SOFTQA_REVIEW_PROTOCOL.md)"
STAGE_INGEST = "ingest (from the generator input provenance)"
STAGE_NOT_PRODUCED = "not produced by softqa_agent v1; stage unassigned"

#: Mechanical checks whose failure means `rejected_pre_review` (agent v1 mandatory set).
TRACKC_MANDATORY_CHECKS = ("span_reslice_pass", "concept_location_pass", "place_location_pass", "place_role_recorded")


class SchemaError(ValueError):
    """A record does not satisfy the frozen schema."""


# --- loader and validator ----------------------------------------------------

def load_schema(path: Path = SCHEMA_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def schema_sha256(path: Path = SCHEMA_PATH) -> str:
    return sha256_file(path)


_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _same(a, b) -> bool:
    """JSON equality: False is not 0, True is not 1."""
    return type(a) is type(b) and a == b if isinstance(a, bool) or isinstance(b, bool) else a == b


def _check(value, sch: dict, where: str, errors: list[str]) -> None:
    if "const" in sch and not _same(value, sch["const"]):
        errors.append(f"{where}: must be {sch['const']!r}, got {value!r}")
    if "enum" in sch and not any(_same(value, e) for e in sch["enum"]):
        errors.append(f"{where}: {value!r} not in {sch['enum']!r}")
    if "type" in sch:
        types = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        if not any(_TYPES[t](value) for t in types):
            errors.append(f"{where}: type {type(value).__name__} not in {types}")
            return
    if isinstance(value, str):
        if len(value) < sch.get("minLength", 0):
            errors.append(f"{where}: shorter than {sch['minLength']}")
        if "pattern" in sch and not re.search(sch["pattern"], value):
            errors.append(f"{where}: does not match {sch['pattern']}")
    if _TYPES["number"](value) and "minimum" in sch and value < sch["minimum"]:
        errors.append(f"{where}: below {sch['minimum']}")
    if isinstance(value, dict):
        props = sch.get("properties", {})
        for k in sch.get("required", []):
            if k not in value:
                errors.append(f"{where}: missing required field {k!r}")
        extra = sch.get("additionalProperties", True)
        for k, v in value.items():
            if k in props:
                _check(v, props[k], f"{where}.{k}", errors)
            elif extra is False:
                errors.append(f"{where}: unexpected field {k!r}")
            elif isinstance(extra, dict):
                _check(v, extra, f"{where}.{k}", errors)
    if isinstance(value, list) and "items" in sch:
        for i, v in enumerate(value):
            _check(v, sch["items"], f"{where}[{i}]", errors)


def schema_errors(record: dict, schema: dict | None = None) -> list[str]:
    errors: list[str] = []
    _check(record, schema or load_schema(), "$", errors)
    return errors


def consistency_errors(record: dict) -> list[str]:
    """Lifecycle rules the schema cannot express."""
    errs: list[str] = []
    st = record["status"]
    dv, pp, hr = record["deterministic_validation"], record["paper_provenance"], record["human_review"]
    if st == "rejected_pre_review":
        if record["deterministic_validation"]["pre_review_status"] not in ("rejected_pre_review", None):
            errs.append("status rejected_pre_review but pre_review_status says otherwise")
        return errs
    if st == "llm_candidate":
        return errs
    # Every later status has passed the pre-review check.
    if dv["pre_review_status"] != "deterministic_pass":
        errs.append(f"status {st} requires pre_review_status deterministic_pass")
    for k in TRACKC_MANDATORY_CHECKS:
        if dv[k] is not True:
            errs.append(f"status {st} requires {k} true")
    for k in ("paper_sha256", "json_path", "span_start", "span_end", "verbatim_passage"):
        if pp[k] is None:
            errs.append(f"status {st} requires paper_provenance.{k}")
    if pp["span_start"] is not None and pp["span_end"] is not None and pp["verbatim_passage"] is not None:
        if pp["span_end"] - pp["span_start"] != len(pp["verbatim_passage"]):
            errs.append("span length differs from the verbatim passage length")
    if st in VALID_FINAL:
        for k in ("reviewer_1_id", "reviewer_1_date", "reviewer_1_disposition", "final_question", "final_answer"):
            if hr[k] is None:
                errs.append(f"status {st} requires human_review.{k}")
        if hr["final_status"] != st:
            errs.append(f"status {st} requires human_review.final_status {st}")
        if st == "accepted_after_edit" and not hr["edit_history"]:
            errs.append("accepted_after_edit requires a non-empty edit_history")
        if hr["requires_second_review"] and hr["reviewer_2_disposition"] is None:
            errs.append("second review required but reviewer_2_disposition is null")
    return errs


def validate(record: dict, schema: dict | None = None) -> dict:
    """Raise SchemaError on any schema or lifecycle violation; return the record."""
    errs = schema_errors(record, schema)
    if not errs:
        errs = consistency_errors(record)
    if errs:
        raise SchemaError(f"{record.get('candidate_identity', {}).get('candidate_id', '?')}: " + "; ".join(errs))
    return record


# --- Track C mapper ------------------------------------------------------------

def _empty(schema: dict) -> dict:
    return {g: {k: None for k in schema["properties"][g]["properties"]} for g in GROUPS}


def _fits(value, sch: dict) -> bool:
    errs: list[str] = []
    _check(value, sch, "", errs)
    return not errs


def map_trackc(agent: dict, schema: dict | None = None) -> dict:
    """Map one softqa_agent v1 candidate (a `candidates.jsonl` line) onto candidate_schema_v1.

    A value the agent produced goes into its schema field if it fits the field's
    vocabulary; otherwise the field stays null and the value is listed in
    `mapping.invalid_agent_values` (it stays verbatim in `agent_record`). Fields
    the agent does not produce stay null, with their stage in `mapping.pending_stages`.
    """
    schema = schema or load_schema()
    rec = _empty(schema)
    pending: dict[str, str] = {}
    invalid: dict[str, object] = {}
    proposal = agent.get("proposal") if isinstance(agent.get("proposal"), dict) else {}
    evidence = agent.get("evidence") if isinstance(agent.get("evidence"), dict) else None
    checks = agent.get("pre_review_checks") if isinstance(agent.get("pre_review_checks"), dict) else {}

    def put(group: str, field: str, value) -> None:
        sch = schema["properties"][group]["properties"][field]
        if value is None or _fits(value, sch):
            rec[group][field] = value
        else:
            invalid[f"{group}.{field}"] = value

    ci = rec["candidate_identity"]
    for f in ci:
        ci[f] = agent.get(f)

    for f, v in (("paper_item_id", agent.get("paper_item_id")), ("paper_sha256", agent.get("paper_sha256")),
                 ("verbatim_passage", agent.get("verbatim_passage"))):
        put("paper_provenance", f, v)
    if evidence is not None:
        for f in ("json_path", "span_start", "span_end"):
            put("paper_provenance", f, evidence.get(f))
    for f in ("paper_geography", "paper_geography_role", "paper_time", "paper_scenario", "paper_concept"):
        put("paper_provenance", f, proposal.get(f))
    pending["paper_provenance.claim_or_passage_type"] = STAGE_NOT_PRODUCED

    put("table_provenance", "unit_id_or_template_id", proposal.get("unit_id"))
    for f in rec["table_provenance"]:
        if f != "unit_id_or_template_id":
            pending[f"table_provenance.{f}"] = STAGE_TABLE

    for f in ("qa_type", "link_rationale", "concept_relation", "geography_relation", "unmatched_dimensions"):
        put("soft_link", f, proposal.get(f))
    for f in ("time_relation", "scenario_relation", "direction_relation", "assumptions"):
        pending[f"soft_link.{f}"] = STAGE_NOT_PRODUCED
    pending["soft_link.c_g_t_s_d_audit"] = STAGE_AUDIT

    gc = rec["generation_controls"]
    gc["table_values_visible_to_generator"] = agent.get("table_values_visible_to_generator")
    gc["answer_visible_to_generator"] = agent.get("answer_visible_to_generator")
    pending["generation_controls.retrieval_terms"] = STAGE_INGEST
    pending["generation_controls.retrieval_source"] = STAGE_INGEST

    for f in TRACKC_MANDATORY_CHECKS:
        put("deterministic_validation", f, checks.get(f))
    put("deterministic_validation", "pre_review_status", agent.get("pre_review_status"))
    for f in ("table_recompute_pass", "slot_validation_pass", "verified_columns_only"):
        pending[f"deterministic_validation.{f}"] = STAGE_TABLE

    for f in rec["human_review"]:
        pending[f"human_review.{f}"] = STAGE_HUMAN

    return {
        "schema_version": SCHEMA_VERSION,
        "status": agent.get("status"),
        **rec,
        "agent_record": agent,
        "mapping": {"mapper_version": MAPPER_VERSION, "pending_stages": pending, "invalid_agent_values": invalid},
    }


def load_agent_candidates(path: Path) -> list[dict]:
    """The agent's `candidates.jsonl`, one record per line."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(ln) for ln in lines if ln.strip()]


def map_and_validate_jsonl(path: Path) -> list[dict]:
    schema = load_schema()
    return [validate(map_trackc(a, schema), schema) for a in load_agent_candidates(path)]
