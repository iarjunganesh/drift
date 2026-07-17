#!/usr/bin/env python3
"""Generate the DRIFT presentation architecture diagram (dark + light SVG).

This is a hand-authored, presentation-grade companion to the canonical
Mermaid source (`arch-pipeline.mmd`). The Mermaid file remains the maintainable
system-of-record; this presentation diagram (`arch-*.svg`) dramatizes the same
first-look "trust boundary" story for slides, the demo video, and the README
top.

One source of truth, two themes. Run:

    python build_arch.py            # writes both SVGs
    # then rasterize to PNG (needs frontend/ deps):
    node build_arch_raster.mjs

Nothing is hand-edited in the SVG output; change this file and regenerate.
"""

from __future__ import annotations

import html
from dataclasses import dataclass

W, H = 1712, 940


# --------------------------------------------------------------------------- #
# Theme
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Theme:
    name: str
    bg0: str
    bg1: str
    grid: str
    panel_stroke: str
    ink: str          # primary text on background
    ink_soft: str     # secondary text on background
    line: str         # pipeline connector
    dep: str          # dashed dependency connector
    # per-kind node styling: (fill, stroke, text)
    kinds: dict
    zone_untrusted: str
    zone_quarantine: str
    zone_trusted: str
    gate_fill0: str
    gate_fill1: str
    gate_stroke: str
    gate_ink: str
    boundary: str
    # DRIFT signature gradient (teal → indigo), theme-adapted. Kept identical
    # to assets/brand/build_banner.py so brand and diagram read as one system.
    brand0: str = "#2dd4bf"
    brand1: str = "#818cf8"


DARK = Theme(
    name="dark",
    bg0="#0b1020",
    bg1="#060912",
    grid="#1b2438",
    panel_stroke="#233047",
    ink="#f8fafc",
    ink_soft="#94a3b8",
    line="#7c8aa5",
    dep="#5b6b86",
    kinds={
        "source": ("#0f766e", "#2dd4bf", "#ecfeff"),
        "agent":  ("#312e81", "#a5b4fc", "#eef2ff"),
        "data":   ("#164e63", "#38d9f0", "#ecfeff"),
        "model":  ("#7c2d12", "#fb923c", "#fff7ed"),
        "api":    ("#166534", "#4ade80", "#f0fdf4"),
        "user":   ("#6b21a8", "#d8b4fe", "#faf5ff"),
        "note":   ("#33415560", "#7c8aa5", "#cbd5e1"),
    },
    zone_untrusted="#f43f5e",
    zone_quarantine="#f59e0b",
    zone_trusted="#10b981",
    gate_fill0="#0f3f2f",
    gate_fill1="#12261f",
    gate_stroke="#fbbf24",
    gate_ink="#fef9c3",
    boundary="#fbbf24",
)

LIGHT = Theme(
    name="light",
    bg0="#f6f8fc",
    bg1="#e9eef7",
    grid="#dbe3ef",
    panel_stroke="#cbd5e1",
    ink="#0f172a",
    ink_soft="#64748b",
    line="#7688a1",
    dep="#94a3b8",
    kinds={
        "source": ("#d5f5f0", "#0d9488", "#0f3d38"),
        "agent":  ("#e5e7ff", "#4f46e5", "#1e1b4b"),
        "data":   ("#d4f2fb", "#0891b2", "#0c3a47"),
        "model":  ("#ffe9d6", "#ea580c", "#7c2d12"),
        "api":    ("#d8f5e2", "#16a34a", "#14532d"),
        "user":   ("#efe1fb", "#9333ea", "#4a1478"),
        "note":   ("#eef2f8", "#94a3b8", "#475569"),
    },
    zone_untrusted="#e11d48",
    zone_quarantine="#d97706",
    zone_trusted="#059669",
    gate_fill0="#ecfdf5",
    gate_fill1="#d1fae5",
    gate_stroke="#b45309",
    gate_ink="#7c2d12",
    boundary="#b45309",
    brand0="#0d9488",
    brand1="#4f46e5",
)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------- #
# Primitives
# --------------------------------------------------------------------------- #
FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


def text(x, y, s, *, size, fill, weight=400, anchor="start", spacing=None,
         opacity=1.0):
    ls = f' letter-spacing="{spacing}"' if spacing is not None else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}"{ls}{op}>{esc(s)}</text>'
    )


def rrect(x, y, w, h, r, *, fill, stroke="none", sw=0, opacity=1.0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{r}" ry="{r}" fill="{fill}"{st}{op}{extra}/>'
    )


class Node:
    def __init__(self, cx, cy, w, h, kind, title, subtitle=None,
                 badge=None, tag=None, tag_color=None):
        self.cx, self.cy, self.w, self.h = cx, cy, w, h
        self.kind = kind
        self.title = title
        self.subtitle = subtitle
        self.badge = badge
        self.tag = tag
        self.tag_color = tag_color

    @property
    def x(self):
        return self.cx - self.w / 2

    @property
    def y(self):
        return self.cy - self.h / 2

    def top(self):
        return (self.cx, self.y)

    def bottom(self):
        return (self.cx, self.y + self.h)

    def left(self):
        return (self.x, self.cy)

    def right(self):
        return (self.x + self.w, self.cy)

    def render(self, t: Theme):
        fill, stroke, ink = t.kinds[self.kind]
        parts = [
            f'<g filter="url(#soft)">',
            rrect(self.x, self.y, self.w, self.h, 14, fill=fill,
                  stroke=stroke, sw=1.6),
            "</g>",
        ]
        # subtle top sheen
        parts.append(
            rrect(self.x + 1, self.y + 1, self.w - 2, self.h * 0.5, 13,
                  fill="url(#sheen)", opacity=0.12)
        )
        tx = self.cx
        if self.subtitle:
            parts.append(text(tx, self.cy - 4, self.title, size=17.5,
                              fill=ink, weight=700, anchor="middle"))
            parts.append(text(tx, self.cy + 16, self.subtitle, size=12.5,
                              fill=ink, weight=400, anchor="middle",
                              opacity=0.82))
        else:
            parts.append(text(tx, self.cy + 6, self.title, size=17.5,
                              fill=ink, weight=700, anchor="middle"))
        # badge (numbered stage)
        if self.badge is not None:
            bx, by = self.x + 20, self.y + 20
            parts.append(
                f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="13" fill="{stroke}" '
                f'opacity="0.95"/>'
            )
            parts.append(text(bx, by + 5, str(self.badge), size=14,
                              fill=fill, weight=800, anchor="middle"))
        # tag pill (e.g. QUARANTINED)
        if self.tag:
            tc = self.tag_color or stroke
            tw = 9 + len(self.tag) * 6.3
            pillx = self.x + self.w - tw - 12
            pilly = self.y + self.h - 22
            parts.append(rrect(pillx, pilly, tw, 17, 8, fill=tc, opacity=0.9))
            parts.append(text(pillx + tw / 2, pilly + 12.5, self.tag, size=10,
                              fill="#0b1020" if t.name == "dark" else "#ffffff",
                              weight=800, anchor="middle", spacing="0.06em"))
        return "".join(parts)


def arrow(p0, p1, *, color, marker, dashed=False, width=2.4, label=None,
          t: Theme = DARK, label_dy=-8):
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    x0, y0 = p0
    x1, y1 = p1
    line = (
        f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
        f'stroke="{color}" stroke-width="{width}"{dash} '
        f'stroke-linecap="round" marker-end="url(#{marker})"/>'
    )
    out = [line]
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + label_dy
        lw = 12 + len(label) * 6.0
        out.append(rrect(mx - lw / 2, my - 13, lw, 18, 9, fill=t.bg0,
                         opacity=0.92))
        out.append(text(mx, my, label, size=11.5, fill=t.ink_soft,
                       weight=600, anchor="middle"))
    return "".join(out)


def elbow(p0, p1, midx, *, color, marker, dashed=False, width=2.4,
          label=None, t: Theme = DARK):
    """Orthogonal connector: horizontal to midx, vertical, into p1."""
    x0, y0 = p0
    x1, y1 = p1
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    path = (
        f'<path d="M {x0:.1f} {y0:.1f} H {midx:.1f} V {y1:.1f} H {x1:.1f}" '
        f'fill="none" stroke="{color}" stroke-width="{width}"{dash} '
        f'stroke-linejoin="round" stroke-linecap="round" '
        f'marker-end="url(#{marker})"/>'
    )
    out = [path]
    if label:
        my = (y0 + y1) / 2
        lw = 12 + len(label) * 6.0
        out.append(rrect(midx - lw / 2, my - 9, lw, 18, 9, fill=t.bg0,
                         opacity=0.92))
        out.append(text(midx, my + 4.5, label, size=11.5, fill=t.ink_soft,
                       weight=600, anchor="middle"))
    return "".join(out)


def zone_panel(x, y, w, h, *, tint, header, sub, t: Theme):
    parts = [
        rrect(x, y, w, h, 20, fill=tint, opacity=0.07),
        rrect(x, y, w, h, 20, fill="none", stroke=tint, sw=1.4, opacity=0.55,
              extra=' stroke-dasharray="2 6"'),
    ]
    # header chip
    chip_w = 14 + len(header) * 8.6
    parts.append(rrect(x + 18, y - 15, chip_w, 30, 15, fill=tint,
                       opacity=0.92, extra=' filter="url(#soft)"'))
    parts.append(text(x + 18 + chip_w / 2, y + 5, header, size=13.5,
                     fill="#0b1020" if t.name == "dark" else "#ffffff",
                     weight=800, anchor="middle", spacing="0.08em"))
    # sub caption, bottom-left inside the panel
    parts.append(text(x + 22, y + h - 20, sub, size=11.5, fill=t.ink_soft,
                     weight=500, anchor="start", opacity=0.85))
    return "".join(parts)


def person_glyph(cx, cy, color):
    return (
        f'<g stroke="{color}" stroke-width="2.4" fill="none" '
        f'stroke-linecap="round">'
        f'<circle cx="{cx:.1f}" cy="{cy - 7:.1f}" r="6"/>'
        f'<path d="M {cx - 10:.1f} {cy + 11:.1f} '
        f'a 10 9 0 0 1 20 0"/></g>'
    )


def lock_glyph(cx, cy, color, ink):
    return (
        f'<g>'
        f'<rect x="{cx - 11:.1f}" y="{cy - 2:.1f}" width="22" height="17" '
        f'rx="4" fill="{color}"/>'
        f'<path d="M {cx - 7:.1f} {cy - 2:.1f} V {cy - 8:.1f} '
        f'a 7 7 0 0 1 14 0 V {cy - 2:.1f}" fill="none" stroke="{color}" '
        f'stroke-width="2.6"/>'
        f'<circle cx="{cx:.1f}" cy="{cy + 6:.1f}" r="2.4" fill="{ink}"/>'
        f'</g>'
    )


# --------------------------------------------------------------------------- #
# Compose
# --------------------------------------------------------------------------- #
def build(t: Theme) -> str:
    S = []
    S.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="{FONT}">'
    )
    # ---- defs ----
    S.append("<defs>")
    S.append(
        f'<radialGradient id="bg" cx="30%" cy="0%" r="120%">'
        f'<stop offset="0%" stop-color="{t.bg0}"/>'
        f'<stop offset="100%" stop-color="{t.bg1}"/></radialGradient>'
    )
    S.append(
        '<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="0.9"/>'
        '<stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>'
        '</linearGradient>'
    )
    S.append(
        f'<linearGradient id="gate" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{t.gate_fill0}"/>'
        f'<stop offset="100%" stop-color="{t.gate_fill1}"/></linearGradient>'
    )
    # DRIFT signature gradient (teal → indigo)
    S.append(
        f'<linearGradient id="word" x1="0" y1="0" x2="1" y2="0.3">'
        f'<stop offset="0%" stop-color="{t.brand0}"/>'
        f'<stop offset="100%" stop-color="{t.brand1}"/></linearGradient>'
    )
    S.append(
        f'<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{t.brand0}"/>'
        f'<stop offset="100%" stop-color="{t.brand1}" '
        f'stop-opacity="0"/></linearGradient>'
    )
    # soft drop shadow
    S.append(
        '<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="3" stdDeviation="5" '
        'flood-color="#000000" flood-opacity="0.28"/></filter>'
    )
    # gate glow
    S.append(
        f'<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="10" '
        f'flood-color="{t.gate_stroke}" flood-opacity="0.55"/></filter>'
    )
    for mid, col in (("ah", t.line), ("ahflow", t.zone_trusted),
                     ("ahdash", t.dep), ("ahgold", t.gate_stroke)):
        S.append(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 L3 5 Z" fill="{col}"/></marker>'
        )
    S.append("</defs>")

    # ---- background ----
    S.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    # faint dot grid
    dots = ['<g opacity="0.5">']
    for gy in range(150, H - 60, 34):
        for gx in range(40, W - 20, 34):
            dots.append(
                f'<circle cx="{gx}" cy="{gy}" r="1" fill="{t.grid}"/>'
            )
    dots.append("</g>")
    S.append("".join(dots))

    # ---- header ----
    S.append(text(52, 52, "DRIFT · RELEASE INTELLIGENCE FOR GPU & AI INFRASTRUCTURE",
                  size=14, fill="url(#word)", weight=800, spacing="0.16em"))
    S.append(rrect(52, 62, 232, 3, 1.5, fill="url(#rule)"))
    S.append(text(52, 92, "Release notes are untrusted input —",
                  size=29, fill=t.ink, weight=800))
    S.append(text(52, 126, "a human reviewer is the only bridge to what an engineer sees.",
                  size=29, fill=t.ink_soft, weight=500))
    # right-side stat pills
    pills = [("6", "typed stages"), ("2", "model passes"), ("1", "human gate")]
    px = W - 52
    for num, lab in reversed(pills):
        pw = 30 + len(lab) * 7.2
        px -= pw
        S.append(rrect(px, 62, pw, 40, 12, fill=t.kinds["agent"][0],
                       stroke=t.kinds["agent"][1], sw=1.3, opacity=0.95))
        S.append(text(px + 20, 88, num, size=20, fill=t.kinds["agent"][1],
                      weight=800, anchor="middle"))
        S.append(text(px + 36, 79, lab.split()[0], size=11, fill=t.ink,
                      weight=600))
        S.append(text(px + 36, 93, lab.split()[1] if len(lab.split()) > 1 else "",
                      size=11, fill=t.ink_soft, weight=500))
        px -= 12

    # ---- zone panels ----
    zy, zh = 176, 604
    zaw = 408          # untrusted + quarantine width (widened to balance trusted)
    za_x = 44
    zb_x = 488
    gate_x, gate_w = 944, 150
    zc_x = 1136
    zc_w = W - zc_x - 44

    S.append(zone_panel(za_x, zy, zaw, zh, tint=t.zone_untrusted,
                        header="UNTRUSTED  INPUT", sub="primary release feeds",
                        t=t))
    S.append(zone_panel(zb_x, zy, zaw, zh, tint=t.zone_quarantine,
                        header="QUARANTINE  ·  MACHINE",
                        sub="drafts · nobody trusts yet", t=t))
    S.append(zone_panel(zc_x, zy, zc_w, zh, tint=t.zone_trusted,
                        header="TRUSTED  ·  PUBLISHED",
                        sub="reviewed evidence only", t=t))

    # ---- trust boundary line at gate right edge ----
    bx = gate_x + gate_w + 20
    S.append(
        f'<line x1="{bx}" y1="{zy - 24}" x2="{bx}" y2="{zy + zh + 24}" '
        f'stroke="{t.boundary}" stroke-width="2" stroke-dasharray="3 7" '
        f'opacity="0.8"/>'
    )
    S.append(
        f'<g transform="translate({bx - 12},{zy + zh + 4}) rotate(-90)">'
        + text(0, 0, "TRUST BOUNDARY", size=11, fill=t.boundary, weight=800,
               spacing="0.22em")
        + "</g>"
    )

    # ---- Zone A nodes ----
    caz = za_x + zaw / 2
    nA1 = Node(caz, 236, zaw - 56, 66, "source", "GitHub Atom feeds",
               "PyTorch · vLLM · TensorRT · …")
    nA2 = Node(caz, 344, zaw - 56, 66, "agent", "Scout",
               "normalize + dedupe", badge=1)
    nA3 = Node(caz, 444, zaw - 56, 56, "data", "raw_items · Postgres")
    nA4 = Node(caz, 552, zaw - 56, 66, "agent", "Synthesizer",
               "embed · cluster · classify", badge=2)
    nA5 = Node(caz, 652, zaw - 72, 48, "model", "text-embedding-3-small")
    for n in (nA1, nA2, nA3, nA4, nA5):
        S.append(n.render(t))

    # ---- Zone B nodes ----
    cbz = zb_x + zaw / 2
    nB1 = Node(cbz, 236, zaw - 56, 66, "agent", "Claim extractor",
               "facts · inferences · checks", badge=3)
    nB2 = Node(cbz, 344, zaw - 56, 66, "agent", "Separate verifier",
               "reject unsupported claims", badge=4)
    nB3 = Node(cbz, 452, zaw - 56, 74, "data", "draft insights + frozen spans",
               "offsets · SHA-256 · pgvector", tag="QUARANTINED",
               tag_color=t.zone_quarantine)
    for n in (nB1, nB2, nB3):
        S.append(n.render(t))
    # model dependency (LLM tiers used by claim extraction + verification)
    nBm = Node(cbz, 606, zaw - 72, 54, "model", "GPT-5.6 tiers",
               "Luna · Terra · Sol")
    S.append(nBm.render(t))

    # ---- Gate (focal element) ----
    gcx = gate_x + gate_w / 2
    gy0, gy1 = 224, 566
    S.append(
        f'<g filter="url(#glow)">'
        + rrect(gate_x, gy0, gate_w, gy1 - gy0, 20, fill="url(#gate)",
                stroke=t.gate_stroke, sw=2.4)
        + "</g>"
    )
    S.append(rrect(gate_x + 2, gy0 + 2, gate_w - 4, (gy1 - gy0) * 0.4, 18,
                   fill="url(#sheen)", opacity=0.10))
    # badge 5
    S.append(f'<circle cx="{gcx}" cy="{gy0 + 34}" r="18" '
             f'fill="{t.gate_stroke}"/>')
    S.append(text(gcx, gy0 + 40, "5", size=20, fill=t.gate_fill1,
                  weight=800, anchor="middle"))
    S.append(person_glyph(gcx, gy0 + 92, t.gate_ink))
    S.append(text(gcx, gy0 + 138, "HUMAN", size=17, fill=t.gate_ink,
                  weight=800, anchor="middle", spacing="0.04em"))
    S.append(text(gcx, gy0 + 160, "REVIEW GATE", size=17, fill=t.gate_ink,
                  weight=800, anchor="middle", spacing="0.02em"))
    S.append(text(gcx, gy0 + 186, "notes required", size=12.5,
                  fill=t.gate_ink, weight=500, anchor="middle", opacity=0.85))
    S.append(lock_glyph(gcx, gy0 + 232, t.gate_stroke, t.gate_fill1))
    S.append(text(gcx, gy0 + 286, "verifier-passed", size=11.5,
                  fill=t.gate_ink, weight=500, anchor="middle", opacity=0.8))
    S.append(text(gcx, gy0 + 302, "drafts only", size=11.5,
                  fill=t.gate_ink, weight=500, anchor="middle", opacity=0.8))
    # HUMAN-GATED brand badge directly under the gate
    hg, hgink = "HUMAN-GATED", "#04231a" if t.name == "dark" else "#ffffff"
    hgw = 26 + len(hg) * 8.6
    S.append(rrect(gcx - hgw / 2, gy1 + 16, hgw, 30, 15, fill=t.zone_trusted,
                   extra=' filter="url(#soft)"'))
    S.append(text(gcx, gy1 + 36, hg, size=13.5, fill=hgink, weight=800,
                  anchor="middle", spacing="0.08em"))

    # ---- Zone C nodes ----
    ccz = zc_x + zc_w / 2
    nC1 = Node(ccz, 236, zc_w - 64, 66, "data", "reviewed insights + vectors",
               "Postgres · pgvector")
    nC2 = Node(ccz, 344, zc_w - 64, 66, "agent", "Briefing",
               "rank + retrieve", badge=6)
    nC3 = Node(ccz, 452, zc_w - 64, 66, "api", "FastAPI",
               "briefing · search · chat")
    nEng = Node(ccz - 96, 566, 168, 56, "user", "Engineer")
    nFix = Node(ccz + 104, 566, 196, 56, "note", "Fixture mode",
                "no-key · deterministic")
    for n in (nC1, nC2, nC3, nEng, nFix):
        S.append(n.render(t))

    # ---- connectors ----
    a = lambda p0, p1, **k: S.append(arrow(p0, p1, t=t, **k))
    e = lambda p0, p1, mx, **k: S.append(elbow(p0, p1, mx, t=t, **k))

    # Zone A vertical spine
    a(nA1.bottom(), (nA2.cx, nA2.y), color=t.line, marker="ah")
    a(nA2.bottom(), (nA3.cx, nA3.y), color=t.line, marker="ah")
    a(nA3.bottom(), (nA4.cx, nA4.y), color=t.line, marker="ah")
    # A -> B handoff
    e(nA4.right(), nB1.left(), (zb_x + za_x + zaw) / 2, color=t.line,
      marker="ah", label="substantive changes")
    # Zone B vertical spine
    a(nB1.bottom(), (nB2.cx, nB2.y), color=t.line, marker="ah")
    a(nB2.bottom(), (nB3.cx, nB3.y), color=t.line, marker="ah")
    # model deps (dashed): Synthesizer embeds; claim/verify call the LLM tiers
    a(nA4.bottom(), (nA5.cx, nA5.y), color=t.dep, marker="ahdash",
      dashed=True, width=1.8, label="embed", label_dy=0)
    railx = zb_x + 14
    e(nB1.left(), (nBm.x, nBm.cy - 8), railx, color=t.dep, marker="ahdash",
      dashed=True, width=1.8)
    e(nB2.left(), (nBm.x, nBm.cy + 8), railx, color=t.dep, marker="ahdash",
      dashed=True, width=1.8)
    # B(drafts) -> Gate
    a(nB3.right(), (gate_x, 452), color=t.gate_stroke, marker="ahgold",
      width=2.6, label="submit")
    # Gate -> Zone C (published)
    e((gate_x + gate_w, 300), nC1.left(), (gate_x + gate_w + zc_x) / 2 + 6,
      color=t.zone_trusted, marker="ahflow", width=2.8, label="published")
    # Zone C vertical spine
    a(nC1.bottom(), (nC2.cx, nC2.y), color=t.line, marker="ah")
    a(nC2.bottom(), (nC3.cx, nC3.y), color=t.line, marker="ah")
    # FastAPI -> Engineer (answer)
    e(nC3.bottom(), nEng.top(), nEng.cx, color=t.zone_trusted,
      marker="ahflow", width=2.4)
    # Fixture -> FastAPI
    e(nFix.top(), (nC3.cx + 60, nC3.y + nC3.h), nFix.cx, color=t.ink_soft,
      marker="ah", dashed=True, width=2.0)
    # Engineer reviews (dashed up to gate)
    a((nEng.x, nEng.cy), (gate_x + gate_w + 8, gy1 - 30), color=t.dep,
      marker="ahdash", dashed=True, width=1.8, label="reviews",
      label_dy=-14)

    # answer caption near Engineer
    S.append(text(nEng.cx, nEng.cy + 52,
                  "what changed · why it matters · what to check",
                  size=11.5, fill=t.ink_soft, weight=500, anchor="middle"))

    # ---- legend / footer ----
    ly = H - 44
    legend = [("source", "Source"), ("agent", "Agent"), ("data", "Store"),
              ("model", "Model"), ("api", "API"), ("user", "Human"),
              ("note", "Fixture")]
    lx = 52
    S.append(text(lx, ly - 1, "LEGEND", size=10.5, fill=t.ink_soft,
                  weight=700, spacing="0.14em"))
    lx += 66
    for kind, lab in legend:
        fill, stroke, _ = t.kinds[kind]
        S.append(rrect(lx, ly - 12, 15, 15, 4, fill=fill, stroke=stroke,
                       sw=1.4))
        S.append(text(lx + 22, ly, lab, size=12, fill=t.ink_soft, weight=500))
        lx += 34 + len(lab) * 7.4
    S.append(text(W - 52, ly,
                  "Cited · Bounded · Inspectable   —   OpenAI Build Week 2026 · Developer Tools",
                  size=12, fill=t.ink_soft, weight=600, anchor="end"))

    S.append("</svg>")
    return "".join(S)


def main() -> None:
    import pathlib
    here = pathlib.Path(__file__).parent
    for t, fname in ((DARK, "arch-dark.svg"),
                     (LIGHT, "arch-light.svg")):
        (here / fname).write_text(build(t), encoding="utf-8")
        print(f"wrote {fname}")


if __name__ == "__main__":
    main()
