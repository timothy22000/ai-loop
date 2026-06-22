#!/usr/bin/env python3
"""
Generate the favicon / app-icon set and web manifest from the loop mark.

    pip install pillow
    python scripts/make_icons.py

Writes: favicon.svg, favicon-32.png, apple-touch-icon.png (180),
icon-192.png, icon-512.png, site.webmanifest. Re-run if the mark changes.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, GOLD, TEAL = "#33302E", "#2E7FCB", "#1B97A1"
PAPER = "#FFF1E5"

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">
  <rect width="24" height="24" rx="5" fill="{ink}"/>
  <circle cx="12" cy="12" r="8" stroke="{gold}" stroke-width="1.6"/>
  <path d="M12 5.6a6.4 6.4 0 0 1 5.9 4" stroke="{teal}" stroke-width="1.6" stroke-linecap="round"/>
  <circle cx="18.2" cy="9.4" r="1.6" fill="{gold}"/>
  <circle cx="5.8" cy="14.6" r="1.6" fill="{teal}"/>
</svg>'''.format(ink=INK, gold=GOLD, teal=TEAL)

def draw_png(size):
    from PIL import Image, ImageDraw
    S = size * 4  # supersample for crisp edges
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(S * 5 / 24)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=INK)
    u = S / 24.0
    def c(cx, cy, rad, **kw): d.ellipse([(cx-rad)*u, (cy-rad)*u, (cx+rad)*u, (cy+rad)*u], **kw)
    lw = max(2, int(1.6 * u))
    c(12, 12, 8, outline=GOLD, width=lw)                      # gold ring
    bb = [(12-6.4)*u, (12-6.4)*u, (12+6.4)*u, (12+6.4)*u]     # teal arc
    d.arc(bb, start=-90, end=-20, fill=TEAL, width=lw)
    c(18.2, 9.4, 1.6, fill=GOLD)
    c(5.8, 14.6, 1.6, fill=TEAL)
    return img.resize((size, size), Image.LANCZOS)

def main():
    try:
        from PIL import Image  # noqa
    except ImportError:
        raise SystemExit("Install deps first:  pip install pillow")

    (ROOT / "favicon.svg").write_text(SVG, encoding="utf-8")
    for name, size in [("favicon-32.png", 32), ("apple-touch-icon.png", 180),
                       ("icon-192.png", 192), ("icon-512.png", 512)]:
        draw_png(size).save(ROOT / name, "PNG")

    manifest = {
        "name": "The AI Loop",
        "short_name": "AI Loop",
        "description": "An interactive map of the circular economy of AI.",
        "start_url": "./",
        "display": "standalone",
        "background_color": PAPER,
        "theme_color": PAPER,
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("wrote favicon.svg, favicon-32.png, apple-touch-icon.png, icon-192.png, icon-512.png, site.webmanifest")

if __name__ == "__main__":
    main()
