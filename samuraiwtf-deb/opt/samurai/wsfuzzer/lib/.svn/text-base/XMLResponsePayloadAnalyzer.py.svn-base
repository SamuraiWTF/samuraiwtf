"""
# Web Services Fuzzer
#
# FILENAME      : XMLResponsePayloadAnalyzer.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 04/13/2007
# LAST UPDATE   : 8/28/2010
# ABSTRACT      : A class that dissects an existing SOAP XML Payload and extracts
#                 useful info from it in order to build attack vectors from it.
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

import StringIO
import re
import sys
from xml.dom import Node
from xml.dom import minidom

class XMLResponsePayloadAnalyzer(object):
    def __init__(self, payloadFileName=None):
        object.__init__(self)

        self.bodyelement = self.resultelement = self.targetNode = ""
        self.payloadFileName = StringIO.StringIO()
        self.tempFileName = "0f060643f71dc42b65f1576d520f8cb9.xml"

        if payloadFileName:
            self.cleanFile(payloadFileName)
        else:
            print "This class can't operate w/o an XML file ..."
            sys.exit(2)

        self.doc = self.rawValue = None
        self.rawValueArr = []
        self.txtCnt = 0
        self.processXMLFile()

    # NAME     : getBodyElemName
    # PARAMS   : nodelist
    # RETURN   : Nothing
    # DESC     : Populates the bodyelement attrib
    #            for this class with the string
    #            of the XML element name of the
    #            SOAP body element
    def getBodyElemName(self, nodelist):
        bodyre = re.compile(r"body", re.IGNORECASE)
        for subnode in nodelist:
            if (subnode.nodeType == subnode.ELEMENT_NODE):
                if bodyre.search(subnode.tagName):
                    self.bodyelement = subnode.tagName
                # recursive call
                self.getBodyElemName(subnode.childNodes)
    # EOF: getBodyElemName

    # NAME     : getBodyChildName
    # PARAMS   : node
    # RETURN   : string
    # DESC     : Extracts and returns the
    #            Element name of the body
    #            elements child (the actual
    #            target method name)
    def getBodyChildName(self, node):
        if node.nodeType == Node.ELEMENT_NODE:
            return node.childNodes[0].tagName
        elif node.nodeType == Node.TEXT_NODE:
            return node[0].parentNode[0].tagName
    # EOF: getBodyChildName

    # NAME     : walk
    # PARAMS   : parent
    # RETURN   : Nothing
    # DESC     : Keeps count of the number of
    #            text nodes, they are basically
    #            used when multiple values are
    #            returned.
    #            Also populates the array rawValueArr
    #            with the values when multiple
    #            values are returned.
    def walk(self, parent):
        for node in parent.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                for child in node.childNodes:
                    if child.nodeType == Node.TEXT_NODE:
                        self.txtCnt += 1
                        self.rawValueArr.append(child.data)
                # recursive call
                self.walk(node)
     # EOF: walk

    # NAME     : getRawValue
    # PARAMS   : node
    # RETURN   : Value from SOAP call - data type will vary
    # DESC     : Extracts and returns the raw value
    #            from a SOAP call (from the XML payload
    #            node passed in)
    def getRawValue(self, node):
        fault = re.compile(r"faultcode", re.IGNORECASE)

        self.walk(node)

        # return tuple where index 0 is
        # the data returned from the SOAP
        # call and index 1 is either 1 or 0
        # 1 = array
        # 0 = primitive type
        if self.txtCnt > 1:
            return (self.rawValueArr, 1)
        else:
            # for SOAP faults just print out the value
            # from the faultstring element
            if fault.search(node.childNodes[0].tagName):
                return (node.childNodes[1].firstChild.data, 0)
            elif node.childNodes[0].firstChild:
                if isinstance(node.childNodes[0].firstChild.data, unicode):
                    return (node.childNodes[0].firstChild.data.encode('utf-8'), 0)
                else:
                    return (node.childNodes[0].firstChild.data, 0)
    # EOF: getRawValue

    # NAME     : cleanFile
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Takes in the known XML file
    #            and strips out all unwanted
    #            line endings.  This was done
    #            because I encountered xml files
    #            with data like >\n<
    #            This method writes the massaged
    #            data back into the original
    #            file object passed in at class level.
    def cleanFile(self, file):
        newdata = re.sub(">(\n*\s*\n*)<", "><", file.getvalue().strip())

        tempFile = open( self.tempFileName, 'w' )
        tempFile.write( newdata )
        tempFile.close()
    # EOF: cleanFile

    # NAME     : processXMLFile
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Wrapper method that calls numerous
    #            methods in order to populate
    #            needed data elements.
    def processXMLFile(self):
        try:
            self.doc = minidom.parse(self.tempFileName)

            # this should set a value in self.bodyelement
            self.getBodyElemName(self.doc.childNodes)
            try:
                bodyRoot = self.doc.getElementsByTagName(self.bodyelement)[0]
                self.resultelement = self.getBodyChildName(bodyRoot)

                self.targetNode = self.doc.getElementsByTagName(self.resultelement)[0]
                self.rawValue = self.getRawValue(self.targetNode)
            except IOError,e:
                print e
                sys.exit(0)
        except:
            #print "Problem parsing response XML: %s ... exiting\n" % err
            # set the raw value of the response body in to
            # self.rawValue because the XML is invalid at
            # this point
        	# this will handle both SAXParseException and
        	# ExpatError
            tempFile = open( self.tempFileName, 'r' )
            self.rawValue = tempFile.read()
            tempFile.close()
    # EOF: processXMLFile
