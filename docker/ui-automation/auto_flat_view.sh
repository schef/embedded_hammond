#!/usr/bin/env sh
set -e

window_name="${SETBFREE_WINDOW_NAME:-setBfree}"
retries="${SETBFREE_AUTOMATION_RETRIES:-50}"
interval="${SETBFREE_AUTOMATION_INTERVAL:-0.2}"
fullscreen="${SETBFREE_FULLSCREEN:-0}"
fullscreen_key="${SETBFREE_FULLSCREEN_KEY:-Super+f}"

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
  window_id=$(xdotool search --name "${window_name}" 2>/dev/null | head -n 1)
  if [ -n "${window_id}" ]; then
    echo "[ui-automation] setBfree window found, sending 's'"
    xdotool windowactivate --sync "${window_id}"
    xdotool key s
    if [ "${fullscreen}" = "1" ]; then
      echo "[ui-automation] sending fullscreen key ${fullscreen_key}"
      xdotool key "${fullscreen_key}"
    fi
    exit 0
  fi
  attempt=$((attempt + 1))
  sleep "${interval}"
done

echo "[ui-automation] window not found after ${retries} attempts"
exit 1
