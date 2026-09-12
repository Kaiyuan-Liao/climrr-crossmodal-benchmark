# M1 — Data grounding and metadata audit (WP2)

> **Current M1 report.** It supersedes
> [`M1_DATA_GROUNDING_REPORT.md`](M1_DATA_GROUNDING_REPORT.md), which is frozen
> as the WP1-stage record. **M1-WP2 is not finished.** It now covers **WP2a —
> machinery and documents** and **WP2b — the 2026-09-10 mentor meeting**. The
> meeting produced **no per-column answer**, so the criteria that were PENDING
> mentor input are now **NOT MET, with no further mentor input available**; the
> proposed way forward is **D-010, which awaits a GUIDANCE ruling**.

---

## 1. Milestone ID and title

**M1 — Data grounding and metadata audit**, work packages **M1-WP2a**
(metadata-resolution machinery and mentor brief) and **M1-WP2b** (record the
2026-09-10 mentor meeting).

**WP2a** built the mechanism by which a mentor answer becomes a traceable status
change, discharged the PDF-completeness action, and produced the document
Kaiyuan took to the meeting. **WP2b** recorded what the meeting produced and ran
one deterministic check. Authorised by the GUIDANCE M1-WP1 review ("Next bounded
objective") and recorded as D-009.

**Neither package changed any column status**, and WP2b was not authorised to.

## 2. Objective

Make every future metadata status change **traceable to a named source before
any such change is made**, and put the questions in front of the person who can
answer them.

WP2a's own success condition is that **no column status changes**. No answer
exists yet; a status that moved in this packet would mean the machinery had
invented one.

**Explicitly excluded**, and not done: any interpretation of a column; any
promotion of the EXECUTOR candidate maps into evidence; any labelling of `-9`
or any other repeated value as missing; phenomenon extraction; geographic
aggregation; thresholds; literature ingestion or retrieval; embeddings; bridge
generation or scoring; QA construction.

## 3. Repository commit SHA

Branch `work/m1-wp2`, local only. **Not pushed** — D-003 keeps the EXECUTOR off
the remote, and the branch merges to `main` only after GUIDANCE review.

| | |
| --- | --- |
| Branch | `work/m1-wp2` |
| Branched from | `62c9137` — the M1-WP1 merge on `main`, accepted by GUIDANCE (D-009) |
| WP2a commits | `c1015f5` (Phases A+B), `4427eaa` (Phase C), `2f2b094` (Phases D+E), `53421f0` (Q0 added by the COORDINATOR) |
| WP2b commit | this commit |
| Remote | `origin/main` at the WP1 merge. **`work/m1-wp2` was pushed by Kaiyuan** and `origin/work/m1-wp2` stands at `53421f0`; this WP2b commit is local until he pushes it. The EXECUTOR does not push (D-003). |

## 4. Data version and checksums

No raw data was modified, and none could be: every read verifies the manifest
first and fails closed (D-005, D-006).

| File | SHA-256 | Bytes | Shape | Storage |
| --- | --- | --- | --- | --- |
| `data/raw/FullData.csv` | `e87ac2cd0f345bc067e7a2ddbaa55f0336fb71e9c34f5f640d12da2aad3bf43e` | 296,407,423 | 62,834 × 275 | out of band, gitignored, pinned by hash (D-005) |
| `data/metadata/ClimRR_Metadata_and_Data_Dictionary.pdf` | `b28dff7cb74101b42e38518c692651ebaf76b156fae16284d5d7d638878823db` | 667,097 | 19 pages | tracked as authoritative metadata (D-002) |
| `data/metadata/resolutions.yaml` | `6cc802c3a8b683a1e8ad6a4be8117810b6f4edc636fd05135cffb8436290940d` | 3,425 | 0 records | tracked, new in this packet |
| `artifacts/profiles/dictionary_coverage.json` | `b61b39d68cb323e822391058dd4cee09680fd6742a60d4cc4de7ccba4b1f42d0` | — | 275 columns | regenerated in this packet |

`CLIMRR_ALLOW_MISSING_RAW=1` was never set.

## 5. Environment and execution location

All WP2a work ran **local only**. Nothing in this packet needs Sophia; the
cross-host reproduction that does is WP1's and stands unchanged.

| Host | Python | Platform | Location label |
| --- | --- | --- | --- |
| Local authoring machine | 3.11.16 | macOS-15.3-arm64 | `local` |

D-007 pin set, recorded in every run record's `pinned_libraries` with a
`matches_pin` flag: `pandas==3.0.5`, `numpy==2.4.6`, `pypdf==6.18.0`,
`pyyaml==6.0.3`, `pytest==9.1.1`, and **new in this packet**
`pypdfium2==5.13.0`. All six report `matches_pin: true` on this host.

**Action for Sophia:** re-run `pip install -r requirements.txt` in the
execution venv before the next pinned checkout. Until that happens `pypdfium2`
will report `matches_pin: false` there and `tests/test_runrecord.py` will fail —
which is the pin-drift detector working, not a defect.

## 6. Work completed

**Phase A — WP1 bookkeeping closed.** D-009 records the GUIDANCE PASS at
reviewed head `fceee7f` (merged as `62c9137`) with its four standing rulings.
The WP1 report carries a superseded-by line. `PROJECT_STATE.md` now reads
milestone M1, active task M1-WP2.

**Phase B — the text-empty PDF page was rendered and looked at.**
`scripts/rasterize_dictionary_pages.py` renders pages from the
manifest-verified PDF at 200 dpi with the newly pinned `pypdfium2` and writes
PNGs through a standard-library `zlib` writer rather than adding Pillow to the
pin set. Pages 2 and 4 were rendered alongside page 3 as a control.

**Phase C — the resolution machinery.** `data/metadata/resolutions.yaml` is
tracked and empty. `src/climrr/dictionary.py` gained the record schema, its
validator, and its application on top of the WP1 dictionary rules; a new status
`owner_confirmed` holds mentor- or owner-confirmed semantics.
`scripts/dictionary_coverage.py` now loads the resolutions file — required, not
optional, because an absent file must never look like "no answers yet" — and
records its hash. `scripts/status_diff.py` reports every movement from the WP1
baseline with the record and decision responsible.

**Phase D — `docs/MENTOR_BRIEF.md`**, the meeting document: plain language, the
19 questions in the GUIDANCE priority order, an empty answers table, and a
meeting log.

**Phase E — this report.**

### M1-WP2b — the 2026-09-10 meeting

**The meeting was recorded, and it changed nothing about the data.** Two
resolution records were written, both `effect: null` — the schema's form for an
answer that settles no column:

- **R-001 (Q0, `confirmed`):** the mentor has no additional metadata for the
  table — no newer data dictionary, no assembly document or script, no release
  note. **Q0 is closed, answered in the negative.**
- **R-002 (Q1–Q18, `stated_not_verified`):** a direction rather than a semantic —
  use the fields that are reliable or reasonably explainable, let reasoning fill
  in the rest, treat each row as one event, connect events to the literature, and
  show examples. **No per-column answer was given for any of Q1–Q18.**

Both statements are Kaiyuan's paraphrase of the mentor, relayed 2026-09-12, and
both are marked `statement_fidelity: paraphrase` rather than passed off as her
words.

**D-010 is proposed and nothing in it is implemented** — no `inferred_candidate`
status exists in the code, no column was interpreted, no pilot subset chosen, no
example built. It awaits a GUIDANCE ruling and Kaiyuan's approval.

**One deterministic check was run**, because Q11.4 does not need the mentor:
`scripts/check_objectid_pair.py` compares indices 235 and 236 row by row as raw
text. The result is in field 9 and it is not what the question assumed.

Two small schema additions were needed to record the meeting honestly:
`effect: null` for an answer that changes nothing, and `statement_fidelity` to
mark a paraphrase as one. Both are validated and tested; a null effect may not
also name columns, which would be a contradiction rather than a shorthand.

## 7. Deliverables and exact file paths

| Path | What it is |
| --- | --- |
| `data/metadata/resolutions.yaml` | the audit trail; schema and rules documented in the file; **2 records (R-001, R-002), both changing no column** |
| `src/climrr/dictionary.py` | extended: record schema, validator, `apply_resolutions`, `owner_confirmed` |
| `scripts/dictionary_coverage.py` | extended: loads resolutions, emits the new per-column fields |
| `scripts/status_diff.py` | new: per-column changes since the WP1 baseline, with invariant checks |
| `scripts/rasterize_dictionary_pages.py` | new: renders dictionary PDF pages to PNG |
| `scripts/check_objectid_pair.py` | **new (WP2b)**: the deterministic Q11.4 comparison |
| `tests/test_objectid_pair.py` | **new (WP2b)**: 9 tests on that comparison |
| `tests/test_resolutions.py` | new: 39 tests on the record schema and what it refuses |
| `tests/test_status_diff.py` | new: 9 tests on the diff and its three invariants |
| `artifacts/profiles/dictionary_coverage.json` | regenerated, with `status_baseline_wp1` and `resolution_refs` |
| `artifacts/profiles/status_diff.md` | generated: the diff, currently empty of changes |
| `artifacts/profiles/dictionary_page02.png` | control: the contents page |
| `artifacts/profiles/dictionary_page03.png` | **the finding**: the text-empty page, blank |
| `artifacts/profiles/dictionary_page04.png` | control: the Metadata narrative |
| `docs/MENTOR_BRIEF.md` | new: the meeting document; **the 2026-09-10 meeting log, answers table and status lines are filled in** |
| `docs/M1_WP1_GUIDANCE_REVIEW.md` | the GUIDANCE review, now tracked |
| `docs/DECISION_LOG.md` | D-009; **D-010 (PROPOSED, not in force)** |
| `docs/DATA_NOTES.md` | §1 gains the page-completeness finding and **the indices 235/236 comparison** |
| `docs/PROJECT_STATE.md` | rewritten for M1-WP2 |
| `reports/milestones/M1_DATA_GROUNDING_REPORT.md` | frozen at the WP1 stage |
| `requirements.txt` | `pypdfium2==5.13.0` added to the D-007 pin set |
| `reports/runs/20260909T22*` | WP2a: five run records — rasterise ×1, `dictionary_coverage` ×2, `status_diff` ×2 |
| `reports/runs/20260912T23*` | WP2b: `dictionary_coverage` ×2, `status_diff` ×2, `check_objectid_pair` ×2 |

## 8. Methods and rules that affect scientific meaning

**No rule applied in this packet changes what any datum means.** No filtering,
no aggregation, no unit conversion, no type coercion, no renaming, no
imputation, no exclusion. Every value read from the CSV was read as text.

Three rules were **added** that govern how meaning may be assigned in future,
and they are restrictions rather than licences:

1. **A resolution record can never produce `verified_from_dictionary`.** The
   validator refuses `effect.to: verified_from_dictionary` by name. That status
   means the tracked dictionary states the fact in its own words; an answer from
   a person — however authoritative — becomes `owner_confirmed`, a distinct
   status, so the difference stays visible downstream (D-009).
2. **A resolution record reaches a column only by naming it**, either by index
   or by naming a column-name stem the column demonstrably carries. Matching the
   prose of an answer against column names is refused. A record naming neither
   is valid and changes nothing.
3. **A column's WP1 status is frozen** in `status_baseline_wp1` at
   classification time and never written again, so the diff against WP1 is
   computed rather than remembered.

The EXECUTOR-authored candidate maps are untouched and remain
`candidate_section` / `candidate_section_source`. A section confirmed by a
resolution is recorded separately as `resolved_section` — the candidate never
becomes the confirmation.

## 9. Results with compact tables or examples

### Metadata status — unchanged, as intended

| Status | WP1 baseline | After WP2a | Change |
| --- | ---: | ---: | ---: |
| `verified_from_dictionary` | 21 | 21 | 0 |
| `owner_confirmed` | 0 | 0 | 0 |
| `partially_resolved` | 143 | 143 | 0 |
| `unresolved` | 28 | 28 | 0 |
| `structurally_observed_only` | 83 | 83 | 0 |
| **Total** | **275** | **275** | **0** |

`resolution_refs` is empty on all 275 columns; the two resolution records from
the 2026-09-10 meeting are applied and change nothing; `status_diff.py` reports
**0 columns changed of 275** with 0 invariant violations. The regenerated coverage JSON is **byte-identical to the WP1 one on
every pre-existing per-column field, across all 275 columns** — only the four
new fields and the new top-level summaries were added.

### Dictionary PDF page completeness — page 3 is blank

| Page | Rendered | PNG bytes | Channel min/max | What it is |
| --- | --- | ---: | --- | --- |
| 2 | 1700×2200 | 199,691 | 0 / 255 | table of contents |
| **3** | **1700×2200** | **15,888** | **255 / 255** | **blank — no marks of any kind** |
| 4 | 1700×2200 | 477,998 | 0 / 255 | opening of the "Metadata" narrative |

Page 3's pixels are a single uniform value across all three channels, and read
as an image it is a white page: no table, no field names, no figure, no scanned
content. Its extracted text is two space characters, which is the whole of its
content. Pages 2 and 4 render fully at the same settings, which is the control
that the renderer is not at fault. **No status changed and no manual
transcription file was created** — there was nothing to transcribe.

### The 2026-09-10 meeting, as recorded

| Record | Questions | Confidence | Effect | What it says |
| --- | --- | --- | --- | --- |
| `R-001` | Q0 | `confirmed` | none | No further metadata exists — no newer dictionary, no assembly document or script, no release note. |
| `R-002` | Q1–Q18 | `stated_not_verified` | none | Use a reliable subset, reason out the rest, treat each row as one event, show examples. A direction, not a column semantic. |

Both are paraphrases relayed by Kaiyuan on 2026-09-12 and are marked as such.
**Zero per-column answers were obtained**, and the status table above is
unchanged because of it, not in spite of it.

### Q11.4 — indices 235 and 236 are not the same column

The question assumed they might be duplicates. They are not, and they are not a
reordering either.

| Comparison | Result |
| --- | --- |
| Rows compared | 62,834 |
| Identical as text | **83** |
| Differing | **62,751** |
| Rows where both are empty | 83 |
| Rows where only one is empty | 0 |
| Empty-row sets identical | **yes** |
| Distinct values (235 / 236) | 62,752 / 62,752 |
| Value sets identical | **no** |
| Values in one column only | 703 in 235, 703 in 236 |

Every row on which they agree is a row on which both are empty. Identical
distinct counts and identical ranges — the WP1 facts that made "duplicate" look
plausible — turn out to be coincidence at the level of summary statistics. This
is a statement about characters and assigns no meaning: what either column *is*,
and which if either is a key, stays open as Q11.

### What a resolution record looks like

```yaml
- id: R-001
  date: 2026-09-10
  source: mentor
  source_detail: "Weekly one-on-one, 2026-09-10, relayed by Kaiyuan Liao"
  question_ids: [Q1]
  columns: []
  stem_section_map: {tempmaxann: "Temperature Maximum - Annual"}
  statement: "<the answer, verbatim as relayed>"
  effect: {field: status, to: owner_confirmed}
  decision_ref: D-010
  confidence: confirmed
```

## 10. Validation performed

| Check | Result |
| --- | --- |
| `pytest` | **261 passed** (198 at WP1; 48 new in WP2a, 15 more in WP2b) |
| `python scripts/verify_no_secrets_or_paths.py` | **0 hits**, 103 tracked text files |
| Manifest verification before every read | PASS, fail-closed, on every script run in both packages |
| `scripts/dictionary_coverage.py` | PASS — 275 classified, 0 statuses without a cited span |
| `scripts/status_diff.py` | PASS — 0 changes, 0 invariant violations, with 2 records applied |
| `scripts/check_objectid_pair.py` | PASS — 62,834 rows compared, 62,751 differing |
| Coverage JSON regression against the WP1 artifact | 0 differences on 275 × every pre-existing field |
| D-007 pin check | all six pins `matches_pin: true` locally |

The new tests are about what the machinery **refuses**: that a record promoting
two named columns changes exactly those two; that a record naming no columns and
no stem map changes nothing even when its prose is unambiguous about which family
it means; that `verified_from_dictionary` is unreachable from a record both at
validation and after loading a file; that an unknown key, a column index past the
end of the table, and a stem no column carries each raise rather than being
ignored.

## 11. Failures, rejected cases, and known limitations

- **`pypdfium2` had to be added to the pin set.** `pdftoppm` was checked for
  first, as the work package allows, and is absent on the local host. `pypdf`,
  already pinned, cannot rasterise. The cost is a sixth pin both hosts must
  carry, and **Sophia will fail its pin-drift test until it reinstalls** — stated
  in `requirements.txt`, `PROJECT_STATE.md` and field 5.
- **Pillow was rejected** as a seventh pin for the sake of writing three PNGs.
  A standard-library `zlib` writer does it instead. The trade is a small amount
  of hand-written PNG encoding in `scripts/rasterize_dictionary_pages.py`
  against a smaller dependency surface on two hosts.
- **The schema met its first real answers and did not quite fit them.** WP2a
  assumed every recorded answer would assign a status. Both answers from the
  2026-09-10 meeting assign none — one is a "no", the other a direction — so
  `effect: null` and `statement_fidelity` had to be added in WP2b. Neither
  loosens anything, but the need for them is evidence that the schema was
  designed against imagined answers rather than real ones, and more of that is
  likely.
- **Both recorded statements are paraphrases, not the mentor's words.** They are
  Kaiyuan's summary, relayed two days after the meeting, and are marked
  `statement_fidelity: paraphrase`. R-002 in particular carries a reading —
  "each row stands for one event" — that the mentor may not have said in those
  terms. The record says so; the risk is that a later reader takes the sentence
  as hers.
- **`confidence: stated` was recorded as `stated_not_verified`.** The work
  package's word is not in the schema's vocabulary; the mapping is exact in
  meaning but it is a mapping, made by the EXECUTOR, and it is noted here rather
  than left silent.
- **The `open_question` text on a column is not cleared when a resolution
  answers it.** It stays as the question the dictionary rules generated;
  `resolution_refs` is what says the column has since been answered. A reader
  going by the question text alone could think a resolved column is still open.
- **The Q11.4 result answers less than it appears to.** Establishing that
  indices 235 and 236 hold different values in every populated row rules out
  "duplicate" and "reordering". It says nothing about what either column is, and
  it makes the rest of Q11 harder rather than easier — there are now two
  unexplained identifier columns instead of one and its copy.
- **Nothing here was reproduced on Sophia.** Both packages are document,
  machinery and single-pass-check work; the cross-host claim is WP1's.

## 12. Deviations from the approved plan

### WP2a — three, all small:

1. **The work package's mentor-brief template repeats "Next meeting:" twice** in
   the header line. Written once.
2. **Pages 2 and 4 are committed, not only page 3.** The work package asks for
   page 3 under `artifacts/profiles/` and for 2 and 4 "for context". They are
   committed because they are the control that the blank page is blank — a
   finding of "nothing there" is worth much less without evidence that the
   renderer works. Combined they add ~680 KB.
3. **Two fields beyond those specified** were added per column,
   `resolved_section` and `resolved_section_source`, set only when a resolution
   carries an explicit stem-to-section map. Without them a confirmed section
   would have to be written into `candidate_section`, which would blur exactly
   the boundary GUIDANCE required be kept sharp.

### WP2b — three, all recorded above:

1. **Two schema fields were added** — `effect: null` and `statement_fidelity` —
   because neither answer from the meeting assigns a status and neither is
   verbatim. Without them the records would have had to claim an effect they do
   not have, or pass a paraphrase off as quotation.
2. **`confidence: stated` was mapped to `stated_not_verified`**, the schema's
   existing term for the same thing.
3. **The Q11.4 check also compares value *sets*, not only rows.** The work
   package asks for row-wise equality and the empty-row sets. Set comparison was
   added because row-wise inequality alone cannot distinguish "two different
   columns" from "the same identifiers in a different order" — and on this data
   the distinction turned out to matter: 703 values occur in one column and not
   the other, which the row-wise result alone would not have shown.

No scope was added, no scientific definition invented, and no open decision
resolved by picking a plausible answer. **Nothing in D-010 was implemented.**

## 13. Open decisions and mentor questions

**The situation changed on 2026-09-10, and not in the direction this package was
built for.** The machinery in WP2a assumes answers arrive and get recorded. The
meeting established that, for this project, **they will not**.

### What is now closed

- **Q0 — closed, answered in the negative (R-001).** There is no newer data
  dictionary, no assembly document or script, no release note. The 19-page
  alpha-release PDF is the whole of the authoritative documentation. **Two of
  the three evidence types D-009 accepts for promoting a stem-to-section
  mapping are therefore unavailable, not merely unobtained.**
- **Q11.4 — answered deterministically**, from the bytes rather than the mentor.
  Indices 235 and 236 are neither duplicates nor a reordering (field 9).

### What is open, and why it cannot be closed the way WP2a planned

- **Q1–Q18: mentor, no answer available (R-002).** All eighteen were put; none
  was answered per column. What was given instead was a direction: use the
  fields that are reliable or reasonably explainable, let reasoning fill in the
  rest, treat each row as one event, and show examples.
- **D-010 is the proposed response, and it is PROPOSED — not in force, and
  nothing in it is implemented.** It would introduce a fifth status,
  `inferred_candidate`, for semantics reached by reasoning from names, value
  patterns and dictionary spans, always with the reasoning and spans recorded;
  confine interpretation to a pilot subset; build 2–3 example event records from
  real rows with every assumption listed; and make **mentor sign-off on an
  example** the thing that promotes the columns it uses to `owner_confirmed`.
  Everything else would stay `unresolved`, explicitly and permanently.

### Decisions required, in order

1. **GUIDANCE ruling on D-010.** It is a real loosening of D-009's premise and
   it is not the EXECUTOR's to take. Two specific authorisations are needed: the
   `inferred_candidate` status itself, and **hand-worked example construction
   ahead of M2** — building event records from real rows is an M2 deliverable,
   and doing it during M1 is a deliberate reordering.
2. **Kaiyuan's approval** of D-010 as project owner.
3. **Confirmation from the mentor that "one row = one event" is the right
   grain.** This is **Kaiyuan's reading** of her direction, not a statement she
   made in those terms, and it is the grain the whole proposed pilot rests on.
   The way to confirm it is to show her examples, which is itself gated on
   decision 1.

**Nothing is outstanding for Kaiyuan except decision 2 and relaying decision 3**,
plus the Sophia reinstall noted in field 5.

## 14. Proposed gate status

The nine M1-WP2 acceptance criteria, quoted verbatim from
`docs/M1_WP1_GUIDANCE_REVIEW.md` § "Acceptance criteria".

| # | Criterion (verbatim) | Status | Evidence |
| --- | --- | --- | --- |
| 1 | "Every status change from the WP1 baseline is tied to a specific authoritative answer/source, date, and provenance record." | **MET for the machinery; PENDING mentor input for content** | The mechanism exists and is enforced: `resolutions.yaml`, `status_baseline_wp1`, `resolution_refs`, `status_diff.py` with three invariants, 48 tests. There are 0 changes to tie, because there are 0 answers. |
| 2 | "The Q1 stem-to-section mapping is confirmed, corrected, or explicitly left unverified." | **MET as "explicitly left unverified"; no mentor answer is available** | Q1 was put at the 2026-09-10 meeting and not answered (R-002); R-001 establishes that no document exists that could answer it. It is left unverified explicitly in `dictionary.py`, `METADATA_QUESTIONS.md` and the new standing table there. The criterion allows this outcome; what it does not allow is calling it resolved. A path to resolution is proposed as **D-010, pending**. |
| 3 | "Q2–Q4 remain documented as dictionary defects until authoritative correction exists." | **MET, and unchanged** | `METADATA_QUESTIONS.md` Q2–Q4 stand as written; nothing in this packet touched them. They are questions 10–12 in the brief. |
| 4 | "High-impact undocumented families relevant to later pilot planning are resolved or explicitly unresolved." | **MET as "explicitly unresolved"; no mentor answer is available** | `precipdaily_*` (Q7, 56 columns) and the FWI classes (Q8, 30 columns) were put and not answered (R-002), and R-001 rules out a document that would describe them. Both stay explicitly unresolved and are marked so in the standing table. Resolution path proposed as **D-010, pending**. |
| 5 | "Geographic fields needed for later aggregation have evidence-backed definitions." | **NOT MET; no mentor answer is available** | Q10 and Q11 were put and not answered (R-002). **No geographic column has an evidence-backed definition, and none can be given from available evidence.** The one advance is negative and deterministic: indices 235 and 236 are not the same column (Q11.4, field 9), which removes a candidate explanation rather than supplying one. This criterion cannot be met without either D-010 or an answer that is not coming. |
| 6 | "Sentinel/fill-code semantics are evidence-backed; candidate sentinels remain distinct from confirmed missing-value rules." | **NOT MET for "evidence-backed"; MET for the distinction; no mentor answer is available** | Q17 and Q9 were put and not answered (R-002). **No sentinel semantic is evidence-backed.** The distinction the criterion protects is intact: the 24 flagged columns remain a frequency flag that asserts nothing, and `-9` at index 117 is still unlabelled (D-009 ruling 3). Nothing was reclassified to make the number look better. |
| 7 | "The known text-empty PDF page is checked for extraction completeness." | **MET** | Page 3 rendered at 200 dpi and inspected: blank, uniform colour, no marks. Pages 2 and 4 as control. `artifacts/profiles/dictionary_page0{2,3,4}.png`, run record `20260909T220506Z_local_rasterize_dictionary_pages`, `DATA_NOTES.md` §1, D-009. |
| 8 | "The per-column dictionary continues to distinguish deterministic structural facts, dictionary-verified facts, mentor/owner-confirmed facts, and unresolved fields." | **MET for the machinery; PENDING mentor input for content** | Four-way distinction is now explicit in the data model: `structurally_observed_only`, `verified_from_dictionary`, the new `owner_confirmed`, and `unresolved`/`partially_resolved`. `owner_confirmed` is unreachable from the dictionary rules and `verified_from_dictionary` unreachable from a resolution — both enforced and tested. 0 columns are `owner_confirmed` today. |
| 9 | "The WP2 report identifies which fields are sufficiently grounded to be considered for later pilot selection, without yet extracting phenomena." | **NOT MET; deliberately not attempted** | Naming pilot-ready fields today would rest on the 21 dictionary-verified columns alone, or would mean promoting the candidate maps — the false-closure risk GUIDANCE named first. **Selecting the pilot subset is exactly what D-010 proposes, and D-010 is not ruled on.** Doing it here would be the EXECUTOR deciding an open question by acting on it. |

**Proposed status for M1-WP2 as a whole: BLOCKED — WP2a and WP2b complete as
issued; M1 cannot be finished on the evidence available.** No milestone gate is
proposed.

The honest summary: **five of the nine criteria turn on external answers that
now definitively will not arrive** (R-001), and the mentor's direction is to
proceed by reasoning instead. Three criteria (1, 3, 7) and the machinery half of
8 are met. Two (2, 4) are met only in their "explicitly unresolved" form, which
the criteria permit but which leaves 86 high-impact columns undescribed. Three
(5, 6, 9) are **NOT MET and unmeetable as things stand.**

**What GUIDANCE is asked to rule on is therefore not this packet but D-010** —
whether interpretation by recorded reasoning, confined to a pilot subset and
promoted only by mentor sign-off on worked examples, is an acceptable way to
reach the M1 gate. If it is not, the alternative is an M1 gate that accepts 21
verified columns and names the other 254 permanently undocumented.

## 15. Proposed next bounded objective

**Obtain the GUIDANCE ruling on D-010, then — only if it is granted — build the
worked examples.**

The ruling comes first because everything downstream depends on it and none of it
is the EXECUTOR's to assume. If D-010 is approved, the next bounded objective is:
**construct 2–3 example event records from real rows of `FullData.csv`**, each
listing every assumption it rests on, each naming the columns it uses, and each
carrying the recorded reasoning and dictionary spans behind every interpreted
column — for Kaiyuan to put in front of the mentor. Her sign-off on an example
becomes an ordinary resolution record naming those columns, and only those
columns move.

If D-010 is refused, the next bounded objective is instead to close M1 with the
21 dictionary-verified columns and an explicit, permanent record of the other
254 as undocumented.
