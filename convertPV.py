#!/usr/bin/env python
from CFSRwrapper import *
from optparse import OptionGroup
from numpy import zeros,log
from configobj import ConfigObj
from validate import Validator
from StringIO import StringIO

locoptions=OptionGroup(parser, "PV conversion options", "Options related to conversion of radiation and temperature to power")
locoptions.add_option("--solarpaneltype", dest="solarpaneltypefile", default=None, type=str,
                      help="file containing characteristics of the solar panels")

parser.add_option_group(locoptions)

(options, args) = parser.parse_args()

infields=['dswsfc','tmp2m']

#the config file spec
spec=StringIO("""
# Solar panel data
name = string

# Solar radiation below which the panel stops giving useful power
threshold = float

# A, B, C are coefficients for the equation : P= A + B*I + C*logI and
# are calculated by using the three different values of solar
# radiation and their peak powers at 25deg C module temperature for
# corresponding radiations from the data sheet
A = float
B = float
C = float

#temperature power coefficient given in data sheet
D = float

#Nominal Operating Cell Temperature given in data sheet
NOCT = float
#STC (Standard testing Condition) module temperature in K
Ts = float
#NTC (Nomial testing Condition) module temperature in K
Tn = float
#NTC radiation in W/m2
In = float
""")
configspec=ConfigObj(spec,
                     list_values=False, file_error=True, _inspec=True)
panelconfig=ConfigObj(options.solarpaneltypefile,
                      list_values=False,
                      configspec=configspec)
panelconfig.validate(Validator())

def SolarPVConversion(data,c):
    """Conversion of radiation and temperature to solar PV power"""
    I=data[0]  #Radiation
    T=data[1]  #Temperature

    #Solar panel data
    threshold=c['threshold'] #solar radiation below which the panel stops giving useful power
    A=c['A'] # A, B, C are coefficients for the equation : P= A + B*I + C*logI and are calculated by using the three different values of solar radiation and their peak powers at 25deg C module temperature for corresponding radiations from the data sheet
    B=c['B']
    C=c['C']
    D=c['D'] #temperature power coefficient given in data sheet
    NOCT=c['NOCT'] #Nominal Operating Cell Temperature given in data sheet
    Ts=c['Ts'] #STC (Standard testing Condition) module temperature in K
    Tn=c['Tn'] #NTC (Nomial testing Condition) module temperature in K
    In=c['In'] #NTC radiation in W/m2
    
    #Mask for lower threshold
    index = I>threshold
    #Convert to solar PV power
    P = zeros(I.shape)
    P[index]=I[index]*(A+(B*I[index])+(C*log(I[index])))*(1.0-D*(T[index]-Ts+((NOCT-Tn)/In*I[index])))
    P[I<=threshold]=0.
    return P

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("PVpower_%s" % (panelconfig['name'],), options.year,options.month,options.lowres),'wb')

convfunc=lambda x: SolarPVConversion(x,panelconfig)

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,convfunc,outf)
else:
    #convert all
    iterateandapply(it,convfunc,outf)
