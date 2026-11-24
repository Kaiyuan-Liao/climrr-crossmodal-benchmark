# Knowledge graphs for cross-modal benchmark question generation: survey and design note

Date: 2026-11-23. Status: discussion note for the project owner and mentors. Nothing described here has been built or trialled; the design in section 3 is a sketch on paper, and any pilot would need the project's usual approval first.

Numbers in square brackets point to the reference list. Each reference carries a verification mark: **[V]** the page or bibliographic record was retrieved during this survey; **[C]** seen only as a citation inside another retrieved source; details marked "from memory" were not re-checked.

---

## Two-minute summary

**Question.** Should the benchmark move from "one evidence packet per table pattern" to a knowledge graph (KG) that joins the climate table, the climate papers, the infrastructure asset graph and the infrastructure papers, so that an agent can write hazard-to-infrastructure questions from it?

**What the literature says.**

- Generating questions from a KG is a mature recipe: sample a subgraph or path, turn it into a formal query, verbalize it, and check it by running the query [1–5, 8, 9]. It works because the graph is treated as ground truth. That assumption is the weak point: a 2025 audit of 16 widely used KG question sets found an average factual correctness of only 57% [8].
- Graphs extracted from scientific papers by language models are noisier than curated ones. Reported relation precision ranges from about 0.55–0.69 for a long-running biomedical system [28] to about 88% [24] and about 99% (with an ontology, evidence spans and a validator) [25]. The best result came with the strictest evidence requirements.
- Hazard and infrastructure KGs exist [15–21], but they are built from datasets and asset inventories, not from literature, and none was used to generate benchmark questions. **I found no published work that generates benchmark items from a graph joining climate projections, hazard literature and infrastructure assets.** On that point the note cannot lean on precedent.
- The locality problem (a place-specific pattern paired with a general mechanism) has standard *representations*: qualifiers on statements, reified statements, scope contexts, support counts [30, 33–40]. I found no published *question generator* that uses them to stop a general mechanism being presented as locally demonstrated. That enforcement would be ours to design and test.

**Assessment.** The current pipeline is already a graph in all but name: patterns, claim groups and the pairing rule are nodes and edges stored as packets. The realistic choice is not "packets or open-ended KG extraction" but whether to make that join explicit, typed and reusable.

**Recommendation.** Build a *thin, statement-centred graph from artifacts that already exist*, add asset classes and impact types from the infrastructure side, and do **not** run open-ended triple extraction over the papers. Test it in a small pilot (about 30 items) against a packet approach extended to four sources.

**Decisions needed from mentors.**

1. Locality level for infrastructure items: general (hazard family → asset class) only, or also place-specific exposure ("assets of this class in this state")?
2. Minimum evidence for an edge to appear in graded text: is one passage enough if worded as single-study, or are two independent papers required?
3. Who owns the shared vocabulary (hazard families, asset classes, impact types) across the two teams, and is the pilot approved at the proposed size?

---

## 1. What has been published

### 1.1 Generating question sets from knowledge graphs

| Work | Graph | How questions are made | Quality control |
| --- | --- | --- | --- |
| LC-QuAD [1], LC-QuAD 2.0 [2] | DBpedia; Wikidata | Subgraphs around seed entities are fitted to query templates, turned into a template question, then rewritten by people; 5,000 and 30,000 questions | Human rewriting |
| GrailQA [3] | Freebase | Formal queries generated from the graph → canonical question → crowd paraphrase; 64,331 questions | Cross-validation of paraphrases by other workers |
| KQA Pro [4] | Wikidata subset | Small set of templates composed into multi-step "programs" with matching queries; about 120k questions | Crowd paraphrase, then five other workers check meaning and fluency; confusing items removed |
| 2WikiMultiHopQA [5] | Wikidata + Wikipedia text | Templates plus logical rules over graph triples; each item carries its evidence triples as the reasoning path | Templates that allowed one-hop answers were removed |
| KGQAGen [8] | Wikidata | A language model expands a subgraph from a seed until it supports a multi-hop question, then writes question, answer and query | Query executed against the graph; 96.3% correct on a 300-item manual sample |
| SynthKGQA [9] | Any KG | Model writes question, answer subgraph and query from random subgraphs | Query executed; a second model paraphrases |
| Dynamic-KGQA [10] | KG | Regenerates question sets on demand to limit memorization | Statistical consistency across versions |
| Chemistry multi-hop study [11] | Entities extracted from recent papers, joined to external databases | Multi-hop questions written along graph paths | Described as automated |

**Provenance.** In all of these the provenance of a question is the subgraph or query that produced it. Provenance of the *edges* is inherited from the source graph and is not re-examined.

**Known failure modes.**

- *Wrong answer keys inherited from the graph.* The audit in [8] attributes its 57% figure to outdated or inconsistent graph content and to ambiguous, trivial or unanswerable questions.
- *Multi-hop questions answerable in one hop.* On a prominent multi-hop text benchmark, a single-hop model scored about as well as multi-hop models, and people could answer most questions without all the intended paragraphs [6]. A 2026 medical benchmark reports the graph version of this: models route through highly connected generic nodes instead of the intended chain [12]. Another 2026 benchmark shows that question wording often gives away the path [13].
- *Unnatural questions.* Questions written backwards from a formal query do not read like questions people ask [7].

For contrast, the main climate-science QA benchmark I found, ClimaQA [14], is generated from graduate textbooks with scientists validating items; it does not use a graph.

### 1.2 Hazard, climate-risk and infrastructure graphs

| Work | Contents | How built | Provenance | Used for questions? |
| --- | --- | --- | --- | --- |
| KnowWhereGraph [15–17] | About 30 integrated datasets on hazards, climate, places; hazards are linked to the places they affect through observations, and all regions are aligned to a global grid of cells | Converted from existing datasets under a shared ontology; mostly U.S. layers | To source datasets (per-statement detail not verified) | Retrieval-style questions ("what happened here before"), not a benchmark |
| Cascading-failure graph [18] | Utility assets, the services they provide and depend on, locations | Ontology pattern filled with utility data | Utility data | No; used to infer cascading service failures in floods |
| Flood digital twin [19, 20] | Buildings, river levels, flood warnings; extended to power, water and telecoms assets | Software agents ingest public data continuously | Source feeds | No; impact assessment |
| Cascading-effects ontology [21] | Concepts for infrastructure interdependencies | From a systematic literature review, checked on real cases | Literature review | No |
| Hazard Information Profiles [27] | Standard definitions for 281 hazards in eight types (2025 revision) | Expert consensus | Authored profiles | No; a candidate controlled vocabulary |
| Literature labelling of hazards × infrastructure [23] | Papers labelled with 18 hazard categories and 55 infrastructure-function categories | Weak supervision plus a classifier | Document level | No; a corpus index, not a graph |
| Heat-wave risk graph [24] (preprint) | Entities in physical, social and economic layers and relations between them, from several thousand papers (the versions report different sizes) | Model extraction, clustering, name standardization | Described as tracked; mechanism not explained | 500 test questions for its own QA system; 87.6% relation precision on a sample |
| Climate-model literature graph [25] | 133,990 nodes, 755,308 relations; curated metadata plus triples from 2,000 papers | Model extracts typed triples *with evidence text*; three checks: ontology fit, evidence found in the paper, model validator | Every edge lists all papers asserting it and each paper's evidence span | No |

The interdependency concepts in [18, 21] trace back to a standard 2001 framework [22].

**Failure modes reported for literature-derived graphs.**

- *Unsupported edges.* A benchmark for model-based graph extraction measures unsupported triples as a separate metric because the problem is routine [31]. In [25], evidence could not be matched for about 7.7% of triples, falling to about 1.4% once tables and figures were excluded; in a long-standing biomedical system the largest error source was entity recognition and normalization [28, 29].
- *Over-general edges.* The authors of [24] state that their pathways reflect co-occurrence in the literature rather than established causal mechanisms. Separately, a study of 4,900 model-written summaries found them nearly five times more likely than human summaries to broaden a paper's conclusions [32]. That study concerns summaries, not triple extraction; applying it to extraction is my inference, though triple extraction compresses text at least as hard.
- *Loss of context.* In [25] the design cannot tell the paper that established a finding from papers that repeat it, so a support count can overstate independent evidence. The same paper drops many correct statements because they do not fit the schema.
- *Locality mismatch.* I found no study that measures it for hazard graphs. The nearest evidence is corpus bias noted in [24] (most studies from particular regions and periods).

## 2. The locality problem: how graphs represent the scope of an edge

A plain triple (heat → stresses → transformers) carries no place, period, scenario or strength. Published options for attaching them:

1. **Qualifiers on statements.** Wikidata attaches property–value pairs to a statement to state when and where it holds, plus references and a rank [33–35]. Qualifiers carry real information: models that read them outperform triple-only models by a wide margin on graph-completion tests [36].
2. **Reified statements.** The statement becomes a node, and scope, source and status hang off it. Four encodings have been compared for Wikidata-scale data (standard reification, n-ary relations, singleton properties, named graphs) [33]. The current RDF 1.2 drafts add a native form in which a statement can be described *without being asserted* [39], which suits claims that are recorded but not endorsed.
3. **Scope as a context around a group of statements.** Nanopublications package an assertion with its provenance and publication details as separate graphs [37]. The base model assumes one source per assertion; an extension adds a record for assertions aggregated from several sources [38].
4. **Evidence-level versus assembled-level statements, with support.** INDRA keeps each extracted sentence as evidence, merges duplicates into one statement, links statements that are more general or more specific versions of each other, and computes a belief score from all supporting evidence [26, 30]. The general–specific link is the closest published analogue to our problem.
5. **A two-axis strength vocabulary.** IPCC guidance bases confidence on the type, amount, quality and consistency of evidence and on the degree of agreement [40]. That scale is for expert assessment; we could borrow the two axes (how much evidence, how consistent) but should not assign IPCC-style confidence ourselves.
6. **Space as a first-class node.** KnowWhereGraph never attaches a hazard to a place by name alone; both are tied to the same grid cells, so "where" is always explicit [16].

**What none of these does.** They record scope; they do not stop a writer ignoring it. I found no published generator that enforces "a general mechanism may not be worded as locally demonstrated." For our case that means two additions beyond published practice:

- The link between a pattern and a mechanism is typed as *compatibility*, never as *explanation*, and carries a **scope relation** computed by rule: same place / containing region / national / global / different region.
- A deterministic wording check keyed to that scope relation (for example, anything other than "same place" forces general phrasing and forbids "in [state], this is caused by").

The existing pipeline already applies wording rules of this kind per packet; the graph would make the scope relation a stored, countable field.

## 3. Design sketch for our case

**Principle.** Deterministic facts and literature claims are kept as different kinds of edge and never merged. Literature content enters only as reified statements with a verbatim passage.

### Node types

| Node | Source | Notes |
| --- | --- | --- |
| Hazard quantity | Table dictionary | For example "days above a heat-index threshold", "Fire Weather Index". Carries required cautions as attributes: the fire index measures fire-weather conditions, not fire occurrence; baseline values are modeled, not observed |
| Hazard family | Controlled list | Groups quantities and literature terms |
| Place | Table | Three levels: grid cell, state, climate region; containment edges computed |
| Horizon / scenario | Table | Mid-century, end-century; one high-emissions scenario |
| Pattern | Existing pattern file | Direction, size class, rank; one node per existing pattern |
| Mechanism / driver | Existing human-checked claim groups | One node per group; label is the reviewed label |
| Asset class | Infrastructure graph | For example substations, water treatment plants |
| Asset (instance) | Infrastructure graph | Optional; only if place-specific exposure is wanted |
| Impact type | Controlled list, to be agreed | For example reduced capacity, physical damage, service outage |
| Paper, Passage | Both corpora | Passage = verbatim text with offsets and hash |

### Edge types and required qualifiers

| Edge | Kind | Required qualifiers |
| --- | --- | --- |
| Pattern → quantity / place / horizon | Computed | Table hash, rule id |
| Place → within → Place | Computed | Mapping version |
| Statement → supported by → Passage → in → Paper | Recorded | Offsets, hash, evidence role (own finding / cites another study / background) |
| Mechanism → drives or modulates → Hazard family | Literature claim (reified) | Stated scope (geography class and the string as written), period, scenario if stated, claim type, number of independent papers, human-check status |
| Hazard family → affects → Asset class, with Impact type | Literature claim (reified) | Same as above, plus any stated intensity condition |
| Pattern → compatible with → Mechanism | Computed link | Match basis (family, geography class, direction), **scope relation**; never labelled "explains" |
| Asset → instance of → Asset class; Asset → located in → Place; Asset → depends on → Asset | From infrastructure graph | That graph's own provenance and version |
| Pattern → co-located with → Asset class in Place | Computed | Count of assets; means exposure only, not impact |

### Mapping existing artifacts

Patterns become pattern nodes unchanged. Claim groups become mechanism nodes; their member statements and verbatim passages become the supporting chain; existing geography classes and claim-type tags become qualifiers. The current pairing rule becomes the "compatible with" edge. The infrastructure graph supplies asset classes, instances and dependencies. New work is limited to (a) impact statements from infrastructure papers, extracted with the existing statement method and human tag check, and (b) the two shared vocabularies.

### How an agent would form each item type

| Item type | Traversal | Guard |
| --- | --- | --- |
| Pattern only | Pattern → quantity, place, horizon | As now |
| Pattern + mechanism | Pattern → compatible with → Mechanism → passages | Wording set by scope relation and support count |
| Regional comparison | Two patterns, same quantity and horizon, different places; optionally a mechanism whose stated scope names both | No explained contrast without a claim naming the regions |
| Hazard → asset impact | Hazard family → affects → Asset class (+ impact type) → passages | General wording unless stated scope matches |
| Multi-hop: hazard → mechanism → impact | Pattern → Mechanism → Hazard family → affects → Asset class | Each hop must have its own passage; reject paths through very high-degree nodes; check the item is not answerable from one hop alone [6, 12] |

For every item the agent would still receive a packet: the subgraph serialized with its passages. The graph changes how packets are assembled, not what the writer sees.

## 4. Honest comparison

| | Packet per pattern (current, extended to four sources) | Thin statement-centred graph |
| --- | --- | --- |
| Reuse of a claim across items | Copied into each packet | One node, many items; edits propagate |
| Multi-hop items | Needs a new pairing rule per item type | Path queries; new item types are new traversals |
| Scope | Enforced by packet rules and checks | Stored on each edge and countable |
| Coverage statistics | Recomputed per build | Direct: which hazards, places and asset classes have evidence, and how much |
| Join with infrastructure graph | Key-based join in code | Shared node ids |
| Cost | Low; exists | Schema, two vocabularies, loaders, a store, tests |
| Maintenance | Rules per item type | Schema changes ripple through everything |
| Main risk | Rule sprawl as item types grow | Edges look authoritative regardless of support |

**Risks specific to the graph.**

- *One-passage edges.* In the current pilot a large share of claim groups have a single member, so most mechanism edges would rest on one paper. Drawn as a graph they look as solid as well-supported ones. Mitigation: support count and evidence role are mandatory fields, and generation rules read them.
- *The locality mismatch moves, it does not disappear.* If the scope relation is wrong or ignored, the graph produces wrong items faster than packets do.
- *Published accuracy figures do not transfer.* The 88–99% precision figures [24, 25] are for other domains, schemas and models, and partly model-judged.
- *Cross-team vocabulary.* The join depends on hazard families and asset classes meaning the same thing on both sides. This is an organizational cost, not a technical one.

**Not answerable from published work:** whether graph-assembled packets give better closed-book items than rule-assembled packets. No comparison of that kind was found.

**When it is worth building.** If the scientists want hazard → infrastructure and multi-hop items in the hundreds; if claims are reused across many items; if the infrastructure graph has stable asset-class identifiers; and if people can check edge tags at the needed rate. If only a few dozen four-source items are wanted, extending the packet rules is cheaper and equally defensible.

**Minimal pilot.**

- *Scope.* Two hazard families (heat index, fire weather), about five asset classes chosen with the infrastructure team, existing patterns and claim groups, and impact statements from a small set of infrastructure papers.
- *Node and edge types first.* Pattern, place, hazard family, mechanism, asset class, impact type, paper, passage; the "compatible with" and "affects" edges with full qualifiers. No asset instances, no dependency edges.
- *Items.* About 30: 10 pattern + mechanism items regenerated for seeds that already have reviewed items (the graph should reproduce them, not degrade them); 10 hazard → asset items; 10 multi-hop items. In parallel, the same 20 new items attempted with packet rules extended by hand.
- *Evaluation.* Same deterministic checks and same blind human rubric for both arms. Compare: pass rate at the checks; reviewer acceptance; count of scope errors (text implying local demonstration); share of items resting on single-paper edges; reviewer minutes per item; engineering time. For multi-hop items, add a one-hop answerability check.
- *Stop rule.* If the graph arm is not at least equal on acceptance and scope errors, keep packets.

## 5. Recommendation

Make the existing join explicit as a thin, statement-centred graph built from artifacts already produced and human-checked, add asset classes and impact types from the infrastructure side, and avoid open-ended triple extraction, which is where the published failure modes concentrate [8, 24, 28, 31, 32]. Treat every literature edge as a recorded claim with a passage, a stated scope and a support count, and type the pattern-to-mechanism link as compatibility with a computed scope relation. Run the 30-item pilot before committing, because no published comparison tells us the graph will produce better items. The mentors would need to decide: (1) whether infrastructure items stay general (hazard family → asset class) or may be place-specific; (2) the minimum evidence for an edge to appear in graded text and how single-study support is worded; (3) who owns the shared hazard, asset-class and impact vocabularies across the two teams, and whether the pilot goes ahead at this size.

---

## References

Verification marks: **[V]** retrieved in this survey; **[C]** seen only as a citation in another retrieved source.

1. Trivedi, Maheshwari, Dubey, Lehmann. "LC-QuAD: A Corpus for Complex Question Answering over Knowledge Graphs." ISWC 2017. doi:10.1007/978-3-319-68204-4_22 **[V]** (author list from memory)
2. Dubey, Banerjee, Abdelkawi, Lehmann. "LC-QuAD 2.0: A Large Dataset for Complex Question Answering over Wikidata and DBpedia." ISWC 2019. https://jens-lehmann.org/files/2019/iswc_lcquad2.pdf **[V]**
3. Gu, Kase, Vanni, Sadler, Liang, Yan, Su. "Beyond I.I.D.: Three Levels of Generalization for Question Answering on Knowledge Bases." 2021 (The Web Conference; venue from memory). https://arxiv.org/abs/2011.07743 **[V]**
4. Cao, Shi, Pan, Nie, Xiang, Hou, Li, He, Zhang. "KQA Pro: A Dataset with Explicit Compositional Programs for Complex Question Answering over Knowledge Base." ACL 2022. https://aclanthology.org/2022.acl-long.422 **[V]**
5. Ho, Nguyen, Sugawara, Aizawa. "Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps." COLING 2020. doi:10.18653/v1/2020.coling-main.580 **[V]**
6. Min, Wallace, Singh, Gardner, Hajishirzi, Zettlemoyer. "Compositional Questions Do Not Necessitate Multi-hop Reasoning." ACL 2019. doi:10.18653/v1/P19-1416 **[V]**
7. "Would You Ask it that Way? Measuring and Improving Question Naturalness for Knowledge Graph Question Answering." 2022. https://arxiv.org/abs/2205.12768 **[V]** (title and content retrieved; authors and venue not checked)
8. Zhang, Jiang, Chi, Chen, et al. "Diagnosing and Addressing Pitfalls in KG-RAG Datasets: Toward More Reliable Benchmarking" (KGQAGen). NeurIPS 2025. https://arxiv.org/abs/2505.23495 **[V]**
9. Cattaneo, Luschi, Justus. "Ground-Truth Subgraphs for Better Training and Evaluation of Knowledge Graph Augmented LLMs" (SynthKGQA). 2025. https://arxiv.org/abs/2511.04473 **[V]**
10. "Dynamic-KGQA: A Scalable Framework for Generating Adaptive Question Answering Datasets." 2025. https://arxiv.org/abs/2503.05049 **[V]** (authors not checked)
11. "Evaluating Multi-Hop Reasoning in Large Language Models: A Chemistry-Centric Case Study." 2025. https://arxiv.org/abs/2504.16414 **[V]** (authors not checked)
12. Zi, Zhou, Xiao, Moreira, Prasad. "Shattering the Shortcut: A Topology-Regularized Benchmark for Multi-hop Medical Reasoning in LLMs." 2026. https://arxiv.org/abs/2603.12458 **[V]**
13. "HiddenPathQA: A Benchmark for Knowledge Graph Question Answering When Questions Hide Their Paths." NeurIPS 2026 (poster). https://arxiv.org/abs/2611.11802 **[V]** (abstract only; authors not checked)
14. Manivannan, Jafari, Eranky, Ho, Yu, Watson-Parris, Ma, Bergen, Berg-Kirkpatrick. "ClimaQA: An Automated Evaluation Framework for Climate Question Answering Models." ICLR 2025. https://arxiv.org/abs/2410.16701 **[V]**
15. Janowicz, Hitzler, Li, et al. "Know, Know Where, KnowWhereGraph: A densely connected, cross-domain knowledge graph and geo-enrichment service stack for applications in environmental intelligence." AI Magazine 43(1):30–39, 2022. doi:10.1002/aaai.12043 **[V]**
16. "The KnowWhereGraph Ontology." 2024. https://arxiv.org/abs/2410.13948 **[V]** (authors not checked)
17. Zhu, Shimizu, Stephen, Fisher, Thelen, et al. "The KnowWhereGraph: A Large-Scale Geo-Knowledge Graph for Interdisciplinary Knowledge Discovery and Geo-Enrichment." 2025. https://arxiv.org/abs/2502.13874 **[V]**
18. Hahmann, Kedrowski. "An Ontology and Geospatial Knowledge Graph for Reasoning About Cascading Failures (Short Paper)." COSIT 2024, LIPIcs vol. 315. doi:10.4230/LIPIcs.COSIT.2024.21 **[V]**
19. Hofmeister, Brownbridge, Hillman, Mosbach, Akroyd, Lee, Kraft. "Cross-domain flood risk assessment for smart cities using dynamic knowledge graphs." Sustainable Cities and Society 101:105113, 2024. doi:10.1016/j.scs.2023.105113 **[V]**
20. Hofmeister, Bai, Brownbridge, Mosbach, Lee, Farazi, Hillman, Agarwal, Ganguly, Akroyd, Kraft. "Semantic agent framework for automated flood assessment using dynamic knowledge graphs." Data-Centric Engineering 5:14, 2024. https://como.ceb.cam.ac.uk/publications/DE-5-14-/ **[V]**
21. Toscano, Fernandes, Mira da Silva, Santoro. "A domain ontology on cascading effects in critical infrastructures based on a systematic literature review." Int. J. Critical Infrastructures 18(1):79–103, 2022. https://econpapers.repec.org/RePEc:ids:ijcist:v:18:y:2022:i:1:p:79-103 **[V]**
22. Rinaldi, Peerenboom, Kelly. "Identifying, understanding, and analyzing critical infrastructure interdependencies." IEEE Control Systems 21(6):11–25, 2001. **[C]** (no URL retrieved)
23. Mallick et al. "Analyzing the impact of climate change on critical infrastructure from the scientific literature: A weakly supervised NLP approach." 2023. https://arxiv.org/abs/2302.01887 **[V]**
24. Wang, Huang, Gao, Zhang. "HeDA: An Intelligent Agent System for Heatwave Risk Discovery through Automated Knowledge Graph Construction and Multi-layer Risk Propagation Analysis." Preprint, 2025. https://arxiv.org/abs/2509.25112 **[V]** (details taken from an automated reading of the arXiv page, not checked line by line; versions differ in reported sizes; not peer-reviewed as far as I could see)
25. Acharya, Zhang, Dragut, Latecki. "Ontology-Guided Knowledge Graph Construction from Structured Metadata and Climate Science Publications." IJCNLP-AACL 2026, pp. 5615–5642. https://aclanthology.org/2026.aacl-long.252.pdf **[V]** (details taken from an automated reading of the PDF, not checked line by line)
26. INDRA World (software documentation). https://github.com/gyorilab/indra_world **[V]**
27. UNDRR and International Science Council. "Hazard definition and classification review: Technical report (2025)" and Hazard Information Profiles. https://www.undrr.org/publication/documents-and-publications/hazard-definition-and-classification-review-technical-report **[V]**
28. Kilicoglu et al. "Broad-coverage biomedical relation extraction with SemRep." BMC Bioinformatics, 2020. doi:10.1186/s12859-020-3517-7 **[V]** (first author and exact title from memory)
29. Kilicoglu et al. "SemMedDB: a PubMed-scale repository of biomedical semantic predications." Bioinformatics, 2012. https://pmc.ncbi.nlm.nih.gov/articles/PMC3509487 **[V]** (first author and exact title from memory)
30. Bachman, Gyori, Sorger. "Automated assembly of molecular mechanisms at scale from text mining and curated databases." Molecular Systems Biology 19(5):e11325, 2023. doi:10.15252/msb.202211325 **[V]**
31. Mihindukulasooriya, Tiwari, Enguix, Lata. "Text2KGBench: A Benchmark for Ontology-Driven Knowledge Graph Generation from Text." 2023. https://arxiv.org/abs/2308.02357 **[V]**
32. Peters, Chin-Yee. "Generalization bias in large language model summarization of scientific research." Royal Society Open Science 12(4):241776, 2025. doi:10.1098/rsos.241776 **[V]**
33. Hernández, Hogan, Krötzsch. "Reifying RDF: What Works Well With Wikidata?" SSWS workshop, 2015. https://ddll.inf.tu-dresden.de/w/images/5/52/Hernandez-Hogan-Kroetzsch-RDF-reification-evaluation-SSWS2015.pdf **[V]**
34. Wikidata. "Help:Qualifiers." https://www.wikidata.org/wiki/Help:Qualifiers **[V]**
35. Vrandečić, Krötzsch. "Wikidata: a free collaborative knowledgebase." Communications of the ACM, 2014. **[C]** (no URL retrieved)
36. Galkin, Trivedi, Maheshwari, Usbeck, Lehmann. "Message Passing for Hyper-Relational Knowledge Graphs." EMNLP 2020. doi:10.18653/v1/2020.emnlp-main.596 **[V]**
37. Kuhn, Meroño-Peñuela, et al. "Nanopublications: A Growing Resource of Provenance-Centric Scientific Linked Data." 2018. https://arxiv.org/abs/1809.06532 **[V]**
38. Extension of nanopublications to multi-source claims. International Journal on Digital Libraries, 2025. doi:10.1007/s00799-025-00431-x **[V]** (abstract only; title and authors not captured)
39. W3C. "RDF 1.2 Concepts and Abstract Syntax." Working Draft, 2025. https://www.w3.org/TR/rdf12-concepts/ **[V]** (a draft; may change)
40. Mastrandrea, Field, Stocker, Edenhofer, Ebi, Frame, Held, Kriegler, Mach, et al. "Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties." IPCC, 2010. https://www.ipcc.ch/site/assets/uploads/2018/05/uncertainty-guidance-note.pdf **[V]**

**Not covered.** I did not review insurance-industry or commercial climate-risk graphs, non-English literature, or temporal-KG question sets. Statements in sections 3 and 4 about the current pipeline come from project records, not from published work.
