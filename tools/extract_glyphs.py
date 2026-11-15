#!/usr/bin/env python3
"""One-off: extract display-font outlines into tools/fonts/*.json so the SVG generator can
draw titles as paths (GitHub serves README SVGs as images, which can't load web fonts).

    python tools/extract_glyphs.py sora path/to/sora-latin-wght-normal.woff2 800
    python tools/extract_glyphs.py cormorant path/to/cormorant-garamond-latin-wght400-500.woff2 500

Sora is Waymark's display face; Cormorant Garamond is Noir Cafe's. Both are SIL OFL 1.1.
Needs fontTools + brotli (only for this step; the generator itself has no dependencies).
"""
import json, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

name, src, wght = sys.argv[1], sys.argv[2], int(sys.argv[3])
font = TTFont(src)
if "fvar" in font:
    font = instantiateVariableFont(font, {"wght": wght})
gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,()/-+:&'’!?#·✦—₹ "
out = {"upm": upm, "capHeight": font["OS/2"].sCapHeight, "glyphs": {}}
for ch in chars:
    if ord(ch) not in cmap:
        continue
    g = gs[cmap[ord(ch)]]
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
    g.draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
    out["glyphs"][ch] = {"adv": g.width, "d": pen.getCommands()}
dst = pathlib.Path(__file__).parent / "fonts" / f"{name}-{wght}.json"
dst.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
print(dst.name, dst.stat().st_size, "bytes", len(out["glyphs"]), "glyphs, upm", upm, "cap", out["capHeight"])
