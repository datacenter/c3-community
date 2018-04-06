#!/usr/local/bin/python2.7
#
# Push configuraiton to F5 BIG-IP using REST
#
# Author: jeye at cisco dot com
# Author: vng at f5 dot com

__author__ = 'jeye'
__author__ = 'vng'

import argparse
import requests
import re
import logging
import sys
import socket
import time
import json
import jinja2
from requests.auth import HTTPBasicAuth

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

protocol_dict = {'https':'''https://''',
                }

url_dict = {'deploy':'''/mgmt/tm/cloud/services/iapp/''',
           }

session = requests.Session()

def argparser():
    parse = argparse.ArgumentParser(description='Push configuration to F5 BIG-IP using REST.')

    parse.add_argument('-u', type=str, metavar='admin', default='admin', help='username')
    parse.add_argument('-p', type=str, metavar='password', default='admin', help='password')
    parse.add_argument('-s', '--https', action='store_true', default=True, help='enable https or http, default is https')
    parse.add_argument('-t', type=str, required=True, metavar='ip', help='multiple target IPs')
    parse.add_argument('-c', type=str, required=True, metavar='rest', help='type of the REST call: post, put, delete')
    parse.add_argument('-template', type=str, metavar='template', help='JSON template file')
    parse.add_argument('-var', type=str, metavar='var', help='Variable in JSON format')

    return parse.parse_args()

def build_url(protocol, host, url):
    full_url = str(protocol) + str(host) + str(url)
    return full_url

def build_iapp_url(protocol, host, url, iapp):
	full_iapp_url = str(protocol) + str(host) + str(url) + str(iapp)
	return full_iapp_url

def postJSON(session, username, password, url, content_type, json_string):
    return session.post(url, auth=HTTPBasicAuth(username, password), headers=content_type, verify=False, data=json_string)

def putJSON(session, username, password, url, content_type, json_string):
    return session.put(url, auth=HTTPBasicAuth(username, password), headers=content_type, verify=False, data=json_string)

def deleteJSON(session, username, password, url, content_type, json_string):
    return session.delete(url, auth=HTTPBasicAuth(username, password), headers=content_type, verify=False, data=json_string)

def read_json_file(jsonfile):
    with open(jsonfile, 'r') as f:
        json_string = json.load(f)
    return json_string

def main(args):
    username = str(args.u)
    password = str(args.p)
    ip = str(args.t)
    rest_call = str(args.c)
    protocol = protocol_dict['https']
    content_type = {'''accept''':'application/json','''content-type''':'application/json'}
    template_file = str(args.template)
    variable_file = str(args.var)
    json_string = ''

    # use level=logging.WARNING to set logging level to warning
    # use level=logging.INFO to set logging level to info
    # use logging=logging.DEBUG to set logging level to debug
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="./"))
    template = template_env.get_template(template_file)

    json_var = read_json_file(variable_file)
    json_string = template.render(json_var)
    logging.debug('+++++ POST this JSON +++++\n' + json_string + '+++++ END of JSON string +++++')

    logging.info('+++++ Logging in... +++++')
    url = build_url(protocol, ip, url_dict['deploy'])
    iapp_url = build_iapp_url(protocol, ip, url_dict['deploy'], json_var["name"])
        
    if rest_call in ['post']:
    	req = postJSON(session, username, password, url, content_type, json_string)
    elif rest_call in ['put']:
    	req = putJSON(session, username, password, iapp_url, content_type, json_string)
    elif rest_call in ['delete']:
    	req = deleteJSON(session, username, password, iapp_url, content_type, json_string)
    else:
    	logging.debug('+++++ Invalid REST input +++++\n' + rest_call + '\n+++++\n')
    
    if '"code":400' in req.text:
    	debug = open('FAILURE','w')
    	debug.write(req.text)
    	logging.debug('+++++ POST FAIL response +++++\n' + req.text +'\n+++++')
    else:
    	debug = open('SUCCESS','w')
    	debug.write(req.text)
    	logging.debug('+++++ POST SUCCESS response +++++\n' + req.text +'\n+++++')

if __name__ == '__main__':
    args = argparser()
    main(args)
