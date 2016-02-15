"""
# Web Services Fuzzer
#
# FILENAME      : XMLPayloadAnalyzer.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Cosmin Banciu <ccbanciu [at] gmail dot com>
# DATE          : 04/04/2007
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

import fileinput
import os
import re
import sys
from xml.dom import minidom

class XMLPayloadAnalyzer(object):
    def __init__(self, payloadFileName=None):
        object.__init__(self)
        self.methodName = self.bodyelement = self.targetNode = ""
        self.paramsHash = {}
        self.names = {}
        self.Path = None
        if payloadFileName:
        	self.setFileNamePath(payloadFileName)
        	self.cleanFile()
        else:
            print "This class can't operate w/o an XML file ..."
            sys.exit(2)
        self.finalPayload = self.bodyRoot = self.bodyRootRaw = self.doc = None
        # open XML file
        if self.Path:
        	self.fh = open(self.Path+self.payloadFileName,"rw")
        else:
        	self.fh = open(self.payloadFileName,"rw")
        if self.payloadFileName and self.fh:
            self.processXMLFile()
            self.alterXMLPayload()
            self.closeFile()
        else:
            sys.exit(0)

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
                self.getBodyElemName(subnode.childNodes)
    # EOF: getBodyElemName

    # NAME     : getParams
    # PARAMS   : nodelist
    # RETURN   : Nothing
    # DESC     : Populates dictionary from data
    #            extracted during the iteration
    #            of target param XML elements
    #            It looks for elements that
    #            establish some data type attribute
    def getParams(self, nodelist):
        for node in nodelist:
            if (node.nodeType == node.ELEMENT_NODE):
                # make sure we target everything below the
                if self.methodName.strip() <> node.tagName.strip() and \
                node.tagName <> self.bodyelement and node.attributes.keys():
                    for k in node.attributes.keys():
                        if 'type' in k:
                            self.paramsHash[node.tagName.strip()] = node.attributes[k].value
                elif self.methodName.strip() <> node.tagName.strip() and \
                node.tagName <> self.bodyelement:
                    self.paramsHash[node.tagName.strip()] = "xsi:string"
                self.getParams(node.childNodes)
    # EOF: getParams

    # NAME     : getParamsHash
    # PARAMS   : None
    # RETURN   : Dictionary
    # DESC     : Wrapper method to get and return the
    #            dictionary/hashtable of parameters
    #            and respective values
    def getParamsHash(self):
        return self.getParams(self.bodyRootRaw)
    # EOF: getParamsHash

    # NAME     : getBodyChildName
    # PARAMS   : node
    # RETURN   : string
    # DESC     : Extracts and returns the
    #            Element name of the body
    #            elements child (the actual
    #            target method name)
    def getBodyChildName(self, node):
        return node.childNodes[0].tagName
    # EOF: getBodyChildName

    # NAME     : processElem
    # PARAMS   : nodelist
    # RETURN   : tuple
    # DESC     : iterates over the XML elements
    #            in nodelist and looks for all
    #            elements that dont equal the
    #            node name o fthe target method
    #            for the SOAP attack.  All elements
    #            that are children to the element
    #            that is the target get processed.
    #            processing means that a hash is
    #            created of the element name (this
    #            represent the target parameters for
    #            the SOAP call) as the key and its
    #            type attributes as values if appropriate.
    def processElem(self, nodelist):
        for node in nodelist:
            if (node.nodeType == node.ELEMENT_NODE):
                # make sure we target everything below the target method node
                if self.methodName.strip() <> node.tagName.strip() and \
                node.tagName <> self.bodyelement and node.attributes.keys():
                    for k in node.attributes.keys():
                        if 'type' in k:
                            self.names[node.tagName.strip()] = (k,node.attributes[k].value)
                elif self.methodName.strip() <> node.tagName.strip() and \
                node.tagName <> self.bodyelement:
                    self.names[node.tagName.strip()] = None
                self.processElem(node.childNodes)

        return (len(self.names),self.names)
    # EOF: processElem

    # NAME     : alterXMLPayload
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Wrapper method that triggers the
    #            creation of a tuple holding key
    #            target node data and then
    #            passes that to the method that
    #            actually alters the XML payload
    def alterXMLPayload(self):
        t = self.processElem(self.targetNode)
        self.alterPayload(t)
    # EOF: alterXMLPayload

    # NAME     : alterPayload
    # PARAMS   : inTuple, body
    # RETURN   : Nothing
    # DESC     : Takes in a baseline of a known
    #            valid XML payload for a given
    #            target.  Then it modifies this
    #            XML to alter the nodes representing
    #            the target params.  They are each
    #            set to format string form - %s
    #            in ordert to dynamically accept
    #            attack data later.
    #            Params:
    #            inTuple = a tuple consisting of:
    #            index 0 - the num of target nodes or
    #            parameters that have been tagged
    #            for attack
    #            index 1 - hash (key/value) of the
    #            target nodes.
    def alterPayload(self, inTuple):
        self.finalPayload = self.doc
        rootNode = self.finalPayload.documentElement

        # loop thru the list of param XML elements
        for k in inTuple[1].keys():
            # remove the original element
            targetNode = rootNode.getElementsByTagName(k)
            if targetNode and (self.methodName <> targetNode[0].tagName):
                parentNode = targetNode[0].parentNode
                targetNode[0].unlink()
                parentNode.removeChild( targetNode[0] )

                # add a new element of same name but
                # with a value of %s
                newtag = self.finalPayload.createElement(k)
                newtag1 = self.finalPayload.createTextNode(k)

                targetBody = rootNode.getElementsByTagName(self.methodName)

                targetBody[0].appendChild(newtag)
                # newtag is an Element
                newtag.appendChild(newtag1)
                # add xsi and xsd info only if necessary, .Net services that
                # use document/literal don't use these attrib's
                if inTuple[1][k]:
                    newtag.setAttribute(inTuple[1][k][0], inTuple[1][k][1])
                newtag1.data = "%s"
    # EOF: alterPayload

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
    def cleanFile(self):
    	if self.Path:
    		oldFileName  = self.Path + 'old_' + self.payloadFileName
    		tempFileName = self.Path + 'temp_' + self.payloadFileName
    		completeFile = self.Path + self.payloadFileName
    	else:
    		oldFileName  = 'old_' + self.payloadFileName
    		tempFileName = 'temp_' + self.payloadFileName
    		completeFile = self.payloadFileName

        # if there's already an 'old_' prefixed backup file there from
        # a previous run, remove it...
        if os.path.isfile( oldFileName ):
            os.remove( oldFileName )

        tempFile = open( tempFileName, 'w' )
        for line in fileinput.input( completeFile ):
            #TODO change o reflect the same logic as XMlStringpayload
            line = line.replace("\n","" )
            line = line.strip()
            tempFile.write(line)
        tempFile.close()

        # Rename the original file by prefixing it with 'old_'
        os.rename( completeFile, oldFileName )
        # Rename the temporary file to what the original was named...
        os.rename( tempFileName, completeFile )
    # EOF: cleanFile

    # NAME     : closeFile
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Cleans up the open file hanlde
    #            used by this class
    def closeFile(self):
        # close XML file
        self.fh.close()
    # EOF: closeFile

    # NAME     : processXMLFile
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Wrapper method that calls numerous
    #            methods in order to populate
    #            needed data elements.
    def processXMLFile(self):
        self.doc = minidom.parse(self.fh)

        # this should set a value in self.bodyelement
        self.getBodyElemName(self.doc.childNodes)
        try:
            self.bodyRoot = self.doc.getElementsByTagName(self.bodyelement)[0]
            self.bodyRootRaw = self.doc.getElementsByTagName(self.bodyelement)
            self.methodName = self.getBodyChildName(self.bodyRoot)


            self.targetNode = self.doc.getElementsByTagName(self.getBodyChildName(self.bodyRoot))
        except IOError,e:
            print e
            sys.exit(0)
    # EOF: processXMLFile

	# NAME	 : setFileNamePath
	# PARAMS : str
	# RETURN : Nothing
	# DESC	 : parses the submitted value if a '/' is
	#		   detected and then sets the path and
	#		   actual file name or just sets the file name
    def setFileNamePath(self, str):
    	# string has a '/' so its a path
    	# *nix solution
    	if str.find('/') >= 0:
    		finalarr = str.rsplit('/')
    		# actual file name
    		self.payloadFileName = finalarr[len(str)-1]
    		# iterate over all values but the final one
    		# in the array and reconstruct the path
    		for x in range(0,len(finalarr)-2):
    			finalpath += finalarr[x] + "/"
    		self.Path = finalpath
    	# windows
    	elif str.find('\\') >= 0:
    		# convert the back slashes to forward slashes
    		str = str.replace('\\','/')
    		finalarr = str.rsplit('/')
    		# actual file name
    		self.payloadFileName = finalarr[len(str)-1]
    		# iterate over all values but the final one
			# in the array and reconstruct the path
    		for x in range(0,len(finalarr)-2):
    			finalpath += finalarr[x] + "\\"
    		self.Path = finalpath
    	else:
    		self.payloadFileName = str
    # EOF: setFileNamePath


