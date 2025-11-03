#!/bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

IFS=$'\n\t'

log()  { printf '%s  %s\n' "$(date +%T)" "$*"; }
die()  { printf '❌ %s\n' "$*" >&2; exit 1; }
run()  { "$@" || die "❌ $* failed with exit code $?"; }

echo "🔍 Detecting package manager..."

if command -v apt-get >/dev/null 2>&1; then
    PM="apt-get"
else
    die "No supported package manager found (apt-get, dnf, yum)"
fi

usage() {
    echo "Usage: $0 -p <product> -v <version> -r <repository_url>"
    echo "  -p   Product name (horizon|meridian)"
    echo "  -v   Version string"
    echo "  -r   Repository URL"
    exit 1
}

parse_args() {
    local OPT
    while getopts ":p:r:v:" OPT; do
        case "$OPT" in
            p) PRODUCT="${OPTARG}" ;;
            r) REPOSITORY_URL="${OPTARG}" ;;
            v) VERSION="${OPTARG}" ;;
            *) die "Usage: $0 -p <product> -v <version> -r <repository_url>" ;;
        esac
    done
    shift $((OPTIND - 1))


    if [[ -z "${PRODUCT:-}" ]]; then
        echo "Error: You must specify a product with -p."
        usage
    fi

    if [[ -z "${VERSION:-}" ]]; then
        echo "Error: You must specify a version with -v."
        usage
    fi

    if [[ -z "${REPOSITORY_URL:-}" ]]; then
        echo "Error: You must specify a repository URL with -r."
        usage
    fi
}

install_if_missing() {
    local pkg="$1"
    local cmd="$2"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log "📦 Installing missing dependency: $pkg"
        if [[ $PM == "apt-get" ]]; then
            run $PM update -y
            run $PM install -y "$pkg"
        else
            run $PM update -y
            run $PM install -y "$pkg"
        fi
    else
        log "✅ $pkg is already installed"
    fi
}

install_postgresql13_debian(){
    log "📦 Installing PostgreSQL 13 for Debian/Ubuntu"

    # Add GPG Key
    curl -fsSL https://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-keyring.gpg

    # Add PostgreSQL 13 repo
    . /etc/os-release
    CODENAME=${VERSION_CODENAME:-$(lsb_release -sc)}
    echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt ${CODENAME}-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list

    # Install PostgreSQL 13 server
    run $PM update -y
    run $PM install -y postgresql-13
}

install_dependencies() {
    install_if_missing curl curl
    install_if_missing jq jq
    install_if_missing wget wget
    install_if_missing tree tree

    # Debian specific as gnupg is not installed by default
    install_if_missing libterm-readline-perl-perl libterm-readline-perl-perl
    install_if_missing tzdata tzdata
    run ln -fs /usr/share/zoneinfo/America/Toronto /etc/localtime
    run dpkg-reconfigure -f noninteractive tzdata
    install_if_missing apt-utils apt-utils
    install_if_missing gnupg gnupg

    install_postgresql13_debian
}

install_product() {
    local product=$1
    local major=${2:-}

    run curl -fsSL https://debian.opennms.org/OPENNMS-GPG-KEY | gpg --dearmor -o /usr/share/keyrings/opennms-keyring.gpg
    run echo "deb [signed-by=/usr/share/keyrings/opennms-keyring.gpg] ${REPOSITORY_URL} stable main" > /etc/apt/sources.list.d/opennms.list
    run $PM update -y

    if [[ $product == "meridian" ]]; then
     run $PM install -y $product 
    else
     run $PM install -y opennms
    fi

    log "📂 /usr/share/opennms (short list)"
    tree /usr/share/opennms -L 1 | head -n 20

    log "Installed Packages"
    if [[ $product == "meridian" ]]; then
      run dpkg -l | grep $product
    else
      run dpkg -l | grep opennms
    fi
}

main() {
    parse_args "$@"
    # Forcing the URL to be expanded
    eval "REPOSITORY_URL=\"$REPOSITORY_URL\""
    major=""
    
    install_dependencies
    install_product "$PRODUCT" "$major"
}


main "$@"