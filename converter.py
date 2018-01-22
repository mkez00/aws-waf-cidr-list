from netaddr import IPNetwork
import requests
import configparser
import boto3
import sys

def getopts():
    from sys import argv
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

# action = INSERT | DELETE
def create_update(ip_address, action):
    update = {}
    update['Action'] = action
    update['IPSetDescriptor'] = create_descriptor('IPV4', ip_address)
    print str(update)
    return update


def create_descriptor(value_type, value):
    descriptor = {}
    descriptor['Type'] = value_type
    descriptor['Value'] = value
    return descriptor


def get_new_change_token(client):
    change_token = client.get_change_token()
    return change_token.get('ChangeToken')


def get_ip_set(client, ip_set_id):
    return client.get_ip_set(IPSetId=ip_set_id)


def remove_ip_set_entries(client, ip_set_id):
    print 'DELETING IP SET ENTRIES'
    list_ip_set = get_ip_set(client, ip_set_id)
    count = 0
    update_list = []
    for ip_set in list_ip_set.get('IPSet').get('IPSetDescriptors'):
        count += 1
        update_list.append(create_update(ip_set.get("Value"), 'DELETE'))
    batch_update(client, ip_set_id, update_list)


# Updates the ip set in a batch
def update_ip_set_bulk(client, ip_set_id, updates):
    change_token_id = get_new_change_token(client)
    client.update_ip_set(
        IPSetId=ip_set_id,
        ChangeToken=change_token_id,
        Updates=updates
    )


def get_config_parser():
    config = configparser.ConfigParser()
    configfile = "converter.conf"
    myargs = getopts()
    if '-config' in myargs:
        configfile = str(myargs['-config'])
    config.read(configfile)
    return config


def get_profile():
    profile = get_config_parser()['DEFAULT']['Profile']
    myargs = getopts()
    if '-profile' in myargs:
        profile = str(myargs['-profile'])
    return profile


def get_boto_client():
    profile = get_profile()
    if profile:
        print 'Using profile: ' + profile
        session = boto3.Session(profile_name=profile)
        return session.client('waf-regional')
    else:
        return boto3.client('waf-regional')


def insert_into_ip_set_from_drop_list(client, ip_set_id):
    print 'CREATING IP SET ENTRIES'
    count = 0
    # get url and fetch content
    url = get_config_parser()['DEFAULT']['DropListUrl']
    r = requests.get(url)
    lines = r.content.splitlines()

    update_list = []
    for line in lines:
        if line[0] != ';':
            cidr = line.split(';')[0]
            cidr_split = cidr.split('/')
            cidr_range = int(cidr_split[1])

            if cidr_range <= 8:
                cidr_range = 8
            elif cidr_range <= 16:
                cidr_range = 16
            elif cidr_range <= 24:
                cidr_range = 24
            else:
                cidr_range = 32

            net = IPNetwork(cidr)
            subnets = net.subnet(cidr_range)
            for subnet in subnets:
                count += 1
                update_list.append(create_update(str(subnet), 'INSERT'))
    batch_update(client, ip_set_id, update_list)
    print 'Inserted: ' + str(count)


def batch_update(client, ip_set_id, updates_list):
    batch_update_list = []
    batch_count = 0
    for update in updates_list:
        batch_update_list.append(update)
        batch_count += 1
        if batch_count == 1000:
            update_ip_set_bulk(client, ip_set_id, batch_update_list)
            batch_count = 0
            batch_update_list = []
    if len(batch_update_list) > 0:
        update_ip_set_bulk(client, ip_set_id, batch_update_list)


def get_ip_set_id():
    ip_set_id = get_config_parser()['DEFAULT']['IpSetId']
    myargs = getopts()
    if '-ipsetid' in myargs:
        ip_set_id = str(myargs['-ipsetid'])
    return ip_set_id


def main():
    client = get_boto_client()
    ip_set_id = get_ip_set_id()
    remove_ip_set_entries(client, ip_set_id)
    insert_into_ip_set_from_drop_list(client, ip_set_id)


print 'STARTING!!!!'
main()
print 'FINISHING'
