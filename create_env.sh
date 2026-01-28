#!/usr/bin/env bash
set -euo pipefail

user_id="$(id -u)"
group_id="$(id -g)"
audio_gid="$(getent group audio | cut -d: -f3)"
video_gid="$(getent group video | cut -d: -f3)"
xauthority="${XAUTHORITY:-$HOME/.Xauthority}"

if [ -z "${audio_gid}" ]; then
  audio_gid=""
fi

if [ -z "${video_gid}" ]; then
  video_gid="$(getent group render | cut -d: -f3)"
fi

cat > .env <<EOF
USER_ID=${user_id}
GROUP_ID=${group_id}
AUDIO_GID=${audio_gid}
VIDEO_GID=${video_gid}
XAUTHORITY=${xauthority}
PIPEWIRE_LATENCY=64/48000
SETBFREE_MATCH=setBfree
MIDI_CLIENT_EXCLUDE=System,Midi Through
EOF

printf "Wrote .env with USER_ID=%s GROUP_ID=%s\n" "${user_id}" "${group_id}"
