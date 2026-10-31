#!/bin/sh
set -eu

repository_root="${REPOSITORY_ROOT:-/app/repositories}"
index_state_path="${INDEX_STATE_PATH:-/app/index_state}"
mkdir -p "$repository_root" "$index_state_path"
chown appuser:appuser "$repository_root" "$index_state_path"

if [ "${1:-}" = "uvicorn" ]; then
    exec gosu appuser "$@" --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-2}"
fi

exec gosu appuser "$@"
