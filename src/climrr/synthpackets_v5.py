"""Seed packets v5 (work package P5a; D-069 scope marking; question forms v1).

Packets v5 = packets v4b (`synthpackets_v4.build_selection(variant="v4b")`, the same seven seeds, selection v2a,
DR-DESC-1 v4, plain language v1a, dispositions and groups, unchanged) with only these fields added:

- **Scope per group (D-069).** Each `model_view.groups[i]` gains `scope_class` and `scope_phrase`. The class is the most
  specific geography class among the group's CITED members (`evidence_role` core / cited candidate, or a
  `review_synthesis` passage --- the members an item's literature statement cites as `supports`): the relevance basis the
  packet already stores per member (`basis`: state > nca_region > us_subregion > us_national > global; litgeo v2), else
  the member's own `region_class` (other / unknown); a group with no cited member is `unknown`. Classes map to the D-069
  stems: `state` -> "Research on <State>"; `nca` -> "Research on the <Region>" (the item's NCA5 region for a state item;
  for a regional contrast the regions the cited members name, of those the pattern covers); `us_subregion` /
  `us_national` -> "Research on the United States"; `global` / `other` / `unknown` -> "In general, research". The verb is
  the group's hedge (D-062): "shows" (multi-source or review; "has shown" also allowed) or "suggests" (single-source).
- **Item scope.** `model_view.scope`: the place, the classes present, `needs_general_clause` (true when no packet group is
  state- or NCA-specific: the clause is then always required; when false it is still required if the item cites no such
  group --- post-checks v3.2 decide on the cited groups), and `general_clause` = "These are general drivers of <hazard
  phrase>, not findings specific to <Place>." (hazard phrase: the plain-language `quantity_short`; Place: the state, or
  "any one region" for a regional contrast). `checks_input.scope` carries the same with each group's class and stem and
  the place names a required rubric point may not name on a group's authority.
- **Question form.** `model_view.question_form` / `checks_input.question_form`: the form assigned by
  `assign_question_forms` (`question_forms_v1.yaml`, round-robin within rung), its skeleton filled with the plain-language
  slots, its opening and the number of question marks it needs; `question_form_id` at the packet top level.

Nothing else changes: `provenance` (the groups with their members) is byte-identical to v4b's, and each model-view group
minus its two scope fields equals v4b's (`group_identity`, checked by the builder and the tests). No model call; no table
value computed.
"""

from __future__ import annotations

import copy
import json
import re

import yaml

from climrr import itemseeds as sd
from climrr import litaggregate as la
from climrr import synthpackets_v4 as v4
from climrr.checksums import sha256_file
from climrr.paths import REPO_ROOT

VERSION = "synthpackets v5"
PACKETS_V5_DIR = REPO_ROOT / "artifacts" / "benchmark" / "synth_packets_v5"
QUESTION_FORMS_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "question_forms_v1.yaml"
DECISION = "D-069"
BASIS_TO_CLASS = {"state": "state", "nca_region": "nca", "us_subregion": "us_subregion", "us_national": "us_national",
                  "global": "global"}
CLASS_ORDER = ("state", "nca", "us_subregion", "us_national", "global", "other", "unknown")
SCOPE_FIELDS = ("scope_class", "scope_phrase")
NO_ARTICLE_REGIONS = ("Alaska", "Hawai'i and U.S.-Affiliated Pacific Islands")
REGIONAL_PLACE = "any one region"


def cited(member: dict) -> bool:
    return member["evidence_role"] in la.CORE_OR_CITED or member.get("passage_type") == "review_synthesis"


def member_class(m: dict) -> str:
    if m.get("basis") in BASIS_TO_CLASS:
        return BASIS_TO_CLASS[m["basis"]]
    rc = m.get("region_class")
    return rc if rc in ("other", "unknown") else "unknown"


def region_np(name: str) -> str:
    return name if name in NO_ARTICLE_REGIONS else f"the {name}"


def join_names(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def group_scope(g: dict, pattern: dict, nca: dict, gz) -> dict:
    """{class, stem, cited_members, cited_by_class, regions} for one packet group (provenance record)."""
    cm = [m for m in g["members"] if cited(m)]
    classes = [member_class(m) for m in cm]
    best = min(classes, key=CLASS_ORDER.index) if classes else "unknown"
    places = sd.pattern_places(pattern, nca)
    regions = []
    if best == "state":
        stem = f"Research on {places['state'][0]}"
    elif best == "nca":
        if pattern["pattern_kind"] == "regional_contrast":
            for m in cm:
                if member_class(m) == "nca":
                    regions += [r for r in gz.names_in(m["region"])[1] if r in places["nca_region"] and r not in regions]
            regions = sorted(regions) or list(places["nca_region"][:1])
        else:
            regions = list(places["nca_region"])
        stem = f"Research on {join_names([region_np(r) for r in regions])}"
    elif best in ("us_subregion", "us_national"):
        stem = "Research on the United States"
    else:
        stem = "In general, research"
    return {"class": best, "stem": stem, "regions": regions, "cited_members": len(cm),
            "cited_by_class": {c: classes.count(c) for c in CLASS_ORDER if c in classes}}


def scope_phrase(stem: str, strength: str) -> str:
    return f"{stem} {'suggests' if strength == 'single_source_supported' else 'shows'}"


def load_question_forms(path=QUESTION_FORMS_PATH) -> dict:
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    ids = [f["id"] for f in d["forms"]]
    if len(ids) != 8 or len(set(ids)) != 8:
        raise ValueError("question_forms_v1 must hold eight distinct forms")
    for f in d["forms"]:
        re.compile(f["opening_regex"])
    return {**d, "sha256": sha256_file(path)}


def admits(form: dict, rung: int, pattern: dict) -> bool:
    return (rung in form["rungs"] and pattern["pattern_kind"] in form["pattern_kinds"]
            and (not form.get("directions") or pattern.get("direction") in form["directions"]))


def assign_question_forms(items: list[tuple[str, int, dict]], forms: dict) -> dict:
    """{item_id: form} --- round-robin, in the given (selection) order, within each rung, over the forms that admit the
    item (id order). `items`: [(item_id, rung, pattern record)]."""
    counter, out = {}, {}
    for iid, rung, p in items:
        ok = [f for f in forms["forms"] if admits(f, rung, p)]
        if not ok:
            raise ValueError(f"{iid}: no question form admits rung {rung}, {p['pattern_kind']}, {p.get('direction')}")
        k = counter.get(rung, 0)
        out[iid] = ok[k % len(ok)]
        counter[rung] = k + 1
    return out


def fill_skeleton(form: dict, slots: dict) -> str:
    text = form["skeleton"]
    for k, v in slots.items():
        text = text.replace("{" + k + "}", v)
    return re.sub(r"\s+", " ", text).strip()


def place_of(pattern: dict) -> str:
    return REGIONAL_PLACE if pattern["pattern_kind"] == "regional_contrast" else pattern["geography"]


def add_scope(pk: dict, form: dict, nca: dict, gz, forms_sha256: str) -> dict:
    """Packet v5 from a packet v4b (deep copy; the input is unchanged)."""
    x = copy.deepcopy(pk)
    p = x["provenance"]["patterns"][0]
    plain = x["model_view"]["plain_language"]
    prov = {g["group_id"]: g for g in x["provenance"]["groups"]}
    scopes = {gid: group_scope(g, p, nca, gz) for gid, g in prov.items()}
    for g in x["model_view"]["groups"]:
        sc = scopes[g["group_id"]]
        g["scope_class"] = sc["class"]
        g["scope_phrase"] = scope_phrase(sc["stem"], prov[g["group_id"]]["strength_in_packet"])
    place = place_of(p)
    places = sd.pattern_places(p, nca)
    classes = sorted({s["class"] for s in scopes.values()}, key=CLASS_ORDER.index)
    needs = not any(c in ("state", "nca") for c in classes)
    clause = f"These are general drivers of {plain['quantity_short']}, not findings specific to {place}."
    slots = {"quantity": plain["quantity_short"], "place": place if p["pattern_kind"] != "regional_contrast" else "U.S. regions",
             "horizon": plain["horizon"], "scenario": plain["scenario"]}
    qf = {"id": form["id"], "name": form["name"], "skeleton": fill_skeleton(form, slots), "opening_regex": form["opening_regex"],
          "min_question_marks": form["min_question_marks"]}
    x["version"] = VERSION
    x["question_form_id"] = form["id"]
    x["model_view"]["scope"] = {"decision": DECISION, "place": place, "classes_present": classes,
                                "needs_general_clause": needs, "general_clause": clause}
    x["model_view"]["question_form"] = qf
    x["checks_input"]["scope"] = {"decision": DECISION, "groups": {gid: {"class": s["class"], "stem": s["stem"]} for gid, s in scopes.items()},
                                  "general_clause": clause, "needs_general_clause": needs,
                                  "place_names": list(dict.fromkeys(places["state"] + places["nca_region"]))}
    x["checks_input"]["question_form"] = {k: qf[k] for k in ("id", "name", "opening_regex", "min_question_marks")}
    x["scope_detail"] = {gid: s for gid, s in scopes.items()}
    x["inputs_sha256"] = {**x["inputs_sha256"], "question_forms": forms_sha256}
    return x


def group_identity(v4b: dict, v5: dict) -> bool:
    """Every model-view group of v5 minus its scope fields equals v4b's, and the provenance groups are equal."""
    strip = [{k: v for k, v in g.items() if k not in SCOPE_FIELDS} for g in v5["model_view"]["groups"]]
    return strip == v4b["model_view"]["groups"] and v5["provenance"]["groups"] == v4b["provenance"]["groups"]


def build() -> dict:
    """{"v4b": [packet], "v5": [packet], "forms": forms, "assignment": {item_id: form_id}, "selection": ...} from the
    v4b build (in memory) and question_forms_v1. Raises if a group differs from v4b beyond the scope fields."""
    from climrr import litgeo as lg

    b = v4.build_selection(variant="v4b")
    forms = load_question_forms()
    nca = sd.nca_map()
    gz = lg.Gazetteer(nca)
    items = [(pk["item_id"], pk["use_case_level"], pk["provenance"]["patterns"][0]) for pk in b["packets"]]
    assign = assign_question_forms(items, forms)
    out = []
    for pk in b["packets"]:
        x = add_scope(pk, assign[pk["item_id"]], nca, gz, forms["sha256"])
        if not group_identity(pk, x):
            raise ValueError(f"{pk['packet_id']}: a group differs from v4b beyond the scope fields")
        out.append(x)
    return {"v4b": b["packets"], "v5": out, "forms": forms, "assignment": {k: f["id"] for k, f in assign.items()},
            "build": b}


def dumps(pk: dict) -> str:
    return json.dumps(pk, indent=2, ensure_ascii=False) + "\n"
