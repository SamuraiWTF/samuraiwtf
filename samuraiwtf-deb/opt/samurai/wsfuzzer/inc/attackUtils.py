"""
# Web Services Fuzzer
#
# FILENAME      : attackUtils.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 9/01/2006
# LAST UPDATE   : 8/26/2010
# ABSTRACT      : A library to create some standard utilities to be used by
#                 different classes.
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

import base64
import binascii
import hashlib
import random
from random import choice
import string
import time

# NAME     : genRandom
# PARAMS   : range
# RETURN   : Nothing
# DESC     : generate pseudo random attack data with
#            meta=char's randomly injected within
#            the random data
def genRandom(range, sleep = True, b64 = False):
    rnd = ''
    if sleep:
        time.sleep(1)
    random.seed() # use system time
    h = {'a':'','b':'','c':'','d':'','e':'','f':''}
    # set random values for insertion of some
    # potentially dangerous meta-char's
    for k in h:
        h[k] = random.choice(xrange(range))

    for i in xrange(range):
        rnd = rnd + random.choice(string.letters)
        if i == h['a']:
            rnd = rnd + "%00"
        if i == h['b']:
            rnd = rnd + "\00"
        if i == h['c']:
            rnd = rnd+ "0x00"
        if i == h['d']:
            rnd = rnd + "|"
        if i == h['e']:
            rnd = rnd + "'"
        if i == h['f']:
            rnd = rnd + "/00"

    if b64:
        newrnd = []
        # convert each char to its decimal value and then
        # cast that to a string and push onto array
        for r in rnd:
            newrnd.append(str(ord(r)))
        # convert the array into a string
        s = string.join(newrnd,'')
        # base64 encode the whole thing and return
        return binascii.b2a_base64(s).strip()
    else:
        # just return the rnd string
        return rnd
# EOF: genRandom

# NAME     : genRandomVal
# PARAMS   : type
# RETURN   : Depends on type
# DESC     : Generates random value based on the type
def genRandomVal(type):
    if type == 'string' or type == 0:
        chars = string.letters
        newstr = ''
        for i in range(genRandomVal('int')):
            newstr = newstr + choice(chars)
        return newstr
    elif type == 'integer' or type == 'int' or type == 1:
        return random.randint(0,100)
    elif type == 'float' or type == 'double' or type == 2:
        return random.uniform(1, 10)
    elif type == 'boolean' or type == 'bool' or type == 3:
        return bool(random.randint(0,1))
    elif type == 'base64' or type == 4:
        return base64.encodestring(genRandomVal('string'))
    elif type == 'Array' or type == 5:
        arr =[]
        # set random num of indices in the array
        for i in range(genRandomVal('int')):
            # let's have some fun and make the type of value
            # for each entry in the array random
            arr.append(genRandomVal(random.randint(0,4)))
        return arr
    else:
    	return hashlib.sha1(str('Ffo kcuf')).digest().strip()
# EOF: genRandomVal

# NAME     : genNAttribs
# PARAMS   : None
# RETURN   : string
# DESC     : Generates XML header and open XML tags
#            for the envelope, header, wsse sec,
#            and userNameToken
def genNAttribs(n):
    res = ''
    for i in range(n):
        res = res + ("a" + str(i) + '=\"1\" ')

    return res
# EOF: genNAttribs

# NAME     : genLogisticVals
# PARAMS   : rnd1, rnd2
# RETURN   : 3 strings
# DESC     : Makes a new subelement within an
#            XML doc.
def genLogisticVals(rnd1, rnd2):
    x = time.strftime('%Y-%m-%dT%H:%M:%SZ').strip()     # created
    y = hashlib.sha1(str(random.random())).digest().strip() # nonce
    z = hashlib.sha1(y + x + (rnd1 + rnd2)).digest().strip() # digest

    return x, y, z
# EOF: genLogisticVals

# NAME     : genMethodRandTags
# PARAMS   : None
# RETURN   : string
# DESC     : Generates closing XML tags for the body & envelope
def genMethodRandTags(method):
    return '<%s>%s</%s>' % (method, genRandom(600, b64=True), method)
# EOF: genMethodRandTags

# taken from http://hetland.org/python/distance.py
def leven(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
    return current[n]
# EOF: leven
