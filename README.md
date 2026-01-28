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

4) Stop:

```bash
docker compose down
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

1) Install realtime kernel and tools:

```bash
sudo apt-get update
sudo apt-get install -y linux-image-rt-amd64 rtkit
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
