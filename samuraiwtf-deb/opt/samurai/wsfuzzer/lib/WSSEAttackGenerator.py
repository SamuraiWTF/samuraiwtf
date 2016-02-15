"""
# Web Services Fuzzer
#
# FILENAME      : WSSEAttackGenerator.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 9/01/2006
# LAST UPDATE   : 8/28/2010
# ABSTRACT      : A library to dynamically generate some WSSE XML content attack strings.
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
import binascii

from inc import attackUtils
import attackTags

class WSSEAttackGenerator:
    def __init__(self):
        self.wssecurity = []
        self.xml = {}
        self.getTags()
        self.rnd = attackUtils.genRandom(300, b64=True)
        self.rndUser = attackUtils.genRandom(300, b64=True)
        self.rndPass = attackUtils.genRandom(300, b64=True)
        self.rnd3 = attackUtils.genRandom(3000, b64=True)
        self.rnd6 = attackUtils.genRandom(6000, b64=True)

    # NAME     : addstring
    # PARAMS   : data
    # RETURN   : Nothing
    # DESC     : Populates array respective to the
    #            datatype submitted
    def addstring(self, data):
        # comma at the end is for printing on one line
        #print "%d" % len(self.wssecurity),
        self.wssecurity.append([data,"WS-Security Attack"])
    # EOF: addstring

    # NAME     : getTags
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Populates array of XML tags
    def getTags(self):
        self.xml = attackTags.AttackTagGenerator().getTags()
    # EOF: getTags

    # NAME     : getwssecurity
    # PARAMS   : None
    # RETURN   : array
    # DESC     : Returns array of generated XML attack
    #            strings.
    def getwssecurity(self):
        return self.wssecurity
    # EOF: getTags

    # NAME     : genLogisticTags
    # PARAMS   : None
    # RETURN   : 3 strings
    # DESC     : Makes a new subelement within an
    #            XML doc.
    def genLogisticTags(self, digest, nonce, created):
        tmp = ''
        tmp = (self.xml["wp_open"] + "%s" + self.xml["wp_close"]) % binascii.b2a_base64(digest).strip()
        tmp = tmp + (self.xml["wn_open"] + "%s" + self.xml["wn_close"]) % binascii.b2a_base64(nonce).strip()
        tmp = tmp + (self.xml["wc_open"] + "%s" + self.xml["wc_close"]) % created.strip()

        return tmp
    # EOF: genLogisticTags

    # NAME     : genOpenWSSEXML
    # PARAMS   : None
    # RETURN   : string
    # DESC     : Generates XML header and open XML tags
    #            for the envelope, header, wsse sec,
    #            and userNameToken
    def genOpenWSSEXML(self):
        return self.xml["xh"] + self.xml["env_open"] + self.xml["header_open"] +  self.xml["sec_open"] + self.xml["ut_open"]
    # EOF: genOpenWSSEXML

    # NAME     : genMidWSSEXML
    # PARAMS   : None
    # RETURN   : string
    # DESC     : Generates middle XML tags.  This includes
    #            close tags for the userNameToken, wsse sec,
    #            and header.  Then it opens up the body tag.
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

    # NAME     : generateWSSEAttacks
    # PARAMS   : list
    # RETURN   : Nothing
    # DESC     : Wrapper function that calls all the other
    #            functions that will generate WSSE attack XML
    def generateWSSEAttacks(self, method, params):
        print "Mutating Methods ...",
        self.generateWSSEMethodMutate(method, params)
        self.generateWSSEMethodMutate(method, params, 1)
        print "Done\vMutating XML Elements ...",
        self.generateWSSEMutatedTag(method)
        print "Done\n"
    # EOF: generateWSSEAttacks

    # NAME     : generateWSSEMutatedTag
    # PARAMS   : method
    # RETURN   : Nothing
    # DESC     : generates pseudo random WSSE XML attack data.
    #            "open" generates numerous open XML tags with no
    #            corresponding close tags
    #            "random" generates random sets of data and
    #            makes them act as tags
    #            "close" generates numerous close XML tags
    #            with no corresponding open tags
    def generateWSSEMutatedTag(self, method):
        if method:
            type = ['open', 'random', 'close']
            for t in type:
                soapStr = StringIO()

                soapStr.write(self.genOpenWSSEXML())
                soapStr.write((self.xml["un_open"] + "%s" + self.xml["un_close"]) % (self.rndUser))
                # structural threat: weird structure
                soapStr.write("<%s %s>" % (self.rnd, attackUtils.genNAttribs(300)))

                if t == 'open':
                    # structural threat: weird structure - large # open tags
                    for i in range(30):
                        soapStr.write('<%s>' % self.rnd)
                if t == 'random':
                    # structural threat: huge random document
                    for i in range(30):
                        soapStr.write('<%s>%s</%s>' % (self.rnd, self.rnd, self.rnd))
                if t == 'close':
                    # structural threat: weird structure  - large # close tags
                    for i in range(30):
                        soapStr.write('</%s>' % self.rnd)

                created, nonce, digest = attackUtils.genLogisticVals(self.rndUser, self.rndPass)
                soapStr.write(self.genLogisticTags(digest, nonce, created))
                soapStr.write(self.genMidWSSEXML() + attackUtils.genMethodRandTags(method) + self.genCloseWSSEXML())

                self.addstring(soapStr)
    # EOF: generateWSSEMutatedTag

    # NAME     : generateWSSEMethodMutate
    # PARAMS   : method, params, mix
    # RETURN   : Nothing
    # DESC     : generates pseudo random WS-Security XML attack data.
    #            The mix switch will create a condition where a given
    #            open tag has a non-matching close tag
    def generateWSSEMethodMutate(self, method, params, mix = None):
        if method:
            vectors = ['straight','unt','un','pass','nonce', 'created']
            mutate = ['noclose', 'noopen', 'opentag', 'closetag']
            for mutation in mutate:
                for vector in vectors:
                    soapStr = StringIO()
                    # opening for XML
                    soapStr.write(self.genOpenWSSEXML())
                    if vector != 'un':
                        soapStr.write((self.xml["un_open"] + "%s" + self.xml["un_close"]) % (self.rndUser*8))
                    else:
                        if mutation == 'noclose':
                            # no close tag for userName
                            soapStr.write("<wsse:Username>" + self.rndUser)
                        if mutation == 'noopen':
                            # no open tag for userName
                            soapStr.write(self.rndUser + "</wsse:Username>")
                        if mutation == 'opentag':
                            soapStr.write("<")
                        if mutation == 'closetag':
                            soapStr.write("</")

                    created, nonce, digest = attackUtils.genLogisticVals(self.rndUser, self.rndPass)
                    if vector == 'pass':
                        if mutation == 'noclose':
                            # no close tag for password
                            soapStr.write(self.xml["wp_open"] + binascii.b2a_base64(digest).strip())
                        if mutation == 'noopen':
                            # no open tag for password
                            soapStr.write(binascii.b2a_base64(digest).strip() + self.xml["wp_close"])
                        if mutation == 'opentag':
                            soapStr.write("<")
                        if mutation == 'closetag':
                            soapStr.write("</")
                        soapStr.write(self.xml["wn_open"] + binascii.b2a_base64(nonce).strip() + self.xml["wn_close"])
                        soapStr.write(self.xml["wc_open"] + created.strip() + self.xml["wc_close"])
                    elif vector == 'nonce':
                        soapStr.write(self.xml["wp_open"] + binascii.b2a_base64(digest).strip() + self.xml["wp_close"])
                        if mutation == 'noclose':
                            # no close tag for nonce
                            soapStr.write(self.xml["wn_open"] + binascii.b2a_base64(nonce).strip())
                        if mutation == 'noopen':
                            # no open tag for nonce
                            soapStr.write(binascii.b2a_base64(nonce).strip() + self.xml["wn_close"])
                        if mutation == 'opentag':
                            soapStr.write("<")
                        if mutation == 'closetag':
                            soapStr.write("</")
                        soapStr.write(self.xml["wc_open"] + created.strip() + self.xml["wc_close"])
                    elif vector == 'created':
                        soapStr.write(self.xml["wp_open"] + binascii.b2a_base64(digest).strip() + self.xml["wp_close"])
                        soapStr.write(self.xml["wn_open"] + binascii.b2a_base64(nonce).strip() + self.xml["wn_close"])
                        if mutation == 'noclose':
                            # no close tag for created
                            soapStr.write(self.xml["wc_open"] + "%s" % created.strip())
                        if mutation == 'noopen':
                            # no open tag for nonce
                            soapStr.write(created.strip() + self.xml["wc_close"])
                        if mutation == 'opentag':
                            soapStr.write("<")
                        if mutation == 'closetag':
                            soapStr.write("</")
                    else:
                        soapStr.write(self.genLogisticTags(digest, nonce, created))

                    if vector != 'unt':
                        soapStr.write(self.genMidWSSEXML())
                    else:
                        # no close tag for userNameToken
                        soapStr.write(self.xml["sec_close"] + self.xml["header_close"] + self.xml["body_open"])

                    # method elements - open
                    if mix:
                        soapStr.write('<%s>' % self.rnd3)
                    else:
                        soapStr.write('<%s>' % method)

                    # parameter elements
                    if params:
                        for i in params:
                            if mix:
                                soapStr.write('<%s>%s</%s>' % (self.rnd3, self.rnd6, self.rnd3))
                            else:
                                soapStr.write('<%s>%s</%s>' % (i, self.rnd6, i))
                    else:
                        if mix:
                            soapStr.write('<%s>%s</%s>' % (self.rnd3, self.rnd6, self.rnd3))
                        else:
                            soapStr.write('<%s>%s</%s>' % (self.rnd, self.rnd6, self.rnd))

                    # method elements - close
                    if mix:
                        soapStr.write('</%s>' % self.rnd3)
                    else:
                        soapStr.write('</%s>' % method)

                    soapStr.write(self.genCloseWSSEXML())
                    self.addstring(soapStr)
    # EOF: generateWSSEMethodMutate

