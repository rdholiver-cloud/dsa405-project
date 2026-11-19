#!/usr/bin/env python3
"""Rebuild the P4 headline findings and two figures with no download.

This path needs only files committed to the repo:

  data/processed/backtest_full.csv            the 356-month headline backtest
  data/processed/flagged_monthly_returns.csv  the 21 flagged ticker-months
  results/findings.csv                        the recorded findings to check against

It recomputes the headline growth, CAGR, beat share and volatility, both
bootstraps (same seed and draws as the notebook), the three subperiods and the
held-jump check, compares every one of them to results/findings.csv at the
12 significant digits the file stores, and writes the baseline and subperiod
figures to figures/offline/. It exits with status 1 if any value differs.

The three sensitivity paths (21 jumps removed, capped, CHRD only) and the input
counts need the full monthly price panel, which is rebuilt from the Yahoo cache
by the notebook. This script does not recompute them. It reads them from
results/findings.csv and checks that they are internally consistent.

Usage (from the repo root):

    python scripts/reproduce_offline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
OUT_FIGURES = ROOT / "figures" / "offline"

BOOTSTRAP_SEED = 4052026
BOOTSTRAP_REPS = 2000
SUBPERIODS = [
    ("1997-02_to_2006-12", "1997-02", "2006-12"),
    ("2007-01_to_2016-12", "2007-01", "2016-12"),
    ("2017-01_to_2026-09", "2017-01", "2026-09"),
]
SENSITIVITY = ("exclude_flagged", "cap_300", "exclude_chrd_2020_11")


def summarize(strat: pd.Series, spy: pd.Series, earned: pd.Series) -> dict:
    # Same formulas as run_backtest and subperiod_stats in the P4 notebook.
    years = len(strat) / 12
    strat_g = (1 + strat).cumprod()
    spy_g = (1 + spy).cumprod()
    return {
        "n_months": int(len(strat)),
        "first_month": str(earned.iloc[0]),
        "last_month": str(earned.iloc[-1]),
        "final_wealth_strategy": float(strat_g.iloc[-1]),
        "final_wealth_spy": float(spy_g.iloc[-1]),
        "cagr_strategy": float(strat_g.iloc[-1] ** (1 / years) - 1),
        "cagr_spy": float(spy_g.iloc[-1] ** (1 / years) - 1),
        "share_months_strategy_beats_spy": float((strat > spy).mean()),
        "ann_vol_strategy": float(strat.std(ddof=1) * np.sqrt(12)),
        "ann_vol_spy": float(spy.std(ddof=1) * np.sqrt(12)),
    }


def bootstrap(strat: np.ndarray, spy: np.ndarray) -> dict:
    # Independent-month bootstrap, same seed and draw order as bootstrap_cagr in the notebook.
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(strat)
    years = n / 12
    recs = []
    for _ in range(BOOTSTRAP_REPS):
        idx = rng.integers(0, n, size=n)
        ws = float(np.prod(1 + strat[idx]))
        wp = float(np.prod(1 + spy[idx]))
        recs.append((ws, wp, ws ** (1 / years) - 1, wp ** (1 / years) - 1))
    arr = np.array(recs, dtype=float)
    out = {}
    for i, lab in enumerate(("final_wealth_strategy", "final_wealth_spy", "cagr_strategy", "cagr_spy")):
        out[f"{lab}_p05"] = float(np.percentile(arr[:, i], 5))
        out[f"{lab}_p95"] = float(np.percentile(arr[:, i], 95))
    return out


def paired_gap(strat: np.ndarray, spy: np.ndarray) -> dict:
    # Paired bootstrap of the CAGR gap, same seed and draw order as the notebook.
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(strat)
    years = n / 12
    gaps = np.empty(BOOTSTRAP_REPS)
    for k in range(BOOTSTRAP_REPS):
        idx = rng.integers(0, n, size=n)
        gaps[k] = np.prod(1 + strat[idx]) ** (1 / years) - np.prod(1 + spy[idx]) ** (1 / years)
    return {
        "cagr_gap_paired_bootstrap_p05": float(np.percentile(gaps, 5)),
        "cagr_gap_paired_bootstrap_p95": float(np.percentile(gaps, 95)),
        "cagr_gap_share_resamples_positive": float((gaps > 0).mean()),
    }


def stored(value) -> str:
    # The notebook writes floats with 12 significant digits.
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.12g}"
    return str(value)


def month_end_stamps(months: pd.Series) -> pd.DatetimeIndex:
    # Plot at the month the return is earned (pick month + 1), as the notebook does.
    return pd.PeriodIndex(months, freq="M").to_timestamp(how="end") + pd.offsets.MonthBegin(1)


def main() -> int:
    bt = pd.read_csv(PROCESSED / "backtest_full.csv")
    bt["month"] = pd.PeriodIndex(bt["month"], freq="M")
    flagged = pd.read_csv(PROCESSED / "flagged_monthly_returns.csv")
    flagged["month"] = pd.PeriodIndex(flagged["month"], freq="M")
    findings = pd.read_csv(RESULTS / "findings.csv", dtype=str)
    recorded = {(r.metric, r.scenario): r.value for r in findings.itertuples()}

    earned = bt["month"] + 1
    computed: dict[tuple[str, str], object] = {}

    for k, v in summarize(bt["strategy_ret"], bt["spy_ret"], earned).items():
        computed[(k, "baseline")] = v

    strat = bt["strategy_ret"].to_numpy()
    spy = bt["spy_ret"].to_numpy()
    for k, v in bootstrap(strat, spy).items():
        computed[(k, "bootstrap_baseline")] = v
    for k, v in paired_gap(strat, spy).items():
        computed[(k, "bootstrap_baseline")] = v

    sub_stats = {}
    for name, start, end in SUBPERIODS:
        keep = (earned >= pd.Period(start, "M")) & (earned <= pd.Period(end, "M"))
        part = bt.loc[keep]
        s = summarize(part["strategy_ret"], part["spy_ret"], earned.loc[keep])
        sub_stats[name] = s
        for k in ("n_months", "final_wealth_strategy", "final_wealth_spy", "cagr_strategy", "cagr_spy",
                  "share_months_strategy_beats_spy", "ann_vol_strategy", "ann_vol_spy"):
            computed[(k, f"subperiod_{name}")] = s[k]

    picks_by_month = dict(zip(bt["month"], bt["picks"].str.split(",")))
    held = sum(r.ticker in picks_by_month.get(r.month - 1, []) for r in flagged.itertuples())
    computed[("n_flagged_jumps_held_in_portfolio", "inputs")] = int(held)
    computed[("n_flagged_monthly_returns", "inputs")] = int(len(flagged))

    mismatches = []
    for key, value in computed.items():
        want = recorded.get(key)
        got = stored(value)
        if want != got:
            mismatches.append((key, want, got))
    print(f"recomputed from committed tables: {len(computed)} findings values")
    print(f"matching results/findings.csv exactly: {len(computed) - len(mismatches)} of {len(computed)}")
    for (metric, scenario), want, got in mismatches:
        print(f"  MISMATCH {metric} [{scenario}]: findings.csv {want}, recomputed {got}")

    # Sensitivity rows need the price panel, so they are checked for consistency only.
    consistency = []
    for scen in SENSITIVITY:
        for k in ("n_months", "final_wealth_spy", "cagr_spy", "ann_vol_spy"):
            if recorded.get((k, scen)) != recorded.get((k, "baseline")):
                consistency.append(f"{k} [{scen}] differs from baseline")
    if recorded.get(("final_wealth_strategy", "exclude_chrd_2020_11")) != recorded.get(
            ("final_wealth_strategy", "baseline")):
        consistency.append("CHRD-only removal changes the headline, but CHRD was not held")
    n_sens = sum(1 for (_, s) in recorded if s in SENSITIVITY)
    print(f"sensitivity rows read from findings.csv (need the Yahoo cache to recompute): {n_sens}")
    print(f"sensitivity consistency checks failed: {len(consistency)}")
    for msg in consistency:
        print("  " + msg)

    OUT_FIGURES.mkdir(parents=True, exist_ok=True)
    base = computed
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    t = month_end_stamps(bt["month"])
    ax.plot(t, bt["strategy_growth"], color="#1f4e79", lw=1.8, label="Momentum rule (baseline)")
    ax.plot(t, bt["spy_growth"], color="#7a7a7a", lw=1.8, label="SPY buy-and-hold")
    ax.set_yscale("log")
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_xlabel("Month the return is earned")
    ax.set_title("Headline backtest, flagged returns kept")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    fig.tight_layout()
    growth_path = OUT_FIGURES / "growth_baseline.png"
    fig.savefig(growth_path, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    labels, strat_vals, spy_vals = [], [], []
    for name, _, _ in SUBPERIODS:
        s = sub_stats[name]
        labels.append(f"{s['first_month']} to {s['last_month']}")
        strat_vals.append(s["cagr_strategy"] * 100)
        spy_vals.append(s["cagr_spy"] * 100)
    labels.append(f"Full sample\n{base[('first_month', 'baseline')]} to {base[('last_month', 'baseline')]}")
    strat_vals.append(base[("cagr_strategy", "baseline")] * 100)
    spy_vals.append(base[("cagr_spy", "baseline")] * 100)
    x = np.arange(len(labels))
    w = 0.36
    ax.bar(x - w / 2, strat_vals, width=w, color="#1f4e79", label="Momentum rule (baseline)")
    ax.bar(x + w / 2, spy_vals, width=w, color="#9a9a9a", label="SPY buy-and-hold")
    ax.set_xticks(x, labels)
    ax.set_ylabel("CAGR (percent per year)")
    ax.set_title("Subperiod compound annual growth rates, baseline path")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(True, axis="y", ls=":", alpha=0.5)
    fig.tight_layout()
    sub_path = OUT_FIGURES / "subperiod_cagr.png"
    fig.savefig(sub_path, dpi=150)
    plt.close(fig)
    print("wrote", growth_path.relative_to(ROOT))
    print("wrote", sub_path.relative_to(ROOT))

    print(f"headline: $1 -> ${base[('final_wealth_strategy', 'baseline')]:,.2f} for the rule "
          f"({base[('cagr_strategy', 'baseline')]:.1%} a year) vs ${base[('final_wealth_spy', 'baseline')]:,.2f} "
          f"for SPY ({base[('cagr_spy', 'baseline')]:.1%} a year) over {base[('n_months', 'baseline')]} months")
    if mismatches or consistency:
        print("OFFLINE CHECK FAILED")
        return 1
    print("OFFLINE CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
