"""
# SOAP Attack
#
# FILENAME      : CSVWriter.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 11/8/2008
# LAST UPDATE   : 11/8/2008
# ABSTRACT      : A class to handle the logging of results to a CSV file
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

import csv

'''
   CSVWriter is a class that controls all logging
   functionality to CSV file output
'''
class CSVWriter(object):
    def __init__(self, path=None):
        object.__init__(self)
        self.docPath = path
        self.fileName = ""
        self.writer = None
        self.data = []

    # NAME     : setFileName
    # PARAMS   : name
    # RETURN   : Nothing
    # DESC     : sets file name for CSV output
    def setFileName(self, name):
        self.fileName = name
    # EOF: setFileName

	# NAME	 : setLogPath
	# PARAMS : name
	# RETURN : Nothing
	# DESC	 : sets path
    def setLogPath(self, name):
    	self.docPath = name
    	# once filename and path are set create the CSV writer obj
    	self.setWriter()
	# EOF: setLogPath
    
	# NAME	 : setWriter
	# PARAMS : None
	# RETURN : Nothing
	# DESC	 : creates CSV writer object
    def setWriter(self):
    	if self.writer is None:
            self.writer = csv.writer(open(self.docPath + "/" + self.fileName, "wb"))
            # set up the header line
            self.createHeaderLine()
    # EOF: setWriter
    
	# NAME	 : createHeaderLine
	# PARAMS : None
	# RETURN : Nothing
	# DESC	 : writes out the header row of data to the CSV file
    def createHeaderLine(self):
    	if self.writer:
            self.writer.writerow(('Type of Attack', 'Method', 'Request Parameters', 'Request', 'IDS Evasion',
                                 'Response Status Code', 'Raw Response', 'Response Payload',
                                 'Roundtrip Time', 'file:Directory/Filename'))
	# EOF: createHeaderLine

	# NAME	 : writeData
	# PARAMS : data
	# RETURN : Nothing
	# DESC	 : writes out a row of data to the CSV file
    def writeData(self, data):
    	if self.writer:
            self.writer.writerow(data)
    # EOF: writeData
    
	# NAME	 : writeInternalData
	# PARAMS : None
	# RETURN : Nothing
	# DESC	 : writes out a row of data to the CSV file
    def writeInternalData(self):
    	if self.writer:
            self.writer.writerow(tuple(self.data))
    # EOF: writeInternalData
    
    # NAME	 : setNewArr
	# PARAMS : None
	# RETURN : Nothing
	# DESC	 : flushes the data array
    def setNewArr(self):
    	self.data = []
    # EOF: setNewArr

	# NAME	 : pushIntoArr
	# PARAMS : Val
	# RETURN : Nothing
	# DESC	 : pushes data into the array
    def pushIntoArr(self, val):
    	self.data.append(val)
	# EOF: pushIntoArr


