import json
import urllib2
from base64 import b64encode

data = json.loads(open('params.json', 'r').read())

a10_api_server = data['a10_api_server']
provider = data['provider']
tenant = data['tenant']
a10_user = data['a10_user']
a10_user_passwd = data['a10_user_passwd']
cluster_name = data['cluster_name']


def _get_session_token():

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

def create_ladc_cluster():
    session_request = urllib2.Request( a10_api_server + '/cspcluster')
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
            json.dumps({"name": cluster_name, "state": "ACTIVE"}).encode("utf-8"))

    cluster_json_data = json.loads(response.read().decode("utf-8"))
    return cluster_json_data["clusterId"]


session_token = _get_session_token()
cluster_id=create_ladc_cluster()
print cluster_id
