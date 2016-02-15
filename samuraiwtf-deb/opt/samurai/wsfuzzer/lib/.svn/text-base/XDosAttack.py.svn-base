"""
# SOAP Attack
#
# FILENAME      : ThreadMaster.py
# AUTHORS       : Cosmin Banciu <ccbanciu [at] gmail dot com>
# DATE          : 9/2/2008
# LAST UPDATE   : 8/31/2010
# ABSTRACT      : Fill me In
#
#
# Copyright (c) 2008 - 2010 neuroFuzz, LLC
#
"""

import threading
import time

import XMLPost

class ThreadMaster(object):
    def __init__(self, numOfThreads = None, totalRunTime = None, numOfTimeoutsThreshold = None, xdos = None):
        object.__init__(self)
        self.runTime = totalRunTime  #total number of minutes to fuzz the target
        self.totalThreads = numOfThreads
        self.numOfTimeoutsThreshold = numOfTimeoutsThreshold # total number of timeouts from remote server before target is declared "dead"
        self.xdos = xdos
        self.numOfTimeouts = 0
        self.timerThread = None
        self.startTime = None
        self.endTime = None

        #create Thread objects
        self.threads = []
        self.threadsOperationTimeoutOccured = []
        for counter in range(0,self.totalThreads):
            self.threads.append(ThreadWorker(self,counter,self.xdos))
            self.threadsOperationTimeoutOccured.append(False)
        if(self.runTime is not None):
            self.timerThread = ThreadTime(self,self.runTime)


    def setXDos(self, xdos = None):
        self.xdos = xdos

    def start(self):
        for thread in self.threads:
            thread.start()
        if(self.runTime is not None):
            self.timerThread.start()
        self.startTime = time.time()

    def join(self):
        for thread in self.threads:
            thread.join()
        if(self.runTime is not None):
            self.timerThread.join()
        self.endTime = time.time()

    def stopThreads(self):
        print "Stopping threads"
        for thread in self.threads:
            thread.setContinueStatus(False)
        if(self.runTime is not None):
            self.timerThread.setContinueStatus(False)

    def resetOperationTimeout(self,threadNumber):
        self.threadsOperationTimeoutOccured[threadNumber] = False

    def timeoutOccured(self,threadNumber = None):
        self.numOfTimeouts += 1
        self.threadsOperationTimeoutOccured[threadNumber] = True
        allThreadsTimedout = True
        #If all threads last attempt timed out, assumed target is dead
        for threadTimeout in self.threadsOperationTimeoutOccured:
            if threadTimeout == False:
                allThreadsTimedout = False

        #if the threshhold has been surpassed, set all threads to stop
        if self.numOfTimeouts > self.numOfTimeoutsThreshold:
            print "TimeoutThreshold of %d timeouts Breached" % self.numOfTimeoutsThreshold
            self.stopThreads()
        if allThreadsTimedout == True:
            print "All Threads timed out last post."
            self.stopThreads()

    def getRunTime(self):
        return self.endTime - self.startTime

    def getTotalRunTime(self):
        return self.runTime

#this will actually do the work of of using XDos and XMLPost etc.. etc..
class ThreadWorker(threading.Thread):
    def __init__(self, threadMaster = None, threadNumber = None, xdos = None):
        threading.Thread.__init__(self)
        self.threadMaster = threadMaster
        self.threadNumber = threadNumber
        self.xdos = xdos
        self.continueStatus = True

        postAttrbs           = xdos.xmlPostAttribs
        self.generate        = postAttrbs['generate']
        self.useTLS          = postAttrbs['https']
        self.version         = postAttrbs['version']
        self.proxy           = None
        self.proxyport       = None
        self.IDSEvasionURI   = None
        self.keyfile         = None
        self.certfile        = None
        self.bauser          = None
        self.bapass          = None
        self.soapAction      = None
        self.alterhost       = None

        if postAttrbs.has_key('proxy'):
            self.proxy      = postAttrbs['proxy']
        if postAttrbs.has_key('proxyport'):
            self.proxyport  = postAttrbs['proxyport']
        if postAttrbs.has_key('IDSEvasionURI'):
            self.IDSEvasionURI   = postAttrbs['IDSEvasionURI']
        if postAttrbs.has_key('keyfile'):
            self.keyfile         = postAttrbs['keyfile']
        if postAttrbs.has_key('certfile'):
            self.certfile        = postAttrbs['certfile']
        if postAttrbs.has_key('bauser'):
            self.bauser          = postAttrbs['bauser']
        if postAttrbs.has_key('bapass'):
            self.bapass          = postAttrbs['bapass']
        if postAttrbs.has_key('alterhost'):
            self.alterhost       = postAttrbs['alterhost']


        self.methods = self.xdos.xmlPostMethods.keys()
        self.payloads = {}
        for method in self.methods:
            self.payloads[method] = self.xdos.getVectors(method)

    def run(self):
        #check continue status
        while self.continueStatus == True:
            for method in self.methods:
                for payload in self.payloads[method]:
                    if(self.continueStatus == False):  #stop posting, some stop threshold has been reached
                        break
                    xmlpost = self.setupXmlPost(str(payload),method)
                    #print "Thread #%d posting to remote object." % self.threadNumber
                    xmlpost.doPost()

                    if xmlpost.getOperationTimeoutStatus() == True: #timeout occured
                        print "Thread #%d - Timeout occured, check host for availability\n" % self.threadNumber
                        self.threadMaster.timeoutOccured(self.threadNumber)
                    else:
                        self.threadMaster.resetOperationTimeout(self.threadNumber)


    def setContinueStatus(self, status = True):
        self.continueStatus = status

    def getContinueStatus(self):
        return self.continueStatus

    def setupXmlPost(self,payload = None,method = None):
        host = self.xdos.xmlPostMethods[method]['host']
        uri = self.xdos.xmlPostMethods[method]['uri']
        if self.keyfile is not None and self.certfile is not None:
            p = XMLPost.XMLPost(host, False, payload, method,
                                    uri, True,
                                    keyfile=self.keyfile, certfile=self.certfile,
                                    proxy=self.proxy, proxyport=self.proxyport,version=self.version)
        else:
            p = XMLPost.XMLPost(host, False, payload, method,
                                uri, https=self.useTLS,
                                proxy=self.proxy, proxyport=self.proxyport,
                                version=self.version)

        if self.bauser is not None and self.bapass is not None:
            p.setBasicAuthCreds(self.bauser, self.bapass)
        if self.xdos.xmlPostMethods[method]['soapAction'] is not None:
            p.setSOAPAction(self.xdos.xmlPostMethods[method]['soapAction'])
        if self.alterhost is not None:
            p.setAlternateHost(self.alterhost)

        return p

class ThreadTime(threading.Thread):
    def __init__(self, threadMaster = None, totalRunTime = None):
        threading.Thread.__init__(self)
        self.threadMaster = threadMaster
        self.runTime = totalRunTime
        self.startTime = None
        self.endTime = None
        self.continueStatus = True

    def run(self):
        self.startTime = time.time()
        endTime = self.startTime + self.runTime
        while time.time() < endTime and self.continueStatus == True:
            time.sleep(10)
        #time has run out
        print "Time has run out"
        self.threadMaster.stopThreads()

    def setContinueStatus(self, status = True):
        self.continueStatus = status

    def getContinueStatus(self):
        return self.continueStatus