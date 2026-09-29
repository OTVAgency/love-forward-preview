# Love Forward Foundation — Option A print package

Client-locked business card (**Option A: stacked contact front**). Source art: `assets/option-a-front.png`, `assets/option-a-back.png`.

## Files

| File | Description |
|------|-------------|
| `love-forward-option-a-print.pdf` | **Send this** — 2 pages: page 1 = front (contact + QR), page 2 = back (logo) |
| `option-a-front.pdf` | Front only (with bleed) |
| `option-a-back.pdf` | Back only (with bleed) |
| `option-a-front-trim-300dpi.png` | Front at trim size, 300 DPI |
| `option-a-back-trim-300dpi.png` | Back at trim size, 300 DPI |
| `option-a-front-bleed-300dpi.png` | Front with bleed, 300 DPI |
| `option-a-back-bleed-300dpi.png` | Back with bleed, 300 DPI |

## Specs for printer

| Setting | Value |
|---------|--------|
| **Trim size** | 3.5" × 2" (US standard business card) |
| **Bleed** | **Yes** — 0.125" on all sides (full artboard 3.75" × 2.25") |
| **Sides** | 2 (front + back) |
| **Pages** | 2 (one card side per page) |
| **Resolution** | 300 DPI effective at trim (source art is 1050×600 px = 300 DPI at 3.5×2") |
| **Color** | RGB (`#E82624` brand red, black, white). **Request CMYK conversion** at prepress if required. |
| **QR code** | Points to https://loveforwardfoundation.org |

### Bleed notes

- White background extends cleanly into bleed on all sides.
- **Front (contact):** left red bar and top/bottom corner rules extended into bleed.
- **Back (logo):** single top red rule extended into bleed.

### Regenerating

```bash
python3 print/option-a/build_print_package.py
```

Requires: `Pillow`, `reportlab` (`pip install Pillow reportlab`).
