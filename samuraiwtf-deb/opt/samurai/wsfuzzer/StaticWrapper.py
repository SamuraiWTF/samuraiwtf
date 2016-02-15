"""
# Web Services Fuzzer
#
# FILENAME      : StaticWrapper.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 03/24/2007
# LAST UPDATE   : 8/29/2010
# ABSTRACT      : A library that gathers up details for fuzzing attacks
#               : against web services based on static XML provided.
#               : This tool is meant to be part of a web app pen testers toolkit.
#
# Copyright (c) 2007 - 2010 neuroFuzz, LLC
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

import sys
import urlparse
import StringIO

from lib import HostChecker

class StaticWrapper(object):
	def __init__(self, xmlpa=None):
		object.__init__(self)
		self.proto = self.method = self.host = self.uri = ''
		self.xmlpayload = StringIO.StringIO()
		self.paramType = {}
		self.httpError = False
		self.xmlpa = xmlpa
		self.soapAction = None


	# NAME     : setSoapAction
    # PARAMS   : soapAction
    # RETURN   : Nothing
    # DESC     : sets SoapAction for this wrapper
	def setSoapAction(self, soapAction = None):
		self.soapAction = soapAction
	# EOF: setSoapAction


	# NAME     : getSoapAction
    # PARAMS   : methodName
    # RETURN   : string
    # DESC     : gets the SoapAction for this wrapper
	def getSoapAction(self, methodName = None):
		return self.soapAction
	# EOF: getSoapAction

    # NAME     : setPayload
    # PARAMS   : payload
    # RETURN   : Nothing
    # DESC     : sets static XML from a file
    #			 obj gathered in WSFuzzer
	def setPayload(self, payloadFileName):
		self.xmlpayload = self.xmlpa.finalPayload
	# EOF: setPayload

    # NAME     : setHost
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : sets a string identifying
    #			the target host
	def setHost(self, host):
		#create HostChecker obj
		hchecker = HostChecker.HostChecker()
		# check host and die if host not available
		if hchecker.isHostAvailable(host) is False:
			print "Sorry but the submitted host is not reachable"
			sys.exit(0)
		self.host = host
	# EOF: setHost

    # NAME     : setMethod
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : sets a string identifying
    #			the target Method
	def setMethod(self, method):
		self.method = method
	# EOF: setMethod

    # NAME     : setUri
    # PARAMS   : Str
    # RETURN   : Nothing
    # DESC     : sets a string identifying
    #			the target URI
	def setUri(self, uri):
		self.uri = uri
	# EOF: setUri

    # NAME     : setProto
    # PARAMS   : Str
    # RETURN   : Nothing
    # DESC     : sets a string identifying
    #			the target protocol
	def setProto(self, host):
		u = urlparse.urlparse(host)
		self.proto = u[0]
	# EOF: setProto

    # NAME     : getUri
    # PARAMS   : methodName
    # RETURN   : string
    # DESC     : returns the target URI
	def getUri(self, methodName=None):
		return self.uri
	# EOF: getUri

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

    # NAME     : setParamType
    # PARAMS   : method, param, type
    # RETURN   : Nothing
    # DESC     : populates a hash (dictionary) with
    #			 the param name as the key and the
    #			 respective value
	def setParamType(self, param, type):
		self.paramType[param] = type
	# EOF: setParamType

    # NAME     : getTypesOfParams
    # PARAMS   : methodName
    # RETURN   : array
    # DESC     : returns an array that holds the
    #			 date type values for the parameters
    #			 of the target method
	def getTypesOfParams(self, methodName=None):
		t = []
		for type in self.paramType:
			t.append(self.paramType[type])

		return t
	# EOF: getTypesOfParams

    # NAME     : getInfo
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : parses URL and extracts info about
    #			 protocol, host, and path
	def getInfo(self):
		u = urlparse.urlparse(self.endpointURL)

		self.proto = u[0]
		self.host = u[1]
		self.uri = u[2]
	# EOF: getInfo

    # NAME     : getProtocol
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			 the protocol
	def getProtocol(self):
		return self.proto
	# EOF: getProtocol

    # NAME     : getHost
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			 the target host
	def getHost(self):
		return self.host
	# EOF: getHost

    # NAME     : getService
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			 the target web service URI
	def getService(self):
		return self.uri
	# EOF: getService

    # NAME     : idSelf
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns an identifying
    #			 string
	def idSelf(self):
		return "StaticWrapper"
	# EOF: idSelf

    # NAME     : invokeMethodGetPayload
    # PARAMS   : methodName, args, IDSEvasion
    # RETURN   : XML as string
    # DESC     : returns the format string based
    #			 XML payload to be used in the attacks
	def invokeMethodGetPayload(self, methodName, args, IDSEvasion):
		return self.xmlpayload.toxml()
	# EOF: invokeMethodGetPayload

