export DEBIAN_FRONTEND=noninteractive
#There is a bug that cliqr repo in sources.list creates issues with ubuntu installation. Remove this line when fix is made.
#For now, commenting it out.
sudo sed -i -e '/cliqr/s/^/#/' /etc/apt/sources.list
sudo apt-get update
sudo apt-get install software-properties-common -y
sudo apt-add-repository ppa:ansible/ansible -y
sudo apt-get update
sudo apt-get install -y ansible
IP="$(ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
HOSTNAME=$(python /opt/remoteFiles/appPackage/streaming/create_inventory.py $IP)
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i /opt/remoteFiles/appPackage/inventory /opt/remoteFiles/appPackage/streaming/es_playbook.yml --limit=$HOSTNAME
