"""Broker-independent execution interface plus a paper broker. No real-money adapter exists."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol
from zoneinfo import ZoneInfo

from .risk import Decision, Order, Portfolio, Quote, RiskEngine

NY = ZoneInfo("America/New_York")


def market_open(asset_class: str, ts: float, extended: bool = False) -> bool:
    """Crypto 24/7. Equities: weekdays 09:30-16:00 ET. Ignores exchange holidays/half days (TODO)."""
    if asset_class == "crypto":
        return True
    dt = datetime.fromtimestamp(ts, NY)
    if dt.weekday() >= 5:
        return False
    start, end = (time(4, 0), time(20, 0)) if extended else (time(9, 30), time(16, 0))
    return start <= dt.time() < end


@dataclass(frozen=True)
class Fill:
    client_id: str
    qty: float
    price: float
    fee: float


@dataclass
class OrderResult:
    client_id: str
    status: str   # filled | partial | rejected | duplicate | resting
    fills: tuple[Fill, ...] = ()
    reasons: tuple[str, ...] = ()


class Broker(Protocol):
    def submit(self, order: Order, quote: Quote) -> OrderResult: ...
    def cancel(self, client_id: str) -> bool: ...


class PaperBroker:
    """Fills against the quote with spread crossing, slippage, fees, and a partial-fill cap."""

    def __init__(self, fee_bps: float = 5.0, slippage_bps: float = 2.0, max_fill_qty: float | None = None):
        self.fee_bps, self.slippage_bps, self.max_fill_qty = fee_bps, slippage_bps, max_fill_qty
        self.resting: dict[str, Order] = {}

    def submit(self, order: Order, quote: Quote) -> OrderResult:
        buy = order.side == "buy"
        touch = quote.ask if buy else quote.bid
        if order.order_type == "limit" and order.limit_price is not None:
            if (buy and order.limit_price < touch) or (not buy and order.limit_price > touch):
                self.resting[order.client_id] = order
                return OrderResult(order.client_id, "resting")
        slip = touch * self.slippage_bps / 1e4
        px = touch + slip if buy else touch - slip
        qty = order.qty if self.max_fill_qty is None else min(order.qty, self.max_fill_qty)
        fee = qty * px * self.fee_bps / 1e4
        status = "filled" if qty == order.qty else "partial"
        return OrderResult(order.client_id, status, (Fill(order.client_id, qty, px, fee),))

    def cancel(self, client_id: str) -> bool:
        return self.resting.pop(client_id, None) is not None


class ExecutionEngine:
    """Order path: duplicate check -> market hours -> risk engine -> broker."""

    def __init__(self, broker: Broker, risk: RiskEngine):
        self.broker, self.risk = broker, risk
        self._seen: dict[str, OrderResult] = {}

    def submit(self, order: Order, pf: Portfolio, quote: Quote, now: float,
               adv_units: float | None = None) -> OrderResult:
        if order.client_id in self._seen:
            return OrderResult(order.client_id, "duplicate")
        if not market_open(order.asset_class, now):
            res = OrderResult(order.client_id, "rejected", reasons=("market closed",))
        else:
            d: Decision = self.risk.check(order, pf, quote, now, adv_units)
            res = self.broker.submit(order, quote) if d.approved else \
                OrderResult(order.client_id, "rejected", reasons=d.reasons)
        self._seen[order.client_id] = res
        return res
