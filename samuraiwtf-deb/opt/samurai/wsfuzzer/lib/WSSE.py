"""
# Web Services Fuzzer
#
# FILENAME      : WSSE.py
# AUTHORS       : Andres Andreu <andres [at] neurofuzz dot com>
# MODIFIED BY   : Andres Andreu
# DATE          : 9/5/2010
# LAST UPDATE   : 9/5/2010
# ABSTRACT      : A prog to perform fuzzing attacks against web services.
#               : This tool is meant to be part of a web app pen testers toolkit.
#
#               : A lot of this is loosely based on the WSSE classes from the
#                 SUDS project: https://fedorahosted.org/suds/
#                 I would have just used their stuff but we do things differently
#                 with WSFuzzer so I just modified accordingly.
#
# Copyright (c) 2010 neuroFuzz, LLC
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
from lib import XMLProcessor
from datetime import datetime
from hashlib import md5
import time
import datetime as dt
import re
######################################################################################
# vars
dsns = \
    ('ds',
     'http://www.w3.org/2000/09/xmldsig#')
wssens = \
    ('wsse',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd')
wsuns = \
    ('wsu',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')
wsencns = \
    ('wsenc',
     'http://www.w3.org/2001/04/xmlenc#')
passtype = \
    ('Type',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
    )
enctype = \
    ('EncodingType',
    'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security1.0#Base64Binary'
    )
######################################################################################

""" Unmodified from the SUDS project """
class Date:
    """
    An XML date object.
    Supported formats:
        - YYYY-MM-DD
        - YYYY-MM-DD(z|Z)
        - YYYY-MM-DD+06:00
        - YYYY-MM-DD-06:00
    @ivar date: The object value.
    @type date: B{datetime}.I{date}
    """
    def __init__(self, date):
        """
        @param date: The value of the object.
        @type date: (date|str)
        @raise ValueError: When I{date} is invalid.
        """
        if isinstance(date, dt.date):
            self.date = date
            return
        if isinstance(date, basestring):
            self.date = self.__parse(date)
            return
        raise ValueError, type(date)

    def year(self):
        """
        Get the I{year} component.
        @return: The year.
        @rtype: int
        """
        return self.date.year

    def month(self):
        """
        Get the I{month} component.
        @return: The month.
        @rtype: int
        """
        return self.date.month

    def day(self):
        """
        Get the I{day} component.
        @return: The day.
        @rtype: int
        """
        return self.date.day

    def __parse(self, s):
        """
        Parse the string date.
        Supported formats:
            - YYYY-MM-DD
            - YYYY-MM-DD(z|Z)
            - YYYY-MM-DD+06:00
            - YYYY-MM-DD-06:00
        Although, the TZ is ignored because it's meaningless
        without the time, right?
        @param s: A date string.
        @type s: str
        @return: A date object.
        @rtype: I{date}
        """
        try:
            year, month, day = s[:10].split('-', 2)
            year = int(year)
            month = int(month)
            day = int(day)
            return dt.date(year, month, day)
        except:
            log.debug(s, exec_info=True)
            raise ValueError, 'Invalid format "%s"' % s

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        return self.date.isoformat()
# EOC: Date

""" Unmodified from the SUDS project """
class Time:
    """
    An XML time object.
    Supported formats:
        - HH:MI:SS
        - HH:MI:SS(z|Z)
        - HH:MI:SS.ms
        - HH:MI:SS.ms(z|Z)
        - HH:MI:SS(+|-)06:00
        - HH:MI:SS.ms(+|-)06:00
    @ivar tz: The timezone
    @type tz: L{Timezone}
    @ivar date: The object value.
    @type date: B{datetime}.I{time}
    """

    def __init__(self, time, adjusted=True):
        """
        @param time: The value of the object.
        @type time: (time|str)
        @param adjusted: Adjust for I{local} Timezone.
        @type adjusted: boolean
        @raise ValueError: When I{time} is invalid.
        """
        self.tz = Timezone()
        if isinstance(time, dt.time):
            self.time = time
            return
        if isinstance(time, basestring):
            self.time = self.__parse(time)
            if adjusted:
                self.__adjust()
            return
        raise ValueError, type(time)

    def hour(self):
        """
        Get the I{hour} component.
        @return: The hour.
        @rtype: int
        """
        return self.time.hour

    def minute(self):
        """
        Get the I{minute} component.
        @return: The minute.
        @rtype: int
        """
        return self.time.minute

    def second(self):
        """
        Get the I{seconds} component.
        @return: The seconds.
        @rtype: int
        """
        return self.time.second

    def microsecond(self):
        """
        Get the I{microsecond} component.
        @return: The microsecond.
        @rtype: int
        """
        return self.time.microsecond

    def __adjust(self):
        """
        Adjust for TZ offset.
        """
        if hasattr(self, 'offset'):
            today = dt.date.today()
            delta = self.tz.adjustment(self.offset)
            d = dt.datetime.combine(today, self.time)
            d = ( d + delta )
            self.time = d.time()

    def __parse(self, s):
        """
        Parse the string date.
        Patterns:
            - HH:MI:SS
            - HH:MI:SS(z|Z)
            - HH:MI:SS.ms
            - HH:MI:SS.ms(z|Z)
            - HH:MI:SS(+|-)06:00
            - HH:MI:SS.ms(+|-)06:00
        @param s: A time string.
        @type s: str
        @return: A time object.
        @rtype: B{datetime}.I{time}
        """
        try:
            offset = None
            part = Timezone.split(s)
            hour, minute, second = part[0].split(':', 2)
            hour = int(hour)
            minute = int(minute)
            second, ms = self.__second(second)
            if len(part) == 2:
                self.offset = self.__offset(part[1])
            if ms is None:
                return dt.time(hour, minute, second)
            else:
                return dt.time(hour, minute, second, ms)
        except:
            log.debug(s, exec_info=True)
            raise ValueError, 'Invalid format "%s"' % s

    def __second(self, s):
        """
        Parse the seconds and microseconds.
        The microseconds are truncated to 999999 due to a restriction in
        the python datetime.datetime object.
        @param s: A string representation of the seconds.
        @type s: str
        @return: Tuple of (sec,ms)
        @rtype: tuple.
        """
        part = s.split('.')
        if len(part) > 1:
            return (int(part[0]), int(part[1][:6]))
        else:
            return (int(part[0]), None)

    def __offset(self, s):
        """
        Parse the TZ offset.
        @param s: A string representation of the TZ offset.
        @type s: str
        @return: The signed offset in hours.
        @rtype: str
        """
        if len(s) == len('-00:00'):
            return int(s[:3])
        if len(s) == 0:
            return self.tz.local
        if len(s) == 1:
            return 0
        raise Exception()

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        time = self.time.isoformat()
        if self.tz.local:
            return '%s%+.2d:00' % (time, self.tz.local)
        else:
            return '%sZ' % time
# EOC: Time

""" Unmodified from the SUDS project """
class DateTime(Date,Time):
    """
    An XML time object.
    Supported formats:
        - YYYY-MM-DDB{T}HH:MI:SS
        - YYYY-MM-DDB{T}HH:MI:SS(z|Z)
        - YYYY-MM-DDB{T}HH:MI:SS.ms
        - YYYY-MM-DDB{T}HH:MI:SS.ms(z|Z)
        - YYYY-MM-DDB{T}HH:MI:SS(+|-)06:00
        - YYYY-MM-DDB{T}HH:MI:SS.ms(+|-)06:00
    @ivar datetime: The object value.
    @type datetime: B{datetime}.I{datedate}
    """
    def __init__(self, date):
        """
        @param date: The value of the object.
        @type date: (datetime|str)
        @raise ValueError: When I{tm} is invalid.
        """
        if isinstance(date, dt.datetime):
            Date.__init__(self, date.date())
            Time.__init__(self, date.time())
            self.datetime = \
                dt.datetime.combine(self.date, self.time)
            return
        if isinstance(date, basestring):
            part = date.split('T')
            Date.__init__(self, part[0])
            Time.__init__(self, part[1], 0)
            self.datetime = \
                dt.datetime.combine(self.date, self.time)
            self.__adjust()
            return
        raise ValueError, type(date)

    def __adjust(self):
        """
        Adjust for TZ offset.
        """
        if not hasattr(self, 'offset'):
            return
        delta = self.tz.adjustment(self.offset)
        try:
            d = ( self.datetime + delta )
            self.datetime = d
            self.date = d.date()
            self.time = d.time()
        except OverflowError:
            log.warn('"%s" caused overflow, not-adjusted', self.datetime)

    def __str__(self):
        return unicode(self)

    def __unicode__(self):
        s = []
        s.append(Date.__unicode__(self))
        s.append(Time.__unicode__(self))
        return 'T'.join(s)
# EOC: DateTime

""" Unmodified from the SUDS project """
class UTC(DateTime):
    """
    Represents current UTC time.
    """

    def __init__(self, date=None):
        if date is None:
            date = dt.datetime.utcnow()
        DateTime.__init__(self, date)
        self.tz.local = 0
# EOC: UTC

""" Unmodified from the SUDS project """
class Timezone:
    """
    Timezone object used to do TZ conversions
    @cvar local: The (A) local TZ offset.
    @type local: int
    @cvar patten: The regex patten to match TZ.
    @type patten: L{re.RegexObject}
    """

    pattern = re.compile('([zZ])|([\-\+][0-9]{2}:[0-9]{2})')

    LOCAL = ( 0-time.timezone/60/60 )

    def __init__(self, offset=None):
        if offset is None:
            offset = self.LOCAL
        self.local = offset

    @classmethod
    def split(cls, s):
        """
        Split the TZ from string.
        @param s: A string containing a timezone
        @type s: basestring
        @return: The split parts.
        @rtype: tuple
        """
        m = cls.pattern.search(s)
        if m is None:
            return (s,)
        x = m.start(0)
        return (s[:x], s[x:])

    def adjustment(self, offset):
        """
        Get the adjustment to the I{local} TZ.
        @return: The delta between I{offset} and local TZ.
        @rtype: B{datetime}.I{timedelta}
        """
        delta = ( self.local - offset )
        return dt.timedelta(hours=delta)
# EOC: Timezone

""" Modified from the SUDS project """
class WSSecurity(object):
    """
    WS-Security object.
    @ivar tokens: A list of security tokens
    @type tokens: [L{Token},...]
    @ivar signatures: A list of signatures.
    @type signatures: TBD
    @ivar references: A list of references.
    @type references: TBD
    @ivar keys: A list of encryption keys.
    @type keys: TBD
    """

    def __init__(self):
        self.mustUnderstand = True
        self.tokens = []
        self.signatures = []
        self.references = []
        self.keys = []

    def xml(self):
        """
        Get xml representation of the object.
        @return: The root node.
        @rtype: L{Element}
        """
        return {'name':'wsse:Security', 'ns':[wssens,('soapenv:mustUnderstand','1')]}
# EOC: WSSecurity

""" Unmodified from the SUDS project """
class Token(object):
    """ I{Abstract} security token. """

    @classmethod
    def now(cls):
        return datetime.now()

    @classmethod
    def utc(cls):
        return datetime.utcnow()

    @classmethod
    def sysdate(cls):
        utc = UTC()
        return str(utc)

    def __init__(self):
        object.__init__(self)
# EOC: Token

""" Modified from the SUDS project """
class UsernameToken(Token):
    """
    Represents a basic I{UsernameToken} WS-Secuirty token.
    @ivar username: A username.
    @type username: str
    @ivar password: A password.
    @type password: str
    @ivar nonce: A set of bytes to prevent reply attacks.
    @type nonce: str
    @ivar created: The token created.
    @type created: L{datetime}
    """

    def __init__(self, username=None, password=None):
        """
        @param username: A username.
        @type username: str
        @param password: A password.
        @type password: str
        """
        Token.__init__(self)
        self.username = username
        self.password = password
        self.nonce = None
        self.created = None

    def setnonce(self, text=None):
        """
        Set I{nonce} which is arbitraty set of bytes to prevent
        reply attacks.
        @param text: The nonce text value.
            Generated when I{None}.
        @type text: str
        """
        if text is None:
            s = []
            s.append(self.username)
            s.append(self.password)
            s.append(Token.sysdate())
            m = md5()
            m.update(':'.join(s))
            self.nonce = m.hexdigest()
        else:
            self.nonce = text

        return {'name':'wsse:Nonce', 'value':self.nonce, 'attributes':[wssens,enctype]}

    def setcreated(self, dt=None):
        """
        Set I{created}.
        @param dt: The created date & time.
            Set as datetime.utc() when I{None}.
        @type dt: L{datetime}
        """
        if dt is None:
            self.created = Token.utc()
        else:
            self.created = dt

        return {'name':'wsu:Created', 'value':str(UTC(self.created)), 'attributes':[wsuns,enctype]}

    def setuser(self):
        return {'name':'wsse:Username', 'value':self.username, 'attributes':[wssens]}

    def setpass(self):
        return {'name':'wsse:Password', 'value':self.password, 'attributes':[passtype]}


    def settoken(self):
        return {'name':'wsse:UsernameToken', 'ns':[wssens]}
# EOC: UsernameToken

'''
class Timestamp(Token):
    """
    Represents the I{Timestamp} WS-Secuirty token.
    @ivar created: The token created.
    @type created: L{datetime}
    @ivar expires: The token expires.
    @type expires: L{datetime}
    """

    def __init__(self, validity=90):
        """
        @param validity: The time in seconds.
        @type validity: int
        """
        Token.__init__(self)
        self.created = Token.utc()
        self.expires = self.created + timedelta(seconds=validity)

    def xml(self):
        root = Element("Timestamp", ns=wsuns)
        created = Element('Created', ns=wsuns)
        created.setText(str(UTC(self.created)))
        expires = Element('Expires', ns=wsuns)
        expires.setText(str(UTC(self.expires)))
        root.append(created)
        root.append(expires)
        return root
'''

"""
    All of the classes above this one are either loosely or
    tightly based on the WSSE classes from the SUDS project:
    https://fedorahosted.org/suds/
"""
class WSSE():
    def __init__(self, username, password):
        self.xmlp = XMLProcessor.XMLProcessor()
        self.xmlp.createDocument()
        self.username = username
        self.password = password
    # EOF: init

    # NAME     : generateWSSEStanza
    # PARAMS   : None
    # RETURN   : str
    # DESC     : generates XML of WSSE data
    def generateWSSEStanza(self):
        s = WSSecurity()
        dict = s.xml()
        self.xmlp.createBaseElement(name=dict['name'],ns=dict['ns'])
        u = UsernameToken(username=self.username, password=self.password)
        dict = u.settoken()
        self.xmlp.populateChildElement(name=dict['name'], value=None, attributes=dict['ns'])
        dict = u.setuser()
        self.xmlp.populateChildElement(name=dict['name'], value=dict['value'], attributes=dict['attributes'], child=1)
        dict = u.setpass()
        self.xmlp.populateChildElement(name=dict['name'], value=dict['value'], attributes=dict['attributes'], child=1)
        dict = u.setnonce()
        self.xmlp.populateChildElement(name=dict['name'], value=dict['value'], attributes=dict['attributes'], child=1)
        dict = u.setcreated()
        self.xmlp.populateChildElement(name=dict['name'], value=dict['value'], attributes=dict['attributes'], child=1)
    # EOF: generateWSSEStanza

    # NAME     : getWSSEStanza
    # PARAMS   : None
    # RETURN   : str
    # DESC     : returns string representation of the WSSE XML
    def getWSSEStanza(self):
        return self.xmlp.writeXML().replace("<?xml version=\"1.0\" ?>","")
    # EOF: getWSSEStanza

    # NAME     : printWSSEStanza
    # PARAMS   : None
    # RETURN   : Nothing
    # DESC     : prints string representation of the WSSE XML
    def printWSSEStanza(self):
        print self.xmlp.writeXML().replace("<?xml version=\"1.0\" ?>","")
    # EOF: printWSSEStanza

# EOC: WSSE
