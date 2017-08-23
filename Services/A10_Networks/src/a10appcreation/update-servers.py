import json
import urllib2
from base64 import b64encode

data = json.loads(open('params.json', 'r').read())

a10_api_server = data['a10_api_server']
provider = data['provider']
tenant = data['tenant']
a10_user = data['a10_user']
a10_user_passwd = data['a10_user_passwd']
app_name = data['app_name']
service_name = data['service_name']
server_ips = data['server_ips']


def _get_session_token(a10_user, a10_user_passwd):

    session_request = urllib2.Request( a10_api_server + '/sessions')

    cred = a10_user + ':' + a10_user_passwd
    bas64 = b64encode(bytes(cred))
    auth = "Basic " + bas64.decode("ascii")
    headers = {
      "provider": provider,
      "Content-Type": "application/json",
      "Authorization": auth
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
         json.dumps({"userId": a10_user}).encode("utf-8"))

    session_json_data = json.loads(response.read().decode("utf-8"))
    return 'Session ' + session_json_data['id']


def get_server_group(app_id, service_id):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_id + '/hosts/default-host/services/' + service_id + '/servergroups/defaultServerGroup?options=loadDetails')

    headers = {
      "provider": provider,
      "tenant": tenant,
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request)

    json_data = json.loads(response.read().decode("utf-8"))
    return json_data

def update_servers(app_id, service_id, server_group):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_id + '/hosts/default-host/services/' + service_id + '/servergroups/_import')

    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    servers = []
    for ip in server_ips:
        servers.append({"state":"ACTIVE","ipAddress": ip ,"port":80,"weight":1,"maxFails":3,"failTimeout":10,"backup":"false"})

    server_group['servers'] = servers

    response = urllib2.urlopen(session_request,
            json.dumps(server_group).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    return json_data["id"]


session_token = _get_session_token(a10_user, a10_user_passwd)
server_group = get_server_group(app_name, service_name)
update_servers(app_name, service_name, server_group)
