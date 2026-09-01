#!/usr/bin/env python3
"""Generate docs/architecture.svg + docs/architecture.png for the Devpost submission.

Design: dark slate-950, 40px grid, semantic component colors, double-rect
masking, arrows behind boxes, legend outside all boundaries.
Regenerate:  uv run --with cairosvg python scripts/gen_architecture.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1680, 1000

C = {
    "bg": "#020617", "box": "#0f172a", "grid": "#1e293b",
    "text": "#e2e8f0", "sub": "#94a3b8", "tiny": "#64748b",
    "emerald": "#34d399", "violet": "#a78bfa", "cyan": "#22d3ee",
    "rose": "#fb7185", "orange": "#fb923c", "slate": "#94a3b8",
}
FILL = {
    "emerald": "rgba(6,78,59,0.40)", "violet": "rgba(76,29,149,0.40)",
    "cyan": "rgba(8,51,68,0.40)", "rose": "rgba(136,19,55,0.40)",
    "orange": "rgba(251,146,60,0.30)", "slate": "rgba(30,41,59,0.50)",
}
FONT = "DejaVu Sans Mono, monospace"
Q = '"'
svg = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(name, sub, x, y, w, h, style, tiny=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{C["box"]}"/>')
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{FILL[style]}" '
               f'stroke="{C[style]}" stroke-width="1.5"/>')
    cy = y + (20 if (sub or tiny) else h / 2 + 4)
    svg.append(f'<text x="{x + w / 2}" y="{cy}" font-family="{FONT}" font-size="12" '
               f'fill="{C["text"]}" text-anchor="middle" font-weight="bold">{esc(name)}</text>')
    if sub:
        svg.append(f'<text x="{x + w / 2}" y="{cy + 15}" font-family="{FONT}" font-size="9" '
                   f'fill="{C["sub"]}" text-anchor="middle">{esc(sub)}</text>')
    if tiny:
        svg.append(f'<text x="{x + w / 2}" y="{cy + 29}" font-family="{FONT}" font-size="7" '
                   f'fill="{C["tiny"]}" text-anchor="middle">{esc(tiny)}</text>')


def arrow(color, path, dashed=False, label=None, lx=0, ly=0, anchor="middle"):
    if label:
        svg.append(f'<text x="{lx}" y="{ly}" font-family="{FONT}" font-size="8" fill="{C["sub"]}" '
                   f'text-anchor="{anchor}">{esc(label)}</text>')
    dash = ' stroke-dasharray="4,4"' if dashed else ""
    svg.append(f'<path d="{path}" fill="none" stroke="{C[color]}" stroke-width="1.5" '
               f'marker-end="url(#{color})"{dash}/>')


# --- document ---------------------------------------------------------------
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
           f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="{C["grid"]}" stroke-width="0.5"/></pattern>')
for k in ("emerald", "violet", "cyan", "rose", "orange", "slate"):
    svg.append(f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
               f'markerHeight="7" orient="auto-start-reverse">'
               f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{C[k]}"/></marker>')
svg.append("</defs>")
svg.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
svg.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')

svg.append(f'<text x="60" y="50" font-family="{FONT}" font-size="16" fill="{C["text"]}" '
           f'font-weight="bold">ClubSteward — System Architecture</text>')
svg.append(f'<text x="60" y="70" font-family="{FONT}" font-size="9" fill="{C["sub"]}">'
           f'Local-first club-secretary agent · Strands Agents SDK · policy-as-data autonomy · fail-closed human-in-the-loop</text>')

# local boundary
svg.append(f'<rect x="40" y="110" width="1360" height="830" rx="12" fill="none" '
           f'stroke="{C["slate"]}" stroke-width="1.5" stroke-dasharray="8,4"/>')
svg.append(f'<text x="60" y="130" font-family="{FONT}" font-size="8" fill="{C["sub"]}" '
           f'letter-spacing="1">LOCAL MACHINE — THE CLUB SECRETARY&#39;S LAPTOP · ALL STATE &amp; TOOLS LOCAL · ~€0.01–0.03 PER NIGHT</text>')  # noqa: RUF001

# arrows first (render behind boxes)
arrow("slate", "M250,272 L316,272")
arrow("emerald", "M530,272 L579,273")
arrow("emerald", "M725,273 L799,298", label="auto", lx=758, ly=278)
arrow("orange", "M725,292 C950,300 1030,470 1144,483", dashed=True,
      label="ask → decision card", lx=940, ly=412)
arrow("slate", "M655,301 L655,369")
arrow("violet", "M685,192 L657,239", label="routes", lx=648, ly=222, anchor="end")
arrow("rose", "M785,175 L804,201", dashed=True, label="drives gate", lx=838, ly=182)
arrow("emerald", "M1055,278 L1144,242", label="update", lx=1094, ly=248)
arrow("emerald", "M1055,300 L1144,358", label="draft", lx=1082, ly=342)
arrow("emerald", "M1055,322 C1105,340 1105,590 1144,604", label="log", lx=1078, ly=508)
arrow("slate", "M530,238 C900,80 1360,140 1444,238",
      label="LiteLLM · openai-compatible API", lx=990, ly=118)
arrow("slate", "M1055,258 C1260,205 1380,215 1444,254")
arrow("cyan", "M1150,500 C980,560 850,640 791,682", label="morning: decision cards", lx=965, ly=596)
arrow("cyan", "M700,646 C700,480 780,420 818,346", dashed=True,
      label="approve → auto_preapproved", lx=704, ly=470, anchor="start")
arrow("slate", "M480,685 L579,685", label="y / e / n", lx=530, ly=676)
arrow("violet", "M425,556 C425,450 422,380 422,320", label="member memory", lx=448, ly=446, anchor="start")

# boxes
box("inbox/", "member mail (.eml)", 80, 240, 170, 64, "violet")
box("Triage Agent", "Strands · structured_output", 320, 230, 210, 84, "emerald",
    tiny="Pydantic: intent · facts · confidence")
box("route", "auto · ask · reject", 585, 245, 140, 56, "orange")
box("spam", "discarded silently", 585, 375, 140, 44, "slate")
box("policy.yaml", "club rules as data (YAML)", 585, 140, 200, 52, "violet")

svg.append(f'<rect x="780" y="190" width="300" height="180" rx="8" fill="none" '
           f'stroke="{C["rose"]}" stroke-width="1.5" stroke-dasharray="4,4"/>')
svg.append(f'<text x="930" y="204" font-family="{FONT}" font-size="8" fill="{C["rose"]}" '
           f'text-anchor="middle" letter-spacing="0.5">HUMANINTHELOOP — SDK INTERVENTION</text>')
box("policy classifier", "custom · fail-closed", 800, 212, 180, 36, "rose")
box("Act Agent", "5 tools · write loop", 805, 260, 250, 80, "emerald",
    tiny="register add/update/lookup · draft · log")

box("register.csv", "members — source of truth", 1150, 210, 210, 60, "violet")
box("outbox/", "draft replies — never auto-sent", 1150, 330, 210, 60, "violet")
box("queue/", "decision cards (why asked)", 1150, 450, 210, 60, "violet")
box("audit + report", "mails · routes · tokens · cost", 1150, 570, 210, 60, "violet")
box("sessions/", "per-member memory", 320, 560, 210, 60, "violet")
box("club secretary", "the human — decides", 290, 650, 190, 70, "slate")
box("decide CLI", "approve · edit · deny", 585, 650, 200, 70, "cyan")
box("GLM on Z.ai", "chat completions API", 1450, 230, 190, 96, "slate", tiny="deep/quick think")

# legend (outside all boundaries)
ly = 968
legend = [("emerald", "Agents (Strands SDK)", False), ("violet", "Data · policy", False),
          ("cyan", "Human-facing", False), ("rose", "Intervention gate", True),
          ("orange", "Routing", True), ("slate", "External / files", False)]
lx = 60
for style, label, dash in legend:
    dash_sw = ' stroke-dasharray="3,3"' if dash else ""
    svg.append(f'<rect x="{lx}" y="{ly - 10}" width="18" height="10" rx="2" fill="{FILL[style]}" '
               f'stroke="{C[style]}" stroke-width="1.2"{dash_sw}/>')
    svg.append(f'<text x="{lx + 26}" y="{ly}" font-family="{FONT}" font-size="8" fill="{C["sub"]}">{esc(label)}</text>')
    lx += 26 + len(label) * 6 + 34
svg.append(f'<text x="{W - 60}" y="{ly}" font-family="{FONT}" font-size="8" fill="{C["tiny"]}" '
           f'text-anchor="end">ClubSteward · Good Neighbor Agents · MIT</text>')

svg.append("</svg>")

out_svg = ROOT / "docs" / "architecture.svg"
out_svg.write_text("\n".join(svg))
print("SVG:", out_svg, out_svg.stat().st_size, "bytes")

import cairosvg  # noqa: E402  # optional heavy dep, only needed for PNG export

out_png = ROOT / "docs" / "architecture.png"
cairosvg.svg2png(url=str(out_svg), write_to=str(out_png), scale=2.0)
print("PNG:", out_png, out_png.stat().st_size, "bytes")
