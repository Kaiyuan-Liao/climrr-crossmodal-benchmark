"""The group handout: verbatim where it quotes, hedged where it writes.

`docs/GROUP_MEETING_2026-09-14.md` is the only M1-WP3b document written by hand
around generated output, and that is exactly the shape of the defect the
pre-meeting review of M1-WP3 found: the generated prose was correct and the
hand-authored framing around it stated an inferred reading as fact. Two things
are therefore pinned here --- that the quoted records are quoted **exactly**, and
that no stored label value appears in a hand-written sentence as though it were
a place.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOUT_PATH = REPO_ROOT / "docs" / "GROUP_MEETING_2026-09-14.md"
PROTOTYPE_DIR = REPO_ROOT / "artifacts" / "phenomena" / "prototypes"
RECORD_IDS = ("P-CELL-1", "P-COUNTY-1", "P-STATE-1")

#: The legend every description ends with. Stated once in the handout, so the
#: quoted bodies stop here.
LEGEND_MARKER = "Every clause marked [provisional:...]"

_BACKTICKED = re.compile(r"`[^`]*`")
_PROVISIONAL = re.compile(r"\[provisional[^\]]*\]")


@pytest.fixture(scope="module")
def handout() -> str:
    return HANDOUT_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def records() -> dict:
    return {
        record_id: json.loads((PROTOTYPE_DIR / f"{record_id}.json").read_text("utf-8"))
        for record_id in RECORD_IDS
    }


def description_body(record: dict) -> str:
    """The description without its caution block and without the closing legend."""
    lines = [
        line for line in record["description"].splitlines() if not line.startswith("> ")
    ]
    return "\n".join(lines).split(LEGEND_MARKER)[0].strip()


def test_each_record_is_quoted_verbatim(handout, records):
    """A hand-edited number in a handout is a fabricated result. Quote or nothing."""
    for record_id, record in records.items():
        body = description_body(record)
        assert handout.count(body) == 1, f"{record_id} is not quoted verbatim"


def test_the_quoted_bodies_carry_every_number_the_record_holds(handout, records):
    for record in records.values():
        assert record["D"]["change_value"] in handout
        assert record["M"]["tercile"] in handout
        assert record["G"]["n_cells"] in handout


def test_the_caution_that_a_fire_weather_index_is_not_a_fire_is_stated(handout):
    assert "It is not a wildfire, an ignition, a burned area" in handout


def test_the_modeled_baseline_caution_is_stated(handout):
    assert "modeled historical baseline" in handout
    assert "It is not an observation." in handout


def test_the_magnitude_field_is_introduced_as_a_placeholder(handout):
    collapsed = " ".join(handout.split())
    assert "**That is a placeholder chosen so the field is not empty.**" in collapsed
    assert "It is not a threshold, it rests on no literature" in collapsed


def hand_authored_lines(handout: str, records: dict) -> list[tuple[int, str]]:
    """Every line outside a quoted record body, 1-indexed.

    The quoted bodies are generated text with their own labelling rules and
    their own guard; what this module polices is the prose written around them.
    """
    quoted = set()
    lines = handout.splitlines()
    for record in records.values():
        body = description_body(record).splitlines()
        for start in range(len(lines) - len(body) + 1):
            if lines[start : start + len(body)] == body:
                quoted.update(range(start, start + len(body)))
    return [
        (number, line)
        for number, line in enumerate(lines, start=1)
        if number - 1 not in quoted
    ]


def test_no_stored_label_value_is_stated_as_a_place_in_hand_written_prose(
    handout, records
):
    """`Oklahoma`, `Stephens`, `California` are strings this file stores.

    Reading them as places is `inferred_candidate`. They may appear quoted as
    code, or inside a `[provisional: ...]` span, and nowhere else.
    """
    labels = sorted(
        {
            value
            for record in records.values()
            for value in record["G"]["identifier"].values()
        }
    )
    offences = []
    for number, line in hand_authored_lines(handout, records):
        bare = _BACKTICKED.sub("", _PROVISIONAL.sub("", line))
        found = [label for label in labels if label in bare]
        if found:
            offences.append((number, found, line.strip()[:90]))
    assert offences == [], offences


def test_the_guard_would_catch_the_framing_the_wp3_review_rejected(handout, records):
    """The exact shape of defect D-012 found, fed back through this guard."""
    rejected = handout.replace(
        "### One county-shaped row set",
        "### Stephens County, Oklahoma",
    )
    with pytest.raises(AssertionError):
        test_no_stored_label_value_is_stated_as_a_place_in_hand_written_prose(
            rejected, records
        )


def test_the_record_headings_describe_a_row_set_and_not_a_place(handout):
    assert "### One grid cell" in handout
    assert "### One county-shaped row set" in handout
    assert "### One state-shaped row set" in handout


def test_every_literature_question_type_says_the_claim_is_not_available(handout):
    rows = [line for line in handout.splitlines() if line.startswith("| Pattern to")
            or line.startswith("| Claim to")
            or line.startswith("| Support /")
            or line.startswith("| Insufficient")
            or line.startswith("| Compositional")]
    assert len(rows) == 5
    for row in rows:
        assert "not yet available" in row


def test_the_table_only_row_is_marked_as_the_kind_we_are_not_building(handout):
    row = next(line for line in handout.splitlines() if line.startswith("| Table-only"))
    assert "trying not to build" in row


def test_there_are_exactly_five_questions_for_the_group(handout):
    section = handout.split("## Five questions for the group", 1)[1]
    numbered = [line for line in section.splitlines() if re.match(r"^\d+\. ", line)]
    assert [line.split(".", 1)[0] for line in numbered] == ["1", "2", "3", "4", "5"]


def test_the_handout_carries_no_internal_process_jargon(handout):
    """It goes to the group, not to the review chain."""
    for word in ("GUIDANCE", "COORDINATOR", "EXECUTOR", "work package", "commit SHA"):
        assert word not in handout, word
