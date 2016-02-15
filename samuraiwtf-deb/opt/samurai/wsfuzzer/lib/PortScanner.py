"""
# Web Services Fuzzer
#
# FILENAME      : PortScanner.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 05/23/2006
# LAST UPDATE   : 8/26/2010
# ABSTRACT      : A simple queue based multi-threaded TCP port scanner
#               : and wrapper class to interface with the scanner
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

import socket
import threading
import Queue

MAX_THREADS = 50

class PortScanner(threading.Thread):
    # NAME     : __init__
    # PARAMS   : inqueue, outqueue
    # RETURN   : Nothing
    # DESC     : overridden __init__ function
    #            from Python's Thread object
    def __init__(self, inqueue, outqueue):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        # queue holding (host, port) data to be scanned
        self.inqueue = inqueue
        # queue holding (host, port, status) result data from the scan
        self.outqueue = outqueue
    # EOF: __init__

    # NAME     : run
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : overridden run() function
    #            from Python's Thread object
    def run(self):
        while 1:
            # pop the queue for target data
            host, port = self.inqueue.get()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # try to connect to socket to the given host:port
                sock.connect((host, port))
            except socket.error:
                # set the CLOSED flag
                # socket could not be established
                # push closed result data to queue
                self.outqueue.put((host, port, 'CLOSED'))
            else:
                # push open result data to queue
                self.outqueue.put((host, port, 'OPEN'))
                # close established socket
                sock.close()
    # EOF: run

class WrapPortScanner:
    def __init__(self, host=None, start=None, stop=None):
        self.nThreads = MAX_THREADS
        self.finalports = []
        if host and start and stop:
            self.scan(host, start, stop)

    # NAME     : addport
    # PARAMS   : port
    # RETURN   : Nothing
    # DESC     : adds discovered port to final array
    def addport(self,port):
        self.finalports.append(port)
    # EOF: addport

    # NAME     : getports
    # PARAMS   : None
    # RETURN   : Array
    # DESC     : returns array containing all discovered
    #            open ports for a given target
    def getports(self):
        return self.finalports
    # EOF: getports

    # NAME     : scan
    # PARAMS   : host, start, stop
    # RETURN   : Nothing
    # DESC     : creates queues to manage data to
    #            be tested and related results.
    #            Also creates PortScanner objects and
    #            kicks off the threaded scanning functionality.
    #            Finally performs the necessary logic
    #            to populate final array with discovered
    #            active port data
    def scan(self, host, start, stop):
        toscan = Queue.Queue()
        scanned = Queue.Queue()
        hostports = []
        results = {}

        # create the 50 threads
        for i in range(self.nThreads):
            scanners = [PortScanner(toscan, scanned)]
        # start each thread
        for sc in scanners:
            sc.start()

        # setup array for all ports to test
        for port in xrange(start, stop+1):
            hostports.append((host, port))
        # push to queue all target host,port values
        for h in hostports:
            toscan.put(h)

        for host, port in hostports:
            # get results for each set of target
            # host and port key/value pair
            while (host, port) not in results:
                # pop the queue for results data
                shost, nport, sstatus = scanned.get()
                results[(shost, nport)] = sstatus

            status = results[(host, port)]
            if status != 'CLOSED':
                self.addport(port)
    # EOF: scan

