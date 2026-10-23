"""Typed fast-model output and the code-owned gate. The model only classifies."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

REGIMES = {"trending", "mean_reverting", "high_vol", "crisis"}
DIRECTIONS = {"long", "short", "neutral"}
RISK_STATES = {"safe", "near_limit", "reduce"}


@dataclass(frozen=True)
class FastModelOutput:
    regime: str
    direction: str
    direction_confidence: float
    toxic_flow: bool
    setup_quality: int      # 0..3
    risk_state: str

    def __post_init__(self):
        if self.regime not in REGIMES or self.direction not in DIRECTIONS \
                or self.risk_state not in RISK_STATES:
            raise ValueError("untyped model output rejected")
        if not 0.0 <= self.direction_confidence <= 1.0 or not 0 <= self.setup_quality <= 3:
            raise ValueError("model output out of range")


class Action(Enum):
    HOLD = "hold"
    TRADE = "trade"
    ESCALATE = "escalate"   # deeper re-read by the reasoning model; still not an order


@dataclass(frozen=True)
class Gate:
    min_setup_quality: int = 2
    min_confidence: float = 0.80
    escalate_below: float = 0.60


def decide(out: FastModelOutput, gate: Gate = Gate()) -> tuple[Action, str]:
    if out.regime == "crisis":
        return Action.ESCALATE, "crisis regime"
    if out.direction_confidence < gate.escalate_below:
        return Action.ESCALATE, "low confidence"
    if out.toxic_flow:
        return Action.HOLD, "toxic flow"
    if out.direction == "neutral":
        return Action.HOLD, "neutral"
    if out.setup_quality < gate.min_setup_quality:
        return Action.HOLD, "setup quality below gate"
    if out.direction_confidence <= gate.min_confidence:
        return Action.HOLD, "confidence below gate"
    if out.risk_state != "safe":
        return Action.HOLD, f"risk_state={out.risk_state}"
    return Action.TRADE, "gate passed"
