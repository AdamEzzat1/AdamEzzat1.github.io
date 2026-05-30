"""Run cjc_locke over the synthetic Adult dataset and print the findings
in a human-readable layout. Reproduces the numbers in the blog post.

Requires the cjc-locke Python wheel built from the CJC-Lang workspace:

    cd CJC/python
    pip install maturin numpy pandas
    maturin develop --release
"""

import json
import sys
from pathlib import Path

import pandas as pd

import cjc_locke

# Windows console is cp1252 by default — Locke emits some Unicode
# (≥ etc.) inside finding messages. Force UTF-8 so the printout works.
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]


def main():
    csv_path = Path(__file__).parent / "adult_synth.csv"
    df = pd.read_csv(csv_path)
    print(f"loaded {len(df)} rows × {len(df.columns)} cols")
    print()

    # ── Single-shot validate ────────────────────────────────────────────
    report = cjc_locke.validate(df, label="adult-synth")
    print(f"=== Locke report ===")
    print(f"  n_findings={report.n_findings}  severities={report.severity_counts}")
    print()
    rd = report.to_dict()
    for f in rd["findings"]:
        col = f["column"] if f["column"] else "<dataset>"
        print(f"  [{f['severity'].upper():7s}] {f['code']:6s} {col:18s} {f['message']}")
    print()

    # ── Multi-class leakage E9063 needs a target column ────────────────
    # Encode income as a binary int target (0 = <=50K, 1 = >50K) and
    # extend the report with the leakage detector.
    df_with_target = df.copy()
    df_with_target["income_bin"] = (df_with_target["income"] == ">50K").astype("int64")
    df_with_target = df_with_target.drop(columns=["income"])
    print(f"=== with binary target ===")
    rep2 = cjc_locke.validate(df_with_target, label="adult-target-bin")
    print(f"  n_findings={rep2.n_findings}  severities={rep2.severity_counts}")
    print()
    for f in rep2.to_dict()["findings"]:
        col = f["column"] if f["column"] else "<dataset>"
        print(f"  [{f['severity'].upper():7s}] {f['code']:6s} {col:18s} {f['message']}")
    print()

    # ── Belief report ──────────────────────────────────────────────────
    belief = cjc_locke.belief_report(report)
    print(f"=== belief score ===")
    sd = belief.score_dict()
    for axis, val in sd.items():
        print(f"  {axis:14s} {val:.4f}")
    print()

    # ── Determinism canary ─────────────────────────────────────────────
    json1 = report.to_json()
    json2 = cjc_locke.validate(df, label="adult-synth").to_json()
    print(f"=== determinism ===")
    print(f"  JSON bytes identical across runs: {json1 == json2}")
    print(f"  report run_id: {rd['run_id']}")
    print()

    # ── Train / test drift demo ────────────────────────────────────────
    # Split deterministically: first 70% train, last 30% test
    n_train = int(0.7 * len(df))
    train_df = df.iloc[:n_train]
    test_df = df.iloc[n_train:]
    val, drift, drift_belief = cjc_locke.validate_and_compare(
        train_df, test_df, label="train-vs-test"
    )
    print(f"=== train/test drift ===")
    print(f"  drift findings: {drift.finding_codes()}")
    print(f"  belief overall: {drift_belief.overall:.4f}")
    print(f"  belief drift  : {drift_belief.drift_score:.4f}")
    print()


if __name__ == "__main__":
    main()
