#!/usr/bin/env bash
# Launch, check, and stop the Company Brain verification instance.
# Kills only processes recorded in the state directory.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
STATE="${CEO_VERIFY_STATE_DIR:-/tmp/ceo-verify}"
API_HOST="127.0.0.1"
API_PORT="8000"
WEB_HOST="127.0.0.1"
WEB_PORT="3000"
API_URL="http://${API_HOST}:${API_PORT}"
WEB_URL="http://${WEB_HOST}:${WEB_PORT}"
ARTIFACTS="${ROOT}/.cursor/skills/verify-company-brain/artifacts"

export PATH="${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

usage() {
  cat <<EOF
Usage: verify.sh <launch|doctor|cleanup|paths>

  launch   Start the API and web console, or refuse if a port is taken.
  doctor   Read-only check that this run's instance is the one listening.
  cleanup  Stop the processes this script started and remove ${STATE}.
  paths    Print the URLs, state directory, and evidence directory.
EOF
}

port_pid() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true
}

read_pid() {
  local file="$1"
  if [[ -f "$file" ]]; then
    tr -d '[:space:]' <"$file"
  fi
}

pid_alive() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

in_tree() {
  local root="$1"
  local current="$2"
  while [[ -n "$current" && "$current" != "0" && "$current" != "1" ]]; do
    if [[ "$current" == "$root" ]]; then
      return 0
    fi
    current="$(ps -o ppid= -p "$current" 2>/dev/null | tr -d '[:space:]' || true)"
  done
  return 1
}

stop_recorded() {
  local pid="$1"
  if ! pid_alive "$pid"; then
    return 0
  fi
  local pgid
  pgid="$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d '[:space:]' || true)"
  if [[ -n "$pgid" && "$pgid" == "$pid" ]]; then
    kill -TERM -"$pgid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  else
    kill -TERM "$pid" 2>/dev/null || true
  fi
  local _i
  for _i in 1 2 3 4 5 6 7 8 9 10; do
    pid_alive "$pid" || return 0
    sleep 0.2
  done
  if [[ -n "$pgid" && "$pgid" == "$pid" ]]; then
    kill -KILL -"$pgid" 2>/dev/null || true
  fi
  kill -KILL "$pid" 2>/dev/null || true
}

health_ok() {
  local body="$1"
  [[ "$body" == *'"status":"ok"'* || "$body" == *'"status": "ok"'* ]]
}

wait_ready() {
  local i health home api_pid web_pid
  api_pid="$(read_pid "${STATE}/api.pid")"
  web_pid="$(read_pid "${STATE}/web.pid")"
  for i in $(seq 1 90); do
    if ! pid_alive "$api_pid" || ! pid_alive "$web_pid"; then
      echo "verification process exited before the pages were usable" >&2
      break
    fi
    health="$(curl -sf "${API_URL}/health" || true)"
    home="$(curl -sf "${WEB_URL}/" || true)"
    if health_ok "$health" && [[ "$home" == *"Control plane"* ]]; then
      return 0
    fi
    sleep 1
  done
  echo "timed out waiting for ${API_URL}/health and a home page that contains 'Control plane'" >&2
  echo "--- api log ---" >&2
  tail -n 50 "${STATE}/api.log" >&2 || true
  echo "--- web log ---" >&2
  tail -n 50 "${STATE}/web.log" >&2 || true
  return 1
}

cmd_paths() {
  printf 'web_url=%s\n' "$WEB_URL"
  printf 'api_url=%s\n' "$API_URL"
  printf 'state_dir=%s\n' "$STATE"
  printf 'artifacts_dir=%s\n' "$ARTIFACTS"
}

cmd_cleanup() {
  local api_pid web_pid
  api_pid="$(read_pid "${STATE}/api.pid")"
  web_pid="$(read_pid "${STATE}/web.pid")"
  stop_recorded "$web_pid"
  stop_recorded "$api_pid"
  rm -rf "$STATE"
  echo "stopped verification instance; evidence kept in ${ARTIFACTS}"
}

cmd_doctor() {
  local api_pid web_pid api_listen web_listen health home
  api_pid="$(read_pid "${STATE}/api.pid")"
  web_pid="$(read_pid "${STATE}/web.pid")"
  if ! pid_alive "$api_pid" || ! pid_alive "$web_pid"; then
    echo "doctor: no live verification instance in ${STATE}" >&2
    exit 1
  fi
  api_listen="$(port_pid "$API_PORT")"
  web_listen="$(port_pid "$WEB_PORT")"
  if ! in_tree "$api_pid" "$api_listen"; then
    echo "doctor: ${API_URL} is owned by pid ${api_listen:-none}, not verification pid ${api_pid}" >&2
    exit 1
  fi
  if ! in_tree "$web_pid" "$web_listen"; then
    echo "doctor: ${WEB_URL} is owned by pid ${web_listen:-none}, not verification pid ${web_pid}" >&2
    exit 1
  fi
  health="$(curl -sf "${API_URL}/health" || true)"
  home="$(curl -sf "${WEB_URL}/" || true)"
  if ! health_ok "$health"; then
    echo "doctor: ${API_URL}/health returned: ${health:-<empty>}" >&2
    exit 1
  fi
  if [[ "$home" != *"Control plane"* ]]; then
    echo "doctor: ${WEB_URL}/ did not contain 'Control plane'" >&2
    exit 1
  fi
  printf 'web_url=%s\n' "$WEB_URL"
  printf 'api_url=%s\n' "$API_URL"
  printf 'api_pid=%s\n' "$api_pid"
  printf 'web_pid=%s\n' "$web_pid"
  printf 'api_listen_pid=%s\n' "$api_listen"
  printf 'web_listen_pid=%s\n' "$web_listen"
  printf 'api_health=%s\n' "$health"
  printf 'web_ready=Control plane\n'
  printf 'state_dir=%s\n' "$STATE"
}

cmd_launch() {
  local api_pid web_pid
  if [[ ! -x "${ROOT}/.venv/bin/python" ]]; then
    echo "launch: missing ${ROOT}/.venv. Run 'uv sync --all-packages' from the repo root." >&2
    exit 1
  fi
  if [[ ! -x "${ROOT}/apps/web/node_modules/.bin/next" ]]; then
    echo "launch: missing apps/web/node_modules. Run 'pnpm install' from the repo root." >&2
    exit 1
  fi
  api_pid="$(read_pid "${STATE}/api.pid")"
  web_pid="$(read_pid "${STATE}/web.pid")"
  if pid_alive "$api_pid" || pid_alive "$web_pid"; then
    echo "launch: a verification instance is already running in ${STATE}; refusing to start another" >&2
    exit 1
  fi
  rm -rf "$STATE"
  local port owner
  for port in "$API_PORT" "$WEB_PORT"; do
    owner="$(port_pid "$port")"
    if [[ -n "$owner" ]]; then
      echo "launch: port ${port} is already owned by pid ${owner}; refusing to start a second instance" >&2
      exit 1
    fi
  done
  mkdir -p "$STATE" "$ARTIFACTS"
  cat >"${STATE}/run-api.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}"
exec uv run uvicorn ceo_api.main:app --host ${API_HOST} --port ${API_PORT} --log-level info
EOF
  cat >"${STATE}/run-web.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${ROOT}/apps/web"
exec ./node_modules/.bin/next dev --hostname ${WEB_HOST} --port ${WEB_PORT}
EOF
  chmod +x "${STATE}/run-api.sh" "${STATE}/run-web.sh"
  python3 -c 'import os,sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
    "${STATE}/run-api.sh" >"${STATE}/api.log" 2>&1 &
  echo $! >"${STATE}/api.pid"
  python3 -c 'import os,sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
    "${STATE}/run-web.sh" >"${STATE}/web.log" 2>&1 &
  echo $! >"${STATE}/web.pid"
  if ! wait_ready; then
    cmd_cleanup >/dev/null
    exit 1
  fi
  cmd_doctor
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    launch) cmd_launch ;;
    doctor) cmd_doctor ;;
    cleanup) cmd_cleanup ;;
    paths) cmd_paths ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
