"""
# Web Services Fuzzer
#
# FILENAME      : HostChecker.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 6/29/2008
# LAST UPDATE   : 8/31/2010
# ABSTRACT      : A small class to verify the availability of a submitted host
#               : This tool is meant to be part of a web app pen testers toolkit.
#
# Copyright (c) 2008 - 2010 neuroFuzz, LLC
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

import urllib2
from urllib2 import HTTPError

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result

class HostChecker:

    # NAME     : checkHost
    # PARAMS   : Str
    # RETURN   : Bool
    # DESC     : checks the availability of
    #            the given http(s) host
    def isHostAvailable(self, host):
        try:
            request = urllib2.Request(self.sanitizeHost(host))
            opener = urllib2.build_opener(SmartRedirectHandler())
            resp = opener.open(request)
            if resp:
                return True
        except HTTPError, e:
            """
                HTTP Error 500 - in respect to SOAP services tends to be:
                GET fails, only POSTS are allowed
            """
            if str(e).startswith('HTTP Error'):
                return True
            print "Sorry but that target cannot be hit: %s" % e
            return False
        except urllib2.URLError, e:
            print "Cannot retrieve URL: " + e.reason[1]
            return False
    # EOF: checkHost

    # NAME     : sanitizeHost
    # PARAMS   : Str
    # RETURN   : Str
    # DESC     : Sanitizes the submitted host string
    #            to ensure that the protocol is in
    #            place
    def sanitizeHost(self, host):
        if host.startswith('http://') or host.startswith('https://'):
            return host
        return "http://" + host
    # EOF: sanitizeHost
