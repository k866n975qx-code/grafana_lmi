#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DASH_DIR="$REPO_ROOT/grafana_lmi/dashboards"
DB_DEFAULT="$REPO_ROOT/../lmi-service/data/app.db"
DB_PATH="${1:-$DB_DEFAULT}"

if [[ ! -d "$DASH_DIR" ]]; then
  echo "Dashboards directory not found: $DASH_DIR" >&2
  exit 1
fi

if [[ ! -f "$DB_PATH" ]]; then
  echo "SQLite database not found: $DB_PATH" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 is required" >&2
  exit 1
fi

required_tables=$(cat <<'EOF'
daily_portfolio
daily_holdings
daily_dividends_upcoming
daily_goal_tiers
daily_margin_rate_scenarios
daily_return_attribution
period_summary
period_intervals
period_interval_holdings
period_interval_attribution
period_holding_changes
period_activity
period_position_lists
period_contributions
period_withdrawals
period_dividend_events
period_trades
period_macro_stats
period_risk_stats
period_margin_detail
alert_messages
alert_notifications
margin_balance_history
EOF
)

errors=0
query_count=0
seen_tables_file=$(mktemp)

while IFS= read -r f; do
  jq empty "$f" >/dev/null

  while IFS= read -r q; do
    [[ -z "$q" ]] && continue
    query_count=$((query_count + 1))

    echo "$q" | tr '\n' ' ' | sed 's/;/;\n/g' | rg -o "\b(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*)" -r '$1' | tr '[:upper:]' '[:lower:]' >> "$seen_tables_file"

    if ! sqlite3 "$DB_PATH" "PRAGMA busy_timeout=5000; EXPLAIN QUERY PLAN $q" >/dev/null 2>&1; then
      echo "SQL validation failed in $(basename "$f"):"
      echo "  $q"
      errors=$((errors + 1))
    fi
  done < <(jq -r '.. | objects | select(has("queryText")) | .queryText' "$f")
done < <(find "$DASH_DIR" -maxdepth 1 -type f -name 'lmi-v2-*.json' | sort)

sort -u "$seen_tables_file" -o "$seen_tables_file"

missing=0
while IFS= read -r t; do
  [[ -z "$t" ]] && continue
  if ! grep -qx "$t" "$seen_tables_file"; then
    echo "Missing table coverage: $t"
    missing=$((missing + 1))
  fi
done <<< "$required_tables"

rm -f "$seen_tables_file"

echo "Validated queries: $query_count"
echo "SQL errors: $errors"
echo "Missing required tables: $missing"

if [[ $errors -ne 0 || $missing -ne 0 ]]; then
  exit 1
fi

echo "Validation passed."
