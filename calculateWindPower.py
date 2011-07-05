from CFSRwrapper import *
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--year", dest="year", default=2000, type=int,
                  help="year")
parser.add_option("--month", dest="month", default=1, type=int,
                  help="day of month")
parser.add_option("--lowres",
                  action="store_true", dest="lowres",
                  help="convert low resolution data")
parser.add_option("--debug",
                  action="store_true", dest="debug",
                  help="run in debug mode")

(options, args) = parser.parse_args()

def PWconversion(i):
    """Plain Wrong conversion of windspeed and radiation to power"""
    return i[0]**3 + i[1]

infields=['wnd10m','dswsfc']

it=openfields(infields,options.year,options.month,options.lowres)

outf=file(filenamefromfield("PWpower",options.year,options.month,options.lowres),'wb')

if options.debug:
    #convert just one timestep
    i=it.next()
    unpackandapply(i,PWconversion,outf)
else:
    #convert all
    iterateandapply(it,PWconversion,outf)
