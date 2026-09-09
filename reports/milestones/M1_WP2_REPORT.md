# M1 — Data grounding and metadata audit (WP2)

> **Current M1 report.** It supersedes
> [`M1_DATA_GROUNDING_REPORT.md`](M1_DATA_GROUNDING_REPORT.md), which is frozen
> as the WP1-stage record. **M1-WP2 is not finished**: this packet covers
> **WP2a — machinery and documents**, and most acceptance criteria are
> **PENDING mentor input** by design, not by omission.

---

## 1. Milestone ID and title

**M1 — Data grounding and metadata audit**, work package **M1-WP2a**:
metadata-resolution machinery and mentor brief.

M1-WP2 is split. **WP2a — this packet —** builds the mechanism by which a
mentor answer becomes a traceable status change, discharges the PDF-completeness
action, and produces the document Kaiyuan takes to the meeting. **WP2b applies
the answers** as they arrive, one commit per meeting. Authorised by the GUIDANCE
M1-WP1 review ("Next bounded objective") and recorded as D-009.

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
| Commits in this packet | Phase A+B `c1015f5`, Phase C `4427eaa`, Phase D+E — this commit |
| Remote | `origin/main` at the WP1 merge; `work/m1-wp2` exists nowhere but this clone |

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
18 questions in the GUIDANCE priority order, an empty answers table, and a
meeting log.

**Phase E — this report.**

## 7. Deliverables and exact file paths

| Path | What it is |
| --- | --- |
| `data/metadata/resolutions.yaml` | the audit trail; schema and rules documented in the file; **0 records** |
| `src/climrr/dictionary.py` | extended: record schema, validator, `apply_resolutions`, `owner_confirmed` |
| `scripts/dictionary_coverage.py` | extended: loads resolutions, emits the new per-column fields |
| `scripts/status_diff.py` | new: per-column changes since the WP1 baseline, with invariant checks |
| `scripts/rasterize_dictionary_pages.py` | new: renders dictionary PDF pages to PNG |
| `tests/test_resolutions.py` | new: 39 tests on the record schema and what it refuses |
| `tests/test_status_diff.py` | new: 9 tests on the diff and its three invariants |
| `artifacts/profiles/dictionary_coverage.json` | regenerated, with `status_baseline_wp1` and `resolution_refs` |
| `artifacts/profiles/status_diff.md` | generated: the diff, currently empty of changes |
| `artifacts/profiles/dictionary_page02.png` | control: the contents page |
| `artifacts/profiles/dictionary_page03.png` | **the finding**: the text-empty page, blank |
| `artifacts/profiles/dictionary_page04.png` | control: the Metadata narrative |
| `docs/MENTOR_BRIEF.md` | new: the meeting document |
| `docs/M1_WP1_GUIDANCE_REVIEW.md` | the GUIDANCE review, now tracked |
| `docs/DECISION_LOG.md` | D-009 |
| `docs/DATA_NOTES.md` | §1 gains the page-completeness finding |
| `docs/PROJECT_STATE.md` | rewritten for M1-WP2 |
| `reports/milestones/M1_DATA_GROUNDING_REPORT.md` | frozen at the WP1 stage |
| `requirements.txt` | `pypdfium2==5.13.0` added to the D-007 pin set |
| `reports/runs/20260909T22*` | five run records: rasterise ×1, `dictionary_coverage` ×2, `status_diff` ×2 |

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

`resolution_refs` is empty on all 275 columns; `resolutions_applied` is empty;
`status_diff.py` reports **0 columns changed of 275** with 0 invariant
violations. The regenerated coverage JSON is **byte-identical to the WP1 one on
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
| `pytest` | **246 passed** (198 at WP1; 48 new) |
| `python scripts/verify_no_secrets_or_paths.py` | **0 hits**, 103 tracked text files |
| Manifest verification before every read | PASS, fail-closed, on all three script runs that read pinned data |
| `scripts/dictionary_coverage.py` | PASS — 275 classified, 0 statuses without a cited span |
| `scripts/status_diff.py` | PASS — 0 changes, 0 invariant violations |
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
- **The machinery is entirely untested against a real answer.** Every test uses
  a synthetic record. The first real mentor answer may not decompose into
  "columns" and "stem map" as cleanly as the schema assumes — an answer of the
  form "all the precipitation columns" names no columns at all, and by rule will
  move nothing until someone writes down which columns are meant. That is the
  intended behaviour and it will feel like friction the first time.
- **The `open_question` text on a column is not cleared when a resolution
  answers it.** It stays as the question the dictionary rules generated;
  `resolution_refs` is what says the column has since been answered. A reader
  going by the question text alone could think a resolved column is still open.
- **Nothing here was reproduced on Sophia.** WP2a is document and machinery work
  and the cross-host claim is WP1's.

## 12. Deviations from the approved plan

Three, all small:

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

No scope was added, no scientific definition invented, and no open decision
resolved by picking a plausible answer.

## 13. Open decisions and mentor questions

**Everything material in WP2 is open, and all of it belongs to the mentor or the
ClimRR authors.** The 18 questions are in `docs/METADATA_QUESTIONS.md` with
column indices and PDF line numbers, and restated for a non-specialist reader in
`docs/MENTOR_BRIEF.md` in GUIDANCE's priority order: **Q1, Q7, Q8, Q10–Q12,
Q17, Q9, Q18, then Q2–Q6 and Q13–Q16.**

Per GUIDANCE, Q1 must be answered as the **actual mapping** — which prefix is
which variable — not as agreement that the candidate map looks right. The brief
phrases it that way.

**For GUIDANCE, one question:** is the split of WP2 into a machinery package and
an answer-application package acceptable as a way to reach the M1 gate, given
that the answer half cannot be scheduled by this project? If a single mentor
meeting does not resolve the priority questions, M1 will need either a further
resolution package or a gate that accepts named columns as permanently
undocumented.

**Nothing is outstanding for Kaiyuan except the meeting itself**, and the Sophia
reinstall noted in field 5.

## 14. Proposed gate status

The nine M1-WP2 acceptance criteria, quoted verbatim from
`docs/M1_WP1_GUIDANCE_REVIEW.md` § "Acceptance criteria".

| # | Criterion (verbatim) | Status | Evidence |
| --- | --- | --- | --- |
| 1 | "Every status change from the WP1 baseline is tied to a specific authoritative answer/source, date, and provenance record." | **MET for the machinery; PENDING mentor input for content** | The mechanism exists and is enforced: `resolutions.yaml`, `status_baseline_wp1`, `resolution_refs`, `status_diff.py` with three invariants, 48 tests. There are 0 changes to tie, because there are 0 answers. |
| 2 | "The Q1 stem-to-section mapping is confirmed, corrected, or explicitly left unverified." | **PENDING mentor input** | Q1 is question 1 in `MENTOR_BRIEF.md`, phrased to elicit the actual mapping. Currently left unverified, explicitly, in `dictionary.py` and `METADATA_QUESTIONS.md`. |
| 3 | "Q2–Q4 remain documented as dictionary defects until authoritative correction exists." | **MET, and unchanged** | `METADATA_QUESTIONS.md` Q2–Q4 stand as written; nothing in this packet touched them. They are questions 10–12 in the brief. |
| 4 | "High-impact undocumented families relevant to later pilot planning are resolved or explicitly unresolved." | **PENDING mentor input** | `precipdaily_*` (Q7, 56 columns) and the FWI classes (Q8, 30 columns) are explicitly unresolved and are questions 2 and 3 in the brief. |
| 5 | "Geographic fields needed for later aggregation have evidence-backed definitions." | **PENDING mentor input** | Q10–Q11 are questions 4 and 5. No geographic column has been given a definition. |
| 6 | "Sentinel/fill-code semantics are evidence-backed; candidate sentinels remain distinct from confirmed missing-value rules." | **PENDING mentor input; the distinction is preserved** | The 24 flagged columns remain a frequency flag that asserts nothing; `-9` at index 117 is still unlabelled (D-009 ruling 3). Q17 and Q9 are questions 7 and 8. |
| 7 | "The known text-empty PDF page is checked for extraction completeness." | **MET** | Page 3 rendered at 200 dpi and inspected: blank, uniform colour, no marks. Pages 2 and 4 as control. `artifacts/profiles/dictionary_page0{2,3,4}.png`, run record `20260909T220506Z_local_rasterize_dictionary_pages`, `DATA_NOTES.md` §1, D-009. |
| 8 | "The per-column dictionary continues to distinguish deterministic structural facts, dictionary-verified facts, mentor/owner-confirmed facts, and unresolved fields." | **MET for the machinery; PENDING mentor input for content** | Four-way distinction is now explicit in the data model: `structurally_observed_only`, `verified_from_dictionary`, the new `owner_confirmed`, and `unresolved`/`partially_resolved`. `owner_confirmed` is unreachable from the dictionary rules and `verified_from_dictionary` unreachable from a resolution — both enforced and tested. 0 columns are `owner_confirmed` today. |
| 9 | "The WP2 report identifies which fields are sufficiently grounded to be considered for later pilot selection, without yet extracting phenomena." | **PENDING mentor input** | Deliberately not attempted. Naming pilot-ready fields today would rest on the 21 dictionary-verified columns alone and would in practice mean promoting the candidate maps — the false-closure risk GUIDANCE named first. |

**Proposed status for M1-WP2 as a whole: IN PROGRESS — WP2a complete, WP2b
blocked on mentor answers.** No milestone gate is proposed. WP2a is offered for
GUIDANCE review of the **mechanism and the brief**, not of any resolution
outcome; the honest summary is that this packet makes the next packet auditable
and answers nothing about the data itself.

## 15. Proposed next bounded objective

**M1-WP2b — apply mentor answers from the 2026-09-10 meeting.** For each answer
Kaiyuan relays: one record in `data/metadata/resolutions.yaml` with its date,
source and verbatim statement; one decision-log entry accepting it; a regenerated
`dictionary_coverage.json`; and a `status_diff.py` run showing exactly which
columns moved and on whose authority. Answers that name no columns are recorded
and move nothing.
