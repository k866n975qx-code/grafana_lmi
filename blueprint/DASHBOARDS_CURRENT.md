# Current Grafana Dashboards (LMI v2 Compact)

Updated: 2026-03-04

## Hosted target
- Grafana host: `192.168.12.221`
- Grafana URL: `https://grafana.joseai.dev`
- Server repo path: `/home/jose/grafana_lmi`
- Provisioned dashboards: `/home/jose/grafana_lmi/grafana_lmi/dashboards`
- Provisioning config: `/home/jose/grafana_lmi/grafana_lmi/provisioning`
- SQLite DB path (container mount): `/var/lib/lmi/app.db`
- Datasource: `LMI SQLite` (uid `lmi_sqlite`)

## Design guarantees
- Timeseries panels use explicit `time_series` target format with epoch `time` field.
- Compact kiosk layout target: max dashboard height `14` grid units.
- Table panels are trimmed to compact column sets and low row limits to avoid panel scroll.

## Dashboard inventory (23)

### Data-heavy (12)
- `lmi-v2-d01-daily-command-board.json` (`lmi-v2-d01-daily-command`)
- `lmi-v2-d02-holdings-risk-matrix.json` (`lmi-v2-d02-holdings-risk`)
- `lmi-v2-d03-income-calendar-reliability.json` (`lmi-v2-d03-income-calendar`)
- `lmi-v2-d04-margin-stress-desk.json` (`lmi-v2-d04-margin-stress`)
- `lmi-v2-d05-rolling-completed-scorecard.json` (`lmi-v2-d05-period-scorecard`)
- `lmi-v2-d06-period-interval-activity-ledger.json` (`lmi-v2-d06-interval-ledger`)
- `lmi-v2-d07-goals-tier-scenarios.json` (`lmi-v2-d07-goals-tiers`)
- `lmi-v2-d08-alerts-console.json` (`lmi-v2-d08-alerts-console`)
- `lmi-v2-d09-data-quality-guardrail.json` (`lmi-v2-d09-data-quality`)
- `lmi-v2-d10-period-activity-flows.json` (`lmi-v2-d10-period-activity`)
- `lmi-v2-d11-period-positions-dividends.json` (`lmi-v2-d11-period-positions`)
- `lmi-v2-d12-period-macro-risk.json` (`lmi-v2-d12-period-macro-risk`)

### Graph (11)
- `lmi-v2-g01-portfolio-trajectory.json` (`lmi-v2-g01-portfolio-trajectory`)
- `lmi-v2-g02-risk-tail-trends.json` (`lmi-v2-g02-risk-tail`)
- `lmi-v2-g03-income-yield-trends.json` (`lmi-v2-g03-income-yield`)
- `lmi-v2-g04-margin-stress-trends.json` (`lmi-v2-g04-margin-trends`)
- `lmi-v2-g05-period-dynamics.json` (`lmi-v2-g05-period-dynamics`)
- `lmi-v2-g06-goal-pace-trends.json` (`lmi-v2-g06-goal-pace`)
- `lmi-v2-g07-alert-trends.json` (`lmi-v2-g07-alert-trends`)
- `lmi-v2-g08-performance-trends.json` (`lmi-v2-g08-performance-trends`)
- `lmi-v2-g09-macro-risk-period-trends.json` (`lmi-v2-g09-macro-risk-period`)
- `lmi-v2-g10-income-stability-trends.json` (`lmi-v2-g10-income-stability`)
- `lmi-v2-g11-benchmark-concentration-trends.json` (`lmi-v2-g11-benchmark-concentration`)

## Validation snapshot
- Query count: `120`
- SQL parse errors: `0`
- Required table coverage: complete
