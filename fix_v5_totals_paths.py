#!/usr/bin/env python3
"""
Fix all Grafana dashboard JSONPaths for v5 snapshot schema migration.

V5 restructured the daily snapshot payload:
  - $.totals.*          -> $.portfolio.totals.*
  - $.income.*          -> $.portfolio.income.*
  - $.portfolio_rollups -> $.portfolio  (risk nested under volatility/ratios/drawdown/var)
  - $.margin_stress.*   -> $.margin.*
  - $.goal_progress.*   -> $.goals.baseline.*
  - $.goal_progress_net -> $.goals.net_of_interest.*
  - $.goal_tiers.*      -> $.goals.*
  - $.goal_pace.*       -> $.goals.pace.*
  - Holdings sub-fields -> nested under cost/valuation/income/analytics/reliability
  - $.dividends.windows -> $.dividends.realized
  - $.coverage.*        -> $.meta.data_quality.*

Period snapshots: intervals keep flat field names, but
  intervals[].totals.market_value -> intervals[].totals.total_market_value
"""

import json
import os
import sys

DASHBOARDS_DIR = os.path.join(os.path.dirname(__file__), "grafana_lmi", "dashboards")

# ---------------------------------------------------------------------------
# DAILY dashboard replacements  (table: snapshot_daily_current)
# ---------------------------------------------------------------------------
DAILY_REPLACEMENTS = [
    # ── Totals: root → portfolio.totals ──
    ("'$.totals.market_value'",              "'$.portfolio.totals.market_value'"),
    ("'$.totals.net_liquidation_value'",     "'$.portfolio.totals.net_liquidation_value'"),
    ("'$.totals.margin_to_portfolio_pct'",   "'$.portfolio.totals.margin_to_portfolio_pct'"),
    ("'$.totals.margin_loan_balance'",       "'$.portfolio.totals.margin_loan_balance'"),
    ("'$.totals.unrealized_pnl'",            "'$.portfolio.totals.unrealized_pnl'"),
    ("'$.totals.unrealized_pct'",            "'$.portfolio.totals.unrealized_pct'"),
    ("'$.totals.cost_basis'",                "'$.portfolio.totals.cost_basis'"),
    ("'$.totals.holdings_count'",            "'$.portfolio.totals.holdings_count'"),

    # ── Income: root → portfolio.income ──
    ("'$.income.projected_monthly_income'",    "'$.portfolio.income.projected_monthly_income'"),
    ("'$.income.forward_12m_total'",           "'$.portfolio.income.forward_12m_total'"),
    ("'$.income.portfolio_current_yield_pct'", "'$.portfolio.income.portfolio_current_yield_pct'"),
    ("'$.income.portfolio_yield_on_cost_pct'", "'$.portfolio.income.portfolio_yield_on_cost_pct'"),

    # ── Risk: drawdown_status → drawdown  (before general risk rules) ──
    ("'$.portfolio_rollups.risk.drawdown_status.currently_in_drawdown'",
     "'$.portfolio.risk.drawdown.currently_in_drawdown'"),
    ("'$.portfolio_rollups.risk.drawdown_status.current_drawdown_depth_pct'",
     "'$.portfolio.risk.drawdown.current_drawdown_depth_pct'"),
    ("'$.portfolio_rollups.risk.drawdown_status.days_since_peak'",
     "'$.portfolio.risk.drawdown.days_since_peak'"),
    ("'$.portfolio_rollups.risk.drawdown_status.recovery_progress_pct'",
     "'$.portfolio.risk.drawdown.recovery_progress_pct'"),

    # ── Risk: volatility ──
    ("'$.portfolio_rollups.risk.vol_30d_pct'",  "'$.portfolio.risk.volatility.vol_30d_pct'"),
    ("'$.portfolio_rollups.risk.vol_90d_pct'",  "'$.portfolio.risk.volatility.vol_90d_pct'"),

    # ── Risk: ratios ──
    ("'$.portfolio_rollups.risk.sharpe_1y'",       "'$.portfolio.risk.ratios.sharpe_1y'"),
    ("'$.portfolio_rollups.risk.sortino_1y'",      "'$.portfolio.risk.ratios.sortino_1y'"),
    ("'$.portfolio_rollups.risk.calmar_1y'",       "'$.portfolio.risk.ratios.calmar_1y'"),
    ("'$.portfolio_rollups.risk.ulcer_index_1y'",  "'$.portfolio.risk.ratios.ulcer_index_1y'"),
    ("'$.portfolio_rollups.risk.omega_ratio_1y'",  "'$.portfolio.risk.ratios.omega_ratio_1y'"),

    # ── Risk: drawdown (max) ──
    ("'$.portfolio_rollups.risk.max_drawdown_1y_pct'",
     "'$.portfolio.risk.drawdown.max_drawdown_1y_pct'"),

    # ── Risk: VaR / CVaR ──
    ("'$.portfolio_rollups.risk.var_95_1d_pct'",  "'$.portfolio.risk.var.var_95_1d_pct'"),
    ("'$.portfolio_rollups.risk.var_95_1w_pct'",  "'$.portfolio.risk.var.var_95_1w_pct'"),
    ("'$.portfolio_rollups.risk.var_95_1m_pct'",  "'$.portfolio.risk.var.var_95_1m_pct'"),
    ("'$.portfolio_rollups.risk.cvar_95_1d_pct'", "'$.portfolio.risk.var.cvar_95_1d_pct'"),
    ("'$.portfolio_rollups.risk.cvar_95_1w_pct'", "'$.portfolio.risk.var.cvar_95_1w_pct'"),
    ("'$.portfolio_rollups.risk.cvar_95_1m_pct'", "'$.portfolio.risk.var.cvar_95_1m_pct'"),

    # ── Risk: standalone fields ──
    ("'$.portfolio_rollups.risk.beta_portfolio'",        "'$.portfolio.risk.beta_portfolio'"),
    ("'$.portfolio_rollups.risk.portfolio_risk_quality'", "'$.portfolio.risk.portfolio_risk_quality'"),
    ("'$.portfolio_rollups.risk.income_stability_score'", "'$.portfolio.risk.income_stability_score'"),
    ("'$.portfolio_rollups.risk.tracking_error_1y_pct'",
     "'$.portfolio.performance.vs_benchmark.tracking_error_1y_pct'"),
    ("'$.portfolio_rollups.risk.corr_1y'",
     "'$.portfolio.performance.vs_benchmark.correlation_to_benchmark'"),

    # ── vs_benchmark ──
    ("'$.portfolio_rollups.vs_benchmark.excess_return_1y_pct'",
     "'$.portfolio.performance.vs_benchmark.excess_return_1y_pct'"),
    ("'$.portfolio_rollups.vs_benchmark.tracking_error_1y_pct'",
     "'$.portfolio.performance.vs_benchmark.tracking_error_1y_pct'"),
    ("'$.portfolio_rollups.vs_benchmark.information_ratio_1y'",
     "'$.portfolio.performance.vs_benchmark.information_ratio_1y'"),

    # ── Attribution  (prefix-based – covers .top_contributors, .bottom_contributors, etc.) ──
    ("'$.portfolio_rollups.return_attribution_1m.",  "'$.portfolio.attribution.1m."),
    ("'$.portfolio_rollups.return_attribution_3m.",  "'$.portfolio.attribution.3m."),
    ("'$.portfolio_rollups.return_attribution_6m.",  "'$.portfolio.attribution.6m."),
    ("'$.portfolio_rollups.return_attribution_12m.", "'$.portfolio.attribution.12m."),

    # ── Income stability (portfolio_rollups.income_stability → portfolio.income.income_stability) ──
    ("'$.portfolio_rollups.income_stability.", "'$.portfolio.income.income_stability."),

    # ── Margin stress → margin ──
    ("'$.margin_stress.", "'$.margin."),

    # ── Goals  (order: _net before plain to avoid partial match) ──
    ("'$.goal_progress_net.", "'$.goals.net_of_interest."),
    ("'$.goal_progress.",     "'$.goals.baseline."),
    ("'$.goal_tiers.current_state.", "'$.goals.current_state."),
    ("'$.goal_tiers.tiers'",         "'$.goals.tiers'"),
    ("'$.goal_pace.",                "'$.goals.pace."),

    # ── Data quality ──
    ("'$.prices_as_of'",        "'$.timestamps.price_data_as_of_date'"),
    ("'$.missing_prices'",      "'$.meta.data_quality.missing_paths'"),
    ("'$.coverage.derived_pct'","'$.meta.data_quality.derived_pct'"),

    # ── Dividends ──
    ("'$.dividends.windows.30d.by_symbol'", "'$.dividends.realized.30d.by_symbol'"),

    # ── Holdings sub-fields  (json_each(h.value) context only in daily) ──
    ("'$.weight_pct'",               "'$.valuation.portfolio_weight_pct'"),
    ("'$.market_value'",             "'$.valuation.market_value'"),
    ("'$.current_yield_pct'",        "'$.income.current_yield_pct'"),
    ("'$.projected_monthly_dividend'","'$.income.projected_monthly_dividend'"),
    ("'$.unrealized_pct'",           "'$.valuation.unrealized_pct'"),
    ("'$.yield_on_cost_pct'",        "'$.income.yield_on_cost_pct'"),
    ("'$.forward_12m_dividend'",     "'$.income.forward_12m_dividend'"),
    ("'$.cost_basis'",               "'$.cost.cost_basis'"),
    ("'$.avg_cost_per_share'",       "'$.cost.avg_cost_per_share'"),
    ("'$.last_price'",               "'$.valuation.last_price'"),
    ("'$.unrealized_pnl'",           "'$.valuation.unrealized_pnl'"),

    # Holdings: ultimate.* → analytics.risk.*
    ("'$.ultimate.sortino_1y'",           "'$.analytics.risk.sortino_1y'"),
    ("'$.ultimate.sharpe_1y'",            "'$.analytics.risk.sharpe_1y'"),
    ("'$.ultimate.risk_quality_category'","'$.analytics.risk.risk_quality_category'"),
    ("'$.ultimate.risk_quality_score'",   "'$.analytics.risk.risk_quality_score'"),
    ("'$.ultimate.vol_30d_pct'",          "'$.analytics.risk.vol_30d_pct'"),
    ("'$.ultimate.vol_90d_pct'",          "'$.analytics.risk.vol_90d_pct'"),
    ("'$.ultimate.beta_3y'",              "'$.analytics.risk.beta_3y'"),
    ("'$.ultimate.max_drawdown_1y_pct'",  "'$.analytics.risk.max_drawdown_1y_pct'"),
    ("'$.ultimate.corr_1y'",              "'$.analytics.performance.corr_1y'"),
    ("'$.ultimate.twr_1m_pct'",           "'$.analytics.performance.twr_1m_pct'"),
    ("'$.ultimate.twr_3m_pct'",           "'$.analytics.performance.twr_3m_pct'"),
    ("'$.ultimate.twr_6m_pct'",           "'$.analytics.performance.twr_6m_pct'"),
    ("'$.ultimate.twr_12m_pct'",          "'$.analytics.performance.twr_12m_pct'"),
    ("'$.ultimate.distribution_frequency'",  "'$.analytics.distribution.distribution_frequency'"),
    ("'$.ultimate.trailing_12m_yield_pct'",  "'$.analytics.distribution.trailing_12m_yield_pct'"),
    ("'$.ultimate.forward_yield_pct'",       "'$.analytics.distribution.forward_yield_pct'"),
    ("'$.ultimate.next_ex_date_est'",        "'$.analytics.distribution.next_ex_date_est'"),

    # Holdings: dividend_reliability.* → reliability.*
    ("'$.dividend_reliability.", "'$.reliability."),
]

# ---------------------------------------------------------------------------
# PERIOD dashboard replacements  (table: snapshots)
# ---------------------------------------------------------------------------
PERIOD_REPLACEMENTS = [
    # intervals totals: market_value → total_market_value
    # (period_summary already uses total_market_value – only intervals need fixing)
    ("intervals[%d].totals.market_value'", "intervals[%d].totals.total_market_value'"),
]


def classify_file(content: str) -> str:
    """Return 'daily', 'period', or 'both' based on which table the file queries."""
    has_daily = "snapshot_daily_current" in content
    # In JSON strings, newlines are encoded as literal \n, so check for that too
    has_period = (
        "FROM snapshots " in content
        or "FROM snapshots\\n" in content
        or "FROM snapshots'" in content
    )
    if has_daily and has_period:
        return "both"
    if has_daily:
        return "daily"
    if has_period:
        return "period"
    return "unknown"


def apply_replacements(content: str, replacements: list[tuple[str, str]]) -> tuple[str, int]:
    """Apply all replacements and return (new_content, total_count)."""
    total = 0
    for old, new in replacements:
        count = content.count(old)
        if count:
            content = content.replace(old, new)
            total += count
    return content, total


def main():
    if not os.path.isdir(DASHBOARDS_DIR):
        print(f"ERROR: Dashboard directory not found: {DASHBOARDS_DIR}")
        sys.exit(1)

    json_files = sorted(
        f for f in os.listdir(DASHBOARDS_DIR) if f.endswith(".json")
    )

    if not json_files:
        print("ERROR: No JSON files found in dashboard directory")
        sys.exit(1)

    print(f"Found {len(json_files)} dashboard files in {DASHBOARDS_DIR}\n")

    grand_total = 0
    files_changed = 0

    for fname in json_files:
        fpath = os.path.join(DASHBOARDS_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            original = f.read()

        file_type = classify_file(original)
        content = original
        file_count = 0

        if file_type in ("daily", "both"):
            content, n = apply_replacements(content, DAILY_REPLACEMENTS)
            file_count += n

        if file_type in ("period", "both"):
            content, n = apply_replacements(content, PERIOD_REPLACEMENTS)
            file_count += n

        if content != original:
            # Validate JSON is still parseable
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                print(f"  WARNING: {fname} – JSON validation failed after replacement: {e}")
                print(f"           Skipping write for this file.")
                continue

            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            files_changed += 1
            print(f"  [{file_type:6s}] {fname:45s}  {file_count:3d} replacements")
        else:
            print(f"  [{file_type:6s}] {fname:45s}    0 replacements (unchanged)")

        grand_total += file_count

    print(f"\nDone: {grand_total} total replacements across {files_changed} files")


if __name__ == "__main__":
    main()
