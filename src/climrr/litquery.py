"""Deterministic parse of the literature collection query (M4-WP0, ruling §2).

The query in `data/metadata/literature_query.txt` is the Boolean search
expression the external literature corpus was collected with. It is a
provenance record, pinned by SHA-256 in `data/manifest.json`. This module turns
its bytes into a structure and does **nothing else**: no synonyms, no stemming,
no grouping by meaning, no names for the groups. The ruling's boundary is

    Deterministic lexical normalization is allowed. Scientific
    reinterpretation is not.

What the parser accepts
-----------------------

A small, closed grammar, and anything outside it raises `QueryParseError` with
the character offset of the problem rather than being guessed at:

- `(` and `)`;
- the operators `AND` and `OR`, **upper case only** --- a lower-case `and` is a
  bare term, because the query's author wrote every operator in upper case and
  a lower-case one would be a different thing;
- a quoted phrase, `"..."` (straight double quotes, or the curly pair);
- a bare term: letters, digits, `-`, `_`, `.`.

`AND` and `OR` may not be mixed at one level without parentheses: the query does
not need precedence rules, and inventing one would be a reinterpretation.
`NOT`, wildcards and field tags are not in the query and are refused.

What the parse represents
-------------------------

The source query is a top-level `AND` of two disjunctions. The first is an `OR`
of parenthesised groups, each an `OR` of terms; the second is an `OR` of terms.
`extract_structure` checks that shape exactly and fails on any other. The groups
are given **positional ids only** --- `HG-01` in source order --- and the terms
in the second disjunction `CT-01`, ... . No group is given a name: calling a
group "flood" would be a reading of its terms, which is the one thing this
module is not allowed to do. Documents may refer to a group by its id and its
first term, which is a quotation, not a label.

Per term: the exact text, whether it was quoted, the character offsets of the
whole lexeme and of its text in the source file, and a normalized form.

The normalized form
-------------------

`normalize_term`: curly quotes to straight, lower case, runs of whitespace to
one space, trimmed. **Hyphens are kept** --- `wet-bulb` stays `wet-bulb` --- and
no other character is touched. The en dash is not a hyphen and is not
converted. That is the whole rule.

Absence rules (ruling action 15)
--------------------------------

Three deterministic rules over the term list, each reported with the rule
itself and every hit. Their result is a statement **about the query's terms**
and about nothing else; in particular "no place name" is verified only against
the lists written here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PARSER_VERSION = "litquery-1"

OPEN_QUOTES = {'"': '"', "“": "”"}
_BARE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-_.]*")
_OPERATORS = {"AND", "OR"}
_REFUSED_OPERATORS = {"NOT", "NEAR", "ADJ", "W", "PRE"}
_CURLY = {"“": '"', "”": '"', "‘": "'", "’": "'"}


class QueryParseError(ValueError):
    """The query text is outside the grammar. Carries the character offset."""

    def __init__(self, message: str, offset: int):
        super().__init__(f"{message} (at character offset {offset})")
        self.offset = offset


class QueryShapeError(ValueError):
    """The query parsed, but not into the AND-of-two-disjunctions shape."""


# --- lexemes -----------------------------------------------------------------


@dataclass(frozen=True)
class Lexeme:
    kind: str  # LPAREN | RPAREN | AND | OR | TERM
    start: int  # offset of the lexeme's first character in the source
    end: int  # offset one past its last character
    text: str = ""  # TERM only: the term's text, without quotes
    quoted: bool = False
    text_start: int = 0  # TERM only: offset of `text` in the source
    text_end: int = 0


def lex(source: str) -> list[Lexeme]:
    lexemes: list[Lexeme] = []
    i, n = 0, len(source)
    while i < n:
        ch = source[i]
        if ch.isspace():
            i += 1
        elif ch == "(":
            lexemes.append(Lexeme("LPAREN", i, i + 1))
            i += 1
        elif ch == ")":
            lexemes.append(Lexeme("RPAREN", i, i + 1))
            i += 1
        elif ch in OPEN_QUOTES:
            close = source.find(OPEN_QUOTES[ch], i + 1)
            if close < 0:
                raise QueryParseError("unterminated quoted phrase", i)
            text = source[i + 1 : close]
            if text.strip() == "":
                raise QueryParseError("empty quoted phrase", i)
            lexemes.append(Lexeme("TERM", i, close + 1, text, True, i + 1, close))
            i = close + 1
        else:
            match = _BARE_RE.match(source, i)
            if match is None:
                raise QueryParseError(f"unexpected character {ch!r}", i)
            word = match.group(0)
            if word in _OPERATORS:
                lexemes.append(Lexeme(word, i, match.end()))
            elif word.upper() in _REFUSED_OPERATORS and word.isupper():
                raise QueryParseError(f"operator {word!r} is not supported", i)
            else:
                lexemes.append(Lexeme("TERM", i, match.end(), word, False, i, match.end()))
            i = match.end()
    return lexemes


# --- tree -------------------------------------------------------------------


@dataclass
class Term:
    lexeme: Lexeme


@dataclass
class Group:
    op: str | None  # AND | OR | None (a single operand in parentheses)
    children: list
    start: int  # offset of "(" --- or of the first child for the top level
    end: int


class _Parser:
    def __init__(self, lexemes: list[Lexeme], source_len: int):
        self.lexemes = lexemes
        self.pos = 0
        self.source_len = source_len

    def peek(self) -> Lexeme | None:
        return self.lexemes[self.pos] if self.pos < len(self.lexemes) else None

    def _offset(self) -> int:
        tok = self.peek()
        return tok.start if tok is not None else self.source_len

    def expression(self, start: int) -> Group:
        children = [self.operand()]
        op: str | None = None
        while (tok := self.peek()) is not None and tok.kind in _OPERATORS:
            if op is not None and tok.kind != op:
                raise QueryParseError(
                    f"{op} and {tok.kind} mixed at one level without parentheses", tok.start
                )
            op = tok.kind
            self.pos += 1
            children.append(self.operand())
        end = self.lexemes[self.pos - 1].end
        return Group(op, children, start, end)

    def operand(self):
        tok = self.peek()
        if tok is None:
            raise QueryParseError("expected a term or '(' but the query ended", self.source_len)
        if tok.kind == "TERM":
            self.pos += 1
            return Term(tok)
        if tok.kind == "LPAREN":
            self.pos += 1
            inner = self.expression(tok.start)
            close = self.peek()
            if close is None or close.kind != "RPAREN":
                raise QueryParseError("expected ')'", self._offset())
            self.pos += 1
            inner.start, inner.end = tok.start, close.end
            return inner
        raise QueryParseError(f"expected a term or '(' but found {tok.kind}", tok.start)


def parse(source: str) -> Group:
    """Parse the whole query into a tree. Raises QueryParseError on anything else."""
    lexemes = lex(source)
    if not lexemes:
        raise QueryParseError("the query is empty", 0)
    parser = _Parser(lexemes, len(source))
    tree = parser.expression(lexemes[0].start)
    if parser.peek() is not None:
        raise QueryParseError("unexpected text after the complete expression", parser._offset())
    return tree


# --- normalization and rendering --------------------------------------------


def normalize_term(text: str) -> str:
    """Curly quotes to straight, lower case, single spaces, trimmed. Hyphens kept."""
    for curly, straight in _CURLY.items():
        text = text.replace(curly, straight)
    return re.sub(r"\s+", " ", text.lower()).strip()


def render(node, indent: int = 0) -> str:
    """Re-render a tree as query text: one term or bracket per line."""
    pad = "  " * indent
    if isinstance(node, Term):
        tok = node.lexeme
        return pad + (f'"{tok.text}"' if tok.quoted else tok.text)
    lines = [pad + "("]
    for k, child in enumerate(node.children):
        if k:
            lines.append(pad + "  " + node.op)
        lines.append(render(child, indent + 1))
    lines.append(pad + ")")
    return "\n".join(lines)


def strip_unquoted_whitespace(text: str) -> str:
    """Remove whitespace outside quoted phrases; keep it exactly inside them.

    This is what "equal modulo whitespace" means for the round-trip test.
    Removing *all* whitespace would equate `"heat wave"` with `heatwave`,
    which are two different terms in the query.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in OPEN_QUOTES:
            close = text.find(OPEN_QUOTES[ch], i + 1)
            close = n - 1 if close < 0 else close
            out.append(text[i : close + 1])
            i = close + 1
        else:
            if not ch.isspace():
                out.append(ch)
            i += 1
    return "".join(out)


def round_trips(source: str) -> bool:
    """True when re-rendering the parse reproduces `source` modulo whitespace.

    The top level of the source is unparenthesised, so the rendering's
    outermost bracket pair is removed before comparing.
    """
    rendered = strip_unquoted_whitespace(render(parse(source)))
    assert rendered.startswith("(") and rendered.endswith(")")
    return rendered[1:-1] == strip_unquoted_whitespace(source)


# --- structure --------------------------------------------------------------


def _term_record(term_id: str, position: int, tok: Lexeme, source: str) -> dict:
    assert source[tok.text_start : tok.text_end] == tok.text
    return {
        "term_id": term_id,
        "position": position,
        "text": tok.text,
        "quoted": tok.quoted,
        "lexeme_offsets": [tok.start, tok.end],
        "text_offsets": [tok.text_start, tok.text_end],
        "normalized": normalize_term(tok.text),
    }


def _terms_of(group, where: str) -> list[Lexeme]:
    if isinstance(group, Term):
        return [group.lexeme]
    if group.op not in ("OR", None):
        raise QueryShapeError(f"{where}: expected a disjunction of terms, found {group.op}")
    lexemes = []
    for child in group.children:
        if not isinstance(child, Term):
            raise QueryShapeError(f"{where}: expected only terms, found a nested group")
        lexemes.append(child.lexeme)
    return lexemes


def extract_structure(source: str) -> dict:
    """The query as `AND(OR(group, group, ...), OR(term, term, ...))`, or raise."""
    tree = parse(source)
    if tree.op != "AND" or len(tree.children) != 2:
        raise QueryShapeError(
            f"top level: expected AND of exactly two operands, found "
            f"{tree.op} of {len(tree.children)}"
        )
    first, second = tree.children
    if isinstance(first, Term) or first.op != "OR":
        raise QueryShapeError("first AND operand: expected a disjunction of groups")

    groups = []
    for g, group in enumerate(first.children, start=1):
        if isinstance(group, Term):
            raise QueryShapeError(f"first AND operand, item {g}: a bare term, not a group")
        group_id = f"HG-{g:02d}"
        lexemes = _terms_of(group, group_id)
        groups.append(
            {
                "group_id": group_id,
                "position": g,
                "group_offsets": [group.start, group.end],
                "n_terms": len(lexemes),
                "terms": [
                    _term_record(f"{group_id}.T{t:02d}", t, tok, source)
                    for t, tok in enumerate(lexemes, start=1)
                ],
            }
        )

    if isinstance(second, Term):
        raise QueryShapeError("second AND operand: expected a parenthesised disjunction")
    context_tokens = _terms_of(second, "second AND operand")
    context = [
        _term_record(f"CT-{t:02d}", t, tok, source)
        for t, tok in enumerate(context_tokens, start=1)
    ]
    return {
        "boolean_structure": "AND( OR(hazard groups HG-01..HG-{:02d}), OR(context terms CT-01..CT-{:02d}) )".format(
            len(groups), len(context)
        ),
        "top_level": {
            "op": "AND",
            "operands": [
                {"role": "first disjunction", "op": "OR", "of": "groups",
                 "offsets": [first.start, first.end], "n_groups": len(groups)},
                {"role": "second disjunction", "op": "OR", "of": "terms",
                 "offsets": [second.start, second.end], "n_terms": len(context)},
            ],
        },
        "hazard_groups": groups,
        "context_terms": context,
    }


def all_terms(structure: dict) -> list[dict]:
    """Every term record, hazard groups first in source order, then context terms."""
    terms = [t for g in structure["hazard_groups"] for t in g["terms"]]
    return terms + list(structure["context_terms"])


# --- absence rules (ruling action 15) ---------------------------------------

SCENARIO_HORIZON_PATTERN = r"rcp|ssp|\d{4}|century|mid-|end-|projection|scenario|baseline|historical"

#: The 50 states and the District of Columbia, and their USPS codes.
US_STATE_NAMES = (
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine",
    "maryland", "massachusetts", "michigan", "minnesota", "mississippi",
    "missouri", "montana", "nebraska", "nevada", "new hampshire", "new jersey",
    "new mexico", "new york", "north carolina", "north dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina",
    "south dakota", "tennessee", "texas", "utah", "vermont", "virginia",
    "washington", "west virginia", "wisconsin", "wyoming", "district of columbia",
)
US_POSTAL_CODES = (
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
)
GEO_UNIT_WORDS = ("county", "tract", "united states", "usa")


def _word_hits(normalized: str, phrases) -> list[str]:
    return [p for p in phrases if re.search(r"(?<![a-z0-9])" + re.escape(p) + r"(?![a-z0-9])", normalized)]


def _token_hits(normalized: str, codes) -> list[str]:
    lexemes = set(re.findall(r"[a-z0-9]+", normalized))
    return [c for c in codes if c in lexemes]


ABSENCE_RULES = (
    {
        "rule_id": "AR-1-scenario-horizon",
        "dimension": "scenario / temporal horizon",
        "rule": f"no term's normalized form matches the regular expression /{SCENARIO_HORIZON_PATTERN}/ (re.search, anywhere in the term)",
    },
    {
        "rule_id": "AR-2-us-state",
        "dimension": "geography: US state",
        "rule": (
            "no term's normalized form contains, as a whole word, any of the 50 US state "
            "names or 'district of columbia', and no alphanumeric word of it equals any "
            "of their 51 two-letter USPS codes (compared in lower case)"
        ),
    },
    {
        "rule_id": "AR-3-geographic-unit",
        "dimension": "geography: sub-national unit or country",
        "rule": "no term's normalized form contains, as a whole word, any of: " + ", ".join(repr(w) for w in GEO_UNIT_WORDS),
    },
)


def absence_checks(structure: dict) -> list[dict]:
    """Apply the three absence rules to every term. Each result lists every hit."""
    terms = all_terms(structure)
    finders = {
        "AR-1-scenario-horizon": lambda s: re.findall(SCENARIO_HORIZON_PATTERN, s),
        "AR-2-us-state": lambda s: _word_hits(s, US_STATE_NAMES) + _token_hits(s, US_POSTAL_CODES),
        "AR-3-geographic-unit": lambda s: _word_hits(s, GEO_UNIT_WORDS),
    }
    results = []
    for rule in ABSENCE_RULES:
        find = finders[rule["rule_id"]]
        hits = [
            {"term_id": t["term_id"], "text": t["text"], "matched": find(t["normalized"])}
            for t in terms
            if find(t["normalized"])
        ]
        results.append(
            {
                **rule,
                "n_terms_checked": len(terms),
                "n_hits": len(hits),
                "hits": hits,
                "result": "absent" if not hits else "present",
            }
        )
    return results
