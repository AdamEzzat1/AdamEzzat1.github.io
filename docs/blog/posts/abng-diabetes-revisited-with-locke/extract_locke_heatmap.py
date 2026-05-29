"""Extract Locke's actual Pearson heatmap SVG from the audit HTML.

Produces two artifacts under figures/locke/:
  - pearson_heatmap_actual.svg : wrapped + titled, ready to embed at scale
  - pearson_heatmap_raw.svg    : the unmodified fragment from the audit
"""

from pathlib import Path

SRC = Path(r"C:\Users\adame\CJC\.claude\worktrees\adoring-shtern-01c720\bench_results\diabetes_phase_0_10_section_4b\diabetes_locke_baseline.html")
OUT_DIR = Path(__file__).parent / "figures" / "locke"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    html = SRC.read_text(encoding="utf-8")
    i = html.find("<svg ")
    j = html.find("</svg>", i) + len("</svg>")
    svg_body = html[i:j]

    # Raw — exactly what Locke emitted.
    raw_path = OUT_DIR / "pearson_heatmap_raw.svg"
    raw_path.write_text(svg_body, encoding="utf-8")
    print(f"saved {raw_path.name} ({len(svg_body):,} bytes)")

    # Wrapped — with a title bar and a larger viewBox so it renders crisp
    # at blog widths.
    inner = svg_body
    inner = inner.replace(
        '<svg xmlns="http://www.w3.org/2000/svg" width="252" height="252"',
        '<svg width="252" height="252"',
    )
    # If the inner string is still a full <svg> block, strip the outer
    # <svg> wrapper so we can nest it inside our title bar.
    if inner.startswith("<svg"):
        # Move past the opening tag.
        first_close = inner.find(">") + 1
        inner_body = inner[first_close:].rstrip()
        if inner_body.endswith("</svg>"):
            inner_body = inner_body[: -len("</svg>")]
    else:
        inner_body = inner

    wrapped = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 290 305" '
        'width="580" height="610" '
        'style="font-family: \'Helvetica Neue\', Arial, sans-serif; '
        'background: #ffffff;">\n'
        '  <rect x="0" y="0" width="290" height="305" fill="#ffffff"/>\n'
        '  <text x="12" y="22" font-size="13" font-weight="bold" fill="#1a1a1a">'
        'Locke audit — Pearson |r| heatmap (6 numeric cols)</text>\n'
        '  <text x="12" y="38" font-size="10" fill="#666666">'
        'Inline SVG, extracted from the actual `cjcl locke validate` HTML report. '
        'Deterministic, content-addressed.</text>\n'
        f'  <g transform="translate(12, 40)">\n{inner_body}\n  </g>\n'
        '</svg>\n'
    )
    wrap_path = OUT_DIR / "pearson_heatmap_actual.svg"
    wrap_path.write_text(wrapped, encoding="utf-8")
    print(f"saved {wrap_path.name} ({len(wrapped):,} bytes)")


if __name__ == "__main__":
    main()
