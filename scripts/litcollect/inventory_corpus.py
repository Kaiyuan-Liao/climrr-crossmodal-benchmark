#!/usr/bin/env python3
"""Inventory of a flat-JSON literature corpus (work package P5a; D-070) --- the LITCORPUS-02 inventory, generalised.

Corpus layout: <root>/<shard>/<id>.json, each file a JSON object keyed by section heading (the JL family: section-keyed
string text, plus `_araiadoc_tags` in LITCORPUS-03). For LITCORPUS-03 the root is the extracted `kept/` directory, so the
content identity below equals the one `build_index.py --root <kept>` writes.

Reads every file read-only, as raw bytes; nothing is repaired, normalised in place or written next to the corpus. Reports:
- counts: files, bytes, parse failures, non-object files, ids seen in more than one shard;
- shards: files per shard directory;
- sections: string sections per file (min / quartiles / max), distinct section keys, the 30 most frequent keys by
  document frequency, non-string values per key (top 30);
- `_araiadoc_tags`: the value's JSON type per file and the distribution of its values (list elements / the string /
  `key=value` for an object), the top `--top-tags` (default 20) and the number of distinct values. What JL's pipeline left
  is recorded, not interpreted;
- duplicates: by content hash (SHA-256 of the bytes) and by normalised title (NFKC, lowercase, every character outside
  [a-z0-9] a space, whitespace collapsed; titles shorter than 10 characters after normalisation are not compared) ---
  group counts, redundant copies, the first 10 groups;
- overlap with another corpus by paper id (`--compare-ids`: a build_index manifest.csv --- `doc_id` column --- or a text
  file of ids, one per line): count and the first 20 ids, sorted;
- content identity: SHA-256 of UTF-8 lines 'rel_path<TAB>sha256<TAB>bytes<LF>' in rel_path order (the build_index rule).

v1.1 (P5a hotfix, 2026-11-23): parses `_araiadoc_tags.critical_infrastructure.sectors[]` ({sector, subsectors[]}; the
CISA sector names JL's pipeline wrote) into `asset_sector_tag` per paper --- a list of 'sector/subsector' strings ('sector'
alone when a sector has no subsector), `origin: external_model (JL pipeline)`. The report adds `sector_tags`: files with the
entry / with >= 1 sector, the shape problems met (counted, never repaired), files per sector name and per sector/subsector,
and the MAPPING of each sector name to a class of infrastructure_lexicon_v1 BY NAME (`CISA_SECTOR_CLASSES`, equal to the
lexicon --- tested): `exact` (lowercase, '&' -> 'and', non-alphanumerics -> space, a trailing 'sector' dropped, then equal)
or `prefix` (its words a leading run of exactly one CISA name's words: 'Transportation' -> transportation_systems), else
`unmapped` (reported with its file count). `--tags-out PATH` writes one JSON line per parsed file in rel_path order:
{doc_id, rel_path, sha256, asset_sector_tag, sector_names, origin} --- the input of run_query.py v4.1 `--sector-tags`
(the index does not hold the tags: build_index.py stores string sections only). The tags are the pipeline's labels,
recorded, not verified and not the paper's words. Everything else as v1.

Usage (Polaris; standalone --- Python 3 standard library only):
  python inventory_corpus.py --root <kept dir> --out litcorpus03_inventory.json --corpus-id LITCORPUS-03 \\
      --compare-ids <186k index>/manifest.csv --compare-label LITCORPUS-02-source-186k \\
      --tags-out litcorpus03_sector_tags.jsonl
The JSON written is the run evidence (no run record: an external collection tool, as build_index.py / run_query.py).
"""
import argparse, csv, hashlib, json, re, statistics, sys, time, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "inventory_corpus v1.1"
TAGS_KEY = "_araiadoc_tags"
MIN_TITLE_CHARS = 10
CI_KEY = "critical_infrastructure"
TAG_ORIGIN = "external_model (JL pipeline)"
#: The class ids and CISA sector names of data/metadata/litstatements/infrastructure_lexicon_v1.yaml (equality is tested).
CISA_SECTOR_CLASSES = (
    ("chemical", "Chemical Sector"), ("commercial_facilities", "Commercial Facilities Sector"),
    ("communications", "Communications Sector"), ("critical_manufacturing", "Critical Manufacturing Sector"),
    ("dams", "Dams Sector"), ("defense_industrial_base", "Defense Industrial Base Sector"),
    ("emergency_services", "Emergency Services Sector"), ("energy", "Energy Sector"),
    ("financial_services", "Financial Services Sector"), ("food_and_agriculture", "Food and Agriculture Sector"),
    ("government_services_and_facilities", "Government Services and Facilities Sector"),
    ("healthcare_and_public_health", "Healthcare and Public Health Sector"),
    ("information_technology", "Information Technology Sector"),
    ("nuclear_reactors_materials_and_waste", "Nuclear Reactors, Materials, and Waste Sector"),
    ("transportation_systems", "Transportation Systems Sector"), ("water_and_wastewater", "Water and Wastewater Sector"))


def norm_sector(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", " ", name.lower().replace("&", " and ")).split()
    if s and s[-1] == "sector":
        s = s[:-1]
    return " ".join(s)


def map_sector_name(name: str) -> dict:
    """v1.1: {class_id, match} by name --- exact, else a unique word prefix, else unmapped (climrr.infra_lexicon twin)."""
    names = [(cid, norm_sector(n).split()) for cid, n in CISA_SECTOR_CLASSES]
    w = norm_sector(name).split()
    exact = [cid for cid, n in names if n == w]
    if exact:
        return {"class_id": exact[0], "match": "exact"}
    pre = [cid for cid, n in names if w and len(w) < len(n) and n[:len(w)] == w]
    return {"class_id": pre[0], "match": "prefix"} if len(pre) == 1 else {"class_id": None, "match": "unmapped"}


def sector_tags(tags) -> tuple[list, list, list]:
    """v1.1: (asset_sector_tag, sector_names, problems) from one file's `_araiadoc_tags` value. Nothing is repaired: an
    entry of the wrong shape is skipped and named in `problems`."""
    problems = []
    if not isinstance(tags, dict):
        return [], [], ["tags_not_object"]
    ci = tags.get(CI_KEY)
    if ci is None:
        return [], [], ["no_critical_infrastructure_entry"]
    if not isinstance(ci, dict):
        return [], [], ["critical_infrastructure_not_object"]
    secs = ci.get("sectors")
    if secs is None:
        return [], [], ["no_sectors_key"]
    if not isinstance(secs, list):
        return [], [], ["sectors_not_list"]
    out, names = [], []
    for e in secs:
        if not (isinstance(e, dict) and isinstance(e.get("sector"), str) and e["sector"].strip()):
            problems.append("sector_entry_malformed")
            continue
        name = e["sector"].strip()
        subs = e.get("subsectors")
        if subs is None:
            subs = []
        if not isinstance(subs, list):
            problems.append("subsectors_not_list")
            subs = []
        good = [x.strip() for x in subs if isinstance(x, str) and x.strip()]
        if len(good) != len(subs):
            problems.append("subsector_malformed")
        if name not in names:
            names.append(name)
        for t in ([f"{name}/{x}" for x in good] or [name]):
            if t not in out:
                out.append(t)
    return out, names, problems


def norm_title(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]", " ", s)).strip()


def tag_values(v):
    if isinstance(v, list):
        return [x if isinstance(x, str) else json.dumps(x, sort_keys=True, ensure_ascii=False) for x in v]
    if isinstance(v, dict):
        return [f"{k}={x if isinstance(x, str) else json.dumps(x, sort_keys=True, ensure_ascii=False)}" for k, x in v.items()]
    return [v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)]


def jtype(v) -> str:
    return {dict: "object", list: "array", str: "string", bool: "boolean", type(None): "null"}.get(type(v), "number")


def load_compare_ids(path: Path) -> set:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and "doc_id" in lines[0].split(","):
        return {r["doc_id"] for r in csv.DictReader(lines)}
    return {x.strip() for x in lines if x.strip()}


def quartiles(xs):
    if not xs:
        return None
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
    return {"min": xs[0], "q1": q[0], "median": q[1], "q3": q[2], "max": xs[-1], "mean": round(sum(xs) / len(xs), 2)}


def inventory(root: Path, top_tags: int = 20, compare=None, compare_label=None, tags_out=None) -> dict:
    files = sorted((p for p in root.rglob("*.json") if p.is_file()), key=lambda p: p.relative_to(root).as_posix())
    shards, key_df, nonstring_key, tag_type, tag_counter = Counter(), Counter(), Counter(), Counter(), Counter()
    by_sha, by_title, ids = defaultdict(list), defaultdict(list), defaultdict(list)
    n_sections, total_bytes, parse_fail, not_object, files_with_title = [], 0, [], [], 0
    ident = hashlib.sha256()
    st_files_entry, st_files_sector, st_problems, st_sector, st_tag = 0, 0, Counter(), Counter(), Counter()
    tag_fh = open(tags_out, "w", encoding="utf-8") if tags_out else None
    for p in files:
        rel = p.relative_to(root).as_posix()
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        total_bytes += len(raw)
        ident.update(f"{rel}\t{sha}\t{len(raw)}\n".encode("utf-8"))
        shards[str(Path(rel).parent)] += 1
        by_sha[sha].append(rel)
        ids[p.stem].append(rel)
        try:
            obj = json.loads(raw.decode("utf-8"))
        except Exception:  # noqa: BLE001
            parse_fail.append(rel)
            continue
        if not isinstance(obj, dict):
            not_object.append(rel)
            continue
        ns = 0
        for k, v in obj.items():
            key_df[k] += 1
            if isinstance(v, str):
                ns += 1
            else:
                nonstring_key[k] += 1
        n_sections.append(ns)
        if TAGS_KEY in obj:
            tag_type[jtype(obj[TAGS_KEY])] += 1
            tag_counter.update(tag_values(obj[TAGS_KEY]))
        else:
            tag_type["absent"] += 1
        ast, names, probs = sector_tags(obj.get(TAGS_KEY)) if TAGS_KEY in obj else ([], [], ["tags_absent"])
        if isinstance(obj.get(TAGS_KEY), dict) and isinstance(obj[TAGS_KEY].get(CI_KEY), dict):
            st_files_entry += 1
        st_files_sector += bool(names)
        st_problems.update(set(probs))
        st_sector.update(names)
        st_tag.update(ast)
        if tag_fh:
            tag_fh.write(json.dumps({"doc_id": p.stem, "rel_path": rel, "sha256": sha, "asset_sector_tag": ast,
                                     "sector_names": names, "origin": TAG_ORIGIN}, ensure_ascii=False) + "\n")
        title = next((v for k, v in obj.items() if k.strip().lower() == "title" and isinstance(v, str)), None)
        if title is not None:
            files_with_title += 1
            t = norm_title(title)
            if len(t) >= MIN_TITLE_CHARS:
                by_title[t].append(rel)

    def dup_report(groups):
        dups = sorted((sorted(v) for v in groups.values() if len(v) > 1), key=lambda v: v[0])
        return {"groups": len(dups), "redundant_copies": sum(len(v) - 1 for v in dups), "first_10_groups": dups[:10]}

    if tag_fh:
        tag_fh.close()
    mapping = {n: {"files": k, **map_sector_name(n)} for n, k in sorted(st_sector.items())}
    multi_shard = sorted(k for k, v in ids.items() if len(v) > 1)
    out = {
        "artifact": "literature corpus inventory", "tool_version": VERSION, "inventory_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root_basename": root.name, "files": len(files), "total_bytes": total_bytes,
        "parse_failures": len(parse_fail), "parse_failure_paths_first_20": parse_fail[:20],
        "not_object": len(not_object), "not_object_paths_first_20": not_object[:20],
        "distinct_ids": len(ids), "ids_in_more_than_one_shard": len(multi_shard), "ids_in_more_than_one_shard_first_20": multi_shard[:20],
        "content_identity_sha256": ident.hexdigest(),
        "content_identity_rule": "SHA-256 of UTF-8 lines 'rel_path<TAB>sha256<TAB>bytes<LF>' in rel_path order (the build_index.py rule)",
        "shards": {"count": len(shards), "files_per_shard": dict(sorted(shards.items())),
                   "files_per_shard_stats": quartiles(list(shards.values()))},
        "sections": {"string_sections_per_file": quartiles(n_sections), "string_sections_total": sum(n_sections),
                     "distinct_keys": len(key_df), "top_30_keys_by_doc_frequency": key_df.most_common(30),
                     "nonstring_values_by_key_top_30": nonstring_key.most_common(30)},
        "araiadoc_tags": {"key": TAGS_KEY, "value_type_per_file": dict(sorted(tag_type.items())),
                          "distinct_values": len(tag_counter), f"top_{top_tags}_values": tag_counter.most_common(top_tags),
                          "note": "values as stored (list elements; the string; key=value for an object); recorded, not interpreted"},
        "sector_tags": {"path": f"{TAGS_KEY}.{CI_KEY}.sectors[]", "origin": TAG_ORIGIN,
                        "files_with_critical_infrastructure_object": st_files_entry, "files_with_at_least_one_sector": st_files_sector,
                        "shape_problems_files": dict(sorted(st_problems.items())),
                        "distinct_sector_names": len(st_sector), "files_per_sector_name": dict(st_sector.most_common()),
                        "distinct_sector_subsector_tags": len(st_tag), f"top_{top_tags}_sector_subsector_tags": st_tag.most_common(top_tags),
                        "mapping_to_lexicon_classes": mapping,
                        "mapped_names": sorted(n for n, m in mapping.items() if m["class_id"]),
                        "unmapped_names": sorted(n for n, m in mapping.items() if not m["class_id"]),
                        "classes_with_no_sector_name": sorted({cid for cid, _ in CISA_SECTOR_CLASSES} - {m["class_id"] for m in mapping.values()}),
                        "mapping_rule": "by name: exact after normalisation (lowercase, '&' -> 'and', non-alphanumerics -> space, trailing 'sector' dropped), else a unique leading-word prefix of one CISA sector name, else unmapped",
                        "tags_out": Path(tags_out).name if tags_out else None,
                        "note": "the pipeline's labels (external model), recorded, not verified; never the paper's words"},
        "titles": {"files_with_title_key": files_with_title, "min_normalised_chars": MIN_TITLE_CHARS,
                   "normalisation": "NFKC, lowercase, [^a-z0-9] -> space, whitespace collapsed"},
        "duplicates": {"by_content_sha256": dup_report(by_sha), "by_normalised_title": dup_report(by_title)},
    }
    if compare is not None:
        both = sorted(set(ids) & compare)
        out["overlap"] = {"compare_label": compare_label, "compare_ids": len(compare), "overlap_by_paper_id": len(both),
                          "overlap_first_20": both[:20], "rule": "paper id = file basename without .json, compared as strings"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="corpus root: <root>/<shard>/<id>.json (LITCORPUS-03: the kept/ directory)")
    ap.add_argument("--out", required=True, help="output JSON path (refuses to overwrite)")
    ap.add_argument("--corpus-id", default=None)
    ap.add_argument("--top-tags", type=int, default=20)
    ap.add_argument("--compare-ids", default=None, help="build_index manifest.csv (doc_id column) or a text file of ids")
    ap.add_argument("--compare-label", default=None)
    ap.add_argument("--tags-out", default=None, help="v1.1: per-paper sector tags, JSON lines (refuses to overwrite)")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    if a.tags_out and Path(a.tags_out).exists():
        sys.exit(f"refusing to overwrite {a.tags_out}")
    t0 = time.time()
    compare = load_compare_ids(Path(a.compare_ids)) if a.compare_ids else None
    rep = inventory(Path(a.root).resolve(), a.top_tags, compare, a.compare_label or (Path(a.compare_ids).name if a.compare_ids else None),
                    a.tags_out)
    if a.tags_out:
        rep["sector_tags"]["tags_out_sha256"] = hashlib.sha256(Path(a.tags_out).read_bytes()).hexdigest()
    rep = {"corpus_id": a.corpus_id, **rep, "elapsed_seconds": round(time.time() - t0, 1), "python": sys.version.split()[0]}
    out.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("corpus_id", "files", "parse_failures", "distinct_ids", "content_identity_sha256", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()
