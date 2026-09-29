# Love Forward Foundation — Option A print package

Client-locked business card (**Option A: stacked contact front**). Source art: `assets/option-a-front.png`, `assets/option-a-back.png`.

## Which file to send the printer

| File | When to use |
|------|-------------|
| **`love-forward-option-a-print.pdf`** | **Default / primary.** Trim-size 3.5" × 2", 2 pages (front, back). Matches the client mock exactly — **no bleed**. Use when the printer adds their own bleed or accepts trim-only art. |
| **`love-forward-option-a-print-bleed.pdf`** | Use when the printer requires supplied bleed. Artboard 3.75" × 2.25" (0.125" bleed) with **crop/trim marks** in the margin showing the 3.5" × 2" cut line. Bleed is built by extending edge pixels only (red bars stay thin at trim). |

## Other files

| File | Description |
|------|-------------|
| `previews/trim-page-*.png` | Page previews of the trim PDF (matches `assets/*.png`) |
| `previews/bleed-page-*.png` | Page previews of the bleed PDF (includes crop marks) |
| `option-a-*-trim-300dpi.png` | Individual sides at trim size, 300 DPI |
| `option-a-*-bleed-300dpi.png` | Individual sides with bleed artboard, 300 DPI |

## Specs for printer

| Setting | Value |
|---------|--------|
| **Trim size** | 3.5" × 2" (US standard business card) |
| **Bleed (optional file)** | 0.125" on all sides → 3.75" × 2.25" artboard |
| **Sides** | 2 (front + back) |
| **Pages** | 2 (one card side per page) |
| **Resolution** | 300 DPI at trim (source art is 1050×600 px) |
| **Color** | RGB (`#E82624` brand red, black, white). **Request CMYK conversion** at prepress if required. |
| **QR code** | Points to https://loveforwardfoundation.org |

### Back art (logo side)

Two thin red bars at **top and bottom** (matches client mock on `assets/option-a-back.png`).

### Regenerating

```bash
python3 print/option-a/build_print_package.py
```

Requires: `Pillow`, `reportlab`, `pypdf` (`pip install Pillow reportlab pypdf`).
