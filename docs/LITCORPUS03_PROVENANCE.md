# LITCORPUS-03 --- provenance of the critical-infrastructure corpus

**Status: received, not yet verified, inventoried or indexed (D-070, 2026-11-23).** Every figure below is **as supplied**
until the inventory on Polaris is ingested; a hash, size or count that differs on Eagle is an escalation, not a correction.
No paper has been read, opened for content or sampled. Never in Git.

## 1. Identity as supplied

| Field | Value |
| --- | --- |
| Corpus id | `LITCORPUS-03` |
| File | `critical_infrastructure_judged_relevant.tar.gz` |
| SHA-256 (supplied) | `6c6e21c2b07cfa0ef6a4098b19a0335949d3bf68a9a97d9f16b5f7904791ec76` |
| Size (supplied) | 750 MB |
| Papers (supplied) | 89,497 JSON files |
| Layout (supplied) | `kept/<last two digits>/<id>.json` |
| Schema (supplied) | as the 186k set (`full_705k_v2_filtered`, LITCORPUS-02's source): section-keyed text, plus `_araiadoc_tags` |
| Supplied by | Alvi, 2026-11-23 (after the group meeting of the same day) |
| Selection | **`external_model_judged`**: relevance to critical infrastructure judged by JL's agentic pipeline; the criteria, model, prompt and threshold are **not available to the project** |
| Parent set | unknown (not stated) |
| Location | Eagle, `climrr-litcollect/sources/critical_infrastructure_v1/` under the litcollect root (`config/local_paths.yaml:litcollect_root_polaris`, untracked); never in the clone, never in Git |
| Year / venue / authors | `unknown` |

## 2. What "external_model_judged" means for its use

The corpus is a candidate pool, not a sample of the infrastructure literature. A paper's presence says only that JL's
pipeline judged it relevant to critical infrastructure; nothing about the hazard, the place or the quality. Its absence
says nothing either. No yield from it may be described as prevalence. The project's own selection on top of it is
`DR-CAND-INFRA-1` (`docs/P5_INFRA_IMPACT_DESIGN.md` §3), recorded per paper.

## 3. Checks before use (Polaris; commands in `docs/P5_INFRA_IMPACT_DESIGN.md` §6)

1. **Hash** of the tarball on Eagle equals the supplied SHA-256.
2. **Inventory** (`scripts/litcollect/inventory_corpus.py`, root = the extracted `kept/`): files (expect 89,497), parse
   failures, shards, section-key statistics, the `_araiadoc_tags` type and its top 20 values, duplicates by content hash
   and by normalised title, overlap with the 186k set by paper id, and the content identity (the `build_index.py` rule).
   Output `litcorpus03_inventory.json`, shipped back to `reports/litcorpus03_inventory.json`.
3. **`_araiadoc_tags` type.** If it is a string, `build_index.py` stores it as a section and every lexical query can match
   tag text (the tags are the pipeline's words, not the paper's). Then the COORDINATOR rules before the lexicon query runs
   (exclude the key from matching, or accept and record). If it is a list or an object, it is not indexed (only counted as
   a non-string value).
4. **Index** (`build_index.py`, unchanged): its content identity must equal the inventory's.

## 4. Inventory results

*To be filled from `reports/litcorpus03_inventory.json` at ingest.*
