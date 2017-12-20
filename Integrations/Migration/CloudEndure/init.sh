#!/bin/sh
source /usr/local/agentlite/bin/vars.sh
SCRIPT_LOCATION="http://<IP>/migration/CE"
# Setting the script to exit immediately on any command failure
set -e
set -o pipefail

yum install epel-release -y
yum install python-pip -y
pip install requests
pip install argparse
yum install wget -y

echo "Downloading the migration script.."
cd /tmp/
wget ${SCRIPT_LOCATION}/CE_Cisco_Integration.py

python CE_Cisco_Integration.py -u $user -p $passwd -n $hostname -j $ceproject &

migration_pid=$!

echo "Tracking the migration run....Process Id is $migration_pid "

while [ "ps | grep $migration_pid" ]
do
	echo "Migration Process $migration_pid Still running"
	sleep 120
done

echo "Migration Task Completed..."
