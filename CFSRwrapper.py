import pygrib
import re
from pylab import vector_lengths
import numpy
from optparse import OptionParser

def filenamefromfield(field,year,month,lowres=False,basedir=""):
    if lowres:
        lowres=".l."
    else:
        lowres="."
    return "%s%i%02i/%s%sgdas.%i%02i.grb2" % (basedir,year,month,field,lowres,year,month)

def deepcopydatatolist(c):
    return map(lambda x: x.getdata() , c)

def ReduceToVecLengths(mcl):
    """
    Calculate absoulute value of vectors stored in a list of wrapped
    grib messages

    Danger Will Robinson: This function has side effects on the first
    element of the list!

    However, if it is used as 'Reduce' function in the iterator, noone
    will ever see the original element, so we don't care about side
    effects.
    """
    ret=mcl[0]
    ret.putdata(vector_lengths(numpy.array(deepcopydatatolist(mcl)),axis=0))
    return [ret]

class messagecontainer(object):
    grbmsg=None
    data=None
    def __init__(self,grbmsg):
        self.grbmsg=grbmsg
        self.data=self.grbmsg.values.copy()
    def __repr__(self):
        return self.grbmsg.__repr__()
    def getdata(self):
        return self.data.copy()
    def data2grbmsg(self):
        self.grbmsg.values=self.data.copy()
    def putdata(self,d):
        self.data=d.copy()
        self.data2grbmsg()

    def createmask(self,f):
        """create a bitmap mask defined by the boolean function f(lat,lon)

        nonsense lambda function to use:
        (lambda la,lo: [True,False][(int((la+lo)/10.)%2)])
        """
        la,lo=self.grbmsg.latlons()
        return numpy.vectorize(f)(la,lo)
    
    def applymask(self,m):
        """return a masked array containg the data of the current grib message masked with m

        BEWARE: a value of True in m means that this pixel will be masked out!

        use create/apply mask like this:
        m=I.createmask(sillymask)
        mw=I.applymask(m==False)
        """
        return (numpy.ma.masked_array(self.grbmsg.values,mask=m))

def sillymask(la,lo):
    x=complex(0.,0.)
    c=complex(((lo-180.)/90.),la/90.)
    for i in range(100):
        try:
            x=x**2+c
            if abs(x)>2:
                return False
        except OverflowError:
            return False
    return abs(x)<2.

class CFSRwrapper(pygrib.open):
    """Iterator for traversing grbs file skipping spin-up timestamps"""
    recpertimestep=None
    spinup=None
    nonspinup=None
    instant=None
    unaverage=None
    fieldnametoparam={
        'dswsfc':(1,1,6,False,True,None),
        'tmp2m':(1,1,6,True,False,None),
        'wnd10m':(2,1,6,True,False,ReduceToVecLengths),
        }
    _previousdata=None
    _currentdata=None
    _Reduce=None
    def __init__(self, fname,recpertimestep=None,spinup=None,nonspinup=None,instant=None,unaverage=None,autoconf=True,Reduce=None):
        if autoconf:
            assert(recpertimestep==None)
            assert(spinup==None)
            assert(nonspinup==None)
            assert(instant==None)
            assert(unaverage==None)
            assert(Reduce==None)
            fieldname=re.match("(|.*/)([^\./]+)(\.l\.|\.)gdas\..*grb2",fname).groups()[1]
            (self.recpertimestep,self.spinup,self.nonspinup,self.instant,self.unaverage,self._Reduce)=self.fieldnametoparam[fieldname]
        else:
            self.recpertimestep=recpertimestep
            self.spinup=spinup
            self.nonspinup=nonspinup
            self.instant=instant
            self.unaverage=unaverage
            self._Reduce=Reduce
        pygrib.open.__init__(self,fname)
    def __new__(cls, fname, *args, **kwargs):
        obj=pygrib.open.__new__(cls, fname)
        return obj
    def __iter__(self):
        self.rewind()
        return self
    def messagestep(self):
        return self.messagenumber/self.recpertimestep % ((self.spinup + self.nonspinup))
    def isspinupstep(self):
        return self.spinup and (self.messagestep() == 0)
    def read(self,N=None):
        return map(messagecontainer,pygrib.open.read(self,N))
    def step(self):
        """read the next step of the raw data series

        If 'unaverage' reverse the averaging, and return instantaneous
        data.  Unaveraging is done according to

        $$ \tilde{x}_T = \frac{1}{T} \sum_{t=1}^{T} x_t \\
        = \sum_{t=1}^{T-1} \frac{T-1}{T} \frac{x_t}{T-1} + \frac{x_T}{T} \\
        = \frac{T-1}{T} \tilde{x}_{T-1} + \frac{x_T}{T}\\
        x_{t} = T\tilde{x}_{T} -(T-1)\tilde{x}_{T-1} $$

        where $x_t$ is the instantaneous data and $\tilde{x}_t$ is the
        averaged data at time $t$.
        """
        currentdata=self.read(self.recpertimestep)
        if self.unaverage:
            T=self.messagestep()
            if T <= 1: self._previousdata=None
            currentdata[0].stepType='instant'
            self._currentdata=deepcopydatatolist(currentdata)
            if self._previousdata:
                ret=currentdata
                for p,c,r in zip(self._previousdata, self._currentdata, ret):
                    r.putdata(T*c - (T-1)*p)
                self._previousdata=self._currentdata
                return ret
            else:
                #first step after spin up
                self._previousdata=self._currentdata
        return currentdata

    def next(self):
        if self.messagenumber + self.recpertimestep > self.messages:
            raise StopIteration
        if self.isspinupstep():
            self.step()
        if self._Reduce:
            return self._Reduce(self.step())
        else:
            return self.step()

def openfields(infields,year,month,lowres=False):
    import itertools
    r=[]
    for f in infields:
        r.append(CFSRwrapper(filenamefromfield(f,year,month,lowres)))
    return itertools.izip(*r)

def unpackandapply(i,conv,outf):
    rnp=conv(map(lambda x:x[0].data,i))
    rmc=i[0][0]
    rmc.putdata(rnp)
    # changing the units is not that easy, apparently the units have to match a 'concept'
    #rmc.grbmsg.units='MW'
    outf.write(rmc.grbmsg.tostring())
    return rmc

def iterateandapply(it,conv,outf):
    assert(outf.mode=='wb')
    for i in it:
        rmc=unpackandapply(i,conv,outf)

parser = OptionParser()
parser.add_option("--year", dest="year", default=2000, type=int,
                  help="year")
parser.add_option("--month", dest="month", default=1, type=int,
                  help="day of month")
parser.add_option("--lowres",
                  action="store_true", dest="lowres",
                  help="convert low resolution data")
parser.add_option("--debug",
                  action="store_true", dest="debug",
                  help="run in debug mode")
