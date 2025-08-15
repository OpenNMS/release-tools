#!/usr/bin/env bash

# Get the major version number
if [ -f /etc/redhat-release ]; then
    rhel_major=$(awk '{for(i=1;i<=NF;i++) if ($i ~ /^[0-9]+\./) {split($i, a, "."); print a[1]; exit}}' /etc/redhat-release)
else
    echo "❌ Could not detect major version. /etc/redhat-release not found."
    exit 1
fi

echo "🔍 Detected version: $rhel_major"

case "$rhel_major" in
    7)
        echo "📦 Installing repo for RHEL 7..."
        dnf --color=never -y install https://yum.opennms.org/repofiles/opennms-repo-stable-rhel7.noarch.rpm
        ;;
    8)
        echo "📦 Installing repo for RHEL 8..."
        dnf --color=never -y install https://yum.opennms.org/repofiles/opennms-repo-stable-rhel8.noarch.rpm

        echo "📦 Installing Java 17 (workaround)"
        dnf install --color=never -y openjdk-17-jdk

        echo "📦 Installing Postgress"
        dnf install --color=never -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        dnf --color=never -qy module disable postgresql
        dnf install --color=never -y postgresql13-server
        /usr/pgsql-13/bin/postgresql-13-setup initdb
        ;;
    9)
        echo "📦 Installing repo for RHEL 9..."
        dnf --color=never -y install https://yum.opennms.org/repofiles/opennms-repo-stable-rhel9.noarch.rpm
        ;;
    *)
        echo "❌ Unsupported version: $rhel_major"
        exit 1
        ;;
esac

echo "🔐 Import GPG Key"
rpm --import https://yum.opennms.org/OPENNMS-GPG-KEY

echo "📦 Install OpenNMS"
dnf --color=never -y install opennms

echo "📦 Install tree"
dnf --color=never -y install tree

echo "📂 List OpenNMS folder"
tree /opt/opennms -L 1

echo "📦 Get OpenNMS package information "
dnf --color=never info opennms
