#!/usr/bin/python
"""
# Web Services Fuzzer
#
# FILENAME      : WSFuzzer.py
# AUTHORS       : Cosmin Banciu <ccbanciu [at] gmail dot com>
#               : David Shu <ydpanda [at] gmail dot com>
#               : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Andres Andreu
# DATE          : 12/7/2005
# LAST UPDATE   : 9/5/2010
# ABSTRACT      : A prog to perform fuzzing attacks against web services.
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

import getopt
import re
import sys

import Detector
import Fuzzer
import NoWSDLWrapper
import StaticWrapper
import WSDLWrapper

from lib import AntiIDS
from lib import HostChecker
from lib import PortScanner
from lib import XMLPayloadAnalyzer
from lib import XDoS
from lib import XDosAttack
from inc import configobj
from inc import genUtils
from inc import vars

# NAME     : processConfFile
# PARAMS   : config
# RETURN   : Nothing
# DESC     : Populates the vars.confval dictionary with
#            values read in from the conf file
def processConfFile(config):
    for c in config:
        if vars.confval.has_key(c):
            vars.confval[c] = config[c]
# EOF: processConfFile

# set some regexes
y = re.compile(r"y", re.IGNORECASE)
dotnet = re.compile(r".asmx|.aspx", re.IGNORECASE)

# init variables and dict
vars.initializeVars()
vars.initializeDict()
# prog version check
genUtils.doProgVersionCheck()
# file version check
genUtils.doFileVersionCheck()

# handle switches from input
try:
    opts, args = getopt.getopt(sys.argv[1:], "l:h:e:d:n:w:",
                               ['wsdl=', 'endpoint=', 'namespace=', 'host=',
                               'bauser=', 'bapass=', 'keyfile=', 'certfile=',
                               'xml=', 'proxy=', 'proxyport=', 'conf=', 'attacks=',
                               'wsseuser=', 'wssepass='])
except getopt.GetoptError, e:
    print str(e)
    print '\nRun with no arguments to see help...\n'
    sys.exit(2)

# now process all switches/arguments
for o, a in opts:
    if o == '-d': verbosity = 3
    if o == '-l': lev_setting = a
    if o in ('-h', '--host'): vars.target = a
    if o in ('-e', '--endpoint'): vars.endpoint = a
    if o in ('-n', '--namespace'): vars.namespace = a
    if o in ('-w', '--wsdl'): vars.wsdl = a
    if o in ('-x','--xDos'): vars.xmlDosFile = a
    if o == '--conf': vars.config = configobj.ConfigObj(a)
    if o == '--bauser': vars.bauser = a
    if o == '--bapass': vars.bapass = a
    if o == '--wsseuser': vars.wsseuser = a
    if o == '--wssepass': vars.wssepass = a
    if o == '--keyfile': vars.keyfile = a
    if o == '--certfile': vars.certfile = a
    if o == '--xml': vars.xml = a
    if o == '--attacks': vars.attacks = a
    if o == '--proxyport': vars.proxyport = int(a.strip())
    if o == '--proxy': vars.proxy = a

# No args
if len(sys.argv) < 2:
    genUtils.usage(0)

# The config obj is populated so we are dealing with a conf file
if vars.config:
    # first extract the data from the conf file
    processConfFile(vars.config)
    # validate the extracted data against the presented mode
    x = genUtils.validateConfig(vars.config)
    if x[0] is False:
        print "%s is missing from your config file add it in and try again\n" % x[1]
        sys.exit(2)

# Validity checks for proxy server and ports
genUtils.validateCombo(vars.proxy, 'proxy server', vars.proxyport, 'proxy port')
genUtils.validateCombo(vars.proxyport, 'proxy port', vars.proxy, 'proxy server')
# Validity checks for client-side cert values
genUtils.validateCombo(vars.keyfile, 'key file name', vars.certfile, 'certificate')
genUtils.validateCombo(vars.certfile, 'certificate', vars.keyfile, 'key file name')
# Validity checks for Basic Auth and client-side cert values
genUtils.validateCombo(vars.bauser, 'Basic Auth User', vars.bapass, 'Basic Auth Password')
genUtils.validateCombo(vars.bapass, 'Basic Auth Password', vars.bauser, 'Basic Auth User')
# Validity checks for WS-Security
genUtils.validateCombo(vars.wsseuser, 'WS-Security User', vars.wssepass, 'WS-Security Password')
genUtils.validateCombo(vars.bapass, 'WS-Security Password', vars.bauser, 'WS-Security User')

# NAME     : populateVars
# PARAMS   : dict
# RETURN   : Nothing
# DESC     : this function populates variables
#            with values from a conf file
#            It assumes the each key from the
#            dict has a corresponding variable
#            by the same name
def populateVars(dict):
    comma = re.compile(r",", re.IGNORECASE)
    for key in dict.iterkeys():
        if key <> 'Mode':
            if key == 'parameters':
                paramsArray = []
                if comma.search(str(dict[key])):
                    for i in dict[key]:
                        paramsArray.append(i)
                else:
                    paramsArray.append(dict[key])
            else:
                #globals()['vars.'+key] = dict[key]
                vars.setVar(key,dict[key])
            genUtils.echoStatus(vars.confvaloutput[key], dict[key])
# EOF: populateVars

# NAME     : establishMethods
# PARAMS   : wrapper
# RETURN   : Nothing
# DESC     : this function is intercative so as to
#            setup the logistics behind a given pen test.
#            It allows the user to choose the target methods
#            from a list of discovered methods.
#            Then it allows you to choose the type of attack
#            you want to engage in.
#            At the end of the process some fuzzer based objects
#            are populated with necessary data for the attack.
def establishMethods(wrapper=None, dictionary=None, automate=None, simultaneous=None):
    if wrapper != None:
        methods = wrapper.getMethods()
        total = len(methods)
        counter = 0
        while counter < total:
            print "\nMethod[%s]: %s" % (counter, methods[counter])
            print "Params:"
            paramsHash = wrapper.getParamsOfMethod(methods[counter])
            for param in  paramsHash.keys():
                print "\t" + param + "(" + paramsHash[param] + ")"
            counter = counter + 1

        methodsChosen = raw_input("\nSelect the methods you want to Fuzz(ex: 0,1,2,3 or A for All)\nMethods: ")
        methodsChosen = methodsChosen.strip('\r')
        if (methodsChosen == 'A'):
            methodsArray = []
            num = 0
            for w in wrapper.getMethods():
                methodsArray.append(num)
                num += 1
        else:
            methodsArray = methodsChosen.split(',')

        pcount = 0
        for m in methodsArray:
            for p in wrapper.getParamsOfMethod(methods[int(m)]):
                pcount += 1

        if pcount > 1 and simultaneous is None:
            vars.simultaneous = raw_input("\nWould you like to attack all the chosen params simultaneously? ")
            vars.simultaneous = vars.simultaneous.strip('\r')
        elif simultaneous is None:
            vars.simultaneous = "No"
        # simultaneous mode chosen
        if y.search(vars.simultaneous):
            fuzzer.setSim(True)
            if vars.attacks is None:
                if dictionary is None:
                    dictionary = genUtils.defineDictionaryName(0)

                if automate is None:
                    automate = genUtils.getAutoAttackResponse(0)

            for methodInt in methodsArray:
                print "\nMethod: " + methods[int(methodInt)]
                method = Fuzzer.Method(methods[int(methodInt)])
                paramsHash = wrapper.getParamsOfMethod(methods[int(methodInt)])

                for param in paramsHash.keys():
                    print "\tParameter: " + param + " Type: " + paramsHash[param]

                    if vars.allparams is not None and y.search(vars.allparams):
                        fuzzChosen = 'yes'
                    else:
                        fuzzChosen = raw_input("\nWould you like to fuzz this param: ")
                        fuzzChosen = fuzzChosen.strip('\r')
                    fuzzThisParam = False

                    if vars.attacks is None:
                        fuzzer.setDictType("standard")
                        fuzzer.initObjects()
                        if y.search(automate):
                            fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard", True)
                            fuzzer.setAuto(True)
                        else:
                            fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard")
                    else:
                        fuzzType = Fuzzer.DictionaryFuzz(dictionaryType="payload")
                        fuzzer.setSaveFileName(vars.attacks)
                        fuzzType.setDictionaryFileName(vars.attacks)
                        fuzzer.setDictType("payload")

                    if (y.search(fuzzChosen)):
                        print "\tFuzzing this param"
                        fuzzThisParam = True

                    parameter = Fuzzer.Parameter(param, paramsHash[param], fuzzType, fuzzThisParam)
                    method.addParameter(parameter)
                fuzzer.addMethodToFuzz(method)
        else:
            for methodInt in methodsArray:
                print "\nMethod: " + methods[int(methodInt)]
                method = Fuzzer.Method(methods[int(methodInt)])
                paramsHash = wrapper.getParamsOfMethod(methods[int(methodInt)])
                for param in paramsHash.keys():
                    if vars.attacks is None:
                        fuzzChosen = genUtils.defineFuzzType(param)
                        fuzzThisParam = False
                        fuzzType = None
                    else:
                        fuzzChosen = 1

                    if(fuzzChosen == 0):
                        print "\nNot fuzzing this param"
                        fuzzThisParam = False
                    elif (fuzzChosen == 1):
                        print "\tFuzzing using dictionary"
                        if vars.attacks is None:
                            if dictionary is None:
                                dictionary = genUtils.defineDictionaryName(0)

                            if automate is None:
                                automate = genUtils.getAutoAttackResponse(0)

                        if vars.attacks is None:
                            fuzzer.setDictType("standard")
                            fuzzer.initObjects()
                            if y.search(automate):
                                fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard", True)
                                fuzzer.setAuto(True)
                            else:
                                fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard")
                        else:
                            fuzzType = Fuzzer.DictionaryFuzz(dictionaryType="payload")
                            fuzzer.setDictType("payload")
                            fuzzer.setSaveFileName(vars.attacks)
                            fuzzType.setDictionaryFileName(vars.attacks)

                        fuzzThisParam = True
                    elif (fuzzChosen == 2):
                        print "\nFuzzing using patterns not implemented yet\n\n"
                        sys.exit(0)
                    else:
                        print "Input not valid\n\n"
                        sys.exit(0)
                    parameter = Fuzzer.Parameter(param, paramsHash[param], fuzzType, fuzzThisParam)
                    method.addParameter(parameter)
                fuzzer.addMethodToFuzz(method)
# EOF: establishMethods

# NAME     : establishXDosAttackParams
# PARAMS   : XDoS
# RETURN   : ThreadMaster
# DESC     : this function is intercative so as to
#            setup the logistics behind a given xDos attack.
#            It allows the user to choose the ammount of threads,
#            the total time to conduct the attack and total Threads timeout
#            threshold.
#
def establishXDosAttackParams(xdos = None, totalThreads = None, minutes = None, totalTimeouts = None):
    print "\nHow many threads would you like generated(leave blank for default of 10)?"
    totalThreads = raw_input("Answer: ")
    totalThreads = totalThreads.strip('\r')
    if totalThreads == '':
        totalThreads = 10
    else:
        totalThreads = int(totalThreads)

    print "\nHow many minutes should we attack the target(leave blank for default of 10 minutes)?"
    minutes = raw_input("Answer: ")
    minutes = minutes.strip('\r')
    if minutes == '':
        minutes = 10
    else:
        minutes = int(minutes)

    print "\nChoose a threshold number for total timeouts before ending the attack(leave blank for default of 100)?"
    totalTimeouts = raw_input("Answer: ")
    totalTimeouts = totalTimeouts.strip('\r')
    if totalTimeouts == '':
        totalTimeouts = 100
    else:
        totalTimeouts = int(totalTimeouts)

    print "You chose: %d threads for %d minutes and total timeout threshold of %d" % (totalThreads, minutes, totalTimeouts)
    return XDosAttack.ThreadMaster(totalThreads, 60 * minutes, totalTimeouts, xdos)
# EOF

#create HostChecker obj
hchecker = HostChecker.HostChecker()
# set things up based on the switches entered by the user
# and/or data read in from some config file
# if -w is used or mode 1 from config file
if ((vars.wsdl and (not vars.endpoint and not vars.namespace) and not vars.target) or vars.confval['Mode'] == '1'):
    # config file is used, Mode 1
    if vars.confval['Mode'] == '1':
        populateVars(vars.confval)

    wrapper = WSDLWrapper.WSDLWrapper(vars.wsdl, vars.proxy, vars.proxyport, vars.bauser, vars.bapass, genUtils.VERSION)
    print "WSDL Discovered (%s)" % (vars.wsdl)
    if vars.directory is None:
        vars.directory = genUtils.defineDirName(0)
    fuzzer = Fuzzer.Fuzzer(wrapper=wrapper, dirName=vars.directory)
    fuzzer.setVer(genUtils.VERSION)
    # Basic Auth is in use
    if vars.bauser is not None and vars.bapass is not None:
        fuzzer.setBAFuzz(vars.bauser, vars.bapass)
    # Client-side cert is in use
    if vars.keyfile is not None and vars.certfile is not None:
        fuzzer.setCertFuzz(vars.keyfile, vars.certfile)
    # WS-Sec
    if vars.wsseuser and vars.wssepass:
        fuzzer.setWSSEFuzz(vars.wsseuser, vars.wssepass)

    establishMethods(wrapper=wrapper, dictionary=vars.dictionary, automate=vars.automate, simultaneous=vars.simultaneous)
# if -h is used
elif (vars.target and not vars.wsdl and (not vars.endpoint and not vars.namespace)):
    vars.directory = genUtils.defineDirName(0)

    print "0) Basic Discovery (faster but less accurate)"
    print "1) Advanced Discovery (slower and more intrusive but more thorough and accurate)"
    print "2) Advanced Discovery (like #1) with port scanning first"
    probeChosen = input("\nProbe Type: ")

    detect = Detector.WSDLDetector()
    if (probeChosen == 0):
        detect.detect(vars.target, 'basic', 5)
    elif (probeChosen == 1):
        spiderChosen = raw_input("\nWould you like to Spider the target on top of the advanced probe: ")
        spiderChosen = spiderChosen.strip('\r')
        if y.search(spiderChosen):
            detect.detect(vars.target, 'advanced', 7, True)
        else:
            detect.detect(vars.target, 'advanced', 7)
    elif (probeChosen == 2):
        startPort = input("\nBeginning TCP port for scan: ")
        endPort = input("\nEnding TCP port for scan: ")
        if (startPort in range (0, 65534)) and (endPort in range (1, 65535)
                                                and startPort <= endPort):
            portScan = PortScanner.WrapPortScanner(vars.target, startPort, endPort)
            ports = portScan.getports()
            total = len(ports)
            cnt = 0

            print "Open TCP ports discovered for target %s:" % vars.target
            while cnt < total:
                print "[%d] %d" % (cnt, ports[cnt])
                cnt += 1

            pickedPort = input("\nPick one via numeric index (i.e. 1 for [1]): ")
            if pickedPort in range(total) and ports[pickedPort]:
                spiderChosen = raw_input("\nWould you like to Spider the target on top of the advanced probe: ")
                spiderChosen = spiderChosen.strip('\r')
                if y.search(spiderChosen):
                    detect.detect(vars.target + ":" + str(ports[pickedPort]), 'advanced', 7, True)
                else:
                    detect.detect(vars.target + ":" + str(ports[pickedPort]), 'advanced', 7)
            else:
                print "That port is out of range .... exiting"
                sys.exit(0)

        else:
            print "There was a problem with the port data entered ... exiting"
            sys.exit(0)
    else:
        print "That entry is invalid ... exiting"
        sys.exit(0)

    if (detect.final_targets):
        print "Discovered WSDL links: "
        i = 0
        while i < len(detect.final_targets):
            print "%d => %s" % (i, detect.final_targets[i])
            i += 1

        t = input("Please choose ONE link, via numeric index, from the above list\n")
        if (t >= 0 and t <= len(detect.final_targets)):
            #TODO Run some tests with new WSDL parser
            wrapper = WSDLWrapper.WSDLWrapper(detect.final_targets[t],vars.bauser, vars.bapass)
            fuzzer = Fuzzer.Fuzzer(wrapper, vars.directory)
            fuzzer.setVer(genUtils.VERSION)
            # Basic Auth is in use
            if vars.bauser is not None and vars.bapass is not None:
                fuzzer.setBAFuzz(vars.bauser, vars.bapass)
            # Client-side cert is in use
            if vars.keyfile is not None and vars.certfile is not None:
                fuzzer.setCertFuzz(vars.keyfile, vars.certfile)
            # WS-Sec
            if vars.wsseuser and vars.wssepass:
                fuzzer.setWSSEFuzz(vars.wsseuser, vars.wssepass)

            establishMethods(wrapper=wrapper)
        else:
            print "Value chosen is out of array bounds \n"
            sys.exit(0)
    else:
        print "Sorry no WSDL links discovered\n"
        sys.exit(0)
# if -e and -n are used or mode 2 from config file
elif ((vars.endpoint and vars.namespace) and (not vars.wsdl and not vars.target) or vars.confval['Mode'] == '2'):
    # config file is used, Mode 2
    if vars.confval['Mode'] == '2':
        populateVars(vars.confval)
    else:
        methodChosen = raw_input("\nWhat method do you wish to execute?\nMethod Name: ")
        methodChosen = methodChosen.strip('\r')
        methodParams = raw_input("\nEnter the parameter names for this method \nseparated by comma (i.euid,date)\nParameter List: ")
        methodParams = methodParams.strip('\r')
        paramsArray = methodParams.split(',')

    print "\nEndpoint Discovered (%s)" % (vars.endpoint)

    if vars.directory is None:
        vars.directory = genUtils.defineDirName(0)
    wrapper = NoWSDLWrapper.NoWSDLWrapper(vars.endpoint, vars.namespace)
    fuzzer = Fuzzer.Fuzzer(wrapper, vars.directory)
    fuzzer.setVer(genUtils.VERSION)
    # Basic Auth is in use
    if vars.bauser is not None and vars.bapass is not None:
        fuzzer.setBAFuzz(vars.bauser, vars.bapass)
    # Client-side cert is in use
    if vars.keyfile is not None and vars.certfile is not None:
        fuzzer.setCertFuzz(vars.keyfile, vars.certfile)
    # WS-Sec
    if vars.wsseuser and vars.wssepass:
        fuzzer.setWSSEFuzz(vars.wsseuser, vars.wssepass)

    print "\nMethod: " + methodChosen
    method = Fuzzer.Method(methodChosen)

    # get types of params here
    pcount = 0
    for p in paramsArray:
        pp = raw_input('\nType for param %s: ' % p)
        # get type string from user input
        # possible val's are string, integer, boolean, float, array
        # pump it into an array in NoWSDLWrapper
        wrapper.setParamType(method, p, pp)
        pcount += 1

    if pcount > 1 and vars.simultaneous is None:
        vars.simultaneous = raw_input("\nWould you like to attack all the chosen params simultaneously? ")
        vars.simultaneous = vars.simultaneous.strip('\r')
    elif vars.simultaneous is None:
        vars.simultaneous = 'No'

    # simultaneous mode chosen
    if y.search(vars.simultaneous):
        fuzzer.setSim(True)

        if vars.attacks is None:
            if vars.dictionary is None:
                vars.dictionary = genUtils.defineDictionaryName(0)

            if vars.automate is None:
                vars.automate = genUtils.getAutoAttackResponse(0)

        for param in paramsArray:
            print "\tParameter: " + param

            if vars.allparams is not None and y.search(vars.allparams):
                fuzzChosen = 'yes'
            else:
                fuzzChosen = raw_input("\nWould you like to fuzz this param: ")
                fuzzChosen = fuzzChosen.strip('\r')
            fuzzThisParam = False

            if vars.attacks is None:
                fuzzer.setDictType("standard")
                fuzzer.initObjects()
                if y.search(vars.automate):
                    fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard", True)
                    fuzzer.setAuto(True)
                else:
                    fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard")
            else:
                fuzzType = Fuzzer.DictionaryFuzz(dictionaryType="payload")
                fuzzer.setDictType("payload")
                fuzzer.setSaveFileName(vars.attacks)
                fuzzType.setDictionaryFileName(vars.attacks)

            if (y.search(fuzzChosen)):
                print "\tFuzzing this param"
                fuzzThisParam = True

            parameter = Fuzzer.Parameter(param, None, fuzzType, fuzzThisParam)
            method.addParameter(parameter)
        fuzzer.addMethodToFuzz(method)
    else:
        for param in paramsArray:
            if vars.attacks is None:
                fuzzChosen = genUtils.defineFuzzType(param)
                fuzzThisParam = False
                fuzzType = None
            else:
                fuzzChosen = 1

            if(fuzzChosen == 0):
                print "\nNot fuzzing this param"
                fuzzThisParam = False
            elif (fuzzChosen == 1):
                print "\tFuzzing using dictionary"
                if vars.attacks is None:
                    if dictionary is None:
                        dictionary = genUtils.defineDictionaryName(0)

                    if vars.automate is None:
                        vars.automate = genUtils.getAutoAttackResponse(0)

                if vars.attacks is None:
                    fuzzer.setDictType("standard")
                    fuzzer.initObjects()
                    if y.search(vars.automate):
                        fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard", True)
                        fuzzer.setAuto(True)
                    else:
                        fuzzType = Fuzzer.DictionaryFuzz(dictionary, "standard")
                else:
                    fuzzType = Fuzzer.DictionaryFuzz(dictionaryType="payload")
                    fuzzer.setDictType("payload")
                    fuzzer.setSaveFileName(vars.attacks)
                    fuzzType.setDictionaryFileName(vars.attacks)

                fuzzThisParam = True
            elif (fuzzChosen == 2):
                print "\nFuzzing using patterns not implemented yet\n\n"
                sys.exit(0)
            else:
                print "Input not valid\n\n"
                sys.exit(0)
            parameter = Fuzzer.Parameter(param, None, fuzzType, fuzzThisParam)
            method.addParameter(parameter)
        fuzzer.addMethodToFuzz(method)
# if the --xml switch is used or mode 3 from a conifg file
elif vars.xml or vars.confval['Mode'] == '3':
    if vars.confval['Mode'] == '3':
        populateVars(vars.confval)
        # check host right away and die if it is not available
        if hchecker.isHostAvailable(host) is False:
            print "Sorry but the submitted host is not reachable"
            sys.exit(0)
    else:
        print "Since you are using the static XML feature we need some data from you...\n"
        host = raw_input("\nHost to attack (i.e. sec.neurofuzz.com): ")
        host = host.strip('\r')
        # check host and die if host not available
        if hchecker.isHostAvailable(host) is False:
            print "Sorry but the submitted host is not reachable"
            sys.exit(0)
        uri = raw_input("\nURI to attack (i.e. /axis/EchoHeaders.jws): ")
        uri = uri.strip('\r')
        soapyn = raw_input("\nDo you want use a SOAPAction attrib? (.Net services usually require this): ")
        soapyn = soapyn.strip('\r')
        if y.search(soapyn):
            soapaction = raw_input("\nEnter the SOAPAction value: ")
            soapaction = soapaction.strip('\r')

        if vars.attacks is None:
            if vars.dictionary is None:
                vars.dictionary = genUtils.defineDictionaryName(0)

            if vars.automate is None:
                vars.automate = genUtils.getAutoAttackResponse(0)

    xmlpa = XMLPayloadAnalyzer.XMLPayloadAnalyzer(vars.xml)
    wrapper = StaticWrapper.StaticWrapper(xmlpa)
    if vars.directory is None:
        vars.directory = genUtils.defineDirName(0)

    wrapper.setHost(host)
    wrapper.setPayload(vars.xml)
    wrapper.setProto(host)
    if not uri.startswith("/"):
        uri = "/%s" % uri
    wrapper.setUri(uri)

    n = xmlpa.methodName
    method = Fuzzer.Method(n)
    wrapper.setMethod(n)
    fuzzer = Fuzzer.Fuzzer(wrapper, vars.directory, method)
    fuzzer.setVer(genUtils.VERSION)

    # Basic Auth is in use
    if vars.bauser is not None and vars.bapass is not None:
        fuzzer.setBAFuzz(vars.bauser, vars.bapass)
    # Client-side cert is in use
    if vars.keyfile is not None and vars.certfile is not None:
        fuzzer.setCertFuzz(vars.keyfile, vars.certfile)
    # WS-Sec
    if vars.wsseuser and vars.wssepass:
        fuzzer.setWSSEFuzz(vars.wsseuser, vars.wssepass)

    if soapaction is not None:
        wrapper.setSoapAction(soapaction)

    if dotnet.search(uri) and soapaction is None:
        print "Unless some serious masking/spoofing is in place, it seems "
        print "you are targeting a .Net host so you will need to use a SOAPAction header ..."
        soapaction = raw_input("\nEnter the SOAPAction value: ")
        wrapper.setSoapAction(soapaction.strip('\r'))

    print "\nMethod: " + n

    xmlpa.getParamsHash()
    h = xmlpa.paramsHash
    for param in h:
        print "Param discovered: %s, of type: %s" % (param, h[param])
        wrapper.setParamType(param, h[param])

    if len(h) >= 1:
        fuzzer.setSim(True)
        print "Simultaneous Mode activated"

        for param in h:
            print "\tParameter: " + param

            if vars.allparams is not None and y.search(vars.allparams):
                fuzzChosen = 'yes'
            else:
                fuzzChosen = raw_input("\nWould you like to fuzz this param: ")
                fuzzChosen = fuzzChosen.strip('\r')
            fuzzThisParam = False

            if vars.attacks is None:
                fuzzer.setDictType("standard")
                fuzzer.initObjects()
                if y.search(vars.automate):
                    fuzzType = Fuzzer.DictionaryFuzz(vars.dictionary, "standard", True)
                    fuzzer.setAuto(True)
                else:
                    fuzzType = Fuzzer.DictionaryFuzz(vars.dictionary, "standard")
            else:
                fuzzType = Fuzzer.DictionaryFuzz(dictionaryType="payload")
                fuzzer.setDictType("payload")
                fuzzer.setSaveFileName(vars.attacks)
                fuzzType.setDictionaryFileName(vars.attacks)

            if y.search(fuzzChosen):
                print "\tFuzzing this param"
                fuzzThisParam = True

            parameter = Fuzzer.Parameter(param, None, fuzzType, fuzzThisParam)
            method.addParameter(parameter)
        fuzzer.addMethodToFuzz(n)
# if -x is used or mode 4 from config file
elif (vars.xmlDosFile and (not vars.endpoint and not vars.namespace and not vars.wsdl and not vars.target) or vars.confval['Mode'] == '4'):
    #run a xDos attack from a previous run
    print "You've chosen to attempt a xml Dos attack using previous Fuzzing results"
    print "Project dir chosen: %s" % vars.xmlDosFile
    #check if dire and file exists, if not exit
    master = establishXDosAttackParams(XDoS.XDoS(vars.xmlDosFile))
    print "Starting Dos Attack"
    #socket.setdefaulttimeout(15)
    master.start()
    print "Threads Initialized, xml Dos Attack started"
    master.join()    # Wait for the background task to finish
    print "Finished XDos Attack in %d minutes" % (master.getRunTime() / 60)
else:
    genUtils.usage(0)

# by this point the fuzzer is established
if vars.proxy and vars.proxyport:
    fuzzer.setProxy(vars.proxy)
    fuzzer.setProxyPort(vars.proxyport)

antiids = AntiIDS.AntiIDS(wrapper)
if vars.idsevasion is None:
    print "\nWould you like to enable IDS evasion(y/n)?"
    vars.idsevasion = raw_input("Answer: ")
    vars.idsevasion = vars.idsevasion.strip('\r')

if y.search(vars.idsevasion):
    fuzzer.setIDSEvasion(True)
    if vars.idsevasionopt is None:
        genUtils.printIDSOpts()
        vars.idsevasionopt = raw_input("Option: ")
        vars.idsevasionopt = vars.idsevasionopt.strip('\r')
    # validate the option value passed in
    while genUtils.validateIDSEvasionOptInput(vars.idsevasionopt) == False:
       	print "\n\nInvalid IDS Evasion Option, please try again\n"
       	genUtils.printIDSOpts()
       	vars.idsevasionopt = raw_input("Option: ")
       	vars.idsevasionopt = vars.idsevasionopt.strip('\r')

    if vars.idsevasionopt is not None:
        fuzzer.setIDSEvasionOpt(vars.idsevasionopt)

    if fuzzer.IDSEvasionOpt == 'R':
        print "\nIs this a Windows target(y/n)?"
        idsWin = raw_input("Answer: ")
        idsWin = idsWin.strip('\r')
        if y.search(idsWin):
            antiids.idsWin = True
else:
    fuzzer.IDSEvasion = False
    print "Not using IDS evasion"

if vars.alternatehost is None:
    print "\nWould you like to alter the value in the Host Header(y/n)?"
    vars.alternatehost = raw_input("Answer: ")
    vars.alternatehost = vars.alternatehost.strip('\r')

    if y.search(vars.alternatehost):
        alternatehostval = raw_input("Value for Host Header: ")
        alternatehostval = alternatehostval.strip('\r')
        fuzzer.setAlternateHost(alternatehostval)
elif vars.alternatehost <> "no" and vars.alternatehost <> "No":
    fuzzer.setAlternateHost(vars.alternatehost)

print "\nShall I begin Fuzzing(y/n)?"
answer = raw_input("Answer: ")
answer = answer.strip('\r')

if y.search(answer):
    print "\nCommencing the fuzz ...."
    fuzzer.startFuzzing()
    if fuzzer.xdosObjExists:
        print "\nWould you like to attempt a xml Dos Attack?(y/n)?"
        dosAnswer = raw_input("Answer: ")
        dosAnswer = dosAnswer.strip('\r')
        if y.search(dosAnswer):
            import time
            from lib import BaseLiner

            master = establishXDosAttackParams(fuzzer.xdos)
            print "Starting Dos Attack"
            master.start()
            print "Threads Initialized, xml Dos Attack started"
            """
                let's poll the target with simple SOAP
                requests. If it's available then the
                XDoS attack has not worked.
            """
            totalRunTime = time.time() + master.getTotalRunTime()
            print "Polling target - checking for availability during XDoS Attack, total runtime: %.2f seconds\n" % master.getTotalRunTime()
            while time.time() < totalRunTime:
                for xmlpobj in fuzzer.pollObjects:
                    b = BaseLiner.BaseLiner(xmlp=xmlpobj[0], targetParams=None, cnt=xmlpobj[1], modXML=xmlpobj[2])
                    b.grind(padding=False)
                    print "State of target is: UP - average response time: %.2f seconds" % (b.getBaseLine() / 60)
                    time.sleep(5)

            print "XDoS test has finished, waiting for related threads to get cleaned up"
            master.join()    # Wait for the background task to finish
            fintime = master.getRunTime() / 60
            if fintime > 1:
                min = 'minnutes'
            else:
                min = 'minute'
            print "Finished XDos Attack in %d %s" % (fintime,min)
else:
    print "****  Ending program run, you entered '%s'  ****\n" % answer
