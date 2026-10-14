#!/usr/bin/env python3
"""One-off: extract Syne ExtraBold (wght 800) outlines from the portfolio's font file
into tools/fonts/syne-800.json so the SVG generator can draw display type as paths.

    python tools/extract_glyphs.py path/to/syne-latin-wght-normal.woff2

Needs fontTools + brotli (only for this step; the generator itself has no dependencies).
"""
import json, sys, pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

src = sys.argv[1]
font = instantiateVariableFont(TTFont(src), {"wght": 800})
gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,()/-+:&'!?#·✦ "
out = {"upm": upm, "capHeight": font["OS/2"].sCapHeight, "glyphs": {}}
for ch in chars:
    if ord(ch) not in cmap:
        continue
    g = gs[cmap[ord(ch)]]
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
    g.draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
    out["glyphs"][ch] = {"adv": g.width, "d": pen.getCommands()}
dst = pathlib.Path(__file__).parent / "fonts" / "syne-800.json"
dst.write_text(json.dumps(out, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
print(dst, dst.stat().st_size, "bytes", len(out["glyphs"]), "glyphs, upm", upm, "cap", out["capHeight"])
