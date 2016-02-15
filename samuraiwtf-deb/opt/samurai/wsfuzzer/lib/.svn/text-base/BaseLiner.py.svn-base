"""
# SOAP Attack
#
# FILENAME      : BaseLiner.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# DATE          : 9/18/2008
# LAST UPDATE   : 8/30/2010
# ABSTRACT      : A class to establish time baselines for a sampling
#                 of random trips to and from a target
#
# Copyright (c) 2008 - 2010 neuroFuzz, LLC
#
"""

from StringIO import StringIO

'''
   Baseliner takes 20 ultra-simple vectors and uses them
   in payloads against the target. The goal is to establish a
   pool of known good round trips and collect the time for each.
   From that a baseline formulated with some time padding.
'''
class BaseLiner(object):
    def __init__(self, xmlp=None, targetParams=None, cnt=None, modXML=None):
        object.__init__(self)
        self.xmlp = xmlp
        self.baseLine = 0
        self.alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'aaa', 'bbb',
            'ccc', 'ddd', 'eee', 'fff', 'AAA', 'BBB', 'CCC', 'DDD',
            'A', 'B', 'C', 'D']

        if targetParams:
            self.targetParams = targetParams
        else:
            self.targetParams = []
        if cnt:
            self.cnt = cnt-1
        else:
            self.cnt = None
        if modXML is not None:
            self.modXML = modXML
        # populate the array of arrays of generic data to send
        # to the target
        self.prepPayloads()
        self.times = []

    # NAME     : getBaseLine
    # PARAMS   : None
    # RETURN   : Int
    # DESC     : returns self.baseLine
    def getBaseLine(self):
        return self.baseLine
    # EOF: getBaseLine

    # NAME     : getPayloads
    # PARAMS   : None
    # RETURN   : Array
    # DESC     : returns self.payLoads
    def getPayloads(self):
        return self.payLoads
    # EOF: getPayloads

    # NAME     : prepPayloads
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : An array of arrays is populated.
    #            Each subarray is populated
    #            with generic data from
    #            self.alphabet based on the number
    #            of parameters for the target, this
    #            value is in self.cnt.
    def prepPayloads(self):
        if self.cnt:
            one = []
            two = []
            three = []
            four = []
            five = []
            six = []
            seven = []
            eight = []
            nine = []
            ten = []
            eleven = []
            twelve = []
            thirteen = []
            fourteen = []
            fifteen = []
            sixteen = []
            seventeen = []
            eighteen = []
            nineteen = []
            twenty = []
            self.payLoads = [one, two, three, four, five, six, seven, eight, nine, ten,
                eleven, twelve, thirteen, fourteen, fifteen, sixteen,
                seventeen, eighteen, nineteen, twenty]

            cnt = 0
            for p in self.payLoads:
                for c in range(0, self.cnt):
                    p.append(self.alphabet[cnt])
                cnt = cnt + 1
    # EOF: prepPayloads

    # NAME     : grind
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : here the XML payload is modified
    #            using the data from self.alphabet
    #            then XMLPost object is used to
    #            send the 20 requests at the target.
    #            All round trip time measurements are
    #            placed into the array "times".
    #            Then calcBaseLine is called since
    #            all the necessary values are recorded
    def grind(self, padding=False):
        for p in self.payLoads:
            # modify the XML payload
            payload = self.modXML.getvalue() % tuple(p)
            # set the payload for XMLPost obj
            self.xmlp.setSOAPStr(StringIO(payload))
            # send the POST
            self.xmlp.doPost()
            # force a capture of the elapsed time value
            self.xmlp.getElapsed()
            # populate the array with the elapsed time values
            self.times.append(self.xmlp.getRawElapsed())
        self.calcBaseLine(padding)
    # EOF: grind

    # NAME     : calcBaseLine
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : calculates a baseline time
    #            value from the average of
    #            20 round trips. Then this
    #            value is padded by multiplication
    #            of 3 to play it safe. The result
    #            is placed into a class variable
    def calcBaseLine(self, padding=False):
        # calc the average of the 20
        # round trips first
        cnt = 0
        for t in self.times:
            cnt = cnt + t

        avg = cnt / 20.00
        if padding:
            # then pad it (X3) just to be safe
            self.baseLine = avg * 2.50
        else:
            self.baseLine = avg
    # EOF: calcBaseLine
