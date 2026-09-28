#!/usr/bin/env python3
"""Build print-ready PDFs for Love Forward Foundation Option A business cards."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

TRIM_W_IN = 3.5
TRIM_H_IN = 2.0
BLEED_IN = 0.125
DPI = 300

BRAND_RED = (232, 38, 36)  # #E82624

TRIM_W_PX = round(TRIM_W_IN * DPI)   # 1050
TRIM_H_PX = round(TRIM_H_IN * DPI)   # 600
# 0.125" @ 300 DPI = 37.5 px; split 38 + 37 for exact 1125×675 full artboard.
BLEED_L = 38
BLEED_R = 37
BLEED_T = 38
BLEED_B = 37
FULL_W_PX = TRIM_W_PX + BLEED_L + BLEED_R   # 1125
FULL_H_PX = TRIM_H_PX + BLEED_T + BLEED_B   # 675

FULL_W_IN = TRIM_W_IN + 2 * BLEED_IN  # 3.75
FULL_H_IN = TRIM_H_IN + 2 * BLEED_IN  # 2.25

SIDES = [
    ("front", ASSETS / "option-a-front.png"),
    ("back", ASSETS / "option-a-back.png"),
]


def add_bleed_contact_front(src: Image.Image) -> Image.Image:
    """Contact side: extend left red bar and corner rules into bleed."""
    src = src.convert("RGB")
    assert src.size == (TRIM_W_PX, TRIM_H_PX), src.size

    out = Image.new("RGB", (FULL_W_PX, FULL_H_PX), (255, 255, 255))
    out.paste(src, (BLEED_L, BLEED_T))

    # Full-height left bar into bleed.
    for x in range(BLEED_L):
        for y in range(FULL_H_PX):
            out.putpixel((x, y), BRAND_RED)

    # Top/bottom corner rules (red only where trim edge is red).
    for y in range(BLEED_T):
        for x in range(FULL_W_PX):
            trim_x = x - BLEED_L
            if 0 <= trim_x < TRIM_W_PX and src.getpixel((trim_x, 0)) == BRAND_RED:
                out.putpixel((x, y), BRAND_RED)

    for y in range(FULL_H_PX - BLEED_B, FULL_H_PX):
        for x in range(FULL_W_PX):
            trim_x = x - BLEED_L
            if 0 <= trim_x < TRIM_W_PX and src.getpixel((trim_x, TRIM_H_PX - 1)) == BRAND_RED:
                out.putpixel((x, y), BRAND_RED)

    return out


def add_bleed_logo_back(src: Image.Image) -> Image.Image:
    """Logo side: extend top/bottom red rules into bleed."""
    src = src.convert("RGB")
    assert src.size == (TRIM_W_PX, TRIM_H_PX), src.size

    out = Image.new("RGB", (FULL_W_PX, FULL_H_PX), (255, 255, 255))
    out.paste(src, (BLEED_L, BLEED_T))

    for y in range(BLEED_T):
        for x in range(FULL_W_PX):
            out.putpixel((x, y), BRAND_RED)

    for y in range(FULL_H_PX - BLEED_B, FULL_H_PX):
        for x in range(FULL_W_PX):
            out.putpixel((x, y), BRAND_RED)

    return out


BLEED_FN = {
    "front": add_bleed_contact_front,
    "back": add_bleed_logo_back,
}


def save_png(im: Image.Image, path: Path) -> None:
    im.save(path, "PNG", dpi=(DPI, DPI))


def build_pdf(images: list[tuple[str, Image.Image]], path: Path) -> None:
    page_w = FULL_W_IN * inch
    page_h = FULL_H_IN * inch
    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))

    for _label, im in images:
        tmp = OUT / "_tmp_page.png"
        save_png(im, tmp)
        c.drawImage(
            ImageReader(str(tmp)),
            0,
            0,
            width=page_w,
            height=page_h,
            preserveAspectRatio=False,
            mask=None,
        )
        c.showPage()
        tmp.unlink(missing_ok=True)

    c.save()


def effective_dpi(im: Image.Image, width_in: float, height_in: float) -> tuple[float, float]:
    w, h = im.size
    return w / width_in, h / height_in


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bleed_images: list[tuple[str, Image.Image]] = []
    trim_images: list[tuple[str, Image.Image]] = []

    for label, src_path in SIDES:
        src = Image.open(src_path)
        trim_images.append((label, src.copy()))
        bleed = BLEED_FN[label](src)
        bleed_images.append((label, bleed))

        save_png(src, OUT / f"option-a-{label}-trim-300dpi.png")
        save_png(bleed, OUT / f"option-a-{label}-bleed-300dpi.png")

    build_pdf(bleed_images, OUT / "love-forward-option-a-print.pdf")

    for label, im in bleed_images:
        build_pdf([(label, im)], OUT / f"option-a-{label}.pdf")

    print("Source trim px:", TRIM_W_PX, "x", TRIM_H_PX)
    print("Bleed full px:", FULL_W_PX, "x", FULL_H_PX)
    for label, im in trim_images:
        dx, dy = effective_dpi(im, TRIM_W_IN, TRIM_H_IN)
        print(f"{label} trim effective DPI: {dx:.2f} x {dy:.2f}")
    for label, im in bleed_images:
        dx, dy = effective_dpi(im, FULL_W_IN, FULL_H_IN)
        print(f"{label} bleed effective DPI: {dx:.2f} x {dy:.2f}")


if __name__ == "__main__":
    main()
