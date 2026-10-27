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
