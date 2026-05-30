#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instagram carousel figures for the Gibran "charts + per-group ranking +
CTE-aware row filters" post.

Three 1080x1080 cards (post in order):
  1. ig_1_charts.png      — hook: ask in English, get a chart
  2. ig_2_topn.png        — top-N-per-group (windowed CTE) in English
  3. ig_3_governance.png  — the kicker: the row-filter fix you can't see

The chart values are illustrative sample data (the post's examples), not a
benchmark. Run:  python make_figures.py
"""
import os
import plotly.graph_objects as go

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

# palette (shared with the rest of the site's social cards)
COST = "#E76F51"   # the bug / "before"
WIN  = "#2A9D8F"   # the fix / primary series
BASE = "#8D99AE"   # neutral
GOLD = "#E9C46A"   # second series highlight
INK  = "#1D3557"   # text
SUB  = "#6B7785"   # subtitle / footnote
BG   = "#FFFFFF"
GRID = "#EAEDF0"
FONT = "Arial, Helvetica, sans-serif"
MONO = "Consolas, monospace"
DOT  = "·"
ARR  = "→"
CHK  = "✓"
CROSS = "✗"
LE   = "≤"


def footer(fig, y=-0.10, size=16):
    fig.add_annotation(text=f"adamezzat1.github.io  {DOT}  Gibran", xref="paper", yref="paper",
                       x=0.5, y=y, showarrow=False, font=dict(size=size, color=SUB))


def save(fig, name, w=1080, h=1080):
    fig.write_image(os.path.join(OUT, name), width=w, height=h, scale=2)
    print("wrote", name)


def ig_layout(fig, title, subtitle, top=170):
    fig.update_layout(
        title=dict(text=f"<b>{title}</b><br><span style='font-size:0.5em;color:#6B7785'>{subtitle}</span>",
                   x=0.5, xanchor="center", y=0.94, font=dict(size=34, color=INK)),
        paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=INK),
        margin=dict(t=top, b=90, l=70, r=50), showlegend=False)
    footer(fig)


# 1. Charts: a trend line from a plain-English question
def ig_charts():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    rev = [120, 145, 138, 175, 205, 240]
    fig = go.Figure(go.Scatter(
        x=months, y=rev, mode="lines+markers",
        line=dict(color=WIN, width=5), marker=dict(size=12, color=WIN),
        fill="tozeroy", fillcolor="rgba(42,157,143,0.12)"))
    fig.update_yaxes(range=[0, 275], gridcolor=GRID, zeroline=False,
                     ticksuffix="k", tickfont=dict(size=18, color=SUB))
    fig.update_xaxes(tickfont=dict(size=20, color=INK))
    ig_layout(fig, "Ask in English. Get a chart.",
              f"\"revenue by month\"  {ARR}  table or chart, one toggle  {DOT}  lazy-loaded")
    save(fig, "ig_1_charts.png")


# 2. Top-N-per-group: one English line vs. the window function you'd write
def _nb(s):
    """Preserve spaces for monospace alignment in plotly annotations."""
    return s.replace(" ", "&nbsp;")


_SQL_LINES = [
    "WITH grouped AS (",
    "  SELECT country, customer, SUM(spend) AS spend",
    "  FROM orders GROUP BY country, customer",
    "), ranked AS (",
    "  SELECT country, customer, spend,",
    "    ROW_NUMBER() OVER (PARTITION BY country",
    "      ORDER BY spend DESC) AS rn",
    "  FROM grouped",
    ")",
    "SELECT country, customer, spend",
    f"FROM ranked WHERE rn {LE} 5 ORDER BY country, rn;",
]

_RES_LINES = [
    f"{'country':<10}{'customer':<11}spend",
    f"{'USA':<10}{'Acme':<11}92.4k",
    f"{'USA':<10}{'Globex':<11}78.1k",
    f"{'USA':<10}{'Initech':<11}64.0k",
    f"{'UK':<10}{'Hooli':<11}55.2k",
    f"{'UK':<10}{'Stark':<11}41.3k",
]


def ig_topn():
    fig = go.Figure()
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])

    # 1) the English you type in Gibran
    fig.add_annotation(text="TYPE IN GIBRAN", x=0.08, y=0.885, xref="paper", yref="paper",
                       showarrow=False, xanchor="left", font=dict(size=15, color=SUB))
    fig.add_shape(type="rect", x0=0.06, x1=0.94, y0=0.80, y1=0.865, xref="paper", yref="paper",
                  fillcolor="#E8F4F1", line=dict(color=WIN, width=2))
    fig.add_annotation(text="<b>biggest 5 customer per country by spend</b>", x=0.5, y=0.8325,
                       xref="paper", yref="paper", showarrow=False, font=dict(size=21, color=INK))

    # 2) the SQL it replaces (the windowed CTE you'd otherwise hand-write)
    fig.add_annotation(text=f"compiles to the SQL you'd otherwise write by hand  {ARR}",
                       x=0.5, y=0.760, xref="paper", yref="paper", showarrow=False,
                       font=dict(size=15, color=SUB))
    fig.add_shape(type="rect", x0=0.06, x1=0.94, y0=0.40, y1=0.725, xref="paper", yref="paper",
                  fillcolor="#F1F5F8", line=dict(color="#C9D2DA", width=1))
    fig.add_annotation(text="<br>".join(_nb(l) for l in _SQL_LINES), x=0.095, y=0.70,
                       xref="paper", yref="paper", showarrow=False, xanchor="left", yanchor="top",
                       align="left", font=dict(size=15, color=INK, family=MONO))

    # 3) the result (tangible)
    fig.add_annotation(text="RESULT", x=0.08, y=0.360, xref="paper", yref="paper",
                       showarrow=False, xanchor="left", font=dict(size=15, color=SUB))
    fig.add_shape(type="rect", x0=0.06, x1=0.94, y0=0.085, y1=0.325, xref="paper", yref="paper",
                  fillcolor="#FBFBFC", line=dict(color="#C9D2DA", width=1))
    res_text = f"<b>{_nb(_RES_LINES[0])}</b><br>" + "<br>".join(_nb(l) for l in _RES_LINES[1:])
    fig.add_annotation(text=res_text, x=0.095, y=0.30, xref="paper", yref="paper",
                       showarrow=False, xanchor="left", yanchor="top", align="left",
                       font=dict(size=15, color=INK, family=MONO))

    ig_layout(fig, "Ask it. Skip the SQL.",
              "top-N-per-group: one English line, none of the window function", top=150)
    save(fig, "ig_2_topn.png")


# 3. Governance: where the row filter lands (before / after)
def ig_governance():
    fig = go.Figure()
    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0, 1])

    # BEFORE — filter on the outer SELECT (which reads a CTE): broken
    fig.add_shape(type="rect", x0=0.06, x1=0.94, y0=0.55, y1=0.83,
                  xref="paper", yref="paper", fillcolor="#FBEAE5",
                  line=dict(color=COST, width=2))
    fig.add_annotation(text="<b>BEFORE</b>   filter on the outer SELECT", x=0.10, y=0.785,
                       xref="paper", yref="paper", showarrow=False, xanchor="left",
                       font=dict(size=20, color=COST))
    fig.add_annotation(text=f"… FROM ranked WHERE rn {LE} 3 <b>AND region = 'west'</b>",
                       x=0.10, y=0.700, xref="paper", yref="paper", showarrow=False,
                       xanchor="left", font=dict(size=17, color=INK, family=MONO))
    fig.add_annotation(text=f"{CROSS}  'region' isn't a column of the CTE  {ARR}  error",
                       x=0.10, y=0.615, xref="paper", yref="paper", showarrow=False,
                       xanchor="left", font=dict(size=17, color=COST))

    # AFTER — filter inside the source-reading CTE: correct + safe
    fig.add_shape(type="rect", x0=0.06, x1=0.94, y0=0.17, y1=0.45,
                  xref="paper", yref="paper", fillcolor="#E8F4F1",
                  line=dict(color=WIN, width=2))
    fig.add_annotation(text="<b>AFTER</b>   filter inside the source scan", x=0.10, y=0.405,
                       xref="paper", yref="paper", showarrow=False, xanchor="left",
                       font=dict(size=20, color=WIN))
    fig.add_annotation(text="WITH grouped AS (… FROM orders <b>WHERE region = 'west'</b> …)",
                       x=0.10, y=0.320, xref="paper", yref="paper", showarrow=False,
                       xanchor="left", font=dict(size=16, color=INK, family=MONO))
    fig.add_annotation(text=f"{CHK}  the ranking only sees rows you're allowed to see",
                       x=0.10, y=0.235, xref="paper", yref="paper", showarrow=False,
                       xanchor="left", font=dict(size=17, color=WIN))

    ig_layout(fig, "The fix you can't see",
              "Row filters now compose with CTE queries (cohort / funnel / top-N).", top=185)
    save(fig, "ig_3_governance.png")


if __name__ == "__main__":
    ig_charts()
    ig_topn()
    ig_governance()
    print("done")
