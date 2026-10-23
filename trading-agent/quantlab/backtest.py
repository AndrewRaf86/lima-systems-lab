"""Minimal cost-aware walk-forward harness and a verdict that can say 'no trade'."""
from __future__ import annotations

import math


def metrics(rets: list[float], periods_per_year: int = 252) -> dict:
    n = len(rets)
    if n < 2:
        return {"n": n, "ann_return": 0.0, "sharpe": 0.0, "max_dd": 0.0}
    mean = sum(rets) / n
    sd = math.sqrt(sum((r - mean) ** 2 for r in rets) / (n - 1))
    eq, peak, mdd = 1.0, 1.0, 0.0
    for r in rets:
        eq *= 1 + r
        peak = max(peak, eq)
        mdd = max(mdd, (peak - eq) / peak)
    return {"n": n, "ann_return": (eq ** (periods_per_year / n) - 1),
            "sharpe": (mean / sd * math.sqrt(periods_per_year)) if sd > 0 else 0.0,
            "max_dd": mdd}


def momentum_returns(prices: list[float], lookback: int, cost_bps: float) -> list[float]:
    """Long when trailing return > 0, else cash. Signal at t-1 close, earned over t (no look-ahead)."""
    out, pos = [], 0
    for t in range(lookback + 1, len(prices)):
        new = 1 if prices[t - 1] / prices[t - 1 - lookback] - 1 > 0 else 0
        r = prices[t] / prices[t - 1] - 1
        cost = abs(new - pos) * cost_bps / 1e4
        out.append(new * r - cost)
        pos = new
    return out


def walk_forward(prices: list[float], lookbacks: list[int], train: int, test: int,
                 cost_bps: float) -> list[float]:
    """Pick lookback by train Sharpe, apply to the next unseen window. Returns stitched OOS returns."""
    oos, start = [], 0
    while start + train + test <= len(prices):
        tr = prices[start:start + train]
        best = max(lookbacks, key=lambda lb: metrics(momentum_returns(tr, lb, cost_bps))["sharpe"])
        seg = prices[start + train - best - 1:start + train + test]  # warmup uses only past data
        oos += momentum_returns(seg, best, cost_bps)[-test:]
        start += test
    return oos


def verdict(strategy: list[float], benchmark: list[float], min_n: int = 500,
            min_sharpe_edge: float = 0.3) -> str:
    """Conservative gate. Passing it is necessary, not sufficient, for paper trading."""
    s, b = metrics(strategy), metrics(benchmark)
    if s["n"] < min_n:
        return f"NO TRADE JUSTIFIED: sample too small ({s['n']} < {min_n})"
    if s["sharpe"] < b["sharpe"] + min_sharpe_edge:
        return "NO TRADE JUSTIFIED: does not beat benchmark Sharpe by required margin"
    if s["max_dd"] > b["max_dd"]:
        return "NO TRADE JUSTIFIED: deeper drawdown than benchmark"
    return "CANDIDATE: proceed to independent review and paper trading only"
