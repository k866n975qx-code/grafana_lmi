# LMI Grafana starter (SQLite)

This runs Grafana with the SQLite datasource plugin and mounts your `lmi-service` DB (`app.db`) read-only.

## Quick start

1) Edit `docker-compose.yml` and set the DB path mount.

2) Start Grafana:

```bash
docker compose up -d
```

3) Open http://<server-ip>:3000
- login: admin / admin (Grafana forces a password change)

The datasource is provisioned as **LMI SQLite**.

## Panels to add (suggested)

Create a new dashboard and add panels using these SQL queries.

### Portfolio stats (Stat panel)
**Market value (latest)**
```sql
SELECT json_extract(payload_json,'$.totals.market_value') AS value
FROM snapshot_daily_current
ORDER BY as_of_date_local DESC
LIMIT 1;
```

**Margin loan balance (latest)**
```sql
SELECT json_extract(payload_json,'$.totals.margin_loan_balance') AS value
FROM snapshot_daily_current
ORDER BY as_of_date_local DESC
LIMIT 1;
```

## Panels to add (suggested)

Create a new dashboard and add panels using these SQL queries.

### Portfolio stats (Stat panel)

Market value (latest)
```sql
SELECT json_extract(payload_json,'$.totals.market_value') AS value
FROM snapshot_daily_current
ORDER BY as_of_date_local DESC
LIMIT 1;
```

Margin loan balance (latest)
```sql
SELECT json_extract(payload_json,'$.totals.margin_loan_balance') AS value
FROM snapshot_daily_current
ORDER BY as_of_date_local DESC
LIMIT 1;
```

Margin to portfolio % (latest)
```sql
SELECT json_extract(payload_json,'$.totals.margin_to_portfolio_pct') AS value
FROM snapshot_daily_current
ORDER BY as_of_date_local DESC
LIMIT 1;
```

Projected monthly income (latest)
```sql
SELECT json_extract(payload_json,'$.income.projected_monthly_income') AS value
FROM snapshot_daily_current
ORDER BY as_of_date_local DESC
LIMIT 1;
```

### Portfolio over time (Time series panel)

Market value over time (90d range controlled by dashboard time picker)
```sql
SELECT
  as_of_date_local AS time,
  json_extract(payload_json,'$.totals.market_value') AS market_value
FROM snapshot_daily_current
WHERE $__timeFilter(as_of_date_local)
ORDER BY as_of_date_local;
```

If your plugin build doesn't support `__$timeFilter`, replace the `WHERE` with a fixed window, e.g.:
```sql
WHERE as_of_date_local >= date('now','-90 day')
```

### Portfolio over time (Time series panel)

Market value over time
```sql
SELECT
  as_of_date_local AS time,
  json_extract(payload_json,'$.totals.market_value') AS market_value
FROM snapshot_daily_current
WHERE $__timeFilter(as_of_date_local)
ORDER BY as_of_date_local;
```

(If `__$timeFilter` is unavailable)
```sql
SELECT
  as_of_date_local AS time,
  json_extract(payload_json,'$.totals.market_value') AS market_value
FROM snapshot_daily_current
WHERE as_of_date_local >= date('now','-90 day')
ORDER BY as_of_date_local;
```

### Holdings table (Table panel)

Top holdings by market value (latest snapshot)
```sql
WITH latest AS (
  SELECT payload_json
  FROM snapshot_daily_current
  ORDER BY as_of_date_local DESC
  LIMIT 1
)
SELECT
  json_extract(j.value,'$.symbol') AS symbol,
  json_extract(j.value,'$.weight_pct') AS weight_pct,
  json_extract(j.value,'$.market_value') AS market_value,
  json_extract(j.value,'$.current_yield_pct') AS current_yield_pct,
  json_extract(j.value,'$.projected_monthly_dividend') AS projected_monthly_dividend
FROM latest, json_each(latest.payload_json,'$.holdings') AS j
ORDER BY market_value DESC;
```

### Holdings table (Table panel)

Top holdings by market value (latest snapshot)
```sql
WITH latest AS (
  SELECT payload_json
  FROM snapshot_daily_current
  ORDER BY as_of_date_local DESC
  LIMIT 1
)
SELECT
  json_extract(j.value,'$.symbol') AS symbol,
  json_extract(j.value,'$.weight_pct') AS weight_pct,
  json_extract(j.value,'$.market_value') AS market_value,
  json_extract(j.value,'$.current_yield_pct') AS current_yield_pct
FROM latest, json_each(latest.payload_json,'$.holdings') j
ORDER BY market_value DESC;
```

### Holdings table (Table panel)

Top holdings by market value (latest snapshot)
```sql
WITH latest AS (
  SELECT payload_json
  FROM snapshot_daily_current
  ORDER BY as_of_date_local DESC
  LIMIT 1
)
SELECT
  json_extract(j.value,'$.symbol') AS symbol,
  json_extract(j.value,'$.weight_pct') AS weight_pct,
  json_extract(j.value,'$.market_value') AS market_value
FROM latest, json_each(latest.payload_json,'$.holdings') j
ORDER BY market_value DESC;
```

### Holdings table (Table panel)

Top holdings by market value (latest snapshot)
```sql
WITH latest AS (
  SELECT payload_json
  FROM snapshot_daily_current
  ORDER BY as_of_date_local DESC
  LIMIT 1
)
SELECT
  json_extract(j.value,'$.symbol') AS symbol,
  json_extract(j.value,'$.weight_pct') AS weight_pct,
  json_extract(j.value,'$.market_value') AS market_value
FROM latest, json_each(latest.payload_json,'$.holdings') j
ORDER BY market_value DESC;
```
