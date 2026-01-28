# embedded_hammond

Docker Compose setup to run setBfree with X11 UI and MIDI hotplug routing.

## Usage

1) Generate `.env` for your machine:

```bash
./create_env.sh
```

Edit `.env` if needed (USER_ID/GROUP_ID, XAUTHORITY path, group IDs).

2) Allow local X11 access (if needed):

```bash
xhost +si:localuser:$USER
```

3) Build and start:

```bash
docker compose up --build
```

The `ui-automation` service sends the `s` key once to switch to flat view.
If your window title differs, set `SETBFREE_WINDOW_NAME` in `.env`.
To auto-fullscreen in i3, set `SETBFREE_FULLSCREEN=1` and adjust
`SETBFREE_FULLSCREEN_KEY` if your i3 binding differs.

4) Stop:

```bash
docker compose down
```

If you want to autostart via i3, add this to your i3 config:

```text
exec --no-startup-id sh -lc 'cd ~/git/embedded_hammond && docker compose up -d'
```

## Debug

- Check container logs:

```bash
docker compose logs --tail=200 setbfree midi-hotplug
```

- List JACK ports in the setbfree container:

```bash
docker compose exec setbfree pw-jack jack_lsp -p
```

- Show current JACK connections:

```bash
docker compose exec setbfree pw-jack jack_lsp -c
```

- UI automation logs:

```bash
docker compose logs --tail=200 ui-automation
```

- If the UI does not show, re-check X11 auth and DISPLAY:

```bash
echo "$DISPLAY"
echo "$XAUTHORITY"
```

## Low latency and realtime setup

These steps are host-side and required for stable low-latency audio.

### Debian

Minimal setup for RT kernel + PipeWire JACK with fixed low-latency buffers.

1) Install realtime kernel and tools:

```bash
sudo apt-get update
sudo apt-get install -y linux-image-rt-amd64 rtkit pipewire pipewire-jack wireplumber alsa-utils
```

2) Add user to audio group:

```bash
sudo usermod -aG audio $USER
```

3) Realtime limits:

Create `/etc/security/limits.d/audio.conf`:

```text
@audio   -  rtprio     95
@audio   -  memlock    unlimited
```

4) Reboot and verify:

```bash
uname -r
```

5) Enable PipeWire user services:

```bash
systemctl --user enable --now pipewire pipewire-pulse wireplumber
```

6) Optional fixed latency (64/48k):

Create `~/.config/pipewire/pipewire.conf.d/10-lowlatency.conf`:

```ini
context.properties = {
    default.clock.rate = 48000
    default.clock.quantum = 64
    default.clock.min-quantum = 64
    default.clock.max-quantum = 64
}
```

Restart PipeWire:

```bash
systemctl --user restart pipewire pipewire-pulse wireplumber
```

7) Quick verification:

```bash
pw-jack jack_lsp
ulimit -r
ulimit -l
```

Troubleshooting tips:

- If `ulimit -l` is low, confirm your user is in `audio` group and you logged out/in.
- If you see xruns, increase `default.clock.quantum` to 128.
- If JACK apps cannot connect, verify PipeWire user services are running.

### Arch Linux

1) Install realtime kernel:

```bash
sudo pacman -S linux-rt linux-rt-headers
```

2) Add user to audio group:

```bash
sudo usermod -aG audio $USER
```

3) Realtime limits:

Create `/etc/security/limits.d/95-audio.conf`:

```text
@audio   -  rtprio     95
@audio   -  memlock    unlimited
```

4) Reboot and verify:

```bash
uname -r
```
