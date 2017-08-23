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
app_name = data['app_name']

#a10_api_server ='https://api.a10networks.com/api/v2'
#provider = 'root'
#tenant = 'Cisco'
#a10_user = 'movaswan@cisco.com'
#a10_user_passwd = 'C1sco12345'
#cluster_name = 'MoMagic112'
#app_name = 'Jenkins112'

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

def get_ladc_cluster(cluster_name):

    session_request = urllib2.Request( a10_api_server + '/cspcluster/' + cluster_name)
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request)

    session_json_data = json.loads(response.read().decode("utf-8"))

    return session_json_data['csps']


def delete_ladcs(cluster_name, ladcs):
    for ladc in ladcs:
        
        session_request = urllib2.Request( a10_api_server + '/cspcluster/' + cluster_name + '/csps/' + ladc['cspId'])
        session_request.get_method = lambda: 'DELETE'
        headers = {
          "provider": provider,
          "tenant": tenant,
          "Content-Type": "application/json",
          "Authorization": session_token
        }
        for key, value in headers.items():
            session_request.add_header(key, value)

        response = urllib2.urlopen(session_request, 'null')

    return True


def delete_ladc_cluster(cluster_name):
    session_request = urllib2.Request( a10_api_server + '/cspcluster/' + cluster_name)
    session_request.get_method = lambda: 'DELETE'
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request, 'null')

    return True

def delete_app(app_name):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_name + '?force=true')
    session_request.get_method = lambda: 'DELETE'
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request, 'null')

    return True


session_token = _get_session_token()
delete_app(app_name)
ladcs = get_ladc_cluster(cluster_name)
delete_ladcs(cluster_name, ladcs)
delete_ladc_cluster(cluster_name)
