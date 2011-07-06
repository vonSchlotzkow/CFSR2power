#!/usr/bin/env python
from CFSRwrapper import *
from optparse import OptionGroup

locoptions=OptionGroup(parser, "Wind conversion options", "Options related to converting ")
locoptions.add_option("--turbinecurve", dest="turbinecurve", default=None, type=str,
                      help="File containing the characteristic curve of a turbine")

parser.add_option_group(locoptions)

(options, args) = parser.parse_args()

def PWconversion(i,nonsensfactor):
    """Plain Wrong conversion of windspeed and radiation to power"""
    return i[0]**3

infields=['wnd10m']

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("WindPower",options.year,options.month,options.lowres),'wb')

#example of binding additional options to the conversion function
#convfunc=lambda x:PWconversion(x,options.nonsensfactor)
convfunc=PWconversion

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,convfunc,outf)
else:
    #convert all
    iterateandapply(it,convfunc,outf)
