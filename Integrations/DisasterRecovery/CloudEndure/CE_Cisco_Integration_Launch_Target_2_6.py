#!/usr/bin/python

# =================================================================================================
# CE_Cisco_Integration_Launch_Target_2_6.py
# 
# Version 2018-03-01
# 
# By Oren Gev, March. 2018
# 
# This script is a Cloud Center plugin which will utilize the CloudEndure API for launchin a target machine
# in case of DR.
# (CloudEndure is a server-replication provider, allowing migration and/or DR.) https://www.cloudendure.com/
# 
# CloudEndure API full documentation can be found here - https://console.cloudendure.com/api_doc/apis.html#
#
# usage: CE_Cisco_Integration_Launch_Target_2_6.py -u USERNAME -p PASSWORD -n HOSTNAME -j PROJECT_NAME
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
# Outputs: Will print to console the entire process of launching the target machine. 
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

INSTANCE_TYPE = "c4.large"
SUBNET = 'subnet-xxxxxx'
SG = 'sg-xxxxxx'

WIN_FOLDER = "c:\\temp"
LINUX_FOLDER = "/tmp"


###################################################################################################
def main():

# This is the main function, call the other functions to do the following:
# 	1. CloudEndure Agent installation on the target server.
#	2. Blueprint settings.
#	3. Replication progress.
#	4. Target server launch progress.
# 
# Returns: 	nothing - will always exit

	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--user', required=True, help='User name')
	parser.add_argument('-p', '--password', required=True, help='Password')
	parser.add_argument('-j', '--project', required=True, help='Project name')
	parser.add_argument('-n', '--agentname', required=True, help='Name of server')
	
	args = parser.parse_args()
	
	machine_id, project_id = get_parms(args)
	# Check if we were able to fetch the machine id
	if machine_id == -1:
		print "Failed to retrieve machine id"
		return -1
	
	# Launch the target instance on the cloud
	launch_target_machine(args, machine_id, project_id)

###################################################################################################
def get_parms(args):

# This function makes the HTTPS call out to the CloudEndure API to get machine Id and project ID
# 
# Usage: get_parms(args)
# 	'args' is script user input (args.user, args.password, args.agentname, args.project)
# 	
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
def launch_target_machine(args, machine_id, project_id):

# This function makes the HTTPS call out to the CloudEndure API and launches the target server on the Cloud
# 
# Usage: launch_target_machine(args, machine_id, project_id)
# 	'args' is script user input
# 	'machine_id' is the CloudEndure replicatin machine ID
# 	'project_id' is the CloudEndure project ID
# 
# Returns: 0 on success

	print "Launching target server"
	session, resp, endpoint = login(args)
	if session == -1:
		print "Failed to login"
		return -1
	items = {'machineId': machine_id}
	resp = session.post(url=HOST+endpoint+'projects/'+project_id+'/launchMachines', data=json.dumps({'items': [items], 'launchType': 'TEST'}))
	if resp.status_code != 202:
		print 'Error creating target machine!'
		print 'Status code is: ', resp.status_code
		return -1
	jobId = json.loads(resp.content)['id']


	isPending = True
	log_index = 0
	print "Waiting for job to finish..."
	while isPending:
		resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/jobs/'+jobId)
		job_status = json.loads(resp.content)['status']
		isPending = (job_status == 'STARTED')
		job_log = json.loads(resp.content)['log']
		while log_index < len(job_log):
			print job_log[log_index]['message']
			log_index += 1
		
		time.sleep(5)

	print 'Target server creation completed!'
	return 0;

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
