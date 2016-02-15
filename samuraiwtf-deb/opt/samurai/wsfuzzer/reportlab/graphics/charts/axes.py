#Copyright ReportLab Europe Ltd. 2000-2004
#see license.txt for license details
#history http://www.reportlab.co.uk/cgi-bin/viewcvs.cgi/public/reportlab/trunk/reportlab/graphics/charts/axes.py
__version__=''' $Id: axes.py 3609 2009-12-07 17:58:49Z meitham $ '''
__doc__="""Collection of axes for charts.

The current collection comprises axes for charts using cartesian
coordinate systems. All axes might have tick marks and labels.
There are two dichotomies for axes: one of X and Y flavours and
another of category and value flavours.

Category axes have an ordering but no metric. They are divided
into a number of equal-sized buckets. Their tick marks or labels,
if available, go BETWEEN the buckets, and the labels are placed
below to/left of the X/Y-axis, respectively.

  Value axes have an ordering AND metric. They correspond to a nu-
  meric quantity. Value axis have a real number quantity associated
  with it. The chart tells it where to go.
  The most basic axis divides the number line into equal spaces
  and has tickmarks and labels associated with each; later we
  will add variants where you can specify the sampling
  interval.

The charts using axis tell them where the labels should be placed.

Axes of complementary X/Y flavours can be connected to each other
in various ways, i.e. with a specific reference point, like an
x/value axis to a y/value (or category) axis. In this case the
connection can be either at the top or bottom of the former or
at any absolute value (specified in points) or at some value of
the former axes in its own coordinate system.
"""

import string

from reportlab.lib.validators import    isNumber, isNumberOrNone, isListOfStringsOrNone, isListOfNumbers, \
                                        isListOfNumbersOrNone, isColorOrNone, OneOf, isBoolean, SequenceOf, \
                                        isString, EitherOr, Validator, _SequenceTypes, NoneOr, isInstanceOf
from reportlab.lib.attrmap import *
from reportlab.lib import normalDate
from reportlab.graphics.shapes import Drawing, Line, PolyLine, Group, STATE_DEFAULTS, _textBoxLimits, _rotatedBoxLimits
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.utils import nextRoundNumber

# Helpers.
def _findMinMaxValue(V, x, default, func, special=None):
    if isinstance(V[0][0],_SequenceTypes):
        if special:
            f=lambda T,x=x,special=special,func=func: special(T,x,func)
        else:
            f=lambda T,x=x: T[x]
        V=map(lambda e,f=f: map(f,e),V)
    V = filter(len,map(lambda x: filter(lambda x: x is not None,x),V))
    if len(V)==0: return default
    return func(map(func,V))

def _findMin(V, x, default,special=None):
    '''find minimum over V[i][x]'''
    return _findMinMaxValue(V,x,default,min,special=special)

def _findMax(V, x, default,special=None):
    '''find maximum over V[i][x]'''
    return _findMinMaxValue(V,x,default,max,special=special)

def _allInt(values):
    '''true if all values are int'''
    for v in values:
        try:
            if int(v)!=v: return 0
        except:
            return 0
    return 1

class AxisLineAnnotation:
    '''Create a grid like line using the given user value to draw the line
    kwds may contain
    startOffset offset from the default grid start position
    endOffset   offset from the default grid end position
    scaleValue  True/not given --> scale the value
                otherwise use the absolute value
    lo          lowest coordinate to draw default 0
    hi          highest coordinate to draw at default = length
    drawAtLimit True draw line at appropriate limit if its coordinate exceeds the lo, hi range
                False ignore if it's outside the range
    all Line keywords are acceptable
    '''
    def __init__(self,v,**kwds):
        self._v = v
        self._kwds = kwds

    def __call__(self,axis):
        kwds = self._kwds.copy()
        scaleValue = kwds.pop('scaleValue',True)
        if axis.isYAxis:
            offs = axis._x
        else:
            offs = axis._y
        s = kwds.pop('start',None)
        e = kwds.pop('end',None)
        if s is None or e is None:
            dim = getattr(getattr(axis,'joinAxis',None),'getGridDims',None)
            if dim and callable(dim):
                dim = dim()
            if dim:
                if s is None: s = dim[0]
                if e is None: e = dim[1]
            else:
                if s is None: s = 0
                if e is None: e = 0
        hi = kwds.pop('hi',axis._length)
        lo = kwds.pop('lo',0)
        lo,hi=min(lo,hi),max(lo,hi)
        drawAtLimit = kwds.pop('drawAtLimit',False)
        if not scaleValue:
            oaglp = axis._get_line_pos
            axis._get_line_pos = lambda x: x
        try:
            v = self._v
            func = axis._getLineFunc(s-offs,e-offs,kwds.pop('parent',None))
            if not hasattr(axis,'_tickValues'):
                axis._pseudo_configure()
            d = axis._get_line_pos(v)
            if d<lo or d>hi:
                if not drawAtLimit: return None
                if d<lo:
                    d = lo
                else:
                    d = hi
                axis._get_line_pos = lambda x: d
            L = func(v)
            for k,v in kwds.iteritems():
                setattr(L,k,v)
        finally:
            if not scaleValue:
                axis._get_line_pos = oaglp
        return L

class _AxisG(Widget):
    def _get_line_pos(self,v):
        v = self.scale(v)
        try:
            v = v[0]
        except:
            pass
        return v

    def _cxLine(self,x,start,end):
        x = self._get_line_pos(x)
        return Line(x, self._y + start, x, self._y + end)

    def _cyLine(self,y,start,end):
        y = self._get_line_pos(y)
        return Line(self._x + start, y, self._x + end, y)

    def _cxLine3d(self,x,start,end,_3d_dx,_3d_dy):
        x = self._get_line_pos(x)
        y0 = self._y + start
        y1 = self._y + end
        y0, y1 = min(y0,y1),max(y0,y1)
        x1 = x + _3d_dx
        return PolyLine([x,y0,x1,y0+_3d_dy,x1,y1+_3d_dy],strokeLineJoin=1)

    def _cyLine3d(self,y,start,end,_3d_dx,_3d_dy):
        y = self._get_line_pos(y)
        x0 = self._x + start
        x1 = self._x + end
        x0, x1 = min(x0,x1),max(x0,x1)
        y1 = y + _3d_dy
        return PolyLine([x0,y,x0+_3d_dx,y1,x1+_3d_dx,y1],strokeLineJoin=1)

    def _getLineFunc(self, start, end, parent=None):
        _3d_dx = getattr(parent,'_3d_dx',None)
        if _3d_dx is not None:
            _3d_dy = getattr(parent,'_3d_dy',None)
            f = self.isYAxis and self._cyLine3d or self._cxLine3d
            return lambda v, s=start, e=end, f=f,_3d_dx=_3d_dx,_3d_dy=_3d_dy: f(v,s,e,_3d_dx=_3d_dx,_3d_dy=_3d_dy)
        else:
            f = self.isYAxis and self._cyLine or self._cxLine
            return lambda v, s=start, e=end, f=f: f(v,s,e)

    def _makeLines(self,g,start,end,strokeColor,strokeWidth,strokeDashArray,strokeLineJoin,strokeLineCap,strokeMiterLimit,parent=None):
        func = self._getLineFunc(start,end,parent)
        if not hasattr(self,'_tickValues'):
            self._pseudo_configure()
        for t in self._tickValues:
                L = func(t)
                L.strokeColor = strokeColor
                L.strokeWidth = strokeWidth
                L.strokeDashArray = strokeDashArray
                L.strokeLineJoin = strokeLineJoin
                L.strokeLineCap = strokeLineCap
                L.strokeMiterLimit = strokeMiterLimit
                g.add(L)

    def makeGrid(self,g,dim=None,parent=None):
        '''this is only called by a container object'''
        c = self.gridStrokeColor
        w = self.gridStrokeWidth or 0
        if w and c and self.visibleGrid:
            s = self.gridStart
            e = self.gridEnd
            if s is None or e is None:
                if dim and callable(dim):
                    dim = dim()
                if dim:
                    if s is None: s = dim[0]
                    if e is None: e = dim[1]
                else:
                    if s is None: s = 0
                    if e is None: e = 0
            if s or e:
                if self.isYAxis: offs = self._x
                else: offs = self._y
                self._makeLines(g,s-offs,e-offs,c,w,self.gridStrokeDashArray,self.gridStrokeLineJoin,self.gridStrokeLineCap,self.gridStrokeMiterLimit,parent=parent)
        self._makeSubGrid(g,dim,parent)

    def _makeSubGrid(self,g,dim=None,parent=None):
        '''this is only called by a container object'''
        if not (getattr(self,'visibleSubGrid',0) and self.subTickNum>0): return
        c = self.subGridStrokeColor
        w = self.subGridStrokeWidth or 0
        if not(w and c): return
        s = self.subGridStart
        e = self.subGridEnd
        if s is None or e is None:
            if dim and callable(dim):
                dim = dim()
            if dim:
                if s is None: s = dim[0]
                if e is None: e = dim[1]
            else:
                if s is None: s = 0
                if e is None: e = 0
        if s or e:
            if self.isYAxis: offs = self._x
            else: offs = self._y
            otv = self._calcSubTicks()
            try:
                self._makeLines(g,s-offs,e-offs,c,w,self.subGridStrokeDashArray,self.subGridStrokeLineJoin,self.subGridStrokeLineCap,self.subGridStrokeMiterLimit,parent=parent)
            finally:
                self._tickValues = otv

    def getGridDims(self,start=None,end=None):
        if start is None: start = (self._x,self._y)[self.isYAxis]
        if end is None: end = start+self._length
        return start,end

    def isYAxis(self):
        if getattr(self,'_dataIndex',None)==1: return True
        acn = self.__class__.__name__
        return acn[0]=='Y' or acn[:4]=='AdjY'
    isYAxis = property(isYAxis)

    def isXAxis(self):
        if getattr(self,'_dataIndex',None)==0: return True
        acn = self.__class__.__name__
        return acn[0]=='X' or acn[:11]=='NormalDateX'
    isXAxis = property(isXAxis)

    def addAnnotations(self,g):
        for x in getattr(self,'annotations',[]):
            g.add(x(self))

# Category axes.
class CategoryAxis(_AxisG):
    "Abstract category axis, unusable in itself."
    _nodoc = 1
    _attrMap = AttrMap(
        visible = AttrMapValue(isBoolean, desc='Display entire object, if true.'),
        visibleAxis = AttrMapValue(isBoolean, desc='Display axis line, if true.'),
        visibleTicks = AttrMapValue(isBoolean, desc='Display axis ticks, if true.'),
        visibleLabels = AttrMapValue(isBoolean, desc='Display axis labels, if true.'),
        visibleGrid = AttrMapValue(isBoolean, desc='Display axis grid, if true.'),
        strokeWidth = AttrMapValue(isNumber, desc='Width of axis line and ticks.'),
        strokeColor = AttrMapValue(isColorOrNone, desc='Color of axis line and ticks.'),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone, desc='Dash array used for axis line.'),
        strokeLineCap = AttrMapValue(OneOf(0,1,2),desc="Line cap 0=butt, 1=round & 2=square"),
        strokeLineJoin = AttrMapValue(OneOf(0,1,2),desc="Line join 0=miter, 1=round & 2=bevel"),
        strokeMiterLimit = AttrMapValue(isNumber,desc="miter limit control miter line joins"),
        gridStrokeWidth = AttrMapValue(isNumber, desc='Width of grid lines.'),
        gridStrokeColor = AttrMapValue(isColorOrNone, desc='Color of grid lines.'),
        gridStrokeDashArray = AttrMapValue(isListOfNumbersOrNone, desc='Dash array used for grid lines.'),
        gridStrokeLineCap = AttrMapValue(OneOf(0,1,2),desc="Grid Line cap 0=butt, 1=round & 2=square"),
        gridStrokeLineJoin = AttrMapValue(OneOf(0,1,2),desc="Grid Line join 0=miter, 1=round & 2=bevel"),
        gridStrokeMiterLimit = AttrMapValue(isNumber,desc="Grid miter limit control miter line joins"),
        gridStart = AttrMapValue(isNumberOrNone, desc='Start of grid lines wrt axis origin'),
        gridEnd = AttrMapValue(isNumberOrNone, desc='End of grid lines wrt axis origin'),
        drawGridLast = AttrMapValue(isBoolean, desc='if true draw gridlines after everything else.'),
        labels = AttrMapValue(None, desc='Handle of the axis labels.'),
        categoryNames = AttrMapValue(isListOfStringsOrNone, desc='List of category names.'),
        joinAxis = AttrMapValue(None, desc='Join both axes if true.'),
        joinAxisPos = AttrMapValue(isNumberOrNone, desc='Position at which to join with other axis.'),
        reverseDirection = AttrMapValue(isBoolean, desc='If true reverse category direction.'),
        style = AttrMapValue(OneOf('parallel','stacked','parallel_3d'),"How common category bars are plotted"),
        labelAxisMode = AttrMapValue(OneOf('high','low','axis'), desc="Like joinAxisMode, but for the axis labels"),
        tickShift = AttrMapValue(isBoolean, desc='Tick shift typically'),
        loPad = AttrMapValue(isNumber, desc='extra inner space before start of the axis'),
        hiPad = AttrMapValue(isNumber, desc='extra inner space after end of the axis'),
        annotations = AttrMapValue(None,desc='list of annotations'),
        loLLen = AttrMapValue(isNumber, desc='extra line length before start of the axis'),
        hiLLen = AttrMapValue(isNumber, desc='extra line length after end of the axis'),
        )

    def __init__(self):
        assert self.__class__.__name__!='CategoryAxis', "Abstract Class CategoryAxis Instantiated"
        # private properties set by methods.  The initial values
        # here are to make demos easy; they would always be
        # overridden in real life.
        self._x = 50
        self._y = 50
        self._length = 100
        self._catCount = 0

        # public properties
        self.visible = 1
        self.visibleAxis = 1
        self.visibleTicks = 1
        self.visibleLabels = 1
        self.visibleGrid = 0
        self.drawGridLast = False

        self.strokeWidth = 1
        self.strokeColor = STATE_DEFAULTS['strokeColor']
        self.strokeDashArray = STATE_DEFAULTS['strokeDashArray']

        self.gridStrokeLineJoin = self.strokeLineJoin = STATE_DEFAULTS['strokeLineJoin']
        self.gridStrokeLineCap = self.strokeLineCap = STATE_DEFAULTS['strokeLineCap']
        self.gridStrokeMiterLimit = self.strokeMiterLimit = STATE_DEFAULTS['strokeMiterLimit']
        self.gridStrokeWidth = 0.25
        self.gridStrokeColor = STATE_DEFAULTS['strokeColor']
        self.gridStrokeDashArray = STATE_DEFAULTS['strokeDashArray']
        self.gridStart = self.gridEnd = None

        self.strokeLineJoin = STATE_DEFAULTS['strokeLineJoin']
        self.strokeLineCap = STATE_DEFAULTS['strokeLineCap']
        self.strokeMiterLimit = STATE_DEFAULTS['strokeMiterLimit']

        self.labels = TypedPropertyCollection(Label)
        # if None, they don't get labels. If provided,
        # you need one name per data point and they are
        # used for label text.
        self.categoryNames = None
        self.joinAxis = None
        self.joinAxisPos = None
        self.joinAxisMode = None
        self.labelAxisMode = 'axis'
        self.reverseDirection = 0
        self.style = 'parallel'

        #various private things which need to be initialized
        self._labelTextFormat = None
        self.tickShift = 0
        self.loPad = 0
        self.hiPad = 0
        self.loLLen = 0
        self.hiLLen = 0

    def setPosition(self, x, y, length):
        # ensure floating point
        self._x = float(x)
        self._y = float(y)
        self._length = float(length)

    def configure(self, multiSeries,barWidth=None):
        self._catCount = max(map(len,multiSeries))
        self._barWidth = barWidth or ((self._length-self.loPad-self.hiPad)/float(self._catCount or 1))
        self._calcTickmarkPositions()

    def _calcTickmarkPositions(self):
        n = self._catCount
        if self.tickShift:
            self._tickValues = [t+0.5 for t in xrange(n)]
        else:
            if self.reverseDirection:
                self._tickValues = range(-1,n)
            else:
                self._tickValues = range(n+1)

    def draw(self):
        g = Group()

        if not self.visible:
            return g

        g.add(self.makeAxis())
        g.add(self.makeTicks())
        g.add(self.makeTickLabels())
        self.addAnnotations(g)

        return g

    def _scale(self,idx):
        if self.reverseDirection: idx = self._catCount-idx-1
        return idx

def _assertYAxis(axis):
    assert axis.isYAxis, "Cannot connect to other axes (%s), but Y- ones." % axis.__class__.__name__
def _assertXAxis(axis):
    assert axis.isXAxis, "Cannot connect to other axes (%s), but X- ones." % axis.__class__.__name__

class _XTicks:
    _tickTweaks = 0 #try 0.25-0.5

    def _drawTicksInner(self,tU,tD,g):
        if tU or tD:
            sW = self.strokeWidth
            tW = self._tickTweaks
            if tW:
                if tU and not tD:
                    tD = tW*sW
                elif tD and not tU:
                    tU = tW*sW
            self._makeLines(g,tU,-tD,self.strokeColor,sW,self.strokeDashArray,self.strokeLineJoin,self.strokeLineCap,self.strokeMiterLimit)

    def _drawTicks(self,tU,tD,g=None):
        g = g or Group()
        if self.visibleTicks:
            self._drawTicksInner(tU,tD,g)
        return g

    def _calcSubTicks(self):
        if not hasattr(self,'_tickValues'):
            self._pseudo_configure()
        otv = self._tickValues
        if not hasattr(self,'_subTickValues'):
            acn = self.__class__.__name__
            if acn[:11]=='NormalDateX':
                iFuzz = 0
                dCnv = int
            else:
                iFuzz = 1e-8
                dCnv = lambda x:x
            OTV = otv[:]
            T = [].append
            nst = int(self.subTickNum)
            i = len(OTV)
            if i<2:
                self._subTickValues = []
            else:
                if i==2:
                    dst = OTV[1]-OTV[0]
                elif i==3:
                    dst = max(OTV[1]-OTV[0],OTV[2]-OTV[1])
                else:
                    i >>= 1
                    dst = OTV[i+1] - OTV[i]
                fuzz = dst*iFuzz
                vn = self._valueMin+fuzz
                vx = self._valueMax-fuzz
                if OTV[0]>vn: OTV.insert(0,OTV[0]-dst)
                if OTV[-1]<vx: OTV.append(OTV[-1]+dst)
                dst /= float(nst+1)
                for i,x in enumerate(OTV[:-1]):
                    for j in xrange(nst):
                        t = x+dCnv((j+1)*dst)
                        if t<=vn or t>=vx: continue
                        T(t)
                self._subTickValues = T.__self__
        self._tickValues = self._subTickValues
        return otv

    def _drawSubTicks(self,tU,tD,g):
        if getattr(self,'visibleSubTicks',0) and self.subTickNum>0:
            otv = self._calcSubTicks()
            try:
                self._drawTicksInner(tU,tD,g)
            finally:
                self._tickValues = otv

    def makeTicks(self):
        yold=self._y
        try:
            self._y = self._labelAxisPos(getattr(self,'tickAxisMode','axis'))
            g = self._drawTicks(self.tickUp,self.tickDown)
            self._drawSubTicks(getattr(self,'subTickHi',0),getattr(self,'subTickLo',0),g)
            return g
        finally:
            self._y = yold

    def _labelAxisPos(self,mode=None):
        axis = self.joinAxis
        if axis:
            mode = mode or self.labelAxisMode
            if mode == 'low':
                return axis._y
            elif mode == 'high':
                return axis._y + axis._length
        return self._y

class _YTicks(_XTicks):

    def _labelAxisPos(self,mode=None):
        axis = self.joinAxis
        if axis:
            mode = mode or self.labelAxisMode
            if mode == 'low':
                return axis._x
            elif mode == 'high':
                return axis._x + axis._length
        return self._x

    def makeTicks(self):
        xold=self._x
        try:
            self._x = self._labelAxisPos(getattr(self,'tickAxisMode','axis'))
            g = self._drawTicks(self.tickRight,self.tickLeft)
            self._drawSubTicks(getattr(self,'subTickHi',0),getattr(self,'subTickLo',0),g)
            return g
        finally:
            self._x = xold

class XCategoryAxis(_XTicks,CategoryAxis):
    "X/category axis"

    _attrMap = AttrMap(BASE=CategoryAxis,
        tickUp = AttrMapValue(isNumber,
            desc='Tick length up the axis.'),
        tickDown = AttrMapValue(isNumber,
            desc='Tick length down the axis.'),
        joinAxisMode = AttrMapValue(OneOf('bottom', 'top', 'value', 'points', None),
            desc="Mode used for connecting axis ('bottom', 'top', 'value', 'points', None)."),
        )

    _dataIndex = 0

    def __init__(self):
        CategoryAxis.__init__(self)
        self.labels.boxAnchor = 'n' #north - top edge
        self.labels.dy = -5
        # ultra-simple tick marks for now go between categories
        # and have same line style as axis - need more
        self.tickUp = 0  # how far into chart does tick go?
        self.tickDown = 5  # how far below axis does tick go?

    def demo(self):
        self.setPosition(30, 70, 140)
        self.configure([(10,20,30,40,50)])

        self.categoryNames = ['One','Two','Three','Four','Five']
        # all labels top-centre aligned apart from the last
        self.labels.boxAnchor = 'n'
        self.labels[4].boxAnchor = 'e'
        self.labels[4].angle = 90

        d = Drawing(200, 100)
        d.add(self)
        return d

    def joinToAxis(self, yAxis, mode='bottom', pos=None):
        "Join with y-axis using some mode."

        _assertYAxis(yAxis)
        if mode == 'bottom':
            self._x = yAxis._x
            self._y = yAxis._y
        elif mode == 'top':
            self._x = yAxis._x
            self._y = yAxis._y + yAxis._length
        elif mode == 'value':
            self._x = yAxis._x
            self._y = yAxis.scale(pos)
        elif mode == 'points':
            self._x = yAxis._x
            self._y = pos

    def _joinToAxis(self):
        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('bottom', 'top'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

    def scale(self, idx):
        """returns the x position and width in drawing units of the slice"""
        return (self._x + self.loPad + self._scale(idx)*self._barWidth, self._barWidth)

    def makeAxis(self):
        g = Group()
        self._joinToAxis()
        if not self.visibleAxis: return g

        axis = Line(self._x-self.loLLen, self._y, self._x + self._length+self.hiLLen, self._y)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)

        return g

    def makeTickLabels(self):
        g = Group()

        if not self.visibleLabels: return g

        categoryNames = self.categoryNames
        if categoryNames is not None:
            catCount = self._catCount
            n = len(categoryNames)
            reverseDirection = self.reverseDirection
            barWidth = self._barWidth
            _y = self._labelAxisPos()
            _x = self._x

            for i in xrange(catCount):
                if reverseDirection: ic = catCount-i-1
                else: ic = i
                if ic>=n: continue
                x = _x + (i+0.5) * barWidth
                label = self.labels[i]
                label.setOrigin(x, _y)
                label.setText(categoryNames[ic] or '')
                g.add(label)

        return g

class YCategoryAxis(_YTicks,CategoryAxis):
    "Y/category axis"

    _attrMap = AttrMap(BASE=CategoryAxis,
        tickLeft = AttrMapValue(isNumber,
            desc='Tick length left of the axis.'),
        tickRight = AttrMapValue(isNumber,
            desc='Tick length right of the axis.'),
        joinAxisMode = AttrMapValue(OneOf(('left', 'right', 'value', 'points', None)),
            desc="Mode used for connecting axis ('left', 'right', 'value', 'points', None)."),
        )

    _dataIndex = 1

    def __init__(self):
        CategoryAxis.__init__(self)
        self.labels.boxAnchor = 'e' #east - right edge
        self.labels.dx = -5
        # ultra-simple tick marks for now go between categories
        # and have same line style as axis - need more
        self.tickLeft = 5  # how far left of axis does tick go?
        self.tickRight = 0  # how far right of axis does tick go?

    def demo(self):
        self.setPosition(50, 10, 80)
        self.configure([(10,20,30)])
        self.categoryNames = ['One','Two','Three']
        # all labels top-centre aligned apart from the last
        self.labels.boxAnchor = 'e'
        self.labels[2].boxAnchor = 's'
        self.labels[2].angle = 90

        d = Drawing(200, 100)
        d.add(self)
        return d

    def joinToAxis(self, xAxis, mode='left', pos=None):
        "Join with x-axis using some mode."

        _assertXAxis(xAxis)

        if mode == 'left':
            self._x = xAxis._x * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'right':
            self._x = (xAxis._x + xAxis._length) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'value':
            self._x = xAxis.scale(pos) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'points':
            self._x = pos * 1.0
            self._y = xAxis._y * 1.0

    def _joinToAxis(self):
        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('left', 'right'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

    def scale(self, idx):
        "Returns the y position and width in drawing units of the slice."
        return (self._y + self._scale(idx)*self._barWidth, self._barWidth)

    def makeAxis(self):
        g = Group()
        self._joinToAxis()
        if not self.visibleAxis: return g

        axis = Line(self._x, self._y-self.loLLen, self._x, self._y + self._length+self.hiLLen)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)

        return g

    def makeTickLabels(self):
        g = Group()

        if not self.visibleLabels: return g

        categoryNames = self.categoryNames
        if categoryNames is not None:
            catCount = self._catCount
            n = len(categoryNames)
            reverseDirection = self.reverseDirection
            barWidth = self._barWidth
            labels = self.labels
            _x = self._labelAxisPos()
            _y = self._y
            for i in xrange(catCount):
                if reverseDirection: ic = catCount-i-1
                else: ic = i
                if ic>=n: continue
                y = _y + (i+0.5) * barWidth
                label = labels[i]
                label.setOrigin(_x, y)
                label.setText(categoryNames[ic] or '')
                g.add(label)
        return g

class TickLabeller:
    '''Abstract base class which may be used to indicate a change
    in the call signature for callable label formats
    '''
    def __call__(self,axis,value):
        return 'Abstract class instance called'

# Value axes.
class ValueAxis(_AxisG):
    "Abstract value axis, unusable in itself."

    _attrMap = AttrMap(
        forceZero = AttrMapValue(EitherOr((isBoolean,OneOf('near'))), desc='Ensure zero in range if true.'),
        visible = AttrMapValue(isBoolean, desc='Display entire object, if true.'),
        visibleAxis = AttrMapValue(isBoolean, desc='Display axis line, if true.'),
        visibleLabels = AttrMapValue(isBoolean, desc='Display axis labels, if true.'),
        visibleTicks = AttrMapValue(isBoolean, desc='Display axis ticks, if true.'),
        visibleGrid = AttrMapValue(isBoolean, desc='Display axis grid, if true.'),
        strokeWidth = AttrMapValue(isNumber, desc='Width of axis line and ticks.'),
        strokeColor = AttrMapValue(isColorOrNone, desc='Color of axis line and ticks.'),
        strokeDashArray = AttrMapValue(isListOfNumbersOrNone, desc='Dash array used for axis line.'),
        strokeLineCap = AttrMapValue(OneOf(0,1,2),desc="Line cap 0=butt, 1=round & 2=square"),
        strokeLineJoin = AttrMapValue(OneOf(0,1,2),desc="Line join 0=miter, 1=round & 2=bevel"),
        strokeMiterLimit = AttrMapValue(isNumber,desc="miter limit control miter line joins"),
        gridStrokeWidth = AttrMapValue(isNumber, desc='Width of grid lines.'),
        gridStrokeColor = AttrMapValue(isColorOrNone, desc='Color of grid lines.'),
        gridStrokeDashArray = AttrMapValue(isListOfNumbersOrNone, desc='Dash array used for grid lines.'),
        gridStrokeLineCap = AttrMapValue(OneOf(0,1,2),desc="Grid Line cap 0=butt, 1=round & 2=square"),
        gridStrokeLineJoin = AttrMapValue(OneOf(0,1,2),desc="Grid Line join 0=miter, 1=round & 2=bevel"),
        gridStrokeMiterLimit = AttrMapValue(isNumber,desc="Grid miter limit control miter line joins"),
        gridStart = AttrMapValue(isNumberOrNone, desc='Start of grid lines wrt axis origin'),
        gridEnd = AttrMapValue(isNumberOrNone, desc='End of grid lines wrt axis origin'),
        drawGridLast = AttrMapValue(isBoolean, desc='if true draw gridlines after everything else.'),
        minimumTickSpacing = AttrMapValue(isNumber, desc='Minimum value for distance between ticks.'),
        maximumTicks = AttrMapValue(isNumber, desc='Maximum number of ticks.'),
        labels = AttrMapValue(None, desc='Handle of the axis labels.'),
        labelAxisMode = AttrMapValue(OneOf('high','low','axis'), desc="Like joinAxisMode, but for the axis labels"),
        labelTextFormat = AttrMapValue(None, desc='Formatting string or function used for axis labels.'),
        labelTextPostFormat = AttrMapValue(None, desc='Extra Formatting string.'),
        labelTextScale = AttrMapValue(isNumberOrNone, desc='Scaling for label tick values.'),
        valueMin = AttrMapValue(isNumberOrNone, desc='Minimum value on axis.'),
        valueMax = AttrMapValue(isNumberOrNone, desc='Maximum value on axis.'),
        valueStep = AttrMapValue(isNumberOrNone, desc='Step size used between ticks.'),
        valueSteps = AttrMapValue(isListOfNumbersOrNone, desc='List of step sizes used between ticks.'),
        avoidBoundFrac = AttrMapValue(EitherOr((isNumberOrNone,SequenceOf(isNumber,emptyOK=0,lo=2,hi=2))), desc='Fraction of interval to allow above and below.'),
        rangeRound=AttrMapValue(OneOf('none','both','ceiling','floor'),'How to round the axis limits'),
        zrangePref = AttrMapValue(isNumberOrNone, desc='Zero range axis limit preference.'),
        style = AttrMapValue(OneOf('normal','stacked','parallel_3d'),"How values are plotted!"),
        skipEndL = AttrMapValue(OneOf('none','start','end','both'), desc='Skip high/low tick labels'),
        origShiftIPC = AttrMapValue(isNumberOrNone, desc='Lowest label shift interval ratio.'),
        origShiftMin = AttrMapValue(isNumberOrNone, desc='Minimum amount to shift.'),
        origShiftSpecialValue = AttrMapValue(isNumberOrNone, desc='special value for shift'),
        tickAxisMode = AttrMapValue(OneOf('high','low','axis'), desc="Like joinAxisMode, but for the ticks"),
        reverseDirection = AttrMapValue(isBoolean, desc='If true reverse category direction.'),
        annotations = AttrMapValue(None,desc='list of annotations'),
        loLLen = AttrMapValue(isNumber, desc='extra line length before start of the axis'),
        hiLLen = AttrMapValue(isNumber, desc='extra line length after end of the axis'),
        subTickNum = AttrMapValue(isNumber, desc='Number of axis sub ticks, if >0'),
        subTickLo = AttrMapValue(isNumber, desc='sub tick down or left'),
        subTickHi = AttrMapValue(isNumber, desc='sub tick up or right'),
        visibleSubTicks = AttrMapValue(isBoolean, desc='Display axis sub ticks, if true.'),
        visibleSubGrid = AttrMapValue(isBoolean, desc='Display axis sub grid, if true.'),
        subGridStrokeWidth = AttrMapValue(isNumber, desc='Width of grid lines.'),
        subGridStrokeColor = AttrMapValue(isColorOrNone, desc='Color of grid lines.'),
        subGridStrokeDashArray = AttrMapValue(isListOfNumbersOrNone, desc='Dash array used for grid lines.'),
        subGridStrokeLineCap = AttrMapValue(OneOf(0,1,2),desc="Grid Line cap 0=butt, 1=round & 2=square"),
        subGridStrokeLineJoin = AttrMapValue(OneOf(0,1,2),desc="Grid Line join 0=miter, 1=round & 2=bevel"),
        subGridStrokeMiterLimit = AttrMapValue(isNumber,desc="Grid miter limit control miter line joins"),
        subGridStart = AttrMapValue(isNumberOrNone, desc='Start of grid lines wrt axis origin'),
        subGridEnd = AttrMapValue(isNumberOrNone, desc='End of grid lines wrt axis origin'),
        )

    def __init__(self,**kw):
        assert self.__class__.__name__!='ValueAxis', 'Abstract Class ValueAxis Instantiated'
        self._setKeywords(**kw)
        self._setKeywords(
                        _configured = 0,
                        # private properties set by methods.  The initial values
                        # here are to make demos easy; they would always be
                        # overridden in real life.
                        _x = 50,
                        _y = 50,
                        _length = 100,

                        # public properties
                        visible = 1,
                        visibleAxis = 1,
                        visibleLabels = 1,
                        visibleTicks = 1,
                        visibleGrid = 0,
                        forceZero = 0,

                        strokeWidth = 1,
                        strokeColor = STATE_DEFAULTS['strokeColor'],
                        strokeDashArray = STATE_DEFAULTS['strokeDashArray'],
                        strokeLineJoin =  STATE_DEFAULTS['strokeLineJoin'],
                        strokeLineCap = STATE_DEFAULTS['strokeLineCap'],
                        strokeMiterLimit = STATE_DEFAULTS['strokeMiterLimit'],
                        gridStrokeWidth = 0.25,
                        gridStrokeColor = STATE_DEFAULTS['strokeColor'],
                        gridStrokeDashArray = STATE_DEFAULTS['strokeDashArray'],
                        gridStrokeLineJoin =  STATE_DEFAULTS['strokeLineJoin'],
                        gridStrokeLineCap = STATE_DEFAULTS['strokeLineCap'],
                        gridStrokeMiterLimit = STATE_DEFAULTS['strokeMiterLimit'],
                        gridStart = None,
                        gridEnd = None,
                        drawGridLast = False,
                        visibleSubGrid = 0,
                        visibleSubTicks = 0,
                        subTickNum = 0,
                        subTickLo = 0,
                        subTickHi = 0,
                        subGridStrokeLineJoin = STATE_DEFAULTS['strokeLineJoin'],
                        subGridStrokeLineCap = STATE_DEFAULTS['strokeLineCap'],
                        subGridStrokeMiterLimit = STATE_DEFAULTS['strokeMiterLimit'],
                        subGridStrokeWidth = 0.25,
                        subGridStrokeColor = STATE_DEFAULTS['strokeColor'],
                        subGridStrokeDashArray = STATE_DEFAULTS['strokeDashArray'],
                        subGridStart = None,
                        subGridEnd = None,

                        labels = TypedPropertyCollection(Label),

                        # how close can the ticks be?
                        minimumTickSpacing = 10,
                        maximumTicks = 7,

                        # a format string like '%0.2f'
                        # or a function which takes the value as an argument and returns a string
                        _labelTextFormat = None,
                        labelAxisMode = 'axis',
                        labelTextFormat = None,
                        labelTextPostFormat = None,
                        labelTextScale = None,

                        # if set to None, these will be worked out for you.
                        # if you override any or all of them, your values
                        # will be used.
                        valueMin = None,
                        valueMax = None,
                        valueStep = None,
                        avoidBoundFrac = None,
                        rangeRound = 'none',
                        zrangePref = 0,
                        style = 'normal',
                        skipEndL='none',
                        origShiftIPC = None,
                        origShiftMin = None,
                        origShiftSpecialValue = None,
                        tickAxisMode = 'axis',
                        reverseDirection=0,
                        loLLen=0,
                        hiLLen=0,
                        )
        self.labels.angle = 0

    def setPosition(self, x, y, length):
        # ensure floating point
        self._x = float(x)
        self._y = float(y)
        self._length = float(length)

    def configure(self, dataSeries):
        """Let the axis configure its scale and range based on the data.

        Called after setPosition. Let it look at a list of lists of
        numbers determine the tick mark intervals.  If valueMin,
        valueMax and valueStep are configured then it
        will use them; if any of them are set to None it
        will look at the data and make some sensible decision.
        You may override this to build custom axes with
        irregular intervals.  It creates an internal
        variable self._values, which is a list of numbers
        to use in plotting.
        """
        self._setRange(dataSeries)
        self._configure_end()

    def _configure_end(self):
        self._calcTickmarkPositions()
        self._calcScaleFactor()
        self._configured = 1

    def _getValueStepAndTicks(self, valueMin, valueMax,cache={}):
        try:
            K = (valueMin,valueMax)
            r = cache[K]
        except:
            self._valueMin = valueMin
            self._valueMax = valueMax
            valueStep,T = self._calcStepAndTickPositions()
            r = cache[K] = valueStep, T, valueStep*1e-8
        return r

    def _setRange(self, dataSeries):
        """Set minimum and maximum axis values.

        The dataSeries argument is assumed to be a list of data
        vectors. Each vector is itself a list or tuple of numbers.

        Returns a min, max tuple.
        """

        oMin = valueMin = self.valueMin
        oMax = valueMax = self.valueMax
        rangeRound = self.rangeRound
        if valueMin is None: valueMin = self._cValueMin = _findMin(dataSeries,self._dataIndex,0)
        if valueMax is None: valueMax = self._cValueMax = _findMax(dataSeries,self._dataIndex,0)
        if valueMin == valueMax:
            if valueMax==0:
                if oMin is None and oMax is None:
                    zrp = getattr(self,'zrangePref',0)
                    if zrp>0:
                        valueMax = zrp
                        valueMin = 0
                    elif zrp<0:
                        valueMax = 0
                        valueMin = zrp
                    else:
                        valueMax = 0.01
                        valueMin = -0.01
                elif self.valueMin is None:
                    valueMin = -0.01
                else:
                    valueMax = 0.01
            else:
                if valueMax>0:
                    valueMax = 1.2*valueMax
                    valueMin = 0.0
                else:
                    valueMax = 0.0
                    valueMin = 1.2*valueMin

        if getattr(self,'_bubblePlot',None):
            bubbleMax = float(_findMax(dataSeries,2,0))
            frac=.25
            bubbleV=frac*(valueMax-valueMin)
            self._bubbleV = bubbleV
            self._bubbleMax = bubbleMax
            self._bubbleRadius = frac*self._length
            def special(T,x,func,bubbleV=bubbleV,bubbleMax=bubbleMax):
                try:
                    v = T[2]
                except IndexError:
                    v = bubbleMAx*0.1
                bubbleV *= (v/bubbleMax)**0.5
                return func(T[x]+bubbleV,T[x]-bubbleV)
            if oMin is None: valueMin = self._cValueMin = _findMin(dataSeries,self._dataIndex,0,special=special)
            if oMax is None: valueMax = self._cValueMax = _findMax(dataSeries,self._dataIndex,0,special=special)

        forceZero = self.forceZero
        if forceZero:
            if forceZero=='near':
                forceZero = min(abs(valueMin),abs(valueMax)) <= 5*(valueMax-valueMin)
            if forceZero:
                if valueMax<0: valueMax=0
                elif valueMin>0: valueMin = 0

        abf = self.avoidBoundFrac
        do_rr = not getattr(self,'valueSteps',None)
        do_abf = abf and do_rr
        if not isinstance(abf,_SequenceTypes):
            abf = abf, abf
        do_rr = rangeRound is not 'none' and do_rr
        if do_rr:
            rrn = rangeRound in ['both','floor']
            rrx = rangeRound in ['both','ceiling']
        else:
            rrn = rrx = 0

        go = do_rr or do_abf
        cache = {}
        cMin = valueMin
        cMax = valueMax
        iter = 0
        while go and iter<=10:
            iter += 1
            go = 0
            if do_abf:
                valueStep, T, fuzz = self._getValueStepAndTicks(valueMin, valueMax, cache)
                i0 = valueStep*abf[0]
                i1 = valueStep*abf[1]
                if rrn: v = T[0]
                else: v = valueMin
                u = cMin-i0
                if abs(v)>fuzz and v>=u+fuzz:
                    valueMin = u
                    go = 1
                if rrx: v = T[-1]
                else: v = valueMax
                u = cMax+i1
                if abs(v)>fuzz and v<=u-fuzz:
                    valueMax = u
                    go = 1

            if do_rr:
                valueStep, T, fuzz = self._getValueStepAndTicks(valueMin, valueMax, cache)
                if rrn:
                    if valueMin<T[0]-fuzz:
                        valueMin = T[0]-valueStep
                        go = 1
                    else:
                        go = valueMin>=T[0]+fuzz
                        valueMin = T[0]
                if rrx:
                    if valueMax>T[-1]+fuzz:
                        valueMax = T[-1]+valueStep
                        go = 1
                    else:
                        go = valueMax<=T[-1]-fuzz
                        valueMax = T[-1]
        if iter and not go:
            self._computedValueStep = valueStep
        else:
            self._computedValueStep = None

        self._valueMin = valueMin
        self._valueMax = valueMax

        origShiftIPC = self.origShiftIPC
        origShiftMin = self.origShiftMin
        if origShiftMin is not None or origShiftIPC is not None:
            origShiftSpecialValue = self.origShiftSpecialValue
            self._calcValueStep()
            valueMax, valueMin = self._valueMax, self._valueMin
            if origShiftSpecialValue is None or abs(origShiftSpecialValue-valueMin)<1e-6:
                if origShiftIPC:
                    m = origShiftIPC*self._valueStep
                else:
                    m = 0
                if origShiftMin:
                    m = max(m,(valueMax-valueMin)*origShiftMin/self._length)
                self._valueMin -= m

        self._rangeAdjust()

    def _pseudo_configure(self):
        self._valueMin = self.valueMin
        self._valueMax = self.valueMax
        self._configure_end()

    def _rangeAdjust(self):
        """Override this if you want to alter the calculated range.

        E.g. if want a minumamum range of 30% or don't want 100%
        as the first point.
        """
        pass

    def _adjustAxisTicks(self):
        '''Override if you want to put slack at the ends of the axis
        eg if you don't want the last tick to be at the bottom etc
        '''
        pass

    def _calcScaleFactor(self):
        """Calculate the axis' scale factor.
        This should be called only *after* the axis' range is set.
        Returns a number.
        """
        self._scaleFactor = self._length / float(self._valueMax - self._valueMin)
        return self._scaleFactor

    def _calcStepAndTickPositions(self):
        valueStep = getattr(self,'_computedValueStep',None)
        if valueStep:
            del self._computedValueStep
            self._valueStep = valueStep
        else:
            self._calcValueStep()
            valueStep = self._valueStep
        valueMin = self._valueMin
        valueMax = self._valueMax
        fuzz = 1e-8*valueStep
        rangeRound = self.rangeRound
        i0 = int(float(valueMin)/valueStep)
        v = i0*valueStep
        if rangeRound in ('both','floor'):
            if v>valueMin+fuzz: i0 -= 1
        elif v<valueMin-fuzz: i0 += 1
        i1 = int(float(valueMax)/valueStep)
        v = i1*valueStep
        if rangeRound in ('both','ceiling'):
            if v<valueMax-fuzz: i1 += 1
        elif v>valueMax+fuzz: i1 -= 1
        return valueStep,[i*valueStep for i in xrange(i0,i1+1)]

    def _calcTickPositions(self):
        return self._calcStepAndTickPositions()[1]

    def _calcTickmarkPositions(self):
        """Calculate a list of tick positions on the axis.  Returns a list of numbers."""
        self._tickValues = getattr(self,'valueSteps',None)
        if self._tickValues: return self._tickValues
        self._tickValues = self._calcTickPositions()
        self._adjustAxisTicks()
        return self._tickValues

    def _calcValueStep(self):
        '''Calculate _valueStep for the axis or get from valueStep.'''
        if self.valueStep is None:
            rawRange = self._valueMax - self._valueMin
            rawInterval = rawRange / min(float(self.maximumTicks-1),(float(self._length)/self.minimumTickSpacing))
            self._valueStep = nextRoundNumber(rawInterval)
        else:
            self._valueStep = self.valueStep

    def _allIntTicks(self):
        return _allInt(self._tickValues)

    def makeTickLabels(self):
        g = Group()
        if not self.visibleLabels: return g

        f = self._labelTextFormat       # perhaps someone already set it
        if f is None:
            f = self.labelTextFormat or (self._allIntTicks() and '%.0f' or str)
        elif f is str and self._allIntTicks(): f = '%.0f'
        elif hasattr(f,'calcPlaces'):
            f.calcPlaces(self._tickValues)
        post = self.labelTextPostFormat
        scl = self.labelTextScale
        pos = [self._x, self._y]
        d = self._dataIndex
        pos[1-d] = self._labelAxisPos()
        labels = self.labels
        if self.skipEndL!='none':
            if self.isXAxis:
                sk = self._x
            else:
                sk = self._y
            if self.skipEndL=='start':
                sk = [sk]
            else:
                sk = [sk,sk+self._length]
                if self.skipEndL=='end':
                    del sk[0]
        else:
            sk = []

        i = 0
        for tick in self._tickValues:
            if f and labels[i].visible:
                v = self.scale(tick)
                if sk:
                    for skv in sk:
                        if abs(skv-v)<1e-6:
                            v = None
                            break
                if v is not None:
                    if scl is not None:
                        t = tick*scl
                    else:
                        t = tick
                    if type(f) is str: txt = f % t
                    elif isinstance(f,_SequenceTypes):
                        #it's a list, use as many items as we get
                        if i < len(f):
                            txt = f[i]
                        else:
                            txt = ''
                    elif callable(f):
                        if isinstance(f,TickLabeller):
                            txt = f(self,t)
                        else:
                            txt = f(t)
                    else:
                        raise ValueError, 'Invalid labelTextFormat %s' % f
                    if post: txt = post % txt
                    label = labels[i]
                    pos[d] = v
                    label.setOrigin(*pos)
                    label.setText(txt)
                    g.add(label)
            i += 1

        return g

    def draw(self):
        g = Group()

        if not self.visible:
            return g

        g.add(self.makeAxis())
        g.add(self.makeTicks())
        g.add(self.makeTickLabels())
        self.addAnnotations(g)

        return g

    def scale(self, value):
        """Converts a numeric value to a plotarea position.
        The chart first configures the axis, then asks it to
        """
        assert self._configured, "Axis cannot scale numbers before it is configured"
        if value is None: value = 0

        #this could be made more efficient by moving the definition of org and sf into the configuration
        org = (self._x, self._y)[self._dataIndex]
        sf = self._scaleFactor
        if self.reverseDirection:
            sf = -sf
            org += self._length
        return org + sf*(value - self._valueMin)

class XValueAxis(_XTicks,ValueAxis):
    "X/value axis"

    _attrMap = AttrMap(BASE=ValueAxis,
        tickUp = AttrMapValue(isNumber,
            desc='Tick length up the axis.'),
        tickDown = AttrMapValue(isNumber,
            desc='Tick length down the axis.'),
        joinAxis = AttrMapValue(None,
            desc='Join both axes if true.'),
        joinAxisMode = AttrMapValue(OneOf('bottom', 'top', 'value', 'points', None),
            desc="Mode used for connecting axis ('bottom', 'top', 'value', 'points', None)."),
        joinAxisPos = AttrMapValue(isNumberOrNone,
            desc='Position at which to join with other axis.'),
        )

    # Indicate the dimension of the data we're interested in.
    _dataIndex = 0

    def __init__(self,**kw):
        ValueAxis.__init__(self,**kw)

        self.labels.boxAnchor = 'n'
        self.labels.dx = 0
        self.labels.dy = -5

        self.tickUp = 0
        self.tickDown = 5

        self.joinAxis = None
        self.joinAxisMode = None
        self.joinAxisPos = None

    def demo(self):
        self.setPosition(20, 50, 150)
        self.configure([(10,20,30,40,50)])

        d = Drawing(200, 100)
        d.add(self)
        return d

    def joinToAxis(self, yAxis, mode='bottom', pos=None):
        "Join with y-axis using some mode."
        _assertYAxis(yAxis)
        if mode == 'bottom':
            self._x = yAxis._x * 1.0
            self._y = yAxis._y * 1.0
        elif mode == 'top':
            self._x = yAxis._x * 1.0
            self._y = (yAxis._y + yAxis._length) * 1.0
        elif mode == 'value':
            self._x = yAxis._x * 1.0
            self._y = yAxis.scale(pos) * 1.0
        elif mode == 'points':
            self._x = yAxis._x * 1.0
            self._y = pos * 1.0

    def _joinToAxis(self):
        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('bottom', 'top'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

    def makeAxis(self):
        g = Group()
        self._joinToAxis()
        if not self.visibleAxis: return g

        axis = Line(self._x-self.loLLen, self._y, self._x + self._length+self.hiLLen, self._y)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)

        return g

#additional utilities to help specify calendar dates on which tick marks
#are to be plotted.  After some thought, when the magic algorithm fails,
#we can let them specify a number of days-of-the-year to tick in any given
#year.

#################################################################################
#
#   Preliminary support objects/functions for the axis used in time series charts
#
#################################################################################
_months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
_maxDays = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
def parseDayAndMonth(dmstr):
    """This accepts and validates strings like "31-Dec" i.e. dates
    of no particular year.  29 Feb is allowed.  These can be used
    for recurring dates.  It returns a (dd, mm) pair where mm is the
    month integer.  If the text is not valid it raises an error.
    """

    dstr, mstr = dmstr.split('-')
    dd = int(dstr)
    mstr = mstr.lower()
    mm = _months.index(mstr) + 1
    assert dd <= _maxDays[mm-1]
    return (dd, mm)

class _isListOfDaysAndMonths(Validator):
    """This accepts and validates lists of strings like "31-Dec" i.e. dates
    of no particular year.  29 Feb is allowed.  These can be used
    for recurring dates.
    """
    def test(self,x):
        if isinstance(x,_SequenceTypes):
            answer = True
            for element in x:
                try:
                    dd, mm = parseDayAndMonth(element)
                except:
                    answer = False
            return answer
        else:
            return False

    def normalize(self,x):
        #we store them as presented, it's the most presentable way
        return x

isListOfDaysAndMonths = _isListOfDaysAndMonths()

class NormalDateXValueAxis(XValueAxis):
    """An X axis applying additional rules.

    Depending on the data and some built-in rules, the axis
    displays normalDate values as nicely formatted dates.

    The client chart should have NormalDate X values.
    """

    _attrMap = AttrMap(BASE = XValueAxis,
        bottomAxisLabelSlack = AttrMapValue(isNumber, desc="Fractional amount used to adjust label spacing"),
        niceMonth = AttrMapValue(isBoolean, desc="Flag for displaying months 'nicely'."),
        forceEndDate = AttrMapValue(isBoolean, desc='Flag for enforced displaying of last date value.'),
        forceFirstDate = AttrMapValue(isBoolean, desc='Flag for enforced displaying of first date value.'),
        forceDatesEachYear = AttrMapValue(isListOfDaysAndMonths, desc='List of dates in format "31-Dec",' +
            '"1-Jan".  If present they will always be used for tick marks in the current year, rather ' +
            'than the dates chosen by the automatic algorithm. Hyphen compulsory, case of month optional.'),
        xLabelFormat = AttrMapValue(None, desc="Label format string (e.g. '{mm}/{yy}') or function."),
        dayOfWeekName = AttrMapValue(SequenceOf(isString,emptyOK=0,lo=7,hi=7), desc='Weekday names.'),
        monthName = AttrMapValue(SequenceOf(isString,emptyOK=0,lo=12,hi=12), desc='Month names.'),
        dailyFreq = AttrMapValue(isBoolean, desc='True if we are to assume daily data to be ticked at end of month.'),
        specifiedTickDates = AttrMapValue(NoneOr(SequenceOf(isInstanceOf(normalDate.ND))), desc='Actual tick values to use; no calculations done'),
        )

    _valueClass = normalDate.ND

    def __init__(self,**kw):
        XValueAxis.__init__(self,**kw)

        # some global variables still used...
        self.bottomAxisLabelSlack = 0.1
        self.niceMonth = 1
        self.forceEndDate = 0
        self.forceFirstDate = 0
        self.forceDatesEachYear = []
        self.dailyFreq = 0
        self.xLabelFormat = "{mm}/{yy}"
        self.dayOfWeekName = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.monthName = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                            'August', 'September', 'October', 'November', 'December']
        self.valueSteps = self.specifiedTickDates = None

    def _scalar2ND(self, x):
        "Convert a scalar to a NormalDate value."
        d = self._valueClass()
        d.normalize(x)
        return d

    def _dateFormatter(self, v):
        "Create a formatted label for some value."
        if not isinstance(v,normalDate.NormalDate):
            v = self._scalar2ND(v)
        d, m = normalDate._dayOfWeekName, normalDate._monthName
        try:
            normalDate._dayOfWeekName, normalDate._monthName = self.dayOfWeekName, self.monthName
            return v.formatMS(self.xLabelFormat)
        finally:
            normalDate._dayOfWeekName, normalDate._monthName = d, m

    def _xAxisTicker(self, xVals):
        """Complex stuff...

        Needs explanation...

        Yes please says Andy :-(.  Modified on 19 June 2006 to attempt to allow
        a mode where one can specify recurring days and months.
        """
        axisLength = self._length
        formatter = self._dateFormatter
        labels = self.labels
        fontName, fontSize, leading = labels.fontName, labels.fontSize, labels.leading
        textAnchor, boxAnchor, angle = labels.textAnchor, labels.boxAnchor, labels.angle
        RBL = _textBoxLimits(string.split(formatter(xVals[0]),'\n'),fontName,
                    fontSize,leading or 1.2*fontSize,textAnchor,boxAnchor)
        RBL = _rotatedBoxLimits(RBL[0],RBL[1],RBL[2],RBL[3], angle)
        xLabelW = RBL[1]-RBL[0]
        xLabelH = RBL[3]-RBL[2]
        w = max(xLabelW,labels.width,self.minimumTickSpacing)

        W = w+w*self.bottomAxisLabelSlack
        n = len(xVals)
        ticks = []
        labels = []
        maximumTicks = self.maximumTicks

        def addTick(i, xVals=xVals, formatter=formatter, ticks=ticks, labels=labels):
            ticks.insert(0,xVals[i])
            labels.insert(0,formatter(xVals[i]))

        if self.specifiedTickDates:
            ticks = self.specifiedTickDates[:]
            return ticks,[formatter(d) for d in ticks]

        #AR 20060619 - first we try the approach where the user has explicitly
        #specified the days of year to be ticked.  Other explicit routes may
        #be added.
        if self.forceDatesEachYear:
            forcedPartialDates = map(parseDayAndMonth, self.forceDatesEachYear)
            #generate the list of dates in the range.
            firstDate = xVals[0]
            lastDate = xVals[-1]
            #print 'dates range from %s to %s' % (firstDate, lastDate)
            firstYear = firstDate.year()
            lastYear = lastDate.year()
            ticks = []
            labels = []
            yyyy = firstYear
            #generate all forced dates between the year it starts and the year it
            #ends, adding them if within range.
            while yyyy <= lastYear:
                for (dd, mm) in forcedPartialDates:
                    theDate = normalDate.ND((yyyy, mm, dd))
                    if theDate >= firstDate and theDate <= lastDate:
                        ticks.append(theDate)
                        labels.append(formatter(theDate))
                yyyy += 1

            #first and last may still be forced in.
            if self.forceFirstDate and xVals[0] <> ticks[0]:
                ticks.insert(0, firstDate)
                labels.insert(0,formatter(firstDate))
            if self.forceEndDate and xVals[-1] <> ticks[-1]:
                ticks.append(lastDate)
                labels.append(formatter(lastDate))

            #print 'xVals found on forced dates =', ticks
            return ticks, labels

        #otherwise, we apply the 'magic algorithm...' which looks for nice spacing
        #based on the size and separation of the labels.
        for d in (1,2,3,6,12,24,60,120):
            k = n/d
            if k<=maximumTicks and k*W <= axisLength:
                i = n-1
                if self.niceMonth:
                    j = xVals[-1].month() % (d<=12 and d or 12)
                    if j:
                        if self.forceEndDate: addTick(i)
                        i = i - j

                #weird first date ie not at end of month
                try:
                    wfd = xVals[0].month() == xVals[1].month()
                except:
                    wfd = 0

                while i>=wfd:
                    addTick(i)
                    i = i - d

                if self.forceFirstDate and ticks[0] != xVals[0]:
                    addTick(0)
                    if (axisLength/(ticks[-1]-ticks[0]))*(ticks[1]-ticks[0])<=w:
                        del ticks[1], labels[1]
                if self.forceEndDate and self.niceMonth and j:
                    if (axisLength/(ticks[-1]-ticks[0]))*(ticks[-1]-ticks[-2])<=w:
                        del ticks[-2], labels[-2]
                try:
                    if labels[0] and labels[0]==labels[1]:
                        del ticks[1], labels[1]
                except IndexError:
                    pass

                return ticks, labels

    def _convertXV(self,data):
        '''Convert all XValues to a standard normalDate type'''

        VC = self._valueClass
        for D in data:
            for i in xrange(len(D)):
                x, y = D[i]
                if not isinstance(x,VC):
                    D[i] = (VC(x),y)

    def _getStepsAndLabels(self,xVals):
        if self.dailyFreq:
            xEOM = []
            pm = 0
            px = xVals[0]
            for x in xVals:
                m = x.month()
                if pm!=m:
                    if pm: xEOM.append(px)
                    pm = m
                px = x
            px = xVals[-1]
            if xEOM[-1]!=x: xEOM.append(px)
            steps, labels = self._xAxisTicker(xEOM)
        else:
            steps, labels = self._xAxisTicker(xVals)
        return steps, labels

    def configure(self, data):
        self._convertXV(data)
        from reportlab.lib.set_ops import union
        xVals = reduce(union,map(lambda x: map(lambda dv: dv[0],x),data),[])
        xVals.sort()
        steps,labels = self._getStepsAndLabels(xVals)
        valueMin, valueMax = self.valueMin, self.valueMax
        if valueMin is None: valueMin = xVals[0]
        if valueMax is None: valueMax = xVals[-1]
        self._valueMin, self._valueMax = valueMin, valueMax
        self._tickValues = steps
        self._labelTextFormat = labels

        self._scaleFactor = self._length / float(valueMax - valueMin)
        self._tickValues = steps
        self._configured = 1

class YValueAxis(_YTicks,ValueAxis):
    "Y/value axis"

    _attrMap = AttrMap(BASE=ValueAxis,
        tickLeft = AttrMapValue(isNumber,
            desc='Tick length left of the axis.'),
        tickRight = AttrMapValue(isNumber,
            desc='Tick length right of the axis.'),
        joinAxis = AttrMapValue(None,
            desc='Join both axes if true.'),
        joinAxisMode = AttrMapValue(OneOf(('left', 'right', 'value', 'points', None)),
            desc="Mode used for connecting axis ('left', 'right', 'value', 'points', None)."),
        joinAxisPos = AttrMapValue(isNumberOrNone,
            desc='Position at which to join with other axis.'),
        )

    # Indicate the dimension of the data we're interested in.
    _dataIndex = 1

    def __init__(self):
        ValueAxis.__init__(self)

        self.labels.boxAnchor = 'e'
        self.labels.dx = -5
        self.labels.dy = 0

        self.tickRight = 0
        self.tickLeft = 5

        self.joinAxis = None
        self.joinAxisMode = None
        self.joinAxisPos = None

    def demo(self):
        data = [(10, 20, 30, 42)]
        self.setPosition(100, 10, 80)
        self.configure(data)

        drawing = Drawing(200, 100)
        drawing.add(self)
        return drawing

    def joinToAxis(self, xAxis, mode='left', pos=None):
        "Join with x-axis using some mode."
        _assertXAxis(xAxis)
        if mode == 'left':
            self._x = xAxis._x * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'right':
            self._x = (xAxis._x + xAxis._length) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'value':
            self._x = xAxis.scale(pos) * 1.0
            self._y = xAxis._y * 1.0
        elif mode == 'points':
            self._x = pos * 1.0
            self._y = xAxis._y * 1.0

    def _joinToAxis(self):
        ja = self.joinAxis
        if ja:
            jam = self.joinAxisMode
            jap = self.joinAxisPos
            jta = self.joinToAxis
            if jam in ('left', 'right'):
                jta(ja, mode=jam)
            elif jam in ('value', 'points'):
                jta(ja, mode=jam, pos=jap)

    def makeAxis(self):
        g = Group()
        self._joinToAxis()
        if not self.visibleAxis: return g

        axis = Line(self._x, self._y-self.loLLen, self._x, self._y + self._length+self.hiLLen)
        axis.strokeColor = self.strokeColor
        axis.strokeWidth = self.strokeWidth
        axis.strokeDashArray = self.strokeDashArray
        g.add(axis)
        return g

class AdjYValueAxis(YValueAxis):
    """A Y-axis applying additional rules.

    Depending on the data and some built-in rules, the axis
    may choose to adjust its range and origin.
    """
    _attrMap = AttrMap(BASE = YValueAxis,
        requiredRange = AttrMapValue(isNumberOrNone, desc='Minimum required value range.'),
        leftAxisPercent = AttrMapValue(isBoolean, desc='When true add percent sign to label values.'),
        leftAxisOrigShiftIPC = AttrMapValue(isNumber, desc='Lowest label shift interval ratio.'),
        leftAxisOrigShiftMin = AttrMapValue(isNumber, desc='Minimum amount to shift.'),
        leftAxisSkipLL0 = AttrMapValue(EitherOr((isBoolean,isListOfNumbers)), desc='Skip/Keep lowest tick label when true/false.\nOr skiplist')
        )

    def __init__(self,**kw):
        YValueAxis.__init__(self,**kw)
        self.requiredRange = 30
        self.leftAxisPercent = 1
        self.leftAxisOrigShiftIPC = 0.15
        self.leftAxisOrigShiftMin = 12
        self.leftAxisSkipLL0 = 0
        self.valueSteps = None

    def _rangeAdjust(self):
        "Adjusts the value range of the axis."

        from reportlab.graphics.charts.utils import find_good_grid, ticks
        y_min, y_max = self._valueMin, self._valueMax
        m = self.maximumTicks
        n = filter(lambda x,m=m: x<=m,[4,5,6,7,8,9])
        if not n: n = [m]

        valueStep, requiredRange = self.valueStep, self.requiredRange
        if requiredRange and y_max - y_min < requiredRange:
            y1, y2 = find_good_grid(y_min, y_max,n=n,grid=valueStep)[:2]
            if y2 - y1 < requiredRange:
                ym = (y1+y2)*0.5
                y1 = min(ym-requiredRange*0.5,y_min)
                y2 = max(ym+requiredRange*0.5,y_max)
                if y_min>=100 and y1<100:
                    y2 = y2 + 100 - y1
                    y1 = 100
                elif y_min>=0 and y1<0:
                    y2 = y2 - y1
                    y1 = 0
            self._valueMin, self._valueMax = y1, y2

        T, L = ticks(self._valueMin, self._valueMax, split=1, n=n, percent=self.leftAxisPercent,grid=valueStep)
        abf = self.avoidBoundFrac
        if abf:
            i1 = (T[1]-T[0])
            if not isinstance(abf,_SequenceTypes):
                i0 = i1 = i1*abf
            else:
                i0 = i1*abf[0]
                i1 = i1*abf[1]
            _n = getattr(self,'_cValueMin',T[0])
            _x = getattr(self,'_cValueMax',T[-1])
            if _n - T[0] < i0: self._valueMin = self._valueMin - i0
            if T[-1]-_x < i1: self._valueMax = self._valueMax + i1
            T, L = ticks(self._valueMin, self._valueMax, split=1, n=n, percent=self.leftAxisPercent,grid=valueStep)

        self._valueMin = T[0]
        self._valueMax = T[-1]
        self._tickValues = T
        if self.labelTextFormat is None:
            self._labelTextFormat = L
        else:
            self._labelTextFormat = self.labelTextFormat

        if abs(self._valueMin-100)<1e-6:
            self._calcValueStep()
            vMax, vMin = self._valueMax, self._valueMin
            m = max(self.leftAxisOrigShiftIPC*self._valueStep,
                    (vMax-vMin)*self.leftAxisOrigShiftMin/self._length)
            self._valueMin = self._valueMin - m

        if self.leftAxisSkipLL0:
            if isinstance(self.leftAxisSkipLL0,_SequenceTypes):
                for x in self.leftAxisSkipLL0:
                    try:
                        L[x] = ''
                    except IndexError:
                        pass
            L[0] = ''

# Sample functions.
def sample0a():
    "Sample drawing with one xcat axis and two buckets."

    drawing = Drawing(400, 200)

    data = [(10, 20)]

    xAxis = XCategoryAxis()
    xAxis.setPosition(75, 75, 300)
    xAxis.configure(data)
    xAxis.categoryNames = ['Ying', 'Yang']
    xAxis.labels.boxAnchor = 'n'
    drawing.add(xAxis)
    return drawing

def sample0b():
    "Sample drawing with one xcat axis and one bucket only."

    drawing = Drawing(400, 200)

    data = [(10,)]

    xAxis = XCategoryAxis()
    xAxis.setPosition(75, 75, 300)
    xAxis.configure(data)
    xAxis.categoryNames = ['Ying']
    xAxis.labels.boxAnchor = 'n'
    drawing.add(xAxis)
    return drawing

def sample1():
    "Sample drawing containing two unconnected axes."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XCategoryAxis()
    xAxis.setPosition(75, 75, 300)
    xAxis.configure(data)
    xAxis.categoryNames = ['Beer','Wine','Meat','Cannelloni']
    xAxis.labels.boxAnchor = 'n'
    xAxis.labels[3].dy = -15
    xAxis.labels[3].angle = 30
    xAxis.labels[3].fontName = 'Times-Bold'
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample4a():
    "Sample drawing, xvalue/yvalue axes, y connected at 100 pts to x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'points'
    xAxis.joinAxisPos = 100
    xAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample4b():
    "Sample drawing, xvalue/yvalue axes, y connected at value 35 of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'value'
    xAxis.joinAxisPos = 35
    xAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample4c():
    "Sample drawing, xvalue/yvalue axes, y connected to bottom of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'bottom'
    xAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample4c1():
    "xvalue/yvalue axes, without drawing axis lines/ticks."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    yAxis.visibleAxis = 0
    yAxis.visibleTicks = 0
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'bottom'
    xAxis.configure(data)
    xAxis.visibleAxis = 0
    xAxis.visibleTicks = 0
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample4d():
    "Sample drawing, xvalue/yvalue axes, y connected to top of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'top'
    xAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample5a():
    "Sample drawing, xvalue/yvalue axes, y connected at 100 pts to x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'points'
    yAxis.joinAxisPos = 100
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample5b():
    "Sample drawing, xvalue/yvalue axes, y connected at value 35 of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'value'
    yAxis.joinAxisPos = 35
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample5c():
    "Sample drawing, xvalue/yvalue axes, y connected at right of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'right'
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample5d():
    "Sample drawing, xvalue/yvalue axes, y connected at left of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis.setPosition(50, 50, 300)
    xAxis.configure(data)
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'left'
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample6a():
    "Sample drawing, xcat/yvalue axes, x connected at top of y."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'top'
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample6b():
    "Sample drawing, xcat/yvalue axes, x connected at bottom of y."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'bottom'
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample6c():
    "Sample drawing, xcat/yvalue axes, x connected at 100 pts to y."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'points'
    xAxis.joinAxisPos = 100
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample6d():
    "Sample drawing, xcat/yvalue axes, x connected at value 20 of y."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    yAxis = YValueAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.configure(data)
    xAxis = XCategoryAxis()
    xAxis._length = 300
    xAxis.configure(data)
    xAxis.joinAxis = yAxis
    xAxis.joinAxisMode = 'value'
    xAxis.joinAxisPos = 20
    xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    xAxis.labels.boxAnchor = 'n'
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample7a():
    "Sample drawing, xvalue/ycat axes, y connected at right of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)
    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'right'
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample7b():
    "Sample drawing, xvalue/ycat axes, y connected at left of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)
    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'left'
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample7c():
    "Sample drawing, xvalue/ycat axes, y connected at value 30 of x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)
    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'value'
    yAxis.joinAxisPos = 30
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing

def sample7d():
    "Sample drawing, xvalue/ycat axes, y connected at 200 pts to x."
    drawing = Drawing(400, 200)
    data = [(10, 20, 30, 42)]
    xAxis = XValueAxis()
    xAxis._length = 300
    xAxis.configure(data)
    yAxis = YCategoryAxis()
    yAxis.setPosition(50, 50, 125)
    yAxis.joinAxis = xAxis
    yAxis.joinAxisMode = 'points'
    yAxis.joinAxisPos = 200
    yAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
    yAxis.labels.boxAnchor = 'e'
    yAxis.configure(data)
    drawing.add(xAxis)
    drawing.add(yAxis)
    return drawing
