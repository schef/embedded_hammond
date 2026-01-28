#!/usr/bin/env sh
set -e

window_name="${SETBFREE_WINDOW_NAME:-setBfree}"
retries="${SETBFREE_AUTOMATION_RETRIES:-50}"
interval="${SETBFREE_AUTOMATION_INTERVAL:-0.2}"

if [ -z "${DISPLAY:-}" ]; then
  echo "[ui-automation] DISPLAY is not set"
  exit 1
fi

if [ ! -f "${XAUTHORITY:-}" ]; then
  echo "[ui-automation] XAUTHORITY not found: ${XAUTHORITY:-}"
  exit 1
fi

attempt=0
while [ "${attempt}" -lt "${retries}" ]; do
  if xdotool search --name "${window_name}" >/dev/null 2>&1; then
    echo "[ui-automation] setBfree window found, sending 's'"
    xdotool key s
    exit 0
  fi
  attempt=$((attempt + 1))
  sleep "${interval}"
done

echo "[ui-automation] window not found after ${retries} attempts"
exit 1
