import sys
import re

env_file_path = '/usr/local/osmosix/etc/userenv'
inventory_loc = '/opt/remoteFiles/appPackage/inventory'
known_host_loc = '/home/cliqruser/known_host_list'
ssh_key_loc = '/home/cliqruser/.ssh/cliqruserKey'
service_map = {}

def create_inventory_file(local_ip):
    local_hostname = ''
    inv_file = open(inventory_loc, 'a')
    host_file = open(known_host_loc, 'a')
    for service_name, ips in service_map.iteritems():
        inv_file.write("[" + service_name + "]\n")
        for count, ip in enumerate(ips.strip("'").split(",")):
                hostname = service_name.replace('_','-') + "-" + `count` + '.ciscozeus.io'
                if ip == local_ip:
                        local_hostname = hostname
                inv_file.write(hostname + ' ' + 'ansible_ssh_host=' + ip.strip() + ' ' + 'ansible_ssh_private_key_file=' + ssh_key_loc + ' ' + 'id=' + `count` + '\n')
                host_file.write(ip.strip()+'\n')
    inv_file.close()
    host_file.close()
    print local_hostname

def main():
    #check for private ips
    lines = [line for line in open(env_file_path) if re.findall(r'CliqrTier_[\w]*_IP=',line) and "PUBLIC" not in line]
    host_info_str = [line.split(" ")[1] for line in lines]
    service_info = [line.split("=") for line in host_info_str]
    for service in service_info:
        service_name = re.match(r'CliqrTier_(\w*)_IP', service[0]).group(1)
        private_ips = service[1].replace('"','').rstrip()
        #print service_name, private_ips
        service_map[service_name] = private_ips
    create_inventory_file(sys.argv[1])


if __name__ == "__main__":
        main()
