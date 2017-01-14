# aws-waf-cidr-list

## Reminder

Still in development...

## Purpose

AWS WAF does not provide the ability of adding a full range of CIDR ranges in its IP Addresses Conditions.  This utility will
take the drop list from SpamHaus and parse it into valid ranges for AWS WAF (/8, /16, /24, /32).

## SpamHaus

Currently for the purposes of my project I use SpamHaus exclusively.  Feel free to modify the script to suit your needs.
