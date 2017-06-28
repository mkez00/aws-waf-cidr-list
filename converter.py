from netaddr import IPNetwork
import requests
import configparser
import boto3


def createUpdate(ipAddr):
    update = {}
    update['Action'] = 'INSERT'
    update['IPSetDescriptor'] = createDescriptor('IPV4', ipAddr)
    return update


def createDescriptor(valueType, value):
    descriptor = {}
    descriptor['Type'] = valueType
    descriptor['Value'] = value
    return descriptor


def getNewChangeTokenId(client):
    changeToken = client.get_change_token()
    return changeToken.get('ChangeToken')


def updateIpSet(client, ipSetId, ipAddr):
    changeTokenId = getNewChangeTokenId(client)
    response = client.update_ip_set(
        IPSetId=ipSetId,
        ChangeToken=changeTokenId,
        Updates=[
            {
                'Action': 'INSERT',
                'IPSetDescriptor': {
                    'Type': 'IPV4',
                    'Value': ipAddr
                }
            },
        ]
    )
    print 'Updated IP set'
    return


def updateIpSetBulk(client, ipSetId, updates):
    print 'Batch Size: ' + str(len(updates))
    changeTokenId = getNewChangeTokenId(client)
    response = client.update_ip_set(
        IPSetId=ipSetId,
        ChangeToken=changeTokenId,
        Updates=updates
    )
    return


def getConfigParser():
    config = configparser.ConfigParser()
    config.read("converter.conf")
    return config


def getBotoClient():
    return boto3.client('waf-regional')


def traverseListAndUpdateIpSetBulk(client, ipSetId):
    count = 0
    # get url and fetch content
    url = config['DEFAULT']['DropListUrl']
    r = requests.get(url)
    lines = r.content.splitlines()

    updatesList = []
    for line in lines:
        if line[0] != ';':
            cidr = line.split(';')[0]
            cidrSplit = cidr.split('/')
            cidrRange = int(cidrSplit[1])

            if cidrRange <= 8:
                cidrRange = 8
            elif cidrRange <= 16:
                cidrRange = 16
            elif cidrRange <= 24:
                cidrRange = 24
            else:
                cidrRange = 32

            net = IPNetwork(cidr)
            subnets = net.subnet(cidrRange)
            for subnet in subnets:
                count += 1
                updatesList.append(createUpdate(str(subnet)))
                print subnet
    batchUpdate(client, ipSetId, updatesList)
    return count


def batchUpdate(client, ipSetId, updatesList):
    batchUpdate = []
    batchCount = 0
    for update in updatesList:
        batchUpdate.append(update)
        batchCount += 1
        if batchCount == 1000:
            updateIpSetBulk(client, ipSetId, batchUpdate)
            batchCount = 0
            batchUpdate = []
    updateIpSetBulk(client, ipSetId, batchUpdate)


def traverseListAndUpdateIpSet(client, ipSetId):
    count = 0
    # get url and fetch content
    url = config['DEFAULT']['DropListUrl']
    r = requests.get(url)
    lines = r.content.splitlines()

    for line in lines:
        if line[0] != ';':
            cidr = line.split(';')[0]
            cidrSplit = cidr.split('/')
            cidrRange = int(cidrSplit[1])

            if cidrRange <= 8:
                cidrRange = 8
            elif cidrRange <= 16:
                cidrRange = 16
            elif cidrRange <= 24:
                cidrRange = 24
            else:
                cidrRange = 32

            net = IPNetwork(cidr)
            subnets = net.subnet(cidrRange)
            for subnet in subnets:
                count += 1
                updateIpSet(client, ipSetId, str(subnet))
                print subnet
    return count


print 'STARTING!!!!'

# configure stuff
client = getBotoClient()
config = getConfigParser()
ipSetId = config['DEFAULT']['IpSetId']

count = 0
count = traverseListAndUpdateIpSetBulk(client, ipSetId)
print 'FINISHING TOTAL: ' + str(count)
