import pygrib
import re

class CFSRwrapper(object):
    """Iterator for traversing grbs file skipping spin-up timestamps"""
    recpertimestep=None
    spinup=None
    nonspinup=None
    instant=None
    grbs=None
    fieldnametoparam={
        'dswsfc':(1,1,6,False),
        'tmp2m':(1,1,6,True),
        'wnd10m':(2,1,6,True),
        }
    def __init__(self, fname,recpertimestep=None,spinup=None,nonspinup=None,instant=None,autoconf=True):
        if autoconf:
            assert(recpertimestep==None)
            assert(spinup==None)
            assert(nonspinup==None)
            assert(instant==None)
            m=re.match("([^\./]+)\.l\.gdas\..*grb2",fname)
            if m:
                fieldname=m.groups()[0]
            else:
                fieldname=re.match("([^\./]+)\.gdas\..*grb2",fname).groups()[0]
            (self.recpertimestep,self.spinup,self.nonspinup,self.instant)=self.fieldnametoparam[fieldname]
        else:
            self.recpertimestep=recpertimestep
            self.spinup=spinup
            self.nonspinup=nonspinup
            self.instant=instant
        self.grbs=pygrib.open(fname)
                
    def __iter__(self):
        self.grbs.rewind()
        return self
    def step(self):
        return self.grbs.read(self.recpertimestep)
    def next(self):
        if self.grbs.messagenumber + self.recpertimestep > self.grbs.messages:
            raise StopIteration
        if self.spinup and (self.grbs.messagenumber % ((self.spinup + self.nonspinup)*self.recpertimestep) == 0):
            self.step()
        return self.step()
