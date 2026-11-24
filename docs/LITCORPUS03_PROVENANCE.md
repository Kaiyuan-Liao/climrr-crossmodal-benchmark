# LITCORPUS-03 --- provenance of the critical-infrastructure corpus

**Status: inventoried on Polaris (2026-11-24 00:33 UTC, `inventory_corpus v1`; facts relayed by Kaiyuan in the P5a
hotfix work package, §4); not yet indexed or queried.** §1 is **as supplied**; the inventory confirms the file count
(89,497) and gives the content identity. The tarball's SHA-256 check on Eagle is not among the relayed facts and is
recorded as not yet reported. The inventory JSON itself has not been shipped back, so there is still no
`data/manifest.json` `external_corpora` entry (D-070 (c)). No paper has been read, opened for content or sampled. Never in
Git.

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
`DR-CAND-INFRA-2` (D-070a; `docs/P5_INFRA_IMPACT_DESIGN.md` §3; it supersedes DR-CAND-INFRA-1 for the pilot), recorded per
paper.

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

## 4. Inventory results (as relayed, P5a hotfix work package, 2026-11-23)

Run on Polaris 2026-11-24 00:33 UTC with `inventory_corpus.py` v1 (root = the extracted `kept/`). Figures as relayed by
Kaiyuan; the output JSON is to be shipped back to `reports/litcorpus03_inventory.json` and checked against them.

| | |
| --- | --- |
| Files | **89,497** (equals the supplied count) |
| Parse failures | 0 |
| Distinct paper ids | 89,497 (no id in two shards) |
| Shards | 32 |
| Content identity | `2dfc8eca533a0e983c4863e712b37ce35a08bc4980996d1483b711b05e3ff725` (the `build_index.py` rule; the index of LITCORPUS-03 must reproduce it) |
| `_araiadoc_tags` | an **object** on every file, holding a `critical_infrastructure` entry (§5) |
| Duplicates by content (SHA-256 of the bytes) | 103 groups, 109 redundant copies |
| Duplicates by normalised title | 891 groups, 2,078 redundant copies |
| Overlap with the 186k set (LITCORPUS-02's source) by paper id | 6,533 papers |

**What follows.** (a) `_araiadoc_tags` is an object, not a string: `build_index.py` stores string sections only, so the tags
are not in the index and no lexical query can match tag text (§3 point 3 settled; D-070 (b)). (b) The duplicates are
recorded, not removed: DR-LIT-IND-1 v2 (same SHA-256 = one paper; same normalised title counted as one) applies when
statements are aggregated, as for LITCORPUS-02; the candidate rule does not de-duplicate. (c) 6,533 papers (7.3 %) are also
in the 186k set; each candidate records `in_186k_set` (DR-CAND-INFRA-2), so statements already extracted from those papers
in the pilots can be recognised. The overlap is by paper id only, not by content.

## 5. Sector tags (`_araiadoc_tags.critical_infrastructure`)

As relayed: on every file the `critical_infrastructure` entry carries `matched_groups[]`, `sectors[]` (objects
`{sector, subsectors[]}`) and `tags[]`, with CISA sector names; **10,403 distinct tag values**; the most frequent:
Transportation/Highways 6,701 files; Communications/Wireless 3,985; Energy/Electricity 3,934; Transportation/Aviation 2,583.

These are **labels written by JL's pipeline** (an external model), not the paper's words, and not verified by the project.
From the P5a hotfix (D-070a) they are used as follows:

- `inventory_corpus.py` v1.1 parses `sectors[]` into `asset_sector_tag` per paper (`sector/subsector`; `sector` alone when
  there is no subsector), `origin: external_model (JL pipeline)`, and writes one line per paper (`--tags-out`) for
  `run_query.py` v4.1. Shape problems are counted, never repaired.
- Each sector name is mapped to an `infrastructure_lexicon_v1` class **by name** (exact after normalisation, else a unique
  leading-word prefix of one CISA sector name; else `unmapped`, reported with its file count). From the names relayed:
  Transportation -> `transportation_systems` (prefix), Communications -> `communications`, Energy -> `energy` (exact). The
  full mapping comes with the v1.1 inventory.
- DR-CAND-INFRA-2 admits a paper with a hazard section and **any** sector tag (basis b) as well as a paper with a hazard
  term and an asset term in one section (basis a). The tag says only that the pipeline associated the paper with a sector;
  it is never evidence of an impact.
