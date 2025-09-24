#!/bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

IFS=$'\n\t'

log()  { printf '%s  %s\n' "$(date +%T)" "$*"; }
die()  { printf '❌ %s\n' "$*" >&2; exit 1; }
run()  { "$@" || die "❌ $* failed with exit code $?"; }

echo "🔍 Detecting package manager..."

if command -v dnf >/dev/null 2>&1; then
    PM="dnf"
elif command -v yum >/dev/null 2>&1; then
    PM="yum"
else
    die "No supported package manager found (dnf, yum)"
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

rhel_major() {
    [[ -f /etc/redhat-release ]] || die "/etc/redhat-release not found"
    local line
    line=$(< /etc/redhat-release)
    [[ $line =~ ([0-9]+)\. ]] || die "Could not parse RHEL major version"
    echo "${BASH_REMATCH[1]}"
}


install_postgresql13_rhel8() {
    log "📦 Installing PostgreSQL 13 for RHEL 8"

    # Disable conflicting module
    run $PM module disable -y postgresql

    # Add GPG Key
    rpm --import https://download.postgresql.org/pub/repos/yum/keys/PGDG-RPM-GPG-KEY-RHEL

    # Add PostgreSQL 13 repo
    run $PM install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm

    # Install PostgreSQL 13 server
    run $PM install -y postgresql13-server
}

install_dependencies() {
    install_if_missing curl curl
    install_if_missing jq jq
    install_if_missing wget wget
    install_if_missing tree tree

    # RHEL 8-specific PostgreSQL fix
    if [[ ${major:-} == "8" ]]; then
        install_postgresql13_rhel8
    fi
}

install_product() {
    local product=$1
    local major=${2:-}

    run rpm --import https://yum.opennms.org/OPENNMS-GPG-KEY

    if [[ $product == "meridian" ]]; then
    run cat << EOF > /etc/yum.repos.d/opennms-meridian.repo
[meridian]
name=Meridian for Red Hat Enterprise Linux and CentOS
baseurl=${REPOSITORY_URL}
gpgcheck=1
gpgkey=http://yum.opennms.org/OPENNMS-GPG-KEY
EOF
     run $PM install -y $product 
    else
     run $PM install -y $REPOSITORY_URL 
     run $PM install -y opennms
    fi

    log "📂 /opt/opennms (short list)"
    tree /opt/opennms -L 1 | head -n 20

    if [[ $product == "meridian" ]]; then
      run $PM list installed $product
    else
      run $PM list installed opennms
    fi
}

main() {
    parse_args "$@"
    # Forcing the URL to be expanded
    eval "REPOSITORY_URL=\"$REPOSITORY_URL\""
    major=""
    major=$(rhel_major)
    
    install_dependencies
    install_product "$PRODUCT" "$major"
}


main "$@"