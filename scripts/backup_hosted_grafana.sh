#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
TS=${TS:-$(date +%Y%m%d_%H%M%S)}

SERVER=${SERVER:-"jose@192.168.12.221"}
REMOTE_REPO=${REMOTE_REPO:-"/home/jose/grafana_lmi"}
REMOTE_STACK_DIR=${REMOTE_STACK_DIR:-"$REMOTE_REPO/grafana_lmi"}
REMOTE_BACKUP_DIR="$REMOTE_REPO/backups/$TS"

GRAFANA_BASE_URL=${GRAFANA_BASE_URL:-"https://grafana.joseai.dev"}
GRAFANA_USER=${GRAFANA_USER:-"admin"}
GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-""}

LOCAL_BACKUP_DIR="$REPO_ROOT/backups/$TS"
LOCAL_API_DIR="$LOCAL_BACKUP_DIR/api"
mkdir -p "$LOCAL_API_DIR/dashboards" "$LOCAL_API_DIR/playlists"

commit_hash=$(git -C "$REPO_ROOT" rev-parse HEAD)
tag_name="backup/lmi-v2-reset-$TS"

if git -C "$REPO_ROOT" rev-parse "$tag_name" >/dev/null 2>&1; then
  echo "Tag already exists: $tag_name"
else
  git -C "$REPO_ROOT" tag "$tag_name" "$commit_hash"
  echo "Created git tag: $tag_name"
fi

echo "Creating remote backup on $SERVER..."
ssh "$SERVER" "set -euo pipefail; \
  mkdir -p '$REMOTE_BACKUP_DIR'; \
  cp -a '$REMOTE_STACK_DIR/dashboards' '$REMOTE_BACKUP_DIR/dashboards'; \
  cp -a '$REMOTE_STACK_DIR/provisioning' '$REMOTE_BACKUP_DIR/provisioning'; \
  tar -C '$REMOTE_BACKUP_DIR' -czf '$REMOTE_BACKUP_DIR/provisioning_dashboards.tgz' dashboards provisioning"

remote_grafana_db="$REMOTE_BACKUP_DIR/grafana.db"
if ssh "$SERVER" "docker cp grafana:/var/lib/grafana/grafana.db '$remote_grafana_db'" >/dev/null 2>&1; then
  echo "Backed up grafana.db to $remote_grafana_db"
else
  echo "Skipped grafana.db backup (container/path unavailable)."
fi

api_backup_status="skipped"
if [[ -n "$GRAFANA_PASSWORD" ]]; then
  echo "Exporting dashboards/playlists via Grafana API..."
  set +e
  curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/search?type=dash-db&limit=5000" -o "$LOCAL_API_DIR/search_dashboards.json"
  rc=$?
  set -e

  if [[ $rc -eq 0 ]]; then
    api_backup_status="ok"
    while IFS= read -r uid; do
      [[ -z "$uid" ]] && continue
      curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/dashboards/uid/$uid" -o "$LOCAL_API_DIR/dashboards/$uid.json"
    done < <(jq -r '.[].uid // empty' "$LOCAL_API_DIR/search_dashboards.json")

    curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/playlists" -o "$LOCAL_API_DIR/playlists/index.json"
    while IFS= read -r pid; do
      [[ -z "$pid" ]] && continue
      curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/playlists/$pid" -o "$LOCAL_API_DIR/playlists/$pid.json"
      curl -fsS -u "$GRAFANA_USER:$GRAFANA_PASSWORD" "$GRAFANA_BASE_URL/api/playlists/$pid/items" -o "$LOCAL_API_DIR/playlists/$pid.items.json"
    done < <(jq -r '.[].id // empty' "$LOCAL_API_DIR/playlists/index.json")
  else
    api_backup_status="failed"
    echo "Grafana API export failed (check GRAFANA_USER/GRAFANA_PASSWORD)."
  fi
else
  echo "Skipping Grafana API export (GRAFANA_PASSWORD not set)."
fi

manifest="$LOCAL_BACKUP_DIR/backup-manifest.txt"
cat > "$manifest" <<EOF
Timestamp: $TS
Commit: $commit_hash
Git tag: $tag_name
Server: $SERVER
Remote repo: $REMOTE_REPO
Remote backup dir: $REMOTE_BACKUP_DIR
Remote archive: $REMOTE_BACKUP_DIR/provisioning_dashboards.tgz
Remote grafana.db: $remote_grafana_db
Grafana URL: $GRAFANA_BASE_URL
API export status: $api_backup_status
Local API backup dir: $LOCAL_API_DIR
EOF

echo "Backup complete."
echo "Remote backup dir: $REMOTE_BACKUP_DIR"
echo "Local backup dir:  $LOCAL_BACKUP_DIR"
echo "Manifest:          $manifest"
