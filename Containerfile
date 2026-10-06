FROM debian:bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        live-build debootstrap squashfs-tools systemd git curl sudo ca-certificates rsync apt-utils \
        python3-pil fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
