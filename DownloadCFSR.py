#!/bin/env python
from optparse import OptionParser
from numpy import meshgrid,array

years=array(range(1979,2010))
months=array(range(1,13))

parser = OptionParser()
parser.add_option("--year", dest="year", type=int,
                  help="the year to download, all years (%i-%i) if left blank" % (years[0],years[-1]))
parser.add_option("--minyear", dest="minyear", type=int, default=years[0],
                  help="min year to download [%i]" % (years[0],))
parser.add_option("--maxyear", dest="maxyear", type=int, default=years[-1],
                  help="max year to download [%i]" % (years[-1],))
parser.add_option("--month", dest="month", type=int,
                  help="the month to download, all months if left blank")
parser.add_option("--datafield", dest="field",
                  type=str,
                  help="the datafield to download")
parser.add_option("--lowresonly",
                  action="store_true", dest="lowresonly",
                  help="download only the low resoultion files")
parser.add_option("--debug",
                  action="store_true", dest="debug",
                  help="run in debug mode")

(options, args) = parser.parse_args()

assert(options.field in ["wnd10m","tmp2m","dswsfc"])

if options.year:
    assert(options.year in years)
    years=array([options.year])
years=years[years>=options.minyear]
years=years[years<=options.maxyear]
if options.month:
    assert(options.month in months)
    months=array([options.month])

base="http://nomads.ncdc.noaa.gov/data/cfsr/"

def createfilenames(field,year,month,lowresonly=False):
    d="%i%02i" % (year,month)
    r=[]
    r.append("%s/%s.l.gdas.%s.grb2" % (d,field,d))
    r.append("%s/%s.l.gdas.%s.grb2.inv" % (d,field,d))
    if not(lowresonly):
        r.append("%s/%s.gdas.%s.grb2" % (d,field,d))
        r.append("%s/%s.gdas.%s.grb2.inv" % (d,field,d))
    return r
    #197902/wnd10m.l.gdas.197902.grb2.inv

def wgetfile(field,years,months,lowresonly=False):
    fname="download_%s.wget" % (field,)
    f=file(fname, "w")
    #f.write("#!/usr/bin/wget --base=%s  -i \n" % (base,))
    M,Y=meshgrid(months,years)
    for m,y in zip(M.ravel(),Y.ravel()):
        map(lambda x: f.write(x + "\n"), createfilenames(field,y,m,lowresonly=lowresonly))
    return fname

print "Creating wget file for data field", options.field
print "for the years:", years
print "and months:", months
fname=wgetfile(options.field,years,months,lowresonly=options.lowresonly)
print "now you use:\n    wget --base=%s --continue -nH -r --cut-dirs=2 --input-file=%s\nto download the files." % (base,fname) 
