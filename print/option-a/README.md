# Love Forward Foundation — Option A print package

Client-locked business card (**Option A: stacked contact front**). Conforms to [printer business card template](https://splus-prod-phoenix-site-assets.pnimedia.com/dynamic/Content/documents/Category/Templates/en-us/BusinessCards/template.pdf) (trim 3.5" × 2", bleed page 3.75" × 2.25" / 270×162 pt, safety 3.25" × 1.75").

Source art: `assets/option-a-front.png`, `assets/option-a-back.png`.

## Which file to send the printer

| File | When to use |
|------|-------------|
| **`love-forward-option-a-print.pdf`** | **Default / primary.** Trim 3.5" × 2", 2 pages (front contact + QR, back logo). Matches client mock — **no bleed**. |
| **`love-forward-option-a-print-bleed.pdf`** | Use when printer requires supplied bleed. Page exactly **3.75" × 2.25"** (270×162 pt), **no crop marks**, no extra margin. `TrimBox` = inner 3.5" × 2"; `BleedBox` = full page. Bleed built by extending edge pixels. |

## Safety-line verification (300 DPI trim canvas)

Measured content margins inside the **3.25" × 1.75" safety box** (75 px inset from trim). Background bars/rails excluded.

| Side | Left | Top | Right | Bottom | Content bbox (px) |
|------|------|-----|-------|--------|-------------------|
| **Front** | 0 | 88 | 0 | 67 | 75, 163 → 974, 457 |
| **Back** | 69 | 35 | 69 | 35 | 144, 110 → 905, 489 |

Overlay previews (magenta = trim, cyan = safety): `previews/safety-overlay-front.png`, `previews/safety-overlay-back.png`.

Front layout tweak: contact block shifted +15 px right, QR shifted −2 px left; left red rail unchanged (bleeds to trim edge).

## Thin bar risk (back)

Top/bottom red bars are ~11 px / ~10 px tall (~**0.037"** at trim) and sit **on the trim edge**. Background art is correct per client mock, but cutter tolerance (often ±1/16" or more) can make one bar look slightly thicker/thinner or clip a hairline. Flag to the printer that edge bars are intentional full-bleed graphics.

## Other files

| File | Description |
|------|-------------|
| `previews/trim-page-*.png` | Trim PDF page previews |
| `previews/bleed-page-*.png` | Bleed artboard previews |
| `option-a-*-trim-300dpi.png` / `*-bleed-300dpi.png` | Individual sides |
| `safety-margins.json` | Machine-readable margin report |
| `build_print_package.py` | Regenerate all outputs |

## Specs

| Setting | Value |
|---------|--------|
| **Trim** | 3.5" × 2" |
| **Bleed (optional PDF)** | 0.125" all sides → 3.75" × 2.25" |
| **Safety** | 3.25" × 1.75" (0.25" inset from trim) |
| **Resolution** | 300 DPI at trim (1050×600 px) |
| **Color** | RGB `#E82624`, black, white — request CMYK at prepress |
| **QR** | https://loveforwardfoundation.org |

### Regenerating

```bash
python3 print/option-a/build_print_package.py
```

Requires: `Pillow`, `reportlab`, `pypdf`, `numpy`.

If `assets/option-a-front.png` is replaced with an unadjusted layout, re-apply the safety shift (see `fix_front_layout()` in `build_print_package.py`) before rebuilding.
