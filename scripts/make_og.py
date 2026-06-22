#!/usr/bin/env python3
"""
Regenerate og-image.png (1200x630) in the site's style.

    pip install pillow numpy
    python scripts/make_og.py

Fonts (Space Grotesk, Space Mono) are downloaded once from the Google Fonts
GitHub mirror and cached under scripts/.fontcache/. Re-run this whenever the
headline or palette changes so the social card stays in sync.
"""
import json, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "scripts" / ".fontcache"
FONTS = {
    "SourceSerif4.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf",
    "IBMPlexMono-Bold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Bold.ttf",
    "IBMPlexMono-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf",
}
INK, BONE, GOLD, TEAL, MUTED = (255,241,229), (51,48,46), (15,84,153), (13,118,128), (107,102,96)

def fonts():
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in FONTS.items():
        dst = CACHE / name
        if not dst.exists():
            print("downloading", name)
            urllib.request.urlretrieve(url, dst)
    return CACHE

def main():
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import numpy as np
    except ImportError:
        raise SystemExit("Install deps first:  pip install pillow numpy")

    fdir = fonts()
    meta = json.loads((ROOT / "data" / "deals.json").read_text(encoding="utf-8")).get("meta", {})
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), INK)

    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = 965, 300
    for rx, ry, a in [(250,250,34),(180,180,26),(120,120,20)]:
        d.ellipse([cx-rx,cy-ry,cx+rx,cy+ry], outline=(170,150,135,a), width=2)
    d.arc([cx-210,cy-210,cx+210,cy+210], 300, 80, fill=(15,84,153,160), width=4)
    d.arc([cx-210,cy-210,cx+210,cy+210], 110, 250, fill=(13,118,128,150), width=4)
    d.ellipse([cx+205-9,cy-30-9,cx+205+9,cy-30+9], fill=GOLD)
    d.ellipse([cx-205-8,cy+40-8,cx-205+8,cy+40+8], fill=TEAL)

    def grok(sz):
        f = ImageFont.truetype(str(fdir/"SourceSerif4.ttf"), sz)
        try: f.set_variation_by_axes([60,700])
        except Exception:
            try: f.set_variation_by_axes([700,60])
            except Exception: pass
        return f
    monoR = lambda sz: ImageFont.truetype(str(fdir/"IBMPlexMono-Regular.ttf"), sz)
    mono  = lambda sz: ImageFont.truetype(str(fdir/"IBMPlexMono-Bold.ttf"), sz)

    M, lx, ly = 78, 78, 70
    d.ellipse([lx,ly,lx+38,ly+38], outline=GOLD, width=3)
    d.arc([lx,ly,lx+38,ly+38], -90, 30, fill=TEAL, width=3)
    d.ellipse([lx+30,ly+4,lx+30+7,ly+4+7], fill=GOLD)
    d.ellipse([lx+3,ly+27,lx+3+7,ly+27+7], fill=TEAL)

    def spaced(xy, text, font, fill, ls):
        x, y = xy
        for ch in text:
            d.text((x,y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + ls
    spaced((lx+54, ly+8), "THE AI LOOP", mono(24), BONE, 3)

    def line(y, text, fill, sz=92):
        f = grok(sz); d.text((M,y), text, font=f, fill=fill)
        return d.textbbox((M,y), text, font=f)[3]
    y = 190
    y = line(y, "The money goes", BONE)
    y = line(y+8, "in circles.", BONE)
    line(y+8, "So do the chips.", TEAL)

    ky = H - 86
    d.line([M, ky-22, M+62, ky-22], fill=GOLD, width=2)
    spaced((M, ky), "THE CIRCULAR ECONOMY OF AI", monoR(21), GOLD, 2)
    asof = meta.get("lastUpdatedLabel", "")
    sub = "INTERACTIVE MAP OF THE MONEY, THE MATERIALS, THE RISK"
    spaced((M, ky+34), sub, monoR(17), MUTED, 1)

    noise = (np.random.rand(H, W, 1) * 255).astype("uint8")
    nimg = Image.fromarray(np.repeat(noise, 3, axis=2), "RGB")
    img = Image.blend(img, nimg, 0.018)

    out = ROOT / "og-image.png"
    img.save(out, "PNG")
    print("wrote", out)

if __name__ == "__main__":
    main()
