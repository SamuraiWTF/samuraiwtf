"""
# Web Services Fuzzer
#
# FILENAME      : StopWatch.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 10/20/2005
# LAST UPDATE   : 8/26/2010
# ABSTRACT      : A class that implements a stopwatch to measure time delta's.
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

import time

class StopWatch:
    def __init__(self):
        self.rawElapsed = 00.00
        # instantiate at a state of None
        self.reset()

    # NAME     : reset
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Sets the baseline (of None) for 
    #            the measurements and related
    #            delta calculations.
    def reset(self):
        self._start = None
        self._stop = None
    # EOF: reset

    # NAME     : start
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Starts a stopwatch operation 
    #            by grabbing the current time
    #            when it is called.  Ensures
    #            that stop is not set yet.
    def start(self):
        self._stop = None
        self._start = time.time()
    # EOF: start

    # NAME     : elapsed
    # PARAMS   : None
    # RETURN   : float/int
    # DESC     : First it ensures that the 
    #            stopwatch operation at hand is 
    #            using valid start and stop val's.
    #            Then it calculates the delta 
    #            for the val's at hand and returns
    #            said delta.
    def elapsed(self):
        if self._start is None:
            return 0
        elif self._stop is None:
            end = time.time()
        else:
            end = self._stop
            
        final = end - self._start
        if final >= 1.0:
            self.rawElapsed = float(final)
            return "%.2f seconds" % (end - self._start)
        elif final < 1.0 and final > 0.0:
            self.rawElapsed = float((final*1000))
            return "%.5f milliseconds" % ((end - self._start)*1000)
        else:
            return 0
    # EOF: elapsed
    
    def getRawElapsed(self):
        return self.rawElapsed

    # NAME     : state
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Calculates and returns the  
    #            state of the stopwatch using
    #            it.
    def state(self):
        if self._stop is None and self._start is not None:
            return "RUNNING"
        else:
            return "STOPPED"
    # EOF: state

    # NAME     : stop
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : Stops a stopwatch operation 
    #            by setting stop to the 
    #            current time when it is called.
    def stop(self):
        self._stop = time.time()
    # EOF: stop
