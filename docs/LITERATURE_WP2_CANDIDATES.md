# M4-WP2 --- retrieved candidates (retrieval only)

> **Relevance-guided candidate-generation sample, not representative.**
>
> **No candidate has been read; semantic inspection waits for M4-WP1b (D-018).**

Authorized by D-018 (`docs/M5_WP1_REVIEW_FOLLOWON_GUIDANCE_RULING.md`). This
page reports **where frozen terms occur**. A hit is a reason to inspect an item
later, not evidence that the item is about the hazard or the place it names,
and **no hit is a semantic bridge**.

## Terms (frozen)

`artifacts/literature/wp2_terms.json`, SHA-256
`3d0b1513478b8096a4507f454df1ab5b22928b25fd3354d096961198a1e7d02c`, committed
before any scan (`6080cc3`).

| Id | Class | Term | Source |
| --- | --- | --- | --- |
| WP2-T01 | concept | `fire weather index` | concept map, `fire_weather_index` (family, `approved_lexical`) |
| WP2-T02 | concept | `FWI` | concept map, `fire_weather_index` (family, `approved_lexical`) |
| WP2-T03 | concept | `heat index` | concept map, `heat_index` (family, `approved_lexical`) |
| WP2-T04 | place | `Oklahoma` | P-COUNTY-1 `G.identifier.State` |
| WP2-T05 | place | `Stephens` | P-COUNTY-1 `G.identifier.NAME` |
| WP2-T06 | place | `California` | P-STATE-1 `G.identifier.State` |

No alias, no abbreviation, no postal code. The two metric entries of the
concept map are `proposed` and contribute no term.

## Rule

Scan every corpus-manifest item (SHA-256 verified, decoded as JSON); in every
string value at any depth (object keys not scanned), find every term
**case-insensitively**, where the code points immediately before and after the
match, if any, are **not letters, numbers or combining marks** (Unicode
categories `L*`, `N*`, `M*`). So `FWI` does not match `FWIs` or `FWI2`, and
`heat index` does not match `heat-index`. Qualify iff ≥ 1 concept hit **and**
≥ 1 place hit. Remove the later member of every exact-byte duplicate group
(keep the lowest LIT id) **before** the cap. Sort by LIT id; take the first 12.
No manual replacement.

## Result

| | Items |
| --- | ---: |
| Scanned (`LITCORPUS-00`, manifest `3281aa72…`) | 1,918 |
| Parse failures | 0 |
| With ≥ 1 concept hit | 18 |
| With ≥ 1 place hit | 172 |
| **Qualifying (both)** | **4** |
| Removed as later duplicates | 0 |
| **Qualifying pool** | **4** |
| **Candidates (cap 12)** | **4** |

**The pool is smaller than the cap.** All four qualifying items are
candidates. The terms were **not** loosened to reach 12 (work-package
instruction; D-018 forbids aliases).

| Candidate | Concept hits | Place hits | by term (T01 / T02 / T03 · T04 / T05 / T06) |
| --- | ---: | ---: | --- |
| `LIT-000166` | 1 | 1 | 1 / 0 / 0 · 0 / 1 / 0 |
| `LIT-000519` | 13 | 1 | 6 / 7 / 0 · 0 / 0 / 1 |
| `LIT-001501` | 11 | 22 | 0 / 11 / 0 · 15 / 0 / 7 |
| `LIT-001536` | 1 | 11 | 0 / 0 / 1 · 2 / 0 / 9 |

Every hit --- item id, JSON path, term, term class, `[start, end)` code-point
span and the exact matched characters --- is in
`artifacts/literature/wp2_candidates.json` (SHA-256
`e155e70e338ffb67f8c881a8a3fdb794e28c0f048c43afc10b0a723135ec8d9c`). Every
qualifying id with its counts is in `wp2_qualifying_pool.json` (SHA-256
`8f097f7adfab4fc5987061aefb0d31b37f12c9fcc1fba8721b6e96316048a3f0`).

## What a hit cannot tell you

- **A place hit is a lexical signal only.** `California` may be an affiliation
  or a publisher's address; `Stephens` is also a surname, so a hit may sit in a
  citation. Only structured claim extraction can establish a paper's actual
  geography (ruling, "Scientific risks" 4).
- **A concept hit names a family, never a metric.** `heat index` does not
  mean days above 105°F; `FWI` does not mean a seasonal FWI average (D-018,
  item 3).
- **Four items estimate nothing** about the corpus, and a relevance-guided
  sample is built to over-represent the terms it was built from.
