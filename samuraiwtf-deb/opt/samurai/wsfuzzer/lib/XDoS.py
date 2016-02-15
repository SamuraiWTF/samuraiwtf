"""
# SOAP Attack
#
# FILENAME      : XDoS.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 9/2/2008
# LAST UPDATE   : 8/29/2010
# ABSTRACT      : A class to handle the vectors and processes related to
#                  XML DoS (XDoS) attack vectors.
#
# Copyright (c) 2008 - 2010 neuroFuzz, LLC
#
"""
import os

import XMLProcessor

'''
   XDoS is a class that facilitates the XDoS functionality
   of SOAP Attack. It handles the saving out of possible
   XDoS vectors to XML file. And then performs a
   multi-threaded attack against the given target.
'''
class XDoS(object):
    def __init__(self, fp=None):
        object.__init__(self)
        self.filePath = fp
        self.fileName = "xdosvectors.xml"
        self.xmlPostAttribs = {}
        self.xmlPostMethods = {}
        self.loadXDoSFileObj()
        self.baseElement = "xdosvectors"
        self.vectors = {}   #form of {method}[payloads]

    # NAME     : setFilePath
    # PARAMS   : fp (file path)
    # RETURN   : Nothing
    # DESC     : sets the val from the param "fp"
    #			 to the class var "filePath"
    def setFilePath(self, fp):
        self.filePath = fp
    # EOF: setFilePath

    # NAME	 : getVectorArrSize
    # PARAMS   : None
    # RETURN   : integer
    # DESC	 : returns the size of the vectors array
    def getVectorArrSize(self):
        return len(self.vectors.keys())
    # EOF: getVectorArrSize

    # NAME     : getFilePath
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : returns the val from the
    #			 filePath var
    def getFilePath(self):
        return self.filePath
    # EOF: getFilePath

    # NAME     : loadXDoSFileObj
    # PARAMS   : None
    # RETURN   : Boolean
    # DESC     : checks if the xdos vector XML file
    #             exists, if it exists the xmlPostAttribs
    #             and xmlPostMethods are loaded.
    #             If the file does not exist then no action
    #             is performed.
    def loadXDoSFileObj(self):
        if self.filePath and os.path.exists(self.filePath + "/" + self.fileName):
            self.xmlp = XMLProcessor.XMLProcessor()
            self.xmlPostAttribs = self.xmlp.getAllDataByTag(self.filePath + "/" + self.fileName, "config")
            self.xmlPostMethods = self.xmlp.getAllAttrsByTag(self.filePath + "/" + self.fileName, "method")
    # EOF: loadXDoSFileObj

    # NAME     : createXDoSFileObj
    # PARAMS   : None
    # RETURN   : Boolean
    # DESC     : checks if the xdos vector XML file
    #			 exists, if it doesnt the file gets
    #			 gets created and True is returned
    #			 If the file exists then no action
    #			 is performed and False is returned
    def createXDoSFileObj(self):
        #if path exists and file does not exist yet then create it
        if self.filePath and not os.path.exists(self.fileName):
            self.xmlp = XMLProcessor.XMLProcessor()
            #############################################################
            # Create the minidom XML document
            self.xmlp.createDocument()
            # Create the <vectors> base element
            self.xmlp.createBaseElement(self.baseElement)
            self.xmlp.setFileHandle(self.filePath, self.fileName)
            return True
        else:
            return False
    # EOF: createXDoSFileObj

    # NAME     : populateVectors
    # PARAMS   : v (vectors/payloads)
    # RETURN   : Nothing
    # DESC     : populates the "vectors" array with
    #			 passed in via param v
    def populateVectors(self, method, v):
        if(self.vectors.has_key(method) == False):
            self.vectors[method] = []
        self.vectors[method].append([{v:'C'}, "isignored"])  #attack category is specified later
    # EOF: populateVectors

    # NAME     : saveVectors
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : populates XML file with attack vectors
    def saveVectors(self):
        for k, v in self.xmlPostAttribs.iteritems():
            if(v is not None):
                self.xmlp.populateChildElement("config", v, {'type':k})
        for k, v in self.xmlPostMethods.iteritems():
            self.xmlp.populateChildElement("method", k, v)
        for method in self.vectors.keys():
            self.xmlp.populateChildElements(name="xdosvector", arr=self.vectors[method], type=method, attackcategory="XML Denial of Service", file=True)
    # EOF: saveVectors

    # NAME     : getVectors
    # PARAMS   : None
    # RETURN   : Array
    # DESC     : invokes the parsing of the
    #            XML from the file passed in as
    #            the first param, returns an
    #			 array of SOAP XML payloads
    def getVectors(self, method):
        return self.xmlp.getAllData(self.filePath + "/" + self.fileName, method, "xdosvector")
    # EOF: getVectors

    # NAME     : setXMLPostAttribs
    # PARAMS   : d (dictionary)
    # RETURN   : Nothing
    # DESC     : sets a dictionary to hold all
    #            of the attributes necessary
    #            to invoke XMLPost objects
    def setXMLPostAttribs(self, d):
        self.xmlPostAttribs = d
    # EOF: setXMLPostAttribs

    # NAME     : setXMLPostMethods
    # PARAMS   : d (dictionary)
    # RETURN   : Nothing
    # DESC     : sets a dictionary to hold all
    #            of the methods necessary
    #            to invoke XMLPost objects
    def setXMLPostMethods(self, d):
        self.xmlPostMethods = d
    # EOF: getXMLPostMethods
