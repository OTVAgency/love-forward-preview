#!/usr/bin/env python3
"""Build print-ready PDFs for Love Forward Foundation Option A business cards."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREVIEWS = OUT / "previews"
ASSETS = ROOT / "assets"

TRIM_W_IN = 3.5
TRIM_H_IN = 2.0
BLEED_IN = 0.125
DPI = 300
MARK_MARGIN_IN = 0.25
MARK_LEN_IN = 0.125
MARK_GAP_IN = 0.02

TRIM_W_PX = round(TRIM_W_IN * DPI)   # 1050
TRIM_H_PX = round(TRIM_H_IN * DPI)   # 600
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


def extend_bleed_edges(src: Image.Image) -> Image.Image:
    """Extend trim artwork into bleed by replicating edge pixels (no bar thickening)."""
    src = src.convert("RGB")
    assert src.size == (TRIM_W_PX, TRIM_H_PX), src.size

    out = Image.new("RGB", (FULL_W_PX, FULL_H_PX))
    out.paste(src, (BLEED_L, BLEED_T))

    # Left bleed
    for x in range(BLEED_L):
        for y in range(TRIM_H_PX):
            out.putpixel((x, BLEED_T + y), src.getpixel((0, y)))

    # Right bleed
    for x in range(FULL_W_PX - BLEED_R, FULL_W_PX):
        for y in range(TRIM_H_PX):
            out.putpixel((x, BLEED_T + y), src.getpixel((TRIM_W_PX - 1, y)))

    # Top bleed
    for y in range(BLEED_T):
        for x in range(TRIM_W_PX):
            out.putpixel((BLEED_L + x, y), src.getpixel((x, 0)))

    # Bottom bleed
    for y in range(FULL_H_PX - BLEED_B, FULL_H_PX):
        for x in range(TRIM_W_PX):
            out.putpixel((BLEED_L + x, y), src.getpixel((x, TRIM_H_PX - 1)))

    # Corners (bleed strips that row/column passes missed)
    for y in range(BLEED_T):
        for x in range(BLEED_L):
            out.putpixel((x, y), src.getpixel((0, 0)))
        for x in range(FULL_W_PX - BLEED_R, FULL_W_PX):
            out.putpixel((x, y), src.getpixel((TRIM_W_PX - 1, 0)))

    for y in range(FULL_H_PX - BLEED_B, FULL_H_PX):
        for x in range(BLEED_L):
            out.putpixel((x, y), src.getpixel((0, TRIM_H_PX - 1)))
        for x in range(FULL_W_PX - BLEED_R, FULL_W_PX):
            out.putpixel((x, y), src.getpixel((TRIM_W_PX - 1, TRIM_H_PX - 1)))

    return out


def save_png(im: Image.Image, path: Path) -> None:
    im.save(path, "PNG", dpi=(DPI, DPI))


def build_trim_pdf(images: list[tuple[str, Image.Image]], path: Path) -> None:
    page_w = TRIM_W_IN * inch
    page_h = TRIM_H_IN * inch
    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))

    for _label, im in images:
        tmp = OUT / "_tmp_trim_page.png"
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


def draw_crop_marks(
    c: canvas.Canvas,
    trim_x: float,
    trim_y: float,
    trim_w: float,
    trim_h: float,
) -> None:
    """Draw trim/crop marks in the margin outside the bleed box."""
    gap = MARK_GAP_IN * inch
    mark = MARK_LEN_IN * inch
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)

    # Bottom-left
    c.line(trim_x - mark, trim_y, trim_x - gap, trim_y)
    c.line(trim_x, trim_y - mark, trim_x, trim_y - gap)
    # Bottom-right
    c.line(trim_x + trim_w + gap, trim_y, trim_x + trim_w + mark, trim_y)
    c.line(trim_x + trim_w, trim_y - mark, trim_x + trim_w, trim_y - gap)
    # Top-left
    top = trim_y + trim_h
    c.line(trim_x - mark, top, trim_x - gap, top)
    c.line(trim_x, top + gap, trim_x, top + mark)
    # Top-right
    c.line(trim_x + trim_w + gap, top, trim_x + trim_w + mark, top)
    c.line(trim_x + trim_w, top + gap, trim_x + trim_w, top + mark)


def build_bleed_pdf(images: list[tuple[str, Image.Image]], path: Path) -> None:
    margin = MARK_MARGIN_IN * inch
    page_w = FULL_W_IN * inch + 2 * margin
    page_h = FULL_H_IN * inch + 2 * margin
    art_x = margin
    art_y = margin
    trim_x = art_x + BLEED_IN * inch
    trim_y = art_y + BLEED_IN * inch
    trim_w = TRIM_W_IN * inch
    trim_h = TRIM_H_IN * inch

    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))

    for _label, im in images:
        tmp = OUT / "_tmp_bleed_page.png"
        save_png(im, tmp)
        c.drawImage(
            ImageReader(str(tmp)),
            art_x,
            art_y,
            width=FULL_W_IN * inch,
            height=FULL_H_IN * inch,
            preserveAspectRatio=False,
            mask=None,
        )
        draw_crop_marks(c, trim_x, trim_y, trim_w, trim_h)
        c.showPage()
        tmp.unlink(missing_ok=True)

    c.save()


def save_bleed_preview_with_marks(bleed_im: Image.Image) -> Image.Image:
    """Raster preview of bleed PDF page (art + crop marks in margin)."""
    margin_px = round(MARK_MARGIN_IN * DPI)
    page_w = FULL_W_PX + 2 * margin_px
    page_h = FULL_H_PX + 2 * margin_px
    page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
    page.paste(bleed_im, (margin_px, margin_px))

    from PIL import ImageDraw

    draw = ImageDraw.Draw(page)
    trim_l = margin_px + BLEED_L
    trim_t = margin_px + BLEED_T
    trim_r = trim_l + TRIM_W_PX
    trim_b = trim_t + TRIM_H_PX
    gap = round(MARK_GAP_IN * DPI)
    mark = round(MARK_LEN_IN * DPI)
    black = (0, 0, 0)

    # Bottom-left
    draw.line([(trim_l - mark, trim_b), (trim_l - gap, trim_b)], fill=black, width=2)
    draw.line([(trim_l, trim_b + gap), (trim_l, trim_b + mark)], fill=black, width=2)
    # Bottom-right
    draw.line([(trim_r + gap, trim_b), (trim_r + mark, trim_b)], fill=black, width=2)
    draw.line([(trim_r, trim_b + gap), (trim_r, trim_b + mark)], fill=black, width=2)
    # Top-left
    draw.line([(trim_l - mark, trim_t), (trim_l - gap, trim_t)], fill=black, width=2)
    draw.line([(trim_l, trim_t - mark), (trim_l, trim_t - gap)], fill=black, width=2)
    # Top-right
    draw.line([(trim_r + gap, trim_t), (trim_r + mark, trim_t)], fill=black, width=2)
    draw.line([(trim_r, trim_t - mark), (trim_r, trim_t - gap)], fill=black, width=2)

    return page


def save_page_previews(
    trim_images: list[tuple[str, Image.Image]],
    bleed_images: list[tuple[str, Image.Image]],
) -> list[Path]:
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for i, (label, im) in enumerate(trim_images, start=1):
        path = PREVIEWS / f"trim-page-{i}-{label}.png"
        save_png(im, path)
        paths.append(path)

    for i, (label, im) in enumerate(bleed_images, start=1):
        path = PREVIEWS / f"bleed-page-{i}-{label}.png"
        save_png(save_bleed_preview_with_marks(im), path)
        paths.append(path)

    return paths


def images_match(a: Image.Image, b: Image.Image) -> bool:
    a_rgb = a.convert("RGB")
    b_rgb = b.convert("RGB")
    return a_rgb.tobytes() == b_rgb.tobytes()


def verify_trim_region(bleed_im: Image.Image, trim_im: Image.Image) -> bool:
    crop = bleed_im.crop((BLEED_L, BLEED_T, BLEED_L + TRIM_W_PX, BLEED_T + TRIM_H_PX))
    return images_match(crop, trim_im)


def measure_bar_rows(im: Image.Image, brand_red: tuple[int, int, int] = (232, 38, 36)) -> tuple[int, int]:
    w, h = im.size
    top = 0
    for y in range(h):
        if all(im.getpixel((x, y)) == brand_red for x in range(w)):
            top += 1
        else:
            break
    bottom = 0
    for y in range(h - 1, -1, -1):
        if all(im.getpixel((x, y)) == brand_red for x in range(w)):
            bottom += 1
        else:
            break
    return top, bottom


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    trim_images: list[tuple[str, Image.Image]] = []
    bleed_images: list[tuple[str, Image.Image]] = []

    for label, src_path in SIDES:
        src = Image.open(src_path).convert("RGB")
        assert src.size == (TRIM_W_PX, TRIM_H_PX), f"{label} expected 1050x600, got {src.size}"
        trim_images.append((label, src.copy()))
        bleed = extend_bleed_edges(src)
        bleed_images.append((label, bleed))

        save_png(src, OUT / f"option-a-{label}-trim-300dpi.png")
        save_png(bleed, OUT / f"option-a-{label}-bleed-300dpi.png")

    build_trim_pdf(trim_images, OUT / "love-forward-option-a-print.pdf")
    build_bleed_pdf(bleed_images, OUT / "love-forward-option-a-print-bleed.pdf")

    preview_paths = save_page_previews(trim_images, bleed_images)

    # Visual verification against source assets
    ok = True
    for label, trim_im in trim_images:
        asset = Image.open(ASSETS / f"option-a-{label}.png").convert("RGB")
        if not images_match(trim_im, asset):
            print(f"FAIL: trim {label} does not match assets/option-a-{label}.png")
            ok = False
        bleed_im = next(im for l, im in bleed_images if l == label)
        if not verify_trim_region(bleed_im, trim_im):
            print(f"FAIL: bleed trim region for {label} does not match trim art")
            ok = False

    back_trim = next(im for l, im in trim_images if l == "back")
    top, bottom = measure_bar_rows(back_trim)
    print(f"Back bar rows (trim): top={top}, bottom={bottom}")
    if top != 11 or bottom != 10:
        print("WARN: back bar row counts differ from original main art (expected top=11, bottom=10)")

    back_bleed = next(im for l, im in bleed_images if l == "back")
    bleed_top, bleed_bottom = measure_bar_rows(back_bleed)
    print(f"Back bar rows (full bleed canvas): top={bleed_top}, bottom={bleed_bottom}")
    # Trim region inside bleed should still be 11/10
    trim_crop = back_bleed.crop((BLEED_L, BLEED_T, BLEED_L + TRIM_W_PX, BLEED_T + TRIM_H_PX))
    t2, b2 = measure_bar_rows(trim_crop)
    print(f"Back bar rows (trim crop inside bleed): top={t2}, bottom={b2}")

    print("Verification:", "PASS" if ok else "FAIL")
    print("Preview PNGs:")
    for p in preview_paths:
        print(" ", p.relative_to(ROOT))

    print("Source trim px:", TRIM_W_PX, "x", TRIM_H_PX)
    print("Bleed full px:", FULL_W_PX, "x", FULL_H_PX)


if __name__ == "__main__":
    main()
