# aws-waf-cidr-list

## Disclaimer

You'll need to configure AWS CLI on the client you are running this script from.

## Purpose

AWS WAF does not provide the ability to add a full range of CIDR ranges in its IP Addresses Conditions.  This utility will:

1) Delete all IP Addresses in specified IP Set
2) Take the drop list from SpamHaus and parse it into valid ranges for AWS WAF (/8, /16, /24, /32)
3) Chunk the valid ranges list into blocks of 1000 and append the ranges to an IP Set using Boto3 (GUID of IP Set needs to be specified in converter.conf)

## SpamHaus

Currently for the purposes of my project I use SpamHaus exclusively.  Feel free to modify the script to suit your needs.