#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
env_file="${script_dir}/.env"

if [ -f "${env_file}" ]; then
  set -a
  # shellcheck disable=SC1090
  . "${env_file}"
  set +a
fi

display="${DISPLAY:-:0}"
xauth="${XAUTHORITY:-$HOME/.Xauthority}"
runtime_dir="/run/user/${USER_ID:-$(id -u)}"
pipewire_sock="${runtime_dir}/pipewire-0"

until [ -S "${pipewire_sock}" ]; do
  sleep 1
done

until [ -f "${xauth}" ]; do
  sleep 1
done

cd "${script_dir}"
DISPLAY="${display}" XAUTHORITY="${xauth}" docker compose up -d

while true; do
  if ! docker compose ps --status running --services | grep -q '^setbfree$'; then
    DISPLAY="${display}" XAUTHORITY="${xauth}" docker compose up -d
  fi
  sleep 5
done
