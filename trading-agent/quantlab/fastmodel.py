"""Fast-model interface. Only a mock exists: Jev's API is unverified (see docs/FEASIBILITY.md)."""
from __future__ import annotations

from typing import Protocol

from .policy import FastModelOutput


class FastModel(Protocol):
    def classify(self, snapshot: dict) -> FastModelOutput: ...


class RuleBaselineModel:
    """Deterministic baseline any learned model must beat. Imbalance + vol rule, no learning."""

    def __init__(self, vol_crisis: float = 0.01, imb_thresh: float = 0.3):
        self.vol_crisis, self.imb_thresh = vol_crisis, imb_thresh

    def classify(self, s: dict) -> FastModelOutput:
        crisis = s["realized_vol"] >= self.vol_crisis
        d = "long" if s["imbalance"] > self.imb_thresh else \
            "short" if s["imbalance"] < -self.imb_thresh else "neutral"
        conf = min(0.99, 0.5 + abs(s["imbalance"]) / 2)
        return FastModelOutput(
            regime="crisis" if crisis else "mean_reverting", direction=d,
            direction_confidence=conf, toxic_flow=s["spread_bps"] > 30,
            setup_quality=3 if abs(s["imbalance"]) > 0.6 else 1 if d != "neutral" else 0,
            risk_state="safe" if s["drawdown"] < 0.05 else "near_limit")
