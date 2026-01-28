FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        xdotool \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY auto_flat_view.sh /app/auto_flat_view.sh
RUN chmod +x /app/auto_flat_view.sh

CMD ["/app/auto_flat_view.sh"]
