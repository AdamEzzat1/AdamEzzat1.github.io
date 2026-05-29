"""Phase 0.10 figures — traditional Plotly + cyberpunk themes.

Generates 5 figures × 2 themes = 10 PNGs into figures/<theme>/, plus
interactive HTML copies into figures/interactive/<theme>/.

Run: `python generate_figures.py`
"""

import os
import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

HERE = Path(__file__).parent
FIG_DIR = HERE / "figures"
TRAD_DIR = FIG_DIR / "traditional"
CYBER_DIR = FIG_DIR / "cyberpunk"
INTERACTIVE_DIR = FIG_DIR / "interactive"

for d in [TRAD_DIR, CYBER_DIR, INTERACTIVE_DIR, INTERACTIVE_DIR / "traditional", INTERACTIVE_DIR / "cyberpunk"]:
    d.mkdir(parents=True, exist_ok=True)


# ── Theme dictionaries ──────────────────────────────────────────────────

TRADITIONAL = {
    "name": "traditional",
    "template": "plotly_white",
    "bg": "white",
    "plot_bg": "white",
    "text": "#2a2a2a",
    "grid": "#e8e8e8",
    "axis": "#444444",
    "primary": "#1f77b4",     # plotly blue — headline color
    "secondary": "#ff7f0e",   # plotly orange — Round Two improvements
    "accent1": "#2ca02c",     # plotly green — positive / strong-model band
    "accent2": "#d62728",     # plotly red (unused after warning split)
    "warning": "#d62728",     # red — negative result (§4.B prune hurt AUC)
    "neutral": "#7f7f7f",     # gray
    "band": "rgba(44, 160, 44, 0.10)",   # light green band for strong-model
    "band_edge": "rgba(44, 160, 44, 0.5)",
    "band_text": "#1d6b1d",              # dark green for band annotation
    "first_post": "#888888",
    "font_family": "Arial, Helvetica, sans-serif",
    "title_size": 16,
    "axis_label_size": 13,
    "tick_size": 11,
    "marker_size": 12,
    "line_width": 2.5,
}

CYBERPUNK = {
    "name": "cyberpunk",
    "template": "plotly_dark",
    "bg": "#0a0a14",
    "plot_bg": "#14141f",
    "text": "#e5e5ff",
    "grid": "#2a2a44",
    "axis": "#5a5a8a",
    "primary": "#ff006e",     # hot pink — headline color
    "secondary": "#00ffff",   # cyan — Round Two improvements
    "accent1": "#fbff12",     # neon yellow
    "accent2": "#00ff41",     # matrix green — positive / strong-model band
    "warning": "#ff5500",     # neon orange — negative result (§4.B prune hurt AUC)
    "neutral": "#9d9dff",     # lavender
    "band": "rgba(0, 255, 65, 0.10)",
    "band_edge": "rgba(0, 255, 65, 0.6)",
    "band_text": "#00ff41",              # matrix green for band annotation
    "first_post": "#7d7da8",
    "font_family": "Courier New, monospace",
    "title_size": 16,
    "axis_label_size": 13,
    "tick_size": 11,
    "marker_size": 14,
    "line_width": 3.0,
}


def style_layout(fig, theme, title=None, xaxis_title=None, yaxis_title=None,
                 height=480, width=900, legend_y=1.02):
    """Apply common layout styling to a figure under one theme."""
    fig.update_layout(
        template=theme["template"],
        paper_bgcolor=theme["bg"],
        plot_bgcolor=theme["plot_bg"],
        font=dict(family=theme["font_family"], color=theme["text"], size=theme["tick_size"]),
        title=dict(
            text=title or "",
            font=dict(size=theme["title_size"], color=theme["text"]),
            x=0.02, xanchor="left",
        ) if title else None,
        xaxis=dict(
            title=dict(text=xaxis_title or "", font=dict(size=theme["axis_label_size"])),
            gridcolor=theme["grid"], linecolor=theme["axis"], tickcolor=theme["axis"],
            zerolinecolor=theme["grid"],
        ),
        yaxis=dict(
            title=dict(text=yaxis_title or "", font=dict(size=theme["axis_label_size"])),
            gridcolor=theme["grid"], linecolor=theme["axis"], tickcolor=theme["axis"],
            zerolinecolor=theme["grid"],
        ),
        height=height, width=width,
        margin=dict(t=60 if title else 30, l=70, r=30, b=60),
        legend=dict(
            orientation="h", yanchor="bottom", y=legend_y, xanchor="right", x=1,
            font=dict(size=theme["tick_size"]),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


def save_fig(fig, theme, name):
    """Save fig as PNG into figures/<theme>/<name>.png and HTML into figures/interactive/<theme>/<name>.html."""
    png_path = FIG_DIR / theme["name"] / f"{name}.png"
    html_path = FIG_DIR / "interactive" / theme["name"] / f"{name}.html"
    fig.write_image(str(png_path), scale=2)
    fig.write_html(str(html_path), include_plotlyjs="cdn")
    print(f"  saved {png_path.name} + interactive HTML")


# ── Figure 1: AUC trajectory ────────────────────────────────────────────

AUC_PHASES = [
    {"label": "First post<br>(20K, K=3, raw)",      "auc": 0.5760, "n": "20K",   "kind": "first_baseline"},
    {"label": "First post<br>(20K, K=2 calibrated)",   "auc": 0.6107, "n": "20K",   "kind": "first_published"},
    {"label": "§4.A<br>(20K, K=2, prior=0.5)",     "auc": 0.6312, "n": "20K",   "kind": "round_two"},
    {"label": "§4.B<br>(20K, K=2, pruned)",         "auc": 0.6194, "n": "20K",   "kind": "negative"},
    {"label": "§4.E<br>(101K, K=2, seed 42)",      "auc": 0.6621, "n": "101K",  "kind": "round_two"},
    {"label": "§4.F<br>(101K, K=2, 3-seed mean)",  "auc": 0.6645, "auc_std": 0.0018, "n": "101K", "kind": "headline"},
]


def fig_auc_trajectory(theme):
    fig = go.Figure()

    # Strong-model band 0.64-0.68 (shaded region)
    fig.add_shape(type="rect", x0=-0.5, x1=len(AUC_PHASES) - 0.5,
                  y0=0.64, y1=0.68,
                  line=dict(color=theme["band_edge"], width=1, dash="dot"),
                  fillcolor=theme["band"], layer="below")
    fig.add_annotation(x=0.05, y=0.685, text="Strong-published-model band (0.64–0.68)",
                       showarrow=False, xanchor="left", yanchor="bottom",
                       font=dict(color=theme["band_text"], size=11, family=theme["font_family"]),
                       bgcolor=theme["plot_bg"], borderpad=3)

    # Coin-flip baseline
    fig.add_hline(y=0.5, line=dict(color=theme["neutral"], width=1, dash="dot"),
                  annotation_text="Random (0.50)", annotation_position="bottom right",
                  annotation=dict(font=dict(color=theme["neutral"], size=11)))

    # First post calibrated headline
    fig.add_hline(y=0.611, line=dict(color=theme["first_post"], width=1, dash="dash"),
                  annotation_text="First post calibrated (0.611)", annotation_position="top right",
                  annotation=dict(font=dict(color=theme["first_post"], size=11)))

    # Bars / markers
    xs = list(range(len(AUC_PHASES)))
    labels = [p["label"] for p in AUC_PHASES]
    aucs = [p["auc"] for p in AUC_PHASES]
    colors = []
    for p in AUC_PHASES:
        if p["kind"] == "first_baseline":
            colors.append(theme["neutral"])
        elif p["kind"] == "first_published":
            colors.append(theme["first_post"])
        elif p["kind"] == "negative":
            colors.append(theme["warning"])     # negative-result signal in both themes
        elif p["kind"] == "headline":
            colors.append(theme["primary"])
        else:
            colors.append(theme["secondary"])

    fig.add_trace(go.Bar(
        x=xs, y=aucs,
        text=[f"<b>{a:.4f}</b>" for a in aucs],
        textposition="outside",
        textfont=dict(color=theme["text"], size=12),
        marker=dict(color=colors, line=dict(color=theme["axis"], width=1)),
        showlegend=False,
        hovertemplate="%{customdata}<br>AUC: <b>%{y:.4f}</b><extra></extra>",
        customdata=labels,
    ))

    # Add error bars for the 3-seed result
    headline_idx = next(i for i, p in enumerate(AUC_PHASES) if p["kind"] == "headline")
    fig.add_trace(go.Scatter(
        x=[xs[headline_idx]], y=[AUC_PHASES[headline_idx]["auc"]],
        error_y=dict(type="data", array=[AUC_PHASES[headline_idx]["auc_std"]], color=theme["accent1"], thickness=3, width=6),
        mode="markers",
        marker=dict(size=0, color=theme["accent1"]),
        showlegend=False,
        hoverinfo="skip",
    ))

    fig.update_layout(
        xaxis=dict(tickmode="array", tickvals=xs, ticktext=labels, tickangle=0),
        yaxis=dict(range=[0.45, 0.72]),
        bargap=0.30,
    )
    style_layout(fig, theme,
                 title="<b>Held-out test AUC trajectory — diabetes-130 readmission</b>",
                 xaxis_title="", yaxis_title="<b>AUC</b>",
                 height=540, width=1080)
    return fig


# ── Figure 2: Multi-seed variance ───────────────────────────────────────

MULTI_SEED = {
    "AUC":           {"seeds": [0.6621, 0.6664, 0.6649], "mean": 0.6645, "std": 0.0018, "range_lo": 0.660, "range_hi": 0.670},
    "Brier":         {"seeds": [0.0953, 0.0948, 0.0950], "mean": 0.0950, "std": 0.0002, "range_lo": 0.094, "range_hi": 0.096},
    "NLL":           {"seeds": [0.3349, 0.3340, 0.3347], "mean": 0.3346, "std": 0.0004, "range_lo": 0.333, "range_hi": 0.336},
    "ECE":           {"seeds": [0.0044, 0.0030, 0.0041], "mean": 0.0038, "std": 0.0006, "range_lo": 0.000, "range_hi": 0.008},
    "Bal. accuracy": {"seeds": [0.5012, 0.5015, 0.5030], "mean": 0.5019, "std": 0.0008, "range_lo": 0.500, "range_hi": 0.504},
    "F1 @ 0.5":      {"seeds": [0.0061, 0.0070, 0.0130], "mean": 0.0087, "std": 0.0031, "range_lo": 0.000, "range_hi": 0.016},
}

SEED_LABELS = ["seed 42", "seed 43", "seed 44"]


def fig_multi_seed(theme):
    metrics = list(MULTI_SEED.keys())
    fig = make_subplots(rows=2, cols=3, subplot_titles=[f"<b>{m}</b>" for m in metrics],
                        horizontal_spacing=0.10, vertical_spacing=0.18)

    seed_colors = [theme["primary"], theme["secondary"], theme["accent1"]]

    for i, metric in enumerate(metrics):
        row = i // 3 + 1
        col = i % 3 + 1
        d = MULTI_SEED[metric]

        # Mean ± std band
        fig.add_shape(type="rect", x0=-0.5, x1=2.5,
                      y0=d["mean"] - d["std"], y1=d["mean"] + d["std"],
                      line=dict(color=theme["band_edge"], width=1, dash="dot"),
                      fillcolor=theme["band"], layer="below",
                      row=row, col=col)

        # Mean line
        fig.add_trace(go.Scatter(
            x=[-0.5, 2.5], y=[d["mean"], d["mean"]],
            mode="lines", line=dict(color=theme["neutral"], width=2, dash="dash"),
            showlegend=False, hoverinfo="skip",
        ), row=row, col=col)

        # Per-seed dots
        fig.add_trace(go.Scatter(
            x=[0, 1, 2], y=d["seeds"],
            mode="markers+text",
            text=[f"{v:.4f}" for v in d["seeds"]],
            textposition="top center",
            textfont=dict(color=theme["text"], size=10),
            marker=dict(size=theme["marker_size"], color=seed_colors,
                        line=dict(color=theme["axis"], width=1.5)),
            showlegend=False,
            hovertemplate="<b>%{customdata}</b><br>%{y:.4f}<extra></extra>",
            customdata=SEED_LABELS,
        ), row=row, col=col)

        # Update axes per subplot
        fig.update_xaxes(tickmode="array", tickvals=[0, 1, 2], ticktext=SEED_LABELS,
                         range=[-0.6, 2.6], gridcolor=theme["grid"], linecolor=theme["axis"],
                         row=row, col=col)
        fig.update_yaxes(range=[d["range_lo"], d["range_hi"]],
                         gridcolor=theme["grid"], linecolor=theme["axis"],
                         row=row, col=col)

    fig.update_annotations(font=dict(color=theme["text"], size=12))

    fig.update_layout(
        template=theme["template"],
        paper_bgcolor=theme["bg"],
        plot_bgcolor=theme["plot_bg"],
        font=dict(family=theme["font_family"], color=theme["text"], size=theme["tick_size"]),
        title=dict(
            text="<b>§4.F multi-seed variance — full 101K, K=2, prior=0.5</b>",
            font=dict(size=theme["title_size"], color=theme["text"]),
            x=0.02, xanchor="left",
        ),
        height=620, width=1080,
        margin=dict(t=70, l=60, r=30, b=40),
        showlegend=False,
    )
    return fig


# ── Figure 3: Per-leaf belief — naive vs ?-aware ────────────────────────

LEAVES = [
    {"id": 1, "n_rows": 9617, "naive_miss": 1.0000, "aware_miss": 0.9621},
    {"id": 2, "n_rows": 6215, "naive_miss": 1.0000, "aware_miss": 0.9624},
    {"id": 3, "n_rows": 2545, "naive_miss": 1.0000, "aware_miss": 0.9621},
    {"id": 4, "n_rows": 1623, "naive_miss": 1.0000, "aware_miss": 0.9613},
]


def fig_per_leaf_belief(theme):
    fig = go.Figure()

    labels = [f"Leaf {l['id']}<br><span style='font-size:11px'>n={l['n_rows']:,}</span>" for l in LEAVES]
    naive = [l["naive_miss"] for l in LEAVES]
    aware = [l["aware_miss"] for l in LEAVES]

    fig.add_trace(go.Bar(
        name="Naive (default Locke)", x=labels, y=naive,
        text=[f"<b>{v:.4f}</b>" for v in naive],
        textposition="outside",
        textfont=dict(color=theme["text"], size=11),
        marker=dict(color=theme["neutral"], line=dict(color=theme["axis"], width=1)),
        hovertemplate="<b>%{x}</b><br>Naive missingness_score: %{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="?-aware (with NullMaskMap)", x=labels, y=aware,
        text=[f"<b>{v:.4f}</b>" for v in aware],
        textposition="outside",
        textfont=dict(color=theme["text"], size=11),
        marker=dict(color=theme["primary"], line=dict(color=theme["axis"], width=1)),
        hovertemplate="<b>%{x}</b><br>?-aware missingness_score: %{y:.4f}<extra></extra>",
    ))

    # Reference line at 1.0
    fig.add_hline(y=1.0, line=dict(color=theme["accent1"], width=1.2, dash="dot"))
    # Annotation lifted into the headroom above the y=1.0 line so it
    # doesn't collide with the "1.0000" bar-top labels.
    fig.add_annotation(x=0.02, y=1.018, xref="paper",
                       text="Perfect (no missingness detected)",
                       showarrow=False, xanchor="left", yanchor="middle",
                       font=dict(color=theme["accent1"], size=11, family=theme["font_family"]),
                       bgcolor=theme["plot_bg"], borderpad=3)

    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0.94, 1.030]),
        bargap=0.30, bargroupgap=0.05,
    )
    style_layout(fig, theme,
                 title="<b>§4.D Part 1 — Locke per-leaf missingness, naive vs ?-aware</b>",
                 xaxis_title="", yaxis_title="<b>missingness_score (1.0 = perfect)</b>",
                 height=480, width=1000)
    return fig


# ── Figure 4: Calibration comparison — first post calibrated vs Round Two raw ──

CALIBRATION = [
    {"metric": "Brier", "first_cal": 0.0980, "round_two_raw": 0.0950, "lower_is_better": True, "base_rate": 0.099},
    {"metric": "NLL",   "first_cal": 0.3435, "round_two_raw": 0.3346, "lower_is_better": True, "base_rate": 0.351},
    {"metric": "ECE",   "first_cal": 0.0101, "round_two_raw": 0.0038, "lower_is_better": True, "base_rate": 0.000},
]


def fig_calibration(theme):
    fig = make_subplots(rows=1, cols=3, subplot_titles=[f"<b>{c['metric']}</b>" for c in CALIBRATION],
                        horizontal_spacing=0.12)

    for i, c in enumerate(CALIBRATION):
        col = i + 1
        labels = ["First post<br>(Platt calibrated, 20K)", "Round Two<br>(raw, 101K, n=3)"]
        vals = [c["first_cal"], c["round_two_raw"]]
        colors = [theme["first_post"], theme["primary"]]

        # Bar value labels INSIDE the bars so the base-rate annotation
        # (which lives above the bars near the line) doesn't collide
        # with them. For ECE the bars are tall enough that "inside"
        # reads cleanly; for Brier/NLL the bars are also tall enough
        # because the values are well above zero.
        label_color = "white" if theme["name"] == "cyberpunk" else "white"
        fig.add_trace(go.Bar(
            x=labels, y=vals,
            text=[f"<b>{v:.4f}</b>" for v in vals],
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color=label_color, size=12, family=theme["font_family"]),
            marker=dict(color=colors, line=dict(color=theme["axis"], width=1)),
            showlegend=False,
            hovertemplate="%{x}<br>%{y:.4f}<extra></extra>",
        ), row=1, col=col)

        # Y-axis headroom — generous so the base-rate annotation, the
        # base-rate line, and the bar-top labels all have room above the
        # bars.
        max_v = max(vals + [c["base_rate"]]) * 1.55
        fig.update_yaxes(range=[0, max_v], gridcolor=theme["grid"], linecolor=theme["axis"],
                         row=1, col=col)
        fig.update_xaxes(gridcolor=theme["grid"], linecolor=theme["axis"], row=1, col=col)

        # Base-rate baseline — drawn AFTER the y-axis range is set so the
        # annotation can be parked at the top of the panel, well away
        # from the bar tops and their value labels.
        if c["base_rate"] > 0:
            fig.add_shape(type="line", x0=-0.5, x1=1.5,
                          y0=c["base_rate"], y1=c["base_rate"],
                          line=dict(color=theme["secondary"], width=1.5, dash="dash"),
                          row=1, col=col)
            # Pin the annotation to the top of the panel with a small
            # downward arrow pointing at the base-rate line. Avoids
            # collision with bar-top labels even when bars and base-rate
            # are at nearly the same y.
            fig.add_annotation(x=1.4, y=max_v * 0.95,
                               ax=1.4, ay=c["base_rate"],
                               axref=f"x{col if col > 1 else ''}",
                               ayref=f"y{col if col > 1 else ''}",
                               xref=f"x{col if col > 1 else ''}",
                               yref=f"y{col if col > 1 else ''}",
                               text=f"<b>base rate</b><br>{c['base_rate']:.3f}",
                               showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5,
                               arrowcolor=theme["secondary"],
                               xanchor="center", yanchor="middle",
                               font=dict(color=theme["secondary"], size=10,
                                         family=theme["font_family"]),
                               bgcolor=theme["plot_bg"], borderpad=3, bordercolor=theme["secondary"])

    fig.update_annotations(font=dict(color=theme["text"], size=13))

    fig.update_layout(
        template=theme["template"],
        paper_bgcolor=theme["bg"],
        plot_bgcolor=theme["plot_bg"],
        font=dict(family=theme["font_family"], color=theme["text"], size=theme["tick_size"]),
        title=dict(
            text="<b>Calibration metrics — first post (Platt calibrated) vs Round Two (raw)</b>",
            font=dict(size=theme["title_size"], color=theme["text"]),
            x=0.02, xanchor="left",
        ),
        height=500, width=1080,
        margin=dict(t=70, l=60, r=30, b=80),
        bargap=0.30,
    )
    return fig


# ── Figure 5: MI routing-feature selection at 20K vs 101K ──────────────

MI_ROUTING = {
    "20K trial (§4.A)": {
        "features": ["num_inpatient", "time_in_hospital", "number_diagnoses",
                     "number_emergency", "num_lab_procedures"],
        "selected": [True, True, False, False, False],
        "ranks": [1, 2, 3, 4, 5],  # arbitrary rank — illustrative
    },
    "101K full (§4.E)": {
        "features": ["num_inpatient", "time_in_hospital", "number_diagnoses",
                     "number_emergency", "num_lab_procedures"],
        "selected": [True, False, False, True, False],
        "ranks": [1, 3, 4, 2, 5],
    },
}


def fig_mi_routing(theme):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=[f"<b>{k}</b>" for k in MI_ROUTING.keys()],
                        horizontal_spacing=0.18)

    for i, (label, d) in enumerate(MI_ROUTING.items()):
        col = i + 1
        ranks = d["ranks"]
        # Sort by rank for plot
        order = sorted(range(len(ranks)), key=lambda k: ranks[k])
        feats = [d["features"][k] for k in order]
        sel = [d["selected"][k] for k in order]
        # Show as horizontal bars with rank position
        bar_colors = [theme["primary"] if s else theme["neutral"] for s in sel]
        bar_text = ["<b>SELECTED</b>" if s else "" for s in sel]

        fig.add_trace(go.Bar(
            y=feats, x=list(range(len(feats), 0, -1)),
            text=bar_text, textposition="inside",
            textfont=dict(color=theme["text"], size=11),
            orientation="h",
            marker=dict(color=bar_colors, line=dict(color=theme["axis"], width=1)),
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>MI rank: %{customdata}<extra></extra>",
            customdata=[r for r in sorted(ranks)],
        ), row=1, col=col)

        fig.update_xaxes(title=dict(text="<b>MI rank (higher = better)</b>",
                                    font=dict(size=12, color=theme["text"])),
                         showticklabels=False,
                         gridcolor=theme["grid"], linecolor=theme["axis"],
                         row=1, col=col)
        fig.update_yaxes(gridcolor=theme["grid"], linecolor=theme["axis"],
                         tickfont=dict(family="Courier New, monospace", size=11),
                         row=1, col=col)

    fig.update_annotations(font=dict(color=theme["text"], size=13))

    fig.update_layout(
        template=theme["template"],
        paper_bgcolor=theme["bg"],
        plot_bgcolor=theme["plot_bg"],
        font=dict(family=theme["font_family"], color=theme["text"], size=theme["tick_size"]),
        title=dict(
            text="<b>MI-selected routing features — scale dependence</b>",
            font=dict(size=theme["title_size"], color=theme["text"]),
            x=0.02, xanchor="left",
        ),
        height=420, width=1080,
        margin=dict(t=70, l=20, r=20, b=60),
        bargap=0.25,
        annotations=list(fig.layout.annotations) + [
            dict(text="<i>time_in_hospital wins at 20K → number_emergency wins at 101K</i>",
                 xref="paper", yref="paper", x=0.5, y=-0.18, showarrow=False,
                 font=dict(color=theme["neutral"], size=11)),
        ],
    )
    return fig


# ── Driver ──────────────────────────────────────────────────────────────

THEMES = [TRADITIONAL, CYBERPUNK]

FIGURES = [
    ("auc_trajectory", fig_auc_trajectory),
    ("multi_seed_variance", fig_multi_seed),
    ("per_leaf_belief_question_marks", fig_per_leaf_belief),
    ("calibration_first_vs_round_two", fig_calibration),
    ("mi_routing_scale", fig_mi_routing),
]


def main():
    for theme in THEMES:
        print(f"\n[{theme['name']}]")
        for name, builder in FIGURES:
            fig = builder(theme)
            save_fig(fig, theme, name)
    print("\ndone.")


if __name__ == "__main__":
    main()
