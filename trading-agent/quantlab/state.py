"""Deterministic snapshot builder with causal timestamps. All numbers computed in code."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class BookSnap:
    ts: float
    bids: tuple[tuple[float, float], ...]  # (price, size), best first
    asks: tuple[tuple[float, float], ...]


class LookAheadError(ValueError):
    pass


def build_snapshot(history: list[BookSnap], asof: float, inventory: float,
                   equity: float, peak_equity: float, depth: int = 5,
                   vol_window: int = 50, max_age_s: float = 5.0) -> dict:
    """Use only snapshots with ts <= asof. Raises if data is stale or empty."""
    past = [b for b in history if b.ts <= asof]
    if not past:
        raise LookAheadError("no data at or before asof")
    last = past[-1]
    if asof - last.ts > max_age_s:
        raise LookAheadError("latest book is stale")
    bb, ba = last.bids[0][0], last.asks[0][0]
    mid = (bb + ba) / 2
    bid_sz = sum(s for _, s in last.bids[:depth])
    ask_sz = sum(s for _, s in last.asks[:depth])
    imbalance = (bid_sz - ask_sz) / (bid_sz + ask_sz) if bid_sz + ask_sz else 0.0
    mids = [(b.bids[0][0] + b.asks[0][0]) / 2 for b in past[-(vol_window + 1):]]
    rets = [math.log(b / a) for a, b in zip(mids, mids[1:]) if a > 0 and b > 0]
    if len(rets) > 1:
        m = sum(rets) / len(rets)
        rv = math.sqrt(sum((r - m) ** 2 for r in rets) / (len(rets) - 1))
    else:
        rv = 0.0
    dd = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0.0
    return {
        "asof": asof, "book_ts": last.ts, "age_s": round(asof - last.ts, 3),
        "mid": round(mid, 6), "spread_bps": round((ba - bb) / mid * 1e4, 3),
        "imbalance": round(imbalance, 4), "realized_vol": round(rv, 8),
        "inventory": inventory, "drawdown": round(dd, 4), "n_obs": len(rets),
    }


def approx_tokens(snapshot: dict) -> int:
    return len(str(snapshot)) // 3  # conservative: ~3 chars/token for numeric text
