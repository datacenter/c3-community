#!/bin/bash 

########################################################################
# Name: es_local_init_ansible.sh
#
# DESCRIPTION:
# Script to <specify function>
#
########################################################################

export DEBIAN_FRONTEND=noninteractive

sudo /usr/local/osmosix/etc/.osmosix.sh
. /usr/local/osmosix/etc/userenv
OSSVC_HOME=/usr/local/osmosix/service
. $OSSVC_HOME/utils/cfgutil.sh
. $OSSVC_HOME/utils/nosqlutil.sh
. $OSSVC_HOME/utils/install_util.sh
. $OSSVC_HOME/utils/os_info_util.sh
. $OSSVC_HOME/utils/agent_util.sh

### Install Pre-Requistes
agentSendLogMessage "Setting up pre-requistes.."

sudo sed -i -e '/cliqr/s/^/#/' /etc/apt/sources.list
sudo apt-get update
sudo apt-get install software-properties-common -y
sudo apt-add-repository ppa:ansible/ansible -y
sudo apt-get update
sudo apt-get install -y ansible

### Run playbook to install elastic search component
agentSendLogMessage "Running ansible playbook to install component.."

IP="$(ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
HOSTNAME=$(python /opt/remoteFiles/appPackage/elastic_local/create_inventory.py $IP)

ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i /opt/remoteFiles/appPackage/inventory /opt/remoteFiles/appPackage/elastic_local/es_playbook.yml --limit=$HOSTNAME
