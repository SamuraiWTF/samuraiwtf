__doc__="""An experimental SVG renderer for the ReportLab graphics framework.

This will create SVG code from the ReportLab Graphics API (RLG).
To read existing SVG code and convert it into ReportLab graphics
objects download the svglib module here:

  http://python.net/~gherman/#svglib
"""

import math, types, sys, os
from operator import getitem

from reportlab.pdfbase.pdfmetrics import stringWidth # for font info
from reportlab.lib.utils import fp_str
from reportlab.lib.colors import black
from reportlab.graphics.renderbase import StateTracker, getStateDelta, Renderer, renderScaledDrawing
from reportlab.graphics.shapes import STATE_DEFAULTS, Path, UserNode
from reportlab.graphics.shapes import * # (only for test0)
from reportlab import rl_config
from reportlab.lib.utils import getStringIO

from xml.dom import getDOMImplementation

### some constants ###

sin = math.sin
cos = math.cos
pi = math.pi

LINE_STYLES = 'stroke-width stroke-linecap stroke fill stroke-dasharray'
TEXT_STYLES = 'font-family font-size'

### top-level user function ###
def drawToString(d, showBoundary=rl_config.showBoundary):
    "Returns a SVG as a string in memory, without touching the disk"
    s = getStringIO()
    drawToFile(d, s, showBoundary=showBoundary)
    return s.getvalue()

def drawToFile(d, fn, showBoundary=rl_config.showBoundary):
    d = renderScaledDrawing(d)
    c = SVGCanvas((d.width, d.height))
    draw(d, c, 0, 0, showBoundary=showBoundary)
    c.save(fn)

def draw(drawing, canvas, x=0, y=0, showBoundary=rl_config.showBoundary):
    """As it says."""
    r = _SVGRenderer()
    r.draw(renderScaledDrawing(drawing), canvas, x, y, showBoundary=showBoundary)

### helper functions ###
def _pointsFromList(L):
    """
    given a list of coordinates [x0, y0, x1, y1....]
    produce a list of points [(x0,y0), (y1,y0),....]
    """

    P=[]
    for i in range(0,len(L), 2):
        P.append((L[i], L[i+1]))

    return P

def transformNode(doc, newTag, node=None, **attrDict):
    """Transform a DOM node into new node and copy selected attributes.

    Creates a new DOM node with tag name 'newTag' for document 'doc'
    and copies selected attributes from an existing 'node' as provided
    in 'attrDict'. The source 'node' can be None. Attribute values will
    be converted to strings.

    E.g.

        n = transformNode(doc, "node1", x="0", y="1")
        -> DOM node for <node1 x="0" y="1"/>

        n = transformNode(doc, "node1", x=0, y=1+1)
        -> DOM node for <node1 x="0" y="2"/>

        n = transformNode(doc, "node1", node0, x="x0", y="x0", zoo=bar())
        -> DOM node for <node1 x="[node0.x0]" y="[node0.y0]" zoo="[bar()]"/>
    """

    newNode = doc.createElement(newTag)
    for newAttr, attr in attrDict.items():
        sattr =  str(attr)
        if not node:
            newNode.setAttribute(newAttr, sattr)
        else:
            attrVal = node.getAttribute(sattr)
            newNode.setAttribute(newAttr, attrVal or sattr)

    return newNode

### classes ###
class SVGCanvas:
    def __init__(self, size=(300,300)):
        self.verbose = 0
        self.width, self.height = self.size = size
        # self.height = size[1]
        self.code = []
        self.style = {}
        self.path = ''
        self._strokeColor = self._fillColor = self._lineWidth = \
            self._font = self._fontSize = self._lineCap = \
            self._lineJoin = self._color = None

        implementation = getDOMImplementation('minidom')
        #Based on official example here http://www.w3.org/TR/SVG10/linking.html want:
        #<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN" 
        #  "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
        #Thus,
        #doctype = implementation.createDocumentType("svg",
        #          "-//W3C//DTD SVG 20010904//EN",
        #          "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd")
        #
        #However, putting that example through http://validator.w3.org/ recommends:
        #<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" 
        #  "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
        #So we'll use that for our SVG 1.0 output.
        doctype = implementation.createDocumentType("svg",
                  "-//W3C//DTD SVG 1.0//EN",
                  "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd")
        self.doc = implementation.createDocument(None,"svg",doctype)
        self.svg = self.doc.documentElement
        self.svg.setAttribute("width", str(size[0]))
        self.svg.setAttribute("height", str(self.height))

        #these suggested by Tim Roberts, as updated by peter@maubp.freeserve.co.uk 
        self.svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        self.svg.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.svg.setAttribute("version", "1.0")
        #self.svg.setAttribute("baseProfile", "full")   #disliked in V 1.0
        title = self.doc.createElement('title')
        text = self.doc.createTextNode('...')
        title.appendChild(text)
        self.svg.appendChild(title)

        desc = self.doc.createElement('desc')
        text = self.doc.createTextNode('...')
        desc.appendChild(text)
        self.svg.appendChild(desc)

        self.setFont(STATE_DEFAULTS['fontName'], STATE_DEFAULTS['fontSize'])
        self.setStrokeColor(STATE_DEFAULTS['strokeColor'])
        self.setLineCap(2)
        self.setLineJoin(0)
        self.setLineWidth(1)

        # Add a rectangular clipping path identical to view area.
        clipPath = transformNode(self.doc, "clipPath", id="clip")
        clipRect = transformNode(self.doc, "rect", x=0, y=0,
            width=self.width, height=self.height)
        clipPath.appendChild(clipRect)
        self.svg.appendChild(clipPath)

        self.groupTree = transformNode(self.doc, "g",
            id="group",
            transform="scale(1,-1) translate(0,-%d)" % self.height,
            style="clip-path: url(#clip)")
        self.svg.appendChild(self.groupTree)
        self.currGroup = self.groupTree

    def save(self, fn=None):
        if isinstance(fn,str):
            f = open(fn, 'w')
        else:
            f = fn

        f.write(self.doc.toprettyxml(indent="     "))

        if f is not fn:
            f.close()

    ### helpers ###
    def NOTUSED_stringWidth(self, s, font=None, fontSize=None):
        """Return the logical width of the string if it were drawn
        in the current font (defaults to self.font).
        """

        font = font or self._font
        fontSize = fontSize or self._fontSize

        return stringWidth(s, font, fontSize)

    def _formatStyle(self, include=''):
        include = include.split()
        keys = self.style.keys()
        if include:
            #2.1-safe version of the line below follows:
            #keys = filter(lambda k: k in include, keys)
            tmp = []
            for word in keys:
                if word in include:
                    tmp.append(word)
            keys = tmp

        items = []
        for k in keys:
            items.append((k, self.style[k]))
        items = map(lambda i: "%s: %s"%(i[0], i[1]), items)

        return '; '.join(items) + ';'

    def _escape(self, s):
        """
        return a copy of string s with special characters in postscript strings
        escaped with backslashes.
        Have not handled characters that are converted normally in python strings
        i.e. \\n -> newline
        """
        return s.replace(chr(0x5C), r'\\' ).replace('(', '\(' ).replace(')', '\)')

    def _genArcCode(self, x1, y1, x2, y2, startAng, extent):
        """Calculate the path for an arc inscribed in rectangle defined
        by (x1,y1),(x2,y2)."""

        return

        #calculate semi-minor and semi-major axes of ellipse
        xScale = abs((x2-x1)/2.0)
        yScale = abs((y2-y1)/2.0)
        #calculate centre of ellipse
        x, y = (x1+x2)/2.0, (y1+y2)/2.0

        codeline = 'matrix currentmatrix %s %s translate %s %s scale 0 0 1 %s %s %s setmatrix'

        if extent >= 0:
            arc='arc'
        else:
            arc='arcn'
        data = (x,y, xScale, yScale, startAng, startAng+extent, arc)

        return codeline % data

    def _fillAndStroke(self, code, clip=0, link_info=None):
        path = transformNode(self.doc, "path",
            d=self.path, style=self._formatStyle(LINE_STYLES))
        if link_info :
            path = self._add_link(path, link_info)
        self.currGroup.appendChild(path)
        self.path = ''


    ### styles ###
    def setLineCap(self, v):
        vals = {0:'butt', 1:'round', 2:'square'}
        if self._lineCap != v:
            self._lineCap = v
            self.style['stroke-linecap'] = vals[v]

    def setLineJoin(self, v):
        vals = {0:'miter', 1:'round', 2:'bevel'}
        if self._lineJoin != v:
            self._lineJoin = v
            self.style['stroke-linecap'] = vals[v]

    def setDash(self, array=[], phase=0):
        """Two notations. Pass two numbers, or an array and phase."""

        if type(array) in (types.IntType, types.FloatType):
            self.style['stroke-dasharray'] = ', '.join(map(str, ([array, phase])))
        elif type(array) in (types.ListType, types.TupleType) and len(array) > 0:
            assert phase >= 0, "phase is a length in user space"
            self.style['stroke-dasharray'] = ', '.join(map(str, (array+[phase])))

    def setStrokeColor(self, color):
        self._strokeColor = color
        self.setColor(color)
        if color == None:
            self.style['stroke'] = 'none'
        else:
            r, g, b = color.red, color.green, color.blue
            self.style['stroke'] = 'rgb(%d%%,%d%%,%d%%)' % (r*100, g*100, b*100)

    def setColor(self, color):
        if self._color != color:
            self._color = color

    def setFillColor(self, color):
        self._fillColor = color
        self.setColor(color)
        if color == None:
            self.style['fill'] = 'none'
        else:
            r, g, b = color.red, color.green, color.blue
            self.style['fill'] = 'rgb(%d%%,%d%%,%d%%)' % (r*100, g*100, b*100)

    def setLineWidth(self, width):
        if width != self._lineWidth:
            self._lineWidth = width
            self.style['stroke-width'] = width

    def setFont(self, font, fontSize):
        if self._font != font or self._fontSize != fontSize:
            self._font, self._fontSize = (font, fontSize)
            self.style['font-family'] = font
            self.style['font-size'] = '%spx' % fontSize

    def _add_link(self, dom_object, link_info) :
        assert isinstance(link_info, dict)
        link = transformNode(self.doc, "a", **link_info)
        link.appendChild(dom_object)
        return link

    ### shapes ###
    def rect(self, x1,y1, x2,y2, rx=8, ry=8, link_info=None):
        "Draw a rectangle between x1,y1 and x2,y2."

        if self.verbose: print "+++ SVGCanvas.rect"

        rect = transformNode(self.doc, "rect",
            x=x1, y=y1, width=x2-x1, height=y2-y1,
            style=self._formatStyle(LINE_STYLES))

        if link_info :
            rect = self._add_link(rect, link_info)

        self.currGroup.appendChild(rect)

    def roundRect(self, x1,y1, x2,y2, rx=8, ry=8, link_info=None):
        """Draw a rounded rectangle between x1,y1 and x2,y2.

        Corners inset as ellipses with x-radius rx and y-radius ry.
        These should have x1<x2, y1<y2, rx>0, and ry>0.
        """

        rect = transformNode(self.doc, "rect",
            x=x1, y=y1, width=x2-x1, height=y2-y1, rx=rx, ry=ry,
            style=self._formatStyle(LINE_STYLES))

        if link_info :
            rect = self._add_link(rect, link_info)

        self.currGroup.appendChild(rect)

    def drawString(self, s, x, y, angle=0, link_info=None):
        if self.verbose: print "+++ SVGCanvas.drawString"

        if self._fillColor != None:
            self.setColor(self._fillColor)
            s = self._escape(s)
            st = self._formatStyle(TEXT_STYLES)
            if angle != 0:
               st = st + " rotate(%f %f %f);" % (angle, x, y)
            st = st + " fill: %s;" % self.style['fill']
            text = transformNode(self.doc, "text",
                x=x, y=y, style=st,
                transform="translate(0,%d) scale(1,-1)" % (2*y))
            content = self.doc.createTextNode(s)
            text.appendChild(content)

            if link_info:
                text = self._add_link(text, link_info)
    
            self.currGroup.appendChild(text)

    def drawCentredString(self, s, x, y, angle=0, text_anchor='middle', link_info=None):
        if self.verbose: print "+++ SVGCanvas.drawCentredString"

        if self._fillColor != None:
            if not text_anchor in ['start', 'inherited']:
                textLen = stringWidth(s,self._font,self._fontSize)
                if text_anchor=='end':
                    x -= textLen
                elif text_anchor=='middle':
                    x -= textLen/2.
                elif text_anchor=='numeric':
                    x -= numericXShift(text_anchor,s,textLen,self._font,self._fontSize)
                else:
                    raise ValueError, 'bad value for text_anchor ' + str(text_anchor)
        self.drawString(x,y,text,angle=angle, link_info=link_info)

    def drawRightString(self, text, x, y, angle=0, link_info=None):
        self.drawCentredString(text,x,y,angle=angle,text_anchor='end', link_info=link_info)

    def comment(self, data):
        "Add a comment."

        comment = self.doc.createComment(data)
        # self.currGroup.appendChild(comment)

    def drawImage(self, image, x1, y1, x2=None, y2=None):
        pass

    def line(self, x1, y1, x2, y2):
        if self._strokeColor != None:
            if 0: # something is wrong with line in my SVG viewer...
                line = transformNode(self.doc, "line",
                    x=x1, y=y1, x2=x2, y2=y2,
                    style=self._formatStyle(LINE_STYLES))
                self.currGroup.appendChild(line)
            path = transformNode(self.doc, "path",
                d="M %f,%f L %f,%f Z" % (x1,y1,x2,y2),
                style=self._formatStyle(LINE_STYLES))
            self.currGroup.appendChild(path)

    def ellipse(self, x1, y1, x2, y2, link_info=None):
        """Draw an orthogonal ellipse inscribed within the rectangle x1,y1,x2,y2.

        These should have x1<x2 and y1<y2.
        """

        ellipse = transformNode(self.doc, "ellipse",
            cx=(x1+x2)/2.0, cy=(y1+y2)/2.0, rx=(x2-x1)/2.0, ry=(y2-y1)/2.0,
            style=self._formatStyle(LINE_STYLES))

        if link_info:
            ellipse = self._add_link(ellipse, link_info)
            
        self.currGroup.appendChild(ellipse)

    def circle(self, xc, yc, r, link_info=None):
        circle = transformNode(self.doc, "circle",
            cx=xc, cy=yc, r=r,
            style=self._formatStyle(LINE_STYLES))

        if link_info:
            circle = self._add_link(circle, link_info)
        
        self.currGroup.appendChild(circle)

    def drawCurve(self, x1, y1, x2, y2, x3, y3, x4, y4, closed=0):
        pass
        return

        codeline = '%s m %s curveto'
        data = (fp_str(x1, y1), fp_str(x2, y2, x3, y3, x4, y4))
        if self._fillColor != None:
            self.setColor(self._fillColor)
            self.code.append((codeline % data) + ' eofill')
        if self._strokeColor != None:
            self.setColor(self._strokeColor)
            self.code.append((codeline % data)
                            + ((closed and ' closepath') or '')
                            + ' stroke')

    def drawArc(self, x1,y1, x2,y2, startAng=0, extent=360, fromcenter=0):
        """Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2.

        Starting at startAng degrees and covering extent degrees. Angles
        start with 0 to the right (+x) and increase counter-clockwise.
        These should have x1<x2 and y1<y2.
        """

        cx, cy = (x1+x2)/2.0, (y1+y2)/2.0
        rx, ry = (x2-x1)/2.0, (y2-y1)/2.0
        mx = rx * cos(startAng*pi/180) + cx
        my = ry * sin(startAng*pi/180) + cy
        ax = rx * cos((startAng+extent)*pi/180) + cx
        ay = ry * sin((startAng+extent)*pi/180) + cy

        str = ''
        if fromcenter:
            str = str + "M %f, %f L %f, %f " % (cx, cy, ax, ay)

        if fromcenter:
            str = str + "A %f, %f %d %d %d %f, %f " % \
              (rx, ry, 0, extent>=180, 0, mx, my)
        else:
            str = str + "M %f, %f A %f, %f %d %d %d %f, %f Z " % \
              (mx, my, rx, ry, 0, extent>=180, 0, mx, my)

        if fromcenter:
            str = str + "L %f, %f Z " % (cx, cy)

        path = transformNode(self.doc, "path",
            d=str, style=self._formatStyle())
        self.currGroup.appendChild(path)

    def polygon(self, points, closed=0, link_info=None):
        assert len(points) >= 2, 'Polygon must have 2 or more points'

        if self._strokeColor != None:
            self.setColor(self._strokeColor)
            pairs = []
            for i in xrange(len(points)):
                pairs.append("%f %f" % (points[i]))
            pts = ', '.join(pairs)
            polyline = transformNode(self.doc, "polygon",
                points=pts, style=self._formatStyle(LINE_STYLES))

            if link_info:
                polyline = self._add_link(polyline, link_info)

            self.currGroup.appendChild(polyline)

        # self._fillAndStroke(polyCode)

    def lines(self, lineList, color=None, width=None):
        # print "### lineList", lineList
        return

        if self._strokeColor != None:
            self._setColor(self._strokeColor)
            codeline = '%s m %s l stroke'
            for line in lineList:
                self.code.append(codeline % (fp_str(line[0]), fp_str(line[1])))

    def polyLine(self, points):
        assert len(points) >= 1, 'Polyline must have 1 or more points'

        if self._strokeColor != None:
            self.setColor(self._strokeColor)
            pairs = []
            for i in xrange(len(points)):
                pairs.append("%f %f" % (points[i]))
            pts = ', '.join(pairs)
            polyline = transformNode(self.doc, "polyline",
                points=pts, style=self._formatStyle(LINE_STYLES))
            self.currGroup.appendChild(polyline)

    ### groups ###
    def startGroup(self):
        if self.verbose: print "+++ begin SVGCanvas.startGroup"
        currGroup, group = self.currGroup, transformNode(self.doc, "g", transform="")
        currGroup.appendChild(group)
        self.currGroup = group
        if self.verbose: print "+++ end SVGCanvas.startGroup"
        return currGroup

    def endGroup(self,currGroup):
        if self.verbose: print "+++ begin SVGCanvas.endGroup"
        self.currGroup = currGroup
        if self.verbose: print "+++ end SVGCanvas.endGroup"

    def transform(self, a, b, c, d, e, f):
        if self.verbose: print "!!! begin SVGCanvas.transform", a, b, c, d, e, f
        tr = self.currGroup.getAttribute("transform")
        t = 'matrix(%f, %f, %f, %f, %f, %f)' % (a,b,c,d,e,f)
        if (a, b, c, d, e, f) != (1, 0, 0, 1, 0, 0):
            self.currGroup.setAttribute("transform", "%s %s" % (tr, t))

    def translate(self, x, y):
        # probably never used
        print "!!! begin SVGCanvas.translate"
        return

        tr = self.currGroup.getAttribute("transform")
        t = 'translate(%f, %f)' % (x, y)
        self.currGroup.setAttribute("transform", "%s %s" % (tr, t))

    def scale(self, x, y):
        # probably never used
        print "!!! begin SVGCanvas.scale"
        return

        tr = self.groups[-1].getAttribute("transform")
        t = 'scale(%f, %f)' % (x, y)
        self.currGroup.setAttribute("transform", "%s %s" % (tr, t))

    ### paths ###
    def moveTo(self, x, y):
        self.path = self.path + 'M %f %f ' % (x, y)

    def lineTo(self, x, y):
        self.path = self.path + 'L %f %f ' % (x, y)

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        self.path = self.path + 'C %f %f %f %f %f %f ' % (x1, y1, x2, y2, x3, y3)

    def closePath(self):
        self.path = self.path + 'Z '

    def saveState(self):
        pass

    def restoreState(self):
        pass

class _SVGRenderer(Renderer):
    """This draws onto an SVG document.
    """

    def __init__(self):
        self._tracker = StateTracker()
        self.verbose = 0

    def drawNode(self, node):
        """This is the recursive method called for each node in the tree.
        """

        if self.verbose: print "### begin _SVGRenderer.drawNode(%r)" % node

        self._canvas.comment('begin node %s'%`node`)
        color = self._canvas._color
        style = self._canvas.style.copy()
        if not (isinstance(node, Path) and node.isClipPath):
            pass # self._canvas.saveState()

        #apply state changes
        deltas = getStateDelta(node)
        self._tracker.push(deltas)
        self.applyStateChanges(deltas, {})

        #draw the object, or recurse
        self.drawNodeDispatcher(node)

        rDeltas = self._tracker.pop()
        if not (isinstance(node, Path) and node.isClipPath):
            pass #self._canvas.restoreState()
        self._canvas.comment('end node %s'%`node`)
        self._canvas._color = color

        #restore things we might have lost (without actually doing anything).
        for k, v in rDeltas.items():
            if self._restores.has_key(k):
                setattr(self._canvas,self._restores[k],v)
        self._canvas.style = style

        if self.verbose: print "### end _SVGRenderer.drawNode(%r)" % node

    _restores = {'strokeColor':'_strokeColor','strokeWidth': '_lineWidth','strokeLineCap':'_lineCap',
                'strokeLineJoin':'_lineJoin','fillColor':'_fillColor','fontName':'_font',
                'fontSize':'_fontSize'}

    def _get_link_info_dict(self, obj):
        #We do not want None or False as the link, even if it is the
        #attribute's value - use the empty string instead.
        url = getattr(obj, "hrefURL", "") or ""
        title = getattr(obj, "hrefTitle", "") or ""
        if url :
            #Is it valid to have a link with no href?  The XML requires
            #the xlink:href to be present, but you might just want a
            #tool tip shown (via the xlink:title attribute).  Note that
            #giving an href of "" is equivalent to "the current page"
            #(a relative link saying go nowhere).
            return {"xlink:href":url, "xlink:title":title, "target":"_top"}
            #Currently of all the mainstream browsers I have tested, only Safari/webkit
            #will show  SVG images embedded in HTML using a simple <img src="..." /> tag.
            #However, the links don't work (Safari 3.2.1 on the Mac).
            #
            #Therefore I use the following, which also works for Firefox, Opera, and
            #IE 6.0 with Adobe SVG Viewer 6 beta:
            #<object data="..." type="image/svg+xml" width="430" height="150" class="img">
            #
            #Once displayed, Firefox and Safari treat the SVG like a frame, and
            #by default clicking on links acts "in frame" and replaces the image.
            #Opera does what I expect, and replaces the whole page with the link.
            #
            #Therefore I use target="_top" to force the links to replace the whole page.
            #This now works as expected on Safari 3.2.1, Firefox 3.0.6, Opera 9.20. 
            #Perhaps the target attribute should be an option, perhaps defaulting to
            #"_top" as used here?
        else :
            return None

    def drawGroup(self, group):
        if self.verbose: print "### begin _SVGRenderer.drawGroup"

        currGroup = self._canvas.startGroup()
        a, b, c, d, e, f = self._tracker.getState()['transform']
        for childNode in group.getContents():
            if isinstance(childNode, UserNode):
                node2 = childNode.provideNode()
            else:
                node2 = childNode
            self.drawNode(node2)
        self._canvas.transform(a, b, c, d, e, f)
        self._canvas.endGroup(currGroup)

        if self.verbose: print "### end _SVGRenderer.drawGroup"

    def drawRect(self, rect):
        link_info = self._get_link_info_dict(rect)
        if rect.rx == rect.ry == 0:
            #plain old rectangle
            self._canvas.rect(
                    rect.x, rect.y,
                    rect.x+rect.width, rect.y+rect.height, link_info=link_info)
        else:
            #cheat and assume ry = rx; better to generalize
            #pdfgen roundRect function.  TODO
            self._canvas.roundRect(
                    rect.x, rect.y,
                    rect.x+rect.width, rect.y+rect.height,
                    rect.rx, rect.ry,
                    link_info=link_info)

    def drawString(self, stringObj):
        if self._canvas._fillColor:
            S = self._tracker.getState()
            text_anchor, x, y, text = S['textAnchor'], stringObj.x, stringObj.y, stringObj.text
            if not text_anchor in ('start', 'inherited'):
                font, fontSize = S['fontName'], S['fontSize']
                textLen = stringWidth(text, font,fontSize)
                if text_anchor=='end':
                    x -= textLen
                elif text_anchor=='middle':
                    x -= textLen/2
                elif text_anchor=='numeric':
                    x -= numericXShift(text_anchor,text,textLen,font,fontSize)
                else:
                    raise ValueError, 'bad value for text_anchor ' + str(text_anchor)
            self._canvas.drawString(text,x,y,link_info=self._get_link_info_dict(stringObj))

    def drawLine(self, line):
        if self._canvas._strokeColor:
            self._canvas.line(line.x1, line.y1, line.x2, line.y2)

    def drawCircle(self, circle):
        self._canvas.circle( circle.cx, circle.cy, circle.r, link_info=self._get_link_info_dict(circle))

    def drawWedge(self, wedge):
        centerx, centery, radius, startangledegrees, endangledegrees = \
         wedge.centerx, wedge.centery, wedge.radius, wedge.startangledegrees, wedge.endangledegrees
        yradius = wedge.yradius or wedge.radius
        (x1, y1) = (centerx-radius, centery-yradius)
        (x2, y2) = (centerx+radius, centery+yradius)
        extent = endangledegrees - startangledegrees
        self._canvas.drawArc(x1, y1, x2, y2, startangledegrees, extent, fromcenter=1)

    def drawPolyLine(self, p):
        if self._canvas._strokeColor:
            self._canvas.polyLine(_pointsFromList(p.points))

    def drawEllipse(self, ellipse):
        #need to convert to pdfgen's bounding box representation
        x1 = ellipse.cx - ellipse.rx
        x2 = ellipse.cx + ellipse.rx
        y1 = ellipse.cy - ellipse.ry
        y2 = ellipse.cy + ellipse.ry
        self._canvas.ellipse(x1,y1,x2,y2, link_info=self._get_link_info_dict(ellipse))

    def drawPolygon(self, p):
        self._canvas.polygon(_pointsFromList(p.points), closed=1, link_info=self._get_link_info_dict(p))

    def drawPath(self, path):
        # print "### drawPath", path.points
        from reportlab.graphics.shapes import _renderPath
        c = self._canvas
        drawFuncs = (c.moveTo, c.lineTo, c.curveTo, c.closePath)
        isClosed = _renderPath(path, drawFuncs)
        if isClosed:
            #Only try and add links to closed paths...
            link_info = self._get_link_info_dict(path)
        else :
            c._fillColor = None
            link_info = None
        c._fillAndStroke([], clip=path.isClipPath, link_info=link_info)

    def applyStateChanges(self, delta, newState):
        """This takes a set of states, and outputs the operators
        needed to set those properties"""

        for key, value in delta.items():
            if key == 'transform':
                pass
                #self._canvas.transform(value[0], value[1], value[2], value[3], value[4], value[5])
            elif key == 'strokeColor':
                self._canvas.setStrokeColor(value)
            elif key == 'strokeWidth':
                self._canvas.setLineWidth(value)
            elif key == 'strokeLineCap':  #0,1,2
                self._canvas.setLineCap(value)
            elif key == 'strokeLineJoin':
                self._canvas.setLineJoin(value)
            elif key == 'strokeDashArray':
                if value:
                    self._canvas.setDash(value)
                else:
                    self._canvas.setDash()
            elif key == 'fillColor':
                self._canvas.setFillColor(value)
            elif key in ['fontSize', 'fontName']:
                fontname = delta.get('fontName', self._canvas._font)
                fontsize = delta.get('fontSize', self._canvas._fontSize)
                self._canvas.setFont(fontname, fontsize)

def test0(outdir='svgout'):
    # print all drawings and their doc strings from the test
    # file
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    #grab all drawings from the test module
    from reportlab.graphics import testshapes
    drawings = []

    for funcname in dir(testshapes):
        #if funcname[0:11] == 'getDrawing2':
        #    print 'hacked to only show drawing 2'
        if funcname[0:10] == 'getDrawing':
            drawing = eval('testshapes.' + funcname + '()')
            docstring = eval('testshapes.' + funcname + '.__doc__')
            drawings.append((drawing, docstring))

    # return

    i = 0
    for (d, docstring) in drawings:
        filename = outdir + os.sep + 'renderSVG_%d.svg' % i
        drawToFile(d, filename)
        # print 'saved', filename
        i += 1

def test1():
    from reportlab.graphics.testshapes import getDrawing01
    d = getDrawing01()
    drawToFile(d, "svgout/test.svg")

def test2():
    from reportlab.lib.corp import RL_CorpLogo
    from reportlab.graphics.shapes import Drawing

    rl = RL_CorpLogo()
    d = Drawing(rl.width,rl.height)
    d.add(rl)
    drawToFile(d, "svgout/corplogo.svg")

if __name__=='__main__':
    test0()
    test1()
    test2()
