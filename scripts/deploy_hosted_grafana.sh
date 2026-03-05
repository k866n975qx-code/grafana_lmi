#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

BRANCH=${BRANCH:-$(git -C "$REPO_ROOT" branch --show-current)}
SERVER=${SERVER:-"jose@192.168.12.221"}
REMOTE_REPO=${REMOTE_REPO:-"/home/jose/grafana_lmi"}

SKIP_PUSH=${SKIP_PUSH:-0}

if [[ "$SKIP_PUSH" != "1" ]]; then
  echo "Pushing local branch '$BRANCH' to origin..."
  git -C "$REPO_ROOT" push origin "$BRANCH"
else
  echo "SKIP_PUSH=1 set, skipping git push."
fi

echo "Deploying on $SERVER..."
ssh "$SERVER" "set -euo pipefail; \
  cd '$REMOTE_REPO'; \
  git fetch origin; \
  git checkout '$BRANCH'; \
  git pull --ff-only origin '$BRANCH'; \
  docker restart grafana >/dev/null; \
  echo 'grafana restarted'"

echo "Deployment complete."
