"""Item design dispositions (D-059; work package P3a): an overlay on the pilot items' review status.

`data/metadata/benchmark/item_design_dispositions_v1.yaml` (manifest-pinned) records BI-P2B-0001 and BI-P2B-0002 as
`rejected_by_design (D-059)`: rung 1 (pattern-only) items are dropped from the benchmark. Item schema v2 has no such
`review.status` value and the item files are immutable, so `effective_status` reads the overlay over the file's status;
`check` holds every record to the item file it names (path and SHA-256).

No model call; no item file is modified.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from climrr.checksums import sha256_file
from climrr.manifest import MANIFEST_PATH, load_entry
from climrr.paths import REPO_ROOT

DISPOSITIONS_PATH = REPO_ROOT / "data" / "metadata" / "benchmark" / "item_design_dispositions_v1.yaml"
REJECTED_BY_DESIGN = "rejected_by_design (D-059)"


def load(path: Path = DISPOSITIONS_PATH, manifest_path: Path = MANIFEST_PATH) -> dict:
    path = Path(path)
    pin = load_entry(path.name, manifest_path)["sha256"]
    if sha256_file(path) != pin:
        raise ValueError(f"{path.name} differs from its manifest pin {pin}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check(doc: dict) -> list[str]:
    """Problems with the overlay against the item files it names (empty when it holds)."""
    errs = []
    for x in doc["items"]:
        f = REPO_ROOT / x["item_file"]
        if not f.is_file():
            errs.append(f"{x['item_id']}: {x['item_file']} absent")
        elif sha256_file(f) != x["item_file_sha256"]:
            errs.append(f"{x['item_id']}: {x['item_file']} differs from the SHA-256 the overlay records")
    return errs


def effective_status(item: dict, doc: dict | None = None) -> str:
    """The item's review status with the design disposition applied."""
    by_id = {x["item_id"]: x["status"] for x in (doc or load())["items"]}
    return by_id.get(item["item_id"], item["review"]["status"])
