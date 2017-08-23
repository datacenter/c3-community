#!/bin/bash


OSSVC_HOME=/usr/local/osmosix/service

. /usr/local/osmosix/etc/.osmosix.sh
. /usr/local/osmosix/etc/userenv
. $OSSVC_HOME/utils/cfgutil.sh
. $OSSVC_HOME/utils/nosqlutil.sh
. $OSSVC_HOME/utils/install_util.sh
. $OSSVC_HOME/utils/os_info_util.sh
. $OSSVC_HOME/utils/agent_util.sh

# RUN EVERYTHING AS ROOT
if [ "$(id -u)" != "0" ]; then
    exec sudo "$0" "$@"
fi

cluster_id=""

function setup_prereqs() {
  agentSendLogMessage "Installing PreReqs.."
  yum install -y docker  wget
  systemctl enable docker
  systemctl start docker
}

function getClusterID() {
  tierName=$CliqrDependencies
  clustervar=CliqrTier_${tierName}_cluster_id
  cluster_id=${!clustervar}
  agentSendLogMessage "Retrieving Cluster ID from Harmony Controller.."
}

function installLDAC() {
  agentSendLogMessage "Installing Lightining ADC with Cluster ID $cluster_id"
  docker run -tdi -e ladc_api_svr_url=$a10_api_server -e ladc_cluster_id=$cluster_id --net=host --privileged=true a10networks/ladc
}

setup_prereqs
getClusterID
installLDAC
