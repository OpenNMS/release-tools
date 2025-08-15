#!/usr/bin/env bash

export VERSION=34.0.0

export DOCKER_OPTIONS=""

export DOCKER_IMAGES_RPM=(
    "almalinux/8-base:latest"
    "almalinux/9-base:latest"
    "rockylinux:8"
    "rockylinux:9"
)

export DOCKER_IMAGES_DEBIAN=(
    "ubuntu:latest"
    "debian:latest"
)

export CURRENT_DIR
CURRENT_DIR="$(pwd)"

if [ ! -d "${CURRENT_DIR}/logs" ];then
 mkdir "${CURRENT_DIR}/logs"
fi

case "$(uname -m)" in
    x86_64)
        echo "Running on x86_64 (Intel/AMD 64-bit)"
        ;;
    arm64|aarch64)
        DOCKER_OPTIONS+=" --platform linux/amd64"
        ;;
    *)
        echo "Unknown architecture: $(uname -m)"
        ;;
esac

echo "DOCKER_OPTIONS: ${DOCKER_OPTIONS}"

run_and_log() {
    local img="$1"
    local helper="$2"
    local safe_name
    safe_name=$(echo "$img" | tr '/:' '_-')
    local logfile="${CURRENT_DIR}/logs/${safe_name}.log"

    echo "=== Running $img, logging to $logfile ==="
    docker run --rm -it ${DOCKER_OPTIONS} -v "${CURRENT_DIR}/helpers/$helper":/start.sh "$img" ./start.sh >"$logfile " 2>&1
}

for img in "${DOCKER_IMAGES_RPM[@]}"; do
    run_and_log "$img" "rpm-base.sh"
done

for img in "${DOCKER_IMAGES_DEBIAN[@]}"; do
    run_and_log "$img" "debian.sh"
done