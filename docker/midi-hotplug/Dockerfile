FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-pyudev \
        jackd2 \
        jack-example-tools \
        pipewire-bin \
        pipewire-jack \
        alsa-utils \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY midi_hotplug.py /app/midi_hotplug.py

CMD ["python3", "/app/midi_hotplug.py"]
