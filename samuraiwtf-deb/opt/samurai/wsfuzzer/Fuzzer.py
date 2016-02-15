"""
# Web Services Fuzzer
#
# FILENAME      : Fuzzer.py
# AUTHORS       : Cosmin Banciu <ccbanciu [at] gmail dot com>
#               : David Shu <ydpanda [at] gmail dot com>
#               : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Andres Andreu
# DATE          : 12/07/2005
# LAST UPDATE   : 9/5/2010
# ABSTRACT      : A library to facilitate fuzzing attacks against web services.
#               : This tool is meant to be part of a web app pen testers toolkit.
#
# Copyright (c) 2005 - 2010 neuroFuzz, LLC
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

from StringIO import StringIO
import re
import sys
import time
import types

#import StatTracker
from inc import attackUtils
from inc import genUtils
from inc import xmlUtils
from lib import AntiIDS
from lib import BaseLiner
from lib import FuzzGenerator
from lib import Logger
from lib import PDFWriter
from lib import WSSEAttackGenerator
from lib import XDoS
from lib import XMLFuzzGenerator
from lib import XMLPost
from lib import XMLProcessor

DataCast = {'int':"IntType",
            'boolean':"Boolean"
            }

class Args(object):
    def __init__(self):
        object.__init__(self)
        self.args = {}

    def addToArgs(self, key=None, value=None):
        key = key.encode('utf-8')
        self.args[key] = value

class ArgBuilder(object):
    def __init__(self, params=None, boolval=False):
        object.__init__(self)
        self.simultaneous = boolval
        self.args = params
        self.argsList = []
        self.buildArgs()

    def classTypeCast(self, data, type):
        try:
            return types.__dict__[DataCast[type]](data)
        except:
            return data

    def getArgs(self):
        return self.argsList

    def buildArgs(self):
        for param in self.args:
            if(param.fuzzParam != False):
                param.fuzzType.beginFuzz(param.name)
        finished = False

        # attack parameters individually
        if self.simultaneous == False:
            while finished == False:
                advancedValue = False
                args = Args()
                for param in self.args:
                    if(param.fuzzParam == False):
                    	# when a parameter is not being fuzzed this is the default value
                    	# to be used on it
                        args.addToArgs(param.name, (self.classTypeCast("?", param.type), "DEFAULT"))
                    elif(param.fuzzType.hasNext() == True and advancedValue == False):
                    	val = param.fuzzType.getNext()
                    	if val:
                            args.addToArgs(param.name, (self.classTypeCast(val[0], param.type), val[1]))
                            advancedValue = True
                    else:
                        args.addToArgs(param.name, self.classTypeCast(None, param.type))
                self.argsList.append(args)

                finished = True
                for param in self.args:
                    if(param.fuzzParam == True and param.fuzzType.hasNext() == True):
                        finished = False
                        break
        # attack parameters simultaneously
        else:
            while finished == False:
                advancedValue = False
                args = Args()
                for param in self.args:
                    if(param.fuzzParam == False):
                        args.addToArgs(param.name, (self.classTypeCast("Default Value", param.type), "DEFAULT"))
                    elif(param.fuzzType.hasNext() == True and advancedValue == False):
                    	val = param.fuzzType.getNext()
                    	if val:
                            args.addToArgs(param.name, (self.classTypeCast(val[0], param.type), val[1]))
                            advancedValue = True
                    else:
                    	val = param.fuzzType.getNext()
                    	if val:
                            args.addToArgs(param.name, (self.classTypeCast(val[0], param.type), val[1]))
                            advancedValue = True
                self.argsList.append(args)

                finished = True
                for param in self.args:
                    if(param.fuzzParam == True and param.fuzzType.hasNext() == True):
                        finished = False
                        break

        # both of these checks need to ensure that the "standard" model is in play
        # if the wsfuzzer_xml model is in play these is no need to process these
        # sections
        for param in self.args:
            if((param.fuzzParam != False) and (param.fuzzType.getDictionaryType() == "standard")):
                param.fuzzType.endFuzz()


class FuzzType(object):
    def __init__(self):
        object.__init__(self)
    def beginFuzz(self, param=None):
        return None
    def endFuzz(self):
        return None
    def resetFuzz(self):
        return None
    def hasNext(self):
        return False
    def getNext(self):
        return False
    def getLength(self):
        return 1

'''
   DictionaryFuzz is a class whose responsibility is
   the construction and management of the attack
   data for the eventual fuzzing process
'''
class DictionaryFuzz(FuzzType):
    def __init__(self, dictionaryName=None, dictionaryType=None, auto=False):
        FuzzType.__init__(self)
        self.xmlp = XMLProcessor.XMLProcessor()
        self.automated = auto
        self.source = dictionaryName
        self.fileHandle = ""
        self.saveFileHandle = ""
        self.fuzzList = []
        self.counter = 0
        self.length = 0
        # types - standard or wsfuzzer_xml
        self.dictType = dictionaryType
        self.dictFile = ""
        self.path = ""
        self.baseLine = 0

    # NAME     : beginFuzz
    # PARAMS   : param
    # RETURN   : Nothing
    # DESC     : Begins the fuzzing process by tapping
    #            into the numerous sources at hand and
    #            collecting all of the attack vectors
    #            into one array: fuzzList
    def beginFuzz(self, param=None):
        # gather all of the static data from
        # the dictionary submitted by the user
        #############################################################
        # standard model means the user chooses options
        # and submits dict in the interactive form
        if self.dictType == "standard":
            try:
                self.fileHandle = open(self.source, 'rb')
            except:
                genUtils.handleFileMsg(self.source, exit=True)

            #self.fuzzList = self.fileHandle.readlines()
            tmpfuzzList = self.fileHandle.readlines()
            # populate the fuzzList array with the added data
            # necessary for the XML write
            for fl in tmpfuzzList:
                # dictionary data should now be coming in as such:
                # vector:::type
                # example:
                # x' OR 1 = 1 --:::SQL Injection
                a = fl.split(':::')
                # fuzzList then holds the following data structure:
                # each node in the array is an array
                # in each node array you will find the index
                # is a dictionary as such:
                # [ [{"x' OR 1 = 1 --": 'C'}, 'SQL Injection'], [{"x' OR '1' = '1": 'C'}, 'SQL Injection'] ]
                if a[0] <> '\n':
                    self.fuzzList.append([{a[0].strip():'C'}, a[1].strip()])
        #############################################################

            if (self.automated == True):
                self.f = FuzzGenerator.FuzzGenerator()
                self.x = XMLFuzzGenerator.XMLFuzzGenerator()

                # gather attacks strings from class FuzzGenerator
                # call generate function and it will
                # generate all dynamic attack strings
                self.f.generate()
                # iterate over each array returned to us
                for all in self.f.getall():
                    # iterate over each val per array
                    for a in all:
                        self.fuzzList.append([{a[0]:'C'}, a[1]])

                # now gather attack strings from
                # class XMLFuzzGenerator
                # call generateAttacks function and
                # it will generate XML attack strings
                self.x.generateAttacks(self.fuzzList, param)
                # iterate over each array returned to us
                for all in self.x.getallparam():
                    # iterate over each val per array
                    for a in all:
                        self.fuzzList.append([{a[0]:'C'}, a[1]])
        #############################################################
        # the payload model means that the user has submitted an XML
        # file containing attack vectors already once generated by
        # WSFuzzer and saved
        if self.dictType == "payload":
            self.fuzzList = self.xmlp.getAllData(self.getDictionaryFileName(), "attack_string", "vector")
        #############################################################
        # logistics ...
        self.length = len(self.fuzzList)
        #self.counter = 0
    # EOF: beginFuzz

    # NAME     : endFuzz
    # PARAMS   : None
    # RETURN   : None if there is an exception
    # DESC     : Ends the fuzzing process by closing
    #            the existing handle to the file that
    #            provided the static dictionary
    #            of attack vectors.
    def endFuzz(self):
        try:
            self.fileHandle.close()
        except:
            print "Closing file Failed (" + self.source + ")"
            return None
    # EOF: endFuzz

    # NAME     : hasNext
    # PARAMS   : None
    # RETURN   : boolean
    # DESC     : returns true if counter is less than
    #            the total size of the array
    #            returns false otherwise
    def hasNext(self):
        if(self.counter < self.length):
            return True
        else:
            return False
    # EOF: hasNext

    # NAME     : getNext
    # PARAMS   : None
    # RETURN   : string
    # DESC     : returns next value in the fuzzlist array
    #            based on the class level counter, then
    #            increments counter
    #            the return value is a tuple --
    #            (vector, attacktype)
    def getNext(self):
        if self.dictType == "standard":
            if self.fuzzList[self.counter]:
                response = (self.fuzzList[self.counter][0].keys()[0].strip(), self.fuzzList[self.counter][1])
                self.counter = self.counter + 1
                return response
        if self.dictType == "payload":
            response = self.fuzzList[self.counter]
            self.counter = self.counter + 1
            return response
        return None
    # EOF: getNext

    # NAME     : getLength
    # PARAMS   : None
    # RETURN   : int
    # DESC     : returns size of fuzzlist array
    #            in an int or 0 if it is empty
    def getLength(self):
        if (self.length):
            return self.length
        else:
            return 0
    # EOF: getLength

    # NAME     : getSaveFileName
    # PARAMS   : None
    # RETURN   : str
    # DESC     : returns file name
    def getSaveFileName(self):
        return self.saveFileHandle
    # EOF: getSaveFileName

    # NAME     : getDictionaryType
    # PARAMS   : None
    # RETURN   : str
    # DESC     : returns file name
    def getDictionaryType(self):
        return self.dictType
    # EOF: getDictionaryType

    # NAME     : setDictionaryFileName
    # PARAMS   : Str
    # RETURN   : Nothing
    # DESC     : returns file name
    def setDictionaryFileName(self, name):
        self.dictFile = name
    # EOF: setDictionaryFileName

    # NAME     : getDictionaryFileName
    # PARAMS   : None
    # RETURN   : str
    # DESC     : returns file name
    def getDictionaryFileName(self):
        return self.dictFile
    # EOF: getDictionaryFileName

class Parameter(object):
    def __init__(self, paramName=None, paramType=None, fuzz=None, fuzzThisParam=False):
        object.__init__(self)
        self.name = paramName
        self.type = paramType
        self.fuzzType = fuzz
        self.fuzzParam = fuzzThisParam

class Method(object):
    def __init__(self, methodName=None):
        object.__init__(self)
        self.name = methodName
        self.parameterList = []

    def addParameter(self, parameter=None):
        print "adding parameter"
        self.parameterList.append(parameter)

    def getParams(self):
        return self.parameterList

    def printParams(self):
        for param in self.parameterList:
            print param.name

'''
   Fuzzer is the class that actually interfaces
   with the various wrappers and kicks off the attack
   requests as well as capturing the responses.
   Based on the captured responses Fuzzer also
   interfaces with class Logger so as to get the
   result data documented.
'''
class Fuzzer(object):
    def __init__(self, wrapper=None, dirName=None, methodObj=None, emptyDir=True):
        object.__init__(self)
        self.wrapper = wrapper
        self.logger = Logger.Logger(dirName=dirName, emptyDir=emptyDir)
        self.methodList = []
        self.methodObj = methodObj
        self.antiids = AntiIDS.AntiIDS(wrapper)
        self.IDSEvasion = self.auto = self.simultaneous = False
        self.IDSEvasionOpt = self.IDSEvasionURI = \
        self.bauser = self.bapass = \
        self.wsseuser = self.wssepass = \
        self.keyfile = self.certfile = \
        self.soapAction = self.proxy = \
        self.proxyport = self.dictType = None
        self.version = 0
        self.alterhost = None
        self.saveFileHandle = ""
        self.xmlp = XMLProcessor.XMLProcessor()
        self.xdos = XDoS.XDoS(fp=self.logger.getLogPath())
        self.xdosObjExists = False
        self.baseLine = 0
        self.pdfw = PDFWriter.PDFWriter(path=self.logger.getLogPath())
        self.fuzzList = []
        # to be used during XDoS process
        self.pollObjects = []

    # NAME     : setDictType
    # PARAMS   : Str
    # RETURN   : Nothing
    # DESC     : sets val for dictType
    def setDictType(self, type):
        self.dictType = type
    # EOF: setDictType

    # NAME     : initObjects
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : initializes objects
    def initObjects(self):
        if self.dictType == "standard":
            # generate and get XXE core level attack XML vectors
            self.x = XMLFuzzGenerator.XMLFuzzGenerator()
            # generate and get WSSE attack XML vectors
            self.w = WSSEAttackGenerator.WSSEAttackGenerator()
    # EOF: initObjects

    # NAME     : setXMLP
    # PARAMS   : XMLProcessor obj
    # RETURN   : Nothing
    # DESC     : sets existing XMLP obj
    def setXMLP(self, xmlp):
        self.xmlp = xmlp
    # EOF: setXMLP

    # NAME     : setIDSEvasion
    # PARAMS   : Bool
    # RETURN   : Nothing
    # DESC     : sets val for IDSEvasion
    def setIDSEvasion(self, bool):
        self.IDSEvasion = bool
    # EOF: setIDSEvasion

    # NAME     : setIDSEvasionOpt
    # PARAMS   : Bool
    # RETURN   : Nothing
    # DESC     : sets val for IDSEvasion
    def setIDSEvasionOpt(self, val):
        self.IDSEvasionOpt = val
    # EOF: setIDSEvasionOpt

    # NAME     : addMethodToFuzz
    # PARAMS   : method
    # RETURN   : Nothing
    # DESC     : adds chosen method name to
    #            array of all methods chosen.
    def addMethodToFuzz(self, method):
        self.methodList.append(method)
    # EOF: addMethodToFuzz

    # NAME     : setAuto
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets bool switch to be used
    #            to establish auto attack
    #            mode
    def setAuto(self, val):
        self.auto = val
    # EOF: setAuto

    # NAME     : setAlternateHost
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets val to be used as an
    #            alternate Host Header value
    def setAlternateHost(self, val):
        self.alterhost = val
    # EOF: setAlternateHost

    # NAME     : setSaveFileName
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets the file name for
    #            storage of attack vectors
    def setSaveFileName(self, val):
        self.saveFileHandle = val
    # EOF: setSaveFileName

    # NAME     : getSaveFileName
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : returns the file name for
    #            storage of attack vectors
    def getSaveFileName(self):
        return self.saveFileHandle
    # EOF: getSaveFileName

    # NAME     : setProxy
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets proxy server value to be used
    def setProxy(self, val):
        self.proxy = val
    # EOF: setProxy

    # NAME     : setProxyPort
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets proxy server value to be used
    def setProxyPort(self, val):
        self.proxyport = val
    # EOF: setProxyPort

    # NAME     : setVer
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets version number
    #            for WSFuzzer
    def setVer(self, val):
        self.version = val
    # EOF: setAuto

    # NAME     : setSOAPAction
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : sets soapaction value
    def setSOAPAction(self, val):
        self.soapAction = val.strip()
    # EOF: setSOAPAction

    # NAME     : setSim
    # PARAMS   : boolval
    # RETURN   : Nothing
    # DESC     : sets bool switch to be used
    #            to establish individual or
    #            simultaneous mode
    def setSim(self, boolval):
        if (boolval == True or boolval == False):
            self.simultaneous = boolval
    # EOF: setSim

    # NAME     : getMethods
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of method names
    #            chosen as targets.
    def getMethods(self):
        return self.methodList
    # EOF: getMethods

    # NAME     : getLoggerObj
    # PARAMS   : None
    # RETURN   : Logger Obj
    # DESC     : returns logger obj
    def getLoggerObj(self):
        return self.logger
    # EOF: getLoggerObj

    # NAME     : getSim
    # PARAMS   : None
    # RETURN   : bool
    # DESC     : returns bool value
    def getSim(self):
        return self.simultaneous
    # EOF: getSim

    # NAME     : showMethods
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of chosen
    #            methods printing each element
    def showMethods(self):
        for method in self.methodList:
            print method.name
    # EOF: showMethods

    # NAME     : setBAFuzz
    # PARAMS   : bauser, bapass
    # RETURN   : Nothing
    # DESC     : sets creds up for use of
    #            HTTP Basic Auth in XMLPost.
    def setBAFuzz(self, bauser=None, bapass=None):
        if bauser is not None and bapass is not None:
            self.bauser = bauser
            self.bapass = bapass
        elif bauser is not None and bapass is None:
            print "A user with no password is not allowed for Basic Auth usage ...\n"
            sys.exit(2)
        elif bauser is None and bapass is not None:
            print "A password set is not allowed without an attached username ...\n"
            sys.exit(2)
        else:
            print "Basic Auth creds were not properly passed in, exiting now ...\n"
            sys.exit(2)
    # EOF: setBAFuzz

    # NAME     : setWSSEFuzz
    # PARAMS   : wsseuser, wssepass
    # RETURN   : Nothing
    # DESC     : sets creds up for use of
    #            WS-Security in SOAP Payload
    def setWSSEFuzz(self, wsseuser=None, wssepass=None):
        if wsseuser and wssepass:
            self.wsseuser = wsseuser
            self.wssepass = wssepass
        elif wsseuser and wssepass is None:
            print "A user with no password is not allowed for WS-Security usage ...\n"
            sys.exit(2)
        elif wsseuser is None and wssepass:
            print "A password set is not allowed without an attached username ...\n"
            sys.exit(2)
        else:
            print "WS-Security creds were not properly passed in, exiting now ...\n"
            sys.exit(2)
    # EOF: setWSSEFuzz

    # NAME     : setCertFuzz
    # PARAMS   : bauser, bapass
    # RETURN   : Nothing
    # DESC     : sets creds up for use of
    #            HTTP Basic Auth in XMLPost.
    def setCertFuzz(self, keyfile=None, certfile=None):
        if keyfile is not None and certfile is not None:
            self.keyfile = keyfile
            self.certfile = certfile
        elif keyfile is not None and certfile is None:
            print "A key with no certificate is not allowed ...\n"
            sys.exit(2)
        elif keyfile is None and certfile is not None:
            print "A certificate with no key is not allowed...\n"
            sys.exit(2)
        else:
            print "Client-side certificate values presented were not acceptable ...\n"
            sys.exit(2)
    # EOF: setCertFuzz

    # NAME     : saveVectors
    # PARAMS   : Array
    # RETURN   : None
    # DESC     : Passes over array of dynamic
    #            payloads generated
    def saveVectors(self, arr=None):
        if arr:
            self.xmlp.populateChildElements("vector", arr, "payload", file=True)
        else:
            self.xmlp.populateChildElements(None, None, None, file=True)
    # EOF: saveVectors

	# NAME	 : saveDictVectors
	# PARAMS : methodName
	# RETURN : None
	# DESC	 : Creates the XML base elements and
	#		   pushes data across to the XMLProcessor
	#		   object
    def saveDictVectors(self, methodName):
        l = self.getLoggerObj()
        path = l.getLogPath()
        #############################################################
        # Create the minidom XML document
        self.xmlp.createDocument()
        # Create the <vectors> base element
        self.xmlp.createBaseElement("vectors")
        self.xmlp.populateChildElements(name="vector", arr=self.fuzzList, type="attack_string")
        # write the xml out to file
        self.xmlp.setFileHandle(l.getLogPath(), self.genName(methodName))
        #############################################################
    # EOF: saveDictVectors

	# NAME	 : genName
	# PARAMS : methodName
	# RETURN : str
	# DESC	 : returns file name based on
	#		   date/time
    def genName(self, methodName):
        now = time.localtime(time.time())
        year, month, day, hour, minute, second, weekday, yearday, daylight = now
        return "wsfuzzer-%s-%04d-%02d-%02d-%02d-%02d-%02d.xml" % (methodName, year, month, day, hour, minute, second)
    # EOF: genName

    # NAME	 : buildXMLPostObj
	# PARAMS : fhost, fsoapstr, fmethodname, fservice, fhttps
	# RETURN : XMLPost object
	# DESC	 : constructs and returns dynamically created XMLPost object
    def buildXMLPostObj(self, fhost, fsoapstr, fmethodname, fservice, fhttps):
        """
            create XMLPost obj
            keyfile, certfile, proxy, proxyport, & version
            should have been set already from WSFuzzer
        """
        xmlpostobj = XMLPost.XMLPost(
                                    host=fhost, generate=False, soapStr=fsoapstr,
                                    method=fmethodname, service=fservice, https=fhttps,
                                    keyfile=self.keyfile, certfile=self.certfile,
                                    proxy=self.proxy, proxyport=self.proxyport,
                                    version=self.version
                                    )
        if self.bauser and self.bapass:
            xmlpostobj.setBasicAuthCreds(self.bauser, self.bapass)
        if self.wrapper.getSoapAction(fmethodname):
            xmlpostobj.setSOAPAction(self.wrapper.getSoapAction(fmethodname))
        if self.alterhost:
            xmlpostobj.setAlternateHost(self.alterhost)

        return xmlpostobj
    # EOF: buildXMLPostObj

    # NAME     : startFuzzing
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : initiates the logging mechanism,
    #            then iterates over the list of
    #            chosen methods. Cleans up the
    #            data for the HTML if it is too large.
    #            Then via the wrapper class it invokes
    #            the target methods with the attack
    #            strings in the arguments.
    def startFuzzing(self):
        xmlpAttribs = {}
        xmlpMethods = {}
        self.logger.begingLogging(ids=self.IDSEvasion)

        # process each target method
        for method in self.methodList:
            #add method to xDos
            xmlpMethods[method.name] = {
                                        'host':self.wrapper.getHost(method.name),
                                        'uri':self.wrapper.getService(method.name),
                                        'soapAction':self.wrapper.getSoapAction(method.name),
                                        'type':method.name
                                        }
            # build list of target parameters
            if self.methodObj:
                method = self.methodObj
                args = ArgBuilder(self.methodObj.getParams(), self.getSim())
            else:
                args = ArgBuilder(method.getParams(), self.getSim())

            targetParams = []
            for p in args.getArgs():
                for k in p.args.iteritems():
                    # k[0] - param name
                    # k[1] - attack value
                    # populate array of the fuzzer object so that
                    # we can write this data out to XML
                    if [{k[1][0]:'C'}, k[1][1]] not in self.fuzzList:
                    	self.fuzzList.append([{k[1][0]:'C'}, k[1][1]])
                    if k[0] not in targetParams:
                        targetParams.append(k[0])
            # push out the already generated data to the XML file
            # for storage and possible re-use
            self.saveDictVectors(method.name)
            #####################################################
            # establish some baseline known valid XML payload
            # this will be used as a template for all attack payloads
            xmlfault = re.compile(r"fault", re.IGNORECASE)
            arr = ()
            tarr = []
            nt = []
            typecnt = 1
            t = self.wrapper.getTypesOfParams(method.name)
            # foreach param generate some bogus request data
            # for the baselining
            for a in t:
                # generate some random legit values based
                # on the data type in question (a)
                tarr.append(attackUtils.genRandomVal(a))
                nt.insert(typecnt, a)
                typecnt += 1

            arr = tuple(tarr)
            # payload holds the baseline xml for some legit known request
            payload = self.wrapper.invokeMethodGetPayload(method.name, arr, {})
            # typecnt - number of params
            # nt - array of data types where the index matches
            #      the number of the param
            # myxml holds the known good payload with all target params
            # converted to format string - %s

            if xmlfault.search(payload):
                print """ There was an anomaly encountered in interfacing
                with the provided target.  The neuroFuzz team
                is aware of these situational conditions and we
                are looking into the root cause(s) ... \n\n
                If you would like to help with this type of research
                send the following data along with some details about
                the target service to wsfuzzer@neurofuzz.com
                Response:\n
                """
                print payload
                sys.exit(2)

            try:
                if "StaticWrapper" in self.wrapper.idSelf():
                    myxml = self.wrapper.xmlpayload
                elif "WSDLWrapper" in self.wrapper.idSelf():
                    myxml = self.wrapper.getFinalPayloadForMethod(method.name)
                else:
                    myxml = xmlUtils.alterPayloadNodes(StringIO(payload), typecnt, nt)
            except Exception, e:
                print "There was an error with the XML Payload, cannot continue ... Error: %s" % e
                sys.exit(2)

            """
                if WSSE is used then inject the WSSE Security
                XML stanza into the SOAP Payload (in myxml),
                since the payload already contains:
                <soapenv:Header/>
                it has to be replaced by:
                <soapenv:Header>
                    sec stuff from WSSE class
                </soapenv:Header>
            """
            if self.wsseuser and self.wssepass:
                from lib import WSSE
                wsse = WSSE.WSSE(username=self.wsseuser, password=self.wssepass)
                wsse.generateWSSEStanza()
                wsseStanza = wsse.getWSSEStanza()
                newxml = StringIO(xmlUtils.addWSSEStanza(myxml.toxml(), wsseStanza))
            else:
                newxml = StringIO(myxml.toxml())
            #####################################################
            if self.IDSEvasion:
                self.IDSEvasionURI = self.antiids.encode_anti_ids(self.IDSEvasionOpt, method.name)
            #####################################################
            # this should populate self.baseLine with a value
            print "Baselining\n"
            self.doBaseline(newxml, method.name, typecnt, targetParams)
            #####################################################
            #####################################################
            # standard model where the user chose automated fuzzing
            if self.dictType == "standard":
                if (self.auto):
                    y = []
                    forwrite = []
                    print "Commencing the automated generation of dynamic attack vectors\n"
                    # generate and get XXE/WSSE attack vectors
                    self.x.generateXXEAttacks(method.name, targetParams)
                    for yy in self.x.getentities():
                        y.append([{yy[0]:'C'}, yy[1]])
                        forwrite.append([{yy[0].getvalue().strip():'C'}, yy[1]])
                    self.w.generateWSSEAttacks(method.name, targetParams)
                    for yy in self.w.getwssecurity():
                        y.append([{yy[0]:'C'}, yy[1]])
                        forwrite.append([{yy[0].getvalue().strip():'C'}, yy[1]])
                    # append file storing all generated attack vectors
                    #self.saveVectors(y)
                    self.saveVectors(forwrite)
                # no auto chosen but the standard Fuzz vectors have to be written
                # out to file
                else:
                    self.saveVectors()

                # print out the number of attack vectors generated
                fh = self.xmlp.getFileHandle()
                print "\nGenerated %d attack vectors and saved them out to file ... %s\n\n" % (self.xmlp.getChildElementCnt(fh, "vector"), fh)
            #####################################################
            # payload model where the user submitted fuzzing dictionary
            # from the XML files only grab the vectors that are full
            # payloads
            if self.dictType == "payload":
                print "Reading in pre-generated payload data\n"
                y = self.xmlp.getAllData(self.getSaveFileName(), "payload", "vector")
            #####################################################
            # print commencement message
            if self.methodObj:
                print "Starting to fuzz method (" + self.methodObj.name + ")"
            else:
                print "Starting to fuzz method (" + method.name + ")"

            # if IDS evasion is used
            if self.IDSEvasion:
                serviceURI = self.IDSEvasionURI
            else:
                serviceURI = self.wrapper.getService(method.name)

            # 1) process all XXE/WSSE based attacks first
            if self.auto:
                # y = ['attackvector','attackvectortype']
                for xxe in y:
                    # create XMLPost obj - check if client-side cert support is necessary
                    p = self.buildXMLPostObj(
                                            fhost=self.wrapper.getHost(method.name),
                                            fsoapstr=xxe[0].keys()[0],
                                            fmethodname=method.name,
                                            fservice=serviceURI,
                                            fhttps=self.wrapper.useTLS()
                                            )
                    p.doPost()

                    self.logger.logSoapInvoke(method=method.name, params='None - XXE attack', request=p.showXMLRequestPayload(type=1), attacktype=xxe[1], idsEvasion=self.IDSEvasionURI)
                    p.showRequest()
                    p.showResponse()
                    code = p.getResponseStatusCode()
                    self.logger.logResponse(roundtrip=p.getElapsed(), rawresponse=p.getRawData(), code=code, xmlpayload=p.getXMLResponsePayload())
                    #######################################################################
                    rawelapsed = p.getRawElapsed()
                    """
                        if the HTTP Response code is in the 50X family
                        or the round trip seriously exceeds the baseline
                        then the respective request is a candidate for
                        further target probing in the XDoS realm
                    """
                    if (str(code).startswith('50') or (rawelapsed > self.baseLine)):
                        # if the XMLP obj hasnt been created yet then create it
                        if not self.xdosObjExists:
                            self.xdosObjExists = self.xdos.createXDoSFileObj()
                        self.xdos.populateVectors(method.name, p.showXMLRequestPayload(type=1))
                        """
                            populate array with XMLPost object
                            to be used for polling
                            use the generic SOAP payload already
                            constructed (newxml) so that we can
                            manipulate it for polling
                        """
                        pollobj = self.buildXMLPostObj(
                                                        fhost=self.wrapper.getHost(method.name), fsoapstr=None,
                                                        fmethodname=method.name, fservice=serviceURI,
                                                        fhttps=self.wrapper.useTLS()
                                                        )
                        # add to array for possible use
                        if pollobj not in self.pollObjects:
                            self.pollObjects.append([pollobj,typecnt,newxml])
                    #######################################################################
            # 2) now process all POST data based attacks
            for args in args.getArgs():
                myargs = {}
                fortuple = []
                attacktuple = ()
                # check the length of each value
                for k, v in args.args.iteritems():
                    if v is not None:
                        if len(str(v[0])) > 30:
                            # optionally print out individual char's via index
                            # as such: v[0] + v[1] ...
                            myargs[k] = '[too much data - see payload below]'
                        else:
                            myargs[k] = v[0]
                        fortuple.append(v[0])
                        if v[1] <> "DEFAULT":
                            atttype = v[1]
                    else:
                        myargs[k] = "Default Value"
                        fortuple.append("Default Value")
                        atttype = "string"

                attacktuple = tuple(fortuple)
                att = StringIO(newxml.getvalue() % attacktuple)
                # create XMLPost obj - check if client-side cert support is necessary
                p = self.buildXMLPostObj(
                                        fhost=self.wrapper.getHost(method.name),
                                        fsoapstr=att,
                                        fmethodname=method.name,
                                        fservice=serviceURI,
                                        fhttps=self.wrapper.useTLS()
                                        )
                p.doPost()

                self.logger.logSoapInvoke(method=method.name, params=myargs, idsEvasion=self.IDSEvasionURI, request=p.showXMLRequestPayload(type=1), attacktype=atttype)

                p.showRequest()
                p.showResponse()
                code = p.getResponseStatusCode()
                self.logger.logResponse(roundtrip=p.getElapsed(), rawresponse=p.getRawData(), code=code, xmlpayload=p.getXMLResponsePayload())
                self.pdfw.writeData(method=method.name, params=myargs, request=p.showXMLRequestPayload(type=1), attacktype=atttype,
                                    roundtrip=p.getElapsed(), rawresponse=p.getRawData(), code=code, xmlpayload=p.getXMLResponsePayload())
                #####################################################
                rawelapsed = p.getRawElapsed()
                # if the HTTP Response code is in the 50X family
                # or the round trip seriously exceeds the baseline
                # then the respective request is a candidate for
                # further target probing in the XDoS realm
                if (str(code).startswith('50') or (rawelapsed > self.baseLine)):
                    # if the XMLP obj hasnt been created yet
                    # then create it
                    if not self.xdosObjExists:
                        self.xdosObjExists = self.xdos.createXDoSFileObj()
                    self.xdos.populateVectors(method.name, p.showXMLRequestPayload(type=1))
                    # populate array with XMLPost object to be used for polling
                    pollobj = self.buildXMLPostObj(
                                                    fhost=self.wrapper.getHost(method.name), fsoapstr=None,
                                                    fmethodname=method.name, fservice=serviceURI,
                                                    fhttps=self.wrapper.useTLS()
                                                    )
                    if pollobj not in self.pollObjects:
                        self.pollObjects.append([pollobj,typecnt,newxml])
                #####################################################
                if(self.wrapper.httpError == True):
                    print "broker server Response code " + self.wrapper.errorCode
                    self.logger.endLogging()
                    sys.exit()
                #####################################################

        #load the images in the html
        self.pdfw.createDoc()
        # TODO: generate encrypted PDF
        #self.pdfw.encryptPDF()
        self.logger.endLogging()
        #####################################################
        # setup a dict of the XMLPost attribs and pass that over to the
        # self.xdos obj
        xmlpAttribs['generate'] = False
        xmlpAttribs['https'] = self.wrapper.useTLS()
        xmlpAttribs['version'] = self.version
        xmlpAttribs['proxy'] = self.proxy
        xmlpAttribs['proxyport'] = self.proxyport
        if(self.IDSEvasion == True):
            xmlpAttribs['IDSEvasionURI'] = self.IDSEvasionURI
        if self.keyfile is not None and self.certfile is not None:
            xmlpAttribs['keyfile'] = self.keyfile
            xmlpAttribs['certfile'] = self.certfile
        if self.bauser is not None and self.bapass is not None:
            xmlpAttribs['bauser'] = self.bauser
            xmlpAttribs['bapass'] = self.bapass

        if self.alterhost is not None:
            xmlpAttribs['alterhost'] = self.alterhost
        self.xdos.setXMLPostAttribs(xmlpAttribs)
        self.xdos.setXMLPostMethods(xmlpMethods)

        # now write out any XDoS data to XML file
        if self.xdos.getVectorArrSize() > 0:
            self.xdos.saveVectors()
        #####################################################

        for method in self.methodList:
            if self.methodObj:
                print "Fuzzing completed for method (" + self.methodObj.name + ")"
            else:
                print "Fuzzing completed for method (" + method.name + ")"
    # EOF: startFuzzing

    # NAME     : doBaseline
    # PARAMS   : payload, methodName, cnt, arguments
    # RETURN   : Nothing
    # DESC     : instantiates a BaseLiner obj
    #            and ultimately establishes a
    #            round trip baseline time value for
    #            the given target.
    def doBaseline(self, payload, methodName, cnt, arguments):
        #####################################################
        # set up XMLPost object necessary for BaseLiner
        # if IDS evasion is used
        if self.IDSEvasion:
            serviceURI = self.IDSEvasionURI
        else:
            serviceURI = self.wrapper.getService(methodName)

        p = self.buildXMLPostObj(
                                fhost=self.wrapper.getHost(methodName),
                                fsoapstr=None,
                                fmethodname=methodName,
                                fservice=serviceURI,
                                fhttps=self.wrapper.useTLS()
                                )

        # create a baseliner object and give it all the info it needs
        # to go get busy
        b = BaseLiner.BaseLiner(xmlp=p, targetParams=arguments, cnt=cnt, modXML=payload)
        b.grind(padding=True)
        self.baseLine = b.getBaseLine()
        print "Done BaseLining round trips: %f\n\n" % self.baseLine
        #####################################################
    # EOF: doBaseline
