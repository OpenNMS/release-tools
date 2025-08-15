#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

echo "📦 Install dependencies"
apt update -q 
apt -q -y install curl gnupg ca-certificates lsb-release wget

echo "📦 Install PostgresSQL"
# Make sure the keyrings directory exists
install -d -m 0755 /usr/share/keyrings

curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
  | gpg --dearmor \
  | tee /usr/share/keyrings/postgresql.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] \
http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
apt update -q 
apt -q -y install postgresql-13

echo "🔐 Import GPG Key and setup the repository"
curl -fsSL https://debian.opennms.org/OPENNMS-GPG-KEY | gpg --dearmor -o /usr/share/keyrings/opennms.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/opennms.gpg] \
https://debian.opennms.org stable main" > /etc/apt/sources.list.d/opennms.list
apt update -q 

echo "📦 Install OpenNMS"
apt -q -y install opennms

echo "📦 Install tree"
apt -q -y install tree

echo "📂 List OpenNMS folder"
tree /usr/share/opennms -L 1

echo "📦 Get OpenNMS package information"
apt show opennms
