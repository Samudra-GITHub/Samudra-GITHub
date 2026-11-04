#!/usr/bin/env python3
"""Generates every SVG in assets/readme/ and validates them.

    python tools/build_readme.py

Design language: "Orbital". An instrument-panel look borrowed from the flagship,
W.E.D.N.E.S.D.A.Y., and its living Earth and Moon.
  themes   every scene is rendered twice, assets/readme/dark/ and assets/readme/light/,
           and the README picks one with <picture> and prefers-color-scheme
  palette  deep navy or paper-white panels, hairline grids, one accent hue per project
  type     Syne ExtraBold drawn as outlined paths from tools/fonts/syne-800.json, so titles
           render identically everywhere; system mono for labels
  forms    rounded panels with corner registration ticks, orbit ellipses, mono index chips
  motion   CSS keyframes and SMIL only. No scripts, no external resources. The static
           (reduced-motion) state of every scene is a complete composition.
Nothing here is live telemetry. Every reading, record and status inside the artwork is
illustrative, and each SVG's <desc> says so.
"""
import json
import math
import pathlib
import random
import sys
import xml.dom.minidom
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "assets" / "readme"
FONT = json.loads((HERE / "fonts" / "syne-800.json").read_text(encoding="utf-8"))
UPM, CAP = FONT["upm"], FONT["capHeight"]

THEMES = {
    "dark": dict(card="#0A1020", panel="#101A2E", line="#22314F", text="#E8EEF9", mute="#8E9BB6",
                 faint="#18233B", star="#DCE6FF", night="#000510", ocean="#0B2340", glass="#FFFFFF"),
    "light": dict(card="#FFFFFF", panel="#F1F5FB", line="#D3DCEA", text="#0B1222", mute="#55627C",
                  faint="#E6ECF5", star="#7D8BA8", night="#0B1222", ocean="#DCEBFA", glass="#0B1222"),
}
# (dark, light) accent per project
ACC = {
    "wed": ("#5CC8FF", "#0A76B8"), "moon": ("#C9D3E3", "#5D6A84"), "samagra": ("#FFB547", "#B86200"),
    "artha": ("#4ADE9A", "#0C8552"), "prahari": ("#FF8A4C", "#C0470C"), "akasha": ("#3EE0D0", "#0B847A"),
    "tarang": ("#FF6FB5", "#BE1D70"), "rinti": ("#A78BFA", "#6A3CDC"), "orbit": ("#7C9CFF", "#2D4CD2"),
    "krama": ("#FF9E5E", "#C0520E"), "niriksh": ("#C6F04B", "#5A8400"), "skycast": ("#6CC8FF", "#0F72BA"),
    "portfolio": ("#7EE8FA", "#0886A0"), "skp": ("#8DA2FF", "#344FD4"), "noir": ("#E2B48A", "#87582C"),
    "waffle": ("#FFC94D", "#A87200"), "singularity": ("#C084FC", "#8629DC"), "fca": ("#FF6B6B", "#BF2828"),
    "website": ("#B8C2D6", "#56627A"), "vyom": ("#93A5FF", "#3F53CC"), "profile": ("#5EEA9F", "#15854C"),
    "ai": ("#F5A3FF", "#A32F9A"),
}
OK = {"dark": "#4ADE80", "light": "#15803D"}

BASE_CSS = """
.m{font-family:ui-monospace,"JetBrains Mono","Cascadia Mono",SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-weight:600}
.s{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-weight:500}
.fb{transform-box:fill-box;transform-origin:center}
.rise{animation:rise 14s cubic-bezier(.16,1,.3,1) infinite both}
@keyframes rise{0%{transform:translateY(110%)}6%,90%{transform:translateY(0)}96%,100%{transform:translateY(110%)}}
.flow{stroke-dasharray:3 9;animation:flow 1.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-24}}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite}
.spinr{transform-box:fill-box;transform-origin:center;animation:spin 30s linear infinite reverse}
@keyframes spin{to{transform:rotate(360deg)}}
.bob{animation:bob 4s ease-in-out infinite alternate}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(-6px)}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:0}}
.tw{animation:tw 3.2s ease-in-out infinite alternate}
@keyframes tw{from{opacity:.15}to{opacity:1}}
.rip{transform-box:fill-box;transform-origin:center;animation:rip 2.8s cubic-bezier(.2,.6,.3,1) infinite}
@keyframes rip{0%{transform:scale(.25);opacity:.95}100%{transform:scale(2.8);opacity:0}}
.eq{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1.1s ease-in-out infinite alternate}
@keyframes eq{from{transform:scaleY(.22)}to{transform:scaleY(1)}}
.grow{transform-box:fill-box;transform-origin:0 50%;animation:grow 7s cubic-bezier(.65,0,.35,1) infinite}
@keyframes grow{0%{transform:scaleX(0)}35%,85%{transform:scaleX(1)}100%{transform:scaleX(0)}}
.draw{stroke-dasharray:100;animation:draw 7s ease-in-out infinite}
@keyframes draw{0%{stroke-dashoffset:100}45%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-100}}
.glow{animation:glow 2.4s ease-in-out infinite alternate}
@keyframes glow{from{opacity:.35}to{opacity:1}}
.steam{transform-box:fill-box;transform-origin:50% 100%;animation:steam 3.6s ease-out infinite}
@keyframes steam{0%{transform:translateY(8px) scaleY(.6);opacity:0}30%{opacity:.9}100%{transform:translateY(-18px) scaleY(1.1);opacity:0}}
.drift{animation:drift 9s ease-in-out infinite alternate}
@keyframes drift{from{transform:translateX(-14px)}to{transform:translateX(18px)}}
.drip{transform-box:fill-box;transform-origin:50% 0;animation:drip 4.5s ease-in-out infinite}
@keyframes drip{0%{transform:scaleY(.15)}60%,85%{transform:scaleY(1)}100%{transform:scaleY(.15)}}
.shim{animation:shim 2.6s ease-in-out infinite}
@keyframes shim{0%{transform:translateX(-120px)}100%{transform:translateX(330px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def e(s):
    return escape(str(s), {'"': "&quot;"})


def f1(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Scene:
    def __init__(self, name, w, h, theme, title, desc):
        self.name, self.w, self.h, self.theme = name, w, h, theme
        self.P = THEMES[theme]
        self.title, self.desc = title, desc + " Illustrative artwork; nothing in it is live data."
        self.parts, self.defs, self.css, self.glyphs, self.n = [], [], "", set(), 0

    def acc(self, key):
        return ACC[key][0 if self.theme == "dark" else 1]

    def uid(self, p="u"):
        self.n += 1
        return f"{p}{self.n}"

    def add(self, *xs):
        self.parts.extend(xs)

    # ---- display type (Syne paths) ---------------------------------------------
    def tw(self, s, size, ls=0.0):
        return sum(FONT["glyphs"].get(c, {"adv": 600})["adv"] for c in s) * size / UPM + ls * size * len(s)

    def fit(self, s, width, ls=0.0, cap=999):
        return min(cap, width / self.tw(s, 1.0, ls))

    def display(self, s, x, y, size, fill, ls=0.0, anchor="start", rise=None):
        """Syne ExtraBold with baseline at y. rise = start delay (s) for a masked letter reveal."""
        width = self.tw(s, size, ls)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        k = size / UPM
        out, cx = "", x
        for i, c in enumerate(s):
            g = FONT["glyphs"].get(c)
            if g is None:
                cx += 0.5 * size
                continue
            if c != " ":
                self.glyphs.add(c)
                use = f'<use href="#g{ord(c)}" transform="translate({cx:.1f} {y:.1f}) scale({k:.4f})"/>'
                if rise is not None:
                    use = f'<g class="rise" style="animation-delay:{rise + i * 0.05:.2f}s">{use}</g>'
                out += use
            cx += g["adv"] * k + ls * size
        if rise is not None:
            cid = self.uid("c")
            top, bot = y - CAP * k - size * 0.14, y + size * 0.18
            self.defs.append(f'<clipPath id="{cid}"><rect x="{x-8:.1f}" y="{top:.1f}" width="{width+16:.1f}" height="{bot-top:.1f}"/></clipPath>')
            return f'<g clip-path="url(#{cid})" fill="{fill}">{out}</g>'
        return f'<g fill="{fill}">{out}</g>'

    def frame(self, accent, rx=22):
        P, w, h = self.P, self.w, self.h
        gid = self.uid("grid")
        self.defs.append(f'<pattern id="{gid}" width="32" height="32" patternUnits="userSpaceOnUse">'
                         f'<path d="M32 0H0V32" fill="none" stroke="{P["line"]}" stroke-opacity=".45" stroke-width="1"/></pattern>')
        cid = self.uid("clip")
        self.defs.append(f'<clipPath id="{cid}"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>')
        self.add(f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{rx}" fill="{P["card"]}"/>',
                 f'<rect width="{w}" height="{h}" fill="url(#{gid})" clip-path="url(#{cid})" opacity=".55"/>')
        self.tail = (f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{rx}" fill="none" stroke="{P["line"]}" stroke-width="1.5"/>'
                     + ticks(14, 14, w - 28, h - 28, accent))

    def seq(self, key, n, dur, fade=1.2):
        """Classes key0..key{n-1}; exactly one is visible at a time. key0 is the static state."""
        css = ""
        for i in range(n):
            a, b = i / n * 100, (i + 1) / n * 100
            frames = (f"0%,{a:.2f}%{{opacity:0}}{min(a+fade,b):.2f}%,{max(b-fade,a):.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}"
                      if i else f"0%,{b-fade:.2f}%{{opacity:1}}{b:.2f}%,{100-fade:.2f}%{{opacity:0}}100%{{opacity:1}}")
            css += f".{key}{i}{{opacity:{1 if i == 0 else 0};animation:{key}{i} {dur}s linear infinite}}@keyframes {key}{i}{{{frames}}}"
        self.css += css

    def stagger(self, key, n, dur, on=0.06, hold=0.86):
        """Classes key0..: element i fades/rises in at i*on of the loop and holds until hold."""
        for i in range(n):
            a = 2 + i * on * 100
            self.css += (f".{key}{i}{{animation:{key}{i} {dur}s cubic-bezier(.16,1,.3,1) infinite}}"
                         f"@keyframes {key}{i}{{0%,{a:.1f}%{{opacity:0;transform:translateY(8px)}}{a+6:.1f}%,{hold*100:.1f}%{{opacity:1;transform:translateY(0)}}{hold*100+5:.1f}%,100%{{opacity:0;transform:translateY(0)}}}}")

    def render(self):
        gdefs = "".join(f'<path id="g{ord(c)}" d="{FONT["glyphs"][c]["d"]}"/>' for c in sorted(self.glyphs))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-labelledby="t d" fill="none">\n<title id="t">{e(self.title)}</title>\n<desc id="d">{e(self.desc)}</desc>\n'
                f'<defs>{gdefs}{"".join(self.defs)}</defs>\n<style>{BASE_CSS}{self.css}</style>\n'
                + "\n".join(self.parts) + "\n" + getattr(self, "tail", "") + "\n</svg>\n")


# ------------------------------------------------------------------ primitives
def T(x, y, s, size=12, fill="#000", anchor="start", cls="m", op=None, ls=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    o = f' opacity="{op}"' if op is not None else ""
    l = f' letter-spacing="{ls}"' if ls is not None else ""
    return f'<text x="{f1(x)}" y="{f1(y)}" class="{cls}" font-size="{size}" fill="{fill}"{a}{o}{l}{extra}>{e(s)}</text>'


def ticks(x, y, w, h, c, L=9):
    d = (f"M{x} {y+L}V{y}H{x+L}M{x+w-L} {y}H{x+w}V{y+L}M{x+w} {y+h-L}V{y+h}H{x+w-L}M{x+L} {y+h}H{x}V{y+h-L}")
    return f'<path d="{d}" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>'


def mono_w(s, size):
    return len(s) * size * 0.62


def pill(x, y, s, fg, bd, size=11, fill="none", dot=None, h=24):
    w = mono_w(s, size) + 22 + (12 if dot else 0)
    out = f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{bd}" stroke-width="1.2"/>'
    tx = x + 11
    if dot:
        out += f'<circle cx="{f1(x+13)}" cy="{f1(y+h/2)}" r="3.5" fill="{dot}" class="glow"/>'
        tx += 12
    out += T(tx, y + h / 2 + size * 0.36, s, size, fg, ls=".04em")
    return out, w


def pills(x, y, items, fg, bd, size=11, gap=8, **kw):
    out = ""
    for s in items:
        p, w = pill(x, y, s, fg, bd, size, **kw)
        out += p
        x += w + gap
    return out


def stars(s, x, y, w, h, n, seed, r=(0.6, 1.6)):
    rnd = random.Random(seed)
    out = ""
    for _ in range(n):
        cx, cy, rr = x + rnd.random() * w, y + rnd.random() * h, rnd.uniform(*r)
        out += (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.2f}" fill="{s.P["star"]}" class="tw" '
                f'style="animation-delay:-{rnd.random()*4:.2f}s;animation-duration:{rnd.uniform(2.2,4.8):.1f}s"/>')
    return out


def ring_path(cx, cy, rx, ry):
    return f"M{f1(cx-rx)} {f1(cy)}a{f1(rx)} {f1(ry)} 0 1 0 {f1(2*rx)} 0a{f1(rx)} {f1(ry)} 0 1 0 {f1(-2*rx)} 0"


def orbiter(path, dur, body, begin=0.0, rot=None):
    return (f'<g>{body}<animateMotion dur="{dur}s" begin="-{begin:.2f}s" repeatCount="indefinite" path="{path}"'
            + (f' rotate="{rot}"' if rot else "") + "/></g>")


def globe(s, cx, cy, R, A, period=36, n=12, tilt=-18, points=(), night=True, grid_op=1.0):
    """A wireframe Earth whose meridians really turn: each meridian is a half-ellipse whose
    signed width follows R*sin(longitude + t), sampled for SMIL path interpolation."""
    P, k, N = s.P, 0.5523, 36
    gid, cid = s.uid("oc"), s.uid("gc")
    s.defs.append(f'<radialGradient id="{gid}" cx=".38" cy=".34" r=".75"><stop offset="0" stop-color="{A}" stop-opacity=".30"/>'
                  f'<stop offset=".7" stop-color="{P["ocean"]}" stop-opacity=".9"/><stop offset="1" stop-color="{P["ocean"]}"/></radialGradient>')
    s.defs.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>')
    hid = s.uid("halo")
    s.defs.append(f'<radialGradient id="{hid}"><stop offset=".72" stop-color="{A}" stop-opacity="0"/><stop offset=".8" stop-color="{A}" stop-opacity=".28"/>'
                  f'<stop offset="1" stop-color="{A}" stop-opacity="0"/></radialGradient>')

    def md(sx):
        return (f"M{cx:.1f} {cy-R:.1f}C{cx+sx*k:.1f} {cy-R:.1f} {cx+sx:.1f} {cy-R*k:.1f} {cx+sx:.1f} {cy:.1f}"
                f"C{cx+sx:.1f} {cy+R*k:.1f} {cx+sx*k:.1f} {cy+R:.1f} {cx:.1f} {cy+R:.1f}")
    out = f'<circle cx="{cx}" cy="{cy}" r="{R*1.25:.1f}" fill="url(#{hid})"/>'
    out += f'<g transform="rotate({tilt} {cx} {cy})"><circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{gid})"/>'
    out += f'<g clip-path="url(#{cid})" stroke="{A}" stroke-width="1" opacity="{grid_op}">'
    for lat in (-60, -30, 0, 30, 60):
        yy, hw = cy - R * math.sin(math.radians(lat)), R * math.cos(math.radians(lat))
        out += f'<path d="M{cx-hw:.1f} {yy:.1f}H{cx+hw:.1f}" stroke-opacity="{.55 if lat == 0 else .3}"/>'
    for i in range(n):
        ph = [2 * math.pi * (i / n + j / N) for j in range(N + 1)]
        ds = ";".join(md(R * math.sin(p)) for p in ph)
        ops = ";".join(f"{(.75 if math.cos(p) > 0 else .1):.2f}" for p in ph)
        out += (f'<path d="{md(R*math.sin(ph[0]))}" stroke-opacity="{ops.split(";")[0]}">'
                f'<animate attributeName="d" dur="{period}s" repeatCount="indefinite" values="{ds}"/>'
                f'<animate attributeName="stroke-opacity" dur="{period}s" repeatCount="indefinite" values="{ops}"/></path>')
    out += "</g>"
    for lat, lon, col in points:
        la, lo = math.radians(lat), math.radians(lon)
        ph = [lo + 2 * math.pi * j / N for j in range(N + 1)]
        xs = ";".join(f"{cx + R*math.cos(la)*math.sin(p):.1f} {cy - R*math.sin(la):.1f}" for p in ph)
        ops = ";".join("1" if math.cos(p) > 0.05 else "0" for p in ph)
        out += (f'<g opacity="{ops.split(";")[0]}"><g><circle r="3" fill="{col}"/><circle r="5" fill="none" stroke="{col}" stroke-width="1.4" class="rip" '
                f'style="animation-delay:-{(lat*7) % 3:.1f}s"/><animateTransform attributeName="transform" type="translate" dur="{period}s" '
                f'repeatCount="indefinite" values="{xs}"/></g>'
                f'<animate attributeName="opacity" dur="{period}s" repeatCount="indefinite" values="{ops}" calcMode="discrete"/></g>')
    if night:
        nid = s.uid("nt")
        s.defs.append(f'<linearGradient id="{nid}" x1="0" x2="1"><stop offset=".45" stop-color="{P["night"]}" stop-opacity="0"/>'
                      f'<stop offset=".72" stop-color="{P["night"]}" stop-opacity="{.55 if s.theme == "dark" else .22}"/>'
                      f'<stop offset="1" stop-color="{P["night"]}" stop-opacity="{.8 if s.theme == "dark" else .35}"/></linearGradient>')
        out += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{nid})"/>'
    out += f'<circle cx="{cx}" cy="{cy}" r="{R}" stroke="{A}" stroke-opacity=".8" stroke-width="1.4"/></g>'
    return out


def moon(s, cx, cy, r, A, seed=7):
    P = s.P
    gid, cid = s.uid("mg"), s.uid("mc")
    lo, hi = ("#2B3346", "#D9DFEA") if s.theme == "dark" else ("#8D97AA", "#F4F6FA")
    s.defs.append(f'<radialGradient id="{gid}" cx=".36" cy=".32" r=".78"><stop offset="0" stop-color="{hi}"/>'
                  f'<stop offset=".75" stop-color="{lo}"/><stop offset="1" stop-color="{lo}"/></radialGradient>')
    s.defs.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    rnd = random.Random(seed)
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/><g clip-path="url(#{cid})">'
    for _ in range(int(r / 2.4)):
        a, d = rnd.random() * 2 * math.pi, r * math.sqrt(rnd.random()) * 0.95
        cr = rnd.uniform(r * .025, r * .11)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        out += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{cr:.1f}" fill="#000" fill-opacity=".16"/>'
                f'<circle cx="{x-cr*.18:.1f}" cy="{y-cr*.18:.1f}" r="{cr*.8:.1f}" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="{max(.6, cr*.12):.1f}"/>')
    # maria
    for dx, dy, rr in ((-.25, -.2, .28), (.18, -.05, .22), (.05, .32, .18)):
        out += f'<circle cx="{cx+dx*r:.1f}" cy="{cy+dy*r:.1f}" r="{rr*r:.1f}" fill="#000" fill-opacity=".09"/>'
    tid = s.uid("mt")
    s.defs.append(f'<linearGradient id="{tid}" x1="0" x2="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="#000" stop-opacity="{.6 if s.theme == "dark" else .3}"/></linearGradient>')
    out += f'<rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="url(#{tid})"/></g>'
    out += f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{A}" stroke-opacity=".5" stroke-width="1.2"/>'
    return out


def wcore(cx, y, w, A, P, s, states=True):
    """The intelligence core: a single W line under the curve of the planet."""
    h = w * 0.34
    x0 = cx - w / 2
    pts = [(x0, y), (x0 + w * .22, y + h), (x0 + w * .5, y + h * .18), (x0 + w * .78, y + h), (x0 + w, y)]
    d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    arc = f"M{x0-w*.15:.1f} {y-6:.1f} Q{cx:.1f} {y-h*.75:.1f} {x0+w*1.15:.1f} {y-6:.1f}"
    out = (f'<path d="{arc}" stroke="{A}" stroke-opacity=".35" stroke-width="1.4"/>'
           f'<path d="{d}" stroke="{P["line"]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
           f'<path d="{d}" stroke="{A}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="glow"/>'
           f'<path d="{d}" pathLength="100" stroke="{P["text"]}" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 94">'
           f'<animate attributeName="stroke-dashoffset" values="100;0" dur="3.2s" repeatCount="indefinite"/></path>')
    return out


def save(s):
    svg = s.render()
    xml.dom.minidom.parseString(svg.encode("utf-8"))
    p = OUT / s.theme / f"{s.name}.svg"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(svg, encoding="utf-8", newline="\n")
    return p


def both(fn):
    for th in THEMES:
        save(fn(th))


# ================================================================== scenes
def hero(th):
    s = Scene("hero", 1000, 400, th, "Samudra Kar",
              "Samudra Kar. Computer Science engineering student building across systems, AI and product, from first principles. "
              "A turning wireframe Earth with a moon and satellites in orbit.")
    P, A, M = s.P, s.acc("wed"), s.acc("moon")
    s.frame(A)
    s.add(stars(s, 20, 20, 960, 360, 70, 3))
    s.add(T(56, 74, "// HELLO, I'M", 13, A, ls=".2em"))
    s.add(s.display("SAMUDRA", 52, 168, s.fit("SAMUDRA", 470), P["text"], rise=0.2))
    s.add(s.display("KAR", 52, 252, s.fit("SAMUDRA", 470), "none", rise=0.6).replace('fill="none"', f'fill="{P["card"]}" stroke="{A}" stroke-width="{2.2/(s.fit("SAMUDRA",470)/UPM):.0f}"', 1))
    s.add(T(56, 292, "Computer Science engineering student building across", 16, P["mute"], cls="s"))
    s.add(T(56, 314, "systems, AI and product, from first principles.", 16, P["mute"], cls="s"))
    s.seq("now", 3, 12)
    for i, w in enumerate(("W.E.D.N.E.S.D.A.Y.  ·  LOCAL-FIRST AI + LIVING EARTH",
                           "LUNAR INTELLIGENCE  ·  A 3D MOON, LIVE EPHEMERIS",
                           "SAMAGRA OS  ·  x86-64, FROM FIRST PRINCIPLES")):
        s.add(f'<g class="now{i}">' + T(56, 352, "NOW BUILDING  →  " + w, 12.5, A, ls=".08em") + "</g>")
    cx, cy = 770, 200
    s.add(f'<path d="{ring_path(cx, cy, 190, 62)}" stroke="{P["line"]}" stroke-width="1.2" transform="rotate(-14 {cx} {cy})"/>')
    s.add(f'<path d="{ring_path(cx, cy, 138, 44)}" stroke="{A}" stroke-opacity=".35" stroke-dasharray="2 6" transform="rotate(24 {cx} {cy})"/>')
    s.add(globe(s, cx, cy, 104, A, points=((35, 20, s.acc("prahari")), (-10, 140, s.acc("prahari")), (50, 250, A))))
    s.add(f'<g transform="rotate(-14 {cx} {cy})">' + orbiter(ring_path(cx, cy, 190, 62), 26, moon(s, 0, 0, 15, M)) + "</g>")
    s.add(f'<g transform="rotate(24 {cx} {cy})">' + orbiter(ring_path(cx, cy, 138, 44), 9, f'<rect x="-4" y="-2.5" width="8" height="5" fill="{P["text"]}"/><path d="M-11 0H11" stroke="{A}" stroke-width="2"/>') + "</g>")
    s.add(T(944, 368, "N 12.97°  E 77.59°  ·  BANGALORE", 10.5, P["mute"], anchor="end", ls=".1em"))
    return s


def section(th, key, idx, label, accent="wed"):
    s = Scene(f"sec-{key}", 1000, 64, th, label.title(), f"Section heading: {label.title()}.")
    P, A = s.P, s.acc(accent)
    s.add(T(4, 40, f"{idx:02d}", 14, A, ls=".1em"))
    s.add(s.display(label, 40, 42, 26, P["text"], ls=0.02))
    x = 40 + s.tw(label, 26, 0.02) + 22
    s.add(f'<path d="M{x:.0f} 33H996" stroke="{P["line"]}" stroke-width="1.2"/>')
    s.add(f'<path d="M{x:.0f} 33H996" stroke="{A}" stroke-width="1.4" class="flow"/>')
    s.add(f'<circle cy="33" r="3.5" fill="{A}"><animate attributeName="cx" values="{x:.0f};996;{x:.0f}" dur="9s" repeatCount="indefinite" '
          f'calcMode="spline" keySplines=".6 0 .4 1;.6 0 .4 1"/></circle>')
    return s


def wed_hero(th):
    s = Scene("wed-hero", 1000, 560, th, "W.E.D.N.E.S.D.A.Y.",
              "W.E.D.N.E.S.D.A.Y.: Watchful Earth-Data Navigator, Entirely Self-hosted Desktop Assistant for You. A personal AI assistant "
              "that runs on your own computer, with a living Earth at its centre. A turning globe with earthquake pulses, a satellite "
              "orbit and an aircraft track; the core's W line cycles through its states.")
    P, A = s.P, s.acc("wed")
    s.frame(A, 26)
    s.add(stars(s, 480, 20, 500, 520, 60, 11))
    s.add(pill(48, 44, "FLAGSHIP", P["card"], A, 11, fill=A)[0])
    s.add(pill(144, 44, "LOCAL-FIRST DESKTOP ASSISTANT", A, A, 11, dot=OK[th])[0])
    size = s.fit("W.E.D.N.E.S.D.A.Y.", 520, 0.01)
    s.add(s.display("W.E.D.N.E.S.D.A.Y.", 46, 140, size, P["text"], ls=0.01, rise=0.1))
    s.add(T(48, 176, "WATCHFUL EARTH-DATA NAVIGATOR, ENTIRELY", 12.5, A, ls=".14em"))
    s.add(T(48, 196, "SELF-HOSTED DESKTOP ASSISTANT FOR YOU", 12.5, A, ls=".14em"))
    for i, line in enumerate(("A personal AI assistant that runs on your own",
                              "computer, with a living Earth at its centre.")):
        s.add(T(48, 238 + i * 25, line, 19, P["text"], cls="s"))
    # core
    s.add(f'<rect x="48" y="300" width="420" height="120" rx="16" fill="{P["panel"]}" stroke="{P["line"]}"/>')
    s.add(T(66, 326, "THE CORE", 11, P["mute"], ls=".18em"))
    s.add(wcore(140, 352, 120, A, P, s))
    states = ("IDLE", "LISTENING", "THINKING", "RETRIEVING", "WAITING FOR APPROVAL", "EXECUTING", "SPEAKING", "REVIEWING")
    s.seq("st", len(states), 16)
    for i, st in enumerate(states):
        s.add(f'<g class="st{i}">' + T(236, 368, st, 15, P["text"], ls=".08em") + "</g>")
    s.add(T(236, 392, "one line, one behaviour per state", 12, P["mute"], cls="s"))
    s.add(pills(48, 448, ("OLLAMA · LOCAL MODEL", "CAPABILITY BROKER", "127.0.0.1 ONLY"), P["text"], P["line"], 11))
    s.add(pills(48, 482, ("CESIUMJS EARTH", "PUSH-TO-TALK"), P["text"], P["line"], 11))
    s.add(pill(48 + sum(mono_w(c, 11) + 30 for c in ("CESIUMJS EARTH", "PUSH-TO-TALK")), 482, "NEW · MOON MODE", s.acc("moon"), s.acc("moon"), 11, dot=s.acc("moon"))[0])
    # globe
    cx, cy, R = 745, 270, 168
    s.add(f'<path d="{ring_path(cx, cy, 228, 70)}" stroke="{P["line"]}" stroke-width="1.2" transform="rotate(-22 {cx} {cy})"/>')
    q = s.acc("prahari")
    s.add(globe(s, cx, cy, R, A, period=40, n=14,
                points=((38, 10, q), (-6, 120, q), (20, 200, q), (55, 290, A), (-30, 60, A))))
    track = f"M{cx-150} {cy+40} Q{cx-20} {cy-150} {cx+130} {cy-60}"
    s.add(f'<path d="{track}" stroke="{P["text"]}" stroke-opacity=".7" stroke-width="1.4" class="flow"/>')
    s.add(orbiter(track, 7, f'<path d="M-6 0L6 0M0 -1.5L-3 -6M0 1.5L-3 6" stroke="{P["text"]}" stroke-width="2" stroke-linecap="round"/>', rot="auto"))
    s.add(f'<g transform="rotate(-22 {cx} {cy})">' + orbiter(ring_path(cx, cy, 228, 70), 11,
          f'<rect x="-4" y="-3" width="8" height="6" fill="{P["text"]}"/><path d="M-13 0H13" stroke="{A}" stroke-width="2.4"/>') + "</g>")
    modes = ("LIVE", "TIME", "ORBIT")
    s.seq("md", 3, 9)
    s.add(f'<rect x="828" y="44" width="124" height="30" rx="15" fill="{P["panel"]}" stroke="{P["line"]}"/>')
    for i, m in enumerate(modes):
        s.add(f'<g class="md{i}"><circle cx="846" cy="59" r="4" fill="{q if i == 0 else A}" class="glow"/>' + T(858, 63.5, f"WORLD · {m}", 11, P["text"], ls=".08em") + "</g>")
    s.add(T(952, 520, "USGS · NASA EONET · GDACS · CELESTRAK · OPEN-METEO", 10, P["mute"], anchor="end", ls=".08em"))
    return s


def wed_moon(th):
    s = Scene("wed-moon", 1000, 340, th, "Lunar Intelligence",
              "Moon mode, Lunar Intelligence: an interactive 3D Moon with NASA Moon Trek LRO imagery, live JPL Horizons ephemeris for "
              "LRO, Chandrayaan-2 and Danuri, and a source-attributed NSSDCA catalogue of landing and impact sites. Three spacecraft "
              "orbit a cratered moon while site markers pulse.")
    P, A, M = s.P, s.acc("wed"), s.acc("moon")
    s.frame(M, 26)
    s.add(stars(s, 20, 20, 960, 300, 80, 21))
    cx, cy, r = 220, 170, 112
    orbits = (("LRO", 150, 44, -18, 8), ("CHANDRAYAAN-2", 178, 60, 12, 12), ("DANURI", 204, 78, -40, 16))
    for name, rx, ry, rot, dur in orbits:
        s.add(f'<path d="{ring_path(cx, cy, rx, ry)}" stroke="{P["line"]}" stroke-width="1.1" transform="rotate({rot} {cx} {cy})"/>')
    s.add(moon(s, cx, cy, r, M))
    for (a, d) in ((-.5, .4), (.2, .55), (.9, .3), (2.4, .62), (3.6, .5)):
        x, y = cx + r * d * math.cos(a), cy + r * d * math.sin(a)
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{A}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="4" stroke="{A}" stroke-width="1.2" class="rip" style="animation-delay:-{a % 2.8:.1f}s"/>')
    for i, (name, rx, ry, rot, dur) in enumerate(orbits):
        body = (f'<rect x="-3.5" y="-3.5" width="7" height="7" fill="{P["text"]}"/><path d="M-10 0H10" stroke="{A}" stroke-width="2"/>'
                f'<g transform="rotate({-rot})">' + T(12, -8, name, 10.5, P["text"], ls=".08em") + "</g>")
        s.add(f'<g transform="rotate({rot} {cx} {cy})">' + orbiter(ring_path(cx, cy, rx, ry), dur, body, begin=i * 3.1) + "</g>")
    x0 = 478
    s.add(pill(x0, 44, "NEW IN W.E.D.N.E.S.D.A.Y.", P["card"], M, 11, fill=M)[0])
    s.add(s.display("LUNAR INTELLIGENCE", x0, 112, s.fit("LUNAR INTELLIGENCE", 470), P["text"], rise=0.3))
    s.add(T(x0, 146, "An interactive 3D Moon beside the living Earth.", 17, P["mute"], cls="s"))
    rows = (("IMAGERY", "NASA Moon Trek · LRO mosaics"),
            ("EPHEMERIS", "JPL Horizons, live: LRO, Chandrayaan-2, Danuri"),
            ("SITES", "NSSDCA landing & impact catalogue, source-attributed"))
    s.stagger("mr", 3, 16, on=0.05, hold=0.95)
    for i, (k, v) in enumerate(rows):
        y = 190 + i * 40
        s.add(f'<g class="mr{i}"><rect x="{x0}" y="{y-22}" width="476" height="32" rx="10" fill="{P["panel"]}" stroke="{P["line"]}"/>'
              + T(x0 + 14, y - 1, k, 11, M, ls=".14em") + T(x0 + 112, y - 1, v, 13.5, P["text"], cls="s") + "</g>")
    return s


def wed_pipeline(th):
    s = Scene("wed-pipeline", 1000, 270, th, "Ask the Earth",
              "Ask the Earth: you ask, the local model picks a tool, the capability broker checks it, the tool fetches public records "
              "with their source and time, and a typed request goes to the globe, which confirms it at the backend, app and globe. "
              "Anything with consequences waits for your approval.")
    P, A = s.P, s.acc("wed")
    s.frame(A, 22)
    s.add(T(40, 50, "ASK THE EARTH", 12, A, ls=".2em") + T(206, 50, "how a question becomes a confirmed action on the globe", 13, P["mute"], cls="s"))
    nodes = (("YOU ASK", "type or speak"), ("LOCAL MODEL", "Ollama · qwen2.5:7b"), ("BROKER", "deny by default"),
             ("TOOL", "public source + time"), ("TYPED REQUEST", "fixed list of actions"), ("EARTH CONFIRMS", "backend · app · globe"))
    bw, gap, y = 140, 16, 82
    xs = [40 + i * (bw + gap) for i in range(6)]
    line = f"M{xs[0]+bw/2} {y+40}H{xs[-1]+bw/2}"
    s.add(f'<path d="{line}" stroke="{P["line"]}" stroke-width="2"/><path d="{line}" stroke="{A}" stroke-width="2" class="flow"/>')
    for i in range(3):
        s.add(orbiter(line, 6, f'<circle r="5" fill="{A}"/><circle r="9" fill="{A}" fill-opacity=".2"/>', begin=i * 2))
    s.seq("pn", 6, 6, fade=.5)
    for i, (h, sub) in enumerate(nodes):
        x = xs[i]
        s.add(f'<rect x="{x}" y="{y}" width="{bw}" height="80" rx="14" fill="{P["panel"]}" stroke="{P["line"]}"/>')
        s.add(f'<g class="pn{i}"><rect x="{x}" y="{y}" width="{bw}" height="80" rx="14" stroke="{A}" stroke-width="1.8"/></g>')
        s.add(T(x + 14, y + 22, f"{i+1:02d}", 10, A, ls=".1em") + T(x + 14, y + 47, h, 12.5, P["text"], ls=".04em")
              + T(x + 14, y + 66, sub, 11, P["mute"], cls="s"))
    # approval branch under broker
    bx = xs[2] + bw / 2
    s.add(f'<path d="M{bx} {y+80}V{y+118}" stroke="{P["line"]}" stroke-width="1.6" stroke-dasharray="3 4"/>')
    p, w = pill(bx - 120, y + 118, "CONSEQUENCES? WAITS FOR YOUR YES", P["text"], s.acc("samagra"), 11, dot=s.acc("samagra"))
    s.add(p)
    # three confirmations
    cxs = xs[5] + 16
    s.stagger("ck", 3, 6, on=0.12, hold=0.9)
    for i, lab in enumerate(("BACKEND", "APP", "GLOBE")):
        yy = y + 112 + i * 0
        xx = cxs + i * 44
        s.add(f'<g class="ck{i}"><circle cx="{xx+8}" cy="{yy+12}" r="9" fill="{OK[th]}" fill-opacity=".15" stroke="{OK[th]}"/>'
              f'<path d="M{xx+4} {yy+12}l3 3 6-6" stroke="{OK[th]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
              + T(xx + 8, yy + 36, lab, 8.5, P["mute"], anchor="middle", ls=".06em") + "</g>")
    s.add(T(40, 244, "No code from the model  ·  invented records are flagged  ·  every source shown with its retrieval time", 12, P["mute"], ls=".02em"))
    return s


def wed_modes(th):
    s = Scene("wed-modes", 1000, 250, th, "Mind, World, Pulse, Private",
              "Four parts of W.E.D.N.E.S.D.A.Y.: Mind, the assistant on a local model; World, the living Earth in Live, Time and Orbit "
              "modes; Pulse, a briefing of significant records with source and time; and Private, a core that listens only to 127.0.0.1.")
    P, A = s.P, s.acc("wed")
    tiles = (("MIND", "conversation, voice and", "approvals on a local model"),
             ("WORLD", "the living Earth: Live,", "Time and Orbit"),
             ("PULSE", "significant records, each", "with its source and time"),
             ("PRIVATE", "local model, local speech,", "core bound to 127.0.0.1"))
    w, gap = 235, 20
    for i, (h, l1, l2) in enumerate(tiles):
        x = i * (w + gap)
        s.add(f'<rect x="{x+.75}" y=".75" width="{w-1.5}" height="248" rx="20" fill="{P["card"]}" stroke="{P["line"]}" stroke-width="1.5"/>')
        s.add(ticks(x + 12, 12, w - 24, 224, A, 7))
        s.add(T(x + 24, 40, f"0{i+1}", 11, A, ls=".1em"))
        s.add(s.display(h, x + 24, 72, 24, P["text"]))
        s.add(T(x + 24, 210, l1, 12.5, P["mute"], cls="s") + T(x + 24, 228, l2, 12.5, P["mute"], cls="s"))
        cx, cy = x + w / 2, 135
        if i == 0:
            rnd = random.Random(4)
            for j in range(19):
                bh = 14 + 46 * abs(math.sin(j * .55)) * rnd.uniform(.5, 1)
                s.add(f'<rect x="{x+30+j*9.4:.1f}" y="{cy+28-bh:.1f}" width="5" height="{bh:.1f}" rx="2.5" fill="{A}" class="eq" '
                      f'style="animation-delay:-{rnd.random():.2f}s;animation-duration:{rnd.uniform(.7,1.3):.2f}s"/>')
            s.add(T(cx, cy + 50, "HOLD TO TALK", 9.5, P["mute"], anchor="middle", ls=".18em"))
        elif i == 1:
            s.add(globe(s, cx, cy - 4, 52, A, period=24, n=10, points=((30, 40, s.acc("prahari")),)))
        elif i == 2:
            rows = ("M5.1  ·  USGS", "WILDFIRE  ·  EONET", "ALERT  ·  GDACS", "M4.6  ·  USGS", "STORM  ·  EONET")
            s.stagger(f"pr{i}", 5, 9, on=0.1)
            for j, r in enumerate(rows):
                yy = 92 + j * 19
                s.add(f'<g class="pr{i}{j}"><circle cx="{x+30}" cy="{yy-4}" r="3" fill="{s.acc("prahari") if j % 3 == 0 else A}"/>'
                      + T(x + 42, yy, r, 10.5, P["text"], ls=".04em") + T(x + w - 24, yy, f"{12+j*7%50:02d}:{(j*17)%60:02d}", 10, P["mute"], anchor="end") + "</g>")
        else:
            s.add(f'<rect x="{cx-26}" y="{cy-14}" width="52" height="40" rx="8" stroke="{A}" stroke-width="2"/>'
                  f'<path d="M{cx-15} {cy-14}V{cy-26}a15 15 0 0 1 30 0V{cy-14}" stroke="{A}" stroke-width="2"/>'
                  f'<circle cx="{cx}" cy="{cy+4}" r="4" fill="{A}" class="glow"/>')
            s.add(f'<circle cx="{cx}" cy="{cy+6}" r="30" stroke="{A}" stroke-width="1.2" class="rip"/>')
            s.add(T(cx, cy + 50, "127.0.0.1", 11, P["text"], anchor="middle", ls=".14em"))
    return s


def samagra(th):
    s = Scene("samagra-os", 1000, 320, th, "Samagra OS",
              "Samagra OS: a real x86-64 operating system built from first principles. Boot stages light in sequence, physical page "
              "frames fill a memory map and a preemptive scheduler slices time across kernel tasks.")
    P, A = s.P, s.acc("samagra")
    s.frame(A, 24)
    s.add(pill(44, 40, "ALSO BUILDING", P["card"], A, 11, fill=A)[0])
    s.add(s.display("SAMAGRA OS", 42, 120, s.fit("SAMAGRA OS", 390, cap=64), P["text"], rise=0.2))
    s.add(T(46, 152, "A REAL x86-64 OPERATING SYSTEM,", 12.5, A, ls=".14em") + T(46, 172, "BUILT FROM FIRST PRINCIPLES", 12.5, A, ls=".14em"))
    s.add(T(46, 210, "Long mode, paging, interrupts, a preemptive", 15, P["mute"], cls="s") + T(46, 230, "scheduler, early Ring 3 and system calls.", 15, P["mute"], cls="s"))
    s.add(pills(46, 262, ("C", "x86-64 ASM", "CLANG · LLD · NASM", "QEMU"), P["text"], P["line"], 11))
    x0, w0 = 470, 486
    stages = ("BOOT", "LONG MODE", "MEMORY", "INTERRUPTS", "SCHEDULER", "RING 3")
    s.add(T(x0, 52, "BOOT SEQUENCE", 10, P["mute"], ls=".18em"))
    bw = (w0 - 5 * 6) / 6
    s.seq("bs", 6, 7.2, fade=.4)
    for i, st in enumerate(stages):
        x = x0 + i * (bw + 6)
        s.add(f'<rect x="{x:.1f}" y="62" width="{bw:.1f}" height="34" rx="8" fill="{P["panel"]}" stroke="{P["line"]}"/>')
        s.add(f'<g class="bs{i}"><rect x="{x:.1f}" y="62" width="{bw:.1f}" height="34" rx="8" fill="{A}" fill-opacity=".18" stroke="{A}" stroke-width="1.6"/></g>')
        s.add(T(x + bw / 2, 83, st, 9.5, P["text"], anchor="middle", ls=".04em"))
    s.add(T(x0, 126, "PHYSICAL PAGE FRAMES", 10, P["mute"], ls=".18em"))
    n, fw = 32, (w0 - 31 * 3) / 32
    rnd = random.Random(9)
    for i in range(n):
        x = x0 + i * (fw + 3)
        s.add(f'<rect x="{x:.1f}" y="136" width="{fw:.1f}" height="24" rx="3" fill="{P["faint"]}"/>')
        if rnd.random() < .7:
            s.add(f'<rect x="{x:.1f}" y="136" width="{fw:.1f}" height="24" rx="3" fill="{A}" opacity="0">'
                  f'<animate attributeName="opacity" values="0;0;.85;.85;0" keyTimes="0;{i/n*.6:.3f};{i/n*.6+.04:.3f};.9;1" dur="8s" repeatCount="indefinite"/></rect>')
    s.add(T(x0, 190, "PREEMPTIVE SCHEDULER", 10, P["mute"], ls=".18em"))
    lanes = ("IDLE", "TASK A", "TASK B", "TASK C")
    for j, ln in enumerate(lanes):
        yy = 200 + j * 22
        s.add(T(x0, yy + 13, ln, 9.5, P["mute"]) + f'<rect x="{x0+56}" y="{yy}" width="{w0-56}" height="16" rx="4" fill="{P["faint"]}"/>')
    slot = (w0 - 56) / 12
    order = [1, 2, 3, 1, 2, 0, 3, 1, 2, 3, 1, 2]
    for k, lane in enumerate(order):
        s.add(f'<rect x="{x0+56+k*slot+1:.1f}" y="{200+lane*22+2}" width="{slot-2:.1f}" height="12" rx="3" fill="{A}" fill-opacity="{.4 if lane else .2}"/>')
    s.add(f'<rect y="196" width="2" height="88" fill="{P["text"]}"><animate attributeName="x" values="{x0+56};{x0+w0}" dur="6s" repeatCount="indefinite"/></rect>')
    return s


# ---- per-project cards ----------------------------------------------------
CW, CH = 480, 300


def card(th, slug, key, idx, title, lang, chips, draw, desc):
    s = Scene(slug, CW, CH, th, title, desc)
    P, A = s.P, s.acc(key)
    s.frame(A, 20)
    s.add(T(28, 44, f"{idx:02d}", 11, A, ls=".1em") + T(52, 44, lang, 11, P["mute"], ls=".12em"))
    s.add(f'<circle cx="446" cy="40" r="4" fill="{A}" class="glow"/>')
    s.add(s.display(title, 26, 88, s.fit(title, 428, cap=34), P["text"]))
    s.add(f'<g transform="translate(24 106)">' + draw(s, P, A) + "</g>")
    s.add(T(28, 276, "  ·  ".join(chips), 10.5, P["mute"], ls=".06em"))
    return s


def d_artha(s, P, A):
    goals = (("EMERGENCY FUND", .9), ("HOME", .48), ("EDUCATION", .7), ("RETIREMENT", .58))
    out = ""
    for i, (g, v) in enumerate(goals):
        y = 14 + i * 32
        out += T(0, y + 4, g, 9.5, P["mute"], ls=".06em")
        out += f'<rect x="0" y="{y+10}" width="230" height="7" rx="3.5" fill="{P["faint"]}"/>'
        out += f'<rect x="0" y="{y+10}" width="{230*v:.0f}" height="7" rx="3.5" fill="{A if i != 1 else s.acc("prahari")}" class="grow" style="animation-delay:{i*.25}s"/>'
    s.seq("fx", 2, 7)
    out += f'<g class="fx0">{pill(150, 30, "SLIPS", s.acc("prahari"), s.acc("prahari"), 9, h=18)[0]}</g>'
    out += f'<g class="fx1">{pill(150, 30, "SMALLEST FIX", A, A, 9, h=18)[0]}</g>'
    pts = [(258 + i * 17, 120 - 80 * (1 - math.exp(-i / 6)) - 6 * math.sin(i)) for i in range(11)]
    out += f'<path d="M256 124H432M256 124V10" stroke="{P["line"]}"/>'
    out += f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in pts)}" pathLength="100" stroke="{A}" stroke-width="2.4" stroke-linecap="round" class="draw"/>'
    out += T(260, 140, "TRAJECTORY · TODAY'S MONEY", 9, P["mute"], ls=".08em")
    return out


def d_prahari(s, P, A):
    cx, cy, r = 70, 100, 62
    out = f'<path d="M{cx-r} {cy}A{r} {r} 0 0 1 {cx+r} {cy}" stroke="{P["faint"]}" stroke-width="12" stroke-linecap="round"/>'
    for a0, a1, c in ((180, 240, OK[s.theme]), (240, 300, s.acc("samagra")), (300, 360, A)):
        p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
        out += f'<path d="M{p0[0]:.1f} {p0[1]:.1f}A{r} {r} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}" stroke="{c}" stroke-width="12" stroke-opacity=".75"/>'
    out += (f'<g><path d="M{cx} {cy}L{cx} {cy-r+14}" stroke="{P["text"]}" stroke-width="3" stroke-linecap="round"/>'
            f'<animateTransform attributeName="transform" type="rotate" values="-60 {cx} {cy};35 {cx} {cy};-10 {cx} {cy};-60 {cx} {cy}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines=".5 0 .5 1;.5 0 .5 1;.5 0 .5 1"/></g>')
    out += f'<circle cx="{cx}" cy="{cy}" r="6" fill="{P["text"]}"/>' + T(cx, cy + 26, "EXPLAINABLE RISK", 9, P["mute"], anchor="middle", ls=".1em")
    s.stagger("ab", 5, 7, on=.1)
    for i in range(5):
        x = 170 + i * 52
        out += f'<g class="ab{i}"><rect x="{x}" y="40" width="40" height="40" rx="8" fill="{P["panel"]}" stroke="{A}" stroke-width="1.4"/>'
        out += T(x + 20, 64, f"#{(i*2654435761) % 4096:03x}", 9, P["text"], anchor="middle")
        if i:
            out += f'<path d="M{x-12} 60H{x}" stroke="{A}" stroke-width="2"/>'
        out += "</g>"
    out += T(170, 108, "AUDIT LOG · TAMPER-EVIDENT", 9, P["mute"], ls=".1em")
    out += T(170, 126, "COPILOT · PERMISSION-SCOPED", 9, P["mute"], ls=".1em")
    return out


def d_akasha(s, P, A):
    rnd = random.Random(5)
    cid = s.uid("ak")
    out = ""
    cols, rows, cw = 13, 7, 20
    for i in range(cols):
        for j in range(rows):
            v = (math.sin(i * .7) + math.cos(j * .9 + i * .3)) * .25 + .5
            out += f'<rect x="{i*cw}" y="{j*cw}" width="{cw-1}" height="{cw-1}" fill="{A}" fill-opacity="{.12+.55*v*rnd.uniform(.7,1):.2f}"/>'
    s.defs.append(f'<clipPath id="{cid}"><rect y="0" width="260" height="140"><animate attributeName="x" values="0;260;260;0" keyTimes="0;.55;.85;1" dur="8s" repeatCount="indefinite"/></rect></clipPath>')
    cl = "#FFFFFF" if s.theme == "dark" else "#F7F9FC"
    out += f'<g clip-path="url(#{cid})"><g class="drift">'
    for _ in range(9):
        x, y, rr = rnd.uniform(0, 260), rnd.uniform(10, 130), rnd.uniform(14, 30)
        out += f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rr*1.6:.0f}" ry="{rr:.0f}" fill="{cl}" fill-opacity=".86"/>'
    out += "</g></g>"
    out += f'<rect x="0" y="0" width="2" height="140" fill="{A}"><animate attributeName="x" values="0;260;260;0" keyTimes="0;.55;.85;1" dur="8s" repeatCount="indefinite"/></rect>'
    # U-Net
    hs = (90, 64, 40, 24, 40, 64, 90)
    for i, h in enumerate(hs):
        x = 290 + i * 20
        out += f'<rect x="{x}" y="{70-h/2}" width="10" height="{h}" rx="3" fill="{A}" fill-opacity=".7" class="glow" style="animation-delay:{i*.18:.2f}s"/>'
    for i in range(3):
        out += f'<path d="M{295+i*20} {70-hs[i]/2-4}V{70-hs[i]/2-10-i*0}H{295+(6-i)*20}V{70-hs[i]/2-4}" stroke="{P["mute"]}" stroke-width="1" stroke-dasharray="2 3"/>'
    out += T(288, 136, "U-NET · SENTINEL-2", 9, P["mute"], ls=".1em")
    return out


def d_tarang(s, P, A):
    rnd = random.Random(2)
    out = ""
    for i in range(26):
        h = rnd.uniform(20, 74)
        out += (f'<rect x="{i*9.5:.1f}" y="{84-h:.1f}" width="6" height="{h:.1f}" rx="3" fill="{A}" class="eq" '
                f'style="animation-delay:-{rnd.random():.2f}s;animation-duration:{rnd.uniform(.5,1.2):.2f}s"/>')
    out += f'<rect x="0" y="104" width="246" height="4" rx="2" fill="{P["faint"]}"/>'
    out += f'<rect x="0" y="104" width="246" height="4" rx="2" fill="{A}" class="grow" style="animation-duration:12s"/>'
    out += T(0, 130, "NOW PLAYING · SYNCED LYRICS", 9, P["mute"], ls=".1em")
    lines = ("first line of the verse", "the line being sung now", "the next line, waiting", "and the one after that")
    s.seq("ly", 4, 8)
    for i, l in enumerate(lines):
        y = 18 + i * 28
        out += T(278, y, l, 12, P["mute"], cls="s", op=".55")
        out += f'<g class="ly{i}"><rect x="268" y="{y-14}" width="3" height="18" rx="1.5" fill="{A}"/>' + T(278, y, l, 12, P["text"], cls="s") + "</g>"
    return out


def d_rinti(s, P, A):
    s.stagger("rb", 4, 9, on=.12)
    msgs = ((True, "what changed in the paper?"), (False, "Three things, with sources"), (False, ""), (True, "remember that for later"))
    out = ""
    for i, (me, m) in enumerate(msgs):
        y = 4 + i * 34
        if i == 2:
            out += f'<g class="rb{i}">' + pills(10, y, ("[1] arxiv", "[2] blog", "[3] docs"), A, A, 9, h=22, gap=6) + "</g>"
            continue
        w = mono_w(m, 10.5) + 24
        x = 260 - w if me else 0
        out += (f'<g class="rb{i}"><rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{A if me else P["panel"]}" '
                f'fill-opacity="{.2 if me else 1}" stroke="{A if me else P["line"]}"/>' + T(x + 12, y + 17, m, 10.5, P["text"]) + "</g>")
    out += f'<path d="M280 4V136" stroke="{P["line"]}"/>'
    for i, (k, v) in enumerate((("MEMORY", "per user"), ("RESEARCH", "cited, multi-step"), ("SESSIONS", "Argon2 · HttpOnly · CSRF"))):
        y = 20 + i * 44
        out += T(296, y, k, 9.5, A, ls=".12em") + T(296, y + 18, v, 11, P["text"], cls="s")
    return out


def d_orbit(s, P, A):
    cx, cy = 216, 68
    out = ""
    for k, (rx, ry, dur) in enumerate(((70, 24, 8), (130, 44, 13), (196, 64, 19))):
        path = ring_path(cx, cy, rx, ry)
        out += f'<path d="{path}" stroke="{P["line"]}" stroke-width="1.2"/>'
        for j in range(k + 1):
            out += orbiter(path, dur, f'<rect x="-11" y="-8" width="22" height="16" rx="4" fill="{P["panel"]}" stroke="{A}" stroke-width="1.4"/>'
                           f'<path d="M-6 -2H6M-6 2H2" stroke="{A}" stroke-width="1.2"/>', begin=j * dur / (k + 1))
    out += f'<circle cx="{cx}" cy="{cy}" r="22" fill="{A}" fill-opacity=".18" stroke="{A}" stroke-width="1.6"/>'
    out += f'<circle cx="{cx}" cy="{cy}" r="22" stroke="{A}" class="rip"/>' + T(cx, cy + 4, "YOU", 10, P["text"], anchor="middle", ls=".1em")
    return out


def d_krama(s, P, A):
    out = f'<ellipse cx="96" cy="118" rx="88" ry="16" stroke="{P["line"]}"/>'
    out += f'<ellipse cx="96" cy="118" rx="88" ry="16" stroke="{A}" stroke-width="1.6" stroke-dasharray="8 14" class="flow" style="animation-duration:3s"/>'
    shoe = ("M18 96 C18 82 30 74 44 74 L70 58 C82 50 96 52 104 62 L120 76 C140 78 162 84 172 92 C178 97 176 106 168 108 "
            "L26 108 C20 108 18 102 18 96 Z")
    out += f'<g class="bob"><path d="{shoe}" fill="{P["panel"]}" stroke="{A}" stroke-width="2" stroke-linejoin="round"/>'
    out += f'<path d="M22 100 H172" stroke="{A}" stroke-width="1.4"/><path d="M78 64 L92 80 M88 58 L102 74" stroke="{P["mute"]}" stroke-width="1.6" stroke-linecap="round"/></g>'
    cid = s.uid("kr")
    s.defs.append(f'<clipPath id="{cid}"><rect x="214" y="0" width="218" height="140" rx="10"/></clipPath>')
    out += f'<g clip-path="url(#{cid})"><g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;-226 0;-226 0;-452 0;-452 0;-678 0;-678 0;0 0" keyTimes="0;.2;.25;.45;.5;.7;.75;.95;1" dur="12s" repeatCount="indefinite"/>'
    for i in range(4):
        x = 214 + i * 226
        out += (f'<rect x="{x}" y="0" width="218" height="140" rx="10" fill="{P["panel"]}" stroke="{P["line"]}"/>'
                + T(x + 16, 28, f"CHAPTER 0{i+1}", 10, A, ls=".16em")
                + f'<rect x="{x+16}" y="44" width="{120 + 20*i}" height="10" rx="5" fill="{P["text"]}" fill-opacity=".8"/>'
                  f'<rect x="{x+16}" y="62" width="150" height="6" rx="3" fill="{P["mute"]}" fill-opacity=".5"/>'
                  f'<rect x="{x+16}" y="74" width="110" height="6" rx="3" fill="{P["mute"]}" fill-opacity=".5"/>'
                + f'<rect x="{x+16}" y="104" width="{40+i*40}" height="4" rx="2" fill="{A}"/>')
    out += "</g></g>"
    return out


def d_niriksh(s, P, A):
    tasks = ("RESTOCK ALERT", "PRICE CHECK", "ORDER FOLLOW-UP", "REVIEW REPLY")
    out = ""
    for i, t in enumerate(tasks):
        y = i * 34
        out += f'<rect x="0" y="{y}" width="270" height="28" rx="8" fill="{P["panel"]}" stroke="{P["line"]}"/>' + T(12, y + 18, t, 10.5, P["text"], ls=".06em")
        out += (f'<g><rect x="196" y="{y+6}" width="62" height="16" rx="8" fill="{P["faint"]}"/>' + T(227, y + 17.5, "QUEUED", 8.5, P["mute"], anchor="middle")
                + f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;{.15+i*.15:.2f};{.18+i*.15:.2f};.92;1" dur="8s" repeatCount="indefinite"/></g>')
        out += (f'<g opacity="0"><rect x="196" y="{y+6}" width="62" height="16" rx="8" fill="{A}" fill-opacity=".25" stroke="{A}"/>' + T(227, y + 17.5, "DONE", 8.5, P["text"], anchor="middle")
                + f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{.15+i*.15:.2f};{.18+i*.15:.2f};.92;1" dur="8s" repeatCount="indefinite"/></g>')
    cx, cy = 360, 62
    out += f'<circle cx="{cx}" cy="{cy}" r="34" fill="{A}" fill-opacity=".12" stroke="{A}" stroke-width="1.6"/>'
    out += f'<circle cx="{cx}" cy="{cy}" r="34" stroke="{A}" class="rip" style="animation-duration:3.4s"/>'
    out += f'<path d="M{cx-14} {cy}h6l4-10 6 20 4-10h8" stroke="{A}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    out += T(cx, cy + 58, "OPS TEAMMATE", 9, P["mute"], anchor="middle", ls=".12em")
    return out


def d_skycast(s, P, A):
    sun = s.acc("waffle")
    out = f'<g class="spin" style="animation-duration:18s">'
    for i in range(12):
        a = math.radians(i * 30)
        out += f'<path d="M{70+38*math.cos(a):.1f} {62+38*math.sin(a):.1f}L{70+50*math.cos(a):.1f} {62+50*math.sin(a):.1f}" stroke="{sun}" stroke-width="3" stroke-linecap="round"/>'
    out += f'</g><circle cx="70" cy="62" r="28" fill="{sun}" class="glow"/>'
    cl = P["text"] if s.theme == "dark" else "#FFFFFF"
    out += (f'<g class="drift"><path d="M60 108a18 18 0 0 1 4-35a26 26 0 0 1 48 6a16 16 0 0 1 2 29Z" fill="{cl}" fill-opacity="{.9 if s.theme == "dark" else 1}" '
            f'stroke="{A}" stroke-width="1.5"/></g>')
    for i, (k, v) in enumerate((("TEMP", .62), ("UV", .4), ("AIR QUALITY", .78))):
        y = 12 + i * 34
        out += T(200, y + 6, k, 9.5, P["mute"], ls=".1em")
        out += f'<rect x="200" y="{y+12}" width="232" height="8" rx="4" fill="{P["faint"]}"/><rect x="200" y="{y+12}" width="{232*v:.0f}" height="8" rx="4" fill="{A}" class="grow" style="animation-delay:{i*.3}s"/>'
    out += T(200, 132, "ANY CITY · OPENWEATHERMAP", 9, P["mute"], ls=".1em")
    return out


def d_portfolio(s, P, A):
    gid = s.uid("drop")
    s.defs.append(f'<radialGradient id="{gid}" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/>'
                  f'<stop offset=".35" stop-color="{A}" stop-opacity=".55"/><stop offset="1" stop-color="{A}" stop-opacity=".12"/></radialGradient>')
    out = ""
    for i in range(3):
        out += f'<circle cx="86" cy="70" r="30" stroke="{A}" stroke-width="1.4" class="rip" style="animation-delay:-{i*.93:.2f}s;animation-duration:2.8s"/>'
    out += f'<g class="bob"><circle cx="86" cy="70" r="34" fill="url(#{gid})" stroke="{A}" stroke-width="1.2"/><ellipse cx="74" cy="56" rx="10" ry="6" fill="#fff" fill-opacity=".7" transform="rotate(-30 74 56)"/></g>'
    out += T(86, 136, "WEBGL GLASS DROP", 9, P["mute"], anchor="middle", ls=".1em")
    s.stagger("ex", 16, 10, on=.035, hold=.88)
    for i in range(16):
        x, y = 210 + (i % 4) * 56, (i // 4) * 32
        out += f'<rect class="ex{i}" x="{x}" y="{y}" width="48" height="26" rx="6" fill="{A}" fill-opacity="{.12 + (i % 5) * .08:.2f}" stroke="{A}" stroke-opacity=".6"/>'
    out += T(210, 140, "AN EXHIBITION OF 16 PROJECTS", 9, P["mute"], ls=".1em")
    return out


def d_skp(s, P, A):
    out = ""
    pos = [(i % 3 * 146, i // 3 * 70) for i in range(6)]
    for i, (x, y) in enumerate(pos):
        out += f'<rect x="{x}" y="{y}" width="134" height="60" rx="10" fill="{P["panel"]}" stroke="{P["line"]}"/>'
        out += f'<rect x="{x+12}" y="{y+14}" width="{50+i*9}" height="7" rx="3.5" fill="{P["mute"]}" fill-opacity=".6"/><rect x="{x+12}" y="{y+30}" width="80" height="5" rx="2.5" fill="{P["mute"]}" fill-opacity=".35"/>'
        kt = f"0;{i/6:.3f};{i/6+.02:.3f};{(i+1)/6:.3f};{(i+1)/6+.02:.3f};1" if i < 5 else "0;.833;.853;.98;1;1"
        out += (f'<rect x="{x}" y="{y}" width="134" height="60" rx="10" stroke="{A}" stroke-width="2" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" dur="9s" repeatCount="indefinite"/></rect>')
    path = "M" + " L".join(f"{x+100} {y+44}" for x, y in pos) + f" L{pos[0][0]+100} {pos[0][1]+44}"
    cursor = f'<path d="M0 0L0 16L4.5 12L8 19L11 17.5L7.5 11L13 11Z" fill="{P["text"]}" stroke="{P["card"]}" stroke-width="1.2"/>'
    keys = ";".join(f"{i/6:.3f}" for i in range(7))
    out += (f'<g>{cursor}<animateMotion dur="9s" repeatCount="indefinite" path="{path}" keyPoints="{";".join(f"{i/6:.3f}" for i in range(7))}" '
            f'keyTimes="{keys}" calcMode="spline" keySplines="{";".join([".6 0 .3 1"]*6)}"/></g>')
    return out


def d_noir(s, P, A):
    out = ""
    for i, x in enumerate((70, 90, 110)):
        out += (f'<path d="M{x} 50 c-10 -12 10 -20 0 -32 c-8 -10 6 -16 0 -24" stroke="{P["mute"]}" stroke-width="2.4" stroke-linecap="round" '
                f'class="steam" style="animation-delay:-{i*1.2:.1f}s"/>')
    out += (f'<path d="M44 58H136V84a40 40 0 0 1-40 40H84a40 40 0 0 1-40-40Z" fill="{A}" fill-opacity=".2" stroke="{A}" stroke-width="2.2"/>'
            f'<path d="M136 66h8a14 14 0 0 1 0 28h-10" stroke="{A}" stroke-width="2.2"/>'
            f'<ellipse cx="90" cy="132" rx="70" ry="7" stroke="{A}" stroke-width="2"/>'
            f'<ellipse cx="90" cy="60" rx="44" ry="5" fill="{A}" fill-opacity=".55"/>')
    s.stagger("nc", 3, 12, on=.12, hold=.92)
    for i, l in enumerate(("SPECIALTY", "COFFEE,", "CINEMATIC")):
        out += f'<g class="nc{i}">' + s.display(l, 206, 40 + i * 44, s.fit("SPECIALTY", 220, cap=30), P["text"] if i != 1 else A) + "</g>"
    return out


def d_waffle(s, P, A):
    out = f'<rect x="20" y="10" width="124" height="124" rx="26" fill="{A}" fill-opacity=".28" stroke="{A}" stroke-width="2.4"/>'
    for i in range(4):
        for j in range(4):
            out += f'<rect x="{32+i*26}" y="{22+j*26}" width="20" height="20" rx="5" fill="{A}" fill-opacity=".55"/>'
    out += f'<rect x="66" y="56" width="32" height="24" rx="5" fill="#FFF6D6" stroke="{A}" class="bob"/>'
    syrup = "#8A4B12" if s.theme == "light" else "#D9893A"
    for x, h, d in ((48, 60, 0), (100, 86, 1.4), (128, 44, 2.6)):
        out += f'<path d="M{x} 10V{10+h}" stroke="{syrup}" stroke-width="7" stroke-linecap="round" class="drip" style="animation-delay:-{d}s"/>'
    for i, l in enumerate(("RESTAURANT", "LANDING PAGE")):
        out += s.display(l, 180, 50 + i * 34, s.fit("LANDING PAGE", 245, cap=22), P["text"] if i == 0 else A)
    out += T(180, 120, "MENU · HOURS · RESERVE", 10, P["mute"], ls=".12em")
    return out


def d_singularity(s, P, A):
    cx, cy = 300, 70
    gid = s.uid("disk")
    s.defs.append(f'<linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{A}" stop-opacity="0"/><stop offset=".5" stop-color="{A}"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>')
    out = f'<g transform="rotate(-16 {cx} {cy})"><g class="spin" style="animation-duration:6s">'
    out += f'<ellipse cx="{cx}" cy="{cy}" rx="110" ry="30" stroke="url(#{gid})" stroke-width="6"/></g>'
    out += f'<ellipse cx="{cx}" cy="{cy}" rx="140" ry="40" stroke="{A}" stroke-opacity=".35" stroke-dasharray="2 8" class="flow"/></g>'
    out += f'<circle cx="{cx}" cy="{cy}" r="30" fill="{P["night"]}" stroke="{A}" stroke-width="1.5"/>'
    out += f'<rect x="0" y="4" width="180" height="132" rx="16" fill="{P["glass"]}" fill-opacity=".07" stroke="{A}" stroke-opacity=".6"/>'
    out += T(16, 28, "SIGN IN", 10, A, ls=".16em")
    for i in range(2):
        out += f'<rect x="16" y="{40+i*32}" width="148" height="24" rx="8" fill="{P["panel"]}" stroke="{P["line"]}"/>'
    out += f'<rect x="26" y="46" width="1.6" height="12" fill="{P["text"]}" class="blink"/>'
    out += f'<path d="M26 84h50" stroke="{P["mute"]}" stroke-width="3" stroke-dasharray="3 5" stroke-linecap="round"/>'
    out += f'<rect x="16" y="104" width="148" height="22" rx="11" fill="{A}" class="glow"/>' + T(90, 119, "ENTER", 9.5, P["card"], anchor="middle", ls=".14em")
    return out


def d_fca(s, P, A):
    out = f'<rect x="0" y="22" width="84" height="84" rx="8" fill="{P["panel"]}" stroke="{A}" stroke-width="1.6"/>'
    for i in range(6):
        out += f'<path d="M{12+i*12} 22V12M{12+i*12} 106V116M0 {34+i*12}H-8M84 {34+i*12}H92" stroke="{P["mute"]}" stroke-width="2"/>'
    out += T(42, 62, "ESP32", 11, P["text"], anchor="middle", ls=".08em") + T(42, 80, "BENCH", 8.5, P["mute"], anchor="middle", ls=".12em")
    rnd = random.Random(8)
    for r, (lab, groups) in enumerate((("FLOAT32", ((1, s.acc("prahari"), "S"), (8, s.acc("samagra"), "EXP"), (23, A, "MANTISSA"))),
                                       ("INT32", ((32, P["mute"], "TWO'S COMPLEMENT"),)))):
        y = 18 + r * 64
        out += T(116, y, lab, 9.5, P["mute"], ls=".12em")
        x = 116
        for n, c, name in groups:
            x0 = x
            for b in range(n):
                out += (f'<rect x="{x:.1f}" y="{y+8}" width="7.4" height="20" rx="1.5" fill="{c}" opacity=".9">'
                        f'<animate attributeName="fill-opacity" values="{rnd.choice(("1;.2;1", ".2;1;.2"))}" dur="{rnd.uniform(1.2,3.2):.1f}s" repeatCount="indefinite"/></rect>')
                x += 9.9
            out += T(x0, y + 42, name, 8.5, c, ls=".06em")
    return out


def d_website(s, P, A):
    out = (f'<rect x="0" y="0" width="432" height="138" rx="12" fill="{P["panel"]}" stroke="{P["line"]}"/>'
           f'<path d="M0 26H432" stroke="{P["line"]}"/><rect x="70" y="7" width="240" height="13" rx="6.5" fill="{P["faint"]}"/>')
    for i, c in enumerate((s.acc("fca"), s.acc("waffle"), OK[s.theme])):
        out += f'<circle cx="{16+i*14}" cy="13" r="4" fill="{c}"/>'
    code = ("<!DOCTYPE html>", "<html>", "  <h1>hello, web</h1>", "</html>")
    for i, l in enumerate(code):
        cid = s.uid("ty")
        w = mono_w(l, 12) + 4
        a, b = .08 + i * .18, .2 + i * .18
        s.defs.append(f'<clipPath id="{cid}"><rect x="18" y="{38+i*22}" height="20"><animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0" keyTimes="0;{a:.2f};{b:.2f};.92;1" dur="8s" repeatCount="indefinite"/></rect></clipPath>')
        out += f'<g clip-path="url(#{cid})">' + T(20, 54 + i * 22, l, 12, A if "<h1" in l else P["text"]) + "</g>"
    out += f'<rect x="{22+mono_w(code[-1],12):.0f}" y="{42+3*22}" width="7" height="14" fill="{A}" class="blink"/>'
    return out


def d_vyom(s, P, A):
    out = stars(s, 0, 0, 432, 90, 40, 17, (0.7, 2.0))
    out += f'<circle cx="380" cy="34" r="16" fill="{A}" fill-opacity=".25" stroke="{A}" class="glow"/>'
    cid = s.uid("vy")
    s.defs.append(f'<clipPath id="{cid}"><rect x="0" y="108" width="432" height="8" rx="4"/></clipPath>')
    gid = s.uid("vg")
    s.defs.append(f'<linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{A}" stop-opacity="0"/><stop offset=".5" stop-color="{A}"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>')
    out += f'<rect x="0" y="108" width="432" height="8" rx="4" fill="{P["faint"]}"/><g clip-path="url(#{cid})"><rect x="0" y="108" width="140" height="8" fill="url(#{gid})" class="shim"/></g>'
    out += T(0, 136, "WORK IN PROGRESS", 10, P["mute"], ls=".2em")
    return out


def d_profile(s, P, A):
    code = ("for theme in THEMES:", "    s = Scene(slug, theme)", "    s.add(globe(...))", "    save(s)  # → .svg")
    out = ""
    for i, l in enumerate(code):
        out += T(0, 18 + i * 22, l, 11, A if i == 0 else P["text"])
    out += f'<path d="M210 60H250" stroke="{A}" stroke-width="2" class="flow"/><path d="M246 54l6 6-6 6" stroke="{A}" stroke-width="2"/>'
    s.stagger("pc", 6, 8, on=.08)
    for i in range(6):
        x, y = 268 + (i % 3) * 56, (i // 3) * 64
        out += (f'<g class="pc{i}"><rect x="{x}" y="{y}" width="48" height="56" rx="7" fill="{P["panel"]}" stroke="{A}" stroke-opacity=".7"/>'
                f'<circle cx="{x+24}" cy="{y+22}" r="10" stroke="{A}"/><rect x="{x+10}" y="{y+40}" width="28" height="4" rx="2" fill="{P["mute"]}"/></g>')
    return out


PROJECTS = [
    # slug, accent, title, label, chips, drawer, desc
    ("arthayukti", "artha", "ArthaYukti", "TYPESCRIPT · PYTHON", ("FASTAPI", "REACT", "TAILWIND", "GEMINI"), d_artha,
     "ArthaYukti: multi-goal financial planning under uncertainty. Goal bars fill, one goal slips and the smallest fix is found, while a trajectory draws."),
    ("prahari", "prahari", "PRAHARI", "TYPESCRIPT", ("NEXT.JS", "PRISMA", "POSTGRESQL", "DOCKER"), d_prahari,
     "PRAHARI: mine safety and compliance monitoring. A risk gauge swings and a tamper-evident audit log links block by block."),
    ("akashalens", "akasha", "AkashaLens", "PYTHON", ("PYTORCH", "SCIKIT-IMAGE", "FLASK"), d_akasha,
     "AkashaLens: a U-Net that reconstructs cloud-covered Sentinel-2 scenes. A scan line sweeps across a satellite tile and clears the clouds."),
    ("tarang", "tarang", "Tarang", "TYPESCRIPT", ("NEXT.JS", "FRAMER MOTION", "ZUSTAND"), d_tarang,
     "Tarang: a music web app. An equaliser moves, the progress bar fills, and the synced lyric line advances."),
    ("rinti-ai", "rinti", "Rinti AI", "PYTHON · TYPESCRIPT", ("FASTAPI", "NEXT.JS", "GROQ", "TAVILY"), d_rinti,
     "Rinti AI: a chat workspace with per-user memory and cited research. Chat bubbles and citation chips appear in turn."),
    ("orbit-os", "orbit", "orbit-os", "TYPESCRIPT", ("NEXT.JS", "FRAMER MOTION", "MOCK DATA"), d_orbit,
     "orbit-os: a personal dashboard that borrows from operating-system design. Widgets orbit a central hub."),
    ("krama", "krama", "Krama", "TYPESCRIPT", ("NEXT.JS", "GSAP"), d_krama,
     "Krama: a luxury sneaker marketplace told as a story. A sneaker turns on a turntable while chapters slide past."),
    ("niriksh-ai", "niriksh", "Niriksh AI", "TYPESCRIPT", ("NEXT.JS", "TYPESCRIPT"), d_niriksh,
     "Niriksh AI: an AI operations teammate for merchants. Example tasks move from queued to done."),
    ("skycast", "skycast", "SkyCast", "PYTHON", ("FLASK", "OPENWEATHERMAP"), d_skycast,
     "SkyCast: one screen of weather. A sun turns, a cloud drifts, and temperature, UV and air-quality bars fill."),
    ("sams-portfolio", "portfolio", "Sam's Portfolio", "TYPESCRIPT", ("REACT 19", "VITE", "GSAP", "WEBGL", "WEB AUDIO"), d_portfolio,
     "Sam's Portfolio: a WebGL glass-drop homepage and an exhibition of 16 projects. A glass drop ripples while sixteen tiles light up."),
    ("samudra-kar-portfolio", "skp", "samudra-kar-portfolio", "TYPESCRIPT", ("INTERACTIVE", "EARLIER PORTFOLIO"), d_skp,
     "samudra-kar-portfolio: an earlier interactive developer portfolio. A cursor visits each card in a grid."),
    ("noir-cafe", "noir", "noir-cafe", "TYPESCRIPT", ("NEXT.JS", "TAILWIND", "FRAMER MOTION", "LENIS"), d_noir,
     "noir-cafe: a cinematic specialty-coffee site. Steam rises from a cup."),
    ("the-waffle-house", "waffle", "the-waffle-house", "TYPESCRIPT", ("LANDING PAGE", "ANIMATED"), d_waffle,
     "the-waffle-house: a restaurant landing page. Syrup drips down a waffle."),
    ("singularity-login", "singularity", "singularity-login", "TYPESCRIPT", ("NEXT.JS", "TAILWIND", "GLASSMORPHISM"), d_singularity,
     "singularity-login: a glassmorphism sign-in UI. An accretion disk turns behind a glass sign-in card with a blinking caret."),
    ("speed-of-numbers-fca", "fca", "speed-of-numbers-fca", "ARDUINO · TEX", ("ESP32", "NUMERIC REPRESENTATION", "TEAM LAB"), d_fca,
     "speed-of-numbers-fca: a team lab on numeric representation and execution speed on the ESP32. Bits flicker in float32 and int32 layouts."),
    ("website", "website", "website", "HTML", ("EARLY EXPERIMENT",), d_website,
     "website: an early website experiment. HTML types itself into a browser window."),
    ("vyom", "vyom", "vyom", "IN PROGRESS", ("WORK IN PROGRESS",), d_vyom,
     "vyom: work in progress. Stars twinkle above a progress shimmer."),
    ("samudra-github", "profile", "Samudra-GITHub", "PYTHON", ("THIS README", "SVG GENERATOR"), d_profile,
     "Samudra-GITHub: this profile README and the generator behind its artwork. Code on the left produces cards on the right."),
]


def ai_workflow(th):
    s = Scene("ai-workflow", 1000, 300, th, "Engineering with AI",
              "Engineering with AI: Samudra directs two AI engineering agents. Claude Code works on UI, UX, design tokens and docs; "
              "Antigravity on boot, memory, interrupts, scheduler and drivers. Both share one repository of docs, API contracts, "
              "handoff notes and commits, and a review, run, accept or reject loop returns to Samudra.")
    P, A, B = s.P, s.acc("ai"), s.acc("wed")
    s.frame(A, 22)
    nodes = {"me": (500, 66, "SAMUDRA", "architecture · direction · validation", P["text"]),
             "cc": (230, 160, "CLAUDE CODE", "UI · UX · design tokens · docs", A),
             "ag": (760, 160, "ANTIGRAVITY", "boot · memory · interrupts · scheduler · drivers", B),
             "repo": (500, 236, "SHARED REPOSITORY", "docs · API contracts · handoff notes · commits", OK[th])}
    links = (("me", "cc"), ("me", "ag"), ("cc", "repo"), ("ag", "repo"))
    for a, b in links:
        (x1, y1, *_), (x2, y2, *_) = nodes[a], nodes[b]
        d = f"M{x1} {y1} C{x1} {(y1+y2)/2} {x2} {(y1+y2)/2} {x2} {y2}"
        s.add(f'<path d="{d}" stroke="{P["line"]}" stroke-width="1.6"/><path d="{d}" stroke="{nodes[b][4] if b != "repo" else nodes[a][4]}" stroke-width="1.6" class="flow"/>')
        s.add(orbiter(d, 3.2, f'<circle r="4" fill="{nodes[b][4] if b != "repo" else nodes[a][4]}"/>', begin=hash(a + b) % 3))
    loop = "M680 236 C960 236 960 66 640 66"
    s.add(f'<path d="{loop}" stroke="{P["mute"]}" stroke-width="1.2" stroke-dasharray="4 6"/>')
    s.add(orbiter(loop, 5, f'<circle r="3.5" fill="{P["text"]}"/>'))
    s.add(T(942, 280, "REVIEW · RUN · ACCEPT / REJECT  ↺", 10, P["mute"], anchor="end", ls=".1em"))
    for k, (x, y, h, sub, c) in nodes.items():
        w = max(mono_w(sub, 10.5), mono_w(h, 13)) + 40
        s.add(f'<rect x="{x-w/2:.0f}" y="{y-26}" width="{w:.0f}" height="52" rx="14" fill="{P["panel"]}" stroke="{c}" stroke-width="1.5"/>')
        s.add(T(x, y - 4, h, 13, P["text"], anchor="middle", ls=".08em") + T(x, y + 15, sub, 10.5, P["mute"], anchor="middle"))
    s.add(T(40, 40, "AI AGENTS, NOT PEOPLE", 10, A, ls=".18em"))
    return s


def stack(th):
    rows = (("LANGUAGES", ("TypeScript", "JavaScript", "Python", "C", "x86-64 Assembly")),
            ("SYSTEMS", ("Clang", "LLD", "NASM", "QEMU", "Git", "Docker")),
            ("WEB", ("React", "Next.js", "Tailwind", "Framer Motion", "GSAP", "Three.js", "CesiumJS")),
            ("AI / VISION", ("PyTorch", "NumPy", "SciPy", "scikit-image", "LLM APIs", "Ollama")),
            ("DESIGN", ("Figma", "Design Systems", "Motion Design")))
    alt = "Stack. " + ". ".join(f"{k.title()}: {', '.join(v)}" for k, v in rows) + "."
    s = Scene("stack", 1000, 290, th, "Stack", alt)
    P, A = s.P, s.acc("wed")
    s.frame(A, 22)
    s.seq("sk", 5, 10, fade=1.5)
    for i, (k, items) in enumerate(rows):
        y = 34 + i * 48
        s.add(f'<g class="sk{i}"><rect x="24" y="{y-4}" width="952" height="40" rx="12" fill="{A}" fill-opacity=".08" stroke="{A}" stroke-opacity=".5"/></g>')
        s.add(T(44, y + 21, k, 11, A, ls=".18em"))
        s.add(pills(190, y + 4, items, P["text"], P["line"], 12, gap=10, h=24))
    return s


def closing(th):
    s = Scene("closing", 1000, 240, th, "Contact",
              "Samudra Kar. Open to internships. Bangalore, India. Chanakya University.")
    P, A = s.P, s.acc("wed")
    s.frame(A, 24)
    s.add(stars(s, 20, 20, 960, 200, 50, 41))
    s.add(globe(s, 860, 120, 76, A, period=30, n=10, points=((13, 77.6 - 90, OK[th]),)))
    s.add(s.display("LET'S BUILD", 48, 104, 54, P["text"], rise=0.2))
    s.add(s.display("SOMETHING REAL.", 48, 162, 54, A, rise=0.6))
    s.add(pill(48, 186, "OPEN TO INTERNSHIPS", P["text"], OK[th], 11, dot=OK[th])[0])
    s.add(T(256, 203, "BANGALORE, INDIA  ·  CHANAKYA UNIVERSITY", 11, P["mute"], ls=".12em"))
    return s


def main():
    both(hero)
    for i, (k, lab, acc) in enumerate((("flagship", "FLAGSHIP", "wed"), ("samagra", "ALSO BUILDING", "samagra"),
                                       ("projects", "ALL PROJECTS", "orbit"), ("ai", "ENGINEERING WITH AI", "ai"),
                                       ("stack", "STACK", "wed"), ("contact", "CONTACT", "profile")), 1):
        both(lambda th, k=k, i=i, lab=lab, acc=acc: section(th, k, i, lab, acc))
    for fn in (wed_hero, wed_moon, wed_pipeline, wed_modes, samagra, ai_workflow, stack, closing):
        both(fn)
    for idx, (slug, key, title, lang, chips, draw, desc) in enumerate(PROJECTS, 2):
        both(lambda th, *a: card(th, slug, key, idx, title, lang, chips, draw, desc))
    n = len(list(OUT.rglob("*.svg")))
    print(f"wrote {n} SVGs to {OUT}")


if __name__ == "__main__":
    sys.exit(main())
