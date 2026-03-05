#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

GRAFANA_BASE_URL=${GRAFANA_BASE_URL:-"https://grafana.joseai.dev"}
GRAFANA_USER=${GRAFANA_USER:-"admin"}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-""}
PLAYLIST_NAME=${PLAYLIST_NAME:-"LMI v2 Mixed Kiosk"}
PLAYLIST_INTERVAL=${PLAYLIST_INTERVAL:-"30s"}

if [[ -z "$GRAFANA_PASSWORD" ]]; then
  echo "GRAFANA_PASSWORD is required." >&2
  exit 1
fi

uids=(
  lmi-v2-d01-daily-command
  lmi-v2-g01-portfolio-trajectory
  lmi-v2-d02-holdings-risk
  lmi-v2-g02-risk-tail
  lmi-v2-d03-income-calendar
  lmi-v2-g03-income-yield
  lmi-v2-d04-margin-stress
  lmi-v2-g04-margin-trends
  lmi-v2-d05-period-scorecard
  lmi-v2-g05-period-dynamics
  lmi-v2-d06-interval-ledger
  lmi-v2-d07-goals-tiers
  lmi-v2-g06-goal-pace
  lmi-v2-d08-alerts-console
  lmi-v2-g07-alert-trends
  lmi-v2-d09-data-quality
)

tmp_items=$(mktemp)
printf '[]' > "$tmp_items"
order=1
for uid in "${uids[@]}"; do
  resp=$(curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/dashboards/uid/$uid")
  dash_id=$(echo "$resp" | jq -r '.dashboard.id')
  dash_title=$(echo "$resp" | jq -r '.dashboard.title')

  if [[ -z "$dash_id" || "$dash_id" == "null" ]]; then
    echo "Dashboard not found or missing id for uid: $uid" >&2
    rm -f "$tmp_items"
    exit 1
  fi

  jq \
    --arg type "dashboard_by_id" \
    --arg value "$dash_id" \
    --arg title "$dash_title" \
    --argjson order "$order" \
    '. += [{type: $type, value: $value, order: $order, title: $title}]' \
    "$tmp_items" > "$tmp_items.new"
  mv "$tmp_items.new" "$tmp_items"

  order=$((order + 1))
done

payload=$(jq -n \
  --arg name "$PLAYLIST_NAME" \
  --arg interval "$PLAYLIST_INTERVAL" \
  --argjson items "$(cat "$tmp_items")" \
  '{name: $name, interval: $interval, items: $items}')

playlist_id=$(curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/playlists" | jq -r --arg n "$PLAYLIST_NAME" '.[] | select(.name==$n) | .id' | head -n1)

if [[ -n "$playlist_id" ]]; then
  echo "Updating existing playlist id=$playlist_id ..."
  result=$(curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -H 'Content-Type: application/json' -X PUT "$GRAFANA_BASE_URL/api/playlists/$playlist_id" -d "$payload")
else
  echo "Creating new playlist..."
  result=$(curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" -H 'Content-Type: application/json' -X POST "$GRAFANA_BASE_URL/api/playlists" -d "$payload")
fi

rm -f "$tmp_items"

new_id=$(echo "$result" | jq -r '.id // empty')
new_uid=$(echo "$result" | jq -r '.uid // empty')
url_path=$(echo "$result" | jq -r '.url // empty')

echo "Playlist ready."
echo "ID:  $new_id"
echo "UID: $new_uid"
if [[ -n "$url_path" ]]; then
  echo "URL: $GRAFANA_BASE_URL$url_path?kiosk=true&autofitpanels=true"
else
  echo "URL: $GRAFANA_BASE_URL/playlists"
fi

echo "Note: Grafana playlist API supports a single interval per playlist; set to $PLAYLIST_INTERVAL."
