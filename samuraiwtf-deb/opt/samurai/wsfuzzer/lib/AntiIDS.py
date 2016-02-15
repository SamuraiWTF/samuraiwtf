"""
# Web Services Fuzzer
#
# FILENAME      : AntiIDS.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 12/7/2005
# LAST UPDATE   : 8/25/2010
# ABSTRACT      : A library to effect IDS evasion within attacks against web services.
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

from random import choice
from random import uniform
import re
import string

class AntiIDS(object):
    def __init__(self, wrapper=None):
        object.__init__(self)
        if wrapper:
            self.wrapper = wrapper
        self.idsWin = False
        self.s = re.compile(r"/|;|=|:|&|@|\\|\?")    

    # NAME     : encode_uri_hex
    # PARAMS   : str
    # RETURN   : encoded string
    # DESC     : Encode a URI in hex
    #            i.e. 'A' => %41
    def encode_uri_hex(self, str=""):
        strt = ""
        con = "%%%02x"

        for c in str:
            if self.s.search(c):
                strt += c
                continue
            strt += con % ord(c)
            
        return strt
    # EOF: encode_uri_hex
        
    # NAME     : encode_uri_randomhex
    # PARAMS   : str
    # RETURN   : encoded string
    # DESC     : Encode a URI randomly in hex 
    #            while avoiding some characters
    def encode_uri_randomhex(self, str=""):
        strt = ""
        con = "%%%02x"

        for c in str:
            if self.s.search(c):
                strt += c
                continue
            i = int(uniform(0, 10))
            i = i % 2
            if i == 1:
                strt += con % ord(c)
            else:
                strt += c
                  
        return strt
    # EOF: encode_uri_randomhex
            
    # NAME     : utils_randstr
    # PARAMS   : drift, chars
    # RETURN   : string
    # DESC     : Returns random string of length drift.        
    def utils_randstr(self, drift=10, chars=None):
        str = ""
    
        if chars == None:
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        while drift > 0:
            ch = choice(chars)
            str += ch
            drift = drift - 1

        return str 
    # EOF: def utils_randstr
    
    # NAME     : encode_uri_double_percent_hex
    # PARAMS   : str
    # RETURN   : encoded string
    # DESC     : Encode a URI with Double Percent Hex Encoding 
    #            i.e. 'A' => %2541
    def encode_uri_double_percent_hex(self, str=""):
        strt = ""
        con = "%%%02x"
        
        # first get it in straight hex
        strt = self.encode_uri_hex(str)        
        strt = strt.replace("%", con % ord("%"))

        return strt
    # EOF: encode_uri_double_percent_hex
    
    # NAME     : encode_uri_double_nibble_hex
    # PARAMS   : str
    # RETURN   : encoded string
    # DESC     : Encode a URI with Double Nibble Hex Encoding
    #            i.e. 'A' => %%34%31
    def encode_uri_double_nibble_hex(self, str=""):
        strt = ""
        fin = ""
        con = "%%%02x"

        # first get it in straight hex
        strt = self.encode_uri_hex(str)
            
        for c in strt:
            if not c == "%":
                if self.s.search(c):
                    fin += c
                    continue
                fin += con % ord(c)
            else:
                fin += c
                
        return fin
    # EOF: encode_uri_double_nibble_hex
    
    # NAME     : encode_uri_first_nibble_hex
    # PARAMS   : str
    # RETURN   : encoded string
    # DESC     : Encode a URI with First Nibble Hex Encoding
    #            i.e. 'A' => %%341
    def encode_uri_first_nibble_hex(self, str=""):
        strt = ""
        fin = ""
        con = "%%%02x"
        
        # first get it in straight hex
        strt = self.encode_uri_hex(str)
        
        count = 0
        for c in strt:
            if not c == "%":
                if self.s.search(c):
                    fin += c
                    continue
                if count == 1:
                    fin += con % ord(c)
                if count == 2:
                    fin += c
            else:
                fin += c
            count += 1
            # reset counter to 0 so as to handle the
            # hex pattern of %XX
            if count == 3:
                count = 0
                
        return fin
    # EOF: encode_uri_first_nibble_hex
    
    # NAME     : encode_uri_second_nibble_hex
    # PARAMS   : str
    # RETURN   : encoded string
    # DESC     : Encode a URI with Second Nibble Hex Encoding
    #            i.e. 'A' => %4%31   
    def encode_uri_second_nibble_hex(self, str=""):
        strt = ""
        fin = ""
        con = "%%%02x"
        
        # first get it in straight hex
        strt = self.encode_uri_hex(str)
        
        count = 0
        for c in strt:
            if not c == "%":
                if self.s.search(c):
                    fin += c
                    continue
                if count == 1:
                    fin += c
                if count == 2:
                    fin += con % ord(c)
            else:
                fin += c
            count += 1
            # reset counter to 0 so as to handle the 
            # hex pattern of %XX
            if count == 3:
                count = 0
                
        return fin
    # EOF: encode_uri_second_nibble_hex
            
    # NAME     : encode_anti_ids
    # PARAMS   : mode, method
    # RETURN   : string
    # DESC     : Returns crafted string of the URI
    #            based on the mode.          
    def encode_anti_ids(self, mode, method, inuri=None):
        modes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '10',
            '11', '12', '13', '14', 'R']
    	# do some whitelisting based on known good input
    	# otherwise return None
    	if mode in modes:
	        # dynamically get the target URI from the 
	        # wrapper (WSDL) class
            if inuri == None:
	            uri = self.wrapper.getService(method)
            else:
	            uri = inuri
	        
            if mode.isalpha():
	            if 'R' in mode:
	                if self.idsWin:
	                    # stick to Win specific data here, anything else
	                    # causes soap faults
	                    mode = choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14])
	                else:
	                    mode = choice([1, 2, 3, 4, 5, 6, 10])
	            
	        # convert string to int
            mode = int(mode)
	        
	        # mode 9 - session splicing
	        # ToDo
	        
	        # mode 4 - prepend long random string
            if mode == 4:
	            s = ''
	            if re.match('^/', uri):
	                while(len(s) < 512):
	                    x = self.utils_randstr()
	                    s += x                
	            return "/" + s + "/.." + uri
	            
	        # mode 7  - random case sensitivity - Windows targets only
            if mode == 7:
	            strt = ""
	            t = string.split(uri, '/')
	            i = len(t)
	            z = 0
	            for str in t:
	                for c in str:
	                    x = int(uniform(0, 10))
	                    x = x % 2
	                    if x == 1:
	                        strt += c.upper()
	                    else:
	                        strt += c
	                if z < i-1:
	                    strt += "/"
	                    z = z + 1
	            return strt        
	        
	        # mode 2 - directory self-reference (/./)
            if mode == 2:
	            str = uri
	            p = re.compile('/')
	            str = p.sub('/./', str)
	            return str
	        
	        # mode 8 - directory separator (\) - Windows targets only
            if mode == 8:
	            str = uri
	            p = re.compile('/')
	            str = p.sub('\\\\', str)
	            p = re.compile('^\\\\')
	            str = p.sub('/', str)
	            return str
	            
	        # mode 1 - random URI (non-UTF8) encoding
            if mode == 1:
	            return self.encode_uri_randomhex(uri)
	                      
	        # mode 5 - fake parameter
            if mode == 5:
	            s = self.utils_randstr()
	            y = self.utils_randstr()
	            return "/" + s + ".html%3f" + y + "=/../" + uri
	        
	        # mode 3 - premature URL ending
            if mode == 3:
	            s = self.utils_randstr()
	            return "/%20HTTP/1.1%0D%0A%0D%0AAccept%3A%20" + s + "/../.." + uri
	        
	        # mode 6 - TAB as request spacer
            if mode == 6:
	            return "\t" + uri
	        
	        # mode 0 - Null method processing - Windows targets only
            if mode == 0:
	            return "%00%20" + uri
	        
	        # mode 10 - URI (non-UTF8) encoding
            if mode == 10:
	            return self.encode_uri_hex(uri)
	        
	        # mode 11 - Double Percent Hex Encoding - Windows targets only
            if mode == 11:
	            return self.encode_uri_double_percent_hex(uri)
	        
	        # mode 12 - Double Nibble Hex Encoding - Windows targets only
            if mode == 12:
	            return self.encode_uri_double_nibble_hex(uri)
	        
	        # mode 13 - First Nibble Hex Encoding - Windows targets only
            if mode == 13:
	            return self.encode_uri_first_nibble_hex(uri)
	        
	        # mode 14 - Second Nibble Hex Encoding - Windows targets only
            if mode == 14:
	            return self.encode_uri_second_nibble_hex(uri)
    	else:
			return None
    # EOF: encode_anti_ids
