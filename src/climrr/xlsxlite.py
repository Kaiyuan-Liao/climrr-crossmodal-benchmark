"""A minimal .xlsx writer on the standard library (pilot P2a review workbook).

Writes inline-string and number cells, a bold frozen header row, an autofilter and
fixed column widths; nothing else (no formulas, styles beyond bold + wrap, or
shared strings). Deterministic: the zip entries carry a fixed timestamp, so the same
sheets give the same bytes. Used instead of adding a spreadsheet library to the
pinned environment.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

_FIXED_TIME = (2026, 1, 1, 0, 0, 0)
_ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
MAX_CELL = 32767  # Excel's per-cell character limit


def _col(i: int) -> str:
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _cell(ref: str, v, style: int) -> str:
    if v is None or v == "":
        return f'<c r="{ref}" s="{style}"/>'
    if isinstance(v, bool):
        v = "true" if v else "false"
    if isinstance(v, (int, float)):
        return f'<c r="{ref}" s="{style}"><v>{v}</v></c>'
    text = _ILLEGAL.sub("", str(v))[:MAX_CELL]
    return f'<c r="{ref}" t="inlineStr" s="{style}"><is><t xml:space="preserve">{escape(text)}</t></is></c>'


def _sheet(rows: list[list], widths: list[int] | None) -> str:
    n_cols = max((len(r) for r in rows), default=1)
    cols = "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths or []))
    body = []
    for ri, row in enumerate(rows, 1):
        style = 1 if ri == 1 else 2
        body.append(f'<row r="{ri}">' + "".join(_cell(f"{_col(ci)}{ri}", v, style) for ci, v in enumerate(row)) + "</row>")
    last = f"{_col(n_cols - 1)}{max(len(rows), 1)}"
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
            '</sheetView></sheetViews>'
            + (f"<cols>{cols}</cols>" if cols else "")
            + "<sheetData>" + "".join(body) + "</sheetData>"
            + (f'<autoFilter ref="A1:{last}"/>' if len(rows) > 1 else "")
            + "</worksheet>")


_STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
           '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
           '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
           '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
           '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
           '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
           '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
           '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')


def write_xlsx(path: Path | str, sheets: list[tuple[str, list[list], list[int] | None]]) -> None:
    """`sheets`: (name, rows with the header first, column widths or None)."""
    names = [n[:31] for n, _, _ in sheets]
    if len(set(names)) != len(names):
        raise ValueError("sheet names must be unique (31 characters)")
    files = {
        "[Content_Types].xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                                '<Default Extension="xml" ContentType="application/xml"/>'
                                '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                                '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                                + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                                          for i in range(1, len(sheets) + 1))
                                + "</Types>"),
        "_rels/.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                        "</Relationships>"),
        "xl/workbook.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                            + "".join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, n in enumerate(names, 1))
                            + "</sheets></workbook>"),
        "xl/_rels/workbook.xml.rels": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                       + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
                                                 for i in range(1, len(sheets) + 1))
                                       + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                                       "</Relationships>"),
        "xl/styles.xml": _STYLES,
    }
    for i, (_, rows, widths) in enumerate(sheets, 1):
        files[f"xl/worksheets/sheet{i}.xml"] = _sheet(rows, widths)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in files.items():
            info = zipfile.ZipInfo(name, date_time=_FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text.encode("utf-8"))
