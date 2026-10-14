#!/usr/bin/env python3
"""Generates every SVG in assets/profile/ and validates them.

    python tools/build_profile_assets.py

Design system, taken from the live portfolio (sam-sportfolio.vercel.app)
  palette  paper #FDF9F1, ink #111215, lime #D8F827 (the portfolio's signature),
           cobalt #1E3AE8, vermilion #FF5226, sand #EBE5D8, plus chrome yellow
           #FFD400 for the README's warm, glossy moments
  type     Syne ExtraBold (the portfolio's display face) drawn as outlined paths from
           tools/fonts/syne-800.json, so it renders identically everywhere; system mono
           for labels; system sans for running text
  forms    2.5px ink borders, hard offset shadows, dot and line grids, outlined numerals,
           "WORLD 0N OF 06" labels, mono tag chips, a single full-bleed colour per world
  motion   CSS keyframes + SMIL only. No scripts, no external resources.
           The non-animated base state of every scene is a complete composition.
Nothing here is live telemetry; every status, score and trace is illustrative and
labelled as such inside the artwork.
"""
import json
import math
import pathlib
import re
import sys
import xml.dom.minidom
from xml.sax.saxutils import escape

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "assets" / "profile"
FONT = json.loads((HERE / "fonts" / "syne-800.json").read_text(encoding="utf-8"))
UPM, CAP = FONT["upm"], FONT["capHeight"]
W = 1000

PAPER, PAPER2, SAND = "#FDF9F1", "#F4F0E8", "#EBE5D8"
INK = "#111215"
LIME, YEL, GOLD = "#D8F827", "#FFD400", "#F2B900"
COBALT, VERM, CORAL = "#1E3AE8", "#FF5226", "#FF6347"

BASE_CSS = """
.m{font-family:ui-monospace,"JetBrains Mono",SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;font-weight:700}
.s{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-weight:800}
.fb{transform-box:fill-box;transform-origin:center}
.rise{animation:rise 12s cubic-bezier(.16,1,.3,1) infinite both}
@keyframes rise{0%{transform:translateY(150px)}7%,88%{transform:translateY(0)}95%,100%{transform:translateY(150px)}}
.flow{stroke-dasharray:4 8;animation:flow 1.4s linear infinite}
@keyframes flow{to{stroke-dashoffset:-24}}
.bob{animation:bob 5s ease-in-out infinite alternate}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(-9px)}}
.spin{animation:spin 40s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def e(s):
    return escape(s, {'"': "&quot;"})


class Scene:
    def __init__(self, pid, h, bg, title, desc):
        self.pid, self.h, self.bg, self.title, self.desc = pid, h, bg, title, desc
        self.parts, self.defs, self.css, self.glyphs = [], [], "", set()

    def add(self, s):
        self.parts.append(s)

    # ---- display type (Syne paths) ---------------------------------------------
    def tw(self, s, size, ls=0.0):
        return sum(FONT["glyphs"].get(c, {"adv": 600})["adv"] for c in s) * size / UPM + ls * size * len(s)

    def fit(self, s, width, ls=0.0):
        return width / self.tw(s, 1.0, ls)

    def display(self, s, x, y, size, fill=INK, stroke=None, sw=0, ls=0.0, anchor="start", rise=None):
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
                use = f'<use href="#{self.pid}-g{ord(c)}" transform="translate({cx:.1f} {y:.1f}) scale({k:.4f})"/>'
                if rise is not None:
                    use = f'<g class="rise" style="animation-delay:{rise + i * 0.045:.2f}s">{use}</g>'
                out += use
            cx += g["adv"] * k + ls * size
        attrs = f'fill="{fill}"'
        if stroke:
            attrs += f' stroke="{stroke}" stroke-width="{sw / k:.1f}" stroke-linejoin="round"'
        if rise is not None:
            cid = f"{self.pid}-c{len(self.defs)}"
            top, bot = y - CAP * k - size * 0.12, y + size * 0.16
            self.defs.append(f'<clipPath id="{cid}"><rect x="{x-8:.1f}" y="{top:.1f}" width="{width+16:.1f}" height="{bot-top:.1f}"/></clipPath>')
            return f'<g clip-path="url(#{cid})"><g {attrs}>{out}</g></g>'
        return f'<g {attrs}>{out}</g>'

    def render(self):
        gdefs = "".join(f'<path id="{self.pid}-g{ord(c)}" d="{FONT["glyphs"][c]["d"]}"/>' for c in sorted(self.glyphs))
        h, pid = self.h, self.pid
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-labelledby="{pid}-t {pid}-d">
<title id="{pid}-t">{e(self.title)}</title>
<desc id="{pid}-d">{e(self.desc)}</desc>
<defs>
{gdefs}
<pattern id="{pid}-dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="14" cy="14" r="1.7" fill="{INK}" fill-opacity=".22"/></pattern>
<pattern id="{pid}-lines" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{INK}" stroke-opacity=".12" stroke-width="1"/></pattern>
<pattern id="{pid}-linesl" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#FFFFFF" stroke-opacity=".22" stroke-width="1"/></pattern>
<linearGradient id="{pid}-chrome" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF7B0"/><stop offset=".3" stop-color="{YEL}"/><stop offset=".62" stop-color="{GOLD}"/><stop offset="1" stop-color="#FFE45C"/></linearGradient>
<radialGradient id="{pid}-ball" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFFBD0"/><stop offset=".35" stop-color="{YEL}"/><stop offset="1" stop-color="{GOLD}"/></radialGradient>
{''.join(self.defs)}
</defs>
<style>{BASE_CSS}{self.css}</style>
<rect width="{W}" height="{h}" fill="{self.bg}"/>
{''.join(self.parts)}
<rect x="1.25" y="1.25" width="{W-2.5}" height="{h-2.5}" fill="none" stroke="{INK}" stroke-width="2.5"/>
</svg>
"""


# ------------------------------------------------------------------ primitives
def card(x, y, w, h, fill=PAPER, sh=6, sw=2.5, shc=INK, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x+sh}" y="{y+sh}" width="{w}" height="{h}" rx="{rx}" fill="{shc}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"{d}/>')


def tag(x, y, text, fill=PAPER, color=INK, size=12, dot=None, h=26):
    w = int(len(text) * size * 0.62 + 20 + (14 if dot else 0))
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
    tx = x + 10
    if dot:
        s += f'<circle cx="{x+15}" cy="{y+h/2}" r="4" fill="{dot}" stroke="{INK}" stroke-width="1.5"/>'
        tx += 14
    s += f'<text class="m" x="{tx}" y="{y+h/2+size*0.36}" font-size="{size}" fill="{color}">{e(text)}</text>'
    return s, w


def world(sc, n, color=PAPER, bg=INK):
    s, w = tag(32, 24, f"WORLD 0{n} OF 06", fill=bg, color=color, size=12)
    sc.add(s)
    return w


def pulse(path, dur, begin, color, r=5, stroke=INK):
    return (f'<circle r="{r}" fill="{color}" stroke="{stroke}" stroke-width="1.8" opacity="0">'
            f'<animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="{path}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></circle>')


def note(sc, text, y=None, color=INK, x=32):
    sc.add(f'<text class="m" x="{x}" y="{y or sc.h - 20}" font-size="11" fill="{color}" fill-opacity=".75">{e(text)}</text>')


# ------------------------------------------------------------------ 00 hero
def about():
    sc = Scene("ab", 640, PAPER, "Samudra Kar",
               "SAMUDRA KAR. Computer Science engineering student building across systems, AI and product, from first principles. A chrome-yellow disc with a 64-bit CPU outline, tilted project cards for Tarang, Rinti AI and AkashaLens, and a running strip of boot instructions. Bangalore, India. Open to internships.")
    sc.css = """
.fan1{animation:fan1 8s ease-in-out infinite alternate}
.fan2{animation:fan2 8s ease-in-out infinite alternate}
.fan3{animation:fan3 8s ease-in-out infinite alternate}
@keyframes fan1{from{transform:rotate(-9deg)}to{transform:rotate(-13deg)}}
@keyframes fan2{from{transform:rotate(-2deg)}to{transform:rotate(2deg)}}
@keyframes fan3{from{transform:rotate(6deg)}to{transform:rotate(10deg)}}
.orb{transform-origin:770px 270px;animation:spin 18s linear infinite}
.orb2{transform-origin:770px 270px;animation:spin 29s linear infinite reverse}
.ping{animation:ping 2.4s ease-out infinite}
@keyframes ping{0%{transform:scale(.4);opacity:.9}100%{transform:scale(2.6);opacity:0}}
.mqa{animation:mqa 30s linear infinite}
@keyframes mqa{to{transform:translateX(-700px)}}
"""
    sc.add(f'<rect width="{W}" height="640" fill="url(#ab-dots)"/>')
    sc.add(f'<rect x="0" y="0" width="{W}" height="66" fill="{PAPER}"/><path d="M0 66H{W}" stroke="{INK}" stroke-width="2.5"/>')
    sc.add(sc.display("samudra.kar", 32, 44, 26))
    sc.add(sc.display("()", 32 + sc.tw("samudra.kar", 26), 44, 26, fill=COBALT))
    t, _ = tag(392, 20, "AVAILABLE FOR INTERNSHIPS", fill=SAND, size=12, dot=LIME, h=28)
    sc.add(t)
    sc.add(f'<circle class="ping fb" cx="407" cy="34" r="4" fill="none" stroke="{INK}"/>')
    sc.add(card(824, 18, 142, 30, PAPER, sh=3, sw=2))
    sc.add(f'<text class="m" x="895" y="38" font-size="12" fill="{INK}" text-anchor="middle">BANGALORE · IN</text>')
    # tilted project cards (callback to the portfolio hero)
    for cls, x, y, fill, n, name, dot in [("fan1", 36, 122, LIME, "01", "TARANG", VERM), ("fan2", 150, 112, COBALT, "02", "RINTI AI", LIME), ("fan3", 264, 124, INK, "03", "AKASHALENS", LIME)]:
        tc = PAPER if fill != LIME else INK
        sc.add(f'<g class="{cls}" style="transform-box:fill-box;transform-origin:50% 100%">'
               + card(x, y, 180, 138, fill, sh=5)
               + f'<circle cx="{x+128}" cy="{y+52}" r="26" fill="{dot}" stroke="{INK}" stroke-width="2.5"/>'
               + f'<text class="m" x="{x+14}" y="{y+26}" font-size="12" fill="{tc}">{n}</text>'
               + f'<text class="m" x="{x+14}" y="{y+124}" font-size="15" fill="{tc}">{name}</text></g>')
    # disc
    sc.add('<g class="bob">')
    sc.add(f'<circle cx="780" cy="280" r="160" fill="{INK}"/>')
    sc.add(f'<circle cx="770" cy="270" r="160" fill="url(#ab-chrome)" stroke="{INK}" stroke-width="3"/>')
    sc.add(f'<path d="M650 190A150 150 0 0 1 790 125" fill="none" stroke="#FFFFFF" stroke-opacity=".75" stroke-width="10" stroke-linecap="round"/>')
    sc.add(f'<path d="M868 380A150 150 0 0 1 700 410" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round" opacity=".6"/>')
    sc.add(f'<rect x="716" y="216" width="108" height="108" rx="10" fill="{PAPER}" stroke="{INK}" stroke-width="3"/>')
    for i in range(5):
        o = 730 + i * 20
        sc.add(f'<path d="M{o} 216V202M{o} 324V338M716 {o-14}H702M824 {o-14}H838" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    sc.add(sc.display("x86", 770, 266, 30, anchor="middle"))
    sc.add(f'<text class="m" x="770" y="292" font-size="12" fill="{INK}" text-anchor="middle">64-BIT</text>')
    sc.add('</g>')
    sc.add(f'<circle cx="770" cy="270" r="196" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="3 9"/>')
    sc.add(f'<g class="orb"><circle cx="966" cy="270" r="11" fill="{COBALT}" stroke="{INK}" stroke-width="2.5"/></g>')
    sc.add(f'<g class="orb2"><circle cx="574" cy="270" r="8" fill="{VERM}" stroke="{INK}" stroke-width="2.5"/></g>')
    # headline
    size = sc.fit("SAMUDRA", 936)
    sc.add(sc.display("SAMUDRA", 32, 456, size, rise=0.1))
    ky = 456 + CAP * size / UPM + 26
    sc.add(sc.display("KAR", 32, ky, size, rise=0.5))
    sc.add(sc.display(".", 32 + sc.tw("KAR", size), ky, size, fill=COBALT, rise=0.7))
    dx = 32 + sc.tw("KAR.", size) + 36
    sc.add(f'<text class="m" x="{dx}" y="{ky-74}" font-size="12.5" fill="{INK}">COMPUTER SCIENCE ENGINEERING STUDENT</text>')
    sc.add(f'<g class="rise" style="animation-delay:.9s"><text class="s" x="{dx}" y="{ky-44}" font-size="26" fill="{INK}">Systems. AI. Product.</text></g>')
    sc.add(f'<text class="m" x="{dx}" y="{ky-14}" font-size="13" fill="{COBALT}">$ build --from-first-principles<tspan class="blink">_</tspan></text>')
    # ticker
    ty = 590
    sc.add(f'<rect x="0" y="{ty}" width="{W}" height="50" fill="{INK}"/>')
    seq = "mov cr3, rax  //  or eax, 1 &lt;&lt; 5  //  wrmsr ; EFER.LME  //  jmp 0x08:long_mode  //  call kernel_main  //  "
    sc.add(f'<g class="mqa"><text class="m" x="20" y="{ty+31}" font-size="16" fill="{LIME}">{seq*3}</text></g>')
    sc.add(f'<rect x="{W-196}" y="{ty+2}" width="194" height="46" fill="{INK}"/><text class="m" x="{W-24}" y="{ty+30}" font-size="11" fill="{PAPER}" fill-opacity=".75" text-anchor="end">ILLUSTRATIVE BOOT FLOW</text>')
    return sc


# ------------------------------------------------------------------ 01 Samagra OS
def samagra():
    sc = Scene("so", 700, PAPER, "Samagra OS",
               "Samagra OS: an illustrated kernel laboratory. A memory map with a user region, kernel image, page tables, physical page bitmap and VGA buffer; privilege rings with system calls crossing between Ring 3 and Ring 0 and a timer interrupt; and a round-robin scheduler across kernel tasks and a user process. Boot, memory, interrupts and scheduling are implemented in QEMU; user mode and a RAM-only filesystem are early; kernel heap, networking, persistent storage, security hardening and a native desktop are planned.")
    sc.css = """
.cur{animation:cur 6s ease-in-out infinite alternate}
@keyframes cur{from{transform:translateY(0)}to{transform:translateY(190px)}}
.sl{animation:sl 6s steps(1) infinite}
@keyframes sl{0%,16.6%{opacity:1}16.7%,100%{opacity:.28}}
.ph{animation:ph 6s linear infinite}
@keyframes ph{from{transform:translateX(0)}to{transform:translateX(180px)}}
.shock{transform-box:fill-box;transform-origin:center;animation:shock 1.8s ease-out infinite}
@keyframes shock{0%{transform:scale(.3);opacity:.9}100%{transform:scale(2);opacity:0}}
.cg{animation:cg 9s ease-in-out infinite}
@keyframes cg{0%,14%,100%{transform:translateY(0)}6%{transform:translateY(-4px)}}
"""
    world(sc, 1)
    t, _ = tag(190, 24, "FLAGSHIP", fill=LIME, size=12)
    sc.add(t)
    t, w = tag(W - 32 - 196, 24, "EARLY DEVELOPMENT", fill=CORAL, size=12, dot=PAPER)
    sc.add(t)
    sz = sc.fit("SAMAGRA OS", 700)
    sc.add(sc.display("SAMAGRA OS", 32, 148, sz, rise=0.1))
    sc.add(f'<text class="m" x="34" y="184" font-size="13" fill="{INK}">A REAL X86-64 OPERATING SYSTEM, BUILT FROM FIRST PRINCIPLES · C + NASM · QEMU</text>')
    by, bh = 212, 300
    sc.add(f'<rect x="0" y="{by}" width="{W}" height="{bh}" fill="url(#so-chrome)"/><rect x="0" y="{by}" width="{W}" height="{bh}" fill="url(#so-lines)"/>')
    sc.add(f'<path d="M0 {by}H{W}M0 {by+bh}H{W}" stroke="{INK}" stroke-width="2.5"/>')
    x0, y0 = 32, by + 26
    sc.add(card(x0, y0, 260, 252, PAPER, sh=6))
    sc.add(f'<text class="m" x="{x0+14}" y="{y0+22}" font-size="11" fill="{INK}">01 · ADDRESS SPACE</text>')
    segs = [("USER · PER PROCESS", "RING 3 · EARLY", PAPER, 46, True), ("KERNEL IMAGE", "RING 0 · C + NASM", INK, 38, False),
            ("PAGE TABLES", "4-LEVEL PAGING", YEL, 38, False), ("PMM BITMAP", "PHYSICAL PAGES", PAPER2, 38, False), ("VGA TEXT BUFFER", "0xB8000", LIME, 34, False)]
    y = y0 + 34
    for nm, sub, fill, h, early in segs:
        tc = YEL if fill == INK else INK
        dash = ' stroke-dasharray="6 4"' if early else ""
        sc.add(f'<rect x="{x0+14}" y="{y}" width="232" height="{h}" fill="{fill}" stroke="{CORAL if early else INK}" stroke-width="2.5"{dash}/>')
        sc.add(f'<text class="m" x="{x0+24}" y="{y+h/2-1}" font-size="12" fill="{tc}">{nm}</text><text class="m" x="{x0+24}" y="{y+h/2+13}" font-size="10" fill="{tc}" fill-opacity=".75">{sub}</text>')
        y += h + 6
    sc.add(f'<g class="cur"><rect x="{x0+8}" y="{y0+36}" width="244" height="4" fill="{COBALT}"/><rect x="{x0+8}" y="{y0+36}" width="244" height="18" fill="{COBALT}" fill-opacity=".14"/></g>')
    rx0 = 330
    sc.add(card(rx0, y0, 340, 252, PAPER, sh=6))
    sc.add(f'<text class="m" x="{rx0+14}" y="{y0+22}" font-size="11" fill="{INK}">02 · PRIVILEGE RINGS + INTERRUPTS</text>')
    cx, cy = rx0 + 190, y0 + 140
    sc.add(f'<circle cx="{cx}" cy="{cy}" r="96" fill="{PAPER2}" stroke="{CORAL}" stroke-width="3" stroke-dasharray="7 5"/>')
    sc.add(f'<circle cx="{cx}" cy="{cy}" r="56" fill="{INK}"/>')
    sc.add(f'<text class="m" x="{cx}" y="{cy-2}" font-size="13" fill="{YEL}" text-anchor="middle">RING 0</text><text class="m" x="{cx}" y="{cy+15}" font-size="10" fill="{PAPER}" text-anchor="middle">KERNEL</text>')
    sc.add(f'<text class="m" x="{cx}" y="{cy-104}" font-size="11" fill="{CORAL}" text-anchor="middle">RING 3 · USER · EARLY</text>')
    pin = f"M{cx-70} {cy-66} C{cx-60} {cy-40} {cx-40} {cy-34} {cx-22} {cy-30}"
    pout = f"M{cx+22} {cy-34} C{cx+44} {cy-40} {cx+62} {cy-52} {cx+70} {cy-70}"
    sc.add(f'<path class="flow" d="{pin}" fill="none" stroke="{COBALT}" stroke-width="4"/><path class="flow" d="{pout}" fill="none" stroke="{COBALT}" stroke-width="4"/>')
    sc.add(pulse(pin, 2.4, 0, COBALT, 5) + pulse(pout, 2.4, 1.2, YEL, 5))
    sc.add(f'<text class="m" x="{cx+78}" y="{cy-52}" font-size="11" fill="{COBALT}">12 SYSCALLS</text>')
    ix, iy = rx0 + 36, cy + 24
    sc.add(f'<circle class="shock" cx="{ix}" cy="{iy}" r="16" fill="none" stroke="{VERM}" stroke-width="3"/>')
    sc.add(f'<circle cx="{ix}" cy="{iy}" r="7" fill="{VERM}" stroke="{INK}" stroke-width="2.5"/><text class="m" x="{ix-12}" y="{iy+30}" font-size="11" fill="{INK}">IRQ0</text>')
    sc.add(f'<path class="flow" d="M{ix+9} {iy}L{cx-55} {cy+8}" stroke="{VERM}" stroke-width="3.5" fill="none"/>' + pulse(f"M{ix+9} {iy}L{cx-55} {cy+8}", 1.8, 0, VERM, 4.5))
    sc.add(f'<text class="m" x="{rx0+14}" y="{y0+244}" font-size="10" fill="{INK}" fill-opacity=".7">PIC REMAPPED 0x20 / 0x28 · PIT 100 Hz</text>')
    sx0 = 708
    sc.add(card(sx0, y0, 260, 252, INK, sh=6, shc=PAPER))
    sc.add(f'<text class="m" x="{sx0+14}" y="{y0+22}" font-size="11" fill="{YEL}">03 · SCHEDULER</text>')
    lx, sw = sx0 + 70, 30
    sc.add(f'<text class="m" x="{sx0+14}" y="{y0+54}" font-size="10" fill="{PAPER}" fill-opacity=".7">IRQ0</text>')
    for i in range(7):
        sc.add(f'<path d="M{lx+i*sw} {y0+42}v14" stroke="{VERM}" stroke-width="3"/>')
    for n, (nm, col) in enumerate([("KERNEL A", LIME), ("KERNEL B", YEL), ("USER", CORAL)]):
        ly = y0 + 72 + n * 46
        sc.add(f'<text class="m" x="{sx0+14}" y="{ly+22}" font-size="9.5" fill="{PAPER}">{nm}</text>')
        sc.add(f'<rect x="{lx}" y="{ly}" width="{sw*6}" height="34" fill="#23252B" stroke="{PAPER}" stroke-opacity=".25"/>')
        for k in range(6):
            if k % 3 == n:
                sc.add(f'<rect class="sl" style="animation-delay:{-(6-k)}s" x="{lx+k*sw+2}" y="{ly+3}" width="{sw-4}" height="28" fill="{col}"/>')
    sc.add(f'<g class="ph"><rect x="{lx}" y="{y0+62}" width="3" height="148" fill="{PAPER}"/></g>')
    sc.add(f'<text class="m" x="{sx0+14}" y="{y0+236}" font-size="11" fill="{PAPER}">PREEMPTIVE ROUND-ROBIN</text>')
    sc.add(f'<text class="m" x="32" y="{by+bh+34}" font-size="11" fill="{INK}">IMPLEMENTED · OBSERVED IN QEMU</text>')
    row1 = [("LONG-MODE BOOT", "ok"), ("PMM", "ok"), ("VMM", "ok"), ("IDT + EXCEPTIONS", "ok"), ("PIC + PIT", "ok"), ("SCHEDULER", "ok"), ("USER MODE", "early"), ("RAM FILESYSTEM", "early")]
    x = 32
    for i, (t, k) in enumerate(row1):
        w = int(len(t) * 7.0 + 42)
        yy = by + bh + 44
        sc.add(f'<g class="cg" style="animation-delay:{i*.5}s"><rect x="{x}" y="{yy}" width="{w}" height="28" rx="14" fill="{PAPER if k=="ok" else SAND}" stroke="{INK}" stroke-width="2"/>'
               f'<circle cx="{x+15}" cy="{yy+14}" r="5" fill="{YEL if k=="ok" else CORAL}" stroke="{INK}" stroke-width="1.8"/>'
               f'<text class="m" x="{x+28}" y="{yy+19}" font-size="11" fill="{INK}">{t}</text></g>')
        x += w + 8
    sc.add(f'<text class="m" x="32" y="{by+bh+100}" font-size="11" fill="{INK}">PLANNED · NOT IMPLEMENTED</text>')
    x = 32
    for t in ["KERNEL HEAP", "NETWORKING", "PERSISTENT STORAGE", "SECURITY HARDENING", "NATIVE DESKTOP"]:
        w = int(len(t) * 7.0 + 30)
        sc.add(f'<rect x="{x}" y="{by+bh+110}" width="{w}" height="28" rx="14" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/><text class="m" x="{x+15}" y="{by+bh+129}" font-size="11" fill="{INK}" fill-opacity=".75">{t}</text>')
        x += w + 8
    note(sc, "Illustrated from the project's documented design. Not live telemetry.", y=682)
    return sc


# ------------------------------------------------------------------ 02 PRAHARI
def prahari():
    sc = Scene("pr", 640, VERM, "PRAHARI",
               "PRAHARI: mine safety and compliance monitoring. A chain of audit blocks, each hash linked to the previous one, verified in sequence; an explainable risk score between 0 and 1 with its contributing factors and an alert threshold at 0.8; and a copilot flow where questions are parsed deterministically, answered from role-scoped database retrieval inside a permission boundary, and only then narrated by an LLM. Built for the Smart India Hackathon.")
    sc.css = """
.vf{animation:vf 10s ease-in-out infinite both}
@keyframes vf{0%{opacity:.18}6%{opacity:1}80%{opacity:1}92%,100%{opacity:.18}}
.nd{animation:nd 7s ease-in-out infinite alternate}
@keyframes nd{from{transform:rotate(-22deg)}to{transform:rotate(26deg)}}
.bp{animation:bp 2.6s ease-in-out infinite}
@keyframes bp{0%,100%{stroke-opacity:.5}50%{stroke-opacity:1}}
"""
    sc.add(f'<rect width="{W}" height="640" fill="url(#pr-linesl)"/>')
    world(sc, 2)
    t, _ = tag(190, 24, "SMART INDIA HACKATHON", fill=YEL, size=12)
    sc.add(t)
    sz = sc.fit("PRAHARI", 520)
    sc.add(sc.display("PRAHARI", 32, 146, sz, rise=0.1))
    sc.add(f'<text class="m" x="34" y="182" font-size="13" fill="{INK}">MINE SAFETY AND COMPLIANCE MONITORING · EXPLAINABLE · TRACEABLE</text>')
    hs = ["a3f9", "9c1e", "e04b", "57d2", "b81a", "4c6d"]
    acts = ["INSPECTION", "VIOLATION", "ALERT", "REPORT", "RISK SCORE"]
    for i in range(5):
        x, y = 32 + i * 192, 214
        sc.add(card(x, y, 152, 112, PAPER, sh=6))
        sc.add(f'<text class="m" x="{x+12}" y="{y+22}" font-size="11" fill="{INK}">BLOCK 0{i+1}</text>')
        sc.add(f'<text class="m" x="{x+12}" y="{y+52}" font-size="14" fill="{INK}">hash {hs[i+1]}…</text><text class="m" x="{x+12}" y="{y+72}" font-size="13" fill="{INK}" fill-opacity=".5">prev {hs[i]}…</text>')
        sc.add(f'<rect x="{x+12}" y="{y+84}" width="{len(acts[i])*6.4+14:.0f}" height="20" fill="{LIME if i%2==0 else YEL}" stroke="{INK}" stroke-width="2"/><text class="m" x="{x+19}" y="{y+98}" font-size="10" fill="{INK}">{acts[i]}</text>')
        sc.add(f'<g class="vf" style="animation-delay:{i*1.4:.1f}s"><circle cx="{x+126}" cy="{y+24}" r="12" fill="{YEL}" stroke="{INK}" stroke-width="2.5"/><path d="M{x+120} {y+24}l5 5 9-10" fill="none" stroke="{INK}" stroke-width="3"/></g>')
        if i < 4:
            sc.add(f'<path d="M{x+158} {y+56}H{x+192}" stroke="{INK}" stroke-width="4"/><path d="M{x+184} {y+48}l9 8-9 8" fill="none" stroke="{INK}" stroke-width="4"/>')
    sc.add(f'<path d="M32 352H{W-32}" stroke="{INK}" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round"/>' + pulse(f"M32 352H{W-32}", 7, 0, LIME, 7))
    sc.add(f'<text class="m" x="32" y="376" font-size="12" fill="{INK}">VERIFY WALKS THE HASH CHAIN · EACH ROW STORES A HASH CHAINED TO THE PREVIOUS ONE</text>')
    sc.add(f'<text class="m" x="{W-32}" y="376" font-size="10" fill="{INK}" fill-opacity=".75" text-anchor="end">ILLUSTRATIVE HASHES</text>')
    rx, ry = 32, 396
    sc.add(card(rx, ry, 450, 200, PAPER, sh=6))
    sc.add(f'<text class="m" x="{rx+14}" y="{ry+24}" font-size="11" fill="{INK}">02 · EXPLAINABLE RISK SCORE · 0 TO 1</text>')
    cx, cy = rx + 120, ry + 140
    sc.add(f'<path d="M{cx-86} {cy}A86 86 0 0 1 {cx} {cy-86}" fill="none" stroke="{YEL}" stroke-width="22"/><path d="M{cx} {cy-86}A86 86 0 0 1 {cx+62} {cy-60}" fill="none" stroke="{CORAL}" stroke-width="22"/><path d="M{cx+62} {cy-60}A86 86 0 0 1 {cx+86} {cy}" fill="none" stroke="{VERM}" stroke-width="22"/>')
    sc.add(f'<path d="M{cx-98} {cy}A98 98 0 0 1 {cx+98} {cy}M{cx-74} {cy}A74 74 0 0 1 {cx+74} {cy}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    sc.add(f'<g class="nd" style="transform-origin:{cx}px {cy}px"><path d="M{cx} {cy}L{cx} {cy-80}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/></g><circle cx="{cx}" cy="{cy}" r="9" fill="{INK}"/>')
    sc.add(f'<text class="m" x="{cx+52}" y="{cy-96}" font-size="10" fill="{INK}">ALERT AT 0.8</text><text class="m" x="{cx-96}" y="{cy+20}" font-size="10" fill="{INK}">0</text><text class="m" x="{cx+84}" y="{cy+20}" font-size="10" fill="{INK}">1</text>')
    for i, (n, v) in enumerate([("FINDINGS", .72), ("SEVERITY KEYWORDS", .55), ("COMPLIANCE SCORE", .38), ("INSPECTION STATUS", .62)]):
        yy = ry + 62 + i * 28
        sc.add(f'<text class="m" x="{rx+246}" y="{yy-6}" font-size="10" fill="{INK}">{n}</text>')
        sc.add(f'<rect x="{rx+246}" y="{yy}" width="186" height="10" fill="{SAND}" stroke="{INK}" stroke-width="1.5"/><rect x="{rx+246}" y="{yy}" width="{186*v:.0f}" height="10" fill="{YEL if i%2==0 else CORAL}" stroke="{INK}" stroke-width="1.5"/>')
    sc.add(f'<text class="m" x="{rx+14}" y="{ry+190}" font-size="10" fill="{INK}" fill-opacity=".75">ILLUSTRATIVE VALUES · SCORE IS STORED WITH ITS REASONS</text>')
    cx0 = 508
    sc.add(card(cx0, ry, 460, 200, PAPER, sh=6))
    sc.add(f'<text class="m" x="{cx0+14}" y="{ry+24}" font-size="11" fill="{INK}">03 · PERMISSION-SCOPED COPILOT</text>')
    cyy = ry + 108

    def node(x, w, t1, t2, fill=PAPER, tc=INK):
        return (f'<rect x="{x+3}" y="{cyy-27}" width="{w}" height="54" fill="{INK}"/><rect x="{x}" y="{cyy-30}" width="{w}" height="54" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
                f'<text class="m" x="{x+w/2}" y="{cyy-6}" font-size="12" fill="{tc}" text-anchor="middle">{t1}</text><text class="m" x="{x+w/2}" y="{cyy+11}" font-size="9" fill="{tc}" fill-opacity=".8" text-anchor="middle">{t2}</text>')
    sc.add(node(cx0 + 14, 66, "QUESTION", "USER ROLE", SAND))
    sc.add(node(cx0 + 102, 84, "PARSE", "DETERMINISTIC", LIME))
    sc.add(f'<rect class="bp" x="{cx0+204}" y="{cyy-62}" width="140" height="116" fill="{YEL}" fill-opacity=".35" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    sc.add(f'<rect x="{cx0+204}" y="{cyy-62}" width="86" height="18" fill="{INK}"/><text class="m" x="{cx0+212}" y="{cyy-49}" font-size="10" fill="{YEL}">RBAC SCOPE</text>')
    sc.add(node(cx0 + 214, 120, "RETRIEVE", "ROLE-VISIBLE MINES", PAPER))
    sc.add(node(cx0 + 366, 82, "LLM", "NARRATES ONLY", COBALT, PAPER))
    for a, b in [(80, 102), (186, 214), (334, 366)]:
        sc.add(f'<path class="flow" d="M{cx0+a} {cyy-3}H{cx0+b}" stroke="{INK}" stroke-width="3.5"/>')
    sc.add(pulse(f"M{cx0+80} {cyy-3}H{cx0+448}", 4.5, 0, YEL, 6))
    sc.add(f'<text class="m" x="{cx0+14}" y="{ry+190}" font-size="10" fill="{INK}" fill-opacity=".75">EVERY NUMBER IN AN ANSWER COMES FROM THE DATABASE</text>')
    note(sc, "Conceptual illustration. Hashes and scores are illustrative, not data from a deployment.", y=626)
    return sc


# ------------------------------------------------------------------ 03 AkashaLens
def akashalens():
    sc = Scene("ak", 640, YEL, "AkashaLens",
               "AkashaLens: cloud removal for Sentinel-2 satellite imagery. A tile grid where clouds drift over a block of tiles and a sweep reveals a reconstruction drawn with cobalt hatching and a dashed outline, with coral tiles marking low-confidence regions. Beside it the pipeline: Sentinel-2 imagery, a rule-based cloud mask, a U-Net, and a reconstruction with a confidence heatmap. A prototype for ISRO Hackathon 2026, trained on a tiny sample set.")
    sc.css = """
.cl{animation:cl 16s ease-in-out infinite}
@keyframes cl{0%,28%{opacity:1}40%,78%{opacity:0}90%,100%{opacity:1}}
.rc{animation:rc 16s ease-in-out infinite}
@keyframes rc{0%,28%{opacity:0}40%,78%{opacity:1}90%,100%{opacity:0}}
.sw{animation:sw 16s linear infinite}
@keyframes sw{0%,28%{transform:translateX(0);opacity:0}30%{opacity:1}40%{transform:translateX(254px);opacity:1}42%,100%{transform:translateX(254px);opacity:0}}
.dr{animation:dr 14s ease-in-out infinite alternate}
@keyframes dr{from{transform:translateX(-26px)}to{transform:translateX(30px)}}
"""
    sc.defs.append('<filter id="ak-bl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>')
    sc.defs.append(f'<pattern id="ak-ht" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0V9" stroke="{COBALT}" stroke-opacity=".8" stroke-width="2"/></pattern>')
    sc.add(f'<rect width="{W}" height="640" fill="url(#ak-lines)"/>')
    world(sc, 3)
    t, _ = tag(190, 24, "ISRO HACKATHON 2026", fill=INK, color=YEL, size=12)
    sc.add(t)
    t, _ = tag(W - 32 - 130, 24, "PROTOTYPE", fill=PAPER, size=12, dot=CORAL)
    sc.add(t)
    sz = sc.fit("AKASHALENS", 936)
    sc.add(sc.display("AKASHALENS", 32, 168, sz, rise=0.1))
    sc.add(f'<text class="m" x="34" y="206" font-size="13" fill="{INK}">CLOUD REMOVAL FOR SENTINEL-2 IMAGERY · A U-NET RECONSTRUCTION PROTOTYPE</text>')
    cols, rows = 9, 6
    x0, y0, tw, th = 48, 244, 64, 44
    pal = [["#2B6B8A", "#337A9C"], ["#2E6B3F", "#3C8450", "#477F46"], ["#7A8A33", "#98A840"], ["#8A6C48", "#A68660"], ["#4D6A4A", "#5C7C58"]]

    def terrain(c, r):
        v = math.sin(c * 0.85 + 0.6) + math.cos(r * 1.25) + math.sin((c + r) * 0.62) + 0.5 * math.cos(c * 2.1 - r)
        grp = pal[max(0, min(4, int((v + 3.0) / 6.0 * 5)))]
        return grp[(c * 7 + r * 3) % len(grp)]

    inreg = lambda c, r: 3 <= c <= 6 and 1 <= r <= 4
    sc.add(f'<rect x="{x0-4+8}" y="{y0-4+8}" width="{cols*tw+8}" height="{rows*th+8}" fill="{INK}"/>')
    sc.add(f'<rect x="{x0-4}" y="{y0-4}" width="{cols*tw+8}" height="{rows*th+8}" fill="{INK}"/>')
    cloud, recon = "", ""
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * tw, y0 + r * th
            if not inreg(c, r):
                sc.add(f'<rect x="{x}" y="{y}" width="{tw-2}" height="{th-2}" fill="{terrain(c, r)}"/>')
            else:
                d = min(c - 3, 6 - c, r - 1, 4 - r)
                heat = [0.0, 0.28, 0.55][min(d, 2)]
                recon += f'<rect x="{x}" y="{y}" width="{tw-2}" height="{th-2}" fill="{terrain(c, r)}"/><rect x="{x}" y="{y}" width="{tw-2}" height="{th-2}" fill="{CORAL}" fill-opacity="{heat}"/><rect x="{x}" y="{y}" width="{tw-2}" height="{th-2}" fill="url(#ak-ht)"/>'
                cloud += f'<rect x="{x}" y="{y}" width="{tw-2}" height="{th-2}" fill="{["#FDF9F1","#F1ECE0","#E4DFD3"][(c*5+r*2)%3]}"/>'
    rx0, ry0, rw, rh = x0 + 3 * tw, y0 + th, 4 * tw - 2, 4 * th - 2
    sc.add(f'<g class="cl">{cloud}</g>')
    sc.add(f'<g class="rc">{recon}<rect x="{rx0}" y="{ry0}" width="{rw}" height="{rh}" fill="none" stroke="{LIME}" stroke-width="4" stroke-dasharray="9 5"/></g>')
    sc.add(f'<clipPath id="ak-gc"><rect x="{x0}" y="{y0}" width="{cols*tw}" height="{rows*th}"/></clipPath>')
    sc.add(f'<g clip-path="url(#ak-gc)"><g class="dr" filter="url(#ak-bl)" opacity=".75" fill="{PAPER}">')
    for cx, cy, rr in [(rx0 + 40, ry0 + 36, 34), (rx0 + 112, ry0 + 62, 44), (rx0 + 190, ry0 + 40, 36), (rx0 + 150, ry0 + 124, 40), (rx0 + 60, ry0 + 132, 30), (x0 + 28, y0 + 22, 26), (x0 + 520, y0 + 224, 30)]:
        sc.add(f'<circle cx="{cx}" cy="{cy}" r="{rr}"/>')
    sc.add('</g></g>')
    sc.add(f'<g class="sw"><rect x="{rx0}" y="{ry0-8}" width="4" height="{rh+16}" fill="{LIME}" stroke="{INK}" stroke-width="1.5"/></g>')
    for c in range(cols):
        sc.add(f'<text class="m" x="{x0+c*tw+tw/2}" y="{y0-12}" font-size="10" fill="{INK}" text-anchor="middle">{"ABCDEFGHI"[c]}</text>')
    ly = y0 + rows * th + 40
    x = x0
    for nm, fill in [("OBSERVED", terrain(0, 0)), ("CLOUD", PAPER), ("RECONSTRUCTED", "url(#ak-ht)"), ("LOW CONFIDENCE", CORAL)]:
        sc.add(f'<rect x="{x}" y="{ly-11}" width="16" height="14" fill="{fill}" stroke="{INK}" stroke-width="2"/><text class="m" x="{x+24}" y="{ly}" font-size="11" fill="{INK}">{nm}</text>')
        x += len(nm) * 7.0 + 50
    px, pw = 676, 292
    for i, (a, b) in enumerate([("SENTINEL-2 L1C", "COPERNICUS DOWNLOAD"), ("CLOUD MASK", "RULE-BASED · LUMINANCE + SATURATION"), ("U-NET", "3 DOWN STAGES · L1 LOSS · ADAM"), ("RECONSTRUCTION", "+ CONFIDENCE HEATMAP FROM THE MASK")]):
        y = 240 + i * 86
        hi = i == 2
        tc = PAPER if hi else INK
        sc.add(card(px, y, pw, 66, COBALT if hi else PAPER, sh=5))
        sc.add(sc.display(f"0{i+1}", px + 12, y + 44, 30, fill="none", stroke=tc, sw=1.2))
        sc.add(f'<text class="m" x="{px+78}" y="{y+30}" font-size="14" fill="{tc}">{a}</text><text class="m" x="{px+78}" y="{y+48}" font-size="9" fill="{tc}" fill-opacity=".85">{b}</text>')
        if i < 3:
            sc.add(f'<path class="flow" d="M{px+pw/2} {y+66}V{y+86}" stroke="{INK}" stroke-width="3.5"/>')
    sc.add(pulse(f"M{px+pw/2} 240V576", 5.5, 0, LIME, 6))
    note(sc, "Conceptual scene. Prototype: 3 sample pairs, no trained weights shipped, no accuracy claims.", y=626)
    return sc


# ------------------------------------------------------------------ 04 Tarang
def wave_path(amp, freq, phase, y0, step=25):
    pts = [(i, y0 + amp * math.sin(math.pi * i / W) ** 1.2 * math.sin(i / W * freq * 2 * math.pi + phase)) for i in range(0, W + 1, step)]
    d = f"M{pts[0][0]} {pts[0][1]:.1f} Q{(pts[0][0]+pts[1][0])/2:.1f} {pts[0][1]:.1f} {pts[1][0]} {pts[1][1]:.1f}"
    for x, y in pts[2:]:
        d += f" T{x} {y:.1f}"
    return d


def tarang():
    sc = Scene("ta", 640, LIME, "Tarang",
               "Tarang: a music-first web app. A spinning vermilion record, layered flowing waveforms, a rhythmic multicoloured equalizer, a smooth playback-progress trace, time-synced lyric lines that highlight in turn, and a floating mini player labelled as seed data. Frontend only.")
    sc.css = """
.eq{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1.2s ease-in-out infinite alternate}
@keyframes eq{from{transform:scaleY(.2)}to{transform:scaleY(1)}}
.ly{animation:ly 9s steps(1) infinite}
@keyframes ly{0%,33%{opacity:0}34%,100%{opacity:1}}
.lh{animation:lh 9s steps(1) infinite}
@keyframes lh{0%,33%{opacity:1}34%,100%{opacity:0}}
.vin{transform-origin:840px 170px;animation:spin 6s linear infinite}
"""
    sc.add(f'<rect width="{W}" height="640" fill="url(#ta-lines)"/>')
    world(sc, 4)
    t, _ = tag(190, 24, "FRONTEND ONLY · SEED DATA", fill=PAPER, size=12, dot=VERM)
    sc.add(t)
    sz = sc.fit("TARANG", 580)
    sc.add(sc.display("TARANG", 32, 168, sz, rise=0.1))
    sc.add(f'<text class="m" x="34" y="206" font-size="13" fill="{INK}">MUSIC-FIRST WEB APP · PERSISTENT PLAYER · DOCUMENTED DESIGN SYSTEM</text>')
    cx, cy = 840, 170
    sc.add(f'<circle cx="{cx+8}" cy="{cy+8}" r="118" fill="{INK}"/><circle cx="{cx}" cy="{cy}" r="118" fill="{VERM}" stroke="{INK}" stroke-width="3"/>')
    sc.add('<g class="vin">')
    for r in (100, 84, 68):
        sc.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="2" stroke-opacity=".55"/>')
    sc.add(f'<path d="M{cx-100} {cy}A100 100 0 0 1 {cx} {cy-100}" stroke="{PAPER}" stroke-width="8" fill="none" stroke-linecap="round" stroke-opacity=".75"/>')
    sc.add(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{LIME}" stroke="{INK}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="7" fill="{INK}"/></g>')
    sc.add(f'<path d="M{cx+110} {cy-110}L{cx+40} {cy-6}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/><circle cx="{cx+110}" cy="{cy-110}" r="12" fill="{COBALT}" stroke="{INK}" stroke-width="3"/>')
    sc.add(f'<text class="m" x="34" y="248" font-size="11" fill="{INK}">TIME-SYNCED LYRICS · PLACEHOLDER LINES</text>')
    for i, t in enumerate(["Synced line, one", "Synced line, two", "Synced line, three"]):
        yy = 288 + i * 34
        dl = f"animation-delay:{-(9-i*3)}s"
        sc.add(f'<g class="lh" style="{dl}"><rect x="30" y="{yy-24}" width="{len(t)*12+24}" height="32" fill="{INK}"/><text class="s" x="42" y="{yy}" font-size="21" fill="{LIME}">{t}</text></g>')
        sc.add(f'<text class="s ly" style="{dl}" x="42" y="{yy}" font-size="21" fill="{INK}">{t}</text>')
    for amp, fr, ph, col, sw, dur in [(54, 2.0, 0.0, INK, 5, 7), (40, 3.0, 1.3, COBALT, 4, 9), (28, 4.5, 2.4, VERM, 3, 11)]:
        d1, d2, d3 = wave_path(amp, fr, ph, 396), wave_path(amp * .8, fr, ph + 2.1, 396), wave_path(amp * 1.05, fr, ph + 4.2, 396)
        sc.add(f'<path d="{d1}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"><animate attributeName="d" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.33;.66;1" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1" values="{d1};{d2};{d3};{d1}"/></path>')
    n, bw = 40, 16
    gap = (936 - n * bw) / (n - 1)
    fills = [INK, COBALT, VERM, PAPER]
    for i in range(n):
        h = 18 + 62 * math.sin(math.pi * (i + .5) / n) ** .9 * (0.5 + 0.5 * abs(math.sin(i * 1.7)))
        x = 32 + i * (bw + gap)
        sc.add(f'<rect class="eq" style="animation-duration:{.8+(i*37%11)/10:.1f}s;animation-delay:-{((i*53)%17)/10:.1f}s" x="{x:.1f}" y="{508-h:.1f}" width="{bw}" height="{h:.1f}" fill="{fills[i%4]}" stroke="{INK}" stroke-width="2"/>')
    sc.add(f'<path d="M32 510H{W-32}" stroke="{INK}" stroke-width="3"/>')
    pd = "M32 536 " + " ".join(f"L{x} {536+5*math.sin(x/34):.1f}" for x in range(52, 969, 20))
    sc.add(f'<path d="{pd}" fill="none" stroke="{INK}" stroke-opacity=".3" stroke-width="3"/>')
    sc.add(f'<path d="{pd}" pathLength="1" fill="none" stroke="{INK}" stroke-width="4" stroke-dasharray="1 1" stroke-dashoffset=".5" stroke-linecap="round"><animate attributeName="stroke-dashoffset" values="1;0" dur="14s" repeatCount="indefinite"/></path>')
    sc.add(f'<circle r="8" fill="{PAPER}" stroke="{INK}" stroke-width="3"><animateMotion dur="14s" repeatCount="indefinite" path="{pd}"/></circle>')
    sc.add(card(290, 556, 420, 50, PAPER, sh=5, rx=25))
    sc.add(f'<circle cx="320" cy="581" r="15" fill="{VERM}" stroke="{INK}" stroke-width="2.5"/><path d="M315 574l13 7-13 7z" fill="{PAPER}"/>')
    sc.add(f'<text class="s" x="346" y="577" font-size="14" fill="{INK}">Seed track</text><text class="m" x="346" y="594" font-size="10" fill="{INK}" fill-opacity=".75">DEMO AUDIO · SEED DATA · FRONTEND ONLY</text>')
    for i in range(6):
        sc.add(f'<rect class="eq" style="animation-duration:{.7+i*.17:.2f}s;animation-delay:-{i*.3:.1f}s" x="{646+i*9}" y="568" width="5" height="26" fill="{[COBALT,VERM,INK][i%3]}"/>')
    note(sc, "Stylised audio scene. Seed data, no real catalogue, no album artwork.", y=632)
    return sc


# ------------------------------------------------------------------ 05 Rinti AI
def rinti():
    sc = Scene("ri", 640, COBALT, "Rinti AI",
               "Rinti AI: a research chat workspace. A question flows through intent detection, query planning, search, page extraction, claim evaluation and synthesis, drawing on four numbered sources and producing a typeset answer with numbered citations. Account sessions use Argon2 password hashing, HttpOnly cookies and CSRF checks, with per-user memory and daily caps.")
    sc.css = """
.st{animation:st 12s ease-in-out infinite both}
@keyframes st{0%{fill:#FDF9F1}6%,14%{fill:#D8F827}22%,100%{fill:#FDF9F1}}
.ci{animation:ci 12s cubic-bezier(.34,1.56,.64,1) infinite both}
@keyframes ci{0%,58%{opacity:0;transform:scale(.4)}66%,92%{opacity:1;transform:scale(1)}100%{opacity:0}}
"""
    sc.add(f'<rect width="{W}" height="640" fill="url(#ri-linesl)"/>')
    world(sc, 5, color=INK, bg=PAPER)
    t, _ = tag(190, 24, "PRODUCT WORKFLOW VIEW", fill=LIME, size=12)
    sc.add(t)
    sz = sc.fit("RINTI AI", 500)
    sc.add(sc.display("RINTI AI", 32, 146, sz, fill=PAPER, rise=0.1))
    sc.add(f'<text class="m" x="34" y="182" font-size="13" fill="{PAPER}">RESEARCH CHAT WORKSPACE · PER-USER MEMORY · CITED MULTI-STEP RESEARCH</text>')
    x = 32
    sc.add(f'<path d="M32 232H{W-32}" stroke="{PAPER}" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round"/>')
    for i, s in enumerate(["INTENT", "PLAN", "SEARCH", "EXTRACT", "EVALUATE", "SYNTHESISE"]):
        w = len(s) * 8.6 + 54
        sc.add(f'<rect x="{x+4}" y="218" width="{w:.0f}" height="36" fill="{INK}"/><rect class="st" style="animation-delay:{i*1.8:.1f}s" x="{x}" y="214" width="{w:.0f}" height="36" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>'
               f'<text class="m" x="{x+12}" y="237" font-size="11" fill="{INK}" fill-opacity=".55">0{i+1}</text><text class="m" x="{x+40}" y="237" font-size="13" fill="{INK}">{s}</text>')
        x += w + 14
    sc.add(card(32, 290, 220, 250, PAPER, sh=6))
    sc.add(f'<text class="m" x="46" y="316" font-size="11" fill="{INK}">01 · QUESTION</text>')
    for i, wd in enumerate([170, 130, 150]):
        sc.add(f'<rect x="46" y="{336+i*16}" width="{wd}" height="8" fill="{INK}"/>')
    sc.add(f'<rect class="blink" x="202" y="368" width="8" height="10" fill="{COBALT}"/>')
    sc.add(f'<rect x="46" y="400" width="190" height="40" fill="{SAND}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/><text class="m" x="58" y="424" font-size="11" fill="{INK}">PER-USER MEMORY</text>')
    sc.add(f'<text class="m" x="46" y="474" font-size="10" fill="{INK}" fill-opacity=".75">QUICK OR STANDARD</text><text class="m" x="46" y="490" font-size="10" fill="{INK}" fill-opacity=".75">RESEARCH BUDGET</text>')
    sxo = 330
    sc.add(f'<text class="m" x="{sxo}" y="284" font-size="11" fill="{PAPER}">02 · SOURCES</text>')
    for i in range(4):
        y, off = 296 + i * 62, (i % 2) * 22
        sc.add(card(sxo + off, y, 230, 50, PAPER, sh=5))
        sc.add(f'<circle cx="{sxo+off+26}" cy="{y+25}" r="14" fill="{LIME}" stroke="{INK}" stroke-width="2.5"/><text class="m" x="{sxo+off+26}" y="{y+30}" font-size="14" fill="{INK}" text-anchor="middle">{i+1}</text>')
        sc.add(f'<rect x="{sxo+off+52}" y="{y+13}" width="{140-i*10}" height="7" fill="{INK}"/><rect x="{sxo+off+52}" y="{y+27}" width="{108+i*8}" height="5" fill="{INK}" fill-opacity=".4"/><rect x="{sxo+off+52}" y="{y+37}" width="{80+i*12}" height="5" fill="{INK}" fill-opacity=".4"/>')
    for i in range(4):
        y = 321 + i * 62
        sc.add(f'<path class="flow" d="M252 415 C290 415 290 {y} {sxo+(i%2)*22} {y}" fill="none" stroke="{PAPER}" stroke-width="3"/>')
        sc.add(f'<path class="flow" d="M{sxo+(i%2)*22+230} {y} C{sxo+300} {y} 620 {400+i*8} 650 415" fill="none" stroke="{PAPER}" stroke-width="3" style="animation-delay:-{i*.3}s"/>')
    sc.add(pulse("M252 415 C290 415 290 321 330 321", 3, 0, LIME, 6))
    ax = 650
    sc.add(card(ax, 290, 318, 250, PAPER, sh=6))
    sc.add(f'<text class="m" x="{ax+14}" y="316" font-size="11" fill="{INK}">04 · CITED ANSWER</text>')
    sc.add(sc.display("The answer,", ax + 14, 366, 30))
    sc.add(sc.display("typeset.", ax + 14, 404, 30, fill=COBALT))
    for i, wd in enumerate([270, 250, 262, 190]):
        sc.add(f'<rect x="{ax+14}" y="{424+i*18}" width="{wd}" height="7" fill="{INK}" fill-opacity=".75"/>')
    for i, (cx, cy) in enumerate([(ax + 270, 366), (ax + 276, 434), (ax + 214, 470)]):
        sc.add(f'<g class="ci fb" style="animation-delay:{i*.9:.1f}s"><rect x="{cx-13}" y="{cy-13}" width="26" height="26" fill="{CORAL}" stroke="{INK}" stroke-width="2.5"/><text class="m" x="{cx}" y="{cy+5}" font-size="14" fill="{INK}" text-anchor="middle">{i+1}</text></g>')
    sc.add(f'<text class="m" x="{ax+14}" y="526" font-size="10" fill="{INK}" fill-opacity=".75">NUMBERED CITATIONS LINK BACK TO SOURCES</text>')
    sc.add(f'<text class="m" x="32" y="576" font-size="11" fill="{PAPER}">ACCOUNT SESSIONS</text>')
    x = 32
    for t in ["ARGON2 PASSWORD HASHING", "HTTPONLY SESSION COOKIES", "CSRF HEADER CHECK", "PER-USER DAILY CAPS"]:
        s, w = tag(x, 586, t, fill=PAPER, size=11, dot=LIME, h=28)
        sc.add(s)
        x += w + 10
    note(sc, "Product workflow and evidence flow only. It does not depict model reasoning.", y=632, color=PAPER)
    return sc


# ------------------------------------------------------------------ 06 Orbit OS
def orbit():
    sc = Scene("ob", 600, SAND, "Orbit OS",
               "Orbit OS: floating tilted panels for a dashboard, weather and a focus timer, geometric orbits with glossy spheres, and a command palette typing the word weather. An interface experiment on mock data, not a real operating system.")
    sc.css = """
.fl1{animation:fl 6s ease-in-out infinite alternate}
.fl2{animation:fl 7.5s ease-in-out infinite alternate-reverse}
.fl3{animation:fl 5s ease-in-out infinite alternate}
@keyframes fl{from{transform:translateY(0)}to{transform:translateY(-10px)}}
.ar{animation:ar 6s ease-in-out infinite alternate}
@keyframes ar{from{stroke-dashoffset:70}to{stroke-dashoffset:20}}
.hl{animation:hl 8s ease-in-out infinite}
@keyframes hl{0%,40%{fill-opacity:.25}55%,90%{fill-opacity:0}100%{fill-opacity:.25}}
"""
    sc.defs.append('<clipPath id="ob-ty"><rect x="318" y="468" width="0" height="26"><animate attributeName="width" values="0;0;98;98;98;0" keyTimes="0;.08;.4;.8;.95;1" dur="8s" repeatCount="indefinite"/></rect></clipPath>')
    sc.add(f'<rect width="{W}" height="600" fill="url(#ob-dots)"/>')
    world(sc, 6, color=PAPER, bg=INK)
    t, _ = tag(190, 24, "MOCK DATA · NOT A REAL OS", fill=VERM, size=12)
    sc.add(t)
    sz = sc.fit("ORBIT OS", 500)
    sc.add(sc.display("ORBIT OS", 32, 146, sz, rise=0.1))
    sc.add(f'<text class="m" x="34" y="182" font-size="13" fill="{INK}">AN INTERFACE EXPLORATION · BORROWS FROM OPERATING-SYSTEM DESIGN</text>')
    ox, oy = 800, 330
    for rx, ry, dash in [(190, 70, ""), (130, 48, ' stroke-dasharray="2 8"')]:
        sc.add(f'<ellipse cx="{ox}" cy="{oy}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="2.5" transform="rotate(-24 {ox} {oy})"{dash}/>')
    sc.add(f'<circle cx="{ox+7}" cy="{oy+7}" r="42" fill="{INK}"/><circle cx="{ox}" cy="{oy}" r="42" fill="url(#ob-ball)" stroke="{INK}" stroke-width="3"/>')
    sc.add(f'<ellipse cx="{ox-14}" cy="{oy-16}" rx="12" ry="7" fill="#FFFFFF" fill-opacity=".75" transform="rotate(-28 {ox-14} {oy-16})"/>')
    p1 = f"M{ox+190} {oy} A190 70 0 1 1 {ox-190} {oy} A190 70 0 1 1 {ox+190} {oy}"
    p2 = f"M{ox-130} {oy} A130 48 0 1 0 {ox+130} {oy} A130 48 0 1 0 {ox-130} {oy}"
    sc.add(f'<g transform="rotate(-24 {ox} {oy})"><circle r="15" fill="{COBALT}" stroke="{INK}" stroke-width="3"><animateMotion dur="14s" repeatCount="indefinite" path="{p1}"/></circle>'
           f'<circle r="10" fill="{VERM}" stroke="{INK}" stroke-width="3"><animateMotion dur="8s" repeatCount="indefinite" path="{p2}"/></circle></g>')
    sc.add('<g class="fl1"><g transform="rotate(-4 200 330)">' + card(60, 220, 360, 210, LIME, sh=8)
           + f'<text class="m" x="76" y="248" font-size="11" fill="{INK}">DASHBOARD</text><rect x="76" y="262" width="200" height="16" fill="{INK}"/><rect x="76" y="286" width="130" height="8" fill="{INK}" fill-opacity=".45"/>'
           + "".join(f'<rect x="{76+i*108}" y="312" width="96" height="52" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/>' for i in range(3))
           + f'<path d="M76 410 C120 380 150 420 196 394 S280 388 330 376 S380 400 404 386" fill="none" stroke="{COBALT}" stroke-width="4"/></g></g>')
    sc.add('<g class="fl2"><g transform="rotate(3 520 260)">' + card(450, 214, 190, 106, COBALT, sh=8)
           + f'<text class="m" x="464" y="240" font-size="11" fill="{PAPER}">WEATHER</text><circle cx="496" cy="282" r="20" fill="{YEL}" stroke="{INK}" stroke-width="2.5"/>'
           + f'<rect x="530" y="270" width="86" height="8" fill="{PAPER}"/><rect x="530" y="288" width="56" height="6" fill="{PAPER}" fill-opacity=".6"/></g></g>')
    sc.add('<g class="fl3"><g transform="rotate(-2 520 380)">' + card(450, 340, 190, 100, PAPER, sh=8)
           + f'<text class="m" x="464" y="366" font-size="11" fill="{INK}">FOCUS TIMER</text><circle cx="500" cy="404" r="20" fill="none" stroke="{SAND}" stroke-width="7"/>'
           + f'<circle class="ar" cx="500" cy="404" r="20" fill="none" stroke="{VERM}" stroke-width="7" pathLength="100" stroke-dasharray="100" stroke-dashoffset="30" transform="rotate(-90 500 404)"/>'
           + f'<rect x="534" y="394" width="86" height="8" fill="{INK}"/><rect x="534" y="412" width="56" height="6" fill="{INK}" fill-opacity=".45"/></g></g>')
    sc.add(card(250, 452, 440, 112, INK, sh=7, shc=COBALT))
    sc.add(f'<circle cx="278" cy="480" r="7" fill="none" stroke="{PAPER}" stroke-width="2.5"/><path d="M283 485l7 7" stroke="{PAPER}" stroke-width="2.5"/>')
    sc.add(f'<text class="m" x="318" y="487" font-size="18" fill="{LIME}" clip-path="url(#ob-ty)">weather</text><rect class="blink" x="428" y="470" width="3" height="22" fill="{LIME}"/>')
    sc.add(f'<text class="m" x="674" y="487" font-size="10" fill="{PAPER}" fill-opacity=".7" text-anchor="end">COMMAND PALETTE</text><path d="M266 504H674" stroke="{PAPER}" stroke-opacity=".25"/>')
    sc.add(f'<rect class="hl" x="262" y="512" width="416" height="22" fill="{LIME}" fill-opacity=".25"/>')
    sc.add(f'<text class="m" x="276" y="528" font-size="12" fill="{PAPER}">Weather · open forecast</text><text class="m" x="276" y="552" font-size="12" fill="{PAPER}" fill-opacity=".65">Focus · start timer</text>')
    note(sc, "Interface exploration. Mock data throughout. Not an operating system.", y=588)
    return sc


# ------------------------------------------------------------------ 07 AI workflow
def ai_workflow():
    sc = Scene("aw", 680, PAPER, "Engineering with AI",
               "A visual narrative of how Samudra works with AI. Step one, Samudra, a human engineer, sets architecture and direction. Step two, two AI engineering agents implement: Claude Code for UI, UX, design tokens and documentation, and Antigravity for boot, memory, interrupts, scheduler and drivers. Step three, both share one repository through sync logs, handoff notes, architecture docs, API contracts and commits. Step four, a validation loop of review, run and accept or reject returns to Samudra.")
    sc.css = """
.sheet{animation:sheet 6s ease-in-out infinite alternate}
@keyframes sheet{from{transform:translateX(0)}to{transform:translateX(6px)}}
"""
    sc.add(f'<rect width="{W}" height="680" fill="url(#aw-dots)"/>')
    world(sc, 6, color=PAPER, bg=INK)
    t, _ = tag(190, 24, "HUMAN-LED · AI-IMPLEMENTED", fill=LIME, size=12)
    sc.add(t)
    sz = sc.fit("ENGINEERING", 700)
    sc.add(sc.display("ENGINEERING", 32, 142, sz, rise=0.1))
    sc.add(sc.display("WITH AI.", 32, 142 + CAP * sz / UPM + 22, sz, fill=COBALT, rise=0.4))
    sc.add(f'<text class="m" x="34" y="262" font-size="12" fill="{INK}">AGENTS ARE TOOLS, NOT PEOPLE · SCOPE, INTERFACES AND TRADE-OFFS STAY WITH SAMUDRA</text>')
    for x, n, nm in [(32, "01", "DIRECT"), (330, "02", "IMPLEMENT"), (690, "03", "SHARE")]:
        sc.add(sc.display(n, x, 322, 34, fill="none", stroke=INK, sw=1.2))
        sc.add(f'<text class="m" x="{x+82}" y="316" font-size="12" fill="{INK}">{nm}</text>')
    # human
    sc.add(f'<circle cx="160" cy="456" r="80" fill="{INK}"/><circle cx="152" cy="448" r="80" fill="url(#aw-chrome)" stroke="{INK}" stroke-width="3"/>')
    sc.add(sc.display("S", 152, 484, 104, anchor="middle"))
    sc.add(f'<text class="m" x="152" y="560" font-size="13" fill="{INK}" text-anchor="middle">SAMUDRA · HUMAN</text>')
    for i, t in enumerate(["ARCHITECTURE", "DIRECTION", "REVIEW + VALIDATION"]):
        w = len(t) * 7.2 + 22
        sc.add(f'<rect x="{152-w/2}" y="{572+i*30}" width="{w:.0f}" height="24" rx="12" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><text class="m" x="152" y="{588+i*30}" font-size="10.5" fill="{INK}" text-anchor="middle">{t}</text>')
    # agents
    for y, fill, tc, nm, sub in [(346, COBALT, PAPER, "CLAUDE CODE", "UI · UX · DESIGN TOKENS · DOCS"), (494, VERM, INK, "ANTIGRAVITY", "BOOT · MEMORY · INTERRUPTS · SCHEDULER")]:
        sc.add(card(330, y, 280, 120, fill, sh=7))
        sc.add(f'<rect x="344" y="{y+14}" width="156" height="20" rx="10" fill="{PAPER}" stroke="{INK}" stroke-width="2"/><text class="m" x="422" y="{y+28}" font-size="9.5" fill="{INK}" text-anchor="middle">AI ENGINEERING AGENT</text>')
        sc.add(sc.display(nm, 344, y + 76, min(26, sc.fit(nm, 236)), fill=tc))
        sc.add(f'<text class="m" x="344" y="{y+102}" font-size="10.5" fill="{tc}">{sub}</text>')
    items = [(".agents/", "SYNC LOG · HANDOFF NOTES", LIME), ("docs/", "ARCHITECTURE · DESIGN", YEL), ("API_CONTRACTS", "PROPOSED > AGREED > IMPLEMENTED", PAPER), ("GIT HISTORY", "SMALL, DESCRIBED COMMITS", SAND)]
    sc.add(f'<text class="m" x="690" y="356" font-size="11" fill="{INK}">ONE SHARED REPOSITORY</text>')
    for i, (n, d, col) in enumerate(items):
        x, y = 690 + i * 8, 366 + i * 62
        sc.add(f'<g class="sheet" style="animation-delay:-{i*1.2}s">' + card(x, y, 270, 54, col, sh=5)
               + f'<text class="m" x="{x+14}" y="{y+23}" font-size="13" fill="{INK}">{n}</text><text class="m" x="{x+14}" y="{y+41}" font-size="9" fill="{INK}" fill-opacity=".8">{d}</text></g>')
    for i, d in enumerate(["M236 430 C290 430 290 410 330 410", "M226 490 C280 560 290 556 330 556", "M610 410 C650 410 650 394 690 394", "M610 556 C650 556 650 480 692 480"]):
        sc.add(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="5"/><path class="flow" d="{d}" fill="none" stroke="{YEL}" stroke-width="2.5"/>' + pulse(d, 3.4, i * .5, LIME, 6))
    vp = "M840 630 C840 680 600 682 420 680 C200 678 40 676 30 600 C26 540 50 520 80 504"
    sc.add(f'<path d="{vp}" fill="none" stroke="{CORAL}" stroke-width="5" stroke-dasharray="12 8"/>' + pulse(vp, 6, 0, CORAL, 7))
    sc.add(f'<rect x="352" y="640" width="336" height="32" rx="16" fill="{YEL}" stroke="{INK}" stroke-width="2.5"/><text class="m" x="520" y="661" font-size="12" fill="{INK}" text-anchor="middle">04 · REVIEW · RUN · ACCEPT OR REJECT</text>')
    return sc


# ------------------------------------------------------------------ 08 capabilities
def capabilities():
    rows = [("LANGUAGES", ["TypeScript", "JavaScript", "Python", "C", "x86-64 Assembly"], LIME),
            ("SYSTEMS", ["Clang", "LLD", "NASM", "QEMU", "Git", "Docker"], YEL),
            ("WEB", ["React", "Next.js", "Tailwind", "Framer Motion", "GSAP", "Three.js"], COBALT),
            ("AI / VISION", ["PyTorch", "NumPy", "SciPy", "scikit-image", "LLM APIs"], VERM),
            ("DESIGN", ["Figma", "Design Systems", "Motion Design"], INK)]
    H = 150 + len(rows) * 96 + 28
    sc = Scene("cp", H, PAPER, "Technical capabilities",
               "Technical index. Languages: TypeScript, JavaScript, Python, C, x86-64 Assembly. Systems: Clang, LLD, NASM, QEMU, Git, Docker. Web: React, Next.js, Tailwind, Framer Motion, GSAP, Three.js. AI and vision: PyTorch, NumPy, SciPy, scikit-image, LLM APIs. Design: Figma, Design Systems, Motion Design.")
    sc.css = """
.rw{animation:rw 10s steps(1) infinite}
@keyframes rw{0%,16%{opacity:1}17%,100%{opacity:0}}
"""
    sc.add(f'<rect width="{W}" height="{H}" fill="url(#cp-dots)"/>')
    s, _ = tag(32, 24, "TECHNICAL INDEX", fill=INK, color=PAPER, size=12)
    sc.add(s)
    sc.add(sc.display("THE TOOLKIT.", 32, 112, sc.fit("THE TOOLKIT.", 560), rise=0.1))
    for i, (label, items, col) in enumerate(rows):
        y = 150 + i * 96
        sc.add(f'<path d="M32 {y}H{W-32}" stroke="{INK}" stroke-width="2.5"/>')
        sc.add(f'<rect class="rw" style="animation-delay:{-(10-i*1.6):.1f}s" x="32" y="{y+2}" width="{W-64}" height="93" fill="{col}" fill-opacity=".2"/>')
        sc.add(sc.display(f"0{i+1}", 32, y + 64, 44, fill="none", stroke=INK, sw=1.4))
        sc.add(sc.display(label, 142, y + 42, min(24, sc.fit(label, 196))))
        sc.add(f'<rect x="142" y="{y+54}" width="{20+len(label)*6}" height="9" fill="{col}" stroke="{INK}" stroke-width="2"/>')
        x, yy = 352, y + 30
        for it in items:
            w = int(len(it) * 7.3 + 32)
            if x + w > W - 32:
                x, yy = 352, yy + 38
            sc.add(f'<rect x="{x+3}" y="{yy+3}" width="{w}" height="32" fill="{INK}"/><rect x="{x}" y="{yy}" width="{w}" height="32" fill="{PAPER}" stroke="{INK}" stroke-width="2.5"/><circle cx="{x+16}" cy="{yy+16}" r="5" fill="{col}" stroke="{INK}" stroke-width="2"/><text class="m" x="{x+30}" y="{yy+21}" font-size="12" fill="{INK}">{e(it)}</text>')
            x += w + 10
    sc.add(f'<path d="M32 {150+len(rows)*96}H{W-32}" stroke="{INK}" stroke-width="2.5"/>')
    return sc


# ------------------------------------------------------------------ 09 closing
def closing():
    sc = Scene("cl", 560, YEL, "Samudra Kar. Open to internships.",
               "SAMUDRA KAR. Open to internships. Bangalore, India. Chanakya University. Portfolio at sam-sportfolio.vercel.app. Email hi.samsstudio@gmail.com.")
    sc.css = """
.ping{animation:ping 2.4s ease-out infinite}
@keyframes ping{0%{transform:scale(.4);opacity:.9}100%{transform:scale(2.6);opacity:0}}
.mqb{animation:mqb 28s linear infinite}
@keyframes mqb{to{transform:translateX(-640px)}}
"""
    sc.add(f'<rect width="{W}" height="560" fill="url(#cl-lines)"/>')
    s, _ = tag(32, 24, "END OF PROFILE", fill=INK, color=PAPER, size=12)
    sc.add(s)
    sc.add(f'<circle cx="860" cy="170" r="96" fill="{INK}" transform="translate(8 8)"/><circle cx="860" cy="170" r="96" fill="{LIME}" stroke="{INK}" stroke-width="3"/>')
    sc.add(f'<path d="M788 120A90 90 0 0 1 868 82" fill="none" stroke="#FFFFFF" stroke-opacity=".8" stroke-width="9" stroke-linecap="round"/>')
    s, w = tag(32, 92, "OPEN TO INTERNSHIPS", fill=PAPER, size=14, dot=LIME, h=34)
    sc.add(s)
    sc.add(f'<circle class="ping fb" cx="52" cy="109" r="5" fill="none" stroke="{INK}" stroke-width="2"/>')
    size = sc.fit("SAMUDRA", 936)
    sc.add(sc.display("SAMUDRA", 32, 330, size, rise=0.1))
    ky = 330 + CAP * size / UPM + 26
    sc.add(sc.display("KAR", 32, ky, size, rise=0.5))
    sc.add(sc.display(".", 32 + sc.tw("KAR", size), ky, size, fill=COBALT, rise=0.7))
    fx = 32 + sc.tw("KAR.", size) + 36
    for i, (k, v) in enumerate([("LOCATION", "Bangalore, India"), ("UNIVERSITY", "Chanakya University"), ("PORTFOLIO", "sam-sportfolio.vercel.app"), ("EMAIL", "hi.samsstudio@gmail.com")]):
        y = ky - 72 + i * 24
        sc.add(f'<text class="m" x="{fx}" y="{y}" font-size="10" fill="{INK}" fill-opacity=".7">{k}</text><text class="m" x="{fx+88}" y="{y}" font-size="12.5" fill="{INK}">{e(v)}</text>')
    sc.add(f'<rect x="0" y="508" width="{W}" height="52" fill="{INK}"/>')
    seq = "OPEN TO INTERNSHIPS  //  SYSTEMS  //  AI  //  PRODUCT ENGINEERING  //  BANGALORE  //  "
    sc.add(f'<g class="mqb"><text class="m" x="20" y="540" font-size="16" fill="{LIME}">{seq*3}</text></g>')
    return sc


SCENES = {
    "about.svg": about, "samagra-os.svg": samagra, "prahari.svg": prahari, "akashalens.svg": akashalens,
    "tarang.svg": tarang, "rinti-ai.svg": rinti, "orbit-os.svg": orbit, "ai-workflow.svg": ai_workflow,
    "capabilities.svg": capabilities, "closing.svg": closing,
}


def check():
    ok, seen = True, {}
    for name in SCENES:
        txt = (OUT / name).read_text(encoding="utf-8")
        try:
            xml.dom.minidom.parseString(txt)
        except Exception as ex:
            print(f"XML ERROR {name}: {ex}")
            ok = False
            continue
        if "<script" in txt or "<image" in txt or "@import" in txt or re.search(r'href="(?!#)', txt) or "http://" in txt.replace("http://www.w3.org/2000/svg", ""):
            print(f"UNSAFE CONTENT in {name}")
            ok = False
        for i in re.findall(r'\bid="([^"]+)"', txt):
            if i in seen and seen[i] != name:
                print(f"DUPLICATE ID {i}: {seen[i]} / {name}")
                ok = False
            seen[i] = name
        print(f"{name:20s} {len(txt)/1024:5.1f} KB  ok")
    return ok


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in SCENES.items():
        (OUT / name).write_text(fn().render(), encoding="utf-8", newline="\n")
    sys.exit(0 if check() else 1)


if __name__ == "__main__":
    main()
