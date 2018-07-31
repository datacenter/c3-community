export DEBIAN_FRONTEND=noninteractive
#There is a bug that cliqr repo in sources.list creates issues with ubuntu installation. Remove this line when fix is made.
#For now, commenting it out.
sudo sed -i -e '/cliqr/s/^/#/' /etc/apt/sources.list
sudo apt-get update
sudo apt-get install software-properties-common -y
sudo apt-add-repository ppa:ansible/ansible -y
sudo apt-get update
sudo apt-get install -y ansible
python /opt/remoteFiles/appPackage/elastic/create_inventory.py
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i /opt/remoteFiles/appPackage/inventory /opt/remoteFiles/appPackage/elastic/es_playbook.yml
