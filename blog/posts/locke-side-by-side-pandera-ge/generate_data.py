"""Synthetic Adult-Income-like dataset with the same quality issues as
the real UCI Adult dataset (https://archive.ics.uci.edu/dataset/2/adult).

We don't ship the real dataset because (a) it would bloat the repo and
(b) the issues we want to demonstrate — '?' sentinels, education / num
redundancy, near-constant capital_gain — are *structural*, not specific
to the exact 32K rows. The synthetic generator below is faithful to the
documented quirks of the real file (see the README of the UCI dataset).

Reproducibility: deterministic via fixed numpy seed. Same input always
yields the same output rows.
"""

import csv
import numpy as np

N = 5_000  # smaller than real Adult for blog readability; quirks are present
SEED = 42

rng = np.random.default_rng(SEED)


def sample(choices, probs, n=N):
    probs = np.asarray(probs, dtype=float)
    probs = probs / probs.sum()  # normalise — the rounded values above
    return rng.choice(choices, size=n, p=probs)


# ── workclass — Private dominates, ~6% '?' as in the real file ─────────
workclass = sample(
    [
        "Private",
        "Self-emp-not-inc",
        "Self-emp-inc",
        "Federal-gov",
        "Local-gov",
        "State-gov",
        "Without-pay",
        "Never-worked",
        "?",
    ],
    [0.696, 0.078, 0.034, 0.030, 0.064, 0.040, 0.0005, 0.0005, 0.057],
)

# ── education / education-num — redundant pair ─────────────────────────
#   education-num is an integer 1..16 mapped 1:1 to the education label.
#   Any model that has both leaks one through the other. The level →
#   income relationship has a strong tail: Doctorate / Prof-school
#   ≳ 70% >50K, Preschool ~0%.
education_levels = [
    ("Preschool", 1),
    ("1st-4th", 2),
    ("5th-6th", 3),
    ("7th-8th", 4),
    ("9th", 5),
    ("10th", 6),
    ("11th", 7),
    ("12th", 8),
    ("HS-grad", 9),
    ("Some-college", 10),
    ("Assoc-voc", 11),
    ("Assoc-acdm", 12),
    ("Bachelors", 13),
    ("Masters", 14),
    ("Prof-school", 15),
    ("Doctorate", 16),
]
edu_probs = np.array([
    0.015,
    0.008,
    0.014,
    0.027,
    0.020,
    0.029,
    0.041,
    0.014,
    0.323,
    0.224,
    0.043,
    0.034,
    0.165,
    0.054,
    0.018,
    0.013,
])
edu_probs = edu_probs / edu_probs.sum()
edu_indices = rng.choice(len(education_levels), size=N, p=edu_probs)
education = np.array([education_levels[i][0] for i in edu_indices])
education_num = np.array([education_levels[i][1] for i in edu_indices])

# ── occupation — also has '?' at the same rate as workclass ─────────────
occupation = sample(
    [
        "Tech-support",
        "Craft-repair",
        "Other-service",
        "Sales",
        "Exec-managerial",
        "Prof-specialty",
        "Handlers-cleaners",
        "Machine-op-inspct",
        "Adm-clerical",
        "Farming-fishing",
        "Transport-moving",
        "Priv-house-serv",
        "Protective-serv",
        "Armed-Forces",
        "?",
    ],
    [
        0.030,
        0.124,
        0.100,
        0.112,
        0.124,
        0.125,
        0.043,
        0.061,
        0.115,
        0.030,
        0.049,
        0.005,
        0.020,
        0.0003,
        0.0617,
    ],
)

# ── native-country — heavily dominated by United-States; '?' present ──
native_country = sample(
    [
        "United-States",
        "Mexico",
        "Philippines",
        "Germany",
        "Canada",
        "Puerto-Rico",
        "India",
        "El-Salvador",
        "China",
        "?",
    ],
    [0.895, 0.020, 0.006, 0.004, 0.004, 0.004, 0.003, 0.003, 0.003, 0.058],
)

# ── age — log-normal-ish around 38, clipped to [17, 90] ─────────────────
age = rng.normal(loc=38, scale=14, size=N).clip(17, 90).astype(np.int64)

# ── fnlwgt — sampling weight, broad range (10k–1.5M in real file) ───────
fnlwgt = rng.integers(13_000, 1_500_000, size=N).astype(np.int64)

# ── capital_gain / capital_loss — ~92% zeros, long sparse tail ──────────
capital_gain = np.where(
    rng.random(N) < 0.92,
    0,
    rng.choice([2174, 3325, 5060, 7298, 7688, 99_999], size=N),
).astype(np.int64)
capital_loss = np.where(
    rng.random(N) < 0.955,
    0,
    rng.choice([1408, 1672, 1887, 1977, 2042, 2174], size=N),
).astype(np.int64)

# ── hours-per-week — centred at 40 with mode at 40 ──────────────────────
hours_per_week = (40 + rng.normal(0, 10, N).round()).clip(1, 99).astype(np.int64)

# ── sex / race / marital-status / relationship — categorical, no '?' ────
sex = sample(["Male", "Female"], [0.668, 0.332])
race = sample(
    ["White", "Black", "Asian-Pac-Islander", "Amer-Indian-Eskimo", "Other"],
    [0.854, 0.096, 0.032, 0.010, 0.008],
)
marital_status = sample(
    [
        "Married-civ-spouse",
        "Never-married",
        "Divorced",
        "Separated",
        "Widowed",
        "Married-spouse-absent",
        "Married-AF-spouse",
    ],
    [0.460, 0.328, 0.136, 0.031, 0.030, 0.013, 0.002],
)
relationship = sample(
    ["Husband", "Not-in-family", "Own-child", "Unmarried", "Wife", "Other-relative"],
    [0.405, 0.255, 0.156, 0.106, 0.048, 0.030],
)

# ── income — the binary target; >50K ≈ 24% (matches real file) ──────────
# Make it loosely correlated with education / hours / age so leakage
# detectors have something to find.
base = 0.05
income_logit = (
    base
    + 0.20 * (education_num >= 13)  # bachelors+ much more likely >50K
    + 0.10 * (education_num >= 11)  # assoc+
    + 0.10 * (hours_per_week >= 40)
    + 0.05 * (age >= 30)
    + 0.30 * (capital_gain > 0)  # any capital gain → almost certainly >50K
)
income_prob = np.clip(income_logit, 0.0, 0.97)
income = np.where(rng.random(N) < income_prob, ">50K", "<=50K")

# ── per-level deterministic leakage that Locke's E9064 should catch ─────
# Anyone with Preschool education is ALWAYS <=50K in the real data and in
# this synthetic — this is a textbook per-level deterministic signature.
income = np.where(education == "Preschool", "<=50K", income)
# And anyone with capital_gain = 99999 (the file's sentinel value) is
# ALWAYS >50K — the second deterministic signature.
income = np.where(capital_gain == 99_999, ">50K", income)


def main():
    columns = [
        ("age", age),
        ("workclass", workclass),
        ("fnlwgt", fnlwgt),
        ("education", education),
        ("education-num", education_num),
        ("marital-status", marital_status),
        ("occupation", occupation),
        ("relationship", relationship),
        ("race", race),
        ("sex", sex),
        ("capital-gain", capital_gain),
        ("capital-loss", capital_loss),
        ("hours-per-week", hours_per_week),
        ("native-country", native_country),
        ("income", income),
    ]
    with open("adult_synth.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in columns])
        for i in range(N):
            w.writerow([c[1][i] for c in columns])
    print(f"wrote adult_synth.csv ({N} rows, {len(columns)} cols)")


if __name__ == "__main__":
    main()
