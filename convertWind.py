#!/usr/bin/env python
from CFSRwrapper import *
from optparse import OptionGroup
from pylab import interp
from configobj import ConfigObj
from validate import Validator
from StringIO import StringIO

locoptions=OptionGroup(parser, "Wind conversion options", "Options related to converting ")
locoptions.add_option("--turbinecurve", dest="turbinecurve", default=None, type=str,
                      help="File containing the characteristic curve of a turbine")

parser.add_option_group(locoptions)

(options, args) = parser.parse_args()

infields=['wnd10m']

#the config file spec
spec=StringIO("""
# Turbine characteristic data
name = string
# The manufacturer of this turbine
manufacturer = string
# Link to the original datasheet of the turbine
source = string

# Hub height
H = float
# Power curve, specified as lists of velocities and powers, including
# cut-in and cut-out speeds
# Power curve velocities
V = list
# Generated power from the power curves
POW = list
""")
configspec=ConfigObj(spec,
                     list_values=False, file_error=True, _inspec=True)
turbineconfig=ConfigObj(options.turbinecurve,
                        list_values=True, file_error=True,
                        configspec=configspec)
turbineconfig.validate(Validator())
# it would be more elegant to give the requirement for lists of floats
# in the spec, which should result in a conversion to floats at the
# same time, but well...
for listkey in ['V','POW']:
    turbineconfig[listkey]=map(float,turbineconfig[listkey])

def WindConversion(data,c):
    """Conversion of wind speed to wind power"""
    wind10m = data[0]
    
    #Turbine data
    H = c['H'] #Hub height
    V = c['V'] #Power curve velocities
    POW = c['POW'] #power from the power curves
   
    #Convert wind speed to hub height H from a height 10m above the ground
    #0.143 is power law index which depends on roughness of the surface and assumed to be constant for the time being.
    wind = wind10m*((H/10)**0.143)
    
    #Apply power curve
    P = interp(wind,V,POW) #interpolation using power curve data

    return P

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("WindPower_%s" % turbineconfig['name'],options.year,options.month,options.lowres),'wb')

#example of binding additional options to the conversion function
convfunc=lambda x:WindConversion(x,turbineconfig)

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,convfunc,outf)
else:
    #convert all
    iterateandapply(it,convfunc,outf)
