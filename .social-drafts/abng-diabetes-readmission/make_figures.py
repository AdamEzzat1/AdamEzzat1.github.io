#!/usr/bin/env python3
"""Figures for the ABNG x Diabetes-130 blog post -- Plotly edition.

Every number is from the Phase 0.9.5 COMMIT-7 runs in the CJC-Lang repo
(tests/abng/dataset_a_diabetes130.rs), seed 42, on the 20,000-row
stratified sub-sample, held-out test split (n_test = 3,002). The runs are
deterministic -- re-running reproduces these exactly.

Static PNGs via Plotly + kaleido, written into ./figures/ (scale=2):
  LinkedIn (1300x720):   auc_trajectory.png  calibration.png  krouting_sweep.png
  Instagram (1080x1080): ig_trajectory.png   ig_calibration.png ig_krouting.png

  python make_figures.py
"""
import os
import plotly
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# Titles here use plain HTML (<b>, <sub>, <br>, —) -- never LaTeX.
# Disabling MathJax skips a CDN fetch that kaleido would otherwise block
# on; that fetch is the main cause of the static-export hang on Windows.
pio.kaleido.scope.mathjax = None

# kaleido 0.1.0.post1 bundles an old plotly.js that throws on the subplot
# figures emitted by plotly 5.x (kaleido "error code 525"). Point kaleido
# at plotly's own matching plotly.js so renderer and figure JSON agree.
_PLOTLYJS = os.path.join(os.path.dirname(plotly.__file__),
                         "package_data", "plotly.min.js")
if os.path.exists(_PLOTLYJS):
    pio.kaleido.scope.plotlyjs = _PLOTLYJS

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "figures")
os.makedirs(OUTDIR, exist_ok=True)

INK = "#1a1a2e"
RAW = "#9aa0b4"      # muted grey: raw / uncalibrated
GOOD = "#0e7c66"     # teal: the improved number
ACCENT = "#c2410c"   # warm: reference lines
BAND = "#e4e7ee"
FONT = "Arial, DejaVu Sans, sans-serif"

# ===== verified data =====
TRAJ_LABELS = ["2,000 rows<br>baseline",
               "20,000 rows<br>default config",
               "20,000 rows<br>tuned config"]
TRAJ_AUC = [0.5499, 0.5870, 0.6107]
CHANCE = 0.50
STRONG_LO, STRONG_HI = 0.64, 0.68

CAL = [("Brier score", 0.1000, 0.0980, 0.0994),
       ("Log loss (NLL)", 0.3913, 0.3435, 0.3505),
       ("Calibration error (ECE)", 0.0314, 0.0101, 0.0)]

SWEEP = {"K_ROUTING = 2": [0.6050, 0.6058, 0.6095],
         "K_ROUTING = 3": [0.5589, 0.5670, 0.5797],
         "K_ROUTING = 4": [0.5830, 0.5843, 0.5931]}
PRECS = ["BLR prior precision 0.01", "BLR prior precision 0.10",
         "BLR prior precision 1.00"]
PREC_COLORS = ["#cbd5e1", "#64748b", GOOD]

BLOG = (1300, 720)
SQUARE = (1080, 1080)


def _write(fig, name, square):
    w, h = SQUARE if square else BLOG
    out = os.path.join(OUTDIR, name)
    fig.write_image(out, width=w, height=h, scale=2)
    print("wrote", out, flush=True)


def fig_trajectory(square):
    fs = 1.35 if square else 1.0
    fig = go.Figure()
    fig.add_hrect(y0=STRONG_LO, y1=STRONG_HI, fillcolor=BAND,
                  line_width=0, layer="below")
    fig.add_hline(y=CHANCE, line_dash="dash", line_color=RAW, line_width=1.6)
    fig.add_trace(go.Scatter(
        x=TRAJ_LABELS, y=TRAJ_AUC, mode="lines+markers+text",
        line=dict(color=GOOD, width=4), marker=dict(size=18, color=GOOD),
        text=[f"<b>{a:.3f}</b>" for a in TRAJ_AUC], textposition="top center",
        textfont=dict(size=int(19 * fs), color=GOOD),
        cliponaxis=False, showlegend=False))
    fig.add_annotation(x=2, y=(STRONG_LO + STRONG_HI) / 2,
                       text="strong published<br>models ~0.64-0.68",
                       showarrow=False, xanchor="right",
                       font=dict(size=int(12.5 * fs), color="#6b7280"))
    fig.add_annotation(x=0, y=CHANCE, yshift=-15, text="chance = 0.50",
                       showarrow=False, xanchor="left",
                       font=dict(size=int(12 * fs), color="#6b7280"))
    fig.update_layout(
        template="plotly_white",
        title=dict(text="<b>ABNG on Diabetes-130 readmission</b><br>"
                        "<sub>held-out test AUC: real, modest progress</sub>",
                   x=0.5, xanchor="center", font=dict(size=int(21 * fs), color=INK)),
        yaxis=dict(range=[0.47, 0.70], title="Held-out test AUC",
                   title_font=dict(size=int(15 * fs)),
                   tickfont=dict(size=int(12 * fs))),
        xaxis=dict(tickfont=dict(size=int(12.5 * fs))),
        font=dict(family=FONT, color=INK),
        margin=dict(l=75, r=45, t=95, b=80))
    _write(fig, "ig_trajectory.png" if square else "auc_trajectory.png", square)


def fig_calibration(square):
    fs = 1.3 if square else 1.0
    titles = [c[0] for c in CAL]
    if square:
        fig = make_subplots(rows=3, cols=1, subplot_titles=titles,
                            vertical_spacing=0.13)
    else:
        fig = make_subplots(rows=1, cols=3, subplot_titles=titles,
                            horizontal_spacing=0.085)
    for i, (_metric, raw, cal, base) in enumerate(CAL):
        r, c = (i + 1, 1) if square else (1, i + 1)
        # Three bars -- raw, calibrated, and the do-nothing base-rate
        # predictor -- so the comparison reads off directly, with no
        # reference line whose label would collide with the bar labels.
        fig.add_trace(go.Bar(
            x=["raw", "calibrated", "base rate"], y=[raw, cal, base],
            marker_color=[RAW, GOOD, ACCENT], width=0.62,
            text=[f"<b>{raw:.3f}</b>", f"<b>{cal:.3f}</b>", f"<b>{base:.3f}</b>"],
            textposition="outside", textfont=dict(size=int(12.5 * fs)),
            cliponaxis=False, showlegend=False), row=r, col=c)
        fig.update_yaxes(range=[0, max(raw, cal, base) * 1.32], row=r, col=c,
                         tickfont=dict(size=int(10.5 * fs)))
        fig.update_xaxes(tickfont=dict(size=int(11.5 * fs)), row=r, col=c)
    fig.update_layout(
        template="plotly_white",
        title=dict(text="<b>Post-hoc Platt calibration — lower is better</b><br>"
                        "<sub>raw vs calibrated vs the do-nothing base-rate predictor</sub>",
                   x=0.5, xanchor="center", font=dict(size=int(19 * fs), color=INK)),
        font=dict(family=FONT, color=INK),
        margin=dict(l=60, r=45, t=190 if square else 120, b=55))
    fig.update_annotations(font_size=int(13.5 * fs))  # subplot titles
    _write(fig, "ig_calibration.png" if square else "calibration.png", square)


def fig_krouting(square):
    fs = 1.3 if square else 1.0
    ks = list(SWEEP.keys())
    fig = go.Figure()
    for j, prec in enumerate(PRECS):
        fig.add_trace(go.Bar(name=prec, x=ks, y=[SWEEP[k][j] for k in ks],
                             marker_color=PREC_COLORS[j]))
    fig.add_annotation(x="K_ROUTING = 2", y=SWEEP["K_ROUTING = 2"][2],
                       yshift=int(34 * fs),
                       text="<b>best config (K=2, prec 1.0)</b>",
                       showarrow=False,
                       font=dict(size=int(12 * fs), color=GOOD))
    fig.update_layout(
        template="plotly_white", barmode="group",
        title=dict(text="<b>Hyperparameter sweep on the 20K rung</b><br>"
                        "<sub>shallower routing won — deeper trees starve "
                        "each leaf</sub>",
                   x=0.5, xanchor="center", font=dict(size=int(19 * fs), color=INK)),
        yaxis=dict(range=[0.54, 0.625], title="Validation AUC",
                   title_font=dict(size=int(15 * fs)),
                   tickfont=dict(size=int(11.5 * fs))),
        xaxis=dict(tickfont=dict(size=int(13 * fs))),
        legend=dict(orientation="h", yanchor="bottom", y=1.005,
                    xanchor="center", x=0.5, font=dict(size=int(11 * fs))),
        font=dict(family=FONT, color=INK),
        margin=dict(l=75, r=45, t=135, b=60))
    _write(fig, "ig_krouting.png" if square else "krouting_sweep.png", square)


if __name__ == "__main__":
    for square in (False, True):
        fig_trajectory(square)
        fig_calibration(square)
        fig_krouting(square)
    print("done -- 6 Plotly figures in", HERE)
