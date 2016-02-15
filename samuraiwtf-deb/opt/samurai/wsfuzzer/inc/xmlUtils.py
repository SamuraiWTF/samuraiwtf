"""
# Web Services Fuzzer
#
# FILENAME      : xmlUtils.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 11/21/2006
# LAST UPDATE   : 9/5/2010
# ABSTRACT      : A library to create some functions to be affect XML
#                 docs natively.
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

from xml.dom import minidom

# NAME     : alterPayloadNodes
# PARAMS   : inFileName, n, nt
# RETURN   : XML Document
# DESC     : Takes in a baseline of a known
#            valid XML payload for a given
#            target.  Then it modifies this
#            XML to alter the nodes representing
#            the target params.  They are each
#            set to format string form - %s
#            in ordert to dynamically accept
#            attack data.
#            Params:
#            inFileName = a StringIO obj
#            that holds the target XML obj
#            to be modified
#            n = the num of target nodes or
#            parameters that have been tagged
#            for attack
#            nt = array of the data types for
#            eachof the targeted parameters
def alterPayloadNodes(inFileName, n, nt):
    # parse the original XML
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement

    for i in range(1,n):
        # remove the original element
        targetNode = rootNode.getElementsByTagName(('v' + str(i)))[0]
        parentNode = targetNode.parentNode
        targetNode.unlink()
        parentNode.removeChild( targetNode )

        # add a new element of same name but
        # with a value of %s
        newtag = doc.createElement(('v' + str(i)))
        newtag1 = doc.createTextNode(('v' + str(i)))
        doc.childNodes[0].childNodes[1].childNodes[1].appendChild(newtag)
        newtag.appendChild(newtag1)
        # newtag is an Element
        newtag.setAttribute('xsi:type', 'xsd:' + nt[i-1])
        newtag1.data = "%s"

    # return native XML document
    return doc
# EOF: alterPayloadNodes

# NAME     : getElementAttribData
# PARAMS   : node, target, attr
# RETURN   : string
# DESC     : Takes in an XML doc in the param
#            "node". Then it finds element "target"
#            and extracts/returns the value from
#            attribute "attr"
#            Params:
#            node = XML doc in the form of DOM
#            target = target Element in the WSDL
#            attr = target attribute in the target
#            Element
def getElementAttribData(node, target, attr):
    return node.getElementsByTagName(target)[0].attributes[attr].value
# EOF: getElementAttribData

# NAME     : addWSSEStanza
# PARAMS   : payload, stanza
# RETURN   : string
# DESC     : Takes in an XML doc (in string form)
#            "payload". Then it takes in an XML
#            stanza with WSSE sec data "stanza".
#            then it replaces the unused SOAP
#            Header with a SOAP Header including
#            including the WSSE sec data
def addWSSEStanza(payload, stanza):
    newstanza = "<soapenv:Header>" + stanza + "</soapenv:Header>"
    return payload.replace("<soapenv:Header/>", newstanza)
# EOF: addWSSEStanza
