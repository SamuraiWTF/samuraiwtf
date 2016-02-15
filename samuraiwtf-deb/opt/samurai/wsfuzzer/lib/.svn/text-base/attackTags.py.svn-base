"""
# Web Services Fuzzer
#
# FILENAME      : attackTags.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 9/01/2006
# LAST UPDATE   : 8/26/2010
# ABSTRACT      : A library to create some standard XML tags to be used by
#                 different classes.
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

class AttackTagGenerator:
    def __init__(self):
        self.xml = {}
        self.baseTags()
        
    # NAME     : baseTags
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Populates dictionary for baseline static XML tags 
    def baseTags(self):
        self.xml["xh"] = "<?xml version=\'1.0\' encoding=\'UTF-8\'?>"
        self.xml["env_open"] = "<SOAP-ENV:Envelope SOAP-ENV:encodingStyle=\'http://schemas.xmlsoap.org/soap/encoding/\'>"
        self.xml["env_close"] = "</SOAP-ENV:Envelope>"
        self.xml["header_open"] = "<SOAP-ENV:Header>"
        self.xml["header_close"] = "</SOAP-ENV:Header>"
        self.xml["body_open"] = "<SOAP-ENV:Body>"
        self.xml["body_close"] = "</SOAP-ENV:Body>"
        self.xml["sec_open"] = "<wsse:Security xmlns:wsse=\'http://schemas.xmlsoap.org/ws/2002/07/secext\' " \
        "xmlns:wsu=\'http://schemas.xmlsoap.org/ws/2002/07/utility\'>"        
        self.xml["sec_close"] = "</wsse:Security>"
        self.xml["ut_open"] = "<wsse:UsernameToken>"
        self.xml["ut_close"] = "</wsse:UsernameToken>"
        self.xml["un_open"] = "<wsse:Username>"
        self.xml["un_close"] = "</wsse:Username>"        
        self.xml["wp_open"] = "<wsse:Password Type=\'wsse:PasswordDigest\'>"
        self.xml["wp_close"] = "</wsse:Password>"        
        self.xml["wn_open"] = "<wsse:Nonce>"
        self.xml["wn_close"] = "</wsse:Nonce>"        
        self.xml["wc_open"] = "<wsse:Created>"
        self.xml["wc_close"] = "</wsse:Created>" 
    # EOF: baseTags
    
    # NAME     : getTags
    # PARAMS   : None
    # RETURN   : Key Value data structure
    # DESC     : returns self.xml 
    def getTags(self):
        return self.xml
    # EOF: getTags
