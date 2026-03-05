#!/usr/bin/env python3
"""Generate Grafana LMI v2 dashboards.

This script intentionally keeps dashboard JSON deterministic so provisioning diffs are easy to review.
"""

from __future__ import annotations

import json
from pathlib import Path

REQUIRES = [
    {
        "type": "grafana",
        "id": "grafana",
        "name": "Grafana",
        "version": "10.0.0",
    }
]

DATASOURCE = {
    "type": "frser-sqlite-datasource",
    "uid": "lmi_sqlite",
}

DASHBOARD_DIR = Path(__file__).resolve().parents[1] / "grafana_lmi" / "dashboards"


def _target(sql: str, ref_id: str = "A") -> dict:
    q = " ".join(sql.strip().split())
    return {
        "refId": ref_id,
        "format": "table",
        "queryType": "table",
        "queryText": q,
        "rawQueryText": q,
    }


def stat_panel(
    panel_id: int,
    title: str,
    sql: str,
    x: int,
    y: int,
    w: int,
    h: int,
    unit: str = "none",
    decimals: int | None = None,
    color_mode: str = "value",
    thresholds: list[dict] | None = None,
) -> dict:
    defaults: dict = {"unit": unit}
    if decimals is not None:
        defaults["decimals"] = decimals
    if thresholds is not None:
        defaults["thresholds"] = {"mode": "absolute", "steps": thresholds}

    return {
        "id": panel_id,
        "type": "stat",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": DATASOURCE,
        "targets": [_target(sql)],
        "options": {
            "colorMode": color_mode,
            "graphMode": "none",
            "justifyMode": "auto",
            "orientation": "auto",
            "reduceOptions": {
                "calcs": ["lastNotNull"],
                "fields": "value",
                "values": False,
            },
            "textMode": "value",
            "wideLayout": True,
        },
        "fieldConfig": {"defaults": defaults, "overrides": []},
    }


def table_panel(panel_id: int, title: str, sql: str, x: int, y: int, w: int, h: int) -> dict:
    return {
        "id": panel_id,
        "type": "table",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": DATASOURCE,
        "targets": [_target(sql)],
        "options": {
            "showHeader": True,
            "cellHeight": "sm",
            "footer": {"show": False},
        },
        "fieldConfig": {"defaults": {}, "overrides": []},
    }


def timeseries_panel(
    panel_id: int,
    title: str,
    sql: str,
    x: int,
    y: int,
    w: int,
    h: int,
    unit: str = "none",
    decimals: int | None = None,
) -> dict:
    defaults: dict = {
        "unit": unit,
        "drawStyle": "line",
        "lineWidth": 2,
        "fillOpacity": 10,
        "showPoints": "never",
        "spanNulls": True,
    }
    if decimals is not None:
        defaults["decimals"] = decimals

    return {
        "id": panel_id,
        "type": "timeseries",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": DATASOURCE,
        "targets": [_target(sql)],
        "options": {
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "single", "sort": "none"},
        },
        "fieldConfig": {"defaults": defaults, "overrides": []},
    }


def make_dashboard(uid: str, title: str, tags: list[str], panels: list[dict], refresh: str = "2m") -> dict:
    return {
        "__inputs": [],
        "__requires": REQUIRES,
        "annotations": {"list": []},
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "id": None,
        "links": [],
        "liveNow": False,
        "panels": panels,
        "refresh": refresh,
        "schemaVersion": 39,
        "style": "dark",
        "tags": tags,
        "templating": {"list": []},
        "time": {"from": "now-120d", "to": "now"},
        "timepicker": {},
        "timezone": "browser",
        "title": title,
        "uid": uid,
        "version": 1,
        "weekStart": "",
    }


def d01_daily_command() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "As Of", "SELECT as_of_date_local AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 0, 3, 3, unit="string", color_mode="none")); i += 1
    p.append(stat_panel(i, "Prices Date", "SELECT COALESCE(substr(prices_as_of_utc,1,10),'n/a') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 3, 0, 3, 3, unit="string", color_mode="none")); i += 1
    p.append(stat_panel(i, "Market Value", "SELECT market_value AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 6, 0, 3, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Net Liquidation", "SELECT net_liquidation_value AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 9, 0, 3, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "LTV %", "SELECT ltv_pct AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 0, 3, 3, unit="percent", decimals=1,
                        thresholds=[{"color": "green", "value": None}, {"color": "yellow", "value": 25}, {"color": "red", "value": 35}])); i += 1
    p.append(stat_panel(i, "Projected Monthly", "SELECT projected_monthly_income AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 15, 0, 3, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Forward 12m", "SELECT forward_12m_total AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 18, 0, 3, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Yield on Cost %", "SELECT portfolio_yield_on_cost_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 21, 0, 3, 3, unit="percentunit", decimals=3)); i += 1

    p.append(stat_panel(i, "Unrealized P&L", "SELECT unrealized_pnl AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 3, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Drawdown Depth %", "SELECT drawdown_depth_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 3, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "In Drawdown", "SELECT CASE WHEN currently_in_drawdown=1 THEN 'YES' ELSE 'NO' END AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Tail Risk", "SELECT COALESCE(UPPER(tail_risk_category),'N/A') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Risk Quality", "SELECT COALESCE(UPPER(portfolio_risk_quality),'N/A') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Health", "SELECT COALESCE(UPPER(health_status),'N/A') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 3, 4, 3, unit="string")); i += 1

    p.append(table_panel(i, "Top Holdings", "SELECT symbol, market_value, weight_pct, current_yield_pct, projected_monthly_dividend FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY weight_pct DESC LIMIT 12", 0, 6, 12, 8)); i += 1
    p.append(table_panel(i, "Upcoming Dividends", "SELECT symbol, ex_date_est, pay_date_est, amount_est FROM daily_dividends_upcoming WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_dividends_upcoming) ORDER BY pay_date_est, ex_date_est LIMIT 12", 12, 6, 12, 8)); i += 1
    p.append(table_panel(i, "Missing Price Symbols", "WITH missing AS (SELECT symbol, weight_pct, market_value FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) AND (last_price IS NULL OR last_price<=0)) SELECT symbol, weight_pct, market_value FROM missing UNION ALL SELECT 'none' AS symbol, NULL AS weight_pct, NULL AS market_value WHERE NOT EXISTS (SELECT 1 FROM missing) LIMIT 20", 0, 14, 12, 6)); i += 1
    p.append(table_panel(i, "120d Daily Return Attribution", "SELECT as_of_date_local, window, contribution_pct AS total_return_pct FROM daily_return_attribution WHERE symbol='_portfolio' AND as_of_date_local>=date('now','-120 day') ORDER BY as_of_date_local DESC, CASE window WHEN '1m' THEN 1 WHEN '3m' THEN 2 WHEN '6m' THEN 3 WHEN '12m' THEN 4 ELSE 9 END", 12, 14, 12, 6)); i += 1

    return "lmi-v2-d01-daily-command-board.json", make_dashboard(
        uid="lmi-v2-d01-daily-command",
        title="D01 LMI v2 - Daily Command Board",
        tags=["lmi", "v2", "data-heavy", "kiosk"],
        panels=p,
    )


def d02_holdings_risk_matrix() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "Holdings Count", "SELECT holdings_count AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 0, 6, 3, unit="none", decimals=0)); i += 1
    p.append(stat_panel(i, "Top 3 %", "SELECT top3_weight_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 6, 0, 6, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Top 5 %", "SELECT top5_weight_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 0, 6, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Herfindahl", "SELECT herfindahl_index AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 18, 0, 6, 3, unit="none", decimals=4)); i += 1

    p.append(table_panel(i, "Holdings Core", "SELECT symbol, shares, market_value, weight_pct, projected_monthly_dividend, current_yield_pct, unrealized_pct FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY market_value DESC LIMIT 25", 0, 3, 12, 8)); i += 1
    p.append(table_panel(i, "Holdings Risk Metrics", "SELECT symbol, vol_30d_pct, vol_90d_pct, beta_3y, sharpe_1y, sortino_1y, var_95_1d_pct, cvar_95_1d_pct, max_drawdown_1y_pct, risk_quality_category FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY weight_pct DESC LIMIT 25", 12, 3, 12, 8)); i += 1

    p.append(table_panel(i, "Reliability Watchlist", "SELECT symbol, reliability_consistency_score, reliability_trend_6m, reliability_missed_payments_12m, distribution_frequency, dividends_30d FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY reliability_consistency_score ASC, weight_pct DESC LIMIT 20", 0, 11, 12, 8)); i += 1
    p.append(table_panel(i, "Most Fragile Holdings", "SELECT symbol, weight_pct, cvar_95_1d_pct, var_95_1d_pct, max_drawdown_1y_pct, risk_quality_category FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY cvar_95_1d_pct ASC, weight_pct DESC LIMIT 20", 12, 11, 12, 8)); i += 1

    return "lmi-v2-d02-holdings-risk-matrix.json", make_dashboard(
        uid="lmi-v2-d02-holdings-risk",
        title="D02 LMI v2 - Holdings Risk Matrix",
        tags=["lmi", "v2", "data-heavy", "kiosk"],
        panels=p,
    )


def d03_income_calendar_reliability() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "MTD Projected", "SELECT dividends_projected_monthly AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "MTD Realized", "SELECT dividends_realized_mtd AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "MTD Gap", "SELECT (dividends_projected_monthly - dividends_realized_mtd) AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Received %", "SELECT (dividends_received_pct/100.0) AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Realized 30d", "SELECT dividends_realized_30d AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Realized YTD", "SELECT dividends_realized_ytd AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1

    p.append(table_panel(i, "Income Leaderboard", "SELECT symbol, projected_monthly_dividend, forward_12m_dividend, current_yield_pct, dividends_30d, dividends_qtd, dividends_ytd FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY projected_monthly_dividend DESC LIMIT 20", 0, 3, 12, 8)); i += 1
    p.append(table_panel(i, "Upcoming Ex/Pay Ledger", "SELECT symbol, ex_date_est, pay_date_est, amount_est, CASE WHEN pay_date_est < date('now') THEN 'OVERDUE' ELSE 'PENDING' END AS status FROM daily_dividends_upcoming WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_dividends_upcoming) ORDER BY pay_date_est, ex_date_est LIMIT 24", 12, 3, 12, 8)); i += 1

    p.append(table_panel(i, "Period Dividend Events", "SELECT period_type, period_start_date, period_end_date, symbol, ex_date, pay_date, amount FROM period_dividend_events ORDER BY period_end_date DESC, ex_date DESC LIMIT 40", 0, 11, 12, 8)); i += 1
    p.append(table_panel(i, "Reliability Watchlist", "SELECT symbol, reliability_consistency_score, reliability_missed_payments_12m, reliability_trend_6m, distribution_frequency, next_ex_date_est FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) ORDER BY reliability_missed_payments_12m DESC, reliability_consistency_score ASC LIMIT 24", 12, 11, 12, 8)); i += 1

    return "lmi-v2-d03-income-calendar-reliability.json", make_dashboard(
        uid="lmi-v2-d03-income-calendar",
        title="D03 LMI v2 - Income Calendar & Reliability",
        tags=["lmi", "v2", "data-heavy", "income"],
        panels=p,
    )


def d04_margin_stress_desk() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "Margin Balance", "SELECT margin_loan_balance AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "LTV %", "SELECT ltv_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Monthly Interest", "SELECT monthly_interest_current AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 0, 4, 3, unit="currencyUSD", decimals=2)); i += 1
    p.append(stat_panel(i, "Annual Interest", "SELECT annual_interest_current AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 0, 4, 3, unit="currencyUSD", decimals=2)); i += 1
    p.append(stat_panel(i, "Income Coverage", "SELECT COALESCE(margin_income_coverage, projected_monthly_income / NULLIF(monthly_interest_current,0)) AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 0, 4, 3, unit="none", decimals=2)); i += 1
    p.append(stat_panel(i, "Buffer to Call %", "SELECT buffer_to_margin_call_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 0, 4, 3, unit="percentunit", decimals=3)); i += 1

    p.append(stat_panel(i, "Max Loan @25%", "SELECT market_value*0.25 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 3, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Max Loan @30%", "SELECT market_value*0.30 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 3, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "MV @ 30% LTV", "SELECT margin_loan_balance / 0.30 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 3, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Drop to 30% %", "SELECT (((margin_loan_balance/0.30)-market_value)/NULLIF(market_value,0))/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 3, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Net Benefit 1y", "SELECT (projected_monthly_income*12.0)-annual_interest_current AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 3, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "ROI on Margin 1y %", "SELECT (((projected_monthly_income*12.0)-annual_interest_current)/NULLIF(margin_loan_balance,0))/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 3, 4, 3, unit="percentunit", decimals=3)); i += 1

    p.append(table_panel(i, "Rate Scenarios (+100/+200/+300)", "SELECT as_of_date_local, scenario, new_rate_pct, new_monthly_cost, income_coverage, margin_impact_pct FROM daily_margin_rate_scenarios WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_margin_rate_scenarios) ORDER BY scenario", 0, 6, 8, 8)); i += 1
    p.append(timeseries_panel(i, "Margin Balance History (Fallback Safe)", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, balance AS value FROM ( SELECT as_of_date_local, balance FROM margin_balance_history UNION ALL SELECT as_of_date_local, margin_loan_balance AS balance FROM daily_portfolio WHERE NOT EXISTS (SELECT 1 FROM margin_balance_history) ) src WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 8, 6, 8, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "LTV / Coverage Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, ltv_pct AS \"LTV %\", COALESCE(margin_income_coverage, projected_monthly_income / NULLIF(monthly_interest_current,0)) AS \"Income Coverage\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 16, 6, 8, 8, unit="short", decimals=2)); i += 1

    return "lmi-v2-d04-margin-stress-desk.json", make_dashboard(
        uid="lmi-v2-d04-margin-stress",
        title="D04 LMI v2 - Margin & Stress Desk",
        tags=["lmi", "v2", "data-heavy", "margin"],
        panels=p,
    )


def d05_period_scorecard() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(table_panel(i, "Rolling WTD/MTD/QTD/YTD Strip", "SELECT CASE period_type WHEN 'WEEK' THEN 'WTD' WHEN 'MONTH' THEN 'MTD' WHEN 'QUARTER' THEN 'QTD' WHEN 'YEAR' THEN 'YTD' END AS period, period_start_date || ' -> ' || period_end_date AS range, mv_delta, monthly_income_delta, twr_period_pct, ltv_pct_delta FROM period_summary WHERE is_rolling=1 AND period_type IN ('WEEK','MONTH','QUARTER','YEAR') ORDER BY CASE period_type WHEN 'WEEK' THEN 1 WHEN 'MONTH' THEN 2 WHEN 'QUARTER' THEN 3 WHEN 'YEAR' THEN 4 END", 0, 0, 12, 7)); i += 1
    p.append(table_panel(i, "Latest Completed W/M/Q/Y", "SELECT period_type, period_start_date, period_end_date, mv_end, monthly_income_end, ltv_pct_end, twr_period_pct FROM period_summary WHERE is_rolling=0 AND period_type IN ('WEEK','MONTH','QUARTER','YEAR') AND (period_type, period_end_date) IN ( SELECT period_type, MAX(period_end_date) FROM period_summary WHERE is_rolling=0 AND period_type IN ('WEEK','MONTH','QUARTER','YEAR') GROUP BY period_type ) ORDER BY CASE period_type WHEN 'WEEK' THEN 1 WHEN 'MONTH' THEN 2 WHEN 'QUARTER' THEN 3 WHEN 'YEAR' THEN 4 END", 12, 0, 12, 7)); i += 1

    p.append(table_panel(i, "Rolling vs Completed Comparison", "WITH r AS (SELECT period_type, mv_delta AS rolling_mv_delta, monthly_income_delta AS rolling_income_delta, twr_period_pct AS rolling_twr FROM period_summary WHERE is_rolling=1), c AS (SELECT p1.period_type, p1.mv_delta AS completed_mv_delta, p1.monthly_income_delta AS completed_income_delta, p1.twr_period_pct AS completed_twr FROM period_summary p1 JOIN (SELECT period_type, MAX(period_end_date) AS max_end FROM period_summary WHERE is_rolling=0 GROUP BY period_type) m ON p1.period_type=m.period_type AND p1.period_end_date=m.max_end WHERE p1.is_rolling=0) SELECT r.period_type, r.rolling_mv_delta, c.completed_mv_delta, r.rolling_income_delta, c.completed_income_delta, r.rolling_twr, c.completed_twr FROM r LEFT JOIN c USING(period_type) ORDER BY CASE r.period_type WHEN 'WEEK' THEN 1 WHEN 'MONTH' THEN 2 WHEN 'QUARTER' THEN 3 WHEN 'YEAR' THEN 4 END", 0, 7, 12, 7)); i += 1
    p.append(table_panel(i, "Risk Event Table", "SELECT period_type, period_start_date, period_end_date, days_exceeding_var_95, margin_call_events, period_max_drawdown_pct, worst_day_return_pct, best_day_return_pct FROM period_summary WHERE period_type IN ('WEEK','MONTH','QUARTER','YEAR') ORDER BY period_end_date DESC LIMIT 40", 12, 7, 12, 7)); i += 1

    p.append(table_panel(i, "Period Macro Summary", "SELECT period_type, period_start_date, period_end_date, metric, avg_val, min_val, max_val, min_date, max_date FROM period_macro_stats WHERE period_type IN ('WEEK','MONTH','QUARTER','YEAR') ORDER BY period_end_date DESC, metric LIMIT 60", 0, 14, 12, 7)); i += 1
    p.append(table_panel(i, "Period Risk Stats Summary", "SELECT period_type, period_start_date, period_end_date, metric, avg_val, min_val, max_val FROM period_risk_stats WHERE period_type IN ('WEEK','MONTH','QUARTER','YEAR') ORDER BY period_end_date DESC, metric LIMIT 60", 12, 14, 12, 7)); i += 1

    return "lmi-v2-d05-rolling-completed-scorecard.json", make_dashboard(
        uid="lmi-v2-d05-period-scorecard",
        title="D05 LMI v2 - Rolling + Completed Period Scorecard",
        tags=["lmi", "v2", "data-heavy", "periods"],
        panels=p,
    )


def d06_period_interval_ledger() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(table_panel(i, "Interval Table", "SELECT period_type, period_start_date, period_end_date, interval_label, interval_start, interval_end, mv, monthly_income, ltv_pct, vol_30d_pct, var_95_1d_pct, cvar_90_1d_pct, goal_progress_pct FROM period_intervals ORDER BY period_end_date DESC, interval_start DESC LIMIT 60", 0, 0, 24, 7)); i += 1

    p.append(table_panel(i, "Latest Interval Holdings", "WITH latest AS (SELECT period_type, period_start_date, period_end_date, interval_label FROM period_intervals ORDER BY period_end_date DESC, interval_start DESC LIMIT 1) SELECT h.period_type, h.period_start_date, h.period_end_date, h.interval_label, h.symbol, h.weight_pct, h.market_value, h.pnl_pct, h.projected_monthly_dividend, h.current_yield_pct, h.risk_quality_category FROM period_interval_holdings h JOIN latest l ON h.period_type=l.period_type AND h.period_start_date=l.period_start_date AND h.period_end_date=l.period_end_date AND h.interval_label=l.interval_label ORDER BY h.weight_pct DESC", 0, 7, 12, 7)); i += 1
    p.append(table_panel(i, "Latest Interval Attribution", "WITH latest AS (SELECT period_type, period_start_date, period_end_date, interval_label FROM period_intervals ORDER BY period_end_date DESC, interval_start DESC LIMIT 1) SELECT a.period_type, a.period_start_date, a.period_end_date, a.interval_label, a.window, a.total_return_pct, a.income_contribution_pct, a.price_contribution_pct FROM period_interval_attribution a JOIN latest l ON a.period_type=l.period_type AND a.period_start_date=l.period_start_date AND a.period_end_date=l.period_end_date AND a.interval_label=l.interval_label ORDER BY CASE a.window WHEN '1m' THEN 1 WHEN '3m' THEN 2 WHEN '6m' THEN 3 WHEN '12m' THEN 4 ELSE 9 END", 12, 7, 12, 7)); i += 1

    p.append(table_panel(i, "Holding Changes", "SELECT period_type, period_start_date, period_end_date, symbol, change_type, market_value_delta, weight_delta_pct, end_projected_monthly, period_max_drawdown_pct FROM period_holding_changes ORDER BY period_end_date DESC, abs(COALESCE(market_value_delta,0)) DESC LIMIT 60", 0, 14, 12, 7)); i += 1
    p.append(table_panel(i, "Position List Matrix", "SELECT period_type, period_start_date, period_end_date, list_type, symbol FROM period_position_lists ORDER BY period_end_date DESC, list_type, symbol LIMIT 100", 12, 14, 12, 7)); i += 1

    p.append(table_panel(i, "Contributions Ledger", "SELECT period_type, period_start_date, period_end_date, contribution_date, amount, account_id FROM period_contributions ORDER BY period_end_date DESC, contribution_date DESC LIMIT 50", 0, 21, 8, 6)); i += 1
    p.append(table_panel(i, "Withdrawals Ledger", "SELECT period_type, period_start_date, period_end_date, withdrawal_date, amount, account_id FROM period_withdrawals ORDER BY period_end_date DESC, withdrawal_date DESC LIMIT 50", 8, 21, 8, 6)); i += 1
    p.append(table_panel(i, "Period Margin Detail", "SELECT period_type, period_start_date, period_end_date, borrowed, repaid, net_change FROM period_margin_detail ORDER BY period_end_date DESC LIMIT 50", 16, 21, 8, 6)); i += 1

    p.append(table_panel(i, "Dividend Events Ledger", "SELECT period_type, period_start_date, period_end_date, symbol, ex_date, pay_date, amount FROM period_dividend_events ORDER BY period_end_date DESC, ex_date DESC LIMIT 60", 0, 27, 12, 6)); i += 1
    p.append(table_panel(i, "Trades Ledger", "SELECT period_type, period_start_date, period_end_date, symbol, buy_count, sell_count FROM period_trades ORDER BY period_end_date DESC, symbol LIMIT 60", 12, 27, 12, 6)); i += 1

    p.append(table_panel(i, "Activity Totals", "SELECT period_type, period_start_date, period_end_date, contributions_total, contributions_count, withdrawals_total, withdrawals_count, dividends_total_received, dividends_count, interest_total_paid, trades_total_count, positions_added_count, positions_removed_count, positions_increased_count, positions_decreased_count FROM period_activity ORDER BY period_end_date DESC LIMIT 50", 0, 33, 24, 6)); i += 1

    return "lmi-v2-d06-period-interval-activity-ledger.json", make_dashboard(
        uid="lmi-v2-d06-interval-ledger",
        title="D06 LMI v2 - Period Interval & Activity Ledger",
        tags=["lmi", "v2", "data-heavy", "periods"],
        panels=p,
    )


def d07_goals_tiers() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "Goal Progress %", "SELECT goal_progress_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Net Progress %", "SELECT goal_net_progress_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Months to Goal", "SELECT goal_months_to_goal AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 0, 4, 3, unit="none", decimals=1)); i += 1
    p.append(stat_panel(i, "Net Months to Goal", "SELECT goal_net_months_to_goal AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 0, 4, 3, unit="none", decimals=1)); i += 1
    p.append(stat_panel(i, "Current Monthly", "SELECT goal_current_projected_monthly AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1
    p.append(stat_panel(i, "Target Monthly", "SELECT goal_target_monthly_income AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 0, 4, 3, unit="currencyUSD", decimals=0)); i += 1

    p.append(stat_panel(i, "Likely Tier", "SELECT CAST(goal_likely_tier AS TEXT) || ' - ' || COALESCE(goal_likely_tier_name,'n/a') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Tier Confidence", "SELECT COALESCE(UPPER(goal_likely_tier_confidence),'N/A') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Pace Category", "SELECT COALESCE(UPPER(goal_pace_category),'N/A') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Months Ahead/Behind", "SELECT goal_pace_months_ahead_behind AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 3, 4, 3, unit="none", decimals=1)); i += 1
    p.append(stat_panel(i, "Revised Goal Date", "SELECT goal_pace_revised_goal_date AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 3, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Additional Needed", "SELECT MAX(goal_required_portfolio_value - market_value, 0) AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 3, 4, 3, unit="currencyUSD", decimals=0)); i += 1

    p.append(table_panel(i, "6-Tier Roadmap", "SELECT tier, name, description, target_monthly, required_portfolio_value, final_portfolio_value, progress_pct, months_to_goal, estimated_goal_date, confidence, assumption_monthly_contribution, assumption_drip_enabled, assumption_annual_appreciation_pct, assumption_ltv_maintained, assumption_target_ltv_pct FROM daily_goal_tiers WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_goal_tiers) ORDER BY tier", 0, 6, 12, 10)); i += 1
    p.append(table_panel(i, "Parsed Pace Windows", "WITH latest AS (SELECT goal_pace_windows_json FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1), windows AS (SELECT value AS w FROM latest, json_each(latest.goal_pace_windows_json)) SELECT json_extract(w,'$.window_name') AS window_name, CAST(json_extract(w,'$.days_in_window') AS INTEGER) AS days, CAST(json_extract(w,'$.expected.portfolio_value') AS REAL) AS expected_pv, CAST(json_extract(w,'$.actual.portfolio_value') AS REAL) AS actual_pv, CAST(json_extract(w,'$.delta.portfolio_value') AS REAL) AS pv_delta, CAST(json_extract(w,'$.delta.portfolio_value_pct') AS REAL) AS pv_delta_pct, CAST(json_extract(w,'$.pace.months_ahead_behind') AS REAL) AS months_ahead_behind, CAST(json_extract(w,'$.pace.pct_of_tier_pace') AS REAL) AS pct_of_tier_pace FROM windows ORDER BY days", 12, 6, 12, 10)); i += 1

    return "lmi-v2-d07-goals-tier-scenarios.json", make_dashboard(
        uid="lmi-v2-d07-goals-tiers",
        title="D07 LMI v2 - Goals & Tier Scenarios",
        tags=["lmi", "v2", "data-heavy", "goals"],
        panels=p,
    )


def d08_alerts_console() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "Open Alerts", "SELECT COUNT(*) AS value FROM alert_messages WHERE status='open'", 0, 0, 4, 3, unit="none", decimals=0)); i += 1
    p.append(stat_panel(i, "Acked Alerts", "SELECT COUNT(*) AS value FROM alert_messages WHERE status='acked'", 4, 0, 4, 3, unit="none", decimals=0)); i += 1
    p.append(stat_panel(i, "Open Sev>=5", "SELECT COUNT(*) AS value FROM alert_messages WHERE status='open' AND severity>=5", 8, 0, 4, 3, unit="none", decimals=0)); i += 1
    p.append(stat_panel(i, "Notifications 24h", "SELECT COUNT(*) AS value FROM alert_notifications WHERE sent_at_utc >= datetime('now','-1 day') AND success=1", 12, 0, 4, 3, unit="none", decimals=0)); i += 1
    p.append(stat_panel(i, "Distinct Categories", "SELECT COUNT(DISTINCT category) AS value FROM alert_messages", 16, 0, 4, 3, unit="none", decimals=0)); i += 1
    p.append(stat_panel(i, "Newest Alert Date", "SELECT COALESCE(MAX(as_of_date_local),'n/a') AS value FROM alert_messages", 20, 0, 4, 3, unit="string", color_mode="none")); i += 1

    p.append(table_panel(i, "Open Alerts Queue", "SELECT id, category, severity, as_of_date_local, title, notification_count, reminder_count, last_notified_at_utc FROM alert_messages WHERE status='open' ORDER BY severity DESC, as_of_date_local DESC", 0, 3, 12, 8)); i += 1
    p.append(table_panel(i, "Recently Acked Alerts", "SELECT id, category, severity, as_of_date_local, acked_at_utc, acked_by, title FROM alert_messages WHERE status='acked' ORDER BY acked_at_utc DESC, created_at_utc DESC LIMIT 40", 12, 3, 12, 8)); i += 1

    p.append(table_panel(i, "Counts by Category/Status/Severity", "SELECT category, status, severity, COUNT(*) AS alert_count, MAX(as_of_date_local) AS latest_as_of FROM alert_messages GROUP BY category, status, severity ORDER BY category, status, severity DESC", 0, 11, 12, 8)); i += 1
    p.append(table_panel(i, "High Severity Detail", "SELECT id, category, severity, status, as_of_date_local, created_at_utc, title, last_notified_at_utc FROM alert_messages WHERE severity>=5 ORDER BY status, severity DESC, created_at_utc DESC LIMIT 50", 12, 11, 12, 8)); i += 1

    p.append(table_panel(i, "Alert Aging and Repeat Fingerprints", "SELECT fingerprint, COUNT(*) AS repeats, SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) AS open_count, MIN(created_at_utc) AS first_seen_utc, MAX(created_at_utc) AS last_seen_utc FROM alert_messages GROUP BY fingerprint ORDER BY repeats DESC, last_seen_utc DESC LIMIT 50", 0, 19, 12, 8)); i += 1
    p.append(table_panel(i, "Daily Notifications", "SELECT date(sent_at_utc) AS day, channel, COUNT(*) AS sent_total, SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) AS success_total FROM alert_notifications GROUP BY date(sent_at_utc), channel ORDER BY day DESC LIMIT 60", 12, 19, 12, 8)); i += 1

    return "lmi-v2-d08-alerts-console.json", make_dashboard(
        uid="lmi-v2-d08-alerts-console",
        title="D08 LMI v2 - Alerts Console",
        tags=["lmi", "v2", "data-heavy", "alerts"],
        panels=p,
    )


def d09_data_quality_guardrail() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(stat_panel(i, "Coverage Derived %", "SELECT coverage_derived_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 0, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Coverage Missing %", "SELECT coverage_missing_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 4, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Coverage Filled %", "SELECT coverage_filled_pct/100.0 AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 8, 0, 4, 3, unit="percentunit", decimals=3)); i += 1
    p.append(stat_panel(i, "Health", "SELECT COALESCE(UPPER(health_status),'N/A') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 12, 0, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Schema Version", "SELECT COALESCE(schema_version,'n/a') AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 16, 0, 4, 3, unit="string")); i += 1
    p.append(stat_panel(i, "Price Lag (Hours)", "SELECT ROUND((julianday('now') - julianday(COALESCE(prices_as_of_utc, datetime(as_of_date_local)))) * 24.0, 2) AS value FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 1", 20, 0, 4, 3, unit="none", decimals=2)); i += 1

    p.append(table_panel(i, "Missing Prices", "SELECT symbol, market_value, weight_pct, last_price, vol_30d_pct FROM daily_holdings WHERE as_of_date_local=(SELECT MAX(as_of_date_local) FROM daily_holdings) AND (last_price IS NULL OR last_price<=0) ORDER BY weight_pct DESC LIMIT 40", 0, 3, 12, 8)); i += 1
    p.append(table_panel(i, "Stale Data Checks (Daily/Period/Alerts)", "WITH daily AS (SELECT 'daily_portfolio' AS dataset, MAX(as_of_date_local) AS latest_date FROM daily_portfolio), period AS (SELECT 'period_summary' AS dataset, MAX(period_end_date) AS latest_date FROM period_summary), alerts AS (SELECT 'alert_messages' AS dataset, MAX(as_of_date_local) AS latest_date FROM alert_messages), unioned AS (SELECT * FROM daily UNION ALL SELECT * FROM period UNION ALL SELECT * FROM alerts) SELECT dataset, latest_date, CAST(julianday('now') - julianday(latest_date) AS INTEGER) AS lag_days, CASE WHEN (julianday('now') - julianday(latest_date)) > 3 THEN 'STALE' ELSE 'FRESH' END AS status FROM unioned", 12, 3, 12, 8)); i += 1

    p.append(table_panel(i, "Recent Daily Health History", "SELECT as_of_date_local, health_status, coverage_derived_pct, coverage_missing_pct, coverage_filled_pct, prices_as_of_utc, schema_version FROM daily_portfolio ORDER BY as_of_date_local DESC LIMIT 60", 0, 11, 12, 8)); i += 1
    p.append(table_panel(i, "Alert Freshness and Status", "SELECT as_of_date_local, status, category, severity, created_at_utc, updated_at_utc, title FROM alert_messages ORDER BY created_at_utc DESC LIMIT 80", 12, 11, 12, 8)); i += 1

    return "lmi-v2-d09-data-quality-guardrail.json", make_dashboard(
        uid="lmi-v2-d09-data-quality",
        title="D09 LMI v2 - Data Quality Guardrail",
        tags=["lmi", "v2", "data-heavy", "data-quality"],
        panels=p,
    )


def g01_portfolio_trajectory() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "Market Value (120d)", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, market_value AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 0, 12, 8, unit="currencyUSD", decimals=0)); i += 1
    p.append(timeseries_panel(i, "Net Liquidation (120d)", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, net_liquidation_value AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 0, 12, 8, unit="currencyUSD", decimals=0)); i += 1
    p.append(timeseries_panel(i, "Projected Monthly Income (120d)", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, projected_monthly_income AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 8, 12, 8, unit="currencyUSD", decimals=0)); i += 1
    p.append(timeseries_panel(i, "Drawdown Depth and Recovery", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, drawdown_depth_pct AS \"Drawdown Depth %\", (100.0 + COALESCE(drawdown_depth_pct,0.0)) AS \"Recovery %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 8, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Concentration Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, top3_weight_pct AS \"Top3 %\", top5_weight_pct AS \"Top5 %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 16, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "TWR Windows Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, twr_1m_pct AS \"TWR 1m %\", twr_3m_pct AS \"TWR 3m %\", twr_6m_pct AS \"TWR 6m %\", twr_12m_pct AS \"TWR 12m %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 16, 12, 8, unit="percent", decimals=2)); i += 1

    return "lmi-v2-g01-portfolio-trajectory.json", make_dashboard(
        uid="lmi-v2-g01-portfolio-trajectory",
        title="G01 LMI v2 - Portfolio Trajectory",
        tags=["lmi", "v2", "graph", "kiosk"],
        panels=p,
    )


def g02_risk_tail_trends() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "Volatility 30d/90d", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, vol_30d_pct AS \"Vol 30d %\", vol_90d_pct AS \"Vol 90d %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 0, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Sharpe/Sortino/Calmar", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, sharpe_1y AS \"Sharpe 1y\", sortino_1y AS \"Sortino 1y\", calmar_1y AS \"Calmar 1y\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 0, 12, 8, unit="none", decimals=3)); i += 1
    p.append(timeseries_panel(i, "VaR Trends", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, var_95_1d_pct AS \"VaR 95 1d %\", var_95_1w_pct AS \"VaR 95 1w %\", var_95_1m_pct AS \"VaR 95 1m %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 8, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "CVaR Trends", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, cvar_95_1d_pct AS \"CVaR 95 1d %\", cvar_95_1w_pct AS \"CVaR 95 1w %\", cvar_95_1m_pct AS \"CVaR 95 1m %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 8, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Max Drawdown / Duration", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, max_drawdown_1y_pct AS \"Max DD 1y %\", drawdown_duration_1y_days AS \"Drawdown Duration 1y Days\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 16, 12, 8, unit="short", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Tail Risk + Risk Quality Timeline", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, cvar_to_income_ratio AS \"CVaR/Income\", CASE lower(COALESCE(tail_risk_category,'')) WHEN 'low' THEN 1 WHEN 'moderate' THEN 2 WHEN 'high' THEN 3 WHEN 'extreme' THEN 4 ELSE NULL END AS \"Tail Risk Level\", CASE lower(COALESCE(portfolio_risk_quality,'')) WHEN 'excellent' THEN 4 WHEN 'good' THEN 3 WHEN 'acceptable' THEN 2 WHEN 'concerning' THEN 1 ELSE NULL END AS \"Risk Quality Level\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 16, 12, 8, unit="none", decimals=2)); i += 1

    return "lmi-v2-g02-risk-tail-trends.json", make_dashboard(
        uid="lmi-v2-g02-risk-tail",
        title="G02 LMI v2 - Risk & Tail Trends",
        tags=["lmi", "v2", "graph", "risk"],
        panels=p,
    )


def g03_income_yield_trends() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "Projected Monthly + Forward 12m", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, projected_monthly_income AS \"Projected Monthly\", forward_12m_total AS \"Forward 12m\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 0, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Yield vs Yield on Cost", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, portfolio_yield_pct AS \"Current Yield %\", portfolio_yield_on_cost_pct AS \"Yield on Cost %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 0, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Realized Dividends Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, dividends_realized_mtd AS \"Realized MTD\", dividends_realized_30d AS \"Realized 30d\", dividends_realized_qtd AS \"Realized QTD\", dividends_realized_ytd AS \"Realized YTD\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 8, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Income Stability Score", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, income_stability_score AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 8, 12, 8, unit="none", decimals=3)); i += 1
    p.append(timeseries_panel(i, "Income Volatility 30d", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, income_volatility_30d_pct AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 16, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Dividend Cut Count 12m", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, dividend_cut_count_12m AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 16, 12, 8, unit="none", decimals=0)); i += 1

    return "lmi-v2-g03-income-yield-trends.json", make_dashboard(
        uid="lmi-v2-g03-income-yield",
        title="G03 LMI v2 - Income & Yield Trends",
        tags=["lmi", "v2", "graph", "income"],
        panels=p,
    )


def g04_margin_stress_trends() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "LTV Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, ltv_pct AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 0, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Margin Loan Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, margin_loan_balance AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 0, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Interest Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, monthly_interest_current AS \"Monthly Interest\", annual_interest_current AS \"Annual Interest\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 8, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Income Coverage Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, COALESCE(margin_income_coverage, projected_monthly_income / NULLIF(monthly_interest_current,0)) AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 8, 12, 8, unit="none", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Buffer to Call Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, buffer_to_margin_call_pct AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 16, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Scenario Coverage Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, MAX(CASE WHEN scenario='+100bp' THEN income_coverage END) AS \"+100bp Coverage\", MAX(CASE WHEN scenario='+200bp' THEN income_coverage END) AS \"+200bp Coverage\", MAX(CASE WHEN scenario='+300bp' THEN income_coverage END) AS \"+300bp Coverage\" FROM daily_margin_rate_scenarios WHERE as_of_date_local >= date('now','-120 day') GROUP BY as_of_date_local ORDER BY as_of_date_local", 12, 16, 12, 8, unit="none", decimals=2)); i += 1

    return "lmi-v2-g04-margin-stress-trends.json", make_dashboard(
        uid="lmi-v2-g04-margin-trends",
        title="G04 LMI v2 - Margin Stress Trends",
        tags=["lmi", "v2", "graph", "margin"],
        panels=p,
    )


def g05_period_dynamics() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "Completed MV Delta by Period", "SELECT (period_end_date || 'T00:00:00Z') AS time, CASE WHEN period_type='WEEK' THEN mv_delta END AS \"WEEK\", CASE WHEN period_type='MONTH' THEN mv_delta END AS \"MONTH\", CASE WHEN period_type='QUARTER' THEN mv_delta END AS \"QUARTER\", CASE WHEN period_type='YEAR' THEN mv_delta END AS \"YEAR\" FROM period_summary WHERE is_rolling=0 AND period_end_date >= date('now','-365 day') ORDER BY period_end_date", 0, 0, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Completed Income Delta by Period", "SELECT (period_end_date || 'T00:00:00Z') AS time, CASE WHEN period_type='WEEK' THEN monthly_income_delta END AS \"WEEK\", CASE WHEN period_type='MONTH' THEN monthly_income_delta END AS \"MONTH\", CASE WHEN period_type='QUARTER' THEN monthly_income_delta END AS \"QUARTER\", CASE WHEN period_type='YEAR' THEN monthly_income_delta END AS \"YEAR\" FROM period_summary WHERE is_rolling=0 AND period_end_date >= date('now','-365 day') ORDER BY period_end_date", 12, 0, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Rolling vs Completed TWR (Monthly)", "WITH rolling AS (SELECT period_end_date, twr_period_pct FROM period_summary WHERE period_type='MONTH' AND is_rolling=1), completed AS (SELECT period_end_date, twr_period_pct FROM period_summary WHERE period_type='MONTH' AND is_rolling=0 AND period_end_date >= date('now','-365 day')) SELECT (period_end_date || 'T00:00:00Z') AS time, twr_period_pct AS \"Completed Month TWR %\", NULL AS \"Rolling Month TWR %\" FROM completed UNION ALL SELECT (period_end_date || 'T00:00:00Z') AS time, NULL AS \"Completed Month TWR %\", twr_period_pct AS \"Rolling Month TWR %\" FROM rolling ORDER BY time", 0, 8, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Period Risk Stats Trend", "SELECT (period_end_date || 'T00:00:00Z') AS time, MAX(CASE WHEN metric='vol_30d_pct' THEN avg_val END) AS \"Vol30 Avg\", MAX(CASE WHEN metric='sharpe_1y' THEN avg_val END) AS \"Sharpe Avg\", MAX(CASE WHEN metric='sortino_1y' THEN avg_val END) AS \"Sortino Avg\" FROM period_risk_stats WHERE period_type='MONTH' AND period_end_date >= date('now','-365 day') GROUP BY period_end_date ORDER BY period_end_date", 12, 8, 12, 8, unit="none", decimals=3)); i += 1
    p.append(timeseries_panel(i, "Period Macro Stats Trend", "SELECT (period_end_date || 'T00:00:00Z') AS time, MAX(CASE WHEN metric='vix' THEN avg_val END) AS \"VIX Avg\", MAX(CASE WHEN metric='ten_year_yield' THEN avg_val END) AS \"10Y Yield Avg\", MAX(CASE WHEN metric='hy_spread_bps' THEN avg_val END) AS \"HY Spread Avg\" FROM period_macro_stats WHERE period_type='MONTH' AND period_end_date >= date('now','-365 day') GROUP BY period_end_date ORDER BY period_end_date", 0, 16, 12, 8, unit="none", decimals=3)); i += 1
    p.append(timeseries_panel(i, "Margin APR / Min Buffer", "SELECT (period_end_date || 'T00:00:00Z') AS time, margin_apr_end AS \"Margin APR End\", margin_min_buffer_to_call_pct AS \"Min Buffer to Call %\" FROM period_summary WHERE period_type='MONTH' AND period_end_date >= date('now','-365 day') ORDER BY period_end_date", 12, 16, 12, 8, unit="none", decimals=3)); i += 1

    return "lmi-v2-g05-period-dynamics.json", make_dashboard(
        uid="lmi-v2-g05-period-dynamics",
        title="G05 LMI v2 - Period Dynamics",
        tags=["lmi", "v2", "graph", "periods"],
        panels=p,
    )


def g06_goal_pace_trends() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "Goal Progress vs Net Progress", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, goal_progress_pct AS \"Goal Progress %\", goal_net_progress_pct AS \"Net Progress %\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 0, 12, 8, unit="percent", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Months-to-Goal vs Net", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, goal_months_to_goal AS \"Months to Goal\", goal_net_months_to_goal AS \"Net Months to Goal\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 0, 12, 8, unit="none", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Projected Monthly vs Target", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, goal_current_projected_monthly AS \"Current Projected\", goal_target_monthly_income AS \"Target\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 8, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Market Value vs Required PV", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, market_value AS \"Market Value\", goal_required_portfolio_value AS \"Required PV\" FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 8, 12, 8, unit="currencyUSD", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Likely Tier Timeline", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, goal_likely_tier AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 0, 16, 12, 8, unit="none", decimals=0)); i += 1
    p.append(timeseries_panel(i, "Months Ahead / Behind", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, goal_pace_months_ahead_behind AS value FROM daily_portfolio WHERE as_of_date_local >= date('now','-120 day') ORDER BY as_of_date_local", 12, 16, 12, 8, unit="none", decimals=2)); i += 1

    return "lmi-v2-g06-goal-pace-trends.json", make_dashboard(
        uid="lmi-v2-g06-goal-pace",
        title="G06 LMI v2 - Goal Pace Trends",
        tags=["lmi", "v2", "graph", "goals"],
        panels=p,
    )


def g07_alert_trends() -> tuple[str, dict]:
    p: list[dict] = []
    i = 1

    p.append(timeseries_panel(i, "Alerts per Day by Category", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, SUM(CASE WHEN category='income' THEN 1 ELSE 0 END) AS income, SUM(CASE WHEN category='margin' THEN 1 ELSE 0 END) AS margin, SUM(CASE WHEN category='goal_pace' THEN 1 ELSE 0 END) AS goal_pace, SUM(CASE WHEN category='ex_dividend' THEN 1 ELSE 0 END) AS ex_dividend FROM alert_messages WHERE as_of_date_local >= date('now','-120 day') GROUP BY as_of_date_local ORDER BY as_of_date_local", 0, 0, 12, 8, unit="none", decimals=0)); i += 1
    p.append(timeseries_panel(i, "Open Alert Count Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) AS open_alerts FROM alert_messages WHERE as_of_date_local >= date('now','-120 day') GROUP BY as_of_date_local ORDER BY as_of_date_local", 12, 0, 12, 8, unit="none", decimals=0)); i += 1
    p.append(timeseries_panel(i, "Severity Trend", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, AVG(severity) AS avg_severity, MAX(severity) AS max_severity FROM alert_messages WHERE as_of_date_local >= date('now','-120 day') GROUP BY as_of_date_local ORDER BY as_of_date_local", 0, 8, 12, 8, unit="none", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Notifications and Success Ratio", "WITH daily AS (SELECT date(sent_at_utc) AS day, COUNT(*) AS sent_count, SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) AS success_count FROM alert_notifications WHERE sent_at_utc >= datetime('now','-120 day') GROUP BY date(sent_at_utc)) SELECT (day || 'T00:00:00Z') AS time, sent_count AS \"Notifications\", CASE WHEN sent_count=0 THEN NULL ELSE (success_count * 100.0 / sent_count) END AS \"Success %\" FROM daily ORDER BY day", 12, 8, 12, 8, unit="none", decimals=2)); i += 1
    p.append(timeseries_panel(i, "Reminder Frequency", "SELECT (as_of_date_local || 'T00:00:00Z') AS time, SUM(reminder_count) AS reminders FROM alert_messages WHERE as_of_date_local >= date('now','-120 day') GROUP BY as_of_date_local ORDER BY as_of_date_local", 0, 16, 12, 8, unit="none", decimals=0)); i += 1

    return "lmi-v2-g07-alert-trends.json", make_dashboard(
        uid="lmi-v2-g07-alert-trends",
        title="G07 LMI v2 - Alert Trends",
        tags=["lmi", "v2", "graph", "alerts"],
        panels=p,
    )


def write_dashboards() -> list[str]:
    dashboards = [
        d01_daily_command(),
        g01_portfolio_trajectory(),
        d02_holdings_risk_matrix(),
        g02_risk_tail_trends(),
        d03_income_calendar_reliability(),
        g03_income_yield_trends(),
        d04_margin_stress_desk(),
        g04_margin_stress_trends(),
        d05_period_scorecard(),
        g05_period_dynamics(),
        d06_period_interval_ledger(),
        d07_goals_tiers(),
        g06_goal_pace_trends(),
        d08_alerts_console(),
        g07_alert_trends(),
        d09_data_quality_guardrail(),
    ]

    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for filename, dashboard in dashboards:
        target_path = DASHBOARD_DIR / filename
        target_path.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
        written.append(str(target_path))

    return written


def main() -> int:
    written = write_dashboards()
    print("Wrote dashboards:")
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
