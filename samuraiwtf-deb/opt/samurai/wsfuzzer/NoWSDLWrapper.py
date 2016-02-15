"""
# Web Services Fuzzer
#
# FILENAME      : NoWSDLWrapper.py
# AUTHORS       : David Shu <ydpanda [at] gmail dot com>
#               : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 12/7/2005
# LAST UPDATE   : 8/29/2010
# ABSTRACT      : A library that wraps SOAPpy up and facilitates fuzzing attacks
#               : against web services without the use of WSDL.
#               : This tool is meant to be part of a web app pen testers toolkit.
#
# Copyright (c) 2006 - 2010 neuroFuzz, LLC
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

from lib import HostChecker

class NoWSDLWrapper(object):
	def __init__(self, endpoint=None, namespace=None, **kw):
		object.__init__(self)
		self.endpointURL = endpoint
		self.namespaceURI = namespace
		self.config = WSDL.Config
		self.config.dumpHeadersIn = 1
		self.config.dumpHeadersOut = 1
		self.config.dumpSOAPIn = 1
		self.config.dumpSOAPOut = 1
		self.config.returnFaultInfo = 1
		self.httpError = False
		self.errorCode = "no message"
		self.proto = ''
		self.host = ''
		self.uri = ''
		self.soapAction = None
		self.getInfo()
		self.paramType = {}
		try:
			self.proxy = SOAPProxy(
				self.endpointURL,
				namespace=self.namespaceURI,
				config=self.config,
				**kw
			)
		except Exception, reason:
			sys.exit(0)


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
    # NAME     : setParamType
    # PARAMS   : method, param, type
    # RETURN   : Nothing
    # DESC     : populates a hash (dictionary) with
    #			 the param name as the key and the
    #			 respective value
	def setParamType(self, method, param, type):
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
    #			protocol, host, and path
	def getInfo(self):
		u = urlparse.urlparse(self.endpointURL)
		#create HostChecker obj
		hchecker = HostChecker.HostChecker()

		self.proto = u[0]
		self.host = u[1]
		self.uri = u[2]
		# check host and die if host not available
		if hchecker.isHostAvailable(self.endpointURL) is False:
			print "Sorry but the submitted host is not reachable"
			sys.exit(0)
	# EOF: getInfo

    # NAME     : getUri
    # PARAMS   : methodName
    # RETURN   : string
    # DESC     : returns the target URI
	def getUri(self, methodName=None):
		return self.proxy.path
	# EOF: getUri

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
	def getHost(self):
		return self.host
	# EOF: getHost

    # NAME     : getService
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns a string identifying
    #			the target web service URI
	def getService(self):
		return self.uri
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
		return "NoWSDLWrapper"
	# EOF: idSelf

    # NAME     : invokeMethod
    # PARAMS   : methodName, args, IDSEvasion
    # RETURN   : response
    # DESC     : invokes the target SOAP method using
    #			the passed in args and IDSEvasion value
	def invokeMethod(self, methodName, args, IDSEvasion):
		try:
			function = self.proxy.__getattr__(methodName)
			self.proxy.path = IDSEvasion
			response = function(**args)
		except HTTPError, (code,msg):
			self.httpError = True
			self.errorCode = reason
			response = "HTTP Error"
		except:
			response = "Soap Fault"
		return response
	# EOF: invokeMethod

    # NAME     : invokeMethodGetPayload
    # PARAMS   : methodName, args, IDSEvasion
    # RETURN   : XML
    # DESC     : invokes the target SOAP method using
    #			 the passed in args and IDSEvasion value
    #			 in order to extract a known good XML payload
	def invokeMethodGetPayload(self, methodName, args, IDSEvasion):
		#args is a list of all parameters for the target method
		try:
			payload = self.proxy.getPayload(methodName, args, {})
		except HTTPError, (code,msg):
			# Caught HTTP Error
			print "Http Error code: %s" % code
			self.httpError = True
			payload = "HTTP Error"
		except:
			payload = "XML Fault"

		return payload
	# EOF: invokeMethodGetPayload

