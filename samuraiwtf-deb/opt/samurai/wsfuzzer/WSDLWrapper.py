"""
# Web Services Fuzzer
#
# FILENAME      : WSDLWrapper.py
# AUTHORS       : Cosmin Banciu <ccbanciu [at] gmail dot com>
#               : David Shu <ydpanda [at] gmail dot com>
#               : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Andres Andreu
# DATE          : 12/7/2005
# LAST UPDATE   : 9/3/2010
# ABSTRACT      : A library that wraps SoapUI WSDL Parser up and facilitates
#				: fuzzing attacks against web services.
#               : This tool is meant to be part of a web app pen testers toolkit.
#
# Copyright (c) 2005 - 2010 neuroFuzz, LLC
# Get the latest versions from:
# http://www.neurofuzz.com
#
# This program is distributed in the hope that it will be useful
# to the application security community.  It is in no way written
# to be used for malicious purposes and the target audience are
# penetration testers who have all legal right to perform these
# types of audits against a given target.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# This file is part of WSFuzzer.
#
# WSFuzzer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WSFuzzer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with WSFuzzer. It is in a file named LICENSE.
# If not, see <http://www.gnu.org/licenses/>
"""

import os
import sys
import re
import urlparse
import fileinput
from xml.dom.minidom import parse

from inc import genUtils
from lib import HostChecker
from lib import XMLStringPayloadAnalyzer

class WSDLWrapper(object):
	def __init__(self, wsdl=None, proxy=None, proxyPort=None, bauser = None, bapass = None , fuzzerVersion=0, wsdlFileName=None):
		object.__init__(self)
		self.wsdlURL = wsdl
		self.methods = {}
		self.methodsSoapAction = {}
		self.methodsEndpoint = {}
		self.httpError = False
		self.errorCode = "no code"
		self.proto = ''
		self.host = ''
		self.uri = ''
		self.wsdlFileName = "tmp.xml"  #just used as a tmp file, but could be stored elsewhere to store parsed wsdl data.

		result = self.getInfo(wsdl)
		self.proto = result[0]
		self.host = result[1]
		self.uri = result[2]

		if bauser is not None and bapass is not None: #add basic auth
			self.wsdlURL = re.sub(self.proto + '://',self.proto + '://' + bauser + ":" + bapass + "@",self.wsdlURL)
		if genUtils.detectWindowsOS():
			result = genUtils.getstatusoutput('parseWsdl.bat ' + self.wsdlURL + ' ' + self.wsdlFileName)
		else:
			result = genUtils.getstatusoutput('sh parseWsdl.sh ' + self.wsdlURL + ' ' + self.wsdlFileName)
		if result[0] != 0:
			print "Error occurred while attempting to parse WSDL"
			print result[1]
			exit(0)

		self.cleanFile(self.wsdlFileName)
		self.fh = open(self.wsdlFileName, "r")
		dom = parse(self.fh)
		methodsInXML = dom.childNodes[0].childNodes
		if dom.childNodes[0].localName == "exception":
			print "The Following exception occurred while attempting to parse WSDL"
			print dom.childNodes[0].childNodes[0].nodeValue
			print result[1]
			exit(0)

		for method in methodsInXML:
		    self.methods[method.tagName] = XMLStringPayloadAnalyzer.XMLStringPayloadAnalyzer(method.childNodes[0].nodeValue)
		    self.methodsSoapAction[method.tagName] = method.attributes['soapAction'].value
		    self.methodsEndpoint[method.tagName] = self.getInfo(method.attributes['endpoint'].value)

		dom.unlink()
		self.fh.close()
		os.remove(self.wsdlFileName)

	# NAME     : cleanFile
	# PARAMS   : None
	# RETURN   : Nothing
	# DESC     : Takes in the known XML file
	#            and strips out all unwanted
	#            line endings and strips out
	#            empty spaces.  This was done
	#            because I encountered xml files
	#            with data like >\n<
	#            This method writes the massaged
	#            data back into the original
	#            file object passed in at class level.
	def cleanFile(self, fileName):
		oldFileName  = 'old_' + fileName
		tempFileName = 'temp_' + fileName
		# if there's already an 'old_' prefixed backup file there from
		# a previous run, remove it...
		if os.path.isfile(oldFileName):
			os.remove(oldFileName)
		tempFile = open(tempFileName, 'w')
		for line in fileinput.input(fileName):
			#TODO change o reflect the same logic as XMlStringpayload
			line = line.replace("\n", "")
			line = line.strip()
			tempFile.write(line)
		tempFile.close()
		# Rename the original file by prefixing it with 'old_'
		os.rename(fileName, oldFileName)
		# Rename the temporary file to what the original was named...
		os.rename(tempFileName, fileName)
	# EOF: cleanFile

    # NAME     : getInfo
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : parses URL and extracts info about
    #			protocol, host, and path
	def getInfo(self, endpoint):
		u = urlparse.urlparse(endpoint)
		self.checkHost(endpoint)
		return u
	# EOF: getInfo

    # NAME     : checkHost
    # PARAMS   : host
    # RETURN   : Nothing
    # DESC     : Attempts to establish a connection to given host, on given port
    #			and protocol
	def checkHost(self, host):
		#create HostChecker obj
		hchecker = HostChecker.HostChecker()
		# check host and die if host not available
		if not hchecker.isHostAvailable(host):
			print "The following host: '%s' is not reachable, shutting down" % host
			sys.exit(0)
	# EOF: checkHost

    # NAME     : getParamsOfMethod
    # PARAMS   : methodName
    # RETURN   : list
    # DESC     : returns a list of parameters
    #			for the given method
	def getParamsOfMethod(self, methodName=None):
		#get params of method
		return self.methods[methodName].getParamsHash()
	# EOF: getParamsOfMethod

    # NAME     : getTypesOfParams
    # PARAMS   : methodName
    # RETURN   : array
    # DESC     : returns an array that holds the
    #			 data type values for the parameters
    #			 of the given method
	def getTypesOfParams(self, methodName=None):
		paramsHash = self.methods[methodName].getParamsHash()
		t = []
		for param in paramsHash.keys():
			t.append(paramsHash[param])
		return t
	# EOF: getTypesOfParams

    # NAME     : getUri
    # PARAMS   : methodName
    # RETURN   : string
    # DESC     : returns the target URI
	def getUri(self, methodName=None):
		return self.uri
	# EOF: getUri

    # NAME     : getSoapAction
    # PARAMS   : methodName
    # RETURN   : string
    # DESC     : returns the methods SoapAction
	def getSoapAction(self, methodName=None):
		#TODO check to see if soapAction is null or empty? then return none
		if self.methodsSoapAction[methodName]:
			return self.methodsSoapAction[methodName]
		else:
			return ""
	# EOF: getSoapAction


    # NAME     : getMethods
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns a list of method names
    #			discovered for given target WSDL
	def getMethods(self):
		return self.methods.keys()
	# EOF: getMethods

    # NAME     : getProtocol
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			the protocol
	def getProtocol(self):
		return self.proto
	# EOF: getProtocol

    # NAME     : getHost
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			the target host
	def getHost(self, methodName):
		result = self.methodsEndpoint[methodName][1]
		#result = result.split(":")[0] #remove port (:80) why remove it?
		return result
	# EOF: getHost

    # NAME     : getService
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			the target web service URI
	def getService(self, methodName):
		return self.methodsEndpoint[methodName][2]
	# EOF: getService

    # NAME     : useTLS
    # PARAMS   : None
    # RETURN   : Bool
    # DESC     : returns true if HTTPS is
    #			 the protocol in use and
    #			 False otherwise
	def useTLS(self):
		if self.proto == "https":
			return True
		else:
			return False
	# EOF: useTLS

    # NAME     : idSelf
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns an identifying
    #			 string
	def idSelf(self):
		return "WSDLWrapper"
	# EOF: idSelf

	def getFinalPayloadForMethod(self, methodName):
		return self.methods[methodName].finalPayload
	# EOF: invokeMethod

    # NAME     : invokeMethodGetPayload
    # PARAMS   : methodName, args, IDSEvasion
    # RETURN   : XML
    # DESC     : retrieves a known xml payload for the method

	def invokeMethodGetPayload(self, methodName, args, IDSEvasion):
		#args is a list of all parameters for the target method
		return self.methods[methodName].finalPayload.toxml()
	# EOF: invokeMethodGetPayload

