FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        setbfree \
        pipewire-jack \
        pipewire-bin \
        jackd2 \
        jack-example-tools \
        alsa-utils \
        x11-apps \
    && rm -rf /var/lib/apt/lists/*

ENV PIPEWIRE_LATENCY=64/48000

CMD ["/bin/sh", "-lc", "PIPEWIRE_LATENCY=\"${PIPEWIRE_LATENCY}\" pw-jack setBfreeUI"]
