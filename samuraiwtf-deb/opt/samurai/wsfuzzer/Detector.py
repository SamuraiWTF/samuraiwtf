"""
# Web Services Fuzzer
#
# FILENAME      : Detector.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 02/21/2006
# LAST UPDATE   : 08/29/2010
# ABSTRACT      : An engine that performs intelligent detection of
#               : Web Service resources
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

import re
import string
import random
import hashlib
import urllib2

from lib import spider
from inc import attackUtils
from inc import genUtils

class WSDLDetector(object):
    def __init__(self):
        object.__init__(self)
        self.target = ''
        self.lev_setting=15
        self.depth = 5
        self.fpath = 'dict/'
        self.infile = self.fpath + 'dirs.txt'
        self.extfile = self.fpath + 'filetypes.txt'
        self.dummy = self.setdummy()
        self.dir_results = ['/']
        self.file_results = []
        self.tmp_final_targets = []
        self.final_targets = []
        self.responses = {}

    # NAME     : setdummy
    # PARAMS   : None
    # RETURN   : random SHA-1 hash
    # DESC     : Generates a SHA-1 hash based on random data.
    #            We dont want any IDS systems to be able to
    #            detect us based on some static pattern &->
    def setdummy(self):
        random.seed() # use system time
        rnd = random.choice(string.letters)
        return hashlib.sha1(rnd).hexdigest()
    # EOF: setdummy

    # NAME     : unique
    # PARAMS   : s
    # RETURN   : empty array if s is empty
    # DESC     : Takes in an array and pushes unique values
    #            out to the final target array of WSDL URL's
    def unique(self,s):
        n = len(s)
        if (n == 0):
            return []

        # enforce unique values by forcing case to '?wsdl'
        # this way ?WSDL and ?wsdl are not treated
        # as unique for the same target
        for x in s:
            x = x.replace('?WSDL','?wsdl')
            if (x not in self.final_targets):
                self.final_targets.append(x)
    # EOF: unique

    # NAME     : compare
    # PARAMS   : a,b
    # RETURN   : 1 upon a match on known negative
    #          : 0 upon a successful hit (positive)
    # DESC     : Compares 2 values utilizing a hash match
    #            or else levenshtein distance.  If either of those
    #            fails then there is a match on the resources
    def compare(self,a,b):
        # 'a' represents a known negative response
        if (hashlib.md5(str(a)).digest() == hashlib.md5(str(b)).digest()):
            return 1
        if (attackUtils.leven(a,b) < self.lev_setting):
            return 1
        else:
            return 0
    # EOF: compare

    # NAME     : fetch
    # PARAMS   : req
    # RETURN   : string
    # DESC     : Performs HTTP fetching.
    def fetch(self,req):
        if (req.startswith('http://')):
            request = urllib2.Request(req)
        else:
            request = urllib2.Request(self.target + req)

        opener = urllib2.build_opener()
        try:
            f = opener.open(request).read()
            # place all data from responses into a dictionary(hashtable)
            self.responses[self.target + req] = str(f)
            return str(f)
        except urllib2.HTTPError, e:
            return str(e)

        except urllib2.URLError, u:
            return 'FAILED'

        except httplib.InvalidURL:
            print 'Caught Some Invalid URL Error: ' + req
        # if this code gets here, beyond me ....
        return "?????????"
    # EOF: fetch

    # NAME     : dir_detect_basic
    # PARAMS   : host, depth
    # RETURN   : Nothing
    # DESC     : Does basic querying for directories based on data
    #            from a static dictionary.  The logic is based
    #            known bad data and anything else is treated as
    #            successful discovery.
    def dir_detect_basic(self,host,depth=5):
        self.target = host
        cnt = 0
        line_cnt = 0
        limit = 0
        s = re.compile(r'[Ee]rror 404', re.IGNORECASE)
        t = re.compile(r'300 [Mm]ultiple', re.IGNORECASE)
        if self.target.startswith('http') is False:
            self.target = 'http://' + self.target
        # get dictionary for dir data
        try:
            dirs = open(self.infile)
            directories = dirs.read().split()
        except IOError, e:
            print 'Error opening file'
            print str(e)
            sys.exit(0)

        # get a count of dir's to poke for
        for num in directories:
            line_cnt = line_cnt + 1
        # establish an exponential cap on the possibilities
        # some env support virtual dir's which can cause
        # nasty nested searches that can go on until a crash
        limit = line_cnt ** depth
        print "Checking %s maximum number of dir combo's based on a depth of %s\n" % (limit, depth)

        # detect existing directories
        for res in self.dir_results:
            if (cnt == limit):
                break

            # get a footprint for a request on a
            # non-existent resource
            # this is a known negative response
            f = self.fetch(res + self.dummy)
            # URL is invalid
            if f == 'FAILED':
                pass
            else:
                for dir in directories:
                    # get footprint of real resource of interest
                    q = self.fetch(res + dir)
                    cnt = cnt + 1
                    if (q == 'FAILED' or s.search(q) or t.search(q)):
                        pass
                    else:
                        # f - known negative response
                        # q - response for request on resource in question
                        if(self.compare(f,q) == 0):
                            # Found Directory: res + dir + '/' - populate dir_results array
                            self.dir_results.append(res + dir + '/')
    # EOF: dir_detect_basic

    # NAME     : dir_detect_adv
    # PARAMS   : host, depth
    # RETURN   : Nothing
    # DESC     : Does advanced querying for directories based on data
    #            from a static dictionary.  The logic is based on
    #            known bad data and anything else is treated as
    #            successful discovery.
    def dir_detect_adv(self,host,depth=5):
        self.target = host
        cnt = 0
        line_cnt = 0
        limit = 0
        s = re.compile(r'[Ee]rror 404', re.IGNORECASE)
        t = re.compile(r'300 [Mm]ultiple', re.IGNORECASE)
        if self.target.startswith('http') is False:
            self.target = 'http://' + self.target
        # get dictionary for dir data
        try:
            dirs = open(self.infile)
            directories = dirs.read().split()
        except IOError, e:
            genUtils.handleFileMsg(self.infile, msg=e, exit=True)

        # get a count of dir's to poke for
        for num in directories:
            line_cnt = line_cnt + 1
        # establish an exponential cap on the possibilities
        # some env support virtual dir's which can cause
        # nasty nested searches that can go on until a crash
        limit = line_cnt ** depth
        print "Checking %s maximum number of dir combo's based on a depth of %s\n" % (limit, depth)

        # detect existing directories
        for res in self.dir_results:
            if (cnt == limit):
                break

            # get a footprint for a request on a
            # non-existent resource
            # this is a known negative response
            f = self.fetch(res + self.dummy)
            # URL is invalid
            if f == 'FAILED':
                pass
            else:
                for dir in directories:
                    # get footprint of real resource of interest
                    q = self.fetch(res + dir)
                    cnt = cnt + 1
                    if (q == 'FAILED' or s.search(q) or t.search(q)):
                        pass
                    else:
                        # f - known negative response
                        # q - response for request on resource in question
                        if(self.compare(f,q) == 0):
                            # Found Directory: res + dir + '/' - populate dir_results array
                            path = res + dir + '/'
                            self.dir_results.append(path)
                            if (path != '/'):
                                self.dig(path,directories,depth)
    # EOF: dir_detect_adv

    # NAME     : res_detect
    # PARAMS   : host, dir_list
    # RETURN   : Nothing
    # DESC     : Does basic querying for resources based on data
    #            from a static dictionary.  The logic is based on
    #            known bad data and anything else is treated as
    #            successful discovery.
    def res_detect(self,host,dir_list):
        self.target = host
        s = re.compile(r'[Ee]rror 404', re.IGNORECASE)
        t = re.compile(r'300 [Mm]ultiple', re.IGNORECASE)
        if self.target.startswith('http') is False:
            self.target = 'http://' + self.target
        # get dictionaries for resource and file extension data
        try:
            dirs = open(self.infile)
            ft = open(self.extfile)
            files = dirs.read().split()
            filetypes = ft.read().split()
        except IOError, e:
            genUtils.handleFileMsg(self.infile, msg=e, exit=True)

        # based on discovered directories
        # discover file resources
        for res in dir_list:
            for type in filetypes:
                f = self.fetch(res + self.dummy + type)
                if f == 'FAILED':
                    pass
                else:
                    for file_name in files:
                        # get footprint of real resource of interest
                        q = self.fetch(res + file_name + type)
                        if (q == 'FAILED' or s.search(q) or t.search(q)):
                            pass
                        else:
                            # f - known negative response
                            # q - response for request on resource in question
                            if(self.compare(f,q) == 0):
                                # Found File: self.target + res + file_name + type
                                if (self.target + res + file_name + type not in self.file_results):
                                    self.file_results.append(self.target + res + file_name + type)
    # EOF: rers_detect

    # NAME     : xtract_wsdl_links
    # PARAMS   : resp
    # RETURN   : Nothing
    # DESC     : iterates over hash of HTML responses (resp)
    #            regex'ing for URL links that include either WSDL or DISCO
    #            query strings and pushes them into file_results array
    def xtract_wsdl_links(self,resp):
        #s = re.compile(".+<a.+=[\"\'](.+?(?:wsdl|disco))", re.IGNORECASE)
        s = re.compile(".+<.+=[\"\'](.+?(?:wsdl|disco))", re.IGNORECASE)
        t = re.compile("(.+/)", re.IGNORECASE)
        for kw in resp.keys():
            # get all regex results from each block of HTML
            m = s.findall(resp[kw])
            x = t.search(kw)
            if (m):
                for n in m:
                    # enforce unique values in the file_results array
                    if (n.startswith('http')):
                        if (n not in self.file_results):
                            self.file_results.append(n)
                    else:
                        if ((x.group(0) + n) not in self.file_results):
                            self.file_results.append(x.group(0) + n)
    # EOF: xtract_wsdl_links

    # NAME     : verify_wsdl
    # PARAMS   : res_list
    # RETURN   : Nothing
    # DESC     : Verfies that some returned data is valid WSDL.
    #            Does so by iterating over responses from all
    #            values in some array.
    def verify_wsdl(self,res_list):
        # assumption is that all WSDL contains the string
        # wsdl:definitions
        s = re.compile(r'wsdl:definitions', re.IGNORECASE)
        # res_list is an array of discovered target resources
        for res in res_list:
            # fetch live responses
            s1 = self.fetch(res)
            if s.search(s1):
                self.tmp_final_targets.append(res)
    # EOF: verify_wsdl

    # NAME     : xtract_wsdl_from_disco
    # PARAMS   : res_list
    # RETURN   : Nothing
    # DESC     : iterates over list of discovered resources.
    #            regex'ing for URL's with a query string of DISCO
    #            then gets the DISCO XML and regex searches through
    #            it for the URL links containing WSDL query string
    def xtract_wsdl_from_disco(self,res_list):
        s = re.compile('.+=[\"\'](.+?wsdl)', re.IGNORECASE)
        t = re.compile('(.+?disco)', re.IGNORECASE)

        for res in res_list:
            if t.search(res):
                # fetch live responses
                s1 = self.fetch(res)
                m = s.findall(s1)
                if (m):
                    for n in m:
                        # enforce unique values in the file_results array
                        if (n.startswith('http')):
                            #print "N: " + n
                            if (n not in self.file_results):
                                self.file_results.append(n)
    # EOF: xtract_wsdl_from_disco

    # NAME     : spider_target
    # PARAMS   : host
    # RETURN   : Nothing
    # DESC     : instantiates the spider object and
    #            then iterates over the results of the
    #            spidering action (weburls function)
    #            pushing the results into the array
    #            of discovered file resources
    def spider_target(self,host):
        # set spidering up here
        if (host.startswith('http://')):
            a = spider.Spider(host, 200, 16)
        else:
            a = spider.Spider('http://'+host, 200, 16)

        for i in a.weburls():
            self.file_results.append(i)
    # EOF: get_tmp_final

    # NAME     : dig
    # PARAMS   : path,directories,depth
    # RETURN   : array
    # DESC     : recursively digs a target looking for
    #            existing dir resources.  Pushes the
    #            results into the dir_results array
    def dig(self, path, directories, depth):
        if (depth == 0):
            pass
        s = re.compile(r'[Ee]rror 404', re.IGNORECASE)
        t = re.compile(r'300 [Mm]ultiple', re.IGNORECASE)

        # get a footprint for a request on a
        # non-existent resource
        # this is a known negative response
        f = self.fetch(path + self.dummy)
        # URL is invalid
        if f == 'FAILED':
            pass
        else:
            for dir in directories:
                # get footprint of real resource of interest
                q = self.fetch(path + dir)
                if (q == 'FAILED' or s.search(q) or t.search(q)):
                    pass
                else:
                    # f - known negative response
                    # q - response for request on resource in question
                    if(self.compare(f,q) == 0):
                        # Found Directory: res + dir + '/' - populate dir_results array
                        path = path + dir + '/'
                        self.dir_results.append(path)
                        # got a hit, make a recursive call
                        # to continue digging in
                        if (depth > 0):
                            self.dig(path,directories,depth-1)
    # EOF: dig

    # NAME     : get_dir_list
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of results for discovered
    #            directories
    def get_dir_list(self):
        return self.dir_results
    # EOF: get_dir_list

    # NAME     : get_file_list
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns array of results for discovered
    #            resources
    def get_file_list(self):
        return self.file_results
    # EOF: get_file_list

    # NAME     : get_responses
    # PARAMS   : None
    # RETURN   : dictionary
    # DESC     : returns dictionary of results for fetched
    #            HTML in responses
    def get_responses(self):
        return self.responses
    # EOF: get_responses

    # NAME     : get_tmp_final
    # PARAMS   : None
    # RETURN   : array
    # DESC     : returns temp array of results for discovered
    #            web service resources
    def get_tmp_final(self):
        return self.tmp_final_targets
    # EOF: get_tmp_final

    # NAME     : detect
    # PARAMS   : host,type,depth,spider
    # RETURN   : Nothing
    # DESC     : calls all relevant functions to perform
    #            the detection as per choices made by the user
    def detect(self,host,type,depth=5,spider=False):
        self.depth=depth
        if (type == 'basic'):
            self.dir_detect_basic(host,depth)
        elif (type == 'advanced'):
            self.dir_detect_adv(host,depth)
            if (spider):
                # set spidering up here
                self.spider_target(host)
        self.res_detect(host,self.get_dir_list())
        self.xtract_wsdl_links(self.get_responses())
        self.xtract_wsdl_from_disco(self.get_file_list())
        self.verify_wsdl(self.get_file_list())
        self.unique(self.get_tmp_final())
    # EOF: detect






