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
    threshold=173.43 #solar radiation below which the panel stops giving useful power
    A=-0.624 # A, B, C are coefficients for the equation : P= A + B*I + C*logI and are calculated by using the three different values of solar radiation and their peak powers at 25deg C module temperature for corresponding radiations from the data sheet
    B=-0.0000883
    C=0.124
    D=0.0048 #temperature power coefficient given in data sheet
    NOCT=323.0 #Nominal Operating Cell Temperature given in data sheet
    Ts=298.0 #STC (Standard testing Condition) module temperature in K
    Tn=293.0 #NTC (Nomial testing Condition) module temperature in K
    In=800.0 #NTC radiation in W/m2
    
    #Mask for lower threshold
    index = I>threshold
    #Convert to solar PV power
    P = zeros(I.shape)
    P[index]=I[index]*(A+(B*I[index])+(C*log(I[index])))*(1.0-D*(T[index]-Ts+((NOCT-Tn)/In*I[index])))
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
