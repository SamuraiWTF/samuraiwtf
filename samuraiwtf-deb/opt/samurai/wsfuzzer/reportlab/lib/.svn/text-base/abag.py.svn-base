#Copyright ReportLab Europe Ltd. 2000-2010
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/lib/abag.py
__version__=''' $Id: abag.py 3623 2009-12-17 16:18:34Z andy $ '''
__doc__='''Data structure to hold a collection of attributes, used by styles.'''
class ABag:
    """
    'Attribute Bag' - a trivial BAG class for holding attributes.

    This predates modern Python.  Doing this again, we'd use a subclass
    of dict.

    You may initialize with keyword arguments.
    a = ABag(k0=v0,....,kx=vx,....) ==> getattr(a,'kx')==vx

    c = a.clone(ak0=av0,.....) copy with optional additional attributes.
    """
    def __init__(self,**attr):
        self.__dict__.update(attr)

    def clone(self,**attr):
        n = ABag(**self.__dict__)
        if attr: n.__dict__.update(attr)
        return n

    def __repr__(self):
        D = self.__dict__
        K = D.keys()
        K.sort()
        return '%s(%s)' % (self.__class__.__name__,', '.join(['%s=%r' % (k,D[k]) for k in K]))

if __name__=="__main__":
    AB = ABag(a=1, c="hello")
    CD = AB.clone()
    print AB
    print CD
