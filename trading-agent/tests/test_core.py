import random
import unittest
from datetime import datetime

from quantlab import backtest, calibration, sizing
from quantlab.execution import ExecutionEngine, PaperBroker, market_open, NY
from quantlab.fastmodel import RuleBaselineModel
from quantlab.policy import Action, FastModelOutput, decide
from quantlab.risk import Order, Portfolio, Quote, RiskEngine
from quantlab.state import BookSnap, LookAheadError, approx_tokens, build_snapshot

NOW = datetime(2026, 10, 21, 11, 0, tzinfo=NY).timestamp()  # Wednesday, in session


def pf(**kw):
    d = dict(equity=100_000, peak_equity=100_000, day_start_equity=100_000,
             week_start_equity=100_000, positions={}, prices={"AAA": 100.0})
    d.update(kw)
    return Portfolio(**d)


def q(ts=NOW, bid=99.99, ask=100.01):
    return Quote(bid, ask, ts)


def buy(cid="1", qty=50, sym="AAA", cls="equity"):
    return Order(cid, sym, "buy", qty, cls, "limit", 100.05)


class RiskTests(unittest.TestCase):
    def test_approves_small_order(self):
        self.assertTrue(RiskEngine().check(buy(), pf(), q(), NOW).approved)

    def test_position_limit(self):
        d = RiskEngine().check(buy(qty=200), pf(), q(), NOW)  # $20k > 10% of 100k
        self.assertIn("position limit", d.reasons)

    def test_stale_and_future_quotes(self):
        self.assertIn("stale quote", RiskEngine().check(buy(), pf(), q(ts=NOW - 60), NOW).reasons)
        self.assertIn("quote timestamp in the future", RiskEngine().check(buy(), pf(), q(ts=NOW + 5), NOW).reasons)

    def test_short_selling_disabled(self):
        o = Order("s", "AAA", "sell", 10, "equity", "limit", 99.0)
        self.assertIn("short selling disabled", RiskEngine().check(o, pf(), q(), NOW).reasons)

    def test_kill_switch_latches_and_allows_reduce(self):
        r = RiskEngine()
        hurt = pf(equity=84_000, positions={"AAA": 50})
        self.assertFalse(r.check(buy(), hurt, q(), NOW).approved)
        self.assertTrue(r.kill_switch_tripped)
        # latched even after equity recovers
        self.assertFalse(r.check(buy("2"), pf(), q(), NOW).approved)
        sell = Order("3", "AAA", "sell", 10, "equity", "limit", 99.0)
        self.assertTrue(r.check(sell, hurt, q(), NOW).approved)  # reducing is allowed
        r.reset()
        self.assertTrue(r.check(buy("4"), pf(), q(), NOW).approved)

    def test_daily_loss_trips(self):
        r = RiskEngine()
        self.assertFalse(r.check(buy(), pf(equity=97_000, peak_equity=100_000), q(), NOW).approved)

    def test_order_frequency(self):
        r = RiskEngine()
        res = [r.check(buy(str(i), qty=1), pf(), q(), NOW + i * 0.1).approved for i in range(12)]
        self.assertEqual(res.count(True), 10)

    def test_liquidity_cap(self):
        d = RiskEngine().check(buy(qty=50), pf(), q(), NOW, adv_units=1000)  # 5% of ADV
        self.assertIn("order exceeds liquidity cap", d.reasons)


class SizingPolicyTests(unittest.TestCase):
    def test_kelly_zero_when_no_edge(self):
        self.assertEqual(sizing.kelly_fraction(0.5, 1.0), 0.0)
        self.assertEqual(sizing.position_fraction(0.4, 1.0), 0.0)

    def test_quarter_kelly_and_cap(self):
        self.assertAlmostEqual(sizing.position_fraction(0.6, 1.0, cap=1.0), 0.25 * 0.2)
        self.assertEqual(sizing.position_fraction(0.99, 5.0), 0.10)

    def _o(self, **kw):
        d = dict(regime="trending", direction="long", direction_confidence=0.9,
                 toxic_flow=False, setup_quality=3, risk_state="safe")
        d.update(kw)
        return FastModelOutput(**d)

    def test_gate(self):
        self.assertEqual(decide(self._o())[0], Action.TRADE)
        self.assertEqual(decide(self._o(setup_quality=1))[0], Action.HOLD)
        self.assertEqual(decide(self._o(direction_confidence=0.80))[0], Action.HOLD)  # strictly above
        self.assertEqual(decide(self._o(risk_state="near_limit"))[0], Action.HOLD)
        self.assertEqual(decide(self._o(toxic_flow=True))[0], Action.HOLD)
        self.assertEqual(decide(self._o(direction_confidence=0.55))[0], Action.ESCALATE)
        self.assertEqual(decide(self._o(regime="crisis"))[0], Action.ESCALATE)

    def test_untyped_output_rejected(self):
        with self.assertRaises(ValueError):
            self._o(regime="moon")


class StateTests(unittest.TestCase):
    def _hist(self, n=60, t0=1000.0):
        return [BookSnap(t0 + i, ((100 + i * 0.01, 5.0),), ((100.02 + i * 0.01, 3.0),)) for i in range(n)]

    def test_no_future_leak(self):
        h = self._hist()
        a = build_snapshot(h[:30], 1029.0, 0, 1e5, 1e5)
        b = build_snapshot(h, 1029.0, 0, 1e5, 1e5)  # same asof, extra future rows present
        self.assertEqual(a, b)

    def test_stale_and_empty_rejected(self):
        with self.assertRaises(LookAheadError):
            build_snapshot(self._hist(), 999.0, 0, 1e5, 1e5)
        with self.assertRaises(LookAheadError):
            build_snapshot(self._hist(), 1100.0, 0, 1e5, 1e5)

    def test_size_and_values(self):
        s = build_snapshot(self._hist(), 1059.0, 2.0, 99_000, 100_000)
        self.assertLess(approx_tokens(s), 400)
        self.assertAlmostEqual(s["drawdown"], 0.01)
        self.assertGreater(s["imbalance"], 0)
        RuleBaselineModel().classify(s)


class ExecutionTests(unittest.TestCase):
    def test_duplicate_prevention(self):
        e = ExecutionEngine(PaperBroker(), RiskEngine())
        self.assertEqual(e.submit(buy("x"), pf(), q(), NOW).status, "filled")
        self.assertEqual(e.submit(buy("x"), pf(), q(), NOW).status, "duplicate")

    def test_market_closed_equity_but_not_crypto(self):
        sat = datetime(2026, 10, 24, 11, 0, tzinfo=NY).timestamp()
        self.assertFalse(market_open("equity", sat))
        self.assertTrue(market_open("crypto", sat))
        e = ExecutionEngine(PaperBroker(), RiskEngine())
        r = e.submit(buy("c"), pf(), q(ts=sat), sat)
        self.assertEqual((r.status, r.reasons), ("rejected", ("market closed",)))

    def test_partial_fill_and_costs(self):
        b = PaperBroker(max_fill_qty=20)
        r = b.submit(buy(qty=50), q())
        self.assertEqual(r.status, "partial")
        f = r.fills[0]
        self.assertGreater(f.price, 100.01)  # paid spread + slippage
        self.assertGreater(f.fee, 0)

    def test_resting_limit_then_cancel(self):
        b = PaperBroker()
        o = Order("r", "AAA", "buy", 10, "equity", "limit", 90.0)
        self.assertEqual(b.submit(o, q()).status, "resting")
        self.assertTrue(b.cancel("r"))
        self.assertFalse(b.cancel("r"))

    def test_risk_rejection_reaches_result(self):
        e = ExecutionEngine(PaperBroker(), RiskEngine())
        r = e.submit(buy("big", qty=500), pf(), q(), NOW)
        self.assertEqual(r.status, "rejected")


class ResearchTests(unittest.TestCase):
    def test_brier(self):
        self.assertEqual(calibration.brier_score([1.0, 0.0], [1, 0]), 0.0)
        self.assertEqual(calibration.brier_score([0.5, 0.5], [1, 0]), 0.25)

    def test_overconfident_model_loses_to_base_rate(self):
        rnd = random.Random(1)
        y = [rnd.random() < 0.5 for _ in range(2000)]
        y = [int(v) for v in y]
        confident = [0.9] * len(y)  # claims 90% on coin flips
        self.assertGreater(calibration.brier_score(confident, y), calibration.base_rate_brier(y))

    def test_no_edge_on_random_walk_is_rejected(self):
        """Synthetic zero-drift noise: the validation gate must not crown a winner."""
        rejected = 0
        for seed in range(20):
            rnd = random.Random(seed)
            p = [100.0]
            for _ in range(3000):
                p.append(p[-1] * (1 + rnd.gauss(0, 0.01)))
            oos = backtest.walk_forward(p, [10, 20, 40, 80], 500, 250, cost_bps=10)
            bench = [p[i + 1] / p[i] - 1 for i in range(len(p) - 1)][-len(oos):]
            if backtest.verdict(oos, bench).startswith("NO TRADE"):
                rejected += 1
        self.assertGreaterEqual(rejected, 18)  # at most ~10% false positives tolerated

    def test_small_sample_rejected(self):
        self.assertTrue(backtest.verdict([0.01] * 50, [0.0] * 50).startswith("NO TRADE"))


if __name__ == "__main__":
    unittest.main()
