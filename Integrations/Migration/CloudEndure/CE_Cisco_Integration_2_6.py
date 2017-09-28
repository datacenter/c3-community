#!/usr/bin/python
# Authored by Oren from CloudEndure
import requests
import os
import time
import argparse
import json
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

HOST = 'https://console.cloudendure.com'

INSTANCE_TYPE = "c4.4xlarge"
SUBNET = 'subnet-XXXXXXXX'
SG = 'sg-XXXXXXX'

WIN_FOLDER = "c:\\temp"
LINUX_FOLDER = "/tmp"


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--user', required=True, help='User name')
	parser.add_argument('-p', '--password', required=True, help='Password')
	parser.add_argument('-n', '--agentname', required=True, help='Name of server')
	
	args = parser.parse_args()
	
	machine_id, project_id = install_agent(args)
	if machine_id == -1:
		print "Failed to retrieve machine id"
		return -1

	wait_for_replicaiton(args, machine_id, project_id)
	
	launch_target_machine(args, machine_id, project_id)

def install_agent(args):
	if os.name == 'nt': #Check if it's windows or not
		if not os.path.exists(WIN_FOLDER):
			os.mkdir(WIN_FOLDER)
		os.chdir(WIN_FOLDER)
		fname = 'installer_win.exe'
		cmd = 'echo | ' +fname + ' -u ' + args.user + ' -p ' + args.password+' --no-prompt'
	else:
		os.chdir(LINUX_FOLDER)
		fname = 'installer_linux.py'
		cmd = 'sudo python '+ fname+ ' -u ' + args.user + ' -p ' + args.password+' --no-prompt'
		
	url = 'https://console.cloudendure.com/api/v12/static/' + fname
	request = requests.get(url)
	open(fname , 'wb').write(request.content)
	
	ret = os.system(cmd)
	if ret != 0:
		print "Failed installing CloudEndure agent"
		return -1, -1
	
	session, resp, endpoint= login(args)
	
	if session == -1:
		print "Failed to login"
		return -1, -1
	
	projects_resp = session.get(url=HOST+endpoint+'projects')
	
	projects = json.loads(projects_resp.content)['items']
	project_id = projects[0]['id']
	
	print 'Getting machine id...'
	machines_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines')
	machines = json.loads(machines_resp.content)['items']


	machine_ids = [m['id'] for m in machines if args.agentname.lower() == m['sourceProperties']['name'].lower()]

	if not machine_ids:
		print 'Error! No agent with name ' + args.agentname+ ' found'
		return -1, -1

	return machine_ids[0], project_id
	
	
def wait_for_replicaiton(args, machine_id, project_id):
	print "Waiting for Replication to complete"
	while True:
		session, resp, endpoint = login(args)
		if session == -1:
			print "Failed to login"
			return -1
		
		while True:
			try:
				machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)
				replication_status = json.loads(machine_resp.content)['replicationStatus']
				break
			except:
				print "Replication has not started. Waiting..."
				time.sleep(10)

		while replication_status != 'STARTED':
			print "Replication has not started. Waiting..."
			time.sleep(120)
			machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)
			replication_status = json.loads(machine_resp.content)['replicationStatus']

		if set_blueprint(args, machine_id, project_id) == -1:
			print "Failed to set blueprint"

		while True:
			try:
				replicated_storage_bytes = json.loads(machine_resp.content)['replicationInfo']['replicatedStorageBytes']
				total_storage_bytes = json.loads(machine_resp.content)['replicationInfo']['totalStorageBytes']
				break
			except:
				print "Replication has not started. Waiting..."
				time.sleep(120)
				machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)
				
		while True:
			try:
				last_consistency = json.loads(machine_resp.content)['replicationInfo']['lastConsistencyDateTime']
				backlog = json.loads(machine_resp.content)['replicationInfo']['backloggedStorageBytes']
				if backlog == 0:
					print "Replication completed. Target machine is launchable!"
					return 0
				else:
					print 'Replication is lagging. Backlog size is '+ str(backlog)
					time.sleep(60)
			except:
				if replicated_storage_bytes == total_storage_bytes:
					print "Finalizing initial sync. Waiting..."
					time.sleep(60)
				else:
					print 'Replicated '+ str(replicated_storage_bytes)+' out of '+str(total_storage_bytes)+' bytes'
					print "Will check again in 5 minutes. Waiting..."
					time.sleep(300)				
			machine_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/machines/'+machine_id)			

def set_blueprint(args, machine_id, project_id):
	print "Setting blueprint..."
	session, resp, endpoint = login(args)
	if session == -1:
		print "Failed to login"
		return -1
	
	blueprints_resp = session.get(url=HOST+endpoint+'projects/'+project_id+'/blueprints')
	blueprints = json.loads(blueprints_resp.content)['items']
	
	blueprint = [bp for bp in blueprints if machine_id==bp['machineId']]
	if len(blueprint) == 0:
		return -1		
	
	blueprint = blueprint[0]	
	
	blueprint['instanceType']=INSTANCE_TYPE
	blueprint['subnetIDs']=[SUBNET]
	blueprint['securityGroupIDs']=[SG]
	blueprint['machineId']=machine_id
	
	resp = session.patch(url=HOST+endpoint+'projects/'+project_id+'/blueprints/'+blueprint['id'],data=json.dumps(blueprint))
	if resp.status_code != 200:
		print 'Error setting blueprint!'
		print resp.status_code
		print resp.reason
		print resp.content
		return -1
		
	print "Blueprint was set successfully"
	return 0

	

		
def launch_target_machine(args, machine_id, project_id):
	print "Launching target server"
	session, resp, endpoint = login(args)
	if session == -1:
		print "Failed to login"
		return -1
	items = {'machineId': machine_id, 'pointInTimeId': ""}
	resp = session.post(url=HOST+endpoint+'projects/'+project_id+'/performTest', data=json.dumps({'items': [items]}))
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
	
def login(args):
	#print 'Logging in to API...'
	endpoint = '/api/latest/'
	session = requests.Session()
	session.headers.update({'Content-type': 'application/json', 'Accept': 'text/plain'})
	resp = session.post(url=HOST+endpoint+'login', data=json.dumps({'username': args.user, 'password': args.password}))
	if resp.status_code != 200 and resp.status_code != 307:
		print "Bad login credentials"
		return -1, -1, -1
	#print 'Logged in successfully'	
	
	# check if need to use a different API entry point
	if resp.history:
		endpoint = '/' + '/'.join(resp.url.split('/')[3:-1]) + '/'
		resp = session.post(url=HOST+endpoint+'login', data=json.dumps({'username': args.user, 'password': args.password}))

	return session, resp, endpoint
	
	
if __name__ == '__main__':
    main()
