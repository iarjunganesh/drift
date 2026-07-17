#!/usr/bin/env python3
"""Generate the canonical DRIFT brand banner (dark + light SVG).

The banner shares one visual language with the architecture presentation diagram
(`assets/architecture/build_arch.py`): the same trust-zone palette, rounded
node styling with sheen + soft shadow, the gold human-review gate, the dot-grid
field, and Inter typography. The right-side "evidence path" card distills the
architecture diagram's story to its core: an untrusted primary release crosses a
human gate to become a cited, bounded briefing.

Filenames are fixed: `backend/main.py` serves `drift-banner-dark.svg` and
`drift-banner-light.svg` at `/brand/{theme}.svg`, and Docker bakes this
directory into the API image. Do not rename the SVG outputs.

    python build_banner.py            # writes both SVGs
    node build_banner_raster.mjs      # optional PNG rasters (needs frontend/ deps)
"""

from __future__ import annotations

import html
from dataclasses import dataclass

W, H = 1600, 520
FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


# Palette mirrors assets/architecture/build_arch.py so the banner and the
# architecture diagram read as one system.
@dataclass(frozen=True)
class Theme:
    name: str
    bg0: str
    bg1: str
    grid: str
    ink: str
    ink_soft: str
    panel: str
    panel_stroke: str
    line: str
    emerald: str
    rose: str
    amber: str
    wordmark0: str
    wordmark1: str
    source: tuple
    api: tuple
    gate_fill0: str
    gate_fill1: str
    gate_stroke: str
    gate_ink: str
    pill_ink: str


DARK = Theme(
    name="dark", bg0="#0b1020", bg1="#060912", grid="#1b2438",
    ink="#f8fafc", ink_soft="#94a3b8", panel="#0e1526", panel_stroke="#233047",
    line="#7c8aa5", emerald="#10b981", rose="#f43f5e", amber="#f59e0b",
    wordmark0="#2dd4bf", wordmark1="#818cf8",
    source=("#0f766e", "#2dd4bf", "#ecfeff"),
    api=("#166534", "#4ade80", "#f0fdf4"),
    gate_fill0="#0f3f2f", gate_fill1="#12261f", gate_stroke="#fbbf24",
    gate_ink="#fef9c3", pill_ink="#5eead4",
)

LIGHT = Theme(
    name="light", bg0="#f6f8fc", bg1="#e9eef7", grid="#dbe3ef",
    ink="#0f172a", ink_soft="#64748b", panel="#ffffff", panel_stroke="#cbd5e1",
    line="#7688a1", emerald="#059669", rose="#e11d48", amber="#d97706",
    wordmark0="#0d9488", wordmark1="#4f46e5",
    source=("#d5f5f0", "#0d9488", "#0f3d38"),
    api=("#d8f5e2", "#16a34a", "#14532d"),
    gate_fill0="#ecfdf5", gate_fill1="#d1fae5", gate_stroke="#b45309",
    gate_ink="#7c2d12", pill_ink="#0f766e",
)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def text(x, y, s, *, size, fill, weight=400, anchor="start", spacing=None,
         opacity=1.0):
    ls = f' letter-spacing="{spacing}"' if spacing is not None else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{ls}{op}>{esc(s)}</text>')


def rrect(x, y, w, h, r, *, fill, stroke="none", sw=0, opacity=1.0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r}" ry="{r}" fill="{fill}"{st}{op}{extra}/>')


def node(cx, cy, w, h, kind_colors, title, subtitle, dot=None):
    fill, stroke, ink = kind_colors
    x, y = cx - w / 2, cy - h / 2
    parts = [
        f'<g filter="url(#soft)">',
        rrect(x, y, w, h, 13, fill=fill, stroke=stroke, sw=1.6),
        "</g>",
        rrect(x + 1, y + 1, w - 2, h * 0.5, 12, fill="url(#sheen)",
              opacity=0.12),
        text(cx, cy - 3, title, size=15.5, fill=ink, weight=700,
             anchor="middle"),
        text(cx, cy + 15, subtitle, size=11, fill=ink, weight=400,
             anchor="middle", opacity=0.82),
    ]
    if dot:
        parts.append(f'<circle cx="{x + 13:.1f}" cy="{y + 13:.1f}" r="4.5" '
                     f'fill="{dot}"/>')
    return "".join(parts)


def arrow(x0, y0, x1, y1, color, label=None, t=DARK):
    out = [f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
           f'stroke="{color}" stroke-width="2.4" stroke-linecap="round" '
           f'marker-end="url(#bah)"/>']
    if label:
        mx = (x0 + x1) / 2
        lw = 10 + len(label) * 6.0
        out.append(rrect(mx - lw / 2, y0 - 26, lw, 17, 8, fill=t.bg0,
                         opacity=0.92))
        out.append(text(mx, y0 - 14, label, size=10.5, fill=color,
                        weight=700, anchor="middle", spacing="0.04em"))
    return "".join(out)


def circuit(t: Theme, x, y, w, h) -> str:
    """Subtle GPU/PCB connector backdrop, clipped to the evidence-path card.

    Drawn before the nodes, so the opaque node fills sit on top and the traces
    read as a compute lattice feeding into and out of the flow.
    """
    trace = t.source[1]
    gold = t.gate_stroke
    op = 0.32 if t.name == "dark" else 0.30

    def via(cx, cy, c=trace):
        return (f'<rect x="{cx - 3:.1f}" y="{cy - 3:.1f}" width="6" height="6" '
                f'rx="1.3" fill="{c}"/>')

    def tp(d, c=trace, sw=1.3):
        return (f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{sw}" '
                f'stroke-linejoin="round" stroke-linecap="round"/>')

    P = [f'<clipPath id="cardclip"><rect x="{x}" y="{y}" width="{w}" '
         f'height="{h}" rx="22"/></clipPath>',
         f'<g clip-path="url(#cardclip)" opacity="{op}">']

    # top rails (below the header band)
    yA = y + 66
    P.append(tp(f"M {x} {yA} H {x + 118} V {yA + 24} H {x + 250} V {yA} "
               f"H {x + 372}"))
    for vx, vy in [(x + 118, yA), (x + 250, yA + 24), (x + 372, yA)]:
        P.append(via(vx, vy))
    yB = y + 86
    P.append(tp(f"M {x + w} {yB} H {x + w - 96} V {yB + 30} H {x + w - 210}"))
    P.append(via(x + w - 96, yB))
    P.append(via(x + w - 210, yB + 30))

    # a lattice of traces radiating from the centre (behind the gate)
    midx, midy = x + w / 2, y + h * 0.58
    P.append(tp(f"M {x} {midy:.1f} H {x + 40}"))
    P.append(via(x + 10, midy))
    P.append(tp(f"M {x + w - 40} {midy:.1f} H {x + w}"))
    P.append(via(x + w - 10, midy))
    for dy in (-40, 40):
        P.append(tp(f"M {midx - 150:.1f} {midy + dy:.1f} H {midx - 40:.1f} "
                   f"V {midy:.1f}"))
        P.append(tp(f"M {midx + 150:.1f} {midy + dy:.1f} H {midx + 40:.1f} "
                   f"V {midy:.1f}"))

    # bottom rails
    yC = y + h - 78
    P.append(tp(f"M {x + 44} {yC} H {x + 168} V {yC + 22} H {x + 330} "
               f"V {yC} H {x + 520} V {yC - 20} H {x + w - 44}"))
    for vx, vy in [(x + 168, yC), (x + 330, yC + 22), (x + 520, yC),
                   (x + w - 44, yC - 20)]:
        P.append(via(vx, vy))

    P.append("</g>")

    # PCB edge-connector fingers along the card foot (warmer, own opacity)
    fy = y + h - 17
    P.append(f'<g clip-path="url(#cardclip)" fill="{gold}" '
             f'opacity="{0.44 if t.name == "dark" else 0.42}">')
    fingers, fw, gap = 13, 11, 9
    startx = x + w / 2 - (fingers * (fw + gap) - gap) / 2
    for i in range(fingers):
        P.append(f'<rect x="{startx + i * (fw + gap):.1f}" y="{fy:.1f}" '
                 f'width="{fw}" height="16" rx="2.5"/>')
    P.append("</g>")
    return "".join(P)


def build(t: Theme) -> str:
    S = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" font-family="{FONT}">']

    # ---- defs ----
    S.append("<defs>")
    S.append(f'<radialGradient id="bg" cx="22%" cy="8%" r="120%">'
             f'<stop offset="0%" stop-color="{t.bg0}"/>'
             f'<stop offset="100%" stop-color="{t.bg1}"/></radialGradient>')
    S.append(f'<radialGradient id="blob" cx="50%" cy="50%" r="50%">'
             f'<stop offset="0%" stop-color="{t.wordmark1}" stop-opacity="0.18"/>'
             f'<stop offset="100%" stop-color="{t.wordmark1}" stop-opacity="0"/>'
             f'</radialGradient>')
    S.append(f'<linearGradient id="word" x1="0" y1="0" x2="1" y2="0.4">'
             f'<stop offset="0%" stop-color="{t.wordmark0}"/>'
             f'<stop offset="100%" stop-color="{t.wordmark1}"/></linearGradient>')
    S.append(f'<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{t.wordmark0}"/>'
             f'<stop offset="100%" stop-color="{t.wordmark1}" '
             f'stop-opacity="0"/></linearGradient>')
    S.append('<linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0%" stop-color="#ffffff" stop-opacity="0.9"/>'
             '<stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>'
             '</linearGradient>')
    S.append(f'<linearGradient id="gate" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0%" stop-color="{t.gate_fill0}"/>'
             f'<stop offset="100%" stop-color="{t.gate_fill1}"/></linearGradient>')
    S.append('<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
             '<feDropShadow dx="0" dy="3" stdDeviation="5" '
             'flood-color="#000000" flood-opacity="0.28"/></filter>')
    S.append(f'<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">'
             f'<feDropShadow dx="0" dy="0" stdDeviation="9" '
             f'flood-color="{t.gate_stroke}" flood-opacity="0.55"/></filter>')
    S.append(f'<marker id="bah" viewBox="0 0 10 10" refX="8.5" refY="5" '
             f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             f'<path d="M0 0 L10 5 L0 10 L3 5 Z" fill="{t.line}"/></marker>')
    S.append("</defs>")

    # ---- background ----
    S.append(f'<rect width="{W}" height="{H}" fill="url(#bg)" rx="0"/>')
    S.append(f'<circle cx="120" cy="70" r="520" fill="url(#blob)"/>')
    dots = ['<g opacity="0.5">']
    for gy in range(60, H - 20, 32):
        for gx in range(40, W - 20, 32):
            dots.append(f'<circle cx="{gx}" cy="{gy}" r="1" fill="{t.grid}"/>')
    dots.append("</g>")
    S.append("".join(dots))

    # ---- left column ----
    lx = 72
    S.append(text(lx, 150, "DRIFT", size=78, fill="url(#word)", weight=800,
                  spacing="0.10em"))
    S.append(text(lx + 4, 186,
                  "RELEASE INTELLIGENCE FOR GPU & AI INFRASTRUCTURE",
                  size=14.5, fill=t.emerald, weight=700, spacing="0.16em"))
    S.append(rrect(lx + 4, 200, 190, 4, 2, fill="url(#rule)"))
    S.append(text(lx, 262, "Know the change before", size=41, fill=t.ink,
                  weight=800))
    S.append(text(lx, 306, "it becomes your incident.", size=41, fill=t.ink,
                  weight=800))
    S.append(text(lx + 2, 352,
                  "Primary releases become cited, review-gated engineering checks.",
                  size=18.5, fill=t.ink_soft, weight=500))
    # trust pill — one centred line so the word gaps are inherently even (the
    # SVG renderer ignores textLength, so per-word slots drift). The separators
    # are emerald bullet glyphs; only the outer pill padding depends on width,
    # and that is symmetric so it can never look lopsided.
    pw, ph, py = 358, 42, 384
    cyp = py + ph / 2
    dot = (f'<tspan fill="{t.emerald}" font-size="16" font-weight="900">'
           f' ● </tspan>')
    S.append(rrect(lx, py, pw, ph, ph / 2, fill="none", stroke=t.emerald,
                   sw=1.6))
    S.append(
        f'<text x="{lx + pw / 2:.1f}" y="{cyp + 5:.1f}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="15" font-weight="700" '
        f'fill="{t.pill_ink}" letter-spacing="0.06em">'
        f'CITED {dot} BOUNDED {dot} INSPECTABLE</text>'
    )
    # model credit
    S.append(f'<text x="{lx}" y="468" font-family="{FONT}" font-size="13.5" '
             f'fill="{t.ink_soft}" font-weight="500">Powered by '
             f'<tspan font-weight="700" fill="{t.amber}">GPT-5.6 tiers</tspan>'
             f' · Luna · Terra · Sol</text>')

    # ---- right card: evidence path ----
    cx0, cy0, cw, ch = 858, 92, 670, 336
    S.append(rrect(cx0, cy0, cw, ch, 22, fill=t.panel, stroke=t.panel_stroke,
                   sw=1.4, opacity=0.92, extra=' filter="url(#soft)"'))
    S.append(circuit(t, cx0, cy0, cw, ch))
    S.append(f'<circle cx="{cx0 + 26:.1f}" cy="{cy0 + 34:.1f}" r="4.5" '
             f'fill="{t.emerald}"/>')
    S.append(text(cx0 + 40, cy0 + 39, "DRIFT EVIDENCE PATH", size=13.5,
                  fill=t.ink_soft, weight=700, spacing="0.14em"))
    tag = "HUMAN-GATED"
    tw = 24 + len(tag) * 8.0
    tagink = "#04231a" if t.name == "dark" else "#ffffff"
    S.append(rrect(cx0 + cw - tw - 22, cy0 + 21, tw, 28, 14, fill=t.emerald,
                   extra=' filter="url(#soft)"'))
    S.append(text(cx0 + cw - 22 - tw / 2, cy0 + 39, tag, size=12,
                  fill=tagink, weight=800, anchor="middle", spacing="0.07em"))

    fy = cy0 + 196
    # source node
    S.append(node(cx0 + 118, fy, 168, 78, t.source, "Release feed",
                  "primary source", dot=t.rose))
    # gate (focal motif)
    gcx, gy0, gy1 = cx0 + 335, cy0 + 118, cy0 + 274
    S.append(f'<g filter="url(#glow)">'
             + rrect(gcx - 62, gy0, 124, gy1 - gy0, 16, fill="url(#gate)",
                     stroke=t.gate_stroke, sw=2.2) + "</g>")
    S.append(rrect(gcx - 60, gy0 + 2, 120, (gy1 - gy0) * 0.4, 14,
                   fill="url(#sheen)", opacity=0.10))
    S.append(f'<circle cx="{gcx:.1f}" cy="{gy0 + 30:.1f}" r="15" '
             f'fill="{t.gate_stroke}"/>')
    S.append(text(gcx, gy0 + 36, "5", size=17, fill=t.gate_fill1, weight=800,
                  anchor="middle"))
    # small person glyph
    pgy = gy0 + 72
    S.append(f'<g stroke="{t.gate_ink}" stroke-width="2.2" fill="none" '
             f'stroke-linecap="round"><circle cx="{gcx:.1f}" '
             f'cy="{pgy - 6:.1f}" r="5"/><path d="M {gcx - 9:.1f} '
             f'{pgy + 9:.1f} a 9 8 0 0 1 18 0"/></g>')
    S.append(text(gcx, gy0 + 108, "HUMAN", size=13.5, fill=t.gate_ink,
                  weight=800, anchor="middle"))
    S.append(text(gcx, gy0 + 126, "GATE", size=13.5, fill=t.gate_ink,
                  weight=800, anchor="middle"))
    # briefing node
    S.append(node(cx0 + 552, fy, 168, 78, t.api, "Cited briefing",
                  "bounded check", dot=t.emerald))
    # arrows
    S.append(arrow(cx0 + 202, fy, gcx - 66, fy, t.line, "untrusted", t))
    S.append(arrow(gcx + 66, fy, cx0 + 468, fy, t.emerald, "reviewed", t))

    S.append("</svg>")
    return "".join(S)


def main() -> None:
    import pathlib
    here = pathlib.Path(__file__).parent
    for t, fname in ((DARK, "drift-banner-dark.svg"),
                     (LIGHT, "drift-banner-light.svg")):
        (here / fname).write_text(build(t), encoding="utf-8")
        print(f"wrote {fname}")


if __name__ == "__main__":
    main()
