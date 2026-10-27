# Soft-QA review protocol, v1

**Status: frozen before any generation run (D-033).** Applies to Track C
(D-030) and Track D (D-031) candidates only. Every passage set in a quotation
block or list below is **verbatim from the GUIDANCE guardrail ruling of
2026-10-27**,
[`TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md`](TRACKC_TRACKD_SOFT_QA_GUARDRAILS_RULING.md);
the EXECUTOR's additions are marked *implementation*.

- Record schema: `data/metadata/softqa/candidate_schema_v1.json` (loader and
  validator `src/climrr/softqa.py`).
- Reviewer form: `data/metadata/softqa/review_form_v1.yaml`.
- Reviewer view: `scripts/softqa_review_view.py`.

## 1. Validity chain

> **candidate generation → deterministic provenance/consistency checks → human semantic review → accepted QA**

> **LLM proposes the semantic connection; deterministic code verifies the source mechanics; humans decide whether the cross-modal QA is scientifically acceptable.**

## 2. Status lifecycle

```text
llm_candidate
→ deterministic_pass
→ human_review
→ accepted
```

Side exits:

```text
rejected_pre_review
needs_second_review
needs_adjudication
rejected_human
accepted_after_edit
```

## 3. Deterministic prerequisites before human review

A candidate must first pass:

1. paper item ID check;
2. paper SHA-256 check;
3. JSON path check;
4. evidence-span exact re-slice;
5. table data SHA check;
6. table row/cell/column identity check;
7. table-side value recomputation;
8. concept term location check;
9. place term location check;
10. place-role recording;
11. template-slot validation;
12. deterministic answer recomputation;
13. verified/authorized-column check;
14. completeness of required provenance fields.

Failure on any mandatory mechanical check means:

```text
status = rejected_pre_review
```

not “send to a human and see.”

*Implementation.* `softqa_agent v1` (Track C proposal) runs items 1--4 and
8--10 and the proposal-field part of 14 at proposal time (its
`pre_review_check`); items 5--7, 11--13 and the table part of 14 run in the
deterministic table stage after the candidate structure is frozen. A candidate
reaches a human only when **all fourteen** have passed. The agent locates the
concept and place terms **anywhere in the paper** (first occurrence), not
within the passage.

## 4. Reviewer count

For ordinary candidates:

> **1 independent human reviewer is sufficient for acceptance.**

The reviewer must not be the same agent/process that generated the candidate.

The reviewer does **not** need to be blind to the QA itself.

However, the reviewer should inspect the evidence **before seeing agent
confidence or self-justification**.

## 5. Review order

1. paper passage;
2. table provenance and deterministic values;
3. QA pair;
4. candidate semantic annotations;
5. agent rationale/confidence last.

*Implementation.* `scripts/softqa_review_view.py` prints a candidate in this
order and withholds the agent's `link_rationale` and `confidence` unless
`--show-rationale` is given. Record the checklist judgments (§7) first, then
re-run with `--show-rationale`. Each view writes a run record noting whether the
rationale was shown.

## 6. Mandatory second reviewer

Require a second human reviewer when any of the following applies:

1. first reviewer selects `ambiguous`;
2. concept relation is soft/related rather than direct;
3. geography requires interpretation beyond explicit study area;
4. multi-concept QA;
5. cross-location comparison with differing spatial granularity;
6. scenario mismatch materially affects interpretation;
7. time mismatch materially affects interpretation;
8. answer depends on a derived statistic rather than a directly reported field;
9. paper passage is a background/cited claim rather than the paper's own result;
10. first reviewer requests escalation.

Second review should be independent of reviewer 1's disposition where
practical.

## 7. Human-review checklist

Require explicit judgments for:

1. **Paper fidelity** — does the passage actually state the paper-side fact?
2. **Table fidelity** — is the table-side fact exactly supported by the recorded cells/computation?
3. **Concept validity** — are the two sides sufficiently related for the QA type?
4. **Geography validity** — are both locations represented accurately?
5. **Temporal validity** — is the wording valid given the periods?
6. **Scenario validity** — is scenario mismatch disclosed rather than silently equated?
7. **Question validity** — is the question answerable from the recorded evidence?
8. **Answer validity** — is the proposed answer correct?
9. **No overclaim** — does the QA avoid implying stronger equivalence or causation than supported?
10. **Overall disposition** — `accept`, `accept_with_edit`, `ambiguous`, `reject`.

*Implementation.* Judgments 1--9 take `yes` / `no` / `unclear` (an EXECUTOR
choice of vocabulary; the ruling names the judgments, not their values). For
"No overclaim", `yes` means the QA **avoids** overclaim.

## 8. Adjudication

If reviewers disagree:

```text
status = needs_adjudication
```

A third/adjudicating reviewer resolves the candidate.

## 9. When a candidate is valid

A candidate counts as valid only after:

```text
human_status = accepted
```

or:

```text
human_status = accepted_after_edit
```

with the final edited QA frozen.

*Implementation.* `human_status` is the record's `human_review.final_status`,
and the record's `status` must equal it. The final question and answer are
`human_review.final_question` / `final_answer`, frozen separately from the
LLM proposal (kept verbatim in `agent_record`); every reviewer edit is kept in
`edit_history` (`softqa.consistency_errors` enforces both).

## 10. What a reviewer must not do

From the ruling's *Do not do yet*: do not use agent confidence as a substitute
for human review; do not approve only from the final QA without inspecting both
source records; do not interpret “soft-constrained” as “unconstrained.”
