#!/bin/sh
. /utils.sh
if [ "$(id -u)" != "0" ]; then
exec sudo "$0" "$@"
fi

SCRIPT_LOCATION="http://<IP>/CE/DR"
#Setting the script to exit immediately on any command failure
set -e
set -o pipefail
nohup yum install epel-release -y &>/dev/null &
wait
nohup yum install python-pip -y &>/dev/null &
wait
nohup pip install requests &>/dev/null &
wait
nohup pip install argparse &>/dev/null &
wait
nohup yum install wget -y &>/dev/null &
wait

echo "Checking the DR Status.."
cd /tmp/
nohup wget ${SCRIPT_LOCATION}/CE_Cisco_Integration_Report_Status_2_6.py &>/dev/null &
wait

python CE_Cisco_Integration_Report_Status_2_6.py -u $user -p $passwd -n $hostnamece -j $ceproject 
exit 0
