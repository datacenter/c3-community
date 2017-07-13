#!/usr/bin/python
# Authored by Srinivasa from Rivermeadow

import sys
import requests
import json
import time
import optparse
from requests.auth import HTTPBasicAuth
from string import Template
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# global variables
basicAuth = HTTPBasicAuth('rivermeadow-user-name', 'rivermeadow-user-pass')
base_url = 'https://beta.rivermeadow.com/api/v3/oneclickmigrations'
header_info = {"Content-Type": "application/json"}
cloud_account = 'cloud-account-id-at-rivermeadow'
flavor_type = 't2.medium'
volume_type = 'magnetic'
security_group = 'security-group-id-at-aws'

def get_one_click_migration(id):
    get_url = base_url + "/" + id
    print
    print "Invoking one click migration get url: " + get_url
    get_response = requests.get(get_url, auth=basicAuth, headers=header_info)
    return get_response.json()

def wait_to_complete_one_click_migration(one_click_migration_id):
    get_result_json = None
    while True:
        get_result_json = get_one_click_migration(one_click_migration_id)
        state = get_result_json["state"]
        print "id: " + get_result_json["id"]
        print "state: " + state
        print "current step: " + get_result_json["current_step"]
        if state == 'success' or state == 'error':
            break
        else:
            print "wait and sleeping...  2 min"
            time.sleep(120)
    return get_result_json["state"]


def post_one_click_migration(json_data_string):
    print "Posting one click migration to server ..."
    post_response = requests.post(base_url, auth=basicAuth, data=json_data_string, headers=header_info)
    if post_response.status_code == 201:
        return post_response.json()
    else:
        print "status code: " + str(post_response.status_code) + " content: " + post_response.content
        return {}

def json_data_string(options):
    print "Preparing one click migration json string from user input ..."
    # source info
    source_info = """ "sources":[
                        {
                            "credentials":{
                                "username":"$user",
                                "password":"$password"
                            },
                            "host":"$ip"
                        }]"""

    source_data = {"ip": options.ip, "user": options.user, "password": options.password}
    source_info_template = Template(source_info)
    source_element = source_info_template.substitute(source_data)

    # cloud account info
    cloud_account_info = """  
                            "cloud_account":
                                {
                                    "id":"$cloud_account"
                                }"""
#   cloud_account_data = {"cloud_account": options.cloud_account}
    cloud_account_data = {"cloud_account": cloud_account}
    cloud_account_template = Template(cloud_account_info)
    cloud_account_element = cloud_account_template.substitute(cloud_account_data)

#   if options.flavor_type is not None and options.volume_type is not None and options.security_group is not None:
        # aws flavor type and volume type
    target_config_info = """
                            "target_config":{
                                    "vm_details":{
                                        "flavor":{
                                            "flavor_type":"$flavor_type",
                                            "volume_type":"$volume_type"
                                            },
                                        "security":{
                                            "security_group_ids":["$security_group"]
                                        }
                                    }
                            }"""

#       target_config_data = {"flavor_type": options.flavor_type, "volume_type": options.volume_type,
    target_config_data = {"flavor_type": flavor_type, "volume_type": volume_type,
                          "security_group": security_group }
    target_config_template = Template(target_config_info)
    target_config_element = target_config_template.substitute(target_config_data)
    return "{ " + source_element + "," + cloud_account_element + "," + target_config_element + " } "
#    else:
#        return "{ " + source_element + "," + cloud_account_element + " } "


def main(argv):
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ip", dest="ip", action="store", type="string")
    parser.add_option("-u", "--user", dest="user", action="store", type="string")
    parser.add_option("-p", "--password", dest="password", action="store", type="string")
#   parser.add_option("-c", "--cloud-account", dest="cloud_account", action="store", type="string")
#   parser.add_option("-f", "--flavor-type", dest="flavor_type", action="store", type="string")
#   parser.add_option("-v", "--volume-type", dest="volume_type", action="store", type="string")
#   parser.add_option("-s", "--security-group", dest="security_group", action="store", type="string")
    (options, args) = parser.parse_args(argv)
#   required = "ip user password cloud_account".split()
    required = "ip user password".split()
    for r in required:
        if options.__dict__[r] is None:
            parser.error("parameter '%s' required" % r)

    json_post_data = json_data_string(options)
    post_response = post_one_click_migration(json_post_data)

    if post_response["id"] is not None:
        wait_to_complete_one_click_migration(post_response["id"])
    else:
        print 'Unable to submit one click migration'


if __name__ == "__main__":
    main(sys.argv)

