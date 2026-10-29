# External references

External material the project draws on but does not store. Each entry pins the
source by hash and states what is taken from it and what is not. **Nothing from
a referenced archive is copied into the repository** unless an entry says so.

## `LLM_Eval-main.zip` --- WildfireGPT question templates (D-032)

| | |
| --- | --- |
| **What** | WildfireGPT case-study question templates and literature-review prompt pipeline |
| **Author** | Yangxinyu Xie (per file header) |
| **Supplied by** | the mentor, 2026-10-22 |
| **SHA-256** | `a88a9f0df284213769b8e65abd69c2c0e8c5f7dec0d46c0d2121338e7ad2938f` (computed by Kaiyuan on the Mac, 2026-10-27; two downloaded copies, identical hash) |
| **Stored in repo** | **No** --- only this entry and D-032 |

**Contents** (from inspection of the archive): `templates.py`,
`infrastructure.py`, `prompt.py`, `prompt.yml`, `search.py`, `index.py`,
`embedding.py`, `utils.py`, `README.md`, `WildfireGPT Case Study Questions.md`,
`pyproject.toml`.

**Taken from it** (for Track D, D-031):

- the template/slot mechanism (`templates.py`, `infrastructure.py`);
- the question categories (fact-based / recommendation / hybrid; data analysis
  / literature review / both);
- the case-study question table.

**Not taken:** its random slot filling, its embedding retrieval, its
news-style answer generation.

**As used by Track D v1** (2026-10-28; `data/metadata/templates/`,
`src/climrr/templates.py`; archive re-hashed on the Mac, same SHA-256):

| From the archive | Track D v1 |
| --- | --- |
| `QuestionTemplate` dataclass: `template` string with `[SLOT]` markers, `category_type`, `research_method`, `topic_category`, `relevant_professions` | kept: `text` with `[SLOT]` markers, `category_type`, `research_method`; added `qa_type` (our six), `answer_mode`, `required_slots`, `retrieval_terms_rule`; **not kept:** `topic_category`, `relevant_professions` |
| `CategoryType`: Fact-Based / Recommendation-Seeking / Hybrid | kept as `fact_based` / `recommendation_seeking` / `hybrid` |
| `ResearchMethod`: Data Analysis / Literature Review / Both | kept as `data_analysis` / `literature_review` / `both` |
| slot pools (`hazard_types`, `locations`, `time_periods`, …) filled with `random` | **replaced** by table-grounded vocabularies with a source and authorization per value (`slots_v1.yaml`), filled by exhaustive enumeration |
| location lists chosen from news reports | **not taken**; locations are row sets of the table (cell / county / state) |
| answers left to a model | **not taken**; every `table_only` answer is computed from `FullData.csv` |

No file, string or template text from the archive is copied into the repository.

## `ENSURE_Prompt Use Cases_v3.xlsx` --- ENSURE prompt use cases (D-040)

| | |
| --- | --- |
| **What** | ENSURE analyst-prompt use cases: one sheet, ten use cases, each with prompt, modalities, relationships, evidence, capability, desired output, illustrative output and guardrails |
| **Supplied by** | the mentor, 2026-10-29 |
| **File name as received** | `ENSURE_Prompt Use Cases_v3.xlsx` (with a space) |
| **SHA-256** | `d3471bfc19294c1872b50add2d1f9e3b1c92d3e985a4b2af0c889ee6f754dee2` (computed by the EXECUTOR on the Mac, 2026-10-29; 15,420 bytes) |
| **Stored in repo** | **No** --- only this entry and D-040 |

**Column headers** (row 1 of `Sheet1`, verbatim, in order; the fourth has a
trailing space in the file):

1. `#`
2. `Prompt / Use Case`
3. `Example Analyst Prompt`
4. `What ENSURE Is Doing `
5. `Reasoning Modalities`
6. `Key Relationships / Concepts`
7. `Evidence / Information Needed`
8. `Capability Tested`
9. `Desired Output Characteristics`
10. `Illustrative Output`
11. `Important Limitations / Guardrails`

**Use cases** (column `Prompt / Use Case`, with `Reasoning Modalities`):

| # | Use case | Reasoning modalities |
| --- | --- | --- |
| 1 | Infrastructure Identification | Infrastructure |
| 2 | Infrastructure Context | Infrastructure + Text |
| 3 | Hazard Characterization | Text |
| 4 | Infrastructure Exposure | Hazard + Infrastructure |
| 5 | Infrastructure Comparison | Infrastructure + Text |
| 6 | Network Criticality | Infrastructure Graph |
| 7 | Dependency Inference | Graph + Infrastructure + Text |
| 8 | Functional Relationship Discovery | Graph + Infrastructure + Text |
| 9 | Evidence-Based Risk Assessment | All core modalities |
| 10 | Resilience Decision Support | All core modalities |

**Taken from it:** the item fields (D-037: `reasoning_modalities`,
`key_relationships`, `evidence_needed`, `capability_tested`,
`desired_output_characteristics`, `reference_answer` ← *Illustrative Output*,
`guardrails`); the capability-ladder shape (D-038). *What ENSURE Is Doing* is not
mapped to a field.

**Not taken:** the infrastructure and graph modalities (out of scope); the
prompts and illustrative outputs themselves. No cell text is copied into the
repository beyond the headers and use-case names above.
