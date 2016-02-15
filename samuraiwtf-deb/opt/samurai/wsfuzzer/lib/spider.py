#! /usr/bin/env python

## Copyright (c) 1999 - 2003 L. C. Rees.  All rights reserved.
## See COPYRIGHT file for license terms.

from __future__ import generators

__name__ = 'spider'
__version__ = '0.5'
__author__ = 'L.C. Rees (xanimal@users.sf.net)'
__all__ = ['ftpurls', 'ftppaths', 'weburls', 'ftpmirror', 'ftpspider',
    'webpaths', 'webreport', 'webmirror', 'webspider', 'urlreport',
    'badurlreport', 'badhtmreport', 'redireport', 'outreport', 'othereport']

'''Multithreaded crawling, reporting, and mirroring for Web and FTP.'''

#from __future__ import generators


class Spider:

    '''HTTP and FTP crawling, reporting, and checking'''
    
    import os as _os
    import urllib as _ulib
    import urlparse as _uparse
    from os import path as _path 
    from ftplib import FTP as _ftp
    from time import strftime as _formtime
    from time import localtime as _localtime
    from ftplib import error_perm as _ftperr        
    from sgmllib import SGMLParseError as _sperror
    from robotparser import RobotFileParser as _rparser
    # Use threads if available 
    try: from threading import Thread as _thread
    except ImportError: pass
    _bdsig, _bfsig, _session, _newparser = None, None, None, None
    # HTML tags with URLs
    _urltags = {'a':1, 'img':1, 'link':1, 'script':1, 'iframe':1, 'object':1,
        'embed':1, 'area':1, 'frame':1, 'applet':1, 'input':1, 'base':1,
        'div':1, 'layer':1, 'ilayer':1, 'bgsound':1}
    # Supported protocols
    _supported = {'HTTP':1, 'http':1, 'HTTPS':1, 'https':1, 'FTP':1, 'ftp':1}
    # HTML attributes with URLs
    _urlattrs = {'href':1, 'src':1, 'data':1}

    def __init__(self, base=None, width=None, depth=None):
        '''Initializes a Spider instance and its base attributes

        Arguments:
        base -- URL to crawl (default: None)
        width -- maximum resources to crawl (default: None)
        depth -- how deep in a hierarchy to crawl (default: None)'''                             
        if base: self.base = base
        else: self.base = None
        if width: self.width = width
        else: self.width = None
        if depth: self.depth = depth
        else: self.depth = None
        
    def _ftpopen(self, base, name='anonymous', password=None, attempts=3):
        '''Returns FTP client session

        Arguments:
        base -- FTP server URL
        name -- login name (default: 'anonymous')
        password -- login password (default: None)
        attempts -- number of login attempts to try (default: 3)'''

        def ftpprompt(tries=0):        
            '''Prompts for FTP username and password

            Arguments:
            tries -- number of login attempts'''
            tries += tries
            try:
                self._name = raw_input('Enter login name: ')
                self._password = raw_input('Enter password: ')
                session = ftp(base, self._name, self._password)
                return session
            # If login attempt fails, retry login
            except ftperr:               
                if attempts >= tries:
                    session = ftpprompt(tries)
                    return session
                # Too many login attempts? End program
                elif attempts <= tries:
                    raise IOError, 'Permission denied.'
                    import sys
                    sys.exit(0)           

        # Assignments
        self._name, self._password, ftperr = name, password, self._ftperr
        su, ftp = self._uparse.urlsplit(base), self._ftp
        # Set URL, path, and strip 'ftp://' off
        base, path = su[1], '/'.join([su[2], ''])
        try: session = ftp(base, name, password)
        # Prompt for username, password if initial arguments are incorrect
        except ftperr: session = ftpprompt()
        # Change to remote path if it exits
        if path: session.cwd(path)
        return session

    def ftpmirror(self, l, t=None, b=None, w=200, d=6, n='anonymous', p=None):
        '''Mirrors an FTP site on a local filesystem

        Arguments:
        l -- local filesystem path (default: None)
        b -- FTP server URL (default: None)
        t -- number of download threads (default: None)
        w -- maximum amount of resources to crawl (default: 200)   
        d -- depth in hierarchy to crawl (default: 6)             
        n -- login username (default: 'anonymous')
        p -- login password (default: None)'''
        if b: self.ftpspider(b, w, d, n, p)
        return self._mirror((self.paths, self.urls), l, t)

    def ftppaths(self, b=None, w=200, d=6, n='anonymous', p=None):
        '''Returns a list of FTP paths.
        
        Arguments:
        b -- FTP server URL (default: None)
        w -- maximum amount of resources to crawl (default: 200) 
        d -- depth in hierarchy to crawl (default: 6)               
        n -- login username (default: 'anonymous')
        p -- login password (default: None)'''
        
        def sortftp(rdir):
            '''Returns a list of entries marked as files or directories

            Arguments:
            rdir -- remote directory list'''
            rlist = []
            rappend = rlist.append
            for rl in rdir:
                # Split remote file based on whitespace
                ri = rl.split()[-1]
                # Add tuple of remote item type, permissions & name to rlist
                if ri not in ('.', '..'): rappend((rl[0], rl[7], ri))
            return rlist
       
        def visitftp():
            '''Extracts contents of an FTP directory'''
            wd = pwd()
            if wd[-1] != '/': wd = '/'.join([wd, ''])
            # Add present working directory to visited directories
            dirs[wd], rlist = None, []
            # Get list of current directory's contents
            retr('LIST -a', rlist.append)
            for url in sortftp(rlist):
                # Test if remote item is a file (indicated by '-')
                if url[0] == '-':
                    # Resolve path of file
                    purl = ''.join([wd, url[2]])
                    # Ensure file list don't exceed max number of resources
                    if len(files) >= width: return None
                    # Add files to file dictionary
                    elif purl not in files: files[purl] = None
                # Test if it's a directory ('d') and allows scanning ('-')
                elif url[0] == 'd':
                    if url[1] != '-':
                        # Resolve path of directory
                        purl = ''.join([wd, url[2], '/'])
                        # Ensure no recursion beyond depth allowed
                        if len(purl.split('/')) >= depth: dirs[purl] = None
                        # Visit directory if it hasn't been visited yet 
                        elif purl not in dirs:
                            # Change to new directory
                            cwd(purl)
                            # Run 'visitftp' on new directory
                            visitftp()
                            
        # Use classwide attributes if set
        if b: self.base = b
        else: b = self.base
        # Use classwide width if different from method default
        if self.width and w == 200: width = self.width
        else: width = w
        # Use classwide depth if different from method default
        if self.depth and d == 6: depth = self.depth + 1
        else: depth = d + 1
        # File and directory dicts
        files, dirs = {}, {}
        # Use existing FTP client session if present
        if self._session: ftp = self._session
        # Create new FTP client session if necessary
        else:
            ftp = self._ftpopen(b, n, p)
            self._session = ftp
        # Avoid outside namespace lookups
        cwd, pwd, retr = ftp.cwd, ftp.pwd, ftp.retrlines
        # Walk FTP site
        visitftp()
        # Make path list out of files' keys and return it
        self.paths = files.keys()
        self.paths.sort()
        return self.paths

    def ftpspider(self, b=None, w=200, d=6, n='anonymous', p=None):
        '''Returns lists of URLs and paths plus a live FTP client session
        
        Arguments:
        b -- FTP server URL (default: None)
        w -- maximum amount of resources to crawl (default: 200) 
        d -- depth in hierarchy to crawl (default: 6)               
        n -- login username (default: 'anonymous')
        p -- login password (default: None)'''
        if b: ftppaths(b, w, d, n, p)
        return self.paths, ftpurls(), self._session

    def ftpurls(self, b=None, w=200, d=6, n='anonymous', p=None):
        '''Returns a list of FTP URLs
        
        Arguments:
        b -- FTP server URL (default: None)
        w -- maximum amount of resources to crawl (default: 200) 
        d -- depth in hierarchy to crawl (default: 6)               
        n -- login username (default: 'anonymous')
        p -- login password (default: None)'''
        if b:
            ftppaths(b, w, d, n, p)
            # Get rid of trailing '/' in base if present before joining
            if b[-1] == '/': base = b[:-1]       
        else:           
            base = self.base
            # Get rid of trailing '/' in base if present before joining
            if base[-1] == '/': base = self.base[:-1]
        paths = self.paths
        # Add FTP URL
        self.urls = [''.join([base, i]) for i in paths]
        return self.urls

    def _parserpick(self, old=None):
        '''Returns a class using the sgmllib parser or the sgmlop parser

        Arguments:
        old -- use classic sgmllib SGMLParser'''
        # Assignments
        urltags, urlattrs = self._urltags, self._urlattrs
        # Lists for bad file and bad directory signatures
        self._bfsig, self._bdsig = [], []
        bfsig, bdsig = self._bfsig, self._bdsig        
        # Use faster SGMLParser if available
        try:
            from sgmlop import SGMLParser as newparser
            self._newparser = newparser
        # If unavailable, use classic SGML parser
        except ImportError:
            from sgmllib import SGMLParser as oldparser
            old = 1
        # Classes using classic sgmllib SGML Parser
        if old:
            from sgmllib import SGMLParser as oldparser
            # Remove sgmlop parser if present
            self._newparser = None
            # UrlExtract class using classic parser
            class UrlExtract(oldparser):
                '''Extracts URLs from a SGMLish document'''
                def reset(self):
                    '''Resets SGML parser and clears lists'''
                    oldparser.reset(self)
                    self.urls, self.text, self.badurl = [], [], None
                def handle_data(self, data):
                    '''Handles non-markup data'''            
                    # Get first 5 lines of non-markup data
                    if len(self.text) <= 5: self.text.append(data)
                    # Compare signature of known bad URL to a new web page
                    if self.text == bfsig: self.badurl = 1
                    elif self.text == bdsig: self.badurl = 1
                def finish_starttag(self, tag, attrs):
                    '''Extracts URL bearing tags'''
                    if tag in urltags:
                        # Get key, vale in attributes if they match
                        url = [v for k, v in attrs if k in urlattrs]
                        if url: self.urls.extend(url)
            # BadUrl class using classic parser
            class BadUrl(oldparser):            
                '''Collects results of intentionally incorrect URLs'''
                def reset(self):
                    '''Resets SGML parser and clears lists'''
                    oldparser.reset(self)
                    self.text = []
                def handle_data(self, data):
                    '''Collects lines to profile bad URLs'''
                    # Adds first 5 lines of non-markup data to text
                    if len(self.text) <= 5: self.text.append(data)
        # If no old flag, use SGMLParser from sgmlop and related classes
        else:
            # UrlExtract class using sgmlop parser
            class UrlExtract:
                '''Extracts URLs from a SGMLish document'''            
                def __init__(self):
                    '''Resets SGML parser and clears lists'''
                    self.urls, self.text, self.badurl = [], [], None
                def handle_data(self, data):
                    '''Handles non-markup data'''            
                    # Get first 5 lines of non-markup data
                    if len(self.text) <= 5: self.text.append(data)
                    # Compare signature of known bad URL to a new web page
                    if self.text == bfsig: self.badurl = 1
                    elif self.text == bdsig: self.badurl = 1
                def finish_starttag(self, tag, attrs):
                    '''Extracts URL bearing tags'''
                    if tag in urltags:
                        # Get key, vale in attributes if they match
                        url = [v for k, v in attrs if k in urlattrs]
                        if url: self.urls.extend(url)
            # BadUrl class using sgmlop parser
            class BadUrl:            
                '''Collects results of intentionally incorrect URLs'''
                def __init__(self):
                    '''Resets SGML parser and clears lists'''
                    self.text = []            
                def handle_data(self, data):
                    '''Collects lines to profile not found responses'''
                    # Adds first 5 lines of non-markup data to list 'text'
                    if len(self.text) <= 5: self.text.append(data)
        # Make resulting classes available class wide
        self._UrlExtract, self._BadUrl = UrlExtract, BadUrl

    def _webtest(self):
        '''Generates signatures for identifying bad URLs'''

        def badurl(url):
            '''Returns first 5 lines of a bad URL

            Arguments:                
            url -- Bad URL to open and parse'''
            # Use different classes if faster SGML Parser is available
            if self._newparser:
                # sgmlop parser must have a handler passed to it
                parser, urlget = self._newparser(), BadUrl()
                # Pass handler (sgmlop cannot be subclassed)
                parser.register(urlget)
                parser.feed(urlopen(url).read())
                parser.close()
            # Use classic parser
            else:
                urlget = BadUrl()
                urlget.feed(urlopen(url).read())
                urlget.close()
            # Return singature of bad URL
            return urlget.text

        # Make globals local
        base, urljoin = self.base, self._uparse.urljoin
        urlopen, BadUrl = self._ulib.urlopen, self._BadUrl
        # Generate random string of jibber
        from string import letters, digits
        from random import choice, randint
        jibber = ''.join([letters, digits])
        ru = ''.join([choice(jibber) for x in range(randint(1, 30))])
        # Builds signature of a bad URL for a file
        self._bfsig.extend(badurl(urljoin(base, '%s.html' % ru)))
        # Builds signature of a bad URL for a directory
        self._bdsig.extend(badurl(urljoin(base,'%s/' % ru)))

    def _webparser(self, html):
        '''Parses HTML and returns bad URL indicator and extracted URLs

        Arguments:
        html -- HTML data'''
        # Use different classes if faster SGML Parser is available
        if self._newparser:
            # Make instances of SGML parser and URL extracting handler
            parser, urlget = self._newparser(), self._UrlExtract()
            # Pass handler to parser
            parser.register(urlget)
            # Feed data to parser
            parser.feed(html)
            parser.close()
            # Return bad URL indicator and extracted URLs
        else:
            urlget = self._UrlExtract()
            urlget.feed(html)
            urlget.close()
        # Return badurl marker and list of child URLS
        return urlget.badurl, urlget.urls

    def _webopen(self, base):
        '''Verifies URL and returns actual URL and extracted child URLs

        Arguments:
        base -- tuple containing a URL and its referring URL'''
        # Assignments
        good, cbase = self._good, base[0]        
        try:
            # If webspiders can access URL, open it            
            if self._robot.can_fetch('*', cbase):
                url = self._ulib.urlopen(cbase)
            # Otherwise, mark as visited and abort
            else:
                self._visited[cbase] = 1
                return False
        # If HTTP error, log bad URL and abort
        except IOError:
            self._visited[cbase] = 1
            self.badurls.append((base[1], cbase))
            return False
        # Get real URL
        newbase = url.geturl()
        # Change URL if different from old URL
        if newbase != cbase: cbase, base = newbase, (newbase, base[1])    
        # URLs with mimetype 'text/html" scanned for URLs
        if url.headers.type == 'text/html':
            # Feed parser
            contents = url.read()
            try: badurl, urls = self._webparser(contents)
            # Log URL if SGML parser can't parse it 
            except self._sperror:
                self._visited[cbase], self.badhtm[cbase] = 1, 1
                return False
            url.close()
            # Return URL and extracted urls if it's good
            if not badurl: return cbase, urls
            # If the URL is bad (after BadUrl), stop processing and log URL
            else:
                self._visited[cbase] = 1
                self.badurls.append((base[1], cbase))
                return False
        # Return URL of non-HTML resources and empty list
        else:
            url.close()
            return cbase, []

    def _genverify(self, urls, base):
        '''Verifies a list of full URL relative to a base URL

        Arguments:
        urls -- list of raw URLs
        base -- referring URL'''
        # Assignments
        cache, visit, urlverify = self._cache, self._visited, self._urlverify
        # Strip file off base URL for joining
        newbase = base.replace(base.split('/')[-1], '') 
        for url in urls:
            # Get resolved url and raw child URLs
            url, rawurls = urlverify(url, base, newbase)
            # Handle any child URLs
            if rawurls:
                newurls = {}
                # Eliminate duplicate URLs
                for rawurl in rawurls:
                    # Eliminate known visited URLs
                    if rawurl not in visit: newurls[rawurl] = 1
                # Put new URLs in cache if present
                if newurls: cache[url] = newurls
            # Yield new URL
            if url: yield url

    def _multiverify(self, url, base):
        '''Verifies a full URL relative to a base URL

        Arguments:
        url -- a raw URLs
        base -- referring URL'''
        # Assignments
        cache, visited = self._cache, self._visited
        # Strip file off base URL for joining
        newbase = base.replace(base.split('/')[-1], '')
        # Get resolved url and raw child URLs
        url, rawurls = self._urlverify(url, base, newbase)
        # Handle any child URLs
        if rawurls:
            # Eliminate known visited URLs and duplicates
            for rawurl in rawurls:
                # Put new URLs in cache if present
                if rawurl not in visited: cache[rawurl] = url
        # Put URL in list of good URLs
        if url: self._good[url] = 1

    def _urlverify(self, url, base, newbase):
        '''Returns a full URL relative to a base URL

        Arguments:
        urls -- list of raw URLs
        base -- referring URL
        newbase -- temporary version of referring URL for joining'''
        # Assignments
        visited, webopen, other = self._visited, self._webopen, self.other
        sb, depth, urljoin = self._sb[2], self.depth, self._uparse.urljoin
        urlsplit, urldefrag = self._uparse.urlsplit, self._uparse.urldefrag
        outside, redirs, supported = self.outside, self.redirs, self._supported
        if url not in visited:
            # Remove whitespace from URL
            if url.find(' ') != -1:
                visited[url], url = 1, url.replace(' ', '')
                if url in visited: return 0, 0
            # Remove fragments i.e. 'http:foo/bar#frag'
            if url.find('#') != -1:
                visited[url], url = 1, urldefrag(url)[0]
                if url in visited: return 0, 0
            # Process full URLs i.e. 'http://foo/bar
            if url.find(':') != -1:
                urlseg = urlsplit(url)
                # Block non-FTP, HTTP URLs
                if urlseg[0] not in supported:
                    # Log as non-FTP/HTTP URL
                    other[url], visited[url] = 1, 1
                    return 0, 0
                # If URL is not in root domain, block it
                if urlseg[1] not in sb:
                    visited[url], outside[url] = 1, 1                        
                    return 0, 0
                # Block duplicate root URLs
                elif not urlseg[2] and urlseg[1] == sb:
                    visited[url] = 1
                    return 0, 0
            # Handle relative URLs i.e. ../foo/bar
            elif url.find(':') == -1:
                # Join root domain and relative URL
                visited[url], url = 1, urljoin(newbase, url)
                if url in visited: return 0, 0
            # Test URL by attempting to open it
            rurl = webopen((url, base))
            if rurl and rurl[0] not in visited:
                # Get URL
                turl, rawurls = rurl
                visited[url], visited[turl] = 1, 1
                # If URL resolved to a different URL, process it
                if turl != url:
                    urlseg = urlsplit(turl)
                    # If URL is not in root domain, block it
                    if urlseg[1] not in sb:
                        # Log as a redirected internal URL
                        redirs[(url, turl)] = 1
                        return 0, 0
                    # Block duplicate root URLs
                    elif not urlseg[2] and urlseg[1] == sb: return 0, 0
                # If URL exceeds depth, don't process 
                if len(turl.split('/')) >= depth: return 0, 0
                # Otherwise return URL
                else:
                    if rawurls: return turl, rawurls
                    else: return turl, []
            else: return 0,0
        else: return 0, 0

    def _onewalk(self):
        '''Yields good URLs from under a base URL'''
        # Assignments
        cache, genverify = self._cache, self._genverify
        # End processing if cache is empty
        while cache:
            # Fetch item from cache
            base, urls = cache.popitem()
            # If item has child URLs, process them and yield good URLs
            if urls:
                for url in genverify(urls, base): yield url

    def _multiwalk(self, threads):
        '''Extracts good URLs from under a base URL
        
        Arguments:
        threads -- number of threads to run'''

        def urlthread(url, base):
            '''Spawns a thread containing a multiverify function

            Arguments:

            url -- URL to verify
            base -- referring URL'''
            # Create instance of Thread
            dthread = Thread(target=multiverify, args=(url, base))
            # Put in pool
            pool.append(dthread)

        # Assignments        
        pool, cache, multiverify = [], self._cache, self._multiverify
        Thread, width, good = self._thread, self.width, self._good
        # End processing if cache is empty
        while cache:
            # Process URLs as long as width not exceeded
            if len(good) <= width:
                # Fetch item from cache
                url, base = cache.popitem()
                # Make thread
                if url: urlthread(url, base)
                # Run threads once pool size is reached
                if len(pool) == threads or threads >= len(cache):
                    # Start threads
                    for thread in pool: thread.start()
                    # Empty thread pool as threads complete
                    while pool:
                        for thread in pool:
                            if not thread.isAlive(): pool.remove(thread)
            # End if width reached
            elif len(good) >= width: break

    def weburls(self, base=None, width=200, depth=5, thread=None):
        '''Returns a list of web paths.
        
        Arguments:
        base -- base web URL (default: None)
        width -- amount of resources to crawl (default: 200)
        depth -- depth in hierarchy to crawl (default: 5)
        thread -- number of threads to run (default: None)'''
        # Assignments
        self._visited, self._good, self._cache, self.badurls = {}, {}, {}, []
        self.redirs, self.outside, self.badhtm, self.other = {}, {}, {}, {}
        onewalk, good, self._robot = self._onewalk, self._good, self._rparser()
        uparse, robot, multiwalk = self._uparse, self._robot, self._multiwalk
        cache = self._cache
        # Assign width
        if self.width and width == 200: width = self.width
        else: self.width = width
        # sgmlop crashes Python after too many iterations
        if width > 5000: self._parserpick(1)
        else: self._parserpick() 
        # Use global base if present
        if not base: base = self.base
        # Verify URL and get child URLs
        newbase, rawurls = self._webopen((base, ''))
        if newbase:
            # Change base URL if different
            if newbase != base: base = newbase            
            # Ensure there's a trailing '/' in base URL
            if base[-1] != '/':
                url = list(uparse.urlsplit(base))
                url[1] = ''.join([url[1], '/'])
                base = uparse.urlunsplit(url)            
            # Eliminate duplicates and put raw URLs in cache
            newurls = {}
            for rawurl in rawurls: newurls[rawurl] = 1
            if newurls:
                # Cache URLs individually if threads are desired
                if thread:
                    for newurl in newurls: cache[newurl] = base
                # Cache in group if no threads
                else: cache[base] = newurls
            # Make base URL, get split, and put in verified URL list
            self.base, self._sb = base, base.split('/')
            self._visited[base], good[base] = 1, 1
        # If URL is bad, abort and raise error
        else: raise IOError, "URL is invalid"
        # Adjust dept to length of base URL
        if self.depth and depth == 6: self.depth += len(self._sb)
        else: self.depth = depth + len(self._sb)
        # Get robot limits
        robot.set_url(''.join([base, 'robots.txt']))
        robot.read()
        # Get signature of bad URL
        self._webtest()
        # Get good URLs as long as total width isn't exceeded
        try:
            # Multiwalk if threaded
            if thread: self._multiwalk(thread)
            # Otherwise, use single thread
            else:
                for item in onewalk():
                    # Don't exceed maximum width
                    if len(good) <= width: good[item] = 1
                    elif len(good) >= width: break
        # If user interrupts crawl, return what's done
        except KeyboardInterrupt: pass
        # Get URLs, sort them, and return list
        self.urls = good.keys()
        self.urls.sort()
        return self.urls                        

    def webpaths(self, b=None, w=200, d=5, t=None):
        '''Returns a list of web paths.
        
        Arguments:
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''

        def pathize():            
            '''Strips base URL from full URLs to produce paths'''            
            for url in urls:
                # Remove base URL from path list
                url = url.replace(self.base, '')
                # Add default name 'index.html' to root URLs and directories
                if not url: url = 'index.html'
                elif url[-1] == '/': url = ''.join([url, 'index.html'])
                # Verify removal of base URL and remove it if found
                if url.find(':') != -1: url = urlsplit(url)[2:][0]                
                yield url

        # Assignments
        urlsplit = self._uparse.urlsplit
        # Run weburls if base passed as an argument
        if b: self.weburls(b, w, d, t)
        # Strip off trailing resource or query from base URL
        if self.base[-1] != '/': self.base = '/'.join(self._sb[:-1])
        urls = self.urls
        # Return path list after stripping base URL
        self.paths = list(pathize())
        return self.paths
        
    def webmirror(self, root=None, t=None, base=None, width=200, depth=5):
        '''Mirrors a website on a local filesystem

        Arguments:
        root -- local filesystem path (default: None)
        t -- number of threads (default: None)
        base -- base web URL (default: None)
        width -- amount of resources to crawl (default: 200)
        depth -- depth in hierarchy to crawl (default: 5)'''
        if base: self.webspider(base, width, depth, t)
        return self._mirror((self.paths, self.urls), root, t)
    
    def webspider(self, b=None, w=200, d=5, t=None):
        '''Returns two lists of child URLs and paths
        
        Arguments:
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        return self.webpaths(), self.urls

    def badurlreport(self, f=None, b=None, w=200, d=5, t=None):
        '''Pretties up a list of bad URLs
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        # Format report if information is available
        if self.badurls:
            # Number of bad URLs
            amount = str(len(self.badurls))
            header = '%s broken URLs under %s on %s:\n'
            # Print referring URL pointing to bad URL
            body = '\n'.join([' -> '.join([i[0], i[1]]) for i in self.badurls])
            report = self._formatreport(amount, header, body, f)
            # Return if just getting string
            if report: return report

    def badhtmreport(self, f=None, b=None, w=200, d=5, t=None):
        '''Pretties up a list of unparsed HTML URLs
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        # Format report if information is available
        if self.badhtm:
            amount = str(len(self.badhtm))
            header = '%s unparsable HTML URLs under %s on %s:\n'
            body = '\n'.join(self.badhtm)
            report = self._formatreport(amount, header, body, f)
            # Return if just getting string
            if report: return report

    def redireport(self, f=None, b=None, w=200, d=5, t=None):
        '''Pretties up a list of URLs redirected to an external URL
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        # Format report if information is available
        if self.redirs:
            amount = str(len(self.redirs))
            header = '%s redirects to external URLs under %s on %s:\n'
            # Print referring URL pointing to new URL
            body = '\n'.join([' -> '.join([i[0], i[1]]) for i in self.redirs])
            report = self._formatreport(amount, header, body, f)
            # Return if just getting string
            if report: return report

    def outreport(self, f=None, b=None, w=200, d=5, t=None):
        '''Pretties up a list of outside URLs referenced under the base URL
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        # Format report if information is available
        if self.outside:
            amount = str(len(self.outside))
            header = '%s links to external URLs under %s on %s:\n'
            body = '\n'.join(self.outside)
            report = self._formatreport(amount, header, body, f)
            # Return if just getting string
            if report: return report            

    def othereport(self, f=None, b=None, w=200, d=5, t=None):
        '''Pretties up a list of non-HTTP/FTP URLs
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        # Format report if information is available
        if self.other:
            amount = str(len(self.other))
            header = '%s non-FTP/non-HTTP URLs under %s on %s:\n'
            body = '\n'.join(self.other)
            report = self._formatreport(amount, header, body, f)
            # Return if just getting string
            if report: return report

    def urlreport(self, f=None, b=None, w=200, d=5, t=None):
        '''Pretties up a list of all URLs under a URL
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)'''
        if b: self.weburls(b, w, d, t)
        # Format report if information is available
        if self.urls:
            amount = str(len(self.urls))
            header = '%s verified URLs under %s on %s:\n'
            body = '\n'.join(self.urls)
            report = self._formatreport(amount, header, body, f)
            # Return if just getting string
            if report: return report

    def webreport(self, f=None, b=None, w=200, d=5, t=None, *vargs):
        '''Pretties up a list of logged information under a URL
        
        Arguments:
        f -- output file for report (default: None)
        b -- base web URL (default: None)
        w -- amount of resources to crawl (default: 200)
        d -- depth in hierarchy to crawl (default: 5)
        t -- number of threads (default: None)
        vargs -- report sections to include or exclude
        To override defaults:
        To include a section add 'badhtm', 'redirs', 'outside', or 'other'
        To exclude a section add 'badurls' or "urls"'''
        if b: self.weburls(b, w, d, t)
        # Defaults for report
        badurls, badhtm, redirs, urls, outside, other = 1, 0, 0, 1, 0, 0
        # Create compilation list
        compile = []
        # Override default report settings if argument is passed to vargs
        for arg in vargs:
            if arg == 'badurls': badurls = 0
            elif arg == 'badhtm': badhtm = 1
            elif arg == 'redirs': redirs = 1
            elif arg == 'urls': urls = 0
            elif arg == 'outside': outside = 1
            elif arg == 'other': other = 1
        # Compile report
        if badurls:
            badurls = self.badurlreport()
            if badurls: compile.append(badurls)
        if urls:
            urls = self.urlreport()
            if urls: compile.append(urls)
        if outside:
            outside = self.outreport()
            if outside: compile.append(outside)
        if redirs:
            redirs = self.redireport()
            if redirs: compile.append(redirs)
        if badhtm:
            badhtm = self.badhtmreport()
            if badhtm: compile.append(badhtm)        
        if other:
            other = self.othereport()
            if other: compile.append(other)
        # Make report
        report = '\n\n'.join(compile)
        # Write to file if argument present
        if file: open(f, 'w').write(report)
        # Or return string
        else: return report
        
    def _formatreport(self, amount, header, body, file=None):
        '''Generic prettifier with date/time stamper
        
        Arguments:
        header -- title of report
        body -- body of report
        file -- output file for report (default: None)'''
        # Get current time
        localtime, strftime = self._localtime, self._formtime        
        curtime = strftime('%A, %B %d, %Y at %I:%M %p', localtime())
        # Make section header
        header = header % (amount, self.base, curtime)
        # Add header to body
        report = '\n'.join([header, body])
        # Write to file if argument present
        if file: open(file, 'w').write(report)
        # Or return string
        else: return report

    def _mirror(self, lists, root=None, threads=None):
        '''Mirrors a site on a local filesystem based on lists passed to it

        Argument:
        lists -- lists of URLs and paths
        root -- local filesystem path (default: None)
        threads -- number of threads (default: None)'''

        def download(url, np, op):
            '''Downloads files that need to be mirrored.'''
            # If ftp...
            if url[:3] == 'ftp':
                # Open local file
                local = open(np, 'wb')
                # Download using FTP session
                ftp = ftpopen(base, name, password)
                ftp.retrbinary('RETR %s' % op, local.write)
                ftp.close()
                # Close local file
                local.close()
            # Use normal urlretrieve if no FTP required
            else: ulib.urlretrieve(url, np)
            
        def dlthread(url, np, op):
            '''Spawns a thread containing the download function'''
            # Create thread
            dthread = Thread(target=download, args=(url, np, op))
            # Add to thread pool
            pool.append(dthread)
                
        # Extract path and URL lists
        paths, urls = lists
        # Avoid outside namespace lookups
        ulib, makedirs, sep = self._ulib, self._os.makedirs, self._os.sep
        normcase, split = self._path.normcase, self._path.split
        exists, isdir = self._path.exists, self._path.isdir
        ftpopen = self._ftpopen
        # Create local names for thread class and thread pool
        if threads: Thread, pool = self._thread, []
        # Localize name and password if exists
        try: base, name, password = self.base, self._name, self._password
        except AttributeError: pass
        # Change to directory if given...
        if root:
            if exists(root):
                if isdir(root): self._os.chdir(root)
            # Create root if it doesn't exist
            else:
                makedirs(root)
                self._os.chdir(root)
        # Otherwise use current directory
        else: root = self._os.getcwd()
        # Iterate over paths and download files
        for oldpath in paths:
            # Sync with the URL for oldpath
            url = urls[paths.index(oldpath)]
            # Create name of local copy
            newpath = normcase(oldpath).lstrip(sep)            
            # Get directory name
            dirname = split(newpath)[0]
            # If the directory exists, download the file directly        
            if exists(dirname):
                if isdir(dirname):
                    if threads: dlthread(url, newpath, oldpath)
                    else: download(url, newpath, oldpath)
            # Don't create local directory if path in root of remote URL
            elif not dirname:
                if threads: dlthread(url, newpath, oldpath)
                else: download(url, newpath, oldpath)
            # Make local directory if it doesn't exist, then dowload file
            else:
                makedirs(dirname)
                if threads: dlthread(url, newpath, oldpath)
                else: download(url, newpath, oldpath)
            # Run threads if they've hit the max number of threads allowed
            if threads:
                # Run if max threads or final thread reached
                if len(pool) == threads or paths[-1] == oldpath:
                    # Start all threads
                    for thread in pool: thread.start()
                    # Clear the thread pool as they finish
                    while pool:
                        for thread in pool:
                            if not thread.isAlive(): pool.remove(thread)


# Instance of Spider enables exporting Spider's methods as standalone functions
_inst = Spider()
ftpurls = _inst.ftpurls
weburls = _inst.weburls
ftppaths = _inst.ftppaths
webpaths = _inst.webpaths
ftpmirror = _inst.ftpmirror
ftpspider = _inst.ftpspider
webmirror = _inst.webmirror
webspider = _inst.webspider
webreport = _inst.webreport
urlreport = _inst.urlreport
outreport = _inst.outreport
redireport = _inst.redireport
othereport = _inst.othereport
badurlreport = _inst.badurlreport
badhtmreport = _inst.badhtmreport
