#!/usr/bin/env python3
"""Generates every SVG in assets/profile/ and validates them.

    python tools/build_profile_assets.py

Design system (shared by all scenes)
  canvas   1000 px wide, graphite #090B10, 25 px grid, 18 px corner radius
  chrome   44 px header strip, mono labels, accent square, corner ticks, bottom note
  type     mono (ui-monospace stack) for labels, system sans for titles
  motion   CSS keyframes + SMIL only, no scripts, no external resources.
           Every base (non-animated) state is a complete, readable composition.
  accent   one accent per scene, chosen from the palette below
Nothing here is live telemetry: every status, score and trace is illustrative
and labelled as such inside the artwork.
"""
import math
import pathlib
import re
import sys
import xml.dom.minidom
from xml.sax.saxutils import escape

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "profile"
W = 1000

BG = "#090B10"
PANEL = "#0E121A"
LINE = "#1D2431"
LINE2 = "#2A3345"
INK = "#EAF0F8"
SOFT = "#B8C2D4"
MUT = "#8E99AD"
DIM = "#566075"
TEAL = "#5FD4C8"
ICE = "#8CC8FF"
AMB = "#F0B55E"
VIO = "#A99BFF"
GRN = "#8BE09A"

BASE_CSS = """
text{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace}
.k{letter-spacing:.14em}
.flow{stroke-dasharray:3 9;animation:flow 1.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-24}}
.scan{animation:scan 9s linear infinite}
@keyframes scan{from{transform:translateY(-90px)}to{transform:translateY(640px)}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{0%,55%{opacity:1}56%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def e(s):
    return escape(s, {'"': "&quot;"})


def doc(pid, h, title, desc, body, accent, css="", defs="", left="", right="", note=""):
    chrome = f"""
<rect width="{W}" height="44" fill="#0C1017"/>
<path d="M0 44.5H{W}" stroke="{LINE}"/>
<rect x="28" y="19" width="6" height="6" fill="{accent}"/>
<text class="m k" x="44" y="26" font-size="11.5" fill="{MUT}">{e(left)}</text>
<text class="m k" x="{W-28}" y="26" font-size="11.5" fill="{DIM}" text-anchor="end">{e(right)}</text>
<text class="m" x="28" y="{h-16}" font-size="11" fill="{DIM}">{e(note)}</text>
<path d="M14 {h-30}V{h-14}H30M{W-14} {h-30}V{h-14}H{W-30}" fill="none" stroke="{accent}" stroke-opacity=".55"/>
<rect class="scan" x="0" y="0" width="{W}" height="70" fill="url(#{pid}-scan)" opacity=".5"/>
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-labelledby="{pid}-t {pid}-d">
<title id="{pid}-t">{e(title)}</title>
<desc id="{pid}-d">{e(desc)}</desc>
<defs>
<pattern id="{pid}-g" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0H0V25" fill="none" stroke="#131923" stroke-width="1"/></pattern>
<radialGradient id="{pid}-glow" cx="85%" cy="0%" r="70%"><stop offset="0" stop-color="{accent}" stop-opacity=".16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<linearGradient id="{pid}-scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".85" stop-color="{accent}" stop-opacity=".14"/><stop offset="1" stop-color="{accent}" stop-opacity=".5"/></linearGradient>
<clipPath id="{pid}-clip"><rect width="{W}" height="{h}" rx="18"/></clipPath>
{defs}
</defs>
<style>{BASE_CSS}{css}</style>
<g clip-path="url(#{pid}-clip)">
<rect width="{W}" height="{h}" fill="{BG}"/>
<rect width="{W}" height="{h}" fill="url(#{pid}-g)"/>
<rect width="{W}" height="{h}" fill="url(#{pid}-glow)"/>
{body}
{chrome}
</g>
<rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="18" fill="none" stroke="{LINE2}"/>
</svg>
"""


def pulse(path, dur, begin, color, r=3.2):
    return (
        f'<circle r="{r}" fill="{color}" opacity="0">'
        f'<animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="{path}"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
        f"</circle>"
    )


def panel(x, y, w, h, title, accent=None, dashed=False):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{PANEL}" stroke="{LINE2}"' + (' stroke-dasharray="4 5"' if dashed else "") + "/>"
    s += f'<text class="m k" x="{x+16}" y="{y+24}" font-size="11" fill="{accent or DIM}">{e(title)}</text>'
    return s


def chip(x, y, text, kind):
    """kind: ok | early | plan. Returns (svg, width)."""
    w = int(len(text) * 7.3 + 38)
    col = {"ok": TEAL, "early": AMB, "plan": DIM}[kind]
    dash = ' stroke-dasharray="3 4"' if kind == "plan" else ""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="13" fill="{PANEL}" stroke="{col if kind!="plan" else LINE2}" stroke-opacity="{".7" if kind!="plan" else "1"}"{dash}/>'
    if kind == "ok":
        s += f'<circle cx="{x+14}" cy="{y+13}" r="3.5" fill="{col}"/>'
    elif kind == "early":
        s += f'<circle cx="{x+14}" cy="{y+13}" r="3.5" fill="none" stroke="{col}" stroke-width="1.5"/><path d="M{x+14} {y+9.5}a3.5 3.5 0 0 0 0 7z" fill="{col}"/>'
    else:
        s += f'<circle cx="{x+14}" cy="{y+13}" r="3.5" fill="none" stroke="{col}" stroke-width="1.5"/>'
    s += f'<text class="m" x="{x+26}" y="{y+17.5}" font-size="12" fill="{INK if kind!="plan" else MUT}">{e(text)}</text>'
    return s, w


# --------------------------------------------------------------------------- hero
def about():
    pid = "ab"
    H = 440
    css = """
.pl{animation:pl 12s ease-out infinite both}
@keyframes pl{0%{opacity:0;transform:translateY(22px)}6%{opacity:1;transform:translateY(0)}90%{opacity:1;transform:translateY(0)}100%{opacity:0;transform:translateY(0)}}
.tr{stroke-dasharray:5 7;animation:flow 1.4s linear infinite}
.nd{animation:nd 3.2s ease-in-out infinite}
@keyframes nd{0%,100%{opacity:.55}50%{opacity:1}}
.rv{animation:rv 12s ease-out infinite both}
@keyframes rv{0%{opacity:0;transform:translateX(-14px)}5%{opacity:1;transform:translateX(0)}92%{opacity:1}100%{opacity:0}}
"""
    plates = [
        ("PRODUCT ENGINEERING", "interfaces people use", ICE),
        ("AI + COMPUTER VISION", "models, pipelines, APIs", VIO),
        ("SYSTEMS + KERNEL", "memory, interrupts, schedulers", TEAL),
        ("x86-64 HARDWARE", "first principles start here", MUT),
    ]
    body = ""
    # stack on the right
    x0, w, ph, dx = 640, 270, 50, 40
    ys = [118, 188, 258, 328]
    sx = x0 + w + dx // 2 - 26
    body += f'<path class="tr" d="M{sx} {ys[3]+ph/2} V{ys[0]+ph/2}" stroke="{TEAL}" stroke-width="1.5" fill="none" opacity=".9"/>'
    for i, (name, sub, col) in enumerate(plates):
        y = ys[i]
        pts = f"{x0+dx},{y} {x0+w+dx},{y} {x0+w},{y+ph} {x0},{y+ph}"
        body += f'<g class="pl" style="animation-delay:{(3-i)*0.45:.2f}s">'
        body += f'<polygon points="{pts}" fill="{PANEL}" stroke="{col}" stroke-opacity=".75"/>'
        body += f'<polygon points="{x0},{y+ph} {x0+w},{y+ph} {x0+w},{y+ph+7} {x0},{y+ph+7}" fill="{col}" fill-opacity=".14"/>'
        body += f'<text class="m k" x="{x0+dx/2+12}" y="{y+22}" font-size="12.5" fill="{INK}">{name}</text>'
        body += f'<text class="m" x="{x0+dx/2+12}" y="{y+39}" font-size="11" fill="{MUT}">{sub}</text>'
        body += f'<circle class="nd" cx="{sx}" cy="{y+ph/2}" r="0" fill="{col}"/>'
        body += "</g>"
    # nodes on the spine
    for i, y in enumerate(ys):
        body += f'<circle class="nd" style="animation-delay:{i*.5}s" cx="{sx}" cy="{y+ph/2+0}" r="3.5" fill="{TEAL}"/>'
    body += pulse(f"M{sx} {ys[3]+ph/2} V{ys[0]+ph/2}", 4.2, 0.6, "#C9FFF8", 3.6)
    # coordinate annotations
    body += f'<text class="m" x="{x0+w+dx+14}" y="{ys[0]+14}" font-size="10.5" fill="{DIM}">y+3</text>'
    body += f'<text class="m" x="{x0+w+dx-26}" y="{ys[3]+ph+22}" font-size="10.5" fill="{DIM}">y+0 · ground truth</text>'
    # identity
    body += f'<g class="rv"><text class="m k" x="56" y="98" font-size="12.5" fill="{TEAL}">SAMUDRA KAR  /  BOOT ▸ PROFILE</text><circle class="blink" cx="40" cy="94" r="3.5" fill="{TEAL}"/></g>'
    body += f'<g class="rv" style="animation-delay:.25s"><text x="54" y="190" font-size="90" font-weight="700" fill="{INK}" letter-spacing="-3">Samudra</text>'
    body += f'<text x="54" y="272" font-size="90" font-weight="700" fill="{INK}" letter-spacing="-3">Kar<tspan fill="{TEAL}">.</tspan></text></g>'
    body += f'<g class="rv" style="animation-delay:.55s"><text x="56" y="316" font-size="25" fill="{SOFT}">Computer Science engineering student</text>'
    body += f'<text class="m" x="56" y="348" font-size="15" fill="{MUT}">systems  ·  AI  ·  product engineering</text></g>'
    body += f'<g class="rv" style="animation-delay:.9s"><text class="m" x="56" y="394" font-size="17" fill="{TEAL}">$ build --from-first-principles</text>'
    body += f'<rect class="blink" x="376" y="381" width="9" height="16" fill="{TEAL}"/></g>'
    # signature mark
    body += f'<g transform="translate(900 66)"><path d="M0 0H34M0 0V34M60 0H34M60 0V12" fill="none" stroke="{TEAL}" stroke-width="2"/><text class="m" x="30" y="40" font-size="26" font-weight="700" fill="{INK}" text-anchor="middle">SK</text></g>'
    return doc(
        pid, H,
        "Samudra Kar",
        "Samudra Kar. Computer Science engineering student building across systems, AI and product, from first principles. Bangalore, India. Chanakya University. Open to internships.",
        body, TEAL, css,
        left="SAMUDRA·KAR  //  PROFILE", right="BANGALORE · IN", note="Stylised boot sequence. Not live telemetry.",
    )


# --------------------------------------------------------------------------- Samagra OS
def samagra():
    pid = "so"
    H = 560
    css = """
.cur{animation:cur 6s linear infinite}
@keyframes cur{from{transform:translateY(0)}to{transform:translateY(204px)}}
.sl{animation:sl 6s steps(1) infinite}
@keyframes sl{0%,16.6%{opacity:1}16.7%,100%{opacity:.2}}
.ph{animation:ph 6s linear infinite}
@keyframes ph{from{transform:translateX(0)}to{transform:translateX(180px)}}
.shock{transform-box:fill-box;transform-origin:center;animation:shock 1.8s ease-out infinite}
@keyframes shock{0%{transform:scale(.3);opacity:.9}100%{transform:scale(1.8);opacity:0}}
.cg{animation:cg 9s ease-in-out infinite}
@keyframes cg{0%,12%,100%{stroke-opacity:.45}4%{stroke-opacity:1}}
.tk{animation:tk 3s steps(1) infinite}
@keyframes tk{0%,8%{opacity:1}9%,100%{opacity:.35}}
"""
    b = ""
    b += f'<text x="40" y="94" font-size="38" font-weight="700" fill="{INK}">Samagra OS</text>'
    b += f'<text class="m" x="42" y="120" font-size="13" fill="{MUT}">a real x86-64 operating system, built from first principles</text>'
    b += f'<rect x="716" y="72" width="244" height="30" rx="15" fill="{PANEL}" stroke="{AMB}" stroke-opacity=".7"/><circle cx="734" cy="87" r="4" fill="{AMB}"/><text class="m k" x="748" y="91" font-size="11" fill="{AMB}">EARLY DEVELOPMENT</text>'
    # panel 1: address space
    b += panel(40, 140, 250, 268, "01 · ADDRESS SPACE", TEAL)
    segs = [
        ("USER · per process", "Ring 3 · early", 52, True),
        ("KERNEL IMAGE", "Ring 0 · C + NASM", 42, False),
        ("PAGE TABLES", "4-level · map / unmap", 38, False),
        ("PMM BITMAP", "physical page allocator", 38, False),
        ("VGA TEXT BUFFER", "0xB8000", 34, False),
    ]
    y = 176
    for name, sub, h, early in segs:
        dash = f' stroke-dasharray="4 4" stroke="{AMB}" stroke-opacity=".7"' if early else f' stroke="{LINE2}"'
        b += f'<rect x="56" y="{y}" width="218" height="{h}" rx="5" fill="#0B0F16"{dash}/>'
        b += f'<text class="m" x="68" y="{y+h/2-1}" font-size="12" fill="{INK}">{name}</text>'
        b += f'<text class="m" x="68" y="{y+h/2+13}" font-size="10.5" fill="{MUT}">{sub}</text>'
        y += h + 4
    b += f'<g class="cur"><rect x="52" y="172" width="226" height="2" fill="{TEAL}"/><rect x="52" y="172" width="226" height="14" fill="{TEAL}" opacity=".10"/></g>'
    # panel 2: rings
    b += panel(310, 140, 340, 268, "02 · PRIVILEGE RINGS", ICE)
    cx, cy = 482, 290
    b += f'<circle cx="{cx}" cy="{cy}" r="100" fill="none" stroke="{AMB}" stroke-opacity=".75" stroke-dasharray="5 5"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="58" fill="{TEAL}" fill-opacity=".07" stroke="{TEAL}"/>'
    b += f'<text class="m k" x="{cx}" y="{cy-76}" font-size="11" fill="{AMB}" text-anchor="middle">RING 3 · USER (EARLY)</text>'
    b += f'<text class="m k" x="{cx}" y="{cy-2}" font-size="12" fill="{TEAL}" text-anchor="middle">RING 0</text>'
    b += f'<text class="m" x="{cx}" y="{cy+16}" font-size="11" fill="{MUT}" text-anchor="middle">kernel</text>'
    # syscall paths
    pin = f"M{cx-60} {cy-62} C{cx-52} {cy-42} {cx-38} {cy-32} {cx-24} {cy-26}"
    pout = f"M{cx+24} {cy-26} C{cx+40} {cy-32} {cx+54} {cy-44} {cx+62} {cy-64}"
    b += f'<path class="flow" d="{pin}" fill="none" stroke="{ICE}" stroke-width="1.5"/><path class="flow" d="{pout}" fill="none" stroke="{ICE}" stroke-width="1.5" style="animation-direction:reverse"/>'
    b += pulse(pin, 2.4, 0, ICE) + pulse(pout, 2.4, 1.2, ICE)
    b += f'<text class="m" x="{cx+70}" y="{cy-78+34}" font-size="11" fill="{ICE}">12 syscalls</text>'
    # IRQ
    ix, iy = cx - 150, cy + 20
    b += f'<circle class="shock" cx="{ix}" cy="{iy}" r="16" fill="none" stroke="{TEAL}"/>'
    b += f'<circle cx="{ix}" cy="{iy}" r="5" fill="{TEAL}"/><text class="m k" x="{ix-10}" y="{iy+28}" font-size="11" fill="{TEAL}">IRQ0</text>'
    b += f'<path class="flow" d="M{ix+6} {iy} L{cx-58} {cy+4}" stroke="{TEAL}" stroke-width="1.5" fill="none"/>'
    b += pulse(f"M{ix+6} {iy} L{cx-58} {cy+4}", 1.8, 0, "#C9FFF8")
    b += f'<text class="m" x="{cx}" y="{cy+120}" font-size="10.5" fill="{DIM}" text-anchor="middle">PIC 0x20 / 0x28 · PIT 100 Hz</text>'
    # panel 3: scheduler
    b += panel(670, 140, 290, 268, "03 · SCHEDULER", TEAL)
    sx, sw = 756, 30
    for i in range(7):
        b += f'<path class="tk" style="animation-delay:{-(6-i)*0.0}s" d="M{sx+i*sw} 178v10" stroke="{DIM}"/>'
    b += f'<text class="m" x="690" y="188" font-size="10.5" fill="{DIM}">IRQ0</text>'
    lanes = [("kernel A", 0), ("kernel B", 1), ("user", 2)]
    for n, (name, li) in enumerate(lanes):
        ly = 208 + n * 52
        b += f'<text class="m" x="690" y="{ly+22}" font-size="11" fill="{MUT}">{name}</text>'
        b += f'<rect x="{sx}" y="{ly}" width="{sw*6}" height="32" rx="4" fill="#0B0F16" stroke="{LINE}"/>'
        for k in range(6):
            if k % 3 == li:
                col = AMB if name == "user" else TEAL
                b += f'<rect class="sl" style="animation-delay:{-(6-k)}s" x="{sx+k*sw+2}" y="{ly+3}" width="{sw-4}" height="26" rx="3" fill="{col}"/>'
    b += f'<g class="ph"><rect x="{sx}" y="198" width="1.5" height="156" fill="{INK}" opacity=".7"/></g>'
    b += f'<text class="m" x="690" y="386" font-size="11.5" fill="{SOFT}">preemptive round-robin</text>'
    b += f'<text class="m" x="690" y="402" font-size="10.5" fill="{DIM}">kernel tasks + user processes</text>'
    # chips
    b += f'<text class="m k" x="40" y="434" font-size="10.5" fill="{DIM}">IMPLEMENTED AND OBSERVED IN QEMU</text>'
    row1 = [("long-mode boot", "ok"), ("PMM", "ok"), ("VMM", "ok"), ("IDT + exceptions", "ok"), ("PIC + PIT", "ok"), ("scheduler", "ok"), ("user mode", "early"), ("RAM filesystem", "early")]
    x = 40
    for i, (t, k) in enumerate(row1):
        s, w = chip(x, 444, t, k)
        b += s.replace("<rect ", f'<rect class="cg" style="animation-delay:{i*.5}s" ', 1)
        x += w + 8
    b += f'<text class="m k" x="40" y="494" font-size="10.5" fill="{DIM}">PLANNED, NOT IMPLEMENTED</text>'
    row2 = [("kernel heap", "plan"), ("networking", "plan"), ("persistent storage", "plan"), ("native desktop", "plan"), ("security hardening", "plan")]
    x = 40
    for t, k in row2:
        s, w = chip(x, 504, t, k)
        b += s
        x += w + 8
    return doc(
        pid, H,
        "Samagra OS",
        "Samagra OS: an animated kernel observability view. An address-space map, privilege rings with system calls and an IRQ0 timer interrupt, and a round-robin scheduler across kernel tasks and a user process. Boot, memory, interrupts and scheduler are implemented in QEMU; user mode and a RAM-only filesystem are early; kernel heap, networking, persistent storage and a native desktop are planned.",
        b, TEAL, css, left="SAMAGRA·OS  //  KERNEL VIEWPORT", right="x86-64 · C + NASM · QEMU",
        note="Conceptual view stylised from the project's documented design. Not live telemetry.",
    )


# --------------------------------------------------------------------------- PRAHARI
def prahari():
    pid = "pr"
    H = 556
    css = """
.vf{animation:vf 10s ease-in-out infinite both}
@keyframes vf{0%{opacity:.25}6%{opacity:1}80%{opacity:1}92%,100%{opacity:.25}}
.sc{animation:sc 6s ease-in-out infinite alternate}
@keyframes sc{from{transform:translateX(-30px)}to{transform:translateX(34px)}}
.bp{animation:bp 2.6s ease-in-out infinite}
@keyframes bp{0%,100%{stroke-opacity:.45}50%{stroke-opacity:1}}
"""
    b = ""
    b += f'<text x="40" y="94" font-size="38" font-weight="700" fill="{INK}">PRAHARI</text>'
    b += f'<text class="m" x="42" y="120" font-size="13" fill="{MUT}">mine safety and compliance monitoring · explainable · traceable</text>'
    b += f'<rect x="676" y="72" width="284" height="30" rx="15" fill="{PANEL}" stroke="{AMB}" stroke-opacity=".7"/><text class="m k" x="818" y="91" font-size="11" fill="{AMB}" text-anchor="middle">SMART INDIA HACKATHON</text>'
    # chain
    hs = ["a3f9", "9c1e", "e04b", "57d2", "b81a", "4c6d"]
    acts = ["inspection", "violation", "alert", "report", "risk score"]
    for i in range(5):
        x = 41 + i * 192
        y = 150
        b += f'<rect x="{x}" y="{y}" width="150" height="104" rx="8" fill="{PANEL}" stroke="{LINE2}"/>'
        b += f'<rect class="vf" style="animation-delay:{i*1.4:.1f}s" x="{x}" y="{y}" width="150" height="104" rx="8" fill="none" stroke="{TEAL}" stroke-width="1.5"/>'
        b += f'<text class="m k" x="{x+14}" y="{y+24}" font-size="10.5" fill="{MUT}">BLOCK 0{i+1}</text>'
        b += f'<text class="m" x="{x+14}" y="{y+50}" font-size="13" fill="{INK}">hash {hs[i+1]}…</text>'
        b += f'<text class="m" x="{x+14}" y="{y+70}" font-size="13" fill="{DIM}">prev {hs[i]}…</text>'
        b += f'<text class="m" x="{x+14}" y="{y+92}" font-size="10.5" fill="{ICE}">{acts[i]}</text>'
        b += f'<g class="vf" style="animation-delay:{i*1.4:.1f}s"><circle cx="{x+130}" cy="{y+22}" r="8" fill="{TEAL}" fill-opacity=".18" stroke="{TEAL}"/><path d="M{x+126} {y+22}l3 3 6-6" fill="none" stroke="{TEAL}" stroke-width="1.8"/></g>'
        if i < 4:
            b += f'<path class="flow" d="M{x+150} {y+52}H{x+192}" stroke="{TEAL}" stroke-width="1.5" fill="none"/><path d="M{x+186} {y+47}l6 5-6 5" fill="none" stroke="{TEAL}"/>'
    b += f'<path d="M41 278H959" stroke="{LINE2}" stroke-dasharray="2 6"/>'
    b += pulse("M41 278H959", 7, 0, TEAL, 3.5)
    b += f'<text class="m" x="41" y="298" font-size="11.5" fill="{MUT}">verify walks the hash chain · each row stores a hash chained to the previous one</text>'
    b += f'<text class="m" x="959" y="298" font-size="10.5" fill="{DIM}" text-anchor="end">illustrative hashes</text>'
    # risk panel
    b += panel(40, 318, 440, 186, "02 · EXPLAINABLE RISK SCORE (0 TO 1)", AMB)
    b += f'<defs><linearGradient id="{pid}-rk" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}"/><stop offset=".7" stop-color="{AMB}"/><stop offset="1" stop-color="#F08A5E"/></linearGradient></defs>'
    b += f'<rect x="64" y="362" width="392" height="8" rx="4" fill="url(#{pid}-rk)" opacity=".85"/>'
    b += f'<path d="M{64+0.8*392} 354v24" stroke="{INK}" stroke-dasharray="2 3"/><text class="m" x="{64+0.8*392}" y="350" font-size="10.5" fill="{INK}" text-anchor="middle">alert at 0.8</text>'
    b += f'<text class="m" x="64" y="388" font-size="10.5" fill="{DIM}">0</text><text class="m" x="456" y="388" font-size="10.5" fill="{DIM}" text-anchor="end">1</text>'
    b += f'<g class="sc"><path d="M{64+0.62*392} 358l-6-9h12z" fill="{INK}"/></g>'
    rows = [("findings", .72), ("severity keywords", .55), ("compliance score", .38), ("inspection status", .62)]
    for i, (n, v) in enumerate(rows):
        y = 408 + i * 20
        b += f'<text class="m" x="64" y="{y}" font-size="11.5" fill="{SOFT}">{n}</text>'
        b += f'<rect x="240" y="{y-9}" width="216" height="8" rx="4" fill="#0B0F16" stroke="{LINE}"/><rect x="240" y="{y-9}" width="{216*v:.0f}" height="8" rx="4" fill="{AMB}" fill-opacity=".75"/>'
    b += f'<text class="m" x="64" y="494" font-size="10.5" fill="{DIM}">illustrative values · score is stored with its reasons</text>'
    # copilot panel
    b += panel(500, 318, 460, 186, "03 · PERMISSION-SCOPED COPILOT", AMB)
    cy = 420
    def node(x, w, t1, t2):
        return (f'<rect x="{x}" y="{cy-24}" width="{w}" height="48" rx="8" fill="#0B0F16" stroke="{LINE2}"/>'
                f'<text class="m" x="{x+w/2}" y="{cy-3}" font-size="12" fill="{INK}" text-anchor="middle">{t1}</text>'
                f'<text class="m" x="{x+w/2}" y="{cy+13}" font-size="10" fill="{MUT}" text-anchor="middle">{t2}</text>')
    b += node(520, 70, "question", "role: user")
    b += node(606, 86, "parse", "deterministic")
    b += f'<rect class="bp" x="706" y="{cy-50}" width="140" height="100" rx="10" fill="{AMB}" fill-opacity=".05" stroke="{AMB}" stroke-dasharray="5 4"/>'
    b += f'<text class="m k" x="776" y="{cy-34}" font-size="9.5" fill="{AMB}" text-anchor="middle">RBAC SCOPE</text>'
    b += node(716, 120, "retrieve", "role-visible mines")
    b += node(864, 86, "LLM", "narrates only")
    for x1, x2 in [(590, 606), (692, 706), (846, 864)]:
        b += f'<path class="flow" d="M{x1} {cy}H{x2}" stroke="{TEAL}" stroke-width="1.5"/>'
    b += pulse(f"M590 {cy}H950", 4.5, 0, "#C9FFF8")
    b += f'<text class="m" x="520" y="{cy+66}" font-size="10.5" fill="{DIM}">every number in an answer comes from the database</text>'
    return doc(
        pid, H,
        "PRAHARI",
        "PRAHARI: an animated compliance-monitoring view. A chain of audit blocks, each hash linked to the previous one, is verified in sequence. Below, an explainable risk score between 0 and 1 with its contributing factors, and a copilot flow where questions are parsed deterministically, answered from role-scoped database retrieval, and only then narrated by an LLM.",
        b, AMB, css, left="PRAHARI  //  AUDIT + RISK + COPILOT", right="NEXT.JS · PRISMA · POSTGRESQL",
        note="Conceptual illustration. Hashes and scores are illustrative, not data from a deployment.",
    )


# --------------------------------------------------------------------------- AkashaLens
def akashalens():
    pid = "ak"
    H = 520
    css = """
.cl{animation:cl 16s ease-in-out infinite}
@keyframes cl{0%,28%{opacity:1}40%,78%{opacity:0}90%,100%{opacity:1}}
.rc{animation:rc 16s ease-in-out infinite}
@keyframes rc{0%,28%{opacity:0}40%,78%{opacity:1}90%,100%{opacity:0}}
.sw{animation:sw 16s linear infinite}
@keyframes sw{0%,28%{transform:translateX(0);opacity:0}30%{opacity:1}40%{transform:translateX(256px);opacity:1}42%,100%{transform:translateX(256px);opacity:0}}
.dr{animation:dr 14s ease-in-out infinite alternate}
@keyframes dr{from{transform:translateX(-22px)}to{transform:translateX(26px)}}
.lb1{animation:cl 16s ease-in-out infinite}
.lb2{animation:rc 16s ease-in-out infinite}
"""
    defs = f"""
<filter id="{pid}-bl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>
<pattern id="{pid}-ht" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0V8" stroke="{TEAL}" stroke-opacity=".5" stroke-width="1"/></pattern>
"""
    cols, rows = 9, 6
    x0, y0, tw, th = 52, 150, 64, 44
    pal = [["#1A3B4D", "#1F4659"], ["#1E3F2C", "#285234", "#2F5F3C"], ["#4A5A2E", "#66763A"], ["#6B5B44", "#85735A"], ["#3A4B3C", "#455A47"]]

    def terrain(c, r):
        v = math.sin(c * 0.85 + 0.6) + math.cos(r * 1.25) + math.sin((c + r) * 0.62) + 0.5 * math.cos(c * 2.1 - r)
        idx = int((v + 3.0) / 6.0 * 5)
        idx = max(0, min(4, idx))
        grp = pal[idx]
        return grp[(c * 7 + r * 3) % len(grp)]

    in_region = lambda c, r: 3 <= c <= 6 and 1 <= r <= 4
    b = ""
    b += f'<text x="40" y="94" font-size="38" font-weight="700" fill="{INK}">AkashaLens</text>'
    b += f'<text class="m" x="42" y="120" font-size="13" fill="{MUT}">cloud removal for Sentinel-2 imagery · a U-Net reconstruction prototype</text>'
    b += f'<rect x="676" y="72" width="284" height="30" rx="15" fill="{PANEL}" stroke="{ICE}" stroke-opacity=".7"/><text class="m k" x="818" y="91" font-size="11" fill="{ICE}" text-anchor="middle">ISRO HACKATHON 2026</text>'
    letters = "ABCDEFGHI"
    for c in range(cols):
        b += f'<text class="m" x="{x0+c*tw+tw/2}" y="{y0-8}" font-size="10" fill="{DIM}" text-anchor="middle">{letters[c]}</text>'
    for r in range(rows):
        b += f'<text class="m" x="{x0-10}" y="{y0+r*th+th/2+4}" font-size="10" fill="{DIM}" text-anchor="end">{r+1}</text>'
    clouds, recon = "", ""
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * tw, y0 + r * th
            if not in_region(c, r):
                b += f'<rect x="{x}" y="{y}" width="{tw-1}" height="{th-1}" fill="{terrain(c, r)}"/>'
            else:
                # confidence: tiles far from the observed edge are less certain
                d = min(c - 3, 6 - c, r - 1, 4 - r)
                heat = [0.0, 0.22, 0.36][min(d, 2)]
                recon += f'<rect x="{x}" y="{y}" width="{tw-1}" height="{th-1}" fill="{terrain(c, r)}"/>'
                recon += f'<rect x="{x}" y="{y}" width="{tw-1}" height="{th-1}" fill="{AMB}" fill-opacity="{heat}"/>'
                recon += f'<rect x="{x}" y="{y}" width="{tw-1}" height="{th-1}" fill="url(#{pid}-ht)"/>'
                shade = ["#DCE4EE", "#C9D3E0", "#B9C5D4"][(c * 5 + r * 2) % 3]
                clouds += f'<rect x="{x}" y="{y}" width="{tw-1}" height="{th-1}" fill="{shade}"/>'
    rx0, ry0, rw, rh = x0 + 3 * tw, y0 + 1 * th, 4 * tw - 1, 4 * th - 1
    b += f'<g class="cl">{clouds}</g>'
    b += f'<g class="rc">{recon}<rect x="{rx0}" y="{ry0}" width="{rw}" height="{rh}" fill="none" stroke="{TEAL}" stroke-width="1.5" stroke-dasharray="6 4"/></g>'
    # drifting wisps (clipped to the grid)
    b += f'<clipPath id="{pid}-gc"><rect x="{x0}" y="{y0}" width="{cols*tw}" height="{rows*th}"/></clipPath>'
    b += f'<g clip-path="url(#{pid}-gc)"><g class="dr" filter="url(#{pid}-bl)" opacity=".55" fill="#E6EDF6">'
    for cx, cy, rr in [(rx0 + 40, ry0 + 36, 34), (rx0 + 110, ry0 + 60, 44), (rx0 + 190, ry0 + 40, 36), (rx0 + 150, ry0 + 120, 40), (rx0 + 60, ry0 + 130, 30), (x0 + 30, y0 + 20, 26), (x0 + 520, y0 + 220, 30)]:
        b += f'<circle cx="{cx}" cy="{cy}" r="{rr}"/>'
    b += "</g></g>"
    b += f'<g class="sw"><rect x="{rx0}" y="{ry0-6}" width="2" height="{rh+12}" fill="{TEAL}"/><rect x="{rx0-18}" y="{ry0-6}" width="18" height="{rh+12}" fill="{TEAL}" opacity=".12"/></g>'
    # legend
    ly = y0 + rows * th + 28
    b += f'<rect x="{x0}" y="{ly-9}" width="14" height="10" fill="{terrain(0,0)}"/><text class="m" x="{x0+22}" y="{ly}" font-size="11.5" fill="{SOFT}">observed</text>'
    b += f'<rect x="{x0+112}" y="{ly-9}" width="14" height="10" fill="#C9D3E0"/><text class="m" x="{x0+134}" y="{ly}" font-size="11.5" fill="{SOFT}">cloud</text>'
    b += f'<rect x="{x0+206}" y="{ly-9}" width="14" height="10" fill="url(#{pid}-ht)" stroke="{TEAL}" stroke-dasharray="3 2"/><text class="m" x="{x0+228}" y="{ly}" font-size="11.5" fill="{SOFT}">reconstructed</text>'
    b += f'<rect x="{x0+350}" y="{ly-9}" width="14" height="10" fill="{AMB}" fill-opacity=".5"/><text class="m" x="{x0+372}" y="{ly}" font-size="11.5" fill="{SOFT}">low confidence</text>'
    # pipeline
    nodes = [
        ("Sentinel-2 L1C", "Copernicus download, sorted by cloud cover"),
        ("Cloud mask", "rule-based: luminance + colour saturation"),
        ("U-Net", "3 down stages · L1 loss · Adam"),
        ("Reconstruction + confidence", "heatmap derived from the mask"),
    ]
    px, pw, ph = 676, 284, 56
    for i, (t, s) in enumerate(nodes):
        y = 150 + i * 80
        hi = TEAL if i == 2 else LINE2
        b += f'<rect x="{px}" y="{y}" width="{pw}" height="{ph}" rx="8" fill="{PANEL}" stroke="{hi}"/>'
        b += f'<text class="m k" x="{px+14}" y="{y+20}" font-size="9.5" fill="{DIM}">0{i+1}</text>'
        b += f'<text x="{px+40}" y="{y+24}" font-size="16" font-weight="600" fill="{INK}">{e(t)}</text>'
        b += f'<text class="m" x="{px+40}" y="{y+43}" font-size="10.5" fill="{MUT}">{e(s)}</text>'
        if i < 3:
            b += f'<path class="flow" d="M{px+pw/2} {y+ph}V{y+80}" stroke="{TEAL}" stroke-width="1.5"/>'
    b += pulse(f"M{px+pw/2} 206V374", 5, 0, "#C9FFF8")
    return doc(
        pid, H,
        "AkashaLens",
        "AkashaLens: an animated satellite tile grid. Clouds drift across a block of tiles, then a sweep reveals a reconstruction drawn with a dashed teal outline and hatching, with amber marking low-confidence regions. Beside it, the pipeline: Sentinel-2 imagery, a rule-based cloud mask, a U-Net, and a reconstruction with a confidence heatmap. A prototype trained on a tiny sample set.",
        b, ICE, css, defs=defs, left="AKASHALENS  //  TILE VIEWPORT", right="PYTORCH · U-NET · FLASK",
        note="Conceptual scene. Prototype: 3 sample pairs, no trained weights shipped, no accuracy claims.",
    )


# --------------------------------------------------------------------------- Tarang
def wave_path(amp, freq, phase, y0, step=25):
    pts = []
    for i in range(0, W + 1, step):
        env = math.sin(math.pi * i / W) ** 1.4
        pts.append((i, y0 + amp * env * math.sin(i / W * freq * 2 * math.pi + phase)))
    d = f"M{pts[0][0]} {pts[0][1]:.1f}"
    d += f" Q{(pts[0][0]+pts[1][0])/2:.1f} {pts[0][1]:.1f} {pts[1][0]} {pts[1][1]:.1f}"
    for x, y in pts[2:]:
        d += f" T{x} {y:.1f}"
    return d


def tarang():
    pid = "ta"
    H = 500
    css = """
.eq{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1.2s ease-in-out infinite alternate}
@keyframes eq{from{transform:scaleY(.22)}to{transform:scaleY(1)}}
.ly{animation:ly 9s steps(1) infinite}
@keyframes ly{0%,33%{opacity:1}34%,100%{opacity:.35}}
"""
    defs = f"""
<linearGradient id="{pid}-w" x1="0" x2="1"><stop offset="0" stop-color="{ICE}" stop-opacity="0"/><stop offset=".25" stop-color="{ICE}"/><stop offset=".6" stop-color="{VIO}"/><stop offset="1" stop-color="{VIO}" stop-opacity="0"/></linearGradient>
<linearGradient id="{pid}-b" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{VIO}" stop-opacity=".25"/><stop offset="1" stop-color="{ICE}"/></linearGradient>
"""
    b = ""
    b += f'<text x="40" y="104" font-size="60" font-weight="700" fill="{INK}" letter-spacing="-1.5">Tarang</text>'
    b += f'<text class="m" x="42" y="132" font-size="13" fill="{MUT}">a music-first web app · persistent player · documented design system</text>'
    # lyrics
    b += f'<text class="m k" x="640" y="74" font-size="10.5" fill="{DIM}">TIME-SYNCED LYRICS · PLACEHOLDER LINES</text>'
    for i, t in enumerate(["synced line, one", "synced line, two", "synced line, three"]):
        b += f'<text class="ly" style="animation-delay:{-(9-i*3)}s" x="640" y="{100+i*26}" font-size="{19 if i==1 else 17}" fill="{INK}">{t}</text>'
    # layered waves
    for amp, fr, ph, y0, op, sw, dur in [(58, 2.0, 0.0, 232, .95, 2.2, 7), (44, 3.0, 1.3, 232, .55, 1.6, 9), (30, 4.5, 2.4, 232, .32, 1.2, 11)]:
        d1 = wave_path(amp, fr, ph, y0)
        d2 = wave_path(amp * 0.8, fr, ph + 2.1, y0)
        d3 = wave_path(amp * 1.05, fr, ph + 4.2, y0)
        b += f'<path d="{d1}" fill="none" stroke="url(#{pid}-w)" stroke-width="{sw}" opacity="{op}"><animate attributeName="d" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.33;.66;1" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1" values="{d1};{d2};{d3};{d1}"/></path>'
    b += f'<path d="M40 232H960" stroke="{LINE2}" stroke-dasharray="2 6"/>'
    # equalizer
    n = 54
    bw = 10
    gap = (920 - n * bw) / (n - 1)
    for i in range(n):
        env = math.sin(math.pi * (i + .5) / n) ** 0.9
        h = 14 + 62 * env * (0.55 + 0.45 * abs(math.sin(i * 1.7)))
        x = 40 + i * (bw + gap)
        dur = 0.8 + (i * 37 % 11) / 10
        dl = -((i * 53) % 17) / 10
        b += f'<rect class="eq" style="animation-duration:{dur:.1f}s;animation-delay:{dl:.1f}s" x="{x:.1f}" y="{372-h:.1f}" width="{bw}" height="{h:.1f}" rx="2" fill="url(#{pid}-b)"/>'
    b += f'<path d="M40 374H960" stroke="{LINE2}"/>'
    # progress trace
    pd = "M40 396 " + " ".join(f"L{x} {396+4*math.sin(x/38):.1f}" for x in range(60, 961, 20))
    b += f'<path d="{pd}" fill="none" stroke="{LINE2}" stroke-width="2"/>'
    b += f'<path d="{pd}" pathLength="1" fill="none" stroke="{VIO}" stroke-width="2.4" stroke-dasharray="1 1" stroke-dashoffset="0.55" stroke-linecap="round"><animate attributeName="stroke-dashoffset" values="1;0" dur="14s" repeatCount="indefinite"/></path>'
    b += f'<circle r="5.5" fill="{INK}" cx="0" cy="0"><animateMotion dur="14s" repeatCount="indefinite" path="{pd}"/></circle>'
    # mini player
    b += f'<rect x="270" y="418" width="460" height="42" rx="21" fill="{PANEL}" stroke="{LINE2}"/>'
    b += f'<circle cx="296" cy="439" r="12" fill="{VIO}" fill-opacity=".2" stroke="{VIO}"/><path d="M292 433l11 6-11 6z" fill="{INK}"/>'
    b += f'<text x="322" y="436" font-size="14" font-weight="600" fill="{INK}">Seed track</text><text class="m" x="322" y="452" font-size="10.5" fill="{MUT}">demo audio · seed data · frontend only</text>'
    for i in range(6):
        b += f'<rect class="eq" style="animation-duration:{.7+i*.17:.2f}s;animation-delay:-{i*.3:.1f}s" x="{660+i*9}" y="430" width="5" height="18" rx="1.5" fill="{ICE}"/>'
    return doc(
        pid, H, "Tarang",
        "Tarang: layered animated waveforms, a rhythmic equalizer, a smooth playback-progress trace and a floating mini player labelled as seed data. Time-synced lyric lines highlight in turn. A frontend-only music web app.",
        b, VIO, css, defs=defs, left="TARANG  //  NOW PLAYING", right="NEXT.JS · FRAMER MOTION · ZUSTAND",
        note="Stylised audio scene. Seed data, no real catalogue, no album artwork.",
    )


# --------------------------------------------------------------------------- Rinti AI
def rinti():
    pid = "ri"
    H = 540
    css = """
.st{animation:st 12s ease-in-out infinite both}
@keyframes st{0%{stroke:#2A3345;fill:#0B0F16}6%,14%{stroke:#8CC8FF;fill:#0F1A26}22%,100%{stroke:#2A3345;fill:#0B0F16}}
.ci{animation:ci 12s ease-out infinite both}
@keyframes ci{0%,55%{opacity:0;transform:scale(.6)}62%,92%{opacity:1;transform:scale(1)}100%{opacity:0}}
.ty{animation:ty 12s steps(1) infinite}
"""
    b = ""
    b += f'<text x="40" y="94" font-size="38" font-weight="700" fill="{INK}">Rinti AI</text>'
    b += f'<text class="m" x="42" y="120" font-size="13" fill="{MUT}">research chat workspace · per-user memory · cited multi-step research</text>'
    b += f'<rect x="716" y="72" width="244" height="30" rx="15" fill="{PANEL}" stroke="{ICE}" stroke-opacity=".7"/><text class="m k" x="838" y="91" font-size="11" fill="{ICE}" text-anchor="middle">PRODUCT WORKFLOW VIEW</text>'
    # question
    b += panel(40, 144, 190, 290, "01 · QUESTION", ICE)
    b += f'<rect x="56" y="180" width="158" height="46" rx="6" fill="#0B0F16" stroke="{LINE2}"/>'
    for i, wd in enumerate([130, 96, 112]):
        b += f'<rect x="68" y="{192+i*11}" width="{wd*0.9:.0f}" height="4" rx="2" fill="{SOFT}" opacity=".55"/>'
    b += f'<text class="m" x="56" y="256" font-size="10.5" fill="{MUT}">user asks a question</text>'
    b += f'<text class="m" x="56" y="278" font-size="10.5" fill="{DIM}">per-user memory</text>'
    b += f'<rect x="56" y="288" width="158" height="34" rx="6" fill="none" stroke="{LINE2}" stroke-dasharray="3 4"/><text class="m" x="68" y="309" font-size="10.5" fill="{MUT}">memory items</text>'
    b += f'<text class="m" x="56" y="352" font-size="10.5" fill="{DIM}">Quick or Standard</text><text class="m" x="56" y="368" font-size="10.5" fill="{DIM}">research budget</text>'
    # stages
    b += panel(250, 144, 260, 290, "02 · PIPELINE STAGES", ICE)
    stages = ["intent detection", "query planning", "search", "page extraction", "claim evaluation", "synthesis"]
    for i, s in enumerate(stages):
        y = 184 + i * 40
        b += f'<rect class="st" style="animation-delay:{i*1.8:.1f}s" x="266" y="{y}" width="228" height="32" rx="6" fill="#0B0F16" stroke="{LINE2}" stroke-width="1.2"/>'
        b += f'<text class="m" x="280" y="{y+21}" font-size="9.5" fill="{DIM}">0{i+1}</text><text class="m" x="308" y="{y+21}" font-size="12.5" fill="{INK}">{s}</text>'
        if i < 5:
            b += f'<path d="M380 {y+32}v8" stroke="{ICE}" stroke-opacity=".6"/>'
    # sources
    b += panel(530, 144, 200, 290, "03 · SOURCES", ICE)
    for i in range(4):
        y = 172 + i * 62
        b += f'<rect x="546" y="{y}" width="168" height="52" rx="6" fill="#0B0F16" stroke="{LINE2}"/>'
        b += f'<circle cx="566" cy="{y+26}" r="10" fill="{ICE}" fill-opacity=".15" stroke="{ICE}"/><text class="m" x="566" y="{y+30}" font-size="11" fill="{ICE}" text-anchor="middle">{i+1}</text>'
        b += f'<rect x="586" y="{y+14}" width="{110-i*9}" height="4" rx="2" fill="{SOFT}" opacity=".55"/><rect x="586" y="{y+26}" width="{86+i*6}" height="4" rx="2" fill="{DIM}"/><rect x="586" y="{y+36}" width="{60+i*10}" height="4" rx="2" fill="{DIM}"/>'
    # answer
    b += panel(750, 144, 210, 290, "04 · CITED ANSWER", ICE)
    for i in range(7):
        wd = [176, 160, 172, 120, 168, 150, 90][i]
        b += f'<rect x="766" y="{182+i*20}" width="{wd*0.9:.0f}" height="5" rx="2.5" fill="{SOFT}" opacity=".6"/>'
    for i, (cx, cy) in enumerate([(886, 196), (846, 238), (880, 296)]):
        b += f'<g class="ci" style="animation-delay:{i*.9:.1f}s;transform-origin:{cx}px {cy}px;transform-box:view-box"><rect x="{cx-11}" y="{cy-11}" width="22" height="20" rx="5" fill="{ICE}" fill-opacity=".18" stroke="{ICE}"/><text class="m" x="{cx}" y="{cy+4}" font-size="11" fill="{ICE}" text-anchor="middle">{i+1}</text></g>'
    b += f'<text class="m" x="766" y="372" font-size="10.5" fill="{MUT}">numbered citations</text><text class="m" x="766" y="388" font-size="10.5" fill="{DIM}">link back to sources</text>'
    # flows
    for xa, xb in [(230, 250), (510, 530), (730, 750)]:
        b += f'<path class="flow" d="M{xa} 290H{xb}" stroke="{ICE}" stroke-width="1.6"/>'
    b += pulse("M230 290H750", 6, 0, "#DCEEFF")
    # session band
    b += f'<text class="m k" x="40" y="466" font-size="10.5" fill="{DIM}">ACCOUNT SESSIONS</text>'
    x = 40
    for t in ["Argon2 password hashing", "HttpOnly session cookies", "CSRF header check", "per-user daily caps"]:
        s, w = chip(x, 476, t, "ok")
        b += s
        x += w + 8
    return doc(
        pid, H, "Rinti AI",
        "Rinti AI: a product workflow view. A question moves through intent detection, query planning, search, page extraction, claim evaluation and synthesis, drawing on numbered sources and producing an answer with numbered citations. Account sessions use Argon2 hashing, HttpOnly cookies and CSRF checks.",
        b, ICE, css, left="RINTI·AI  //  RESEARCH WORKFLOW", right="FASTAPI · NEXT.JS · GROQ · TAVILY",
        note="Product workflow and evidence flow only. It does not depict model reasoning.",
    )


# --------------------------------------------------------------------------- Orbit OS
def orbit():
    pid = "ob"
    H = 480
    css = """
.fl{animation:fl 6s ease-in-out infinite alternate}
@keyframes fl{from{transform:translateY(0)}to{transform:translateY(-7px)}}
.ar{stroke-dasharray:90;animation:ar 6s ease-in-out infinite alternate}
@keyframes ar{from{stroke-dashoffset:60}to{stroke-dashoffset:18}}
.hl{animation:hl 8s ease-in-out infinite}
@keyframes hl{0%,40%{fill-opacity:.18}55%,90%{fill-opacity:.0}100%{fill-opacity:.18}}
"""
    defs = f"""
<linearGradient id="{pid}-gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".09"/><stop offset="1" stop-color="#FFFFFF" stop-opacity=".02"/></linearGradient>
<radialGradient id="{pid}-co" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{VIO}"/><stop offset="1" stop-color="{VIO}" stop-opacity="0"/></radialGradient>
<clipPath id="{pid}-ty"><rect x="318" y="370" width="0" height="20"><animate attributeName="width" values="0;0;74;74;74;0" keyTimes="0;.08;.4;.8;.95;1" dur="8s" repeatCount="indefinite"/></rect></clipPath>
"""
    def glass(x, y, w, h, label, delay, inner=""):
        return (f'<g class="fl" style="animation-delay:{delay}s;animation-duration:{5+delay}s"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="url(#{pid}-gl)" stroke="#FFFFFF" stroke-opacity=".16"/>'
                f'<text class="m k" x="{x+14}" y="{y+22}" font-size="10" fill="{MUT}">{label}</text>{inner}</g>')
    b = ""
    b += f'<text x="40" y="94" font-size="38" font-weight="700" fill="{INK}">Orbit OS</text>'
    b += f'<text class="m" x="42" y="120" font-size="13" fill="{MUT}">an interface exploration · borrows from operating-system design</text>'
    b += f'<rect x="676" y="72" width="284" height="30" rx="15" fill="{PANEL}" stroke="{VIO}" stroke-opacity=".7"/><text class="m k" x="818" y="91" font-size="11" fill="{VIO}" text-anchor="middle">MOCK DATA · NOT A REAL OS</text>'
    # main dashboard panel
    inner = f'<rect x="150" y="182" width="190" height="14" rx="4" fill="{SOFT}" opacity=".5"/><rect x="150" y="204" width="120" height="8" rx="4" fill="{DIM}"/>'
    for i in range(3):
        inner += f'<rect x="{150+i*104}" y="228" width="92" height="52" rx="8" fill="#FFFFFF" fill-opacity=".05" stroke="#FFFFFF" stroke-opacity=".1"/>'
    inner += f'<path d="M150 322 C190 296 220 330 262 306 S340 300 392 288 S440 314 470 296" fill="none" stroke="{VIO}" stroke-width="2"/>'
    b += glass(130, 150, 360, 190, "DASHBOARD", 0, inner)
    b += glass(510, 150, 170, 84, "WEATHER", 1, f'<circle cx="544" cy="204" r="12" fill="{AMB}" fill-opacity=".8"/><rect x="568" y="196" width="80" height="6" rx="3" fill="{SOFT}" opacity=".5"/><rect x="568" y="210" width="54" height="6" rx="3" fill="{DIM}"/>')
    b += glass(510, 250, 170, 90, "FOCUS TIMER", 2, f'<circle cx="560" cy="302" r="18" fill="none" stroke="{LINE2}" stroke-width="4"/><circle class="ar" cx="560" cy="302" r="18" fill="none" stroke="{ICE}" stroke-width="4" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="30" transform="rotate(-90 560 302)"/><rect x="592" y="294" width="64" height="6" rx="3" fill="{SOFT}" opacity=".5"/><rect x="592" y="308" width="40" height="6" rx="3" fill="{DIM}"/>')
    # orbit
    ox, oy = 830, 250
    b += f'<g transform="rotate(-22 {ox} {oy})">'
    b += f'<ellipse cx="{ox}" cy="{oy}" rx="118" ry="44" fill="none" stroke="{LINE2}"/><ellipse cx="{ox}" cy="{oy}" rx="82" ry="30" fill="none" stroke="{LINE2}" stroke-dasharray="3 6"/>'
    b += f'<circle cx="{ox}" cy="{oy}" r="30" fill="url(#{pid}-co)" opacity=".7"/><circle cx="{ox}" cy="{oy}" r="9" fill="{INK}"/>'
    p1 = f"M{ox+118} {oy} A118 44 0 1 1 {ox-118} {oy} A118 44 0 1 1 {ox+118} {oy}"
    p2 = f"M{ox-82} {oy} A82 30 0 1 0 {ox+82} {oy} A82 30 0 1 0 {ox-82} {oy}"
    b += f'<circle r="6" fill="{TEAL}"><animateMotion dur="12s" repeatCount="indefinite" path="{p1}"/></circle>'
    b += f'<circle r="4" fill="{VIO}"><animateMotion dur="7s" repeatCount="indefinite" path="{p2}"/></circle>'
    b += "</g>"
    b += f'<text class="m" x="{ox}" y="{oy+98}" font-size="11" fill="{DIM}" text-anchor="middle">orbit · satellites · modules</text>'
    # palette
    b += f'<g><rect x="250" y="360" width="430" height="92" rx="14" fill="#0D1119" stroke="{VIO}" stroke-opacity=".7"/>'
    b += f'<circle cx="276" cy="380" r="6" fill="none" stroke="{MUT}" stroke-width="1.6"/><path d="M280.5 384.5l5 5" stroke="{MUT}" stroke-width="1.6"/>'
    b += f'<text class="m" x="318" y="385" font-size="14" fill="{INK}" clip-path="url(#{pid}-ty)">weather</text>'
    b += f'<rect class="blink" x="396" y="372" width="2" height="16" fill="{VIO}"/>'
    b += f'<text class="m k" x="660" y="385" font-size="9.5" fill="{DIM}" text-anchor="end">COMMAND PALETTE</text>'
    b += f'<path d="M262 398H668" stroke="{LINE}"/>'
    b += f'<rect class="hl" x="258" y="404" width="414" height="20" rx="5" fill="{VIO}"/>'
    b += f'<text class="m" x="272" y="418" font-size="12" fill="{INK}">Weather · open forecast</text><text class="m" x="272" y="440" font-size="12" fill="{MUT}">Focus · start timer</text></g>'
    return doc(
        pid, H, "Orbit OS",
        "Orbit OS: floating glass panels for a dashboard, weather and a focus timer drift gently, a command palette types the word weather, and small satellites orbit a core. An interface experiment on mock data, not a real operating system.",
        b, VIO, css, defs=defs, left="ORBIT·OS  //  INTERFACE EXPERIMENT", right="NEXT.JS · FRAMER MOTION",
        note="Interface exploration. Mock data throughout. Not an operating system.",
    )


# --------------------------------------------------------------------------- AI workflow
def ai_workflow():
    pid = "aw"
    H = 540
    css = """
.gt{animation:gt 8s ease-in-out infinite}
@keyframes gt{0%,100%{stroke-opacity:.5}50%{stroke-opacity:1}}
"""
    def box(x, y, w, h, col, tag, name, lines):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{PANEL}" stroke="{col}" stroke-opacity=".8"/>'
        s += f'<text class="m k" x="{x+18}" y="{y+26}" font-size="10" fill="{col}">{tag}</text>'
        s += f'<text x="{x+18}" y="{y+54}" font-size="23" font-weight="700" fill="{INK}">{name}</text>'
        for i, l in enumerate(lines):
            s += f'<text class="m" x="{x+18}" y="{y+80+i*20}" font-size="12.5" fill="{SOFT}">{l}</text>'
        return s
    b = ""
    b += box(40, 150, 230, 170, TEAL, "HUMAN · ENGINEER", "Samudra", ["architecture", "direction", "review + validation"])
    b += box(380, 100, 260, 130, ICE, "AI ENGINEERING AGENT", "Claude Code", ["UI · UX · desktop design", "design tokens · docs"])
    b += box(380, 260, 260, 130, VIO, "AI ENGINEERING AGENT", "Antigravity", ["boot · memory · interrupts", "scheduler · drivers"])
    # repo
    b += f'<rect x="730" y="90" width="230" height="310" rx="12" fill="{PANEL}" stroke="{LINE2}"/>'
    b += f'<text class="m k" x="748" y="116" font-size="10" fill="{MUT}">ONE SHARED REPOSITORY</text>'
    ch = [(".agents/", "sync log · handoff notes"), ("docs/", "architecture · design"), ("API_CONTRACTS", "proposed > agreed > done"), ("git history", "small, described commits")]
    for i, (n, d) in enumerate(ch):
        y = 134 + i * 66
        b += f'<rect x="746" y="{y}" width="198" height="54" rx="8" fill="#0B0F16" stroke="{LINE}"/>'
        b += f'<text class="m" x="760" y="{y+23}" font-size="13" fill="{INK}">{n}</text><text class="m" x="760" y="{y+42}" font-size="10.5" fill="{MUT}">{d}</text>'
    # direction paths (teal)
    d1 = "M270 215 C320 215 330 165 380 165"
    d2 = "M270 255 C320 255 330 325 380 325"
    d3 = "M640 165 C690 165 690 200 730 200"
    d4 = "M640 325 C690 325 690 300 730 300"
    for d in (d1, d2, d3, d4):
        b += f'<path class="flow" d="{d}" fill="none" stroke="{TEAL}" stroke-width="1.8"/>'
    for i, d in enumerate((d1, d2, d3, d4)):
        b += pulse(d, 3.2, i * .4, "#C9FFF8")
    b += f'<text class="m k" x="282" y="240" font-size="9.5" fill="{TEAL}">DIRECTION</text>'
    # validation loop (amber)
    vp = "M845 400 V452 H155 V320"
    b += f'<path d="{vp}" fill="none" stroke="{AMB}" stroke-width="1.8" stroke-dasharray="6 6" class="gt"/>'
    b += f'<path d="M149 332l6-12 6 12" fill="none" stroke="{AMB}" stroke-width="1.8"/>'
    b += pulse(vp, 6, 0, AMB, 3.6)
    b += f'<rect x="345" y="436" width="310" height="32" rx="16" fill="{BG}" stroke="{AMB}" stroke-opacity=".8"/>'
    b += f'<text class="m k" x="500" y="456" font-size="11" fill="{AMB}" text-anchor="middle">REVIEW · RUN · ACCEPT OR REJECT</text>'
    b += f'<text class="m k" x="165" y="388" font-size="9.5" fill="{AMB}">VALIDATION</text>'
    return doc(
        pid, H, "Engineering with AI",
        "Workflow diagram. Samudra, a human engineer, sets architecture and direction. Direction flows to two AI engineering agents: Claude Code for UI, UX, design tokens and documentation, and Antigravity for boot, memory, interrupts, scheduler and drivers. Both work in one shared repository through sync logs, handoff notes, architecture docs, API contracts and commits. A validation loop of review, run and accept or reject returns to Samudra.",
        b, TEAL, css, left="HUMAN-LED  //  AI-IMPLEMENTED", right="CLAUDE CODE · ANTIGRAVITY",
        note="The agents are tools, not people. Scope, interfaces and trade-offs stay with Samudra.",
    )


# --------------------------------------------------------------------------- capabilities index
def capabilities():
    pid = "cp"
    rows = [
        ("LANGUAGES", ["TypeScript", "JavaScript", "Python", "C", "x86-64 Assembly"], TEAL),
        ("SYSTEMS", ["Clang", "LLD", "NASM", "QEMU", "Git", "Docker"], TEAL),
        ("WEB", ["React", "Next.js", "Tailwind", "Framer Motion", "GSAP", "Three.js"], ICE),
        ("AI / VISION", ["PyTorch", "NumPy", "SciPy", "scikit-image", "LLM APIs"], VIO),
        ("DESIGN", ["Figma", "Design Systems", "Motion Design"], AMB),
    ]
    H = 80 + len(rows) * 58 + 40
    css = """
.rw{animation:rw 10s ease-in-out infinite both}
@keyframes rw{0%,100%{opacity:.7}8%,18%{opacity:1}28%{opacity:.7}}
"""
    b = ""
    for i, (label, items, col) in enumerate(rows):
        y = 80 + i * 58
        b += f'<g class="rw" style="animation-delay:{i*1.6:.1f}s">'
        b += f'<text class="m" x="40" y="{y+22}" font-size="11" fill="{DIM}">0{i+1}</text>'
        b += f'<text class="m k" x="72" y="{y+22}" font-size="12" fill="{col}">{label}</text>'
        x = 230
        for it in items:
            w = int(len(it) * 8.4 + 28)
            b += f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="{PANEL}" stroke="{LINE2}"/><circle cx="{x+15}" cy="{y+17}" r="3" fill="{col}"/><text class="m" x="{x+26}" y="{y+22}" font-size="13.5" fill="{INK}">{e(it)}</text>'
            x += w + 10
        b += f'<path d="M40 {y+46}H960" stroke="{LINE}"/></g>'
    return doc(
        pid, H, "Technical capabilities",
        "Technical index. Languages: TypeScript, JavaScript, Python, C, x86-64 Assembly. Systems: Clang, LLD, NASM, QEMU, Git, Docker. Web: React, Next.js, Tailwind, Framer Motion, GSAP, Three.js. AI and vision: PyTorch, NumPy, SciPy, scikit-image, LLM APIs. Design: Figma, Design Systems, Motion Design.",
        b, TEAL, css, left="TECHNICAL INDEX", right="5 DOMAINS", note="",
    )


# --------------------------------------------------------------------------- closing
def closing():
    pid = "cl"
    H = 330
    css = """
.ping{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}
@keyframes ping{0%{transform:scale(.4);opacity:.9}100%{transform:scale(2.4);opacity:0}}
"""
    b = ""
    b += f'<circle class="ping" cx="52" cy="104" r="9" fill="none" stroke="{TEAL}"/><circle cx="52" cy="104" r="5" fill="{TEAL}"/>'
    b += f'<text class="m k" x="72" y="109" font-size="12.5" fill="{TEAL}">AVAILABLE</text>'
    b += f'<text x="40" y="184" font-size="60" font-weight="700" fill="{INK}" letter-spacing="-2">Open to internships<tspan fill="{TEAL}">.</tspan></text>'
    b += f'<text class="m" x="42" y="222" font-size="15" fill="{SOFT}">systems  ·  AI  ·  product engineering</text>'
    facts = [("LOCATION", "Bangalore, India"), ("UNIVERSITY", "Chanakya University"), ("PORTFOLIO", "sam-sportfolio.vercel.app"), ("EMAIL", "hi.samsstudio@gmail.com")]
    for i, (k, v) in enumerate(facts):
        x = 40 + i * 232
        b += f'<path d="M{x} 258H{x+210}" stroke="{LINE2}"/><text class="m k" x="{x}" y="280" font-size="10" fill="{DIM}">{k}</text><text class="m" x="{x}" y="300" font-size="13.5" fill="{INK}">{e(v)}</text>'
    return doc(
        pid, H, "Samudra Kar. Open to internships.",
        "Closing card. Samudra Kar is open to internships. Bangalore, India. Chanakya University. Portfolio at sam-sportfolio.vercel.app. Email hi.samsstudio@gmail.com.",
        b, TEAL, css, left="END OF PROFILE  //  SAMUDRA·KAR", right="BANGALORE · IN", note="",
    )


SCENES = {
    "about.svg": about,
    "samagra-os.svg": samagra,
    "prahari.svg": prahari,
    "akashalens.svg": akashalens,
    "tarang.svg": tarang,
    "rinti-ai.svg": rinti,
    "orbit-os.svg": orbit,
    "ai-workflow.svg": ai_workflow,
    "capabilities.svg": capabilities,
    "closing.svg": closing,
}


def check():
    ok = True
    ids_seen = {}
    for name in SCENES:
        p = OUT / name
        txt = p.read_text(encoding="utf-8")
        try:
            xml.dom.minidom.parseString(txt)
        except Exception as ex:
            print(f"XML ERROR {name}: {ex}")
            ok = False
            continue
        if "<script" in txt or "http://" in txt.replace("http://www.w3.org/2000/svg", "") or "href=" in txt:
            print(f"UNSAFE CONTENT in {name}")
            ok = False
        if "viewBox=" not in txt:
            print(f"NO VIEWBOX {name}")
            ok = False
        for i in re.findall(r'\bid="([^"]+)"', txt):
            if i in ids_seen and ids_seen[i] != name:
                print(f"DUPLICATE ID {i}: {ids_seen[i]} and {name}")
                ok = False
            ids_seen[i] = name
        print(f"{name:20s} {len(txt)/1024:5.1f} KB  ok")
    return ok


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in SCENES.items():
        (OUT / name).write_text(fn(), encoding="utf-8", newline="\n")
    sys.exit(0 if check() else 1)


if __name__ == "__main__":
    main()
