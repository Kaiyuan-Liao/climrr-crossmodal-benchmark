#!/usr/bin/env python3
"""M1-WP2 Phase B: rasterise dictionary PDF pages so a text-empty page can be seen.

The GUIDANCE M1-WP1 review (risk 4, required action 5) asks the project to
confirm, before the M1 milestone gate, that the one page of the 19-page metadata
PDF which yielded **no extracted text** carries no metadata relevant to the
275-column inventory. `pypdf` can only report that the page has no text; it
cannot say whether the page has a scanned table, a figure, or nothing at all.
This script renders the page to a PNG so a human --- or the EXECUTOR reading the
image --- can look.

Pages 2 and 4 are rendered alongside page 3 for context: page 2 is the table of
contents and page 4 opens the Metadata narrative, so together they establish
what page 3 sits between.

This script assigns no meaning. It renders pixels from the manifest-verified
PDF and records what it rendered.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import struct
import sys
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import pypdfium2  # noqa: E402

from climrr.checksums import sha256_file  # noqa: E402
from climrr.manifest import ManifestMismatchError, verify_file  # noqa: E402
from climrr.paths import repo_relative  # noqa: E402
from climrr.runrecord import write_run_record  # noqa: E402

PDF_PATH = REPO_ROOT / "data" / "metadata" / "ClimRR_Metadata_and_Data_Dictionary.pdf"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"
OUT_DIR = REPO_ROOT / "artifacts" / "profiles"

#: 1-based page numbers to render. Page 3 is the text-empty page; 2 and 4 are
#: its neighbours, rendered so the finding can be read in context.
DEFAULT_PAGES = (2, 3, 4)

#: 200 dpi is enough to read a small-print table cell and still leaves each PNG
#: well under a megabyte, so the images stay committable evidence.
DEFAULT_DPI = 200

#: pdfium's own unit is 72 dpi.
PDF_POINTS_PER_INCH = 72

#: `pypdfium2` exposes no module-level ``__version__``; the installed
#: distribution version is what requirements.txt pins.
RENDERER_VERSION = importlib.metadata.version("pypdfium2")

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png(rgb, out_path: Path) -> None:
    """Write an (h, w, 3) uint8 array as a PNG using only the standard library.

    Pillow would do this in one call, but it would also be a sixth entry in the
    D-007 pin set that both hosts then have to carry for the sake of one
    screenshot. PNG's non-interlaced, 8-bit truecolour form is a filter byte per
    row in front of the raw scanlines, deflated --- small enough to write here
    and to check by eye against the spec.
    """
    height, width, channels = rgb.shape
    if channels != 3 or rgb.dtype.name != "uint8":
        raise ValueError(f"expected (h, w, 3) uint8, got {rgb.shape} {rgb.dtype}")
    raw = b"".join(b"\x00" + rgb[row].tobytes() for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(
        PNG_MAGIC
        + _png_chunk(b"IHDR", header)
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )


def render_page(pdf: pypdfium2.PdfDocument, number: int, dpi: int, out_path: Path) -> dict:
    """Render one 1-based page to PNG and return what was rendered."""
    page = pdf[number - 1]
    # rev_byteorder gives RGB rather than pdfium's native BGR, which is the
    # channel order PNG stores.
    rgb = page.render(scale=dpi / PDF_POINTS_PER_INCH, rev_byteorder=True).to_numpy()
    write_png(rgb, out_path)
    return {
        "page": number,
        "output_path": repo_relative(out_path),
        "pixels": f"{rgb.shape[1]}x{rgb.shape[0]}",
        "bytes": out_path.stat().st_size,
        "sha256": sha256_file(out_path),
        # A page whose channel minimum equals its maximum is one uniform colour
        # and therefore carries no marks at all. This is a statement about
        # pixels, not about what the page means.
        "uniform_colour": bool(rgb.min() == rgb.max()),
        "channel_extrema": [int(rgb.min()), int(rgb.max())],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=PDF_PATH)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    parser.add_argument("--pages", type=int, nargs="+", default=list(DEFAULT_PAGES))
    args = parser.parse_args()

    try:
        verified = verify_file(args.pdf, args.manifest)
    except (ManifestMismatchError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"Manifest check OK: {args.pdf.name} sha256={verified['sha256']}")

    pdf = pypdfium2.PdfDocument(str(args.pdf))
    n_pages = len(pdf)
    out_of_range = [number for number in args.pages if not 1 <= number <= n_pages]
    if out_of_range:
        print(f"FAIL: pages {out_of_range} are outside the {n_pages}-page document", file=sys.stderr)
        return 2

    rendered = []
    for number in args.pages:
        out_path = args.out_dir / f"dictionary_page{number:02d}.png"
        info = render_page(pdf, number, args.dpi, out_path)
        rendered.append(info)
        print(
            f"  page {number:>2}: {info['pixels']} px, {info['bytes']} bytes, "
            f"uniform_colour={info['uniform_colour']} -> {info['output_path']}"
        )

    passed = len(rendered) == len(args.pages)
    record_path = write_run_record(
        "rasterize_dictionary_pages",
        result_summary={
            "pdf_sha256": verified["sha256"],
            "pdf_pages": n_pages,
            "pypdfium2_version": RENDERER_VERSION,
            "dpi": args.dpi,
            "pages_rendered": args.pages,
            "rendered": rendered,
        },
        passed=passed,
        data_path=args.pdf,
        data_sha256=verified["sha256"],
        output_path=args.out_dir,
        config_snapshot={
            "pdf_path": repo_relative(args.pdf),
            "out_dir": repo_relative(args.out_dir),
            "dpi": args.dpi,
            "pages": args.pages,
            "renderer": f"pypdfium2 {RENDERER_VERSION}",
        },
    )
    print(f"Run record: {repo_relative(record_path)}")
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
