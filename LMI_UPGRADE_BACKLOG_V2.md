# LMI Dashboards V2/V3 Upgrade Backlog

This is a forward-looking backlog for improving **daily + period snapshots**, **Grafana UX**, **Surface kiosk**, **alerts**, and **GPT endpoint integration**.

---

## 1) Alerts dashboard suite (uses existing alert tables)

Even without schema changes, you can build a full alert UX.

- **Alerts Today** (table)
  - time, severity, rule, message, symbol (if present), details JSON
- **Alerts by severity (7/30/90d)** (bar)
  - counts grouped by severity + day
- **Top alert rules** (table)
  - which rules fire most (signal quality check)
- **Alert cooldown / last fired** (table)
  - helps detect spammy rules or broken thresholds
- **Alert → Diff linking**
  - click alert row → jump to the diff dashboard for that date window

---

## 2) Daily snapshot dashboard upgrades (JSON-based, no DB changes)

- **Risk “regime” board**
  - `portfolio_risk_quality` + `ulcer_index_category` + `tail_risk_category` as status chips
- **Drawdown timeline**
  - `peak_date`, `days_since_peak`, `recovery_progress_pct`
- **Income stability board**
  - stability score, coefficient of variation, missed payments, dividend cuts (12m)
- **Tail risk “expected loss”**
  - `worst_expected_loss_1w`, `cvar_to_income_ratio` (great for margin sanity)
- **Benchmark lane**
  - excess return, info ratio, tracking error, correlation (trend it once you store history)
- **Macro overlay (if you start storing it daily)**
  - VIX / rates / SPX stress vs LTV, vol, drawdown

---

## 3) Period snapshot upgrades (story mode)

- **Period “drivers”**
  - top gainers/losers and contributors from period JSON arrays
- **Allocation change recap**
  - weight increases/decreases + net allocation shift
- **Start vs end totals**
  - MV start/end, income start/end, LTV start/end (sanity checks)
- **Narrative panel**
  - “WEEK A→B: MV +X, Income +Y, LTV -Z; drivers: …”
- **Consistency checks**
  - flag if period delta doesn’t reconcile with end-start values

---

## 4) Diff system improvements (daily + period)

- **Top holdings deltas + tags**
  - MV delta, weight delta, income delta + tag “price-driven vs income-driven”
- **New / removed positions**
  - symbols present in one snapshot but not the other
- **Threshold highlights**
  - only show rows where |delta| exceeds thresholds (tap to expand)
- **Alert → Diff → Holding drilldown**
  - link chain to filter holding panels by symbol

---

## 5) Dividend / income upgrades

- **Dividend calendar by symbol + confidence**
  - highlight estimated paydates vs known paydates
- **Projected vs received trend**
  - chart pct_of_projection MTD across months (requires history extraction)
- **Income coverage ratio**
  - projected monthly income / estimated monthly margin interest (approx is OK)
- **Upcoming 30d income by symbol**
  - stacked bars for active symbols

---

## 6) Optional data model upgrades (makes Grafana 10x easier)

Materialize “typed” tables from your JSON blobs while keeping `payload_json` as truth:

- **snapshot_daily_metrics** (1 row/day)
  - market_value, net_liq, margin_loan_balance, ltv_pct, projected_monthly_income, forward_12m_total
- **snapshot_daily_holdings** (N rows/day)
  - symbol, mv, weight, projected monthly dividend, yield, vol, drawdown, risk score

---

## 7) Grafana UX upgrades (Surface-first)

- **Switchboard tiles**
  - big touch tiles: Overview / Income / Risk / Dividends / Diffs / Alerts
- **Multiple playlists**
  - “Status loop” vs “Deep dive”
- **Period selector variable**
  - one dashboard that flips WEEK/MONTH/QUARTER/YEAR via variable
- **Annotations**
  - mark alert fire times on charts

---

## 8) Surface kiosk upgrades


- **Smart connectivity watchdog**
  - restart Chromium only if URL fails N times (avoid playlist resets)

---

## Suggested next 3 upgrades (highest ROI)

1) Alerts dashboard (Today + 7d severity + top rules)
2) Period drivers dashboard (gainers/losers + weight shifts + narrative)
3) Income coverage ratio (income vs interest proxy) for margin management
