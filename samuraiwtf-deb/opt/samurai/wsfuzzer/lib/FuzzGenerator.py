"""
# Web Services Fuzzer
#
# FILENAME      : FuzzGenerator.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 4/20/2006
# LAST UPDATE   : 8/28/2010
# ABSTRACT      : A library to dynamically generate fuzzing attack strings.
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

class FuzzGenerator:
	def __init__(self):
		self.digits = []
		self.strings = []
		self.injects = []

    # NAME     : addstring
    # PARAMS   : data, datatype
    # RETURN   : Nothing
    # DESC     : Populates array respective to the
    #			datatype submitted
	def addstring(self,data,datatype):
		if datatype == "string":
			self.strings.append([data,"Meta-Character Injection"])
		elif datatype == "inject":
			self.injects.append([data,"Meta-Character Injection"])
		elif datatype == "digit":
			self.digits.append([data,"Meta-Character Injection(Integer)"])
		else:
			print "??? - Unknown datatype"
	# EOF: addstring

    # NAME     : generateFuzzData
    # PARAMS   : string, endsize, increment, datatype, startsize
    # RETURN   : Nothing
    # DESC     : Generates fuzz data based on the parameters
    #			passed in.
	def generateFuzzData(self, string, endsize, increment, datatype="string", startsize = 0):
		if startsize:
			x = startsize
		else:
			x = increment
		while x <= endsize:
			y = string * x
			# treat these as white space
			y = y.replace("\x0a", "")
			self.addstring(y, datatype)
			x += increment
	# EOF: generateFuzzData

    # NAME     : generate
    # PARAMS   : none
    # RETURN   : Nothing
    # DESC     : Generates fuzz data by calling generateFuzzData with
    #			appropriate parameters.  It holds all attack strings
    #			that will be used as attack strings
	def generate(self):
		# strings
		self.generateFuzzData("A",1024,128)
		self.generateFuzzData("X",65536,1024)
		self.generateFuzzData("X\\00",1024,256)
		self.generateFuzzData("X|",1024,256)
		self.generateFuzzData("|X|",1024,256)
		self.generateFuzzData("%s",64,8)
		self.generateFuzzData("%n",65536,1024)
		self.generateFuzzData("\\x00A\\x00",256,64)
		self.generateFuzzData("/",1024,128)
		self.generateFuzzData("\\",1024,128)
		self.generateFuzzData(">",1024,128)
		self.generateFuzzData("<",1024,128)
		self.generateFuzzData("%",1024,128)
		self.generateFuzzData("+",1024,128)
		self.generateFuzzData("-",1024,128)
		self.generateFuzzData(",",1024,128)
		self.generateFuzzData(".",1024,128)
		self.generateFuzzData(":",1024,128)
		self.generateFuzzData("?",1024,128)
		self.generateFuzzData("%u000",128,32)
		self.generateFuzzData("\\r",512,32)
		self.generateFuzzData("\\n",512,32)
		self.generateFuzzData("A:",512,32)
		self.generateFuzzData("/\\",512,32)
		self.generateFuzzData("\\r\\n",512,16)
		self.generateFuzzData("~{",256,32)
		self.generateFuzzData("../A/",1024,128)
		self.generateFuzzData("%0a",1024,32)
		self.generateFuzzData("../",1024,32)
		self.generateFuzzData("/.../",1024,64)
		self.generateFuzzData(":/.",1024,32)
		# digits
		self.generateFuzzData("0",32,2,"digit")
		self.generateFuzzData("2",32,2,"digit")
		self.generateFuzzData("9",32,2,"digit")
		self.generateFuzzData("9",1024,128,"digit")
		self.generateFuzzData("99",1024,128,"digit")
	# EOF: generate

    # NAME     : getstrings
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of fuzz string data
	def getstrings(self):
		return self.strings
    # EOF: getstrings

    # NAME     : getinjects
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of fuzz inject data
	def getinjects(self):
		return self.injects
    # EOF: getinjects

    # NAME     : getidigits
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of fuzz digit data
	def getdigits(self):
		return self.digits
    # EOF: getdigits

    # NAME     : showstrings
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of fuzz string data
    #			printing each element
	def showstrings(self):
		for string in self.strings:
			print string
    # EOF: showstrings

    # NAME     : showinjects
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of fuzz inject data
    #			printing each element
	def showinjects(self):
		for inject in self.injects:
			print inject
    # EOF: showinjects

    # NAME     : showintegers
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : iterates over array of fuzz digit data
    #			printing each element
	def showintegers(self):
		for integer in self.digits:
			print integer
    # EOF: showintegers

    # NAME     : showall
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : wrapper function that calls all of
    #			the show functions
	def showall(self):
		self.showstrings()
		self.showintegers()
		self.showinjects()
    # EOF: showall

    # NAME     : getall
    # PARAMS   : None
    # RETURN   : Array
    # DESC     : wrapper function that calls all of
    #			the get functions
	def getall(self):
		all = []
		all.append(self.getstrings())
		all.append(self.getdigits())
		all.append(self.getinjects())

		return all
    # EOF: getall
