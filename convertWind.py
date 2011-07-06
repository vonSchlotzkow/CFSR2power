#!/usr/bin/env python
from CFSRwrapper import *
from optparse import OptionGroup
from pylab import interp

locoptions=OptionGroup(parser, "Wind conversion options", "Options related to converting ")
locoptions.add_option("--turbinecurve", dest="turbinecurve", default=None, type=str,
                      help="File containing the characteristic curve of a turbine")

parser.add_option_group(locoptions)

(options, args) = parser.parse_args()

def PWconversion(i,nonsensfactor):
    """Plain Wrong conversion of windspeed and radiation to power"""
    return i[0]**3

def WindConversion(data):
    """Conversion of wind speed to wind power"""
    wind10m = data[0]
    
    #Turbine data
    H = 80. #Hub height
    V = [0,3,4,5,6,7,8,9,10,11,12,12.5,23.0,23.0] #Power curve velocities
    POW = [0.000,0.000,.110,.230,.405,.720,1.080,1.480,1.800,2.100,2.370,2.600,2.600,0.000] #power from the power curves
   
    #Convert wind speed to hub height H from a height 10m above the ground
    #0.143 is power law index which depends on roughness of the surface and assumed to be constant for the time being.
    wind = wind10m*((H/10)**0.143)
    
    #Apply power curve
    P = interp(wind,V,POW) #interpolation using power curve data

    return P

infields=['wnd10m']

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("WindPower",options.year,options.month,options.lowres),'wb')

#example of binding additional options to the conversion function
#convfunc=lambda x:PWconversion(x,options.nonsensfactor)
convfunc=WindConversion

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,convfunc,outf)
else:
    #convert all
    iterateandapply(it,convfunc,outf)
