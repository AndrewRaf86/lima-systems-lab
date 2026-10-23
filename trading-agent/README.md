# trading-agent (paper-only research platform)

Status: Phase 1 documents + deterministic core. **No live data, no broker adapter, no real-money path exists.**

    python3 -m unittest discover -s tests -t .     # 24 tests, stdlib only

| Path | Purpose |
|---|---|
| `quantlab/risk.py` | Deterministic risk engine, latched kill switch. No model can change it. |
| `quantlab/sizing.py` | Fractional Kelly (quarter, capped). Valid only if probabilities are calibrated. |
| `quantlab/policy.py` | Typed fast-model output + code-owned gate and escalation. |
| `quantlab/state.py` | Causal order-book snapshot (<400 tokens), rejects stale/future data. |
| `quantlab/execution.py` | Broker interface, paper broker, duplicate/market-hours/risk checks. |
| `quantlab/fastmodel.py` | Fast-model interface + deterministic baseline (the bar to beat). Jev is NOT integrated. |
| `quantlab/calibration.py` | Brier score, reliability bins, base-rate baseline. |
| `quantlab/backtest.py` | Cost-aware walk-forward harness and a verdict that can say "no trade". |
| `docs/FEASIBILITY.md` | Feasibility, comparisons, budget, plan, failure modes, open questions. |

Known gaps (not hidden): exchange holidays/half days, corporate actions, position reconciliation,
halts, persistence (Postgres), real data ingestion, dashboard. See the phase plan.
