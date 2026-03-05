# LMI Switchboard (Local Backup Restore)

- **Hosted Grafana**: [https://grafana.joseai.dev](https://grafana.joseai.dev)
- **Server path**: `/home/jose/grafana_lmi`
- **Dashboards path**: `/home/jose/grafana_lmi/grafana_lmi/dashboards`
- **Datasource UID**: `lmi_sqlite`
- **Restored from local backup**: `grafana_lmi/dashboards.backup.20260304_195814`

## Core
1. **[LMI - Kiosk Surface](/d/lmi-kiosk-surface)**
2. **[LMI Overview](/d/lmi-overview)**
3. **[LMI - Daily Regime & Tail Risk](/d/lmi-daily-regime)**
4. **[LMI - Data Quality](/d/lmi-data-quality)**

## Holdings, Income, Risk
5. **[LMI - Holdings](/d/lmi-holdings)**
6. **[LMI - Income](/d/lmi-income)**
7. **[LMI - Dividend Calendar](/d/lmi-dividend-calendar)**
8. **[LMI - Income Stability](/d/lmi-income-stability)**
9. **[LMI - Margin Stress](/d/lmi-margin-stress)**
10. **[LMI - Risk KPIs](/d/lmi-risk-kpis)**
11. **[LMI - Risk Trends](/d/lmi-risk-trends)**
12. **[LMI - Macro Context](/d/lmi-macro-context)**
13. **[LMI - vs Benchmark](/d/lmi-vs-benchmark)**
14. **[LMI - Attribution](/d/lmi-attribution)**

## Goals
15. **[LMI - Goal Progress](/d/lmi-goal-progress)**
16. **[LMI - Goal Pace](/d/lmi-goal-pace)**
17. **[LMI - Goal Tiers](/d/lmi-goal-tiers)**

## Periods
18. **[LMI - Rolling Periods (WTD/MTD/QTD/YTD)](/d/lmi-rolling-periods)**
19. **[LMI - Rolling Detail](/d/lmi-rolling-detail)**
20. **[LMI - Latest Periods](/d/lmi-latest-periods)**
21. **[LMI - Period Performance](/d/lmi-period-performance)**
22. **[LMI - Period Interval Pro](/d/lmi-period-interval-pro)**
23. **[LMI - Period Macro & Rates](/d/lmi-period-macro)**
24. **[LMI - Period Drivers (Week/Month)](/d/lmi-period-drivers-short)**
25. **[LMI - Period Drivers (Quarter/Year)](/d/lmi-period-drivers-long)**

## Diffs
26. **[LMI - Diff (Daily Latest vs Previous)](/d/lmi-diff)**
27. **[LMI - Diff (WEEK vs Previous WEEK)](/d/lmi-diff-week)**
28. **[LMI - Diff (MONTH vs Previous MONTH)](/d/lmi-diff-month)**
29. **[LMI - Diff (QUARTER vs Previous QUARTER)](/d/lmi-diff-quarter)**
30. **[LMI - Diff (YEAR vs Previous YEAR)](/d/lmi-diff-year)**

## Deploy
1. Commit and push from local.
2. On server:
   - `cd /home/jose/grafana_lmi`
   - `git pull`
   - `docker restart grafana`
