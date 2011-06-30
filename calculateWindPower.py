from CFSRwrapper import *

def openfields(infields,year,month,lowres=False):
    import itertools
    r=[]
    for f in infields:
        r.append(CFSRwrapper(filenamefromfield(f,2000,3,lowres)))
    return itertools.izip(*r)

def unpackandapply(i,conv):
    return conv(map(lambda x:x[0].data,i))

def iterateandapply(it,conv):
    for i in it:
        c=unpackandapply(i,conv)

def PWconversion(i):
    """Plain Wrong conversion of windspeed and radiation to power"""
    return i[0]**3 + i[1]

infields=['wnd10m','dswsfc']

it=openfields(infields,2000,3,True)

#convert just one timestep
i=it.next()
unpackandapply(i,PWconversion)

#convert all
iterateandapply(it,PWconversion)

