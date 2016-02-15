"""
# Web Services Fuzzer
#
# FILENAME      : versionchecker.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 4/22/2006
# LAST UPDATE   : 8/27/2010
# ABSTRACT      : A small snippet of code that grabs the latest version number of the prog
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

import urllib2
import hashlib

pre = "http://sec.neurofuzz-software.com/appsec_toolkit/dict/b22c1b09dce4aa4cb51b7403e9f43dd2/"

# NAME     : simplecompare
# PARAMS   : a,b
# RETURN   : bool
# DESC     : does a simple compare of 2 strings
#            1 = equality
#            0 = no match
def simplecompare(a,b):
    if (a == b):
        return 1
    else: 
        return 0
# EOF: simplecompare

# NAME     : shasumfile
# PARAMS   : fobj
# RETURN   : string
# DESC     : returns a sha hash for a file 
#            object based on the read() method 
def shasumfile(fobj):
    s = hashlib.sha1()
    while True:
        d = fobj.read()
        if not d:
            break
        s.update(d)
    return s.hexdigest()
# EOF: shasumfile

# NAME     : writetempfiledata
# PARAMS   : fobj, f
# RETURN   : Nothing
# DESC     : Writes data from a resource on the 
#            Internet to a temp local file. 
def writetempfiledata(fobj, f):
    # read the data via HTTP
    # do not add strip() of line endings
    f.writelines(getremotedata(fobj))
# EOF: writetempfiledata

# NAME     : gethash
# PARAMS   : fobj
# RETURN   : string
# DESC     : Fetch's data from the Internet and 
#            writes it to a temp file locally. 
#            Uses the local copy to generate and  
#            return a SHA sum of the data in question.
def gethash(fobj):
    ff = 'fdeff8d89bf823813bc9d5455d322c44270799d6'
    f = open(ff, 'w')
    writetempfiledata(fobj, f)  
    f.close()
    
    f = open(ff, 'r')
    s = shasumfile(f)
    f.close()
    
    return s
# EOF: gethash

# NAME     : getremotedata
# PARAMS   : fobj
# RETURN   : data if correctly fetch'd
#            None otherwise
# DESC     : Fetch a resource from the Internet 
#            and return its contents based on 
#            the read() method 
def getremotedata(fobj):
    try:
        return urllib2.urlopen(pre + fobj).read()
    except:
        return None
# EOF: getremotedata
