from netaddr import IPNetwork
import requests
import configparser

print 'STARTING'
count = 0

#config file
config = configparser.ConfigParser()
config.read("converter.conf")

#get url and fetch content
url = config['DEFAULT']['DropListUrl']
r = requests.get(url)
lines = r.content.splitlines()

for line in lines:
	if line[0]!=';':
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
			print subnet

print 'FINISHING TOTAL: ' + str(count) 