# LMI v3 Switchboard

- **Hosted Grafana**: [https://grafana.joseai.dev](https://grafana.joseai.dev)
- **Server path**: `/home/jose/grafana_lmi`
- **Dashboards path**: `/home/jose/grafana_lmi/grafana_lmi/dashboards`
- **Datasource UID**: `lmi_sqlite`

## Blended Core
1. **[B01 Command Center](/d/lmi-v3-b01-command-center)**
2. **[B02 Income and Dividends](/d/lmi-v3-b02-income-dividends)**
3. **[B03 Holdings and Risk](/d/lmi-v3-b03-holdings-risk)**
4. **[B04 Margin and Stress](/d/lmi-v3-b04-margin-stress)**
5. **[B05 Goals and Pace](/d/lmi-v3-b05-goals-pace)**
6. **[B06 Alerts and Data Quality](/d/lmi-v3-b06-alerts-quality)**
7. **[B07 Macro and Benchmark](/d/lmi-v3-b07-macro-benchmark)**
8. **[B08 Period Activity](/d/lmi-v3-b08-period-activity)**
9. **[B09 Period Intervals](/d/lmi-v3-b09-period-intervals)**
10. **[B10 Period Attribution](/d/lmi-v3-b10-period-attribution)**

## Period Mode Overviews
11. **[R01 Rolling Overview](/d/lmi-v3-r01-rolling-overview)**
12. **[C01 Completed Overview](/d/lmi-v3-c01-completed-overview)**

## Diff Dashboards
13. **[D01 Diff Daily](/d/lmi-v3-d01-diff-daily)**
14. **[D02 Diff Week](/d/lmi-v3-d02-diff-week)**
15. **[D03 Diff Month](/d/lmi-v3-d03-diff-month)**
16. **[D04 Diff Quarter](/d/lmi-v3-d04-diff-quarter)**
17. **[D05 Diff Year](/d/lmi-v3-d05-diff-year)**
18. **[D06 Rolling vs Completed Gap](/d/lmi-v3-d06-rolling-vs-completed-gap)**

## Deploy (Git-First)
1. Commit and push from local.
2. On server:
   - `cd /home/jose/grafana_lmi`
   - `git pull`
   - `docker restart grafana`

## Kiosk URL Format
- `https://grafana.joseai.dev/d/<dashboard_uid>?kiosk=true&autofitpanels=true`
