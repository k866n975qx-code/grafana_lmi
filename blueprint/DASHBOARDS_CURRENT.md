# Current Grafana Dashboards (LMI v2 Reset)

Updated: 2026-03-04

## Hosted target
- Grafana host: `192.168.12.221`
- Grafana URL: `https://grafana.joseai.dev`
- Server repo path: `/home/jose/grafana_lmi`
- Provisioned dashboards: `/home/jose/grafana_lmi/grafana_lmi/dashboards`
- Provisioning config: `/home/jose/grafana_lmi/grafana_lmi/provisioning`
- SQLite DB path (container mount): `/var/lib/lmi/app.db`
- Datasource: `LMI SQLite` (uid `lmi_sqlite`)

## Dashboard inventory (16)

### Data-heavy
- `grafana_lmi/dashboards/lmi-v2-d01-daily-command-board.json` (`lmi-v2-d01-daily-command`)
- `grafana_lmi/dashboards/lmi-v2-d02-holdings-risk-matrix.json` (`lmi-v2-d02-holdings-risk`)
- `grafana_lmi/dashboards/lmi-v2-d03-income-calendar-reliability.json` (`lmi-v2-d03-income-calendar`)
- `grafana_lmi/dashboards/lmi-v2-d04-margin-stress-desk.json` (`lmi-v2-d04-margin-stress`)
- `grafana_lmi/dashboards/lmi-v2-d05-rolling-completed-scorecard.json` (`lmi-v2-d05-period-scorecard`)
- `grafana_lmi/dashboards/lmi-v2-d06-period-interval-activity-ledger.json` (`lmi-v2-d06-interval-ledger`)
- `grafana_lmi/dashboards/lmi-v2-d07-goals-tier-scenarios.json` (`lmi-v2-d07-goals-tiers`)
- `grafana_lmi/dashboards/lmi-v2-d08-alerts-console.json` (`lmi-v2-d08-alerts-console`)
- `grafana_lmi/dashboards/lmi-v2-d09-data-quality-guardrail.json` (`lmi-v2-d09-data-quality`)

### Graph
- `grafana_lmi/dashboards/lmi-v2-g01-portfolio-trajectory.json` (`lmi-v2-g01-portfolio-trajectory`)
- `grafana_lmi/dashboards/lmi-v2-g02-risk-tail-trends.json` (`lmi-v2-g02-risk-tail`)
- `grafana_lmi/dashboards/lmi-v2-g03-income-yield-trends.json` (`lmi-v2-g03-income-yield`)
- `grafana_lmi/dashboards/lmi-v2-g04-margin-stress-trends.json` (`lmi-v2-g04-margin-trends`)
- `grafana_lmi/dashboards/lmi-v2-g05-period-dynamics.json` (`lmi-v2-g05-period-dynamics`)
- `grafana_lmi/dashboards/lmi-v2-g06-goal-pace-trends.json` (`lmi-v2-g06-goal-pace`)
- `grafana_lmi/dashboards/lmi-v2-g07-alert-trends.json` (`lmi-v2-g07-alert-trends`)

## Mixed kiosk order
`D01, G01, D02, G02, D03, G03, D04, G04, D05, G05, D06, D07, G06, D08, G07, D09`

## Scripts
- `scripts/generate_v2_dashboards.py`
- `scripts/validate_v2_dashboards.sh`
- `scripts/backup_hosted_grafana.sh`
- `scripts/deploy_hosted_grafana.sh`
- `scripts/create_v2_playlist.sh`

## Notes
- This reset is hard-replace: legacy dashboard JSON files are removed from `grafana_lmi/dashboards`.
- A local point-in-time copy is kept under `grafana_lmi/dashboards.backup.<timestamp>/`.
- Playlist API currently uses a single interval per playlist.
