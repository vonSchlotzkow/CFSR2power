#!/usr/bin/env python
from CFSRwrapper import *
from optparse import OptionGroup

locoptions=OptionGroup(parser, "PWconversion options", "Options related to PWconversion")
locoptions.add_option("--nonsensfactor", dest="nonsensfactor", default=1, type=float,
                      help="stupid factor of the plain wrong conversion")

parser.add_option_group(locoptions)

(options, args) = parser.parse_args()

def PWconversion(i,nonsensfactor):
    """Plain Wrong conversion of windspeed and radiation to power"""
    return i[0]**3 + nonsensfactor*i[1]

infields=['wnd10m','dswsfc']

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("PWpower",options.year,options.month,options.lowres),'wb')

convfunc=lambda x:PWconversion(x,options.nonsensfactor)

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,convfunc,outf)
else:
    #convert all
    iterateandapply(it,convfunc,outf)
