import pygrib

class CFSRwrapper(object):
    """Iterator for traversing grbs file skipping spin-up timestamps"""
    recpertimestep=None
    spinup=None
    nonspinup=None
    grbs=None
    def __init__(self, fname,recpertimestep,spinup=1,nonspinup=6):
        self.grbs=pygrib.open(fname)
        self.recpertimestep=recpertimestep
        self.spinup=spinup
        self.nonspinup=nonspinup
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
