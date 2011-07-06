#!/usr/bin/env python
from CFSRwrapper import *
from optparse import OptionGroup
from numpy import zeros,log

locoptions=OptionGroup(parser, "PV conversion options", "Options related to conversion of radiation and temperature to power")
locoptions.add_option("--solarpaneltype", dest="solarpaneltypefile", default=None, type=str,
                      help="file containing characteristics of the solar panels")

parser.add_option_group(locoptions)

(options, args) = parser.parse_args()

infields=['dswsfc','tmp2m']

def SolarPVConversion(data):
    """Conversion of radiation and temperature to solar PV power"""
    I=data[0]  #Radiation
    T=data[1]  #Temperature

    #Solar panel data
    threshold=173.43
    A=-0.624
    B=-0.0000883
    C=0.124
    D=0.0048
    NOCT=50.

    #Mask for lower threshold
    index = I>threshold

    #Convert to solar PV power
    P = zeros(I.shape)
    P[index]=I[index]*(A+(B*I[index])+(C*log(I[index])))*(1.0-D*(T[index]-298.0+((NOCT-20.)/800.*I[index])))
    P[I<=threshold]=0.
    return P

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("PVpower",options.year,options.month,options.lowres),'wb')

convfunc=SolarPVConversion

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,convfunc,outf)
else:
    #convert all
    iterateandapply(it,convfunc,outf)
