#!/usr/bin/env python

# This script decodes the IP and Port of an F5 cookie.
# example string: 839518730.47873.0000
# This script is extended off of the concept from http://penturalabs.wordpress.com/2011/03/29/how-to-decode-big-ip-f5-persistence-cookie-values/ where I have added in the ability to decode the Port in addition to supporting input files containing multiple cookie values.

import struct
import sys


def decode(cookie_value):

	(host, port, end) = cookie_value.split('.')

	(a, b, c, d) = [ord(i) for i in struct.pack("<I", int(host))]

	p = [ord(i) for i in struct.pack("<I", int(port))]
	portOut = p[0]*256 + p[1]


	print "%s.%s.%s.%s:%s" % (a,b,c,d,portOut)

if len(sys.argv) != 3:
        print "Usage: %s input_type encoded_string" % sys.argv[0]
	print "-c Individual cookie value"
	print "-f File Name containing cookie values on each line\n"
	print "ex. %s -c 839518730.47873.0000" % sys.argv[0]
	print "ex. %s -f inputfile.txt" % sys.argv[0]
        exit(1)

if sys.argv[1] == "-c":
	cookie_text = sys.argv[2]
	decode(cookie_text)
if sys.argv[1] == "-f":
	file_name = sys.argv[2]
	with open(file_name,'r') as f:
		for x in f:
			x = x.rstrip()
			if not x: continue
			decode(x)




