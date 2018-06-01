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
domain_name = data['domain_name']
cluster_name = data['cluster_name']
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

def create_app(app_name):
    session_request = urllib2.Request( a10_api_server + '/applications')
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
            json.dumps({"name": app_name, "state": "ACTIVE","description":"MYAPP","productId":"LADC-Pro"}).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    return json_data["id"]

def create_domain_endpoint(app_name, domain_name):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_name + '/hosts')
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
            json.dumps({"name":"default-host","description":"default-host","domains":[{"fqdn":domain_name}],"transportPropertiesList":[{"name":"http_80","port":80}]}).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    create_domain_endpoint_policies(app_name)
    return json_data["id"]

def create_domain_endpoint_policies(app_name):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_name + '/hosts/default-host/policies')
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
            json.dumps(
                {"name":"logging","state":"ACTIVE","type":"logging","perRequestLogLevel":"all","errors":["FourXX","FiveXX","WAF"],"beginLogging":1496393606549,"endLogging":1496397206549,"appOnBoardLoggingDuration":60,"configChangeLoggingDuration":15,"onBoardLogsEnabled":"true","configChangeLogsEnabled":"true","customize":"false","customRange":"false"}
                ).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    return True

def create_service_endpoint(app_id):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_id + '/hosts/default-host/services/_import')
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

    response = urllib2.urlopen(session_request,
            json.dumps(
                {"name":"default-service","description":"This service is created by system to match any URLs at the end. A matching Smart Flow has also been created for you to configure policies for traffic that does not match any other condition.","condition":"URL:ciPrefix:\"/\"","serverGroup":{"name":"defaultServerGroup","servers": servers,"loadBalancingAlgorithmPolicy":{"name":"defaultLBpolicy","state":"ACTIVE","method":"least_conn","type":"serverAlgo"},"clientSSLPolicy":{"name":"defaultClientSSLpolicy","state":"INACTIVE","validateUpstreamCert":"false","cipherVersions":[],"sslVersions":[],"sendServerName":"false","type":"clientSSL"},"sessionPersistencePolicy":{"state":"INACTIVE","method":"cookie_sticky","type":"sessionPersistence","name":"defaultSessionPersistence"},"outOfBandMonitorPolicy":{"state":"ACTIVE","oobInterval":10,"oobTimeout":10,"oobType":"tcp","oobHttpUrl":"","type":"monitor","name":"OutOfBandMonitor"},"policies":[{"type":"serverLimits","name":"serverLimitsPolicy","readTimeout":300,"sendTimeout":300}]}}
                ).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    return json_data["id"]

def create_smartflow(app_id, service_id):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_id + '/hosts/default-host/services/' + service_id + '/smartflows')
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
            json.dumps(
                {"name":"default-smartflow","condition":"URL:ciPrefix:\"/\"","flowType":"allow"}
                ).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    return json_data["id"]

def create_smartflow_policies(app_id, service_id, smartflow_id):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_id + '/hosts/default-host/services/' + service_id + '/smartflows/' + smartflow_id + '/policies')
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request,
            json.dumps(
                {"type":"headerRewrite","name":"headerRewrite","state":"ACTIVE","rules":[{"status":"true","type":"reqHdrAdd","name":"X-Forwarded-For","value":"$http_x_forwarded_for, $remote_addr"},{"status":"true","type":"reqHdrAdd","name":"X-Forwarded-Proto","value":"$scheme"},{"status":"true","type":"reqHdrAdd","name":"X-Forwarded-Port","value":"$server_port"}]}
                ).encode("utf-8"))

    json_data = json.loads(response.read().decode("utf-8"))
    return True

def associate_app_cluster(app_id, cluster_name):
    session_request = urllib2.Request( a10_api_server + '/applications/' + app_id + '/cspclusters/' + cluster_name)
    session_request.get_method = lambda: 'PUT'
    headers = {
      "provider": provider,
      "tenant": tenant,
      "Content-Type": "application/json",
      "Authorization": session_token
    }
    for key, value in headers.items():
        session_request.add_header(key, value)

    response = urllib2.urlopen(session_request, 'null')

    #json_data = json.loads(response.read().decode("utf-8"))
    return True


session_token = _get_session_token(a10_user, a10_user_passwd)
app_id = create_app(app_name)
domain_endpoint_id = create_domain_endpoint(app_id, domain_name)
service_id = create_service_endpoint(app_id)
smartflow_id = create_smartflow(app_id, service_id)
create_smartflow_policies(app_id, service_id, smartflow_id)
associate_app_cluster(app_id, cluster_name)
