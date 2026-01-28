#!/usr/bin/env python3
import os
import subprocess
import time

import pyudev


def run_command(args):
    return subprocess.run(args, check=False, text=True, capture_output=True)


def get_jack_ports():
    result = run_command(["pw-jack", "jack_lsp", "-pt"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "jack_lsp failed")

    ports = {}
    current_port = None
    for line in result.stdout.splitlines():
        if not line[:1].isspace() and line.strip():
            current_port = line.strip()
            ports[current_port] = {"properties": set(), "type": ""}
            continue
        if current_port is None:
            continue
        stripped = line.strip()
        if stripped.startswith("properties:"):
            props = stripped.split(":", 1)[1].strip()
            ports[current_port]["properties"].update(
                {p.strip() for p in props.split(",") if p.strip()}
            )
            continue
        if stripped and not ports[current_port]["type"]:
            ports[current_port]["type"] = stripped
    return ports


def get_jack_connections():
    result = run_command(["pw-jack", "jack_lsp", "-c"])
    if result.returncode != 0:
        return set()
    connections = set()
    current_port = None
    for line in result.stdout.splitlines():
        if not line[:1].isspace() and line.strip():
            current_port = line.strip()
            continue
        if current_port is None:
            continue
        target = line.strip()
        if target:
            connections.add((current_port, target))
    return connections


def is_midi_port(port_info):
    return "midi" in port_info.get("type", "").lower()


def is_audio_port(port_info):
    return "audio" in port_info.get("type", "").lower()


def find_setbfree_inputs(ports, match_text):
    match_text = match_text.lower()
    inputs = []
    for name, info in ports.items():
        if (
            match_text in name.lower()
            and "input" in info["properties"]
            and is_midi_port(info)
        ):
            inputs.append(name)
    return inputs


def list_source_ports(ports, exclude_clients):
    sources = []
    for name, info in ports.items():
        client = name.split(":", 1)[0]
        if client.lower() in exclude_clients:
            continue
        if "output" in info["properties"] and is_midi_port(info):
            sources.append(name)
    return sources


def find_setbfree_audio_outputs(ports):
    left = None
    right = None
    for name, info in ports.items():
        if "setbfree" not in name.lower():
            continue
        if "output" not in info["properties"] or not is_audio_port(info):
            continue
        lower = name.lower()
        if "outl" in lower:
            left = name
        elif "outr" in lower:
            right = name
    return left, right


def find_physical_playback_ports(ports):
    playback = []
    for name, info in ports.items():
        if "input" not in info["properties"]:
            continue
        if "physical" not in info["properties"]:
            continue
        if not is_audio_port(info):
            continue
        playback.append(name)

    preferred = [p for p in playback if "playback_fl" in p.lower()]
    preferred += [p for p in playback if "playback_fr" in p.lower()]
    if len(preferred) >= 2:
        return preferred[:2]

    return playback[:2]


def connect_audio(ports, connections):
    left, right = find_setbfree_audio_outputs(ports)
    if not left or not right:
        return

    playback = find_physical_playback_ports(ports)
    if len(playback) < 2:
        return

    targets = [(left, playback[0]), (right, playback[1])]
    for source, dest in targets:
        if (source, dest) in connections:
            continue
        result = run_command(["pw-jack", "jack_connect", source, dest])
        if result.returncode == 0:
            print(f"[midi-hotplug] connected {source} -> {dest}")


last_sources = set()
last_dest_ports = set()


def connect_ports():
    match_text = os.getenv("SETBFREE_MATCH", "setBfree")
    exclude_raw = os.getenv("MIDI_CLIENT_EXCLUDE", "System,Midi Through")
    exclude_clients = {
        name.strip().lower() for name in exclude_raw.split(",") if name.strip()
    }

    try:
        ports = get_jack_ports()
    except RuntimeError as exc:
        print(f"[midi-hotplug] jack_lsp error: {exc}")
        return

    dest_ports = find_setbfree_inputs(ports, match_text)
    if not dest_ports:
        print("[midi-hotplug] setBfree MIDI input not found yet")
        if last_dest_ports:
            print("[midi-hotplug] setBfree MIDI input went away")
            last_dest_ports.clear()
        return

    if set(dest_ports) != last_dest_ports:
        last_dest_ports.clear()
        last_dest_ports.update(dest_ports)

    exclude_clients.update({name.split(":", 1)[0].lower() for name in dest_ports})
    sources = list_source_ports(ports, exclude_clients)
    connections = get_jack_connections()

    connect_audio(ports, connections)

    current_sources = set(sources)
    removed_sources = last_sources - current_sources
    for source in sorted(removed_sources):
        print(f"[midi-hotplug] source disappeared: {source}")
    last_sources.clear()
    last_sources.update(current_sources)

    for source in sources:
        for dest in dest_ports:
            if (source, dest) in connections:
                continue
            result = run_command(["pw-jack", "jack_connect", source, dest])
            if result.returncode == 0:
                print(f"[midi-hotplug] connected {source} -> {dest}")


def monitor_events():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="sound")

    print("[midi-hotplug] watching for MIDI devices")
    connect_ports()
    last_connect = time.time()
    interval = 1

    while True:
        device = monitor.poll(timeout=1)
        if device is not None and device.action in {"add", "remove", "change"}:
            device_name = (
                device.get("ID_MODEL") or device.get("NAME") or device.sys_name
            )
            print(f"[midi-hotplug] device {device.action}: {device_name}")
            connect_ports()
            last_connect = time.time()
        else:
            now = time.time()
            if now - last_connect >= interval:
                connect_ports()
                last_connect = now
            time.sleep(1)


if __name__ == "__main__":
    monitor_events()
