"""Deterministic risk engine. No model output can change a limit or the kill switch."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RiskLimits:
    """Initial research parameters, not validated safety bounds."""
    max_position_frac: float = 0.10     # of equity, per symbol
    max_gross_exposure: float = 1.00    # no leverage
    max_daily_loss: float = 0.02
    max_weekly_loss: float = 0.05
    max_drawdown: float = 0.15
    max_orders_per_min: int = 10
    max_data_age_s: float = 5.0
    max_spread_bps: float = 30.0
    max_order_frac_of_adv: float = 0.01  # liquidity cap, needs average daily volume


@dataclass(frozen=True)
class Quote:
    bid: float
    ask: float
    ts: float  # epoch seconds, source timestamp

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread_bps(self) -> float:
        return (self.ask - self.bid) / self.mid * 1e4


@dataclass(frozen=True)
class Order:
    client_id: str
    symbol: str
    side: str            # "buy" | "sell"
    qty: float
    asset_class: str     # "equity" | "crypto"
    order_type: str = "limit"
    limit_price: float | None = None


@dataclass
class Portfolio:
    equity: float
    peak_equity: float
    day_start_equity: float
    week_start_equity: float
    positions: dict[str, float] = field(default_factory=dict)  # signed qty
    prices: dict[str, float] = field(default_factory=dict)

    def gross_exposure(self) -> float:
        return sum(abs(q) * self.prices.get(s, 0.0) for s, q in self.positions.items())


@dataclass(frozen=True)
class Decision:
    approved: bool
    reasons: tuple[str, ...] = ()


class RiskEngine:
    def __init__(self, limits: RiskLimits | None = None):
        self.limits = limits or RiskLimits()
        self.kill_switch_tripped = False
        self.kill_reason = ""
        self._order_times: list[float] = []

    def trip(self, reason: str) -> None:
        self.kill_switch_tripped = True
        self.kill_reason = reason

    def reset(self) -> None:
        """Operator-only. Never called by agent or model code."""
        self.kill_switch_tripped = False
        self.kill_reason = ""

    def check(self, order: Order, pf: Portfolio, quote: Quote, now: float,
              adv_units: float | None = None) -> Decision:
        L = self.limits
        no: list[str] = []
        px = pf.prices.get(order.symbol, quote.mid)
        cur = pf.positions.get(order.symbol, 0.0)
        signed = order.qty if order.side == "buy" else -order.qty
        new = cur + signed
        reducing = abs(new) < abs(cur)

        if order.qty <= 0:
            no.append("non-positive quantity")
        # drawdown / loss limits latch the kill switch
        if pf.peak_equity > 0 and (pf.peak_equity - pf.equity) / pf.peak_equity >= L.max_drawdown:
            self.trip("max drawdown breached")
        if pf.day_start_equity > 0 and (pf.day_start_equity - pf.equity) / pf.day_start_equity >= L.max_daily_loss:
            self.trip("daily loss limit breached")
        if pf.week_start_equity > 0 and (pf.week_start_equity - pf.equity) / pf.week_start_equity >= L.max_weekly_loss:
            self.trip("weekly loss limit breached")
        if self.kill_switch_tripped and not reducing:
            no.append(f"kill switch: {self.kill_reason}")

        if now - quote.ts > L.max_data_age_s:
            no.append("stale quote")
        if quote.ts > now:
            no.append("quote timestamp in the future")
        if quote.spread_bps > L.max_spread_bps and not reducing:
            no.append("spread too wide")

        self._order_times = [t for t in self._order_times if now - t < 60]
        if len(self._order_times) >= L.max_orders_per_min:
            no.append("order frequency limit")

        if not reducing:
            if abs(new) * px > L.max_position_frac * pf.equity:
                no.append("position limit")
            added = (abs(new) - abs(cur)) * px
            if pf.gross_exposure() + added > L.max_gross_exposure * pf.equity:
                no.append("gross exposure / leverage limit")
            if adv_units is not None and order.qty > L.max_order_frac_of_adv * adv_units:
                no.append("order exceeds liquidity cap")
            if order.side == "sell" and new < 0:
                no.append("short selling disabled")

        if not no:
            self._order_times.append(now)
        return Decision(not no, tuple(no))
