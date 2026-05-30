#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Social figures for the "Green by Construction" green-compute post.

All numbers are the measured/verified values from the blog post:
  - thermal spectrum: cjcl bench (10 runs) mean on a 1024x1024 matmul, ms
  - adaptive short:   one 1024^2 matmul, --time, seconds
  - adaptive sustained: 25x 1024^2 matmuls, seconds
  - determinism hash + energy/test counts: from the trustworthy/joule experiment

Outputs (figures/):
  LinkedIn (1200x675):  li_adaptive.png, li_thermal.png
  Instagram (1080x1080): ig_1_thermal.png, ig_2_adaptive.png, ig_3_determinism.png
"""
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

# palette
COST = "#E76F51"   # fixed cap = the cost
WIN  = "#2A9D8F"   # adaptive  = the win
BASE = "#8D99AE"   # max-perf  = neutral baseline
GOLD = "#E9C46A"   # default (balanced) highlight
INK  = "#1D3557"   # text
SUB  = "#6B7785"   # subtitle / footnote
BG   = "#FFFFFF"
GRID = "#EAEDF0"
FONT = "Arial, Helvetica, sans-serif"
DOT  = "·"     # middot
MUL  = "×"     # times
APX  = "≈"     # approx
ARR  = "→"     # right arrow
CHK  = "✓"     # check
QTR  = "¼"     # one-quarter
ELL  = "…"     # ellipsis

def footer(fig, y=-0.16, size=13):
    fig.add_annotation(text=f"adamezzat1.github.io  {DOT}  CJC-Lang", xref="paper", yref="paper",
                       x=0.5, y=y, showarrow=False, font=dict(size=size, color=SUB))

def save(fig, name, w, h):
    fig.write_image(os.path.join(OUT, name), width=w, height=h, scale=2)
    print("wrote", name)

# 1. LinkedIn hero: race-to-idle (two regimes)
def li_adaptive():
    cats = ["cool<br>(fixed cap)", "cool<br>(adaptive)", "max-perf"]
    colors = [COST, WIN, BASE]
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.16,
                        subplot_titles=(f"Short burst {DOT} one matmul (s)",
                                        f"Sustained {DOT} 25 matmuls (s)"))
    short = [0.353, 0.196, 0.153]
    fig.add_trace(go.Bar(x=cats, y=short, marker_color=colors,
                         text=[f"{v:.2f}s" for v in short], textposition="outside",
                         textfont=dict(size=16, color=INK)), row=1, col=1)
    sust = [16.7, 10.8, 4.2]
    fig.add_trace(go.Bar(x=cats, y=sust, marker_color=colors,
                         text=[f"{v:.1f}s" for v in sust], textposition="outside",
                         textfont=dict(size=16, color=INK)), row=1, col=2)
    fig.add_annotation(text=f"<b>{APX}1.8{MUL} faster than fixed</b><br>{APX} full speed", x=1, y=0.196,
                       xref="x1", yref="y1", showarrow=True, arrowcolor=WIN, arrowhead=2,
                       ax=58, ay=-54, font=dict(size=13, color=WIN), align="left")
    fig.add_annotation(text="<b>still throttled</b><br>thermal bound holds", x=1, y=10.8,
                       xref="x2", yref="y2", showarrow=True, arrowcolor=WIN, arrowhead=2,
                       ax=92, ay=-44, font=dict(size=13, color=WIN), align="left")
    fig.update_yaxes(range=[0, 0.46], gridcolor=GRID, zeroline=False, row=1, col=1)
    fig.update_yaxes(range=[0, 19.5], gridcolor=GRID, zeroline=False, row=1, col=2)
    fig.update_xaxes(tickfont=dict(size=13, color=INK))
    fig.update_layout(
        title=dict(text="<b>Race-to-idle: full speed when it's safe, throttled when it matters</b>"
                        "<br><span style='font-size:0.62em;color:#6B7785'>"
                        f"A capped run bursts at full width, then throttles only once load is sustained "
                        f"{DOT} output stays bit-identical.</span>",
                   x=0.5, xanchor="center", font=dict(size=23, color=INK)),
        paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=INK),
        margin=dict(t=120, b=80, l=60, r=40), showlegend=False)
    for ann in fig.layout.annotations[:2]:
        ann.font = dict(size=15, color=INK)
    footer(fig, y=-0.14)
    save(fig, "li_adaptive.png", 1200, 675)

# 2. LinkedIn secondary: the thermal dial
def li_thermal():
    cats = ["--threads 1", "cool", "balanced<br>(default)", "max-perf"]
    vals = [628, 468, 268, 210]
    colors = [COST, "#F4A261", GOLD, BASE]
    fig = go.Figure(go.Bar(x=cats, y=vals, marker_color=colors,
                           text=[f"{v} ms" for v in vals], textposition="outside",
                           textfont=dict(size=18, color=INK)))
    fig.update_yaxes(title_text="1024x1024 matmul, mean of 10 runs (ms)", range=[0, 720],
                     gridcolor=GRID, zeroline=False, title_font=dict(size=14, color=SUB))
    fig.update_xaxes(tickfont=dict(size=15, color=INK))
    fig.update_layout(
        title=dict(text="<b>One flag bounds how hard a run drives the CPU</b>"
                        "<br><span style='font-size:0.62em;color:#6B7785'>"
                        "Fewer active cores = less heat. Every setting returns the same bits "
                        f"{DOT} thread count is a heat knob, never an answer knob.</span>",
                   x=0.5, xanchor="center", font=dict(size=23, color=INK)),
        paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=INK),
        margin=dict(t=120, b=80, l=80, r=40), showlegend=False)
    footer(fig)
    save(fig, "li_thermal.png", 1200, 675)

# IG common layout helper
def ig_layout(fig, title, subtitle, top=170):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b><br><span style='font-size:0.5em;color:#6B7785'>{subtitle}</span>",
                   x=0.5, xanchor="center", y=0.94, font=dict(size=34, color=INK)),
        paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=INK),
        margin=dict(t=top, b=90, l=70, r=50), showlegend=False)
    footer(fig, y=-0.10, size=16)

# 3. IG card 1: pick your power budget
def ig_thermal():
    cats = ["1 core", "cool<br>(2)", "balanced<br>(4)", "max-perf<br>(8)"]
    vals = [628, 468, 268, 210]
    colors = [COST, "#F4A261", GOLD, BASE]
    fig = go.Figure(go.Bar(x=cats, y=vals, marker_color=colors,
                           text=[f"<b>{v} ms</b>" for v in vals], textposition="outside",
                           textfont=dict(size=22, color=INK)))
    fig.update_yaxes(range=[0, 760], gridcolor=GRID, zeroline=False, showticklabels=False)
    fig.update_xaxes(tickfont=dict(size=20, color=INK))
    ig_layout(fig, "Pick your power budget",
              f"cool {DOT} balanced {DOT} max-perf: one CLI flag, set once  (1024^2 matmul)")
    save(fig, "ig_1_thermal.png", 1080, 1080)

# 4. IG card 2: capped but full speed
def ig_adaptive():
    cats = ["cool<br>fixed", "cool<br>adaptive", "max-perf"]
    vals = [0.353, 0.196, 0.153]
    colors = [COST, WIN, BASE]
    fig = go.Figure(go.Bar(x=cats, y=vals, marker_color=colors,
                           text=[f"<b>{v:.2f}s</b>" for v in vals], textposition="outside",
                           textfont=dict(size=22, color=INK)))
    fig.add_annotation(text=f"<b>{APX}1.8{MUL} recovered</b>", x=1, y=0.196, showarrow=False,
                       yshift=80, font=dict(size=21, color=WIN))
    fig.update_yaxes(range=[0, 0.47], gridcolor=GRID, zeroline=False, showticklabels=False)
    fig.update_xaxes(tickfont=dict(size=20, color=INK))
    ig_layout(fig, f"Capped to {QTR} the cores.<br>Still ran at full speed.",
              "Race-to-idle: bursts run full-width; only sustained load throttles.", top=215)
    save(fig, "ig_2_adaptive.png", 1080, 1080)

# 5. IG card 3: same bits, every config
def ig_determinism():
    configs = ["default", "--profile max-perf", "--profile cool",
               "--profile cool --no-adaptive", "--threads 1", "--mir-opt  (MIR executor)"]
    fig = go.Figure()
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.add_annotation(text=f"Same program {DOT} six ways to run it:", x=0.12, y=0.80,
                       xref="paper", yref="paper", showarrow=False, xanchor="left",
                       font=dict(size=19, color=SUB))
    for i, c in enumerate(configs):
        yy = 0.715 - i * 0.066
        fig.add_annotation(text=f"<span style='color:{WIN}'><b>{CHK}</b></span>   {c}", x=0.12, y=yy,
                           xref="paper", yref="paper", showarrow=False, xanchor="left",
                           font=dict(size=21, color=INK))
    fig.add_shape(type="rect", x0=0.08, x1=0.92, y0=0.215, y1=0.315, xref="paper", yref="paper",
                  fillcolor="#F1F5F8", line=dict(color=WIN, width=2))
    fig.add_annotation(text=f"all {ARR} <b>e8118361{ELL}b36ff194</b>", x=0.5, y=0.265,
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=23, color=INK, family="Consolas, monospace"))
    fig.add_annotation(text=f"0.0275 J / trustworthy result      80 new tests      0 output bits changed",
                       x=0.5, y=0.135, xref="paper", yref="paper", showarrow=False,
                       font=dict(size=15, color=SUB))
    ig_layout(fig, "Same bits. Every config.",
              "Changed how it runs - not what it computes.", top=180)
    save(fig, "ig_3_determinism.png", 1080, 1080)

if __name__ == "__main__":
    li_adaptive()
    li_thermal()
    ig_thermal()
    ig_adaptive()
    ig_determinism()
    print("done")
