#!/usr/bin/env python3
"""Build print-ready PDFs for Love Forward Foundation Option A business cards."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PREVIEWS = OUT / "previews"
ASSETS = ROOT / "assets"

TRIM_W_IN = 3.5
TRIM_H_IN = 2.0
SAFE_INSET_IN = 0.25
BLEED_IN = 0.125
DPI = 300

BRAND_RED = np.array([232, 38, 36])
WHITE = np.array([255, 255, 255])

TRIM_W_PX = round(TRIM_W_IN * DPI)   # 1050
TRIM_H_PX = round(TRIM_H_IN * DPI)   # 600
SAFE_PX = round(SAFE_INSET_IN * DPI)  # 75
SAFE_W_PX = round((TRIM_W_IN - 2 * SAFE_INSET_IN) * DPI)   # 975
SAFE_H_PX = round((TRIM_H_IN - 2 * SAFE_INSET_IN) * DPI)   # 525

BLEED_L = 38
BLEED_R = 37
BLEED_T = 38
BLEED_B = 37
FULL_W_PX = TRIM_W_PX + BLEED_L + BLEED_R   # 1125
FULL_H_PX = TRIM_H_PX + BLEED_T + BLEED_B   # 675

FULL_W_IN = TRIM_W_IN + 2 * BLEED_IN  # 3.75
FULL_H_IN = TRIM_H_IN + 2 * BLEED_IN  # 2.25
BLEED_PT = BLEED_IN * 72  # 9 pt
PAGE_W_PT = FULL_W_IN * 72  # 270
PAGE_H_PT = FULL_H_IN * 72  # 162

SIDES = [
    ("front", ASSETS / "option-a-front.png"),
    ("back", ASSETS / "option-a-back.png"),
]

TEXT_SHIFT_X = 15
QR_SHIFT_X = -2


def is_red(px: np.ndarray) -> bool:
    return bool(np.all(np.abs(px - BRAND_RED) < 3))


def fix_front_layout(src: Image.Image) -> Image.Image:
    """Shift contact block right and QR slightly left; keep left red rail to trim edge."""
    src = src.convert("RGB")
    arr = np.array(src)
    h, w = arr.shape[:2]
    out = np.full((h, w, 3), 255, dtype=np.uint8)

    rail = np.zeros((h, w), dtype=bool)
    for x in range(33):
        rail[:, x] = np.all(np.abs(arr[:, x] - BRAND_RED) < 3, axis=1)
    for y in range(12):
        for x in range(40):
            if is_red(arr[y, x]):
                rail[y, x] = True
    for y in range(h - 12, h):
        for x in range(40):
            if is_red(arr[y, x]):
                rail[y, x] = True

    qr = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(740, w):
            if tuple(arr[y, x]) != (255, 255, 255) and not rail[y, x]:
                qr[y, x] = True

    text = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(w):
            if tuple(arr[y, x]) == (255, 255, 255) or rail[y, x] or qr[y, x]:
                continue
            text[y, x] = True

    out[rail] = arr[rail]
    out_img = Image.fromarray(out)
    src_px = src.load()

    def paste_mask(mask: np.ndarray, dx: int, dy: int = 0) -> None:
        ys, xs = np.where(mask)
        if len(xs) == 0:
            return
        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        layer_px = layer.load()
        for y, x in zip(ys, xs):
            layer_px[x, y] = src_px[x, y] + (255,)
        crop = layer.crop((x0, y0, x1 + 1, y1 + 1))
        placed = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        placed.paste(crop, (x0 + dx, y0 + dy))
        out_img.paste(placed, (0, 0), placed)

    paste_mask(text, TEXT_SHIFT_X)
    paste_mask(qr, QR_SHIFT_X)
    return out_img


def extend_bleed_edges(src: Image.Image) -> Image.Image:
    """Extend trim artwork into bleed by replicating edge pixels."""
    src = src.convert("RGB")
    assert src.size == (TRIM_W_PX, TRIM_H_PX), src.size

    out = Image.new("RGB", (FULL_W_PX, FULL_H_PX))
    out.paste(src, (BLEED_L, BLEED_T))

    for x in range(BLEED_L):
        for y in range(TRIM_H_PX):
            out.putpixel((x, BLEED_T + y), src.getpixel((0, y)))

    for x in range(FULL_W_PX - BLEED_R, FULL_W_PX):
        for y in range(TRIM_H_PX):
            out.putpixel((x, BLEED_T + y), src.getpixel((TRIM_W_PX - 1, y)))

    for y in range(BLEED_T):
        for x in range(TRIM_W_PX):
            out.putpixel((BLEED_L + x, y), src.getpixel((x, 0)))

    for y in range(FULL_H_PX - BLEED_B, FULL_H_PX):
        for x in range(TRIM_W_PX):
            out.putpixel((BLEED_L + x, y), src.getpixel((x, TRIM_H_PX - 1)))

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


def build_bleed_pdf(images: list[tuple[str, Image.Image]], path: Path) -> None:
    """Bleed PDF: page exactly 3.75x2.25 in, no crop marks, no extra margin."""
    page_w = FULL_W_IN * inch
    page_h = FULL_H_IN * inch
    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))

    for _label, im in images:
        tmp = OUT / "_tmp_bleed_page.png"
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
    set_pdf_boxes(path)


def set_pdf_boxes(path: Path) -> None:
    """Set TrimBox to inner 3.5x2 in and BleedBox to full 3.75x2.25 page."""
    reader = PdfReader(str(path))
    writer = PdfWriter()
    trim_box = [BLEED_PT, BLEED_PT, PAGE_W_PT - BLEED_PT, PAGE_H_PT - BLEED_PT]
    bleed_box = [0, 0, PAGE_W_PT, PAGE_H_PT]

    trim_rect = RectangleObject(trim_box)
    bleed_rect = RectangleObject(bleed_box)

    for page in reader.pages:
        page.trimbox = trim_rect
        page.bleedbox = bleed_rect
        page.cropbox = bleed_rect
        writer.add_page(page)

    with path.open("wb") as fh:
        writer.write(fh)


def content_mask_trim(arr: np.ndarray, side: str) -> np.ndarray:
    """Non-background pixels that must stay inside the safety line (text/logo/QR)."""
    h, w = arr.shape[:2]
    mask = np.zeros((h, w), dtype=bool)

    rail = np.zeros((h, w), dtype=bool)
    if side == "front":
        for x in range(33):
            rail[:, x] = np.all(np.abs(arr[:, x] - BRAND_RED) < 3, axis=1)
        for y in range(12):
            for x in range(40):
                if is_red(arr[y, x]):
                    rail[y, x] = True
        for y in range(h - 12, h):
            for x in range(40):
                if is_red(arr[y, x]):
                    rail[y, x] = True
    elif side == "back":
        for y in range(h):
            if is_red(arr[y, 0]):
                top_bar = y
                break
        else:
            top_bar = 0
        for y in range(h - 1, -1, -1):
            if is_red(arr[y, 0]):
                bot_start = y
                break
        else:
            bot_start = h - 1
        for y in range(h):
            if is_red(arr[y, 0]):
                if y <= top_bar + 15:
                    rail[y, :] = is_red(arr[y, 0])
        for y in range(h):
            if is_red(arr[y, 0]):
                if y >= bot_start - 15:
                    rail[y, :] = is_red(arr[y, 0])

    for y in range(h):
        for x in range(w):
            if tuple(arr[y, x]) == (255, 255, 255):
                continue
            if rail[y, x]:
                continue
            mask[y, x] = True
    return mask


def measure_content_margins(arr: np.ndarray, side: str) -> dict[str, int | None]:
    mask = content_mask_trim(arr, side)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return {"left": None, "top": None, "right": None, "bottom": None, "bbox": None}
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    h, w = arr.shape[:2]
    return {
        "left": x0 - SAFE_PX,
        "top": y0 - SAFE_PX,
        "right": (w - SAFE_PX - 1) - x1,
        "bottom": (h - SAFE_PX - 1) - y1,
        "bbox": [x0, y0, x1, y1],
    }


def draw_template_overlay(bleed_im: Image.Image, side: str) -> Image.Image:
    """Overlay trim + safety rectangles on bleed art (printer template guides)."""
    preview = bleed_im.copy()
    draw = ImageDraw.Draw(preview)

    trim_l = BLEED_L
    trim_t = BLEED_T
    trim_r = trim_l + TRIM_W_PX
    trim_b = trim_t + TRIM_H_PX

    safe_l = trim_l + SAFE_PX
    safe_t = trim_t + SAFE_PX
    safe_r = safe_l + SAFE_W_PX - 1
    safe_b = safe_t + SAFE_H_PX - 1

    magenta = (255, 0, 255)
    cyan = (0, 180, 255)

    draw.rectangle([trim_l, trim_t, trim_r - 1, trim_b - 1], outline=magenta, width=2)
    draw.rectangle([safe_l, safe_t, safe_r, safe_b], outline=cyan, width=2)

    margins = measure_content_margins(np.array(bleed_im.crop((trim_l, trim_t, trim_r, trim_b))), side)
    label = (
        f"{side}: L{margins['left']} T{margins['top']} "
        f"R{margins['right']} B{margins['bottom']} px"
    )
    draw.text((safe_l + 8, safe_t + 8), label, fill=(30, 30, 30))
    return preview


def verify_safe_content(trim_im: Image.Image, side: str) -> tuple[bool, dict]:
    margins = measure_content_margins(np.array(trim_im.convert("RGB")), side)
    ok = all(
        margins[k] is not None and margins[k] >= 0
        for k in ("left", "top", "right", "bottom")
    )
    return ok, margins


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)

    trim_images: list[tuple[str, Image.Image]] = []
    bleed_images: list[tuple[str, Image.Image]] = []
    margin_report: dict[str, dict] = {}

    for label, src_path in SIDES:
        src = Image.open(src_path).convert("RGB")
        assert src.size == (TRIM_W_PX, TRIM_H_PX), f"{label} expected 1050x600, got {src.size}"
        trim_images.append((label, src.copy()))
        bleed_images.append((label, extend_bleed_edges(src)))

        save_png(src, OUT / f"option-a-{label}-trim-300dpi.png")
        save_png(bleed_images[-1][1], OUT / f"option-a-{label}-bleed-300dpi.png")

        ok, margins = verify_safe_content(src, label)
        margin_report[label] = margins
        status = "PASS" if ok else "FAIL"
        print(f"{label} safety check: {status} margins(px)={margins}")

        overlay = draw_template_overlay(bleed_images[-1][1], label)
        overlay_path = PREVIEWS / f"safety-overlay-{label}.png"
        save_png(overlay, overlay_path)

    build_trim_pdf(trim_images, OUT / "love-forward-option-a-print.pdf")
    build_bleed_pdf(bleed_images, OUT / "love-forward-option-a-print-bleed.pdf")

    for i, (label, im) in enumerate(trim_images, start=1):
        save_png(im, PREVIEWS / f"trim-page-{i}-{label}.png")
    for i, (label, im) in enumerate(bleed_images, start=1):
        save_png(im, PREVIEWS / f"bleed-page-{i}-{label}.png")

    # Trim page previews
    for label, _ in trim_images:
        pass

    bleed_pdf = PdfReader(str(OUT / "love-forward-option-a-print-bleed.pdf"))
    page = bleed_pdf.pages[0]
    print(
        "Bleed PDF boxes:",
        "MediaBox", page.mediabox,
        "TrimBox", page.get("/TrimBox"),
        "BleedBox", page.get("/BleedBox"),
    )

    (OUT / "safety-margins.json").write_text(json.dumps(margin_report, indent=2) + "\n")

    all_ok = all(
        verify_safe_content(im, label)[0] for label, im in trim_images
    )
    print("Overall safety verification:", "PASS" if all_ok else "FAIL")
    print("Preview overlays:")
    for label, _ in SIDES:
        print(f"  print/option-a/previews/safety-overlay-{label}.png")


if __name__ == "__main__":
    main()
