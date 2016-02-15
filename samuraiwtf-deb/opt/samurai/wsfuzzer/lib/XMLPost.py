"""
# Web Services Fuzzer
#
# FILENAME      : XMLPost.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 6/20/2006
# LAST UPDATE   : 8/29/2010
# ABSTRACT      : A simple client that will perform HTTP POST requests independent
#               : of any other SOAP client.  This class performs the raw minimum
#               : HTTP functions necessary to act as a SOAP client.  But it is
#               : not a full blown SOAP client in that it doesnt parse WSDL for
#               : instance.
#               : This tool is meant to be part of a web app pen testers toolkit.
#
# Copyright (c) 2006 - 2010 neuroFuzz, LLC
# Get the latest versions from:
# http://www.neurofuzz.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WSFuzzer; if not, write to:
# Free Software Foundation, Inc.
# 51 Franklin St, Fifth Floor
# Boston, MA  02110-1301  USA
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
"""

import httplib
import socket
import re
import base64
import StringIO

import XMLResponsePayloadAnalyzer
import StopWatch

'''
   XMLPost is a simple class that will perform
   HTTP POST requests to a given target.
   This was created to be able to inject
   malformed XML or dangerous XML which
   would not be allowed by SOAP clients that
   adhere to XML rules and sensible data.
'''
class XMLPost(object):
    def __init__(self, host=None, generate=False, soapStr=None, method=None, service=None,
                 https=False, keyfile=None, certfile=None, proxy=None, proxyport=None, version=0):
        object.__init__(self)
        self.host = self.sanitizeHost(host)
        self.method = ""
        self.service = service
        self.requestTracker = []
        self.version = version
        self.proxy = proxy
        self.proxyport = proxyport
        self.https = https
        self.alterHost = False
        self.operationTimeout = False
        self.soapVersion = "1.1"

        # create httplib connection
        if (self.proxy and self.proxyport and https and (keyfile is None and certfile is None)):
            '''
                Proxy servers don't seem to like this.  And this prog seems to
                hang when that happens.  Researching it shows that its a
                Python issue.
            '''
            print "Due to a limitation within Python, \nHTTPS requests through",
            print "Proxy servers are not fully supported yet.  No guarantees of",
            print "this functionality working ......"
            self.ws = httplib.HTTPSConnection(self.proxy, self.proxyport)
        elif (self.proxy and self.proxyport and not https and (keyfile is None and certfile is None)):
            self.ws = httplib.HTTPConnection(self.proxy, self.proxyport)
        elif (https and (keyfile is not None and certfile is not None)):
            '''
                According to http://docs.python.org/lib/module-httplib.html
                key_file is the name of a PEM formatted file that contains
                your private key.
                cert_file is a PEM formatted certificate chain file.
                Warning: This does not do any certificate verification
            '''
            self.ws = httplib.HTTPSConnection(self.host,
                                              key_file=keyfile,
                                              cert_file=certfile)
        elif (https and (keyfile is None and certfile is None)):
            self.ws = httplib.HTTPSConnection(self.host)
        else:
            self.ws = httplib.HTTPConnection(self.host)

        self.response = self.responseVersion = self.responseCode = self.responseMsg = \
        self.responseHeaders = self.responseData = self.basicAuthUser = self.basicAuthPass = \
        self.action = None
        self.sw = StopWatch.StopWatch()

        if generate == True and method:
            self.method = method
            # we will generate XML here, (self.method), eventually
        elif generate == False and soapStr:
            # xml is passed in via a StringIO object
            if type(soapStr) is dict:
                self.soapStr = soapStr.keys()[0].getvalue().strip()
            elif type(soapStr) is str: # dont for XDos attacks as XML payload is a String
                self.soapStr = soapStr.strip()
            else:
                self.soapStr = str(soapStr.getvalue().strip())

    # NAME     : sanitizeHost
    # PARAMS   : Str
    # RETURN   : Str
    # DESC     : Sanitizes the submitted host string
    #            to ensure that the protocol is stripped
    #            out. HTTPLib requires a host to be submitted
    #            in this form.
    def sanitizeHost(self, host):
        if host.startswith('http://'):
            return host[7:len(host)]
        if host.startswith('https://'):
            return host[8:len(host)]
        return host
    # EOF: sanitizeHost

    # NAME     : generateRequestHeaders
    # PARAMS   : service
    # RETURN   : Nothing
    # DESC     : Sets all header and Request data for
    #            the POST request.  Also sets the same
    #            data into array requestTracker for
    #            documentation later.
    def generateRequestHeaders(self, service, charset="UTF-8"):
        '''
            According to RFC 3023, if the media type given in the Content-Type
            HTTP header is text/xml, text/xml-external-parsed-entity,
            or a subtype like text/AnythingAtAll+xml,
            then the encoding attribute of the XML declaration within the document
            is ignored completely, and the character encoding is:

            1. the encoding given in the charset parameter of the Content-Type HTTP header, or
            2. us-ascii.
        '''

        if type(self.soapStr) is str:
            l = len(self.soapStr)
        elif type(self.soapStr) is 'instance':
            l = len(self.soapStr.getvalue())
        else:
        	# unicode??
        	l = len(str(self.soapStr))

        if self.proxy and self.proxyport:
            if not self.host.startswith("http"):
                if self.https:
                    self.host = "https://%s" % self.host
                else:
                    self.host = "http://%s" % self.host
            self.ws.putrequest('POST', (self.host + service), skip_host=1, skip_accept_encoding=1)
            self.requestTracker.append("POST %s HTTP/1.1" % (self.host + service))
        else:
            self.ws.putrequest('POST', service, skip_host=1, skip_accept_encoding=1)
            self.requestTracker.append("POST %s HTTP/1.1" % service)
        if self.alterHost is False:
            self.ws.putheader('Host', self.host)
            self.requestTracker.append("Host: %s" % self.host)
        else:
            self.ws.putheader('Host', self.alterHost)
            self.requestTracker.append("Host: %s" % self.alterHost)
        if self.version > 0:
            self.ws.putheader('User-Agent', 'WSFuzzer-%s' % self.version)
            self.requestTracker.append('User-Agent: WSFuzzer-%s' % self.version)
        else:
            self.ws.putheader('User-Agent', 'WSFuzzer')
            self.requestTracker.append('User-Agent: WSFuzzer')
        # This is for SOAP 1.1
        if self.soapVersion == "1.1":
            self.ws.putheader('Content-type', 'text/xml; charset=\"%s\"' % charset)
            self.requestTracker.append('Content-type: text/xml; charset=\"%s\"' % charset)
        # for SOAP 1.2 the content-type header is now structured as such:
        # Content-Type: application/soap+xml; charset="utf-8"
        elif self.soapVersion == "1.2":
            self.ws.putheader('Content-type', 'application/soap+xml; charset=\"%s\"' % charset)
            self.requestTracker.append('Content-type: application/soap+xml; charset=\"%s\"' % charset)

        self.ws.putheader('Content-length', "%d" % l)
        self.requestTracker.append("Content-length: %d" % l)
        # set basic auth headers if necessary
        if self.basicAuthUser and self.basicAuthPass:
            base64string = base64.encodestring('%s:%s' % (self.basicAuthUser, self.basicAuthPass))[:-1]
            self.ws.putheader("Authorization", "Basic %s" % base64string)
            self.requestTracker.append("Authorization: Basic %s" % base64string)

        # the SOAPAction header has been removed in SOAP 1.2
        # so we only go in here if the target is supporting 1.1
        if self.soapVersion == "1.1":
            if self.action:
                self.ws.putheader('SOAPAction', '\"%s\"' % self.action)
                self.requestTracker.append('SOAPAction: \"%s\"' % self.action)
            else:
                self.ws.putheader('SOAPAction', '\"\"')
                self.requestTracker.append('SOAPAction: \"\"')

        try:
            self.ws.endheaders()
        except socket.error:
            pass
    # EOF: generateRequestHeaders

    # NAME     : setBasicAuthCreds
    # PARAMS   : bauser, bapass
    # RETURN   : Nothing
    # DESC     : Sets credential data in case Basic Auth
    #            is used.
    def setBasicAuthCreds(self, bauser, bapass):
        self.basicAuthUser = bauser
        self.basicAuthPass = bapass
    # EOF: setBasicAuthCreds

    # NAME     : setSOAPAction
    # PARAMS   : action
    # RETURN   : Nothing
    # DESC     : Sets value for the SOAPAction
    #            header
    def setSOAPAction(self, action):
        self.action = action
    # EOF: setSOAPAction

    # NAME     : setSOAPStr
    # PARAMS   : str
    # RETURN   : Nothing
    # DESC     : Sets value for the SOAP Payload to be used
    def setSOAPStr(self, str):
        self.soapStr = str
    # EOF: setSOAPStr

    # NAME     : setSOAPVersion
    # PARAMS   : str
    # RETURN   : Nothing
    # DESC     : Sets value for the version of SOAP in use
    #            either 1.1 or 1.2
    def setSOAPVersion(self, str):
        if str == "1.1" or str == "1.2":
            self.soapVersion = str
    # EOF: setSOAPVersion

    # NAME     : getRequestHeaders
    # PARAMS   : None
    # RETURN   : Array
    # DESC     : Returns array requestTracker that
    #            holds all Request data for the POST
    def getRequestHeaders(self):
        return self.requestTracker
    # EOF: getRequestHeaders

    # NAME     : setProxy
    # PARAMS   : proxy
    # RETURN   : Nothing
    # DESC     : Sets value for a proxy
    #            server to be used
    def setProxy(self, proxy):
        self.proxy = proxy
    # EOF: setProxy

    # NAME     : setAlternateHost
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : Sets value for an alternate
    #            Host Header
    def setAlternateHost(self, val):
        self.alterHost = val
    # EOF: setAlternateHost

    # NAME     : showRequestHeaders
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Displays all Request header data
    #            for the POST.
    def showRequestHeaders(self):
        print '*** Outgoing HTTP headers **********************************************'
        for i in self.requestTracker:
            print i
        print '************************************************************************'
    # EOF: showRequestHeaders

    # NAME     : showXMLRequestPayload
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Displays all XML payload data
    #            for the POST.
    def showXMLRequestPayload(self, type=0):
        if type == 0:
            print '*** Outgoing SOAP ******************************************************'
            '''
                The alterpayload process leaves some really nasty looking
                blank lines where the original (now deleted) XML nodes were
                so we replace them via the following regex
            '''
            ss = re.sub(">\s+<", "><", self.soapStr)
            print ss.replace("><",">\n<")
            print '************************************************************************'
        elif type == 1:
            ss = re.sub(">\s+<", "><", self.soapStr)
            return ss
    # EOF: showXMLRequestPayload

    # NAME     : showRequest
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Wrapper function that calls all other Request
    #            display functions.
    def showRequest(self):
        self.showRequestHeaders()
        self.showXMLRequestPayload()
        print '************************************************************************'
    # EOF: showRequest

    # NAME     : sendRequest
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Sends XML payload to the target. The
    #            httplib connection must be established
    #            since the send function uses it for
    #            transport.
    def sendRequest(self):
        try:
            if type(self.soapStr) is str:
                self.ws.send(self.soapStr)
            elif type(self.soapStr) is 'instance':
                self.ws.send(self.soapStr.getvalue())
            else:
            	self.ws.send(str(self.soapStr))  # account for unicode - weird
        except socket.error, msg:
            print msg
            if msg[0] == 60 or msg[0] == 111 or cmp(msg,"timed out"):
                #60 is Operation Timed Out, 111 is Connection Refused,
                #"timed out" is returned when socket.setdefaulttimeout() is used
                self.operationTimeout = True
    # EOF: sendRequest

    # NAME     : closeConnection
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Closes the httplib connection.
    def closeConnection(self):
        self.ws.close()
    # EOF: closeConnection

    # NAME     : getResponse
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Extracts the response from an
    #            httplib object that has already
    #            sent data.  There is a small work
    #            around built in for IIS based
    #            targets.
    def getResponse(self):
        self.response = None

        try:
            while 1:
                self.response = self.ws.getresponse()
                if self.response.status != 100:
                    break
                self.ws._HTTPConnection__state = httplib._CS_REQ_SENT
                self.ws._HTTPConnection__response = None
        except:
            self.response = "Error in response form the server"
    # EOF: getResponse

    # NAME     : getResponseData
    # PARAMS   : None
    # RETURN   : String on error
    # DESC     : Populates variables with the
    #            elements of data from the
    #            already grabbed response
    #            from an httplib object.
    def getResponseData(self):
        try:
            self.responseVersion, self.responseCode, self.responseMsg, self.responseHeaders, self.responseData = \
            self.response.version, self.response.status, self.response.reason, self.response.msg, self.response.read()
        except:
            return "Error in data sent back from the server\n"
    # EOF: getResponseData

    # NAME     : getResponseVersion
    # PARAMS   : None
    # RETURN   : String
    # DESC     : Returns the HTTP Response
    #            version, i.e. HTTP/1.1.
    #            The returned data is not that
    #            clear though, for instance
    #            HTTP/1.1 is returned as 11.
    def getResponseVersion(self):
        return self.responseVersion
    # EOF: getResponseVersion

    # NAME     : getRawData
    # PARAMS   : None
    # RETURN   : some raw data value
    # DESC     : tries to extract and decode a value from the
    #            raw SOAP response XML payload.
    def getRawData(self):
        if self.responseData and \
            not self.isHTMLError(self.responseData) and \
            not self.isSQLError(self.responseData) and \
            not self.isXMLError(self.responseData):
            # extract the actual response from the XML in the response payload
            try:
                x = XMLResponsePayloadAnalyzer.XMLResponsePayloadAnalyzer(StringIO.StringIO(self.responseData))

                if x.rawValue:
                    return x.rawValue
                else:
                    # xml should only make it here if something has gone
                    # wrong so lets filter it out
                    if self.responseData.startswith("<?xml"):
                        return ("No data returned", 0)
                    else:
                        return (self.responseData, 0)
            except IOError, ioErr:
                raise
        elif self.responseData and self.isHTMLError(self.responseData):
            return ("Error returned in the form of HTML:\n" + str(self.responseData), 0)
        elif self.responseData and self.isSQLError(self.responseData):
            return ("SQL Error returned:\n" + str(self.responseData), 0)
        elif self.responseData and self.isXMLError(self.responseData):
            return ("XML Error returned:\n" + str(self.responseData), 0)
        else:
            return ("No Data Returned", 0)
    # EOF: getRawData

    # NAME     : getResponseStatusCode
    # PARAMS   : None
    # RETURN   : String
    # DESC     : Returns the HTTP Response
    #            Status Code, i.e. 200 or 404.
    def getResponseStatusCode(self):
        return self.responseCode
    # EOF: getResponseStatusCode

    # NAME     : getResponseMsg
    # PARAMS   : None
    # RETURN   : String
    # DESC     : Returns the HTTP Response
    #            Message, i.e. 'OK' for 200 code.
    def getResponseMsg(self):
        return self.responseMsg
    # EOF: getResponseMsg

    # NAME     : getResponseHeaders
    # PARAMS   : None
    # RETURN   : String
    # DESC     : Returns the HTTP Response
    #            Headers (key: value).
    def getResponseHeaders(self):
        return self.responseHeaders
    # EOF: getResponseHeaders

    # NAME     : getOperationTimeoutStatus
    # PARAMS   : None
    # RETURN   : Boolean
    # DESC     : Returns operationTimeout Status
    def getOperationTimeoutStatus(self):
        return self.operationTimeout
    # EOF: getOperationTimeoutStatus

    # NAME     : isHTMLError
    # PARAMS   : responseData
    # RETURN   : Boolean
    # DESC     : Very simple regex based check
    #            of some XML response payload to
    #            see if it has an <html> tag
    #            in it.  The inference is that if
    #            this tag exists then we have an
    #            error returned in some HTML.
    def isHTMLError(self, responseData):
        if responseData:
            html = re.compile(r"<html>", re.IGNORECASE)
            h1 = re.compile(r"<h1>", re.IGNORECASE)
            if html.search(responseData) or h1.search(responseData):
                return True
            else:
                return False
        else:
            return False
    # EOF: isHTMLError

    # NAME     : isSQLError
    # PARAMS   : responseData
    # RETURN   : Boolean
    # DESC     : Very simple regex based check
    #            of some response data to
    #            see if it has any data exposing
    #            SQL related errors
    def isSQLError(self, responseData):
        if responseData:
            sqlerr = re.compile(r"(SQL | ['|\"]where clause)", re.IGNORECASE)
            exc = re.compile(r"(error | exception)", re.IGNORECASE)
            if sqlerr.search(responseData) or (sqlerr.search(responseData) and exc.search(responseData)):
                return True
            else:
                return False
        else:
            return False
    # EOF: isSQLError

    # NAME     : isFault
    # PARAMS   : responseData
    # RETURN   : Boolean
    # DESC     : Very simple regex based check
    #            of some XML response payload to
    #            see if it has a <faultcode> tag
    #            in it.  The inference is that if
    #            this tag exists then we have a
    #            SOAP fault as the response.
    def isFault(self, responseData):
        if responseData:
            s = re.compile(r"fault", re.IGNORECASE)
            if s.search(responseData):
                return True
            else:
                return False
        else:
            return False
    # EOF: isFault

    # NAME     : isXMLError
    # PARAMS   : responseData
    # RETURN   : Boolean
    # DESC     : Very simple regex based check
    #            of some response data to
    #            see if it has any data exposing
    #            XML related errors
    def isXMLError(self, responseData):
        if responseData:
            xmlerr = re.compile(r"xml", re.IGNORECASE)
            exc = re.compile(r"(error | exception)", re.IGNORECASE)
            if xmlerr.search(responseData) and exc.search(responseData):
                return True
            else:
                return False
        else:
            return False
    # EOF: isXMLError

    # NAME     : getXMLResponsePayload
    # PARAMS   : None
    # RETURN   : String
    # DESC     : Returns the XML payload from the
    #            SOAP Response.
    def getXMLResponsePayload(self):
        if not self.isFault(self.responseData):
            return self.responseData
        else:
            return "Soap Fault"
    # EOF: getXMLResponsePayload

    # NAME     : showResponseHeaders
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Displays all Response header data
    #            from the POST.
    def showResponseHeaders(self):
        print self.responseHeaders
        print '************************************************************************'
    # EOF: showResponseHeaders

    # NAME     : showXMLResponsePayload
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Displays all Response XML payload
    #            data from the POST.
    def showXMLResponsePayload(self):
        print '*** Incoming SOAP ******************************************************'
        if self.responseData is not None:
            print self.responseData.replace('><', '>\n<')
        else:
            print '<<< No response gathered >>>\n'
        print '************************************************************************'
    # EOF: showXMLResponsePayload

    # NAME     : showResponse
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Constructs and displays a
    #            complete Response based on
    #            data returned from the POST.
    def showResponse(self):
        print '*** Incoming HTTP headers **********************************************'
        if self.getResponseVersion() == 11:
            print "HTTP/1.1 " + str(self.getResponseStatusCode()) + " " + self.getResponseMsg()
        elif self.getResponseVersion() == 10:
            print "HTTP/1.0 " + str(self.getResponseStatusCode()) + " " + self.getResponseMsg()
        self.showResponseHeaders()
        self.showXMLResponsePayload()
    # EOF: showResponse

    # NAME     : getElapsed
    # PARAMS   : None
    # RETURN   : float
    # DESC     : Fetch's the value representing
    #            the time delta for 2 given
    #            values of start and stop time.
    def getElapsed(self):
        return self.sw.elapsed()
    # EOF: getElapsed

    # NAME     : getRawElapsed
    # PARAMS   : None
    # RETURN   : float
    # DESC     : Fetch's the raw value representing
    #            the time delta for 2 given
    #            values of start and stop time.
    def getRawElapsed(self):
        return self.sw.getRawElapsed()
    # EOF: getRawElapsed

    # NAME     : doPost
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Wrapper function that
    #            performs the SOAP request and
    #            gathers the data returned from
    #            the POST.  Cleans up by closing
    #            the active connection.
    def doPost(self):
        self.operationTimeout = False
        self.generateRequestHeaders(self.service)
        self.sw.reset()
        self.sw.start()
        self.sendRequest()
        self.getResponse()
        self.sw.stop()
        if not str(self.response).startswith('Error'):
            self.getResponseData()
        self.closeConnection()
    # EOF: doPost

