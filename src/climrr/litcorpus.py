"""M4-WP3: freeze LITCORPUS-01 (shard pilot) and LITCORPUS-02 (the 705k arm) from the collection evidence.

**Nothing here reads a paper.** The inputs are the collection evidence bundle
(`litcorpus02_evidence.tar.gz`, extracted outside the repo): query files, hash
lists, logs, id lists, per-run `summary.json`, `hits.csv` (term locations, no
text beyond section headings) and `disambiguation.csv`. The corpus files
themselves stay on Eagle; only manifests, ids, hashes and hit locations are
written under `artifacts/literature/litcorpus0{1,2}/`.

Every copied evidence file is verified against the hash list that came with it
(`reports/query_hashes_v1.txt`, `reports/705k_stage1_hashes.txt`) before it is
copied. Seven evidence files carry absolute Eagle paths; their tracked copies
have each such path replaced by a placeholder, and `redactions.json` records
the original and redacted SHA-256 of each one.

Rules fixed by the work package (M4-WP3; D-020--D-024):

- item id = the source basename (the S2 corpus id), never reinterpreted;
- `LIT2-NNNNNN` assigned once, in code-point order of the item id, over the
  union of the two **admitted** production arms of LITCORPUS-02;
- diagnostic (topical-only) runs are "collection sensitivity diagnostics" and
  get no corpus id;
- year / venue / authors are `unknown` for every item.
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

LIT = REPO_ROOT / "artifacts" / "literature"
L1_DIR = LIT / "litcorpus01"
L2_DIR = LIT / "litcorpus02"
PLACE_DIR = L2_DIR / "place_candidates"
LEGACY_MANIFEST_CSV = LIT / "corpus_manifest.csv"

L1_ID = "LITCORPUS-01-conceptfirst-v1"
L2_ID = "LITCORPUS-02-conceptfirst-705k-v1"

EVIDENCE_TARBALL = "litcorpus02_evidence.tar.gz"
UNKNOWN_METADATA = {"year": "unknown", "venue": "unknown", "authors": "unknown"}
NOT_READ = ("No paper was read, opened for content, or sampled. Retrieval hits are lexical locations, "
            "not claims and not bridges.")

PRODUCTION = ("fire_weather_v1", "extreme_heat_v1")
DIAGNOSTIC = ("fire_weather_diag_topical_only", "extreme_heat_diag_topical_only")
UNUSED = ("fire_weather_v1_btsd_unused", "extreme_heat_v1_btsd_unused")
PLACES = "places_approved"
PLACE_TERMS = ("oklahoma", "stephens", "california")

QUERY_ROLE = {
    **{q: "production (corpus-defining)" for q in PRODUCTION},
    **{q: "collection sensitivity diagnostic (no corpus identity)" for q in DIAGNOSTIC},
    **{q: "unused / not executed as corpus-defining query" for q in UNUSED},
}

PLACE_STATEMENT = ("Lexical hits; role of each place term (study area, affiliation, surname) unknown until "
                   "reading; reading not authorized.")

# Absolute Eagle paths in the evidence -> placeholders. Patterns are assembled from
# fragments so this file holds no literal absolute path (scripts/verify_no_secrets_or_paths.py).
_EAGLE = "/eagl" + "e/"
REDACTION_RULES = (
    ("<LITCOLLECT_ROOT_POLARIS>", re.compile(r"(?:/lus)?" + re.escape(_EAGLE) + r"[^\s\"']*?/climrr-litcollect")),
    ("<EAGLE_DIR>", re.compile(r"(?:/lus)?" + re.escape(_EAGLE) + r"[^\s\"']*/")),
)


class FreezeError(RuntimeError):
    """Evidence does not match its own hash list, or a frozen artifact no longer matches a rebuild."""


# --- helpers ---------------------------------------------------------------------------


def read_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_hash_list(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, rel = line.split(None, 1)
            out[rel.strip()] = digest
    return out


def redact(text: str) -> tuple[str, dict[str, int]]:
    counts = {}
    for placeholder, rx in REDACTION_RULES:
        text, n = rx.subn(placeholder + ("/" if placeholder == "<EAGLE_DIR>" else ""), text)
        if n:
            counts[placeholder] = n
    return text, counts


def _write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8", newline="")


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class _Copier:
    """Copies evidence files, verifying each against a hash list when it is listed there."""

    def __init__(self, ev: Path):
        self.ev = ev
        self.redactions: dict[str, dict] = {}
        self.verified: dict[str, str] = {}

    def copy(self, rel: str, dest: Path, hashes: dict[str, str] | None = None, hash_key: str | None = None) -> None:
        src = self.ev / rel
        digest = sha256_file(src)
        key = hash_key or rel
        if hashes is not None and key in hashes:
            if hashes[key] != digest:
                raise FreezeError(f"{rel}: SHA-256 {digest} differs from its hash list ({hashes[key]})")
            self.verified[rel] = digest
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_bytes().decode("utf-8")
        redacted, counts = redact(text)
        if counts:
            dest.write_text(redacted, encoding="utf-8", newline="")
            self.redactions[dest.relative_to(REPO_ROOT).as_posix()] = {
                "evidence_path": rel, "original_sha256": digest,
                "original_verified_against_hash_list": key in (hashes or {}),
                "redacted_sha256": sha256_file(dest), "substitutions": counts}
        else:
            shutil.copyfile(src, dest)


def _hits(path: Path) -> dict[str, list[dict]]:
    by_doc: dict[str, list[dict]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            r["section_idx"], r["char_start"], r["char_end"] = int(r["section_idx"]), int(r["char_start"]), int(r["char_end"])
            by_doc[r["doc_id"]].append(r)
    return by_doc


def _first(rows: list[dict]) -> dict | None:
    return min(rows, key=lambda r: (r["section_idx"], r["char_start"], -r["char_end"])) if rows else None


def _loc(r: dict | None) -> list:
    return [r["term"], r["section_key"], r["section_idx"], r["char_start"], r["char_end"]] if r else ["", "", "", "", ""]


# --- LITCORPUS-01 ----------------------------------------------------------------------


def freeze_litcorpus01(ev: Path) -> dict:
    cp = _Copier(ev)
    qhashes = read_hash_list(ev / "reports" / "query_hashes_v1.txt")
    out = L1_DIR
    for q in (*PRODUCTION, *DIAGNOSTIC, *UNUSED):
        rel = f"queries/{q}_query.txt"
        if rel not in qhashes:
            raise FreezeError(f"{rel} is not in query_hashes_v1.txt")
        cp.copy(rel, out / rel, qhashes)
    for name in ("query_hashes_v1.txt", "araiadoc_commit.txt", "shard_listing.txt", "fwi_collision_snippets.txt",
                 "litcorpus01_raw_hashes.txt", *(f"{q}_extract.log" for q in (*PRODUCTION, *DIAGNOSTIC))):
        cp.copy(f"reports/{name}", out / "evidence" / name)
    for q in (*PRODUCTION, *DIAGNOSTIC):
        cp.copy(f"ids/{q}_ids.txt", out / "ids" / f"{q}_ids.txt")

    raw = read_hash_list(ev / "reports" / "litcorpus01_raw_hashes.txt")
    by_run: dict[str, dict[str, tuple[str, str]]] = defaultdict(dict)
    for rel, digest in raw.items():
        parts = rel.split("/")  # raw/<run>/<bucket>/<id>.json
        by_run[parts[1]][Path(rel).stem] = (rel, digest)
    for q in (*PRODUCTION, *DIAGNOSTIC):
        ids = read_ids(ev / "ids" / f"{q}_ids.txt")
        if sorted(ids) != sorted(by_run[q]):
            raise FreezeError(f"LITCORPUS-01 {q}: id list and raw-record hash list disagree")
        log = (ev / "reports" / f"{q}_extract.log").read_text(encoding="utf-8")
        m = re.search(r"DuckDB returned (\d+) unique document", log)
        if not m or int(m.group(1)) != len(ids):
            raise FreezeError(f"LITCORPUS-01 {q}: extract log count differs from the id list")

    prod_rows = [[i, q, by_run[q][i][0], by_run[q][i][1]] for q in PRODUCTION for i in sorted(by_run[q])]
    _write_csv(out / "litcorpus01_manifest.csv", ["item_id", "arm", "rel_path", "sha256"], prod_rows)
    diag_rows = [[i, q, by_run[q][i][0], by_run[q][i][1],
                  int(i in by_run[q.replace("_diag_topical_only", "_v1")])]
                 for q in DIAGNOSTIC for i in sorted(by_run[q])]
    _write_csv(out / "litcorpus01_diagnostics.csv", ["item_id", "diagnostic_run", "rel_path", "sha256",
                                                     "in_production_arm"], diag_rows)

    fire, heat = set(by_run["fire_weather_v1"]), set(by_run["extreme_heat_v1"])
    shas: dict[str, list[str]] = defaultdict(list)
    for r in prod_rows:
        shas[r[3]].append(f"{r[1]}:{r[0]}")
    collisions = re.findall(r"^== (\d+):", (ev / "reports" / "fwi_collision_snippets.txt").read_text(encoding="utf-8"),
                            re.MULTILINE)
    listing = (ev / "reports" / "shard_listing.txt").read_text(encoding="utf-8").split()
    shard_bytes, shard_name = int(listing[4]), Path(listing[-1]).name

    summary = {
        "corpus_id": L1_ID,
        "role": "provenance/yield pilot; not the bridge corpus (D-022)",
        "status": "frozen; retained, not discarded (D-024)",
        "source": {
            "kind": "S2ORC v1 shard, via ANL araiadoc",
            "shard_filename": shard_name,
            "shard_bytes": shard_bytes,
            "shard_bytes_source": "evidence/shard_listing.txt (ls -l on Eagle; directory redacted)",
            "records": 54081,
            "records_provenance": "reported by the collection-tool team; not computed by this project",
            "composition": "~48% PubMed, ~18% arXiv --- reported by the collection-tool team; not computed by this project",
        },
        "collection_tool": {
            "araiadoc_commit": (ev / "reports" / "araiadoc_commit.txt").read_text(encoding="utf-8").strip(),
            "matcher": "DuckDB, whole-word, case-insensitive, no stemming, over the concatenated document "
                       "(as reported for araiadoc; the 705k arm matches per section)",
            "duckdb_settings": "threads=1, memory_limit=16GB (extract logs)",
            "host": "Polaris login node",
            "date": "2026-10-12",
        },
        "queries": {q: {"file": f"queries/{q}_query.txt", "sha256": qhashes[f"queries/{q}_query.txt"],
                        "role": QUERY_ROLE[q]} for q in (*PRODUCTION, *DIAGNOSTIC, *UNUSED)},
        "yields": {
            **{q: {"count": len(by_run[q]), "role": QUERY_ROLE[q]} for q in (*PRODUCTION, *DIAGNOSTIC)},
            "cross_arm_overlap": sorted(fire & heat),
            "unique_production_items": len(fire | heat),
            "exact_byte_duplicate_groups_in_production": [v for v in shas.values() if len(v) > 1],
        },
        "fwi_collision_evidence": {
            "file": "evidence/fwi_collision_snippets.txt",
            "documents": collisions,
            "in_fire_weather_v1_arm": sorted(set(collisions) & fire),
            "statement": "at most 2 plausible FWI papers in the 4-paper arm before reading (D-022)",
        },
        "rfwi1_retroactive": {
            "status": "pending --- not computed",
            "reason": "the four raw records are hash-pinned on Eagle and not available on the authoring host; "
                      "scripts/litcollect/apply_rfwi1_litcorpus01.py applies climrr.retrieval R-FWI-1 v1 to them "
                      "after verifying each SHA-256, for Kaiyuan to run on Polaris",
        },
        "manifest": {"production_csv": "litcorpus01_manifest.csv",
                     "production_csv_sha256": sha256_file(out / "litcorpus01_manifest.csv"),
                     "diagnostics_csv": "litcorpus01_diagnostics.csv",
                     "diagnostics_csv_sha256": sha256_file(out / "litcorpus01_diagnostics.csv")},
        "item_id_rule": "item id = source basename (S2 corpus id); per-item SHA-256 of the raw record from "
                        "evidence/litcorpus01_raw_hashes.txt",
        "sectionization": "deferred (disclosed deviation): GUIDANCE is asked to confirm LITCORPUS-02 supersedes "
                          "LITCORPUS-01 as the working corpus first",
        "metadata": UNKNOWN_METADATA,
        "not_read": NOT_READ,
        "storage": "raw records external on Eagle; never in Git",
    }
    _write_json(out / "litcorpus01_manifest.json", summary)
    _write_json(out / "redactions.json", {"rule": _redaction_rule_text(), "files": cp.redactions})
    return summary


def _redaction_rule_text() -> str:
    return ("Every absolute Eagle path ending in the litcollect root (either spelling, with or without the "
            "/lus prefix) is replaced by <LITCOLLECT_ROOT_POLARIS> (real value: config/local_paths.yaml:"
            "litcollect_root_polaris); any other absolute Eagle directory prefix by <EAGLE_DIR>/. Nothing else "
            "is changed. original_sha256 is the evidence file as received.")


# --- LITCORPUS-02 ----------------------------------------------------------------------


def freeze_litcorpus02(ev: Path) -> dict:
    cp = _Copier(ev)
    h = read_hash_list(ev / "reports" / "705k_stage1_hashes.txt")
    qh = read_hash_list(ev / "reports" / "query_hashes_v1.txt")
    out, E = L2_DIR, L2_DIR / "evidence"
    R = "runs/705k"

    for rel in ("index/full_705k_v2_filtered/index_summary.json",):
        cp.copy(rel, E / "index_summary.json", h)
    for name in ("705k_stage1_hashes.txt", "705k_stage1.log"):
        cp.copy(f"reports/{name}", E / name)
    cp.copy("sources/full_705k_v2_filtered.zip.sha256", E / "full_705k_v2_filtered.zip.sha256")
    for q in (*PRODUCTION, *DIAGNOSTIC):
        cp.copy(f"queries/{q}_query.txt", E / "queries" / f"{q}_query.txt", h)
        for f in ("summary.json", "ids.txt", "ids_raw.txt"):
            cp.copy(f"{R}/{q}/{f}", E / "runs" / q / f, h)
        if q.startswith("fire_weather"):
            cp.copy(f"{R}/{q}/disambiguation.csv", E / "runs" / q / "disambiguation.csv", h)
    for q in PRODUCTION:
        cp.copy(f"{R}/{q}/hits.csv", E / "runs" / q / "hits.csv", h)

    summaries = {q: json.loads((ev / R / q / "summary.json").read_text(encoding="utf-8")) for q in (*PRODUCTION, *DIAGNOSTIC)}
    index = json.loads((ev / "index/full_705k_v2_filtered/index_summary.json").read_text(encoding="utf-8"))
    for q, s in summaries.items():
        if s["query_sha256"] != qh[f"queries/{q}_query.txt"]:
            raise FreezeError(f"{q}: 705k query_sha256 differs from the shard run's query hash")
        if s["index"]["content_identity_sha256"] != index["content_identity_sha256"]:
            raise FreezeError(f"{q}: run index identity differs from index_summary.json")
        if len(read_ids(ev / R / q / "ids.txt")) != s["admitted_count"] or \
                len(read_ids(ev / R / q / "ids_raw.txt")) != s["raw_count"]:
            raise FreezeError(f"{q}: id-list lengths differ from summary.json")

    arm_ids = {q: read_ids(ev / R / q / "ids.txt") for q in PRODUCTION}
    hits = {q: _hits(ev / R / q / "hits.csv") for q in PRODUCTION}
    for q in PRODUCTION:
        if set(hits[q]) != set(arm_ids[q]):
            raise FreezeError(f"{q}: hits.csv does not cover exactly the admitted ids")
    meta = {}
    for q in PRODUCTION:
        for d, rows in hits[q].items():
            m = (rows[0]["rel_path"], rows[0]["sha256"])
            if any((r["rel_path"], r["sha256"]) != m for r in rows) or meta.setdefault(d, m) != m:
                raise FreezeError(f"{d}: inconsistent rel_path/sha256 across hit rows")
            if Path(m[0]).name != f"{d}.json":
                raise FreezeError(f"{d}: rel_path basename is not the item id")

    union = sorted(set(arm_ids[PRODUCTION[0]]) | set(arm_ids[PRODUCTION[1]]))
    lit2 = {d: f"LIT2-{i:06d}" for i, d in enumerate(union, 1)}
    for q in PRODUCTION:
        _write_csv(out / f"{q}_manifest.csv", ["item_id", "lit2_id", "arm", "rel_path", "sha256"],
                   [[d, lit2[d], q, *meta[d]] for d in arm_ids[q]])
    _write_csv(out / "lit2_ids.csv", ["lit2_id", "item_id", "arms", "rel_path", "sha256"],
               [[lit2[d], d, ";".join(q for q in PRODUCTION if d in set(arm_ids[q])), *meta[d]] for d in union])

    # R-FWI-1 evidence for the fire arm: run decision + first bare / disambiguator / direct hit.
    fq = PRODUCTION[0]
    with (ev / R / fq / "disambiguation.csv").open(encoding="utf-8", newline="") as f:
        dis = list(csv.DictReader(f))
    raw_ids = read_ids(ev / R / fq / "ids_raw.txt")
    if sorted(r["doc_id"] for r in dis) != sorted(raw_ids):
        raise FreezeError("disambiguation.csv does not cover exactly the raw fire-weather ids")
    rows, basis_counts = [], defaultdict(int)
    for r in sorted(dis, key=lambda r: r["doc_id"]):
        d, hr = r["doc_id"], hits[fq].get(r["doc_id"], [])
        bare = _first([x for x in hr if x["group"] == "0" and x["term"] == "fwi"])
        direct = _first([x for x in hr if x["group"] == "0" and x["term"] != "fwi"])
        disamb = _first([x for x in hr if x["group"] == "D"])
        if r["admitted"] == "1" and r["bare_fwi_only"] == "0":
            basis = "direct_topical_term"
            ok = direct is not None
        elif r["admitted"] == "1":
            basis = "bare_fwi_with_same_document_disambiguator"
            ok = bare is not None and disamb is not None and direct is None
        else:
            basis = "bare_fwi_without_disambiguator"
            ok = d not in hits[fq]
        if not ok:
            raise FreezeError(f"{d}: R-FWI-1 decision is not supported by the recorded hit locations")
        basis_counts[basis] += 1
        rows.append([d, lit2.get(d, ""), r["bare_fwi_only"], r["disambiguator_found"], r["admitted"], basis,
                     *_loc(bare), *_loc(disamb), *_loc(direct)])
    loc_cols = lambda p: [f"{p}_term", f"{p}_section_key", f"{p}_section_idx", f"{p}_char_start", f"{p}_char_end"]
    _write_csv(out / "rfwi1_fire_weather_v1.csv",
               ["item_id", "lit2_id", "bare_fwi_only", "disambiguator_found", "admitted", "rfwi1_basis",
                *loc_cols("bare"), *loc_cols("disambiguator"), *loc_cols("direct")], rows)

    # Overlaps, duplicates, legacy.
    fire, heat = set(arm_ids[PRODUCTION[0]]), set(arm_ids[PRODUCTION[1]])
    with LEGACY_MANIFEST_CSV.open(encoding="utf-8", newline="") as f:
        legacy = {Path(r["basename"]).stem: r for r in csv.DictReader(f)}
    legacy_ids_ev = read_ids(ev / "ids" / "previous_corpus_ids.txt")
    if sorted(legacy_ids_ev) != sorted(legacy):
        raise FreezeError("previous_corpus_ids.txt differs from the LITCORPUS-00 manifest basenames")
    full_ids = set(read_ids(ev / "ids" / "full_705k_ids.txt"))

    def dup_groups(ids):
        g = defaultdict(list)
        for d in sorted(ids):
            g[meta[d][1]].append(d)
        return [{"sha256": k, "item_ids": v, "lit2_ids": [lit2[x] for x in v]} for k, v in sorted(g.items()) if len(v) > 1]

    def legacy_overlap(ids):
        return [{"item_id": d, "lit2_id": lit2[d], "litcorpus00_item_id": legacy[d]["item_id"],
                 "rel_path_705k": meta[d][0],
                 "sha256_equal_to_litcorpus00": meta[d][1] == legacy[d]["sha256"]} for d in sorted(ids & set(legacy))]

    yields = {}
    for q in (*PRODUCTION, *DIAGNOSTIC):
        s = summaries[q]
        yields[q] = {"role": QUERY_ROLE[q], "raw_count": s["raw_count"], "admitted_count": s["admitted_count"],
                     "excluded_by_rfwi1": s["excluded_by_disambiguation"], "disambiguation_arg": s["disambiguation"],
                     "per_group_doc_counts": s["per_group_doc_counts"], "per_term_doc_counts": s["per_term_doc_counts"]}
    overlaps = {
        "cross_arm_overlap": [{"item_id": d, "lit2_id": lit2[d], "rel_path": meta[d][0], "sha256": meta[d][1]}
                              for d in sorted(fire & heat)],
        "union_admitted": len(union),
        "exact_byte_duplicate_groups": {q: dup_groups(set(arm_ids[q])) for q in PRODUCTION} | {"union": dup_groups(set(union))},
        "redundant_copies": {q: sum(len(g["item_ids"]) - 1 for g in dup_groups(set(arm_ids[q]))) for q in PRODUCTION}
                            | {"union": sum(len(g["item_ids"]) - 1 for g in dup_groups(set(union)))},
        "duplicate_policy": "identified, not removed; every copy keeps its own item id and LIT2 id",
        "litcorpus00_in_source": {"present": len(set(legacy) & full_ids), "of": len(legacy)},
        "litcorpus00_overlap": {q: legacy_overlap(set(arm_ids[q])) for q in PRODUCTION},
        "production_within_diagnostic": {
            q: len(set(arm_ids[q]) & set(read_ids(ev / R / q.replace("_v1", "_diag_topical_only") / "ids.txt")))
            for q in PRODUCTION},
        "context_clause_removes": {
            q: summaries[q.replace("_v1", "_diag_topical_only")]["raw_count"] - summaries[q]["raw_count"]
            for q in PRODUCTION},
        "rfwi1_basis_counts_fire_weather_v1": dict(sorted(basis_counts.items())),
    }
    _write_json(out / "overlaps.json", overlaps)

    places = freeze_place_candidates(ev, cp, h, arm_ids, lit2)

    summary = {
        "corpus_id": L2_ID,
        "definition": "the union of the admitted fire_weather_v1 and extreme_heat_v1 arms, produced by the frozen v1 "
                      "queries + R-FWI-1 over the D-023 source (D-024)",
        "source": {
            "name": "full_705k_v2_filtered.zip",
            "supplied_by": "JL, via Google Drive link (D-023)",
            "zip_bytes": 2283251035,
            "zip_sha256": (ev / "sources/full_705k_v2_filtered.zip.sha256").read_text(encoding="utf-8").split()[0],
            "files": index["files"], "unpacked_bytes": index["total_bytes"],
            "directories": index["buckets"],
            "directories_note": "the source's own layout, recorded not interpreted: 00-62, 64-99 and one named "
                                "'unknown' (2,126 files); there is no directory 63 (evidence/705k_stage1.log)",
            "filtering_705k_to_186346": "unknown (Q22)",
            "parent_705k_provenance": "JL's; reported, not verified",
            "location": "Eagle, under config/local_paths.yaml:litcollect_root_polaris; immutable from receipt",
        },
        "index": {k: index[k] for k in ("files", "parse_failures", "section_rows", "total_bytes", "distinct_sha256",
                                        "manifest_csv_sha256", "content_identity_sha256", "content_identity_rule",
                                        "duckdb_version", "python", "built_utc")}
                 | {"exact_byte_redundant_copies_in_source": index["files"] - index["distinct_sha256"],
                    "manifest_csv": "external (not in the evidence bundle); identified by manifest_csv_sha256"},
        "matcher": summaries[PRODUCTION[0]]["matcher"],
        "matcher_difference_from_litcorpus01": "per-section rather than concatenated-document matching: a phrase "
                                               "cannot straddle a section boundary",
        "queries_byte_identical_to_litcorpus01": all(
            summaries[q]["query_sha256"] == qh[f"queries/{q}_query.txt"] for q in (*PRODUCTION, *DIAGNOSTIC)),
        "rfwi1": {"rule": "R-FWI-1 v1 (D-022)", "run_argument": summaries[PRODUCTION[0]]["disambiguation"],
                  "evidence": "rfwi1_fire_weather_v1.csv"},
        "execution": {q: {"run_utc": summaries[q]["run_utc"], "threads": summaries[q]["threads"],
                          "memory_limit": summaries[q]["memory_limit"], "duckdb_version": summaries[q]["duckdb_version"]}
                      for q in (*PRODUCTION, *DIAGNOSTIC)} | {"host": "polaris-login-01 (evidence/705k_stage1.log)"},
        "yields": yields,
        "stable_ids": {"item_id_rule": "source basename (S2 corpus id)",
                       "lit2_rule": "LIT2-NNNNNN in code-point order of item id over the union of the two admitted arms",
                       "n": len(union), "first": lit2[union[0]], "last": lit2[union[-1]]},
        "manifests": {f"{q}_manifest.csv": sha256_file(out / f"{q}_manifest.csv") for q in PRODUCTION}
                     | {"lit2_ids.csv": sha256_file(out / "lit2_ids.csv"),
                        "rfwi1_fire_weather_v1.csv": sha256_file(out / "rfwi1_fire_weather_v1.csv"),
                        "overlaps.json": sha256_file(out / "overlaps.json")},
        "manifest_bytes_column": "omitted: per-item byte counts are not in the evidence bundle",
        "place_candidates": places,
        "metadata": UNKNOWN_METADATA,
        "not_read": NOT_READ,
        "storage": "corpus files external on Eagle; only manifests, ids, hashes and hit locations are tracked",
        "verified_against_hash_lists": dict(sorted(cp.verified.items())),
    }
    _write_json(out / "litcorpus02_manifest.json", summary)
    _write_json(out / "redactions.json", {"rule": _redaction_rule_text(), "files": cp.redactions})
    return summary


def freeze_place_candidates(ev: Path, cp: _Copier, h: dict[str, str], arm_ids: dict, lit2: dict) -> dict:
    R, out = "runs/705k", PLACE_DIR
    cp.copy(f"queries/{PLACES}_query.txt", out / f"{PLACES}_query.txt", h)
    cp.copy(f"{R}/{PLACES}/summary.json", out / "summary.json", h)
    cp.copy(f"{R}/{PLACES}/ids.txt", out / "ids.txt", h)
    s = json.loads((ev / R / PLACES / "summary.json").read_text(encoding="utf-8"))
    place_ids = set(read_ids(ev / R / PLACES / "ids.txt"))
    phits = _hits(ev / R / PLACES / "hits.csv")
    if set(phits) != place_ids or len(place_ids) != s["admitted_count"]:
        raise FreezeError("places hits.csv / ids.txt / summary.json disagree")
    result = {"query": f"{PLACES}_query.txt", "query_sha256": s["query_sha256"],
              "query_text": s["query_text"].strip(), "source_documents_matched": len(place_ids),
              "per_term_source_documents": s["per_term_doc_counts"], "arms": {},
              "first_hits_csv": "first_hits.csv", "candidate_hits_csv": "candidate_hits.csv",
              "statement": PLACE_STATEMENT, "frozen_before_reading": True}
    hit_rows, first_rows = [], []
    for q in PRODUCTION:
        name = f"{q}_place_candidates.txt"
        cp.copy(f"{R}/{name}", out / name, h, hash_key=f"{R}/{name}")
        cands = read_ids(ev / R / name)
        if cands != sorted(set(arm_ids[q]) & place_ids):
            raise FreezeError(f"{name} is not the sorted intersection of the arm and the place hits")
        for d in cands:
            for r in phits[d]:
                hit_rows.append([q, d, lit2[d], r["term"], r["section_key"], r["section_idx"], r["char_start"], r["char_end"]])
            for t in PLACE_TERMS:
                f = _first([r for r in phits[d] if r["term"] == t])
                if f:
                    first_rows.append([q, d, lit2[d], t, f["section_key"], f["section_idx"], f["char_start"], f["char_end"]])
        result["arms"][q] = {"candidates": len(cands), "list": name, "list_sha256": sha256_file(out / name),
                             "per_term": {t: sum(1 for d in cands if any(r["term"] == t for r in phits[d]))
                                          for t in PLACE_TERMS}}
    header = ["arm", "item_id", "lit2_id", "term", "section_key", "section_idx", "char_start", "char_end"]
    _write_csv(out / "candidate_hits.csv", header, hit_rows)
    _write_csv(out / "first_hits.csv", header, first_rows)
    result["first_hits_csv_sha256"] = sha256_file(out / "first_hits.csv")
    result["candidate_hits_csv_sha256"] = sha256_file(out / "candidate_hits.csv")
    _write_json(out / "place_candidates.json", result)
    return result


def external_corpus_entries(l1: dict, l2: dict) -> list[dict]:
    """The `data/manifest.json` `external_corpora` entries for LITCORPUS-01 and -02."""
    return [
        {"corpus_id": L1_ID, "role": l1["role"], "tracked_in_git": False,
         "config_key": "litcollect_root_polaris",
         "source": l1["source"]["shard_filename"], "araiadoc_commit": l1["collection_tool"]["araiadoc_commit"],
         "manifest_path": "artifacts/literature/litcorpus01/litcorpus01_manifest.csv",
         "manifest_sha256": l1["manifest"]["production_csv_sha256"],
         "summary_path": "artifacts/literature/litcorpus01/litcorpus01_manifest.json",
         "summary_sha256": sha256_file(L1_DIR / "litcorpus01_manifest.json"),
         "n_items": l1["yields"]["unique_production_items"],
         "metadata": UNKNOWN_METADATA, "decision_ref": "D-022, D-024"},
        {"corpus_id": L2_ID, "role": "concept-first corpus: union of the two admitted production arms",
         "tracked_in_git": False, "config_key": "litcollect_root_polaris",
         "source_zip_sha256": l2["source"]["zip_sha256"], "source_files": l2["source"]["files"],
         "index_content_identity_sha256": l2["index"]["content_identity_sha256"],
         "index_manifest_csv_sha256": l2["index"]["manifest_csv_sha256"],
         "arm_manifests": {f"artifacts/literature/litcorpus02/{k}": v for k, v in l2["manifests"].items()
                           if k.endswith("_manifest.csv") or k == "lit2_ids.csv"},
         "summary_path": "artifacts/literature/litcorpus02/litcorpus02_manifest.json",
         "summary_sha256": sha256_file(L2_DIR / "litcorpus02_manifest.json"),
         "n_items": l2["stable_ids"]["n"], "metadata": UNKNOWN_METADATA, "decision_ref": "D-023, D-024"},
    ]
