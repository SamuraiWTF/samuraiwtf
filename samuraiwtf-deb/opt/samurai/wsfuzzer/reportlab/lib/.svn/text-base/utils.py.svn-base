#Copyright ReportLab Europe Ltd. 2000-2006
#see license.txt for license details
# $URI:$
__version__=''' $Id: utils.py 3624 2009-12-18 10:52:19Z rgbecker $ '''
__doc__='''Gazillions of miscellaneous internal utility functions'''

import os, sys, imp, time
try:
    from hashlib import md5
except:
    from md5 import md5
from reportlab.lib.logger import warnOnce
from rltempfile import get_rl_tempfile, get_rl_tempdir, _rl_getuid

def isSeqType(v,_st=(tuple,list)):
    return isinstance(v,_st)

if sys.hexversion<0x2030000:
    True = 1
    False = 0

if sys.hexversion >= 0x02000000:
    def _digester(s):
        return md5(s).hexdigest()
else:
    # hexdigest not available in 1.5
    def _digester(s):
        return join(map(lambda x : "%02x" % ord(x), md5(s).digest()), '')

def _findFiles(dirList,ext='.ttf'):
    from os.path import isfile, isdir, join as path_join
    from os import listdir
    ext = ext.lower()
    R = []
    A = R.append
    for D in dirList:
        if not isdir(D): continue
        for fn in listdir(D):
            fn = path_join(D,fn)
            if isfile(fn) and (not ext or fn.lower().endswith(ext)): A(fn)
    return R

try:
    _UserDict = dict
except:
    from UserDict import UserDict as _UserDict

class CIDict(_UserDict):
    def __init__(self,*a,**kw):
        map(self.update, a)
        self.update(kw)

    def update(self,D):
        for k,v in D.items(): self[k] = v

    def __setitem__(self,k,v):
        try:
            k = k.lower()
        except:
            pass
        _UserDict.__setitem__(self,k,v)

    def __getitem__(self,k):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.__getitem__(self,k)

    def __delitem__(self,k):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.__delitem__(self,k)

    def get(self,k,dv=None):
        try:
            return self[k]
        except KeyError:
            return dv

    def has_key(self,k):
        try:
            self[k]
            return True
        except:
            return False

    def pop(self,k,*a):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.pop(*((self,k)+a))

    def setdefault(self,k,*a):
        try:
            k = k.lower()
        except:
            pass
        return _UserDict.setdefault(*((self,k)+a))

if os.name == 'mac':
    #with the Mac, we need to tag the file in a special
    #way so the system knows it is a PDF file.
    #This supplied by Joe Strout
    import macfs, macostools
    _KNOWN_MAC_EXT = {
        'BMP' : ('ogle','BMP '),
        'EPS' : ('ogle','EPSF'),
        'EPSF': ('ogle','EPSF'),
        'GIF' : ('ogle','GIFf'),
        'JPG' : ('ogle','JPEG'),
        'JPEG': ('ogle','JPEG'),
        'PCT' : ('ttxt','PICT'),
        'PICT': ('ttxt','PICT'),
        'PNG' : ('ogle','PNGf'),
        'PPM' : ('ogle','.PPM'),
        'TIF' : ('ogle','TIFF'),
        'TIFF': ('ogle','TIFF'),
        'PDF' : ('CARO','PDF '),
        'HTML': ('MSIE','TEXT'),
        }
    def markfilename(filename,creatorcode=None,filetype=None,ext='PDF'):
        try:
            if creatorcode is None or filetype is None and ext is not None:
                try:
                    creatorcode, filetype = _KNOWN_MAC_EXT[ext.upper()]
                except:
                    return
            macfs.FSSpec(filename).SetCreatorType(creatorcode,filetype)
            macostools.touched(filename)
        except:
            pass
else:
    def markfilename(filename,creatorcode=None,filetype=None):
        pass

import reportlab
__RL_DIR=os.path.dirname(reportlab.__file__)    #possibly relative
_RL_DIR=os.path.isabs(__RL_DIR) and __RL_DIR or os.path.abspath(__RL_DIR)
del reportlab

#Attempt to detect if this copy of reportlab is running in a
#file system (as opposed to mostly running in a zip or McMillan
#archive or Jar file).  This is used by test cases, so that
#we can write test cases that don't get activated in a compiled
try:
    __file__
except:
    __file__ = sys.argv[0]
import glob, fnmatch
try:
    _isFSD = not __loader__
    _archive = os.path.normcase(os.path.normpath(__loader__.archive))
    _archivepfx = _archive + os.sep
    _archivedir = os.path.dirname(_archive)
    _archivedirpfx = _archivedir + os.sep
    _archivepfxlen = len(_archivepfx)
    _archivedirpfxlen = len(_archivedirpfx)
    def __startswith_rl(fn,
                    _archivepfx=_archivepfx,
                    _archivedirpfx=_archivedirpfx,
                    _archive=_archive,
                    _archivedir=_archivedir,
                    os_path_normpath=os.path.normpath,
                    os_path_normcase=os.path.normcase,
                    os_getcwd=os.getcwd,
                    os_sep=os.sep,
                    os_sep_len = len(os.sep)):
        '''if the name starts with a known prefix strip it off'''
        fn = os_path_normpath(fn.replace('/',os_sep))
        nfn = os_path_normcase(fn)
        if nfn in (_archivedir,_archive): return 1,''
        if nfn.startswith(_archivepfx): return 1,fn[_archivepfxlen:]
        if nfn.startswith(_archivedirpfx): return 1,fn[_archivedirpfxlen:]
        cwd = os_path_normcase(os_getcwd())
        n = len(cwd)
        if nfn.startswith(cwd):
            if fn[n:].startswith(os_sep): return 1, fn[n+os_sep_len:]
            if n==len(fn): return 1,''
        return not os.path.isabs(fn),fn

    def _startswith_rl(fn):
        return __startswith_rl(fn)[1]

    def rl_glob(pattern,glob=glob.glob,fnmatch=fnmatch.fnmatch, _RL_DIR=_RL_DIR,pjoin=os.path.join):
        c, pfn = __startswith_rl(pattern)
        r = glob(pfn)
        if c or r==[]:
            r += map(lambda x,D=_archivepfx,pjoin=pjoin: pjoin(_archivepfx,x),filter(lambda x,pfn=pfn,fnmatch=fnmatch: fnmatch(x,pfn),__loader__._files.keys()))
        return r
except:
    _isFSD = os.path.isfile(__file__)   #slight risk of wrong path
    __loader__ = None
    def _startswith_rl(fn):
        return fn
    def rl_glob(pattern,glob=glob.glob):
        return glob(pattern)
del glob, fnmatch
_isFSSD = _isFSD and os.path.isfile(os.path.splitext(__file__)[0] +'.py')

def isFileSystemDistro():
    '''return truth if a file system distribution'''
    return _isFSD

def isCompactDistro():
    '''return truth if not a file system distribution'''
    return not _isFSD

def isSourceDistro():
    '''return truth if a source file system distribution'''
    return _isFSSD

try:
    #raise ImportError
    ### NOTE!  FP_STR SHOULD PROBABLY ALWAYS DO A PYTHON STR() CONVERSION ON ARGS
    ### IN CASE THEY ARE "LAZY OBJECTS".  ACCELLERATOR DOESN'T DO THIS (YET)
    try:
        from _rl_accel import fp_str                # in case of builtin version
    except ImportError:
        from reportlab.lib._rl_accel import fp_str  # specific
except ImportError:
    from math import log
    _log_10 = lambda x,log=log,_log_e_10=log(10.0): log(x)/_log_e_10
    _fp_fmts = "%.0f", "%.1f", "%.2f", "%.3f", "%.4f", "%.5f", "%.6f"
    import re
    _tz_re = re.compile('0+$')
    del re
    def fp_str(*a):
        '''convert separate arguments (or single sequence arg) into space separated numeric strings'''
        if len(a)==1 and isSeqType(a[0]): a = a[0]
        s = []
        A = s.append
        for i in a:
            sa =abs(i)
            if sa<=1e-7: A('0')
            else:
                l = sa<=1 and 6 or min(max(0,(6-int(_log_10(sa)))),6)
                n = _fp_fmts[l]%i
                if l:
                    n = _tz_re.sub('',n)
                    try:
                        if n[-1]=='.': n = n[:-1]
                    except:
                        print i, n
                        raise
                A((n[0]!='0' or len(n)==1) and n or n[1:])
        return ' '.join(s)

#hack test for comma users
if ',' in fp_str(0.25):
    _FP_STR = fp_str
    def fp_str(*a):
        return _FP_STR(*a).replace(',','.')

def recursiveImport(modulename, baseDir=None, noCWD=0, debug=0):
    """Dynamically imports possible packagized module, or raises ImportError"""
    normalize = lambda x: os.path.normcase(os.path.abspath(os.path.normpath(x)))
    path = map(normalize,sys.path)
    if baseDir:
        if not isSeqType(baseDir):
            tp = [baseDir]
        else:
            tp = filter(None,list(baseDir))
        for p in tp:
            p = normalize(p)
            if p not in path: path.insert(0,p)

    if noCWD:
        for p in ('','.',normalize('.')):
            while p in path:
                if debug: print 'removed "%s" from path' % p
                path.remove(p)
    elif '.' not in path:
            path.insert(0,'.')

    if debug:
        import pprint
        pp = pprint.pprint
        print 'path=',
        pp(path)

    #make import errors a bit more informative
    opath = sys.path
    try:
        sys.path = path
        exec 'import %s\nm = %s\n' % (modulename,modulename) in locals()
        sys.path = opath
        return m
    except ImportError:
        sys.path = opath
        msg = "recursiveimport(%s,baseDir=%s) failed" % (modulename,baseDir)
        if baseDir:
            msg = msg + " under paths '%s'" % `path`
        raise ImportError, msg

def recursiveGetAttr(obj, name):
    "Can call down into e.g. object1.object2[4].attr"
    return eval(name, obj.__dict__)

def recursiveSetAttr(obj, name, value):
    "Can call down into e.g. object1.object2[4].attr = value"
    #get the thing above last.
    tokens = name.split('.')
    if len(tokens) == 1:
        setattr(obj, name, value)
    else:
        most = '.'.join(tokens[:-1])
        last = tokens[-1]
        parent = recursiveGetAttr(obj, most)
        setattr(parent, last, value)

def import_zlib():
    try:
        import zlib
    except ImportError:
        zlib = None
        from reportlab.rl_config import ZLIB_WARNINGS
        if ZLIB_WARNINGS: warnOnce('zlib not available')
    return zlib

# Image Capability Detection.  Set a flag haveImages
# to tell us if either PIL or Java imaging libraries present.
# define PIL_Image as either None, or an alias for the PIL.Image
# module, as there are 2 ways to import it
if sys.platform[0:4] == 'java':
    try:
        import javax.imageio
        import java.awt.image
        haveImages = 1
    except:
        haveImages = 0
else:
    try:
        from PIL import Image
    except ImportError:
        try:
            import Image
        except ImportError:
            Image = None
    haveImages = Image is not None

try:
    from cStringIO import StringIO as __StringIO
except ImportError:
    from StringIO import StringIO as __StringIO
def getStringIO(buf=None):
    '''unified StringIO instance interface'''
    return buf is not None and __StringIO(buf) or __StringIO()
_StringIOKlass=__StringIO().__class__

class ArgvDictValue:
    '''A type to allow clients of getArgvDict to specify a conversion function'''
    def __init__(self,value,func):
        self.value = value
        self.func = func

def getArgvDict(**kw):
    ''' Builds a dictionary from its keyword arguments with overrides from sys.argv.
        Attempts to be smart about conversions, but the value can be an instance
        of ArgDictValue to allow specifying a conversion function.
    '''
    def handleValue(v,av,func):
        if func:
            v = func(av)
        else:
            if isinstance(v,basestring):
                if isinstance(v,unicode): v = v.encode('utf8')
                v = av
            elif isinstance(v,float):
                v = float(av)
            elif isinstance(v,int):
                v = int(av)
            elif isinstance(v,list):
                v = list(eval(av))
            elif isinstance(v,tuple):
                v = tuple(eval(av))
            else:
                raise TypeError("Can't convert string %r to %s" % (av,type(v)))
        return v

    A = sys.argv[1:]
    R = {}
    for k, v in kw.items():
        if isinstance(v,ArgvDictValue):
            v, func = v.value, v.func
        else:
            func = None
        handled = 0
        ke = k+'='
        for a in A:
            if a.find(ke)==0:
                av = a[len(ke):]
                A.remove(a)
                R[k] = handleValue(v,av,func)
                handled = 1
                break

        if not handled: R[k] = handleValue(v,v,func)

    return R

def getHyphenater(hDict=None):
    try:
        from reportlab.lib.pyHnj import Hyphen
        if hDict is None: hDict=os.path.join(os.path.dirname(__file__),'hyphen.mashed')
        return Hyphen(hDict)
    except ImportError, errMsg:
        if str(errMsg)!='No module named pyHnj': raise
        return None

def _className(self):
    '''Return a shortened class name'''
    try:
        name = self.__class__.__name__
        i=name.rfind('.')
        if i>=0: return name[i+1:]
        return name
    except AttributeError:
        return str(self)

def open_for_read_by_name(name,mode='b'):
    if 'r' not in mode: mode = 'r'+mode
    try:
        return open(name,mode)
    except IOError:
        if _isFSD or __loader__ is None: raise
        #we have a __loader__, perhaps the filename starts with
        #the dirname(reportlab.__file__) or is relative
        name = _startswith_rl(name)
        s = __loader__.get_data(name)
        if 'b' not in mode and os.linesep!='\n': s = s.replace(os.linesep,'\n')
        return getStringIO(s)

import urllib
def open_for_read(name,mode='b', urlopen=urllib.urlopen):
    '''attempt to open a file or URL for reading'''
    if hasattr(name,'read'): return name
    try:
        return open_for_read_by_name(name,mode)
    except:
        try:
            return getStringIO(urlopen(name).read())
        except:
            raise IOError('Cannot open resource "%s"' % name)
del urllib

def open_and_read(name,mode='b'):
    return open_for_read(name,mode).read()

def open_and_readlines(name,mode='t'):
    return open_and_read(name,mode).split('\n')

def rl_isfile(fn,os_path_isfile=os.path.isfile):
    if hasattr(fn,'read'): return True
    if os_path_isfile(fn): return True
    if _isFSD or __loader__ is None: return False
    fn = _startswith_rl(fn)
    return fn in __loader__._files.keys()

def rl_isdir(pn,os_path_isdir=os.path.isdir,os_path_normpath=os.path.normpath):
    if os_path_isdir(pn): return True
    if _isFSD or __loader__ is None: return False
    pn = _startswith_rl(os_path_normpath(pn))
    if not pn.endswith(os.sep): pn += os.sep
    return len(filter(lambda x,pn=pn: x.startswith(pn),__loader__._files.keys()))>0

def rl_listdir(pn,os_path_isdir=os.path.isdir,os_path_normpath=os.path.normpath,os_listdir=os.listdir):
    if os_path_isdir(pn) or _isFSD or __loader__ is None: return os_listdir(pn)
    pn = _startswith_rl(os_path_normpath(pn))
    if not pn.endswith(os.sep): pn += os.sep
    return [x[len(pn):] for x in __loader__._files.keys() if x.startswith(pn)]

def rl_getmtime(pn,os_path_isfile=os.path.isfile,os_path_normpath=os.path.normpath,os_path_getmtime=os.path.getmtime,time_mktime=time.mktime):
    if os_path_isfile(pn) or _isFSD or __loader__ is None: return os_path_getmtime(pn)
    p = _startswith_rl(os_path_normpath(pn))
    try:
        e = __loader__._files[p]
    except KeyError:
        return os_path_getmtime(pn)
    s = e[5]
    d = e[6]
    y = ((d>>9)&0x7f)+1980
    m = (d>>5)&0xf
    d &= 0x1f
    h = (s>>11)&0xf
    m = (s>>5)&0x3f
    s &= 0x1f
    s <<= 1
    return time_mktime((y,m,d,h,m,s,0,0,0))

def rl_get_module(name,dir):
    if sys.modules.has_key(name):
        om = sys.modules[name]
        del sys.modules[name]
    else:
        om = None
    try:
        f = None
        try:
            f, p, desc= imp.find_module(name,[dir])
            return imp.load_module(name,f,p,desc)
        except:
            if isCompactDistro():
                #attempt a load from inside the zip archive
                import zipimport
                dir = _startswith_rl(dir)
                dir = (dir=='.' or not dir) and _archive or os.path.join(_archive,dir.replace('/',os.sep))
                zi = zipimport.zipimporter(dir)
                return zi.load_module(name)
            raise ImportError('%s[%s]' % (name,dir))
    finally:
        if om: sys.modules[name] = om
        del om
        if f: f.close()

def _isPILImage(im):
    try:
        return isinstance(im,Image.Image)
    except ImportError:
        return 0

class ImageReader(object):
    "Wraps up either PIL or Java to get data from bitmaps"
    _cache={}
    def __init__(self, fileName):
        if isinstance(fileName,ImageReader):
            self.__dict__ = fileName.__dict__   #borgize
            return
        #start wih lots of null private fields, to be populated by
        #the relevant engine.
        self.fileName = fileName
        self._image = None
        self._width = None
        self._height = None
        self._transparent = None
        self._data = None
        if _isPILImage(fileName):
            self._image = fileName
            self.fp = getattr(fileName,'fp',None)
            try:
                self.fileName = self._image.fileName
            except AttributeError:
                self.fileName = 'PILIMAGE_%d' % id(self)
        else:
            try:
                from reportlab.rl_config import imageReaderFlags
                self.fp = open_for_read(fileName,'b')
                if isinstance(self.fp,_StringIOKlass):  imageReaderFlags=0 #avoid messing with already internal files
                if imageReaderFlags>0:  #interning
                    data = self.fp.read()
                    if imageReaderFlags&2:  #autoclose
                        try:
                            self.fp.close()
                        except:
                            pass
                    if imageReaderFlags&4:  #cache the data
                        if not self._cache:
                            from rl_config import register_reset
                            register_reset(self._cache.clear)
                        data=self._cache.setdefault(md5(data).digest(),data)
                    self.fp=getStringIO(data)
                elif imageReaderFlags==-1 and isinstance(fileName,(str,unicode)):
                    #try Ralf Schmitt's re-opening technique of avoiding too many open files
                    self.fp.close()
                    del self.fp #will become a property in the next statement
                    self.__class__=LazyImageReader
                if haveImages:
                    #detect which library we are using and open the image
                    if not self._image:
                        self._image = self._read_image(self.fp)
                    if getattr(self._image,'format',None)=='JPEG': self.jpeg_fh = self._jpeg_fh
                else:
                    from reportlab.pdfbase.pdfutils import readJPEGInfo
                    try:
                        self._width,self._height,c=readJPEGInfo(self.fp)
                    except:
                        raise RuntimeError('Imaging Library not available, unable to import bitmaps only jpegs')
                    self.jpeg_fh = self._jpeg_fh
                    self._data = self.fp.read()
                    self._dataA=None
                    self.fp.seek(0)
            except:
                et,ev,tb = sys.exc_info()
                if hasattr(ev,'args'):
                    a = str(ev.args[-1])+(' fileName=%r'%fileName)
                    ev.args= ev.args[:-1]+(a,)
                    raise et,ev,tb
                else:
                    raise

    def _read_image(self,fp):
        if sys.platform[0:4] == 'java':
            from javax.imageio import ImageIO
            return ImageIO.read(fp)
        else:
            return Image.open(fp)

    def _jpeg_fh(self):
        fp = self.fp
        fp.seek(0)
        return fp

    def jpeg_fh(self):
        return None

    def getSize(self):
        if (self._width is None or self._height is None):
            if sys.platform[0:4] == 'java':
                self._width = self._image.getWidth()
                self._height = self._image.getHeight()
            else:
                self._width, self._height = self._image.size
        return (self._width, self._height)

    def getRGBData(self):
        "Return byte array of RGB data as string"
        if self._data is None:
            self._dataA = None
            if sys.platform[0:4] == 'java':
                import jarray
                from java.awt.image import PixelGrabber
                width, height = self.getSize()
                buffer = jarray.zeros(width*height, 'i')
                pg = PixelGrabber(self._image, 0,0,width,height,buffer,0,width)
                pg.grabPixels()
                # there must be a way to do this with a cast not a byte-level loop,
                # I just haven't found it yet...
                pixels = []
                a = pixels.append
                for i in range(len(buffer)):
                    rgb = buffer[i]
                    a(chr((rgb>>16)&0xff))
                    a(chr((rgb>>8)&0xff))
                    a(chr(rgb&0xff))
                self._data = ''.join(pixels)
                self.mode = 'RGB'
            else:
                im = self._image
                mode = self.mode = im.mode
                if mode=='RGBA':
                    if Image.VERSION.startswith('1.1.7'): im.load()
                    self._dataA = ImageReader(im.split()[3])
                    im = im.convert('RGB')
                    self.mode = 'RGB'
                elif mode not in ('L','RGB','CMYK'):
                    im = im.convert('RGB')
                    self.mode = 'RGB'
                self._data = im.tostring()
        return self._data

    def getImageData(self):
        width, height = self.getSize()
        return width, height, self.getRGBData()

    def getTransparent(self):
        if sys.platform[0:4] == 'java':
            return None
        else:
            if self._image.info.has_key("transparency"):
                transparency = self._image.info["transparency"] * 3
                palette = self._image.palette
                try:
                    palette = palette.palette
                except:
                    palette = palette.data
                return map(ord, palette[transparency:transparency+3])
            else:
                return None

class LazyImageReader(ImageReader): 
    def fp(self): 
        return open_for_read(self.fileName, 'b') 
    fp=property(fp) 

    def _image(self):
        return self._read_image(self.fp)
    _image=property(_image) 

def getImageData(imageFileName):
    "Get width, height and RGB pixels from image file.  Wraps Java/PIL"
    try:
        return imageFileName.getImageData()
    except AttributeError:
        return ImageReader(imageFileName).getImageData()

class DebugMemo:
    '''Intended as a simple report back encapsulator

    Typical usages:
        
    1. To record error data::
        
        dbg = DebugMemo(fn='dbgmemo.dbg',myVar=value)
        dbg.add(anotherPayload='aaaa',andagain='bbb')
        dbg.dump()

    2. To show the recorded info::
        
        dbg = DebugMemo(fn='dbgmemo.dbg',mode='r')
        dbg.load()
        dbg.show()

    3. To re-use recorded information::
        
        dbg = DebugMemo(fn='dbgmemo.dbg',mode='r')
            dbg.load()
        myTestFunc(dbg.payload('myVar'),dbg.payload('andagain'))

    In addition to the payload variables the dump records many useful bits
    of information which are also printed in the show() method.
    '''
    def __init__(self,fn='rl_dbgmemo.dbg',mode='w',getScript=1,modules=(),capture_traceback=1, stdout=None, **kw):
        import time, socket
        self.fn = fn
        if not stdout: 
            self.stdout = sys.stdout
        else:
            if hasattr(stdout,'write'):
                self.stdout = stdout
            else:
                self.stdout = open(stdout,'w')
        if mode!='w': return
        self.store = store = {}
        if capture_traceback and sys.exc_info() != (None,None,None):
            import traceback
            s = getStringIO()
            traceback.print_exc(None,s)
            store['__traceback'] = s.getvalue()
        cwd=os.getcwd()
        lcwd = os.listdir(cwd)
        pcwd = os.path.dirname(cwd)
        lpcwd = pcwd and os.listdir(pcwd) or '???'
        exed = os.path.abspath(os.path.dirname(sys.argv[0]))
        project_version='???'
        md=None
        try:
            import marshal
            md=marshal.loads(__loader__.get_data('meta_data.mar'))
            project_version=md['project_version']
        except:
            pass
        env = os.environ
        K=env.keys()
        K.sort()
        store.update({  'gmt': time.asctime(time.gmtime(time.time())),
                        'platform': sys.platform,
                        'version': sys.version,
                        'hexversion': hex(sys.hexversion),
                        'executable': sys.executable,
                        'exec_prefix': sys.exec_prefix,
                        'prefix': sys.prefix,
                        'path': sys.path,
                        'argv': sys.argv,
                        'cwd': cwd,
                        'hostname': socket.gethostname(),
                        'lcwd': lcwd,
                        'lpcwd': lpcwd,
                        'byteorder': sys.byteorder,
                        'maxint': sys.maxint,
                        'maxint': getattr(sys,'maxunicode','????'),
                        'api_version': getattr(sys,'api_version','????'),
                        'version_info': getattr(sys,'version_info','????'),
                        'winver': getattr(sys,'winver','????'),
                        'environment': '\n\t\t\t'.join(['']+['%s=%r' % (k,env[k]) for k in K]),
                        '__loader__': repr(__loader__),
                        'project_meta_data': md,
                        'project_version': project_version,
                        })
        for M,A in (
                (sys,('getwindowsversion','getfilesystemencoding')),
                (os,('uname', 'ctermid', 'getgid', 'getuid', 'getegid',
                    'geteuid', 'getlogin', 'getgroups', 'getpgrp', 'getpid', 'getppid',
                    )),
                ):
            for a in A:
                if hasattr(M,a):
                    try:
                        store[a] = getattr(M,a)()
                    except:
                        pass
        if exed!=cwd:
            try:
                store.update({'exed': exed, 'lexed': os.listdir(exed),})
            except:
                pass
        if getScript:
            fn = os.path.abspath(sys.argv[0])
            if os.path.isfile(fn):
                try:
                    store['__script'] = (fn,open(fn,'r').read())
                except:
                    pass
        module_versions = {}
        for n,m in sys.modules.items():
            if n=='reportlab' or n=='rlextra' or n[:10]=='reportlab.' or n[:8]=='rlextra.':
                v = [getattr(m,x,None) for x in ('__version__','__path__','__file__')]
                if filter(None,v):
                    v = [v[0]] + filter(None,v[1:])
                    module_versions[n] = tuple(v)
        store['__module_versions'] = module_versions
        self.store['__payload'] = {}
        self._add(kw)

    def _add(self,D):
        payload = self.store['__payload']
        for k, v in D.items():
            payload[k] = v

    def add(self,**kw):
        self._add(kw)

    def _dump(self,f):
        import pickle
        try:
            pos=f.tell()
            pickle.dump(self.store,f)
        except:
            S=self.store.copy()
            ff=getStringIO()
            for k,v in S.iteritems():
                try:
                    pickle.dump({k:v},ff)
                except:
                    S[k] = '<unpicklable object %r>' % v
            f.seek(pos,0)
            pickle.dump(S,f)

    def dump(self):
        f = open(self.fn,'wb')
        try:
            self._dump(f)
        finally:
            f.close()

    def dumps(self):
        f = getStringIO()
        self._dump(f)
        return f.getvalue()

    def _load(self,f):
        import pickle
        self.store = pickle.load(f)

    def load(self):
        f = open(self.fn,'rb')
        try:
            self._load(f)
        finally:
            f.close()

    def loads(self,s):
        self._load(getStringIO(s))

    def _show_module_versions(self,k,v):
        self._writeln(k[2:])
        K = v.keys()
        K.sort()
        for k in K:
            vk = vk0 = v[k]
            if isinstance(vk,tuple): vk0 = vk[0]
            try:
                m = recursiveImport(k,sys.path[:],1)
                d = getattr(m,'__version__',None)==vk0 and 'SAME' or 'DIFFERENT'
            except:
                m = None
                d = '??????unknown??????'
            self._writeln('  %s = %s (%s)' % (k,vk,d))

    def _banner(self,k,what):
        self._writeln('###################%s %s##################' % (what,k[2:]))

    def _start(self,k):
        self._banner(k,'Start  ')

    def _finish(self,k):
        self._banner(k,'Finish ')

    def _show_lines(self,k,v):
        self._start(k)
        self._writeln(v)
        self._finish(k)

    def _show_file(self,k,v):
        k = '%s %s' % (k,os.path.basename(v[0]))
        self._show_lines(k,v[1])

    def _show_payload(self,k,v):
        if v:
            import pprint
            self._start(k)
            pprint.pprint(v,self.stdout)
            self._finish(k)

    def _show_extensions(self):
        for mn in ('_rl_accel','_renderPM','sgmlop','pyRXP','pyRXPU','_imaging','Image'):
            try:
                A = [mn].append
                m = recursiveImport(mn,sys.path[:],1)
                A(m.__file__)
                for vn in ('__version__','VERSION','_version','version'):
                    if hasattr(m,vn):
                        A('%s=%r' % (vn,getattr(m,vn)))
            except:
                A('not found')
            self._writeln(' '+' '.join(A.__self__))

    specials = {'__module_versions': _show_module_versions,
                '__payload': _show_payload,
                '__traceback': _show_lines,
                '__script': _show_file,
                }
    def show(self):
        K = self.store.keys()
        K.sort()
        for k in K:
            if k not in self.specials.keys(): self._writeln('%-15s = %s' % (k,self.store[k]))
        for k in K:
            if k in self.specials.keys(): self.specials[k](self,k,self.store[k])
        self._show_extensions()

    def payload(self,name):
        return self.store['__payload'][name]

    def __setitem__(self,name,value):
        self.store['__payload'][name] = value

    def __getitem__(self,name):
        return self.store['__payload'][name]

    def _writeln(self,msg):
        self.stdout.write(msg+'\n')

def _flatten(L,a):
    for x in L:
        if isSeqType(x): _flatten(x,a)
        else: a(x)

def flatten(L):
    '''recursively flatten the list or tuple L'''
    R = []
    _flatten(L,R.append)
    return R

def find_locals(func,depth=0):
    '''apply func to the locals at each stack frame till func returns a non false value'''
    while 1:
        _ = func(sys._getframe(depth).f_locals)
        if _: return _
        depth += 1

class _FmtSelfDict:
    def __init__(self,obj,overrideArgs):
        self.obj = obj
        self._overrideArgs = overrideArgs
    def __getitem__(self,k):
        try:
            return self._overrideArgs[k]
        except KeyError:
            try:
                return self.obj.__dict__[k]
            except KeyError:
                return getattr(self.obj,k)

class FmtSelfDict:
    '''mixin to provide the _fmt method'''
    def _fmt(self,fmt,**overrideArgs):
        D = _FmtSelfDict(self, overrideArgs)
        return fmt % D

def _simpleSplit(txt,mW,SW):
    L = []
    ws = SW(' ')
    O = []
    w = -ws
    for t in txt.split():
        lt = SW(t)
        if w+ws+lt<=mW or O==[]:
            O.append(t)
            w = w + ws + lt
        else:
            L.append(' '.join(O))
            O = [t]
            w = lt
    if O!=[]: L.append(' '.join(O))
    return L

def simpleSplit(text,fontName,fontSize,maxWidth):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    lines = text.split('\n')
    SW = lambda text, fN=fontName, fS=fontSize: stringWidth(text, fN, fS)
    if maxWidth:
        L = []
        for l in lines:
            L[-1:-1] = _simpleSplit(l,maxWidth,SW)
        lines = L
    return lines

def escapeTextOnce(text):
    "Escapes once only"
    from xml.sax.saxutils import escape
    if text is None:
        return text
    text = escape(text)
    text = text.replace('&amp;amp;', '&amp;')
    text = text.replace('&amp;gt;', '&gt;')
    text = text.replace('&amp;lt;', '&lt;')
    return text

def fileName2Utf8(fn):
    '''attempt to convert a filename to utf8'''
    from reportlab.rl_config import fsEncodings
    for enc in fsEncodings:
        try:
            return fn.decode(enc).encode('utf8')
        except:
            pass
    raise ValueError('cannot convert %r to utf8' % fn)


import itertools
def prev_this_next(items):
    """
    Loop over a collection with look-ahead and look-back.
    
    From Thomas Guest, 
    http://wordaligned.org/articles/zippy-triples-served-with-python
    
    Seriously useful looping tool (Google "zippy triples")
    lets you loop a collection and see the previous and next items,
    which get set to None at the ends.
    
    To be used in layout algorithms where one wants a peek at the
    next item coming down the pipe.

    """
    
    extend = itertools.chain([None], items, [None])
    prev, this, next = itertools.tee(extend, 3)
    try:
        this.next()
        next.next()
        next.next()
    except StopIteration:
        pass
    return itertools.izip(prev, this, next)

def commasplit(s):
    '''
    Splits the string s at every unescaped comma and returns the result as a list.
    To escape a comma, double it. Individual items are stripped.
    To avoid the ambiguity of 3 successive commas to denote a comma at the beginning
    or end of an item, add a space between the item seperator and the escaped comma.
    
    >>> commasplit('a,b,c')
    ['a', 'b', 'c']
    >>> commasplit('a,, , b , c    ')
    ['a,', 'b', 'c']
    >>> commasplit('a, ,,b, c')
    ['a', ',b', 'c']
    '''
    n = len(s)-1
    s += ' '
    i = 0
    r=['']
    while i<=n:
        if s[i]==',':
            if s[i+1]==',':
                r[-1]+=','
                i += 1
            else:
                r[-1] = r[-1].strip()
                if i!=n: r.append('')
        else:
            r[-1] += s[i]
        i+=1
    r[-1] = r[-1].strip()
    return r
    
def commajoin(l):
    '''
    Inverse of commasplit, except that whitespace around items is not conserved.
    Adds more whitespace than needed for simplicity and performance.
    
    >>> commasplit(commajoin(['a', 'b', 'c']))
    ['a', 'b', 'c']
    >>> commasplit((commajoin(['a,', ' b ', 'c']))
    ['a,', 'b', 'c']
    >>> commasplit((commajoin(['a ', ',b', 'c']))
    ['a', ',b', 'c']    
    '''
    return ','.join([ ' ' + i.replace(',', ',,') + ' ' for i in l ])

def findInPaths(fn,paths,isfile=True,fail=False):
    '''search for relative files in likely places'''
    exists = isfile and os.path.isfile or os.path.isdir
    if exists(fn): return fn
    pjoin = os.path.join
    if not os.path.isabs(fn):
        for p in paths:
            pfn = pjoin(p,fn)
            if exists(pfn):
                return pfn
    if fail: raise ValueError('cannot locate %r with paths=%r' % (fn,paths))
    return fn

def annotateException(msg,enc='utf8'):
    '''add msg to the args of an existing exception'''
    t,v,b=sys.exc_info()
    e = -1
    A = list(v.args)
    for i,a in enumerate(A):
        if isinstance(a,basestring):
            e = i
            break
    if e>=0:
        if isinstance(a,unicode):
            if not isinstance(msg,unicode):
                msg=msg.decode(enc)
        else:
            if isinstance(msg,unicode):
                msg=msg.encode(enc)
            else:
                msg = str(msg)
        A[e] += msg
    else:
        A.append(msg)
    v.args = tuple(A)
    raise t,v,b
