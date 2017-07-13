#!/usr/bin/sh
. /utils.sh

pip install requests
cd /tmp/
wget <http-location-of-oneclickligration2-aws.py-file>
python /tmp/oneclickmigration2-aws.py -i $IPADD -u $USERROOT -p $USERPASS &

migration_pid=$!

while ps | grep " $migration_pid "
do
	echo Migration Process $migration_pid Still running
	sleep 120
done

echo Migration Task Completed

