# ClimRR Cross-Modal Benchmark — M4-WP0 Review, Merge Authorization, and M4-WP1 Ruling

**Milestone context:** M1 remains open; M4 provenance preflight complete  
**Reviewed package:** M4-WP0 — Literature Corpus Provenance and Inventory  
**Merge request:** unmerged linear chain through `work/m4-wp0`  
**Next work package:** M4-WP1 — Deterministic 10-paper ingestion and structured-claim pilot  
**GUIDANCE status:** PASS WITH ACTIONS

> This ruling covers three decisions together: M4-WP0 review, authorization to merge the unmerged linear branch chain, and authorization of M4-WP1. Merging the chain does **not** pass M1, and M4-WP1 does **not** authorize prototype matching, M5 bridge work, or QA generation.

---

## Gate status

**PASS WITH ACTIONS**

Three rulings:

1. **M4-WP0: PASS.**
2. **Single `--no-ff` merge of the full unmerged chain into `main`: AUTHORIZED**, after one bookkeeping correction described below.
3. **M4-WP1: AUTHORIZED** as a bounded 10-paper ingestion / structured-claim pilot, with the sampling and evidence-location refinements below.

M1 remains **open**.

Merging the chain records accepted project work; it does **not** imply that M1 has passed its milestone gate.

D-014 may carry provisional interpretations downstream, but it does not:

- promote any field to `owner_confirmed`;
- turn `inferred_candidate` into verified truth;
- authorize QA generation.

---

## Current-stage assessment

M4-WP0 has done the right job.

The literature corpus now has a stable identity without pretending that its documents have been scientifically inspected:

- 1,918 external JSON files;
- a frozen corpus manifest;
- exact per-file hashes;
- one exact-byte duplicate pair;
- no content-derived topic labels;
- no semantic inspection during WP0.

The collection query is now an auditable provenance object rather than informal context.

The deterministic parse found:

- **11 hazard groups**, not 10;
- 80 hazard terms;
- 22 context terms;
- 102 terms total.

Reporting the discrepancy instead of forcing the expected count is the correct behavior.

The query-scope work also preserves the essential distinction between:

> **collection-query vocabulary**

and

> **paper-level evidence**

That gives the project a sound basis for beginning actual M4 ingestion.

---

## Evidence check

### A. M4-WP0

**PASS.**

The evidence supports the intended provenance-only boundary.

The pinned query is exact and hashed.

Its provenance appropriately records unknown values rather than guessing:

- execution platform: `unknown`;
- execution date: `unknown`;
- export date: `unknown`;
- completeness of result set: `unknown`.

The inventory keeps the corpus external and identifies it through stable manifest and byte-level hashes.

The absence findings are scoped correctly.

The project found no matches under its explicit rules for:

- scenario / horizon;
- U.S. states / postal codes;
- county / tract / USA terms.

But those findings remain statements about the **query**, not the papers.

The two disclosed implementation defects do **not** reopen WP0:

- the scanner hit was repaired before hand-back rather than weakening the scanner;
- the mistyped CSV hash was caught by a check against the actual file and corrected.

These are validation-system successes after correction, not evidence that the final scientific artifacts are compromised.

### B. Merge request

**Authorized, with one bookkeeping action first.**

The branch lineage is linear:

```text
main
  → work/m1-wp2
  → work/m1-wp3
  → work/m1-wp3b
  → work/m4-wp0
```

There is no scientific reason to merge the packages separately.

A single no-fast-forward merge of the final `work/m4-wp0` branch into `main` is preferable because it:

- preserves the entire accepted chain;
- creates one explicit integration point;
- avoids unnecessary merge noise.

However, before merge:

- refresh `M4_WP0_REPORT.md`;
- refresh `PROJECT_STATE.md`;
- ensure they reflect the actual reviewed head:
  `1e2fd9f`;
- ensure pushed/unpushed state matches reality.

Then:

1. perform one `--no-ff` merge of the final WP0 branch into `main`;
2. run the normal test/scanner gates on the merge result;
3. record the merge SHA as the new authoritative integrated state.

Do **not** mark M1 as passed.

### C. M4-WP1 sample rule

**Approved.**

The proposed deterministic sample of 10 unique items is appropriate.

Approved rule:

> every 190th stable `LIT` item beginning from `LIT-000001`, while preventing the later member of an exact-byte duplicate group from appearing as a second unique sample item.

This rule is:

- deterministic;
- reproducible;
- tied to the frozen manifest;
- independent of title;
- independent of topic;
- independent of prototype similarity;
- independent of paper content.

The sample is **not statistically representative**, and the report must not describe it as such.

The purpose is workflow validation:

> **Can the ingestion and claim-extraction process work reproducibly?**

—not corpus-prevalence estimation.

### D. JSON evidence-location convention

**Approved with one precision requirement.**

Use:

```text
corpus item id
+ file SHA-256
+ JSON key/path
+ character span
```

for each evidence span.

Character offsets must be defined against:

> **the exact original JSON string value after JSON decoding and before any text normalization**

Recommended convention:

```text
zero-based, half-open Unicode code-point offsets [start, end)
```

Each claim should therefore carry at least:

- `item_id`;
- corpus-manifest SHA;
- file SHA-256;
- JSON key or full JSON path;
- `char_start`;
- `char_end`;
- offset convention;
- exact evidence text or evidence-text hash.

Do **not** compute source offsets after:

- lower-casing;
- whitespace compression;
- Markdown conversion;
- sentence joining;
- other normalization.

---

## Scientific risks

### 1. Forcing claims out of off-topic papers

M4-WP1 must permit legitimate terminal outcomes such as:

- `off_topic`;
- `no_eligible_claim`;
- `parse_failure`;
- `ambiguous_only`.

The pilot must **not** require every paper to yield a scientific claim.

Otherwise it would manufacture evidence.

### 2. Confusing ingestion validation with corpus relevance

Ten deterministic papers cannot establish:

- corpus quality;
- corpus precision;
- hazard distribution;
- adequacy for the ClimRR pilot;
- expected bridge yield.

WP1 may report only what happened in those ten sampled items.

### 3. Prototype vocabulary leaking into extraction

The extractor should not search each sampled paper specifically for:

- heat index;
- FWI;
- California;
- Oklahoma;
- RCP8.5;
- prototype terms.

Those concepts may occur naturally, but WP1's task is:

> **paper → structured claim**

not:

> **prototype → paper**

### 4. JSON section structure may be irregular

The corpus files are JSON, but WP1 must first establish the schema actually encountered.

Do not assume every file has:

- identical keys;
- identical section names;
- identical nesting;
- always-text section values.

Unexpected structures are valid findings.

### 5. Character spans can silently become unstable

Source-location offsets must remain anchored to the original decoded JSON section string.

Any normalization before offset calculation would make source locations non-reproducible.

### 6. D-014 must not collapse provenance distinctions

Proceeding on “our reading” means inferred ClimRR semantics may continue downstream **with provisional status intact**.

It does not convert them into verified semantics.

---

## Required actions

### Before merging

1. Refresh WP0 report/state to actual reviewed head `1e2fd9f` and actual push state.
2. Keep M1 explicitly open.
3. Merge the **final WP0 branch only** into `main` with one `--no-ff` merge.
4. Run repository test/scanner gates after the merge.
5. Record the resulting merge SHA as the new authoritative integrated state.

### For M4-WP1

6. Freeze the 10-paper sample **before opening any sampled file**.
7. Store the sampling rule, sampled IDs, and corpus-manifest SHA.
8. Ensure exact-byte duplicates cannot appear twice.
9. Inspect all ten selected JSON files completely.
10. Establish the actual JSON schema encountered before building claim assumptions around it.
11. Define evidence locations using stable item ID, file SHA, JSON path, zero-based half-open `[start,end)` Unicode code-point span, and exact evidence text or hash.
12. Permit explicit negative outcomes: off-topic, no eligible claim, malformed/unparseable, ambiguous evidence.
13. Keep prototype matching completely outside WP1.

---

## Decisions for Kaiyuan or mentor

### GUIDANCE rulings

| Question                       | Ruling                                      |
| ------------------------------ | ------------------------------------------- |
| M4-WP0                         | **PASS**                                    |
| Merge unmerged chain           | **Authorized after bookkeeping refresh**    |
| Merge strategy                 | **One `--no-ff` merge of final WP0 branch** |
| Does merge pass M1?            | **No**                                      |
| M4-WP1                         | **Authorized**                              |
| Sample size                    | **10 unique items approved**                |
| Every-190th deterministic rule | **Approved**                                |
| Statistical representativeness | **Not claimed**                             |
| JSON section + character span  | **Approved with exact offset convention**   |
| Local-only WP1 execution       | **Approved**                                |
| Sophia corpus transfer now     | **Not required**                            |
| Prototype matching during WP1  | **Not authorized**                          |
| QA generation                  | **Not authorized**                          |

### Wuhan anecdote

**It should not change the sample design.**

The one opened paper that appeared off-topic is a single anecdotal observation, not a corpus property.

Leaving the deterministic sample unchanged is scientifically preferable.

If the sample contains off-topic papers, WP1 should demonstrate that the workflow can correctly return:

```text
off_topic
```

or:

```text
no_eligible_claim
```

rather than forcing a claim.

Changing the sample because one item looked irrelevant would introduce relevance-based selection bias.

---

## Next bounded objective

**Authorize M4-WP1 — Deterministic 10-paper ingestion and structured-claim pilot.**

Central question:

> **Can the project reproducibly inspect a frozen, content-independent sample of corpus items and convert what those papers actually state into structured claims with exact source locations—while safely returning no claim when appropriate?**

For each selected item, produce a record containing:

- stable corpus ID;
- file SHA-256;
- parse status;
- actual JSON structure encountered;
- recoverable bibliographic metadata, if present;
- paper-level scope / relevance status;
- zero or more structured claims;
- exact evidence location for each claim;
- explicit vs. inferred status for extracted attributes;
- rejected / ambiguous candidate passages;
- reason for off-topic / no-claim outcomes where applicable.

A structured claim may contain:

- phenomenon / concept actually discussed;
- direction or relation actually stated;
- geography actually stated;
- temporal frame actually stated;
- scenario actually stated;
- claim type;
- evidence span.

Do not fill absent dimensions from:

- general knowledge;
- ClimRR prototypes;
- query terms;
- filenames.

Prototype-to-claim compatibility begins later, in M5.

---

## Acceptance criteria

M4-WP1 will be ready for GUIDANCE review when:

1. The 10 sampled IDs are frozen before content inspection.
2. Sample selection is reproducible solely from the frozen WP0 manifest and the documented rule.
3. No title, filename meaning, topic, prototype relation, or text content influences sample selection.
4. Exact-byte duplicates cannot appear twice.
5. All 10 sampled items receive a terminal processing status.
6. The actual JSON schema encountered is documented rather than assumed.
7. Every extracted claim is traceable to stable corpus ID, file SHA, JSON path, and exact `[start,end)` character span.
8. Offset semantics are explicitly defined against the unnormalized decoded source string.
9. Evidence text / span integrity is mechanically checked.
10. Zero claims is a valid result for a paper.
11. Off-topic papers remain in the result rather than being replaced.
12. Bibliographic metadata is recorded only when present / recoverable.
13. Claim fields use `unknown` when geography, scenario, horizon, or another dimension is not stated.
14. Explicit statements are distinguished from extractor inference.
15. No claim is labeled supporting or contradicting a ClimRR prototype.
16. No prototype guides paper reading or passage selection.
17. Rejected and ambiguous passages are preserved for audit.
18. No embeddings, semantic retrieval, or corpus-wide search occurs.
19. The ten-item output is described as an **ingestion / claim-extraction pilot**, not a corpus-representative estimate.
20. All outputs remain tied to the exact WP0 corpus manifest identity.

---

## Do not do yet

Do not replace off-topic sampled papers.

Do not stratify the sample by hazard group yet.

Do not estimate “percentage relevant” from 10 items.

Do not search all 1,918 files.

Do not select papers because they mention:

- heat index;
- FWI;
- California;
- Oklahoma;
- RCP8.5;
- prototype terms.

Do not create embeddings.

Do not rank papers.

Do not match claims to the three ClimRR prototypes.

Do not classify claims as supporting, contradictory, or compatible with table phenomena.

Do not begin M5.

Do not generate QA.

The immediate evidence chain remains:

> **frozen corpus → deterministic paper sample → exact-source structured claims**

Only after that layer works should the project ask how those claims relate to ClimRR phenomenon units.
