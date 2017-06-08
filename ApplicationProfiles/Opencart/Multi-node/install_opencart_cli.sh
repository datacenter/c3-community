#!/bin/bash

OSMOSIX_BASE_DIR=/usr/local/osmosix
OPENCART_INSTALLED_FILE=$OSMOSIX_BASE_DIR/etc/.OPENCART_INSTALLED

[[ -f $OPENCART_INSTALLED_FILE ]] && { echo "OpenCart already installed"; exit; }

# ensure running as root
if [ "$(id -u)" != "0" ]; then
  exec sudo "$0" "$@"
fi

source /usr/local/osmosix/etc/userenv

if [ -z $CliqrTier_Apache_PUBLIC_IP ]; then
  exit 4
elif [ -z $CliqrTier_Database_IP ]; then
  exit 5
fi

#####added by vinod#######
IFS=","
hostname=$cliqrNodeHostname
INDEX=0
IPINDEX=0

for i in $CliqrTier_Apache_HOSTNAME ;
  do
    position=${INDEX}
    if [ $i = $hostname ];
        then
          node_position=$position
    fi
    let INDEX=${INDEX}+1
  done
for j in $CliqrTier_Apache_PUBLIC_IP ;
  do
    ipposition=${IPINDEX}
    let IPINDEX=${IPINDEX}+1
    if [ $ipposition = $node_position ];
       then
         HTTP_SERVER=$j;
#         echo $HTTP_SERVER;
    fi
  done

#####added by vinod#######

cd /var/www/install
php cli_install.php install --db_driver mysqli --db_host $CliqrTier_Database_IP --db_user opencart --db_password opencart --db_name opencart --username admin --password admin --email youremail@example.com --agree_tnc yes --http_server http://$HTTP_SERVER/
touch $OPENCART_INSTALLED_FILE
