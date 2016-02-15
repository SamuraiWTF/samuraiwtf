"""
# Web Services Fuzzer
#
# FILENAME      : Logger.py
# AUTHORS       : Cosmin Banciu <ccbanciu [at] gmail dot com>
#               : David Shu <ydpanda [at] gmail dot com>
#               : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Andres Andreu, Cosmin Banciu
# DATE          : 12/07/2005
# LAST UPDATE   : 8/30/2010
# ABSTRACT      : A class to handle the logging of results.
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

import sys
import os
import cgi

import CSVWriter
from inc import xmlpp

'''
   Logger is a class that controls all logging
   functionality to the HTML output as well as
   the text based log files per transaction
'''
class Logger(object):
    def __init__(self, dirName=None, emptyDir=True):
        object.__init__(self)
        self.originalStdOut = sys.stdout
        self.httpDataDirectoryName = "HeaderData"
        self.httpDataDirectory = ""
        self.logPath = ""
        self.outPath = ""
        self.indexFilePath = ""
        self.indexFileHandle = None
        self.httpDataFilePath = ""
        self.httpDataFileName = ""
        self.httpDataFileHandle = None
        self.httpDataFileCounter = 0
        self.responseFileName = ""
        self.responseFileHandle = None
        self.emptyDir = emptyDir

        self.setLogPath(dirName)
        self.createLogPath()
        self.createIndexFile()

        self.csvw = CSVWriter.CSVWriter()
        self.csvw.setFileName('wsfuzzer-results.csv')
        self.csvw.setLogPath(self.outPath)

        self.codes = {}

    # NAME     : setLogPath
    # PARAMS   : dirname
    # RETURN   : Nothing
    # DESC     : Creates the string that represents
    #            the target dir for results
    def setLogPath(self, dirName):
        if (self.emptyDir is not False):
            if (dirName is not None):
                self.logPath = os.path.curdir + '/' + dirName
            else:
                self.logPath = os.path.curdir + "/FuzzingResults"
    # EOF: setLogPath

    # NAME     : createLogPath
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Creates the target dir for results
    def createLogPath(self):
        if (self.emptyDir is not False):
            for count in xrange(0, 1000):
                dirOutput = self.logPath + "-" + str(count)
                try:
                    os.mkdir(dirOutput)
                except:
                    continue
                self.outPath = dirOutput
                self.httpDataDirectory = dirOutput + "/" + self.httpDataDirectoryName
                os.mkdir(self.httpDataDirectory.replace('/',os.path.sep))
                return
    # EOF: createLogPath

    # NAME     : getLogPath
    # PARAMS   : None
    # RETURN   : str
    # DESC     : returns path name for log files
    def getLogPath(self):
        return self.outPath
    # EOF: getLogPath

    # NAME     : createIndexFile
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Creates the target index HTML file for results
    def createIndexFile(self):
        if (self.emptyDir is not False):
            self.indexFileName = self.outPath + "/" + "index.html"
    # EOF: createIndexFile

    # NAME     : begingLogging
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Kicks off the logging process.  First it opens
    #            the index HTML file and then it writes HTML header
    #            data in to it.
    def begingLogging(self, ids=False):
        self.indexFileHandle = open(self.indexFileName.replace('/',os.path.sep), mode="w")

        self.indexFileHandle.write("<HTML><HEAD><TITLE>WSFuzzer Results</TITLE>")
        self.indexFileHandle.write("<style type=\"text/css\"><!-- ")
        self.indexFileHandle.write("table { font-family : Monospace; font-size : small; } ")
        self.indexFileHandle.write(".row0 { background-color: #eee9e9; } ")
        self.indexFileHandle.write(".row1 { background-color: #fffafa; } ")
        self.indexFileHandle.write(" --></style></HEAD>")
        self.indexFileHandle.write("<BODY><center><H2>Fuzzing Results</H2>")
    # EOF: begingLogging

    # NAME     : logCodes
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Writes out to HTML some very simple
    #            stats base don the HTTP response code
    #            sent back by the target
    def logCodes(self):
        self.indexFileHandle.write("<center><H2>Some Basic Stats</H2><TABLE border=2 cellspacing=0 cellpadding=4>")
        self.indexFileHandle.write("<TR><TH align=\"center\">Status Code</TH><TH>Count</TH></TR>")

        items = self.codes.items()
        items.sort()

        for x in items:
            self.indexFileHandle.write("<TR><TD align=\"center\">%s</TD>" % x[0])
            self.indexFileHandle.write("<TD align=\"center\">%s</TD></TR>" % str(x[1]))

        self.indexFileHandle.write("</TABLE></center>")
    # EOF: logCodes

    # NAME     : endLogging
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Closes out the logging process.  First it writes
    #            closing tags to the index HTML file and then it
    #            closes the handle to the HTML file.
    def endLogging(self):

        self.logCodes()

        self.indexFileHandle.write("</BODY></HTML>")
        self.indexFileHandle.close()
        self.indexFileHandle = None
    # EOF: endLogging

    # NAME     : convertToBR
    # PARAMS   : str
    # RETURN   : string
    # DESC     : replaces some XML data so that it
    #            can be displayed as HTML
    def convertToBR(self, str):
        c = str
        c = c.replace("\" x","\"<br />x")
        c = c.replace("\" S","\"<br />S")
        c = c.replace("' x","'<br />x")
        c = c.replace("' S","'<br />S")
        c = c.replace("&quot; x","&quot;<br />x")
        c = c.replace("&quot; S","&quot;<br />S")
        c = c.replace("&gt;&lt;","&gt;<br />&lt;")

        return c
    # EOF: convertToBR

    # NAME     : logSoapInvoke
    # PARAMS   : method, params, idsEvasion
    # RETURN   : Nothing
    # DESC     : First it creates a txt file for the Response /
    #            Request data to be logged.  Then it writes
    #            results data to the HTML index file.  Lastly
    #            it sets the text file handle as the default
    #            STDOUT.
    def logSoapInvoke(self, method, params, request, attacktype=None, idsEvasion=None):
        self.httpDataFileName = str(self.httpDataFileCounter) + ".txt"
        self.httpDataFile = self.httpDataDirectory + "/" + self.httpDataFileName
        self.httpDataFileHandle = open(self.httpDataFile,mode="w")

        # HTML
        self.indexFileHandle.write("<TABLE width=\"90%\" border=2 cellspacing=0 cellpadding=4>")
        # type of attack
        self.indexFileHandle.write("<TR class=\"row0\"><TD width=\"25%\">Type of Attack</TD>")
        # use csvattacktype for a clean attacktype entry in the CSV file
        csvattacktype = ""
        if attacktype:
            self.indexFileHandle.write("<TD width=\"65%s\">%s</TD></TR>" % ("%",attacktype))
            csvattacktype = attacktype
        else:
            self.indexFileHandle.write("<TD width=\"65%s\">%s</TD></TR>" % ("%","Unknown Attack Type"))
            csvattacktype = "Unknown Attack Type"
        # method
        self.indexFileHandle.write("<TR class=\"row1\"><TD>Method</TD>")
        self.indexFileHandle.write("<TD>%s</TD></TR>" % method)
        # params
        self.indexFileHandle.write("<TR class=\"row0\"><TD>Request Params</TD>")
        if type(params) is str:
			self.indexFileHandle.write("<TD>%s</TD></TR>" % params)
        elif type(params) is dict:
			forprint = {}
			# loop on dict escaping HTML entities
			for k,v in params.iteritems():
				forprint[k] = cgi.escape(v, 1)
			self.indexFileHandle.write("<TD>%s</TD></TR>" % forprint)

        # request
        self.indexFileHandle.write("<TR class=\"row1\"><TD>Request Payload</TD>")
        c = cgi.escape(xmlpp.get_pprint(request).strip(), 1)
        c = self.convertToBR(c)
        self.indexFileHandle.write("<TD><pre>%s</pre></TD></TR>" % c)
        # IDS Evasion
        if idsEvasion is not None:
            self.indexFileHandle.write("<TR class=\"row0\"><TD>IDS Evasion</TD>")
            self.indexFileHandle.write("<TD>%s</TD></TR>" % idsEvasion)

        sys.stdout = self.httpDataFileHandle  #will record all print statements to the file

        # CSV logging
        # first flush the csvw array
        self.csvw.setNewArr()
        # order matters since its a CSV file
        self.csvw.pushIntoArr(csvattacktype)
        self.csvw.pushIntoArr(method)
        self.csvw.pushIntoArr(params)
        self.csvw.pushIntoArr(request.replace("\r","").replace("\n","").replace("\"\"","\""))
        self.csvw.pushIntoArr(idsEvasion)
    # EOF: logSoapInvoke

    # NAME     : logResponse
    # PARAMS   : response
    # RETURN   : Nothing
    # DESC     : First it closes HTML table TD tags.  Then it
    #            writes hyperlink data, pointing to the respective
    #            text file, into the HTML.  Then it closes
    #            the text file handle.  Lastly it resets the
    #            STDOUT to its original state.
    def logResponse(self, roundtrip=0, rawresponse=None, code=None, xmlpayload=None):
        self.responseFileName = "response_" + str(self.httpDataFileCounter) + ".txt"
        self.responseFile = self.httpDataDirectory + "/" + self.responseFileName

        if code:
            if self.codes.has_key(code):
                self.codes[code] += 1
            else:
                self.codes[code] = 1

        # status code
        self.indexFileHandle.write("<TR class=\"row0\"><TD>Status Code</TD>")
        self.indexFileHandle.write("<TD>%s</TD></TR>" % code)
        # response
        self.indexFileHandle.write("<TR class=\"row1\"><TD>XML Response Payload</TD>")
        if xmlpayload:
            c = cgi.escape(xmlpp.get_pprint(xmlpayload).strip(), 1)
            c = self.convertToBR(c)
            self.indexFileHandle.write("<TD><pre>%s</pre></TD></TR>" % c)

        self.indexFileHandle.write("<TR class=\"row0\"><TD>Response</TD>")
        # use csvrr for a clean raw response entry in the CSV file
        csvrr = ""
        if rawresponse:
            if rawresponse[1] == 1:
                for xx in rawresponse[0]:
                    self.indexFileHandle.write("<TD>%s</TD></TR>" % str(xx))
                    csvrr += str(xx)
            elif type(rawresponse) is str:
                self.indexFileHandle.write("<TD>%s</TD></TR>" % str(rawresponse))
                csvrr = str(rawresponse)
            else:
                self.indexFileHandle.write("<TD>%s</TD></TR>" % str(rawresponse[0]))
                csvrr = str(rawresponse[0])
        else:
            self.indexFileHandle.write("<TD>%s</TD></TR>" % "No response extracted")
            csvrr = "No response extracted"

        # round trip
        self.indexFileHandle.write("<TR class=\"row1\"><TD>Round Trip</TD>")
        self.indexFileHandle.write("<TD>%s</TD></TR>" % roundtrip)

        self.httpDataFileHandle.close()
        self.httpDataFileHandle = None

        self.indexFileHandle.write("</TABLE><br />")
        self.httpDataFileCounter = self.httpDataFileCounter + 1
        sys.stdout = self.originalStdOut #reset system printing

        # order matters since its a CSV file
        self.csvw.pushIntoArr(code)
        self.csvw.pushIntoArr(csvrr.replace("\r","").replace("\n",""))
        if xmlpayload:
        	self.csvw.pushIntoArr(xmlpayload.replace("\r","").replace("\n","").replace("\"\"","\""))
        else:
        	self.csvw.pushIntoArr("No XML payload received")
        self.csvw.pushIntoArr(roundtrip)
        self.csvw.pushIntoArr('file: ' + self.httpDataFile)
        # now force the row write into CSV file
        self.csvw.writeInternalData()
    # EOF: logResponse
