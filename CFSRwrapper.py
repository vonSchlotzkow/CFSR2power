import pygrib
import re

def deepcopydatatolist(c):
    return map(lambda x: x["values"].copy() , c)

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

class CFSRwrapper(pygrib.open):
    """Iterator for traversing grbs file skipping spin-up timestamps"""
    recpertimestep=None
    spinup=None
    nonspinup=None
    instant=None
    unaverage=None
    fieldnametoparam={
        'dswsfc':(1,1,6,False,True),
        'tmp2m':(1,1,6,True,False),
        'wnd10m':(2,1,6,True,False),
        }
    _previousdata=None
    _currentdata=None
    def __init__(self, fname,recpertimestep=None,spinup=None,nonspinup=None,instant=None,unaverage=None,autoconf=True):
        if autoconf:
            assert(recpertimestep==None)
            assert(spinup==None)
            assert(nonspinup==None)
            assert(instant==None)
            assert(unaverage==None)
            fieldname=re.match("([^\./]+)(\.l\.|\.)gdas\..*grb2",fname).groups()[0]
            (self.recpertimestep,self.spinup,self.nonspinup,self.instant,self.unaverage)=self.fieldnametoparam[fieldname]
        else:
            self.recpertimestep=recpertimestep
            self.spinup=spinup
            self.nonspinup=nonspinup
            self.instant=instant
            self.unaverage=unaverage
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
        if self.unaverage:
            T=self.messagestep()
            if T <= 1: self._previousdata=None
            currentdata=self.read(self.recpertimestep)
            self._currentdata=deepcopydatatolist(currentdata)
            if self._previousdata:
                ret=currentdata
                for p,c,r in zip(self._previousdata, self._currentdata, ret):
                    r["values"] = T*c - (T-1)*p
                self._previousdata=self._currentdata
                return ret
            else:
                #first step after spin up
                self._previousdata=self._currentdata
                return currentdata
        else:
            currentdata=self.read(self.recpertimestep)
            return currentdata
    def next(self):
        if self.messagenumber + self.recpertimestep > self.messages:
            raise StopIteration
        if self.isspinupstep():
            self.step()
        return self.step()
