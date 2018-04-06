#!/usr/bin/python

# =================================================================================================
# CE_Cisco_Integration_DR_2_6.py
# 
# Version 2018-03-01
# 
# By Oren Gev, March. 2018
# 
# This script is a Cloud Center plugin which will utilize the CloudEndure API for the 
# replication / sync status of a host.
# (CloudEndure is a server-replication provider, allowing migration and/or DR.) https://www.cloudendure.com/
# 
# CloudEndure API full documentation can be found here - https://console.cloudendure.com/api_doc/apis.html#
#
# usage: CE_Cisco_Integration_DR_2_6.py -u USERNAME -p PASSWORD -n HOSTNAME -j PROJECT_NAME
# 
# 
# Arguments:
#  
#   -u USERNAME, 	--username USERNAME
#                         user name for the CloudEndure account
#   -p PASSWORD, 	--password PASSWORD
#                         password for the CloudEndure account
#   -n HOSTNAME, 	--agentname HOSTNAME
#                         hostname of instance to migrate
# 	-j PROJECT, 	--project PROJECT_NAME
#                         CloudEndure's project name
# 
# 
# Required inputs: CloudEndure username and password, target server name
# 
# Outputs: Will print to console the entire process:
#	1. CloudEndure Agent installation on the target server.
#	2. Blueprint settings.
#	3. Replication progress until completion.
# 
# 
# =================================================================================================


import requests
import os
import time
import argparse
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

HOST = 'https://console.cloudendure.com'

INSTANCE_TYPE = "c4.4xlarge"
SUBNET = 'subnet-XXXXXX'
SG = 'sg-XXXXXX'

WIN_FOLDER = "c:\\temp"
LINUX_FOLDER = "/tmp"


###################################################################################################
def main():

# This is the main function, call the other functions to do the following:
# 	1. CloudEndure Agent installation on the target server.
#	2. Blueprint settings.
#	3. Replication progress.
# 
# Returns: 	nothing - will always exit

	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--user', required=True, help='User name')
	parser.add_argument('-p', '--password', required=True, help='Password')
	parser.add_argument('-j', '--project', required=True, help='Project name')
	parser.add_argument('-n', '--agentname', required=True, help='Name of server')
	
	args = parser.parse_args()
	
	installation_token = get_token(args)
	if installation_token == -1:
		print "Failed to retrieve project installation token"
		return -1
	
	machine_id, project_id = get_parms(args)
	# Check if we were able to fetch the machine id
	if machine_id == -1:
		print "Failed to retrieve machine id"
		return -1
		
	# Check replication status, set blueprint while waiting for it to complete
	wait_for_replicaiton(args, machine_id, project_id)
	
###################################################################################################
def get_parms(args):

# This function makes the HTTPS call out to the CloudEndure API to get machine Id and project ID
# 
# Usage: get_parms(args)
# 	'args' is script user input (args.user, args.password, args.agentname, args.project)
# 
# Returns: 	0 on success, -1 on failure
	
	session, resp, endpoint= login(args)
	
	if session == -1:
		print "Failed to login"
		return -1, -1
	
	# Fetch the CloudEndure project ID in order to locate the machine itself
	projects_resp = session.get(url=HOST+endpoint+'projects')
	projects = json.loads(projects_resp.content)['items']
	
	project_id = None
	machine_id = None
	
	# Fetch the CloudEndure machine ID in order monitor the replication progress and launch the target server		
	print 'Getting machine id...'
	for project in projects:
		project_id = project['id']	
		
		machines_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines')
		machines = json.loads(machines_resp.content)['items']

		machine_id = [m['id'] for m in machines if args.agentname.lower() == m['sourceProperties']['name'].lower()]

		if machine_id:
			break
			
	if not machine_id:
		print 'Error! No agent with name ' + args.agentname+ ' found'
		return -1, -1
	
	return machine_id[0].encode('ascii','ignore'), project_id


###################################################################################################

def get_token(args):

# This function fetch the project installation token
# Usage: get_token(args)
#       'args' is script user input (args.user, args.password, args.agentname)
#
# Returns:      -1 on failure

        print "Fetching the installation token..."
        session, resp, endpoint = login(args)
        if session == -1:
                print "Failed to login"
                return -1

        project_name = args.project

        projects_resp = session.get(url=HOST+endpoint+'projects')
        projects = json.loads(projects_resp.content)['items']

        project = [p for p in projects if project_name==p['name']]
        if not project:
                print 'Error! No project with name ' + args.project+ ' found'
                return -1
        return project[0]['agentInstallationToken']

###################################################################################################





	
###################################################################################################	
def wait_for_replicaiton(args, machine_id, project_id):

# This function makes the HTTPS call out to the CloudEndure API multiple times until replication to complete.
# Once it's done, the function will call set_blueprint in order to apply the blueprint settings before 
# launching the target server.
#
# Usage: wait_for_replicaiton(args, machine_id, project_id)
# 	'args' is script user input (args.user, args.password, args.agentname)
# 	'machine_id' is the CloudEndure replicatin machine ID
# 	'project_id' is the CloudEndure project ID
# 
# Returns: 	0 on success, -1 on failure

	# Looping until replication completes
	print "Checking Replication Status...."
	session, resp, endpoint = login(args)
	if session == -1:
		print "Failed to login"
		return -1
		
	# Waiting for replication to start and the connection to establish
	try:
		machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)
		replication_status = json.loads(machine_resp.content)['replicationStatus']
	
	except:
		print "Replication has not started. Waiting..."
		time.sleep(10)
		
		# Waiting for replication to start and the coneection to establish
	while replication_status != 'STARTED':
		print "Replication has not started. Waiting..."
		machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)
		replication_status = json.loads(machine_resp.content)['replicationStatus']
		
	try:
		replicated_storage_bytes = json.loads(machine_resp.content)['replicationInfo']['replicatedStorageBytes']
		total_storage_bytes = json.loads(machine_resp.content)['replicationInfo']['totalStorageBytes']

	except:
		print "Replication has not started. Waiting..."
		machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)
		
	try:
		last_consistency = json.loads(machine_resp.content)['replicationInfo']['lastConsistencyDateTime']
		backlog = json.loads(machine_resp.content)['replicationInfo']['backloggedStorageBytes']
		if backlog == 0:
			print "Replication completed. Target machine is launchable!"
			return 0
		else:
			print 'Replication is lagging. Backlog size is '+ str(backlog)
	except:
		if replicated_storage_bytes == total_storage_bytes:
			print "Finalizing initial sync. Waiting..."
		else:
			print 'Replicated '+ str(replicated_storage_bytes)+' out of '+str(total_storage_bytes)+' bytes'
		machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)			


###################################################################################################	
def login(args):

# This function makes the HTTPS call out to the CloudEndure API to login using the credentilas provided
# 
# Usage: login(args)
# 	'args' is script user input (args.user, args.password, args.agentname)
# 
# Returns: 	-1 on failure
#			session, response, endpoint on success

	endpoint = '/api/latest/'
	session = requests.Session()
	session.headers.update({'Content-type': 'application/json', 'Accept': 'text/plain'})
	resp = session.post(url=HOST+endpoint+'login', data=json.dumps({'username': args.user, 'password': args.password}))
	if resp.status_code != 200 and resp.status_code != 307:
		print "Bad login credentials"
		return -1, -1, -1
	#print 'Logged in successfully'	

	
	# Check if need to use a different API entry point and redirect
	if resp.history:
		endpoint = '/' + '/'.join(resp.url.split('/')[3:-1]) + '/'
		resp = session.post(url=HOST+endpoint+'login', data=json.dumps({'username': args.user, 'password': args.password}))
	
	try:
		session.headers.update({'X-XSRF-TOKEN' : resp.cookies['XSRF-TOKEN']})
	except:
		pass
	
	return session, resp, endpoint
	
###################################################################################################		
if __name__ == '__main__':
    main()
