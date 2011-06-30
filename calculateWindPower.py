from CFSRwrapper import *

def openfields(infields,year,month,lowres=False):
    import itertools
    r=[]
    for f in infields:
        r.append(CFSRwrapper(filenamefromfield(f,2000,3,lowres)))
    return itertools.izip(*r)

def unpackandapply(i,conv,outf):
    rnp=conv(map(lambda x:x[0].data,i))
    rmc=i[0][0]
    rmc.putdata(rnp)
    outf.write(rmc.grbmsg.tostring())
    return rmc

def iterateandapply(it,conv,outf):
    assert(outf.mode=='wb')
    for i in it:
        rmc=unpackandapply(i,conv,outf)

def PWconversion(i):
    """Plain Wrong conversion of windspeed and radiation to power"""
    return i[0]**3 + i[1]

infields=['wnd10m','dswsfc']

it=openfields(infields,2000,3,True)

outf=file("PWconversion.output.grib",'wb')

# #convert just one timestep
#i=it.next()
#unpackandapply(i,PWconversion,outf)

# #convert all
#iterateandapply(it,PWconversion,outf)


