import pygrib
import re

class CFSRwrapper(pygrib.open):
    """Iterator for traversing grbs file skipping spin-up timestamps"""
    recpertimestep=None
    spinup=None
    nonspinup=None
    instant=None
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
        return self.read(self.recpertimestep)
    def next(self):
        if self.messagenumber + self.recpertimestep > self.messages:
            raise StopIteration
        if self.isspinupstep():
            self.step()
        return self.step()
