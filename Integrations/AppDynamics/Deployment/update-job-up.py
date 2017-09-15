#! /usr/bin/python

import json
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import sys


c3mgr_url = <CLOUDCENTER-URL-FOR-JOBS>
# Example 'https://192.168.246.25/v2/jobs/'
job_id = <instance-job-id-number>
# Assumes job id is known or derived somehow
c3_user = 'cliqradmin'
c3_passwd = <c3-key>

def scale_up():
    headers = {
        'Content-Type': 'application/json',
        'Accept' : 'application/json',
    }
    payload = {
        "action" : "SCALE_UP",
        "numNodesToScale" : 1
    }
    job = requests.put(c3mgr_url+job_id, headers=headers, auth=(c3_user, c3_passwd), json=payload, verify=False)
    print 'Modified the job to scale up ' + str(job)

print 'Scaling up the instance job'
scale_up()
