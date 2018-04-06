#!/bin/sh
source /usr/local/agentlite/bin/vars.sh
SCRIPT_LOCATION="http://<IP>/CE/DR"
# Setting the script to exit immediately on any command failure
set -e
set -o pipefail

yum install epel-release -y
yum install python-pip -y
pip install requests
pip install argparse
yum install wget -y

echo "Downloading the Disaster Recovery Enable script.."
cd /tmp/
wget ${SCRIPT_LOCATION}/CE_Cisco_Integration_DR_2_6.py

nohup python CE_Cisco_Integration_DR_2_6.py -u $user -p $passwd -n $HOSTNAME -j $ceproject &>/dev/null &

dr_pid=$!
disown
echo "Tracking the DR run....Process Id is $dr_pid "

echo "DR Replication Task Started..."
exit 0
