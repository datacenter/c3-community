#!/bin/bash

AGENT_LOCATION="<location-of-agent-file>"
APPD_CONTROLLER="appd-controller"
APPD_CONTROLLER_PORT="8090"
APPD_CONTROLLER_SSL_ENABLED=""
APPD_ACCESS_KEY="<account-access-key>"
APPD_ACCOUNT_NAME="<account-name>"
DEPLOYMENT_NAME="Machines"

# Setting the script to exit immediately on any command failure
set -e
set -o pipefail

# Add Host file entry for appd-controller if DNS entry not configured
echo '<IP>	appd-controller' | tee --append /etc/hosts > /dev/null

#Downloading the AppD Agent
echo "Downloading the AppDynamics Machine Agent..."
cd /tmp/
mkdir appd-agent
cd /tmp/appd-agent
wget ${AGENT_LOCATION}/machine-agent/linux/appdynamics-machine-agent-4.3.3.8-1.x86_64.rpm; touch /tmp/appd-agent/downloadagent.done &

#Check if download is done then proceed to unzip the agent package
while [ ! -f /tmp/appd-agent/downloadagent.done ]
	do
	 sleep 10
done


# Install the AppD Agent
echo "Installing the AppDynamics Machine Agent..."
rpm -ivh appdynamics-machine-agent-4.3.3.8-1.x86_64.rpm
echo "Configuring the AppDynamics Machine Agent..."
sed -i.bkp -e "s%<controller-host>%<controller-host>${APPD_CONTROLLER}%g" \
-e "s%<controller-port>%<controller-port>${APPD_CONTROLLER_PORT}%g" \
-e "s%<account-access-key>%<account-access-key>${APPD_ACCESS_KEY}%g" \
-e "s%<controller-ssl-enabled>%<controller-ssl-enabled>${APPD_CONTROLLER_SSL_ENABLED}%g" \
-e "s%<account-name>%<account-name>${APPD_ACCOUNT_NAME}%g" \
-e "s%<sim-enabled>false%<sim-enabled>true%g" \
-e "s%</controller-info>%<application-name>${DEPLOYMENT_NAME}</application-name></controller-info>%g" \
/opt/appdynamics/machine-agent/conf/controller-info.xml


# Restart Machine Agent
echo "Starting the AppDynamics Machine Agent..."
sleep 10
service appdynamics-machine-agent start

# Clean up the temporary file and the agent package file
echo "Cleaning files... AppDynamics Machine Agent..."
rm -rf /tmp/appd-agent/downloadagent.done
rm -rf /tmp/appd-agent/appdynamics-machine-agent-4.3.3.8-1.x86_64.rpm

echo "AppDynamics Machine Agent Installation...done!"
