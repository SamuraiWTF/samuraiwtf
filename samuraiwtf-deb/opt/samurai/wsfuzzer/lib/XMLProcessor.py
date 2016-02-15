"""
# Web Services Fuzzer
#
# FILENAME      : XMLProcessor.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Andres Andreu
# DATE          : 6/28/2008
# LAST UPDATE   : 9/5/2010
# ABSTRACT      : A class to handle standard XML Processing.
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

import re
from xml.dom.minidom import Document
from xml.dom.minidom import parse

from inc import genUtils
from inc import typechecker

'''
   XMLProcessor is a class that provides interfaces
   for XML based functionality.
'''
class XMLProcessor(object):
    def __init__(self):
        object.__init__(self)
        self.doc = ""
        self.base = ""
        self.fileHandle = ""

    # NAME     : createDocument
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : creates a minidom Document
    #            object and saves it into class
    #            variable
    def createDocument(self):
        # Create the minidom document
        self.doc = Document()
    # EOF: createDocument

    # NAME     : createBaseElement
    # PARAMS   : str, list
    # RETURN   : Nothing
    # DESC     : creates the base element to
    #            set the base for the XML document
    #            being created
    def createBaseElement(self, name=None, ns=None):
        # Create the base element
        self.base = self.doc.createElement(name)
        if ns:
            for n in ns:
                self.base.setAttribute(n[0], n[1])
        else:
            self.base.setAttribute("xmlns", "http://www.neurofuzz.com")
            self.base.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            self.base.setAttribute("xsi:schemaLocation", "http://www.neurofuzz.com vectors.xsd")
        self.doc.appendChild(self.base)
    # EOF: createBaseElement

    # NAME     : populateChildElements
    # PARAMS   : Str, Array, Str, Bool
    # RETURN   : None
    # DESC     : creates child elements in the XML object
    #            or file
    def populateChildElement(self, name=None, value=None, attributes=None, child=None):
        elem = self.doc.createElement(name)
        if type(attributes) == list:
            for n in attributes:
                elem.setAttribute(n[0], n[1])
        else:
            for key in attributes.keys():
                elem.setAttribute(key, attributes[key])
        if child:
            self.doc.childNodes[0].childNodes[0].appendChild(elem)
        else:
            self.doc.childNodes[0].appendChild(elem)
        if value:
            vv = self.doc.createTextNode(str(value))
            elem.appendChild(vv)
    # EOF: populateChildElement

    # NAME     : populateChildElements
    # PARAMS   : Str, Array, Str, Bool
    # RETURN   : None
    # DESC     : creates child elements in the XML object
    #            or file
    def populateChildElements(self, name=None, arr=None, type=None, attackcategory=None, file=False):
        if typechecker.is_str(arr):
            elem = self.doc.createElement(name)
            if type:
                elem.setAttribute("type", type)
            if attackcategory:
                elem.setAttribute("attackcategory", attackcategory)
            self.doc.childNodes[0].appendChild(elem)
            vv = self.doc.createTextNode(arr)
            elem.appendChild(vv)
        elif typechecker.is_iter(arr):
            cdata = re.compile(r"CDATA", re.IGNORECASE)
            invalidxml = re.compile(r"]]>")
            # iterate over array
            for v in arr:
                for kv in v[0].iteritems():
                    #set the attack category data from the array
                    attackcategory = v[1].strip()
                    # Give the element some data
                    # if value == C then check to see if we need
                    # to pump the data thru a CDATA section
                    if kv[1] == 'C':
                        targetKey = kv[0].strip()
                        # lets substitute the chars: ]]> because we use them
                        # in our attack vectors but they cause massive problems
                        # with XML since they are the closing CDATA tags
                        targetKey = invalidxml.sub('0x5d0x5d0x3e', targetKey)
                        # startswith certain chars that we want to push thru CDATA sections
                        # as well as straight text nodes
                        if targetKey.startswith('<') \
                        or targetKey.startswith('>') \
                        or targetKey.startswith('\\') \
                        or targetKey.startswith('<?xml') \
                        and cdata.search(targetKey) is None:
                            elem = self.doc.createElement(name)
                            if type:
                                elem.setAttribute("type", type)
                            if attackcategory:
                                elem.setAttribute("attackcategory", attackcategory)
                            self.doc.childNodes[0].appendChild(elem)
                            vv = self.doc.createCDATASection(targetKey)
                            elem.appendChild(vv)
                        elif targetKey.startswith('<![') and cdata.search(targetKey):
                            tok = unicode(targetKey)
                            newtok = ""
                            for char in tok:
                                if char == "[" or char == "]" or char == "<" or char == ">":
                                    newtok = newtok + "&#" + str(ord(char)) + ";"
                                else:
                                    newtok = newtok + char
                            elem = self.doc.createElement(name)
                            if type:
                                elem.setAttribute("type", type)
                            if attackcategory:
                                elem.setAttribute("attackcategory", attackcategory)
                            self.doc.childNodes[0].appendChild(elem)
                            vv = self.doc.createTextNode(newtok)
                            elem.appendChild(vv)
                        # otherwise process only as straight text nodes
                        else:
                            elem = self.doc.createElement(name)
                            if type:
                                elem.setAttribute("type", type)
                            if attackcategory:
                                elem.setAttribute("attackcategory", attackcategory)
                            self.doc.childNodes[0].appendChild(elem)
                            vv = self.doc.createTextNode(targetKey)
                            elem.appendChild(vv)
                    # value is something other than 'C' so no CDATA section concerns
                    else:
                        elem = self.doc.createElement(name)
                        if type:
                            elem.setAttribute("type", type)
                        if attackcategory:
                            elem.setAttribute("attackcategory", attackcategory)
                        self.doc.childNodes[0].appendChild(elem)
                        vv = self.doc.createTextNode(targetKey)
                        elem.appendChild(vv)

        if file:
            # write the file with the new XML data
            self.writeXMLToFile(doc=self.doc)
    # EOF: populateChildElements

    # NAME     : setFileHandle
    # PARAMS   : Str, Str
    # RETURN   : None
    # DESC     : sets data to establish the path
    #            to the file that will eventually
    #            hold the XML
    def setFileHandle(self, path, file):
        self.fileHandle = path + "/" + file
    # EOF: setFileHandle

    # NAME     : getFileHandle
    # PARAMS   : None
    # RETURN   : Str
    # DESC     : returns the exact path
    #            to the file that holds the XML
    def getFileHandle(self):
        return self.fileHandle
    # EOF: getFileHandle

    # NAME     : writeXMLToFile
    # PARAMS   : XML Doc
    # RETURN   : Nothing
    # DESC     : writes XML data to a file
    def writeXMLToFile(self, doc=None):
        # write the xml out to file
        try:
        	FILE = open(self.fileHandle,"w")
        	if doc is not None:
        		FILE.write(doc.toxml())
        	else:
        		FILE.write(self.doc.toxml())
        	FILE.close()
        except IOError, detail:
            genUtils.handleFileMsg(self.fileHandle, msg=detail)
            return None
    # EOF: writeXMLToFile

    # NAME     : writeXML
    # PARAMS   : None
    # RETURN   : str
    # DESC     : returns XML as a string for output
    def writeXML(self):
        return self.doc.toxml()
    # EOF: writeXML

    # NAME     : getChildElementCnt
    # PARAMS   : None
    # RETURN   : Int
    # DESC     : Counts the number of vectors
    #            generated and stored in XML
    #            file
    def getChildElementCnt(self, fh, elem):
        dom = parse(fh)
        vv = dom.documentElement.getElementsByTagName(elem)
        cnt = 1
        for v in vv:
            cnt = cnt + 1

        return cnt
    # EOF: getChildElementCnt

    # NAME     : getAllData
    # PARAMS   : fh, type, elem
    # RETURN   : Array
    # DESC     : Extracts and returns the attack vectors
    #            from a stored XML file
    def getAllData(self, fh, type, elem):
    	invalidxml = re.compile(r"0x5d0x5d0x3e")
        final = []
        dom = parse(fh)
        vectors = dom.documentElement.getElementsByTagName(elem)
        for v in vectors:
            if v.attributes['type'].value == type:
            	data = v.childNodes[0].nodeValue.strip()
            	# turn this: 0x5d0x5d0x3e into this: ]]>
            	data = invalidxml.sub(']]>', data)
            	# into the array push a tuple
            	# of the data itself and the category as well
                final.append((data,v.attributes['attackcategory'].value))

        return final
    # EOF: getAllData

    # NAME     : getAllDataByTag
    # PARAMS   : File Handle
    # RETURN   : Array
    # DESC     : Extracts and returns the attack vectors
    #            from a stored XML file based on Tag
    def getAllDataByTag(self, fh, elem):
        final = {}
        dom = parse(fh)
        vectors = dom.documentElement.getElementsByTagName(elem)
        for v in vectors:
            if(v.childNodes[0].nodeValue is not None):
                final[v.attributes['type'].value] = v.childNodes[0].nodeValue.strip()
            else:
                final[v.attributes['type'].value]
        return final
    # EOF: getAllDataByTag

    # NAME     : getAllAttrsByTag
    # PARAMS   : File Handle
    # RETURN   : Array
    # DESC     : Extracts and returns the method attributes
    #            from a stored XML file based on Tag
    def getAllAttrsByTag(self, fh, elem):
        final = {}
        dom = parse(fh)
        vectors = dom.documentElement.getElementsByTagName(elem)
        for v in vectors:
            attribs = {}
            for attr in v.attributes:
                attribs[attr] =v.attributes[attr].value
            final[v.childNodes[0].nodeValue.strip()] = attribs
        return final
    # EOF: getAllAttrsByTag
