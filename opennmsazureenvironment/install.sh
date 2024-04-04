#!/bin/sh
# This script helps with installing OpenNMS Horizon with default settings;
#
# This script is for testing purposes!!!!
#

exec >"/tmp/installlog.txt" 2>&1

if test -f "/tmp/.installed"; then
    echo ".installed exists."
    exit 0 
fi

command -v sudo >/dev/null 2>&1 || { dnf install -y sudo ; }

echo "Install Java 17 and lanpacks"
sudo dnf install -y java-17-openjdk langpacks-en glibc-all-langpacks
echo "set-locale LANG=en_US.UTF-8"
sudo localectl set-locale LANG=en_US.UTF-8
echo "Disable the default postgresql"
sudo dnf module disable -y postgresql
echo "Install Postgresql 16"
sudo dnf -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo dnf -y install postgresql16-server postgresql16-contrib
#sudo -u postgres localectl set-locale LANG=en_US.UTF-8
echo "Restart Postgresql 16"
sudo systemctl restart postgresql-16.service
echo "Initialize Postgresql database"
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb
sudo systemctl restart postgresql-16.service
echo "Install pwgen"
sudo dnf -y install https://dl.fedoraproject.org/pub/epel/9/Everything/x86_64/Packages/p/pwgen-2.08-8.el9.x86_64.rpm

echo "Add OpenNMS repo"
sudo dnf -y install https://yum.opennms.org/repofiles/opennms-repo-stable-rhel9.noarch.rpm
sudo rpm --import https://yum.opennms.org/OPENNMS-GPG-KEY
sudo dnf -y update

echo "Wait for Postgres to be in ready state"
export test_pgready=$(sudo -u postgres /usr/pgsql-16/bin/pg_isready > /dev/null 2>&1; echo $?)
while [ $test_pgready -ne 0 ]
do 
 test_pgready=$(sudo -u postgres /usr/pgsql-16/bin/pg_isready > /dev/null 2>&1; echo $?)
 sleep 1
done

export tmp_pwd1="$(pwgen -n 20 1)"
export tmp_pwd2="$(pwgen -n 20 1)"
sudo -u postgres psql -c "CREATE USER opennms WITH PASSWORD '${tmp_pwd1}';"
sudo -u postgres createdb -O opennms opennms
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${tmp_pwd2}';"
sudo systemctl restart postgresql-16.service

export test_pgready=$(sudo -u postgres /usr/pgsql-16/bin/pg_isready > /dev/null 2>&1; echo $?)
while [ $test_pgready -ne 0 ]
do 
 test_pgready=$(sudo -u postgres /usr/pgsql-16/bin/pg_isready > /dev/null 2>&1; echo $?)
 sleep 1
done

sleep 5
echo "Install Horizon"
sudo dnf -y install opennms tree

echo "Setup OpenNMS Core"
sudo -u opennms  /opt/opennms/bin/scvcli set postgres opennms "${tmp_pwd1}"
sudo -u opennms /opt/opennms/bin/scvcli set postgres-admin postgres "${tmp_pwd2}"
export tmp_pwd3="$(pwgen -n 20 1)"
sudo /opt/opennms/bin/install -S -R "${tmp_pwd3}" 
echo "${tmp_pwd3}" > "/home/$(whoami)/.login_cred"
sudo /opt/opennms/bin/fix-permissions
sudo /opt/opennms/bin/runjava -s
sudo /opt/opennms/bin/install -dis
sleep 10
sudo -u opennms /opt/opennms/bin/opennms status > "/tmp/.installed" 2>&1
sudo systemctl enable --now opennms

