"""Phase 0.10 follow-up figures — 6 more diagrams in 2 themes.

Generates:
  #7  per_column_missingness          (data-driven bar chart)
  #5  locke_findings_sunburst         (data-driven sunburst)
  #6  per_leaf_belief_radar           (data-driven polar plot)
  #1  abng_architecture               (schematic node-and-arrow)
  #11 confounded_experiment_flow      (schematic flowchart)
  #4  locke_pearson_heatmap           (Plotly recreation of Locke's SVG)

Each in figures/traditional/ and figures/cyberpunk/. The raw SVG of
Locke's actual Pearson heatmap is preserved at
figures/locke/pearson_heatmap_raw.svg (extracted from the audit HTML).
"""

from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).parent
FIG_DIR = HERE / "figures"


# ── Theme palettes (same scheme as generate_figures.py) ─────────────────

TRADITIONAL = {
    "name": "traditional",
    "bg": "white",
    "panel": "white",
    "text": "#1a1a1a",
    "text_secondary": "#555555",
    "grid": "#e8e8e8",
    "axis": "#444444",
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "accent1": "#2ca02c",   # green — positive
    "warning": "#d62728",   # red — negative
    "highlight": "#9467bd", # purple — special-cases
    "neutral": "#7f7f7f",
    "first_post": "#888888",
    "band": "rgba(44, 160, 44, 0.10)",
    "band_edge": "rgba(44, 160, 44, 0.5)",
    "band_text": "#1d6b1d",
    "font": "Arial, Helvetica, sans-serif",
}

CYBERPUNK = {
    "name": "cyberpunk",
    "bg": "#0a0a14",
    "panel": "#14141f",
    "text": "#ffffff",
    "text_secondary": "#a8a8d6",
    "grid": "#2a2a44",
    "axis": "#5a5a8a",
    "primary": "#ff006e",     # hot pink — headline
    "secondary": "#00ffff",   # cyan
    "accent1": "#00ff41",     # matrix green — positive
    "warning": "#ff5500",     # neon orange — negative
    "highlight": "#fbff12",   # neon yellow — special-cases
    "neutral": "#9d9dff",
    "first_post": "#7d7da8",
    "band": "rgba(0, 255, 65, 0.10)",
    "band_edge": "rgba(0, 255, 65, 0.6)",
    "band_text": "#00ff41",
    "font": "Courier New, monospace",
}


def save_fig(fig, theme, name, width, height):
    out = FIG_DIR / theme["name"] / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(str(out), width=width, height=height, scale=2)
    html_out = FIG_DIR / "interactive" / theme["name"] / f"{name}.html"
    html_out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(html_out), include_plotlyjs="cdn")
    print(f"  {out.relative_to(HERE)}")


# ── Data — pulled from the prep step ────────────────────────────────────

MISSING = [
    ("weight",            0.969),
    ("medical_specialty", 0.491),
    ("payer_code",        0.396),
    ("race",              0.022),
    ("diag_3",            0.014),
    ("diag_2",            0.004),
    ("diag_1",            0.0001),
]

# Locke audit findings — code/severity pairs from prep step
LOCKE_FINDINGS = [
    # (code, severity, count, label)
    ("E9002", "info",    49, "type-only missingness diagnostic"),
    ("E9007", "info",     7, "info-only sentinel hint"),
    ("E9082", "info",     2, "near-duplicate cat strings (info)"),
    ("E9073", "notice",  44, "duplicate-key disagreement (40 cols)"),
    ("E9011", "notice",  15, "high-cardinality categorical"),
    ("E9040", "notice",   5, "drift signal"),
    ("E9016", "notice",   3, "constant-ish column"),
    ("E9017", "notice",   3, "outlier hint"),
    ("E9023", "notice",   2, "label-encoding risk"),
    ("E9024", "notice",   1, "another nominal risk"),
    ("E9062", "notice",   1, "leakage warning"),
    ("E9072", "notice",   1, "ID-like (encounter_id)"),
    ("E9082", "warning",  5, "near-duplicate cat strings"),
    ("E9010", "warning",  2, "imbalanced target"),
    ("E9041", "warning",  1, "drift warning"),
    ("E9004", "error",    1, "patient_nbr 30K duplicates"),
]

# Per-leaf BeliefScore — naive vs ?-aware (leaf 1 = largest, 9617 rows).
# `overall` is a summary of the other 8 axes, not orthogonal — keep it
# off the radar so the polygon shape reflects orthogonal data-quality
# dimensions only.
BELIEF_AXES = [
    "schema", "missingness", "drift",
    "leakage", "lineage", "sample", "duplication", "constraint",
]
BELIEF_LEAF1_NAIVE   = [0.34, 1.0,    1.0, 1.0, 1.0, 1.0, 1.0, 0.88]
BELIEF_LEAF1_AWARE   = [0.34, 0.9621, 1.0, 1.0, 1.0, 1.0, 1.0, 0.88]


# ── #7 Per-column missingness bar chart ─────────────────────────────────

def fig_missingness(theme):
    fig = go.Figure()
    # Horizontal bar — top column first
    cols = [c for c, _ in MISSING]
    rates = [r for _, r in MISSING]
    cols_rev = list(reversed(cols))
    rates_rev = list(reversed(rates))
    colors = []
    for r in rates_rev:
        if r >= 0.5:
            colors.append(theme["warning"])
        elif r >= 0.1:
            colors.append(theme["secondary"])
        elif r >= 0.01:
            colors.append(theme["highlight"])
        else:
            colors.append(theme["neutral"])

    fig.add_trace(go.Bar(
        y=cols_rev, x=rates_rev,
        orientation="h",
        text=[f"<b>{r*100:.1f}%</b>" for r in rates_rev],
        textposition="outside",
        textfont=dict(family=theme["font"], color=theme["text"], size=13),
        marker=dict(color=colors, line=dict(color=theme["axis"], width=1)),
        showlegend=False,
        hovertemplate="<b>%{y}</b><br>?-rate: %{x:.1%}<extra></extra>",
    ))

    # Highlight band: >50% = "seriously missing"
    fig.add_shape(type="rect", x0=0.5, x1=1.0, y0=-0.5, y1=len(cols)-0.5,
                  fillcolor=theme["band"], line=dict(color=theme["band_edge"], width=1, dash="dot"),
                  layer="below")
    fig.add_annotation(
        x=0.97, y=len(cols)-0.5,
        text="<b>≥50% missing — drop or impute</b>",
        showarrow=False, xanchor="right", yanchor="top",
        font=dict(family=theme["font"], color=theme["band_text"], size=11),
        bgcolor=theme["panel"], borderpad=3,
    )

    fig.update_layout(
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["panel"],
        title=dict(text="<b>Diabetes-130 — per-column `?`-sentinel missingness</b><br>"
                        "<span style='font-size:12px;color:" + theme["text_secondary"] + "'>"
                        "7 of 50 columns contain any `?`. The first 3 carry almost all the missingness.</span>",
                   font=dict(family=theme["font"], color=theme["text"], size=15), x=0.02, xanchor="left"),
        font=dict(family=theme["font"], color=theme["text"]),
        xaxis=dict(range=[0, 1.10], tickformat=".0%",
                   gridcolor=theme["grid"], linecolor=theme["axis"],
                   title=dict(text="<b>% of rows where value is `?`</b>", font=dict(size=12))),
        yaxis=dict(gridcolor=theme["grid"], linecolor=theme["axis"],
                   tickfont=dict(family="Courier New, monospace", size=12)),
        margin=dict(t=80, l=180, r=40, b=60),
        bargap=0.30,
    )
    return fig


# ── #5 Locke findings sunburst ──────────────────────────────────────────

def fig_findings_sunburst(theme):
    """Sunburst hierarchy: severity (inner ring) → code (outer ring).

    Plotly note: don't put an explicit root with value=0 while using
    `branchvalues="total"` — Plotly refuses to render the wedges because
    children must sum to the parent value, and 0 != 142. Two options
    that work: (a) make the root value match the children's sum, or
    (b) drop the explicit root entirely. (b) is cleaner."""
    severity_color = {
        "error":   theme["warning"],
        "warning": theme["secondary"],
        "notice":  theme["primary"] if theme["name"] == "cyberpunk" else "#3a78b8",
        "info":    theme["neutral"],
    }
    labels = []
    parents = []
    values = []
    colors_list = []
    custom = []

    # Severity layer at the centre (no explicit root — Plotly will draw
    # them as the innermost ring automatically).
    sev_totals = {"error":1, "warning":8, "notice":75, "info":58}
    for sev, total in sev_totals.items():
        labels.append(f"<b>{sev}</b><br>{total}")
        parents.append("")    # no parent → centre ring
        values.append(total)
        colors_list.append(severity_color[sev])
        custom.append(f"{total} {sev}-level findings")

    # Codes (outer ring) hang off the severity wedges
    for code, sev, count, label in LOCKE_FINDINGS:
        labels.append(f"{code}<br>×{count}")
        parents.append(f"<b>{sev}</b><br>{sev_totals[sev]}")
        values.append(count)
        # Slightly tinted variant of the severity color
        colors_list.append(severity_color[sev])
        custom.append(f"{code}: {label}")

    fig = go.Figure(go.Sunburst(
        labels=labels, parents=parents, values=values,
        branchvalues="total",
        marker=dict(colors=colors_list, line=dict(color=theme["bg"], width=2)),
        hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
        customdata=custom,
        textfont=dict(family=theme["font"], color=theme["text"], size=11),
        insidetextorientation="radial",
    ))

    # Annotation pointing out the E9063 absence
    annotations = [
        dict(
            x=0.5, y=-0.06, xref="paper", yref="paper", xanchor="center", yanchor="top",
            text=f"<span style='font-size:11px;color:{theme['text_secondary']}'><i>"
                 f"E9063 (multi-class leakage detector) <b style='color:{theme['warning']}'>did NOT fire</b> on "
                 f"`discharge_disposition_id` — per-feature ROC-AUC misses per-level deterministic outcomes."
                 f"</i></span>",
            showarrow=False,
        ),
    ]

    fig.update_layout(
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["bg"],
        title=dict(text="<b>Locke audit — 142 findings on diabetes-130</b><br>"
                        f"<span style='font-size:12px;color:{theme['text_secondary']}'>"
                        f"Inner ring: severity (error 1 · warning 8 · notice 75 · info 58). "
                        f"Outer ring: 15 unique E-codes.</span>",
                   font=dict(family=theme["font"], color=theme["text"], size=15), x=0.02, xanchor="left"),
        font=dict(family=theme["font"], color=theme["text"]),
        margin=dict(t=85, l=20, r=20, b=80),
        annotations=annotations,
    )
    return fig


# ── #6 Per-leaf BeliefScore radar ───────────────────────────────────────

def fig_belief_radar(theme):
    # Repeat first axis to close the polygon
    theta = BELIEF_AXES + [BELIEF_AXES[0]]
    naive = BELIEF_LEAF1_NAIVE + [BELIEF_LEAF1_NAIVE[0]]
    aware = BELIEF_LEAF1_AWARE + [BELIEF_LEAF1_AWARE[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=naive, theta=theta,
        fill="toself", fillcolor="rgba(127,127,127,0.18)" if theme["name"] == "traditional" else "rgba(157,157,255,0.18)",
        line=dict(color=theme["neutral"], width=2),
        marker=dict(size=8, color=theme["neutral"]),
        name="Naive Locke (default)",
        hovertemplate="<b>Naive Locke</b><br>%{theta}: %{r:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=aware, theta=theta,
        fill="toself", fillcolor=f"rgba({'31,119,180' if theme['name']=='traditional' else '255,0,110'}, 0.30)",
        line=dict(color=theme["primary"], width=2.5),
        marker=dict(size=10, color=theme["primary"]),
        name="?-aware (with NullMaskMap)",
        hovertemplate="<b>?-aware</b><br>%{theta}: %{r:.4f}<extra></extra>",
    ))

    # Highlight the missingness axis where the dent appears
    fig.add_annotation(
        x=0.50, y=-0.13, xref="paper", yref="paper",
        text=f"<span style='font-size:11px;color:{theme['text_secondary']}'><i>"
             f"§4.D Part 1 fix shows up as a small dent at <b style='color:{theme['primary']}'>missingness</b> "
             f"(1.0000 → 0.9621). All other axes are unchanged: the `?`-fix is targeted, not noisy."
             f"</i></span>",
        showarrow=False, xanchor="center", yanchor="top",
    )

    fig.update_layout(
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["bg"],
        title=dict(text="<b>§4.D Part 1 — per-leaf BeliefScore vector (leaf 1, n=9,617 rows)</b><br>"
                        f"<span style='font-size:12px;color:{theme['text_secondary']}'>"
                        f"9-axis Locke BeliefScore: 1.0 = perfect on every axis. The naive polygon is a perfect octagon (everything 1.0); "
                        f"the ?-aware polygon dents at <b>missingness</b> because Locke now sees `?` as missing.</span>",
                   font=dict(family=theme["font"], color=theme["text"], size=15), x=0.02, xanchor="left"),
        font=dict(family=theme["font"], color=theme["text"]),
        polar=dict(
            bgcolor=theme["panel"],
            radialaxis=dict(visible=True, range=[0.30, 1.05],
                            gridcolor=theme["grid"], linecolor=theme["axis"],
                            tickfont=dict(family=theme["font"], color=theme["text_secondary"], size=10)),
            angularaxis=dict(gridcolor=theme["grid"], linecolor=theme["axis"],
                             tickfont=dict(family=theme["font"], color=theme["text"], size=12)),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5,
                    font=dict(family=theme["font"], color=theme["text"], size=12)),
        margin=dict(t=90, l=40, r=40, b=100),
    )
    return fig


# ── #1 ABNG architecture diagram ────────────────────────────────────────

def fig_abng_architecture(theme):
    """Schematic of K=2 routing + per-leaf BLR + root/leaf ensemble.

    For clarity, draw the K=1 visualisation (4 leaves) with a footnote
    that K=2 means 16 leaves (4×4). Drawing 16 leaves makes the diagram
    unreadable at social-media sizes.
    """
    fig = go.Figure()

    # Layout coordinates (manual placement)
    # X range: 0..10, Y range: 0..10
    # Top → bottom: Input φ, Routing decision, 4 leaves with BLR heads, Ensemble
    nodes = [
        # (x, y, label, color, kind)
        (5,    9.0, "Row → CategoricalTransform<br>→ (x, φ, y)",                  theme["text"],       "input"),
        (5,    7.2, "Root BLR<br><i>posterior on all data</i>",                    theme["highlight"],   "root"),
        (5,    5.3, "Routing decision<br><b>K=2 MI-selected features</b>",         theme["secondary"],   "routing"),
        # 4 leaves
        (1.2,  3.0, "Leaf 1<br><b>BLR</b>",                                        theme["primary"],     "leaf"),
        (3.7,  3.0, "Leaf 2<br><b>BLR</b>",                                        theme["primary"],     "leaf"),
        (6.3,  3.0, "Leaf 3<br><b>BLR</b>",                                        theme["primary"],     "leaf"),
        (8.8,  3.0, "Leaf 4<br><b>BLR</b>",                                        theme["primary"],     "leaf"),
        # Ensemble
        (5,    0.8, "<b>Ensemble = 0.5 × root + 0.5 × routed leaf</b>",            theme["accent1"],     "ensemble"),
    ]
    edges = [
        (0, 1),  # input → root
        (0, 2),  # input → routing
        # routing → leaves
        (2, 3), (2, 4), (2, 5), (2, 6),
        # leaves → ensemble
        (3, 7), (4, 7), (5, 7), (6, 7),
        # root → ensemble
        (1, 7),
    ]

    # Draw edges as lines first (under nodes)
    for (a, b) in edges:
        x0, y0, _, _, _ = nodes[a]
        x1, y1, _, _, _ = nodes[b]
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                      line=dict(color=theme["grid"] if theme["name"]=="traditional" else theme["axis"], width=2),
                      layer="below")

    # Draw nodes as rounded rectangles with text
    for x, y, label, color, kind in nodes:
        if kind == "leaf":
            w, h = 1.3, 1.1
        elif kind == "ensemble":
            w, h = 5.5, 1.0
        elif kind == "input":
            w, h = 4.2, 1.1
        else:
            w, h = 4.0, 1.1
        fig.add_shape(type="rect", x0=x-w/2, y0=y-h/2, x1=x+w/2, y1=y+h/2,
                      line=dict(color=color, width=2),
                      fillcolor=theme["panel"], opacity=0.95,
                      layer="below")
        fig.add_annotation(
            x=x, y=y, text=label,
            showarrow=False, xanchor="center", yanchor="middle",
            font=dict(family=theme["font"], color=color, size=11),
        )

    # Side-channel annotations
    fig.add_annotation(
        x=0.4, y=5.3, text=f"<i>routing on top-K=2<br>MI-scored cols</i>",
        showarrow=False, xanchor="left", yanchor="middle",
        font=dict(family=theme["font"], color=theme["text_secondary"], size=10),
    )
    fig.add_annotation(
        x=9.6, y=7.2, text=f"<i>root sees<br>all rows</i>",
        showarrow=False, xanchor="right", yanchor="middle",
        font=dict(family=theme["font"], color=theme["text_secondary"], size=10),
    )
    fig.add_annotation(
        x=5, y=4.2, text="<i>each row routes to exactly one leaf</i>",
        showarrow=False, xanchor="center", yanchor="middle",
        font=dict(family=theme["font"], color=theme["text_secondary"], size=10),
    )

    # Footnote
    fig.add_annotation(
        x=5, y=-0.4, text=f"<span style='font-size:10px;color:{theme['text_secondary']}'><i>"
                          f"Shown: K=1 (4 leaves) for legibility. <b>Actual diabetes-130 config: K=2 → 16 leaves</b> "
                          f"(4 routing bins × 4 routing bins). Audit-chain SHA-256 hash advances per `train_step`."
                          f"</i></span>",
        showarrow=False, xanchor="center", yanchor="top",
    )

    fig.update_layout(
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["bg"],
        title=dict(text="<b>ABNG — routing tree + per-leaf BLR + root/leaf ensemble</b><br>"
                        f"<span style='font-size:12px;color:{theme['text_secondary']}'>"
                        f"Frozen MI-selected routing decides which leaf a row trains. Each leaf is a Bayesian "
                        f"linear regression with conjugate posterior. Root sees everything; ensemble averages "
                        f"root + leaf at predict.</span>",
                   font=dict(family=theme["font"], color=theme["text"], size=15), x=0.02, xanchor="left"),
        xaxis=dict(range=[-1, 11], visible=False),
        yaxis=dict(range=[-1, 10], visible=False, scaleanchor="x", scaleratio=0.65),
        margin=dict(t=85, l=20, r=20, b=40),
        showlegend=False,
    )
    return fig


# ── #11 §4.B confounded experiment flow ─────────────────────────────────

def fig_confounded_flow(theme):
    fig = go.Figure()

    def box(x, y, w, h, label, color, fontcolor=None):
        fig.add_shape(type="rect", x0=x-w/2, y0=y-h/2, x1=x+w/2, y1=y+h/2,
                      line=dict(color=color, width=2),
                      fillcolor=theme["panel"], opacity=0.95)
        fig.add_annotation(x=x, y=y, text=label,
                           showarrow=False, xanchor="center", yanchor="middle",
                           font=dict(family=theme["font"],
                                     color=fontcolor or color, size=12))

    def arrow(x0, y0, x1, y1, color, width=2):
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2, arrowsize=1.4, arrowwidth=width,
                           arrowcolor=color, text="")

    # Top action box
    box(5, 9, 6, 1.0, "<b>§4.B intervention</b><br>drop discharge-codes 11, 13, 14, 19, 20, 21<br>(death &amp; hospice — −2,423 rows)",
        theme["highlight"], fontcolor=theme["text"])

    # Two effects boxes
    box(2.0, 6.5, 3.6, 1.4,
        f"<b style='color:{theme['accent1']}'>EFFECT A</b><br>"
        f"<span style='color:{theme['text']}'>Leakage rows removed ✓</span><br>"
        f"<i style='color:{theme['text_secondary']};font-size:10px'>dead patients can't be readmitted —<br>"
        f"those rows were deterministically 'NO'</i>",
        theme["accent1"], fontcolor=None)

    box(8.0, 6.5, 3.6, 1.4,
        f"<b style='color:{theme['warning']}'>EFFECT B</b><br>"
        f"<span style='color:{theme['text']}'>MI re-selects routing features</span><br>"
        f"<i style='color:{theme['text_secondary']};font-size:10px'>time_in_hospital → number_emergency<br>"
        f"(weaker top-2 partner for num_inpatient)</i>",
        theme["warning"], fontcolor=None)

    # Arrows from top to effects
    arrow(3.5, 8.5, 2.0, 7.2, theme["accent1"])
    arrow(6.5, 8.5, 8.0, 7.2, theme["warning"])

    # Bottom outcome
    box(5, 3.2, 7.5, 1.8,
        f"<b style='color:{theme['warning']}'>Net effect: AUC drops 0.6312 → 0.6194 (−0.0118)</b><br>"
        f"<span style='color:{theme['text']}'>routing-feature loss &gt; leakage-removal gain</span><br>"
        f"<i style='color:{theme['text_secondary']};font-size:10px'>This is a <u>confounded</u> experiment.<br>"
        f"To isolate Effect A, you'd need to <i>force</i> the same routing columns across both configs.</i>",
        theme["warning"])

    arrow(2.0, 5.8, 4.0, 4.2, theme["text_secondary"])
    arrow(8.0, 5.8, 6.0, 4.2, theme["text_secondary"])

    # Footnote — text split across two lines so it fits within the
    # canvas without needing margin overrun.
    fig.add_annotation(
        x=5, y=1.4, text=f"<span style='font-size:11px;color:{theme['text_secondary']}'><i>"
                        f"At full 101K (§4.E), MI picks <b>[num_inpatient, number_emergency]</b> too —"
                        f"<br>Effect B was about to happen anyway as data scaled. "
                        f"The §4.B prune just surfaced it early, in a setting where the linear BLR couldn't yet absorb the routing change."
                         f"</i></span>",
        showarrow=False, xanchor="center", yanchor="top",
    )

    fig.update_layout(
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["bg"],
        title=dict(text="<b>§4.B — why removing leakage rows hurt AUC</b><br>"
                        f"<span style='font-size:12px;color:{theme['text_secondary']}'>"
                        f"A confounded experiment: the prune does two things at once. The downstream MI shift dominated.</span>",
                   font=dict(family=theme["font"], color=theme["text"], size=15), x=0.02, xanchor="left"),
        xaxis=dict(range=[-1, 11], visible=False),
        yaxis=dict(range=[-0.5, 10.5], visible=False, scaleanchor="x", scaleratio=0.55),
        margin=dict(t=80, l=20, r=20, b=20),
        showlegend=False,
    )
    return fig


# ── #4 Pearson heatmap (Plotly recreation, themed) ──────────────────────

# Data sourced from Locke's actual SVG (extracted into figures/locke/pearson_heatmap_raw.svg)
PEARSON_COLS = [
    "encounter_id", "patient_nbr", "admission_type_id",
    "discharge_disposition_id", "num_lab_procedures", "diag_1",
]
PEARSON_R = [
    # encounter_id  patient_nbr  adm_type   disp_id    lab_proc   diag_1
    [ 1.000,   0.512,  -0.159,  -0.133,  -0.026,   0.012],  # encounter_id
    [ 0.512,   1.000,  -0.011,  -0.137,   0.016,   0.014],  # patient_nbr
    [-0.159,  -0.011,   1.000,   0.083,  -0.144,  -0.002],  # adm_type_id
    [-0.133,  -0.137,   0.083,   1.000,   0.023,   0.012],  # disp_id
    [-0.026,   0.016,  -0.144,   0.023,   1.000,  -0.063],  # num_lab_procedures
    [ 0.012,   0.014,  -0.002,   0.012,  -0.063,   1.000],  # diag_1
]


def fig_pearson_heatmap(theme):
    # Build a custom colorscale that highlights |r|, neutral at 0
    if theme["name"] == "traditional":
        colorscale = [[0.0, theme["primary"]],   # blue for strongly negative
                      [0.5, "#f7f7f7"],          # neutral
                      [1.0, theme["warning"]]]   # red for strongly positive
    else:
        colorscale = [[0.0, theme["secondary"]],  # cyan for negative
                      [0.5, theme["panel"]],
                      [1.0, theme["primary"]]]   # hot pink for positive

    fig = go.Figure(go.Heatmap(
        z=PEARSON_R, x=PEARSON_COLS, y=PEARSON_COLS,
        colorscale=colorscale, zmin=-1, zmax=1, zmid=0,
        text=[[f"{v:.2f}" for v in row] for row in PEARSON_R],
        texttemplate="%{text}",
        textfont=dict(family=theme["font"], color=theme["text"], size=11),
        hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(title=dict(text="<b>r</b>", font=dict(family=theme["font"], color=theme["text"])),
                      tickfont=dict(family=theme["font"], color=theme["text"]),
                      thickness=15, len=0.7),
    ))

    # Annotate the standout r=0.512 (encounter_id × patient_nbr)
    fig.add_annotation(
        x="patient_nbr", y="encounter_id", ax="patient_nbr", ay=-0.6,
        xref="x", yref="y", axref="x", ayref="y",
        text="<b>r=0.512</b><br><i>encounter_id and patient_nbr<br>are admin-numbered together</i>",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5,
        arrowcolor=theme["warning"] if theme["name"]=="traditional" else theme["primary"],
        font=dict(family=theme["font"], color=theme["text"], size=10),
        bgcolor=theme["panel"], borderpad=4,
        bordercolor=theme["warning"] if theme["name"]=="traditional" else theme["primary"],
        xanchor="left", yanchor="bottom",
    )

    fig.update_layout(
        paper_bgcolor=theme["bg"], plot_bgcolor=theme["bg"],
        title=dict(text="<b>Locke audit — Pearson r heatmap (top-6 numeric columns)</b><br>"
                        f"<span style='font-size:12px;color:{theme['text_secondary']}'>"
                        f"Inline-SVG artifact generated by `cjcl locke validate`. Content-addressed and "
                        f"bit-reproducible across runs. Diagonal is 1.00 by definition; "
                        f"the off-diagonal r=0.512 catches that the two ID columns are sorted together.</span>",
                   font=dict(family=theme["font"], color=theme["text"], size=15), x=0.02, xanchor="left"),
        font=dict(family=theme["font"], color=theme["text"]),
        xaxis=dict(side="bottom", tickangle=-30,
                   tickfont=dict(family="Courier New, monospace", color=theme["text"], size=11)),
        yaxis=dict(autorange="reversed",
                   tickfont=dict(family="Courier New, monospace", color=theme["text"], size=11)),
        margin=dict(t=110, l=180, r=80, b=110),
    )
    return fig


# ── Driver ──────────────────────────────────────────────────────────────

FIGURES = [
    ("per_column_missingness",       fig_missingness,        1100, 520),
    ("locke_findings_sunburst",      fig_findings_sunburst,   900, 760),
    ("per_leaf_belief_radar",        fig_belief_radar,        900, 760),
    ("abng_architecture",            fig_abng_architecture,  1100, 700),
    ("confounded_experiment_flow",   fig_confounded_flow,    1100, 700),
    ("locke_pearson_heatmap",        fig_pearson_heatmap,     900, 760),
]


def main():
    for theme in [TRADITIONAL, CYBERPUNK]:
        print(f"\n[{theme['name']}]")
        for name, builder, w, h in FIGURES:
            fig = builder(theme)
            save_fig(fig, theme, name, w, h)
    print("\ndone.")


if __name__ == "__main__":
    main()
