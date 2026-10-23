# Feasibility, architecture, plan (Phase 1)

Evidence labels: **[V]** verified in this session with a tool; **[U]** unverified, from memory or vendor/secondary
claims, must be checked before relying on it; **[E]** my estimate or opinion.

## 0. What was actually verified

- [V] The sandbox had no route to CoinGecko, DefiLlama, Binance, Hyperliquid, agenkit.xyz or typesafe.ai
  (connections failed). Web search worked. **No live market data was seen. No performance number in this repo is from real markets.**
- [V] The 24 unit tests in `tests/` pass, and 3 deliberate mutations (weakened verdict gate, removed look-ahead
  guard) are caught by tests.
- [V] Search returned no content from agenkit.xyz; I cannot say what AgenKit is. [U] Secondary coverage
  ([DataCamp](https://www.datacamp.com/blog/system-one-models-jev)) describes Jev as TypeSafe AI's early-access
  "System One" model (announced mid-Sept 2026) returning typed probabilistic outputs; speed, price and
  "cannot hallucinate" are vendor claims, and the article reports ~68% accuracy on the vendor's own benchmark.
- Everything below about brokers, frameworks, prices and regulation is [U] until Phase 1 checks are run.

## 1. Feasibility assessment

| Component | Needs AI? | Verdict |
|---|---|---|
| Risk engine, order validation, reconciliation, kill switch | No | Deterministic code only. Built (core). |
| Data ingestion, point-in-time storage | No | Feasible; cost is data licensing, not code. |
| Backtesting, walk-forward, cost models | No | Feasible with existing libraries; leakage is the hard part. |
| Reading filings, transcripts, news into structured features | Yes, plausibly | LLM useful; must be tested vs simple text baselines. |
| Hypothesis generation, post-trade review, code review | Yes | LLM useful; proposes only. |
| Per-candle buy/sell classification (Jev) | Unproven | Must beat `RuleBaselineModel` and a base-rate Brier score out of sample. |
| Autonomous real-money execution | Not justified yet | [E] Retail systematic edge after costs is rare; default is paper only. |

Honest prior [E]: for liquid US equities/ETFs and BTC/ETH, a retail-scale system is more likely to match a
passive benchmark minus costs than to beat it. The platform's first job is to measure that, and it must be able to
output "no trade justified" (implemented in `backtest.verdict`).

## 2. Frameworks, APIs, brokers [U — verify in Phase 1]

| Need | Candidates | Check before choosing |
|---|---|---|
| Backtest (vectorized research) | vectorbt (open-source core, paid "PRO" tier exists), plain pandas/numpy | license, maintenance activity, pandas/numpy compatibility |
| Backtest (event-driven) | QuantConnect LEAN (Apache-2.0), Backtrader (GPL, maintenance reportedly slowed) | license fit, last release date, data handling |
| US equity broker | Alpaca, Interactive Brokers | residency/eligibility, paper-trading API, market-data licensing (real-time SIP vs IEX), fees |
| Crypto venue | A regulated venue available in the operator's jurisdiction | residency restrictions, custody/counterparty risk, API rate limits, fees |
| Data | SEC EDGAR, FRED, BLS, BEA, Treasury (free, primary); exchange/broker feeds; paid fundamentals | point-in-time availability, restatements, redistribution terms, delisted coverage |
| Agent framework | AgenKit (unverified), or plain code + Claude Agent SDK | actual capabilities; prefer plain code if the framework adds no measured value |

Rule: pick the cheapest option that passes the acceptance tests in section 7; no framework adoption without a license and maintenance check.

## 3. Market-data architecture and licensing

- Free primary sources first: EDGAR (filings, with `acceptedDate` as the as-of time), FRED/ALFRED (vintage data for revisions), BLS/BEA, Treasury.
- Every record stores: `source`, `source_ts` (when the source says it happened), `published_ts`, `ingested_ts`, `revision`, `content_hash`. Features may only use rows with `published_ts <= decision_ts`.
- Equities prices: need adjusted and unadjusted series, corporate-action table, delisted names. Free sources are usually survivorship-biased; budget for a point-in-time vendor before trusting any equity backtest.
- Licensing: real-time exchange data is licensed per user class (non-professional vs professional); redistribution through a public dashboard is usually forbidden. Keep the dashboard private.
- Store: raw immutable Parquet by date + DuckDB for research; PostgreSQL for orders, fills, positions, audit log, strategy versions.

## 4. Technical architecture

Six layers, one-way dependencies, risk engine in its own process in production:

    sources -> ingest(provenance) -> parquet/duckdb -> research/backtest -> signals
    signals -> (fast model classify, optional) -> policy gate -> sizing -> RISK ENGINE -> execution -> broker
    risk engine + kill switch: independent, reads portfolio state, can only reject or flatten
    nightly: review job -> reports + PRs (never deploys, never edits limits/permissions)

Hard rules enforced in code: model outputs are typed enums/ranges (untyped is rejected); thresholds, sizes and
side effects live in code; kill switch latches and only an operator `reset()` clears it; reducing orders are
allowed while tripped; shorting and leverage are off.

## 5. Repository structure (target; `*` = exists now)

    trading-agent/
      README.md *
      docs/FEASIBILITY.md *   docs/RISK_SPEC.md   docs/RUNBOOK.md   docs/strategies/{A..F}.md
      quantlab/
        risk.py * sizing.py * policy.py * state.py * execution.py * fastmodel.py * calibration.py * backtest.py *
        data/{edgar.py,fred.py,prices.py,provenance.py}        # Phase 2
        research/{features.py,events.py,regimes.py,costs.py}   # Phase 2-3
        strategies/{momentum.py,earnings.py,rotation.py,crypto_trend.py,events.py,fundamental.py}
        brokers/{paper.py,alpaca.py,ibkr.py}                   # alpaca/ibkr: Phase 5, off by default
        options/research_only.py                               # no execution path
        agents/{research.py,audit.py,...}                      # only where a measured benefit exists
        store/{schema.sql,pg.py}
      services/dashboard/                                      # TypeScript, read-only, Phase 4
      jobs/{daily_brief.py,weekly_report.py,nightly_review.py}
      tests/ *  infra/{Dockerfile,compose.yml}  .github/workflows/ci.yml

## 6. Deterministic risk specification (initial parameters, unvalidated)

Implemented in `quantlab/risk.py`: per-symbol position cap 10% equity; gross exposure <= 100% (no leverage);
daily loss 2%, weekly 5%, drawdown 15% each trip a latched kill switch; max 10 orders/min; quote age <= 5 s and
not future-dated; spread <= 30 bps for opening orders; order <= 1% of ADV; no shorting. Fractional Kelly is
quarter Kelly capped at 10%, and is only meaningful if probabilities are shown calibrated (Brier vs base rate).
Not yet implemented: correlation/concentration limits, volatility-adjusted sizing, fee-aware net-edge check,
exchange holidays, halts, corporate actions, position reconciliation against the broker, circuit breakers on
repeated rejects. These are Phase 2-4 acceptance items.

## 7. Phased plan and acceptance tests

| Phase | Deliverable | Acceptance (all must pass) |
|---|---|---|
| 1 Feasibility | Verified API, broker, license, cost table | Each [U] item above marked verified with a source and date; jurisdiction/eligibility confirmed in writing; Jev API access, latency and price measured on real calls |
| 2 Research infra | Ingest + provenance + Parquet/DuckDB | Replaying any past date reproduces identical features; injected future rows never change output; revised data keeps old vintages |
| 3 Validation | Benchmarks + walk-forward + stress | Each strategy beats its passive benchmark after costs on untouched out-of-sample data; reports N, CI, parameter sensitivity, regime split; a Monte Carlo of the costs/delay assumptions; independent audit finds no leakage |
| 4 Paper trading | Paper broker on live feeds, dashboard | >= 3 months, reconciliation breaks = 0 unresolved, simulated vs expected fills within tolerance, kill-switch and outage drills passed, calibration on live paper decisions |
| 5 Supervised live | Small capital, operator-approved | Written operator approval; hard limits reviewed; emergency shutdown tested the same day; daily human review |
| 6 Improve | Expansion | Only with demonstrated reliability and statistically credible results |

## 8. Monthly operating budget [E, ranges, verify with current vendor pricing]

| Item | Range (USD/month) | Note |
|---|---|---|
| VPS (always-on, small) | 10-40 | Docker, Postgres, jobs |
| Free primary data (EDGAR/FRED/BLS/BEA) | 0 | Rate limits and terms apply |
| Real-time equity data | 0-100+ | Depends on broker plan and user class |
| Point-in-time fundamentals/prices | 0-500+ | Largest uncertain item; free options are survivorship-biased |
| LLM research/review inference | 20-300 | Meter per job; cap in code |
| Fast-model inference | Unknown | Vendor price [U]; measure real token volume first |
| Monitoring/backups/domain | 5-30 | |

Planning figure [E]: roughly 50-1,000 USD/month depending mainly on data licensing. At small capital, fixed costs
alone can exceed any plausible edge; compute break-even capital before Phase 5.

## 9. Failure modes

Technical: look-ahead/leakage, survivorship bias, timezone/DST bugs, duplicate orders on retry, clock skew, silent
feed stalls, schema drift, LLM output drift, secrets leakage, VPS outage with open positions.
Financial: costs exceed edge, overfitting through repeated tuning, regime change, correlation spike in a crash,
miscalibrated probabilities driving Kelly sizing, fixed costs vs small capital.
Regulatory/legal: broker eligibility and residency limits, pattern-day-trader and margin rules, tax lots and wash
sales, data redistribution terms, crypto venue restrictions, operator is responsible for compliance and taxes [U].
Operational: exchange outage or halt, partial fills, stuck orders, broker/system position mismatch, API key
compromise, operator overriding limits during drawdown.

## 10. Final challenge

- Demonstrated edge? **None.** No real data was tested.
- What needs AI? Unstructured text extraction, hypothesis generation, review. Not execution, risk, or sizing.
- Where is deterministic code better? Risk, execution, state computation, data validation, the baseline signals.
- Data accurate and affordable? Unknown; point-in-time data is the likely cost problem.
- Strategies statistically defensible? Not yet testable; each must pass section 7 Phase 3.
- Survive an outage or crash? Partly: latched kill switch and reduce-only path exist; reconciliation and halt handling do not yet.
- Is autonomous execution justified? No.
- Simpler diversified portfolio better? [E] Likely the default winner; it is the benchmark everything must beat.
- What kills the project? Costs > edge, leakage creating a fake edge, or an unreconciled live position during an outage.
- Smallest useful version: daily EDGAR/FRED ingest with provenance + Strategy A (momentum) and a rotation benchmark
  vs buy-and-hold, walk-forward with costs, one honest report, paper broker. No LLM and no Jev needed for this.

## WHAT COULD WE BE WRONG ABOUT?

| # | Assumption | Evidence needed | Cheapest disproving experiment |
|---|---|---|---|
| 1 | A retail-scale edge exists after costs | OOS excess return vs benchmark with CI excluding zero | Run momentum + rotation walk-forward on 10+ years of ETFs; expect it may fail |
| 2 | Free/cheap data is good enough | Point-in-time, delist-aware match to a paid sample | Compare 50 tickers across free vs one paid trial; count discrepancies |
| 3 | Jev exists as advertised and is fast | Real API, measured p50/p99 latency, price | 100 live test calls from the VPS |
| 4 | Jev probabilities are calibrated | Brier < base rate and < rule baseline, reliability near diagonal | Score it on 2,000+ historical snapshots versus `RuleBaselineModel` |
| 5 | The 0.80 confidence gate means 80% accurate | Observed hit rate in the >0.80 bin | Reliability table on held-out data |
| 6 | Costs/slippage assumptions are realistic | Paper fills vs quotes at decision time | 4 weeks of paper fills vs modeled costs |
| 7 | The risk limits are adequate | Stress on historical crashes (2008, 2020, crypto 2022) with delays | Replay crash windows through `RiskEngine` with 1-5 minute execution lag |
| 8 | The broker and venue are legally usable here | Written eligibility, fee and API terms | Read terms, open a paper account, ask support |
| 9 | LLM-derived features add value over simple rules | Ablation with and without the LLM feature | Same backtest with a keyword/surprise-size baseline |
| 10 | Operator time saved exceeds build/run cost | Hours/month saved vs budget | Track weekly hours and spend for 8 weeks before any live step |
