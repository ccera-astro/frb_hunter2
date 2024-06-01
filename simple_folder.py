#!/usr/bin/python3
import numpy
import os
import time
import sys
import argparse
import math
import random

#
# Compute total smear time from basic observing and pulsar parameters
#
def compute_smear(fc,bw,dm):
        
    bw /= 1.0e6
    fc /= 1.0e9

    usec = 8.3 * bw * dm * (fc**-3.0)
    return (usec/1.0e6)


MET = 0.0

parser = argparse.ArgumentParser()
parser.add_argument("--srate", type=float, default=3125, help="Input sample rate")
parser.add_argument("--width", type=int, default=32, help="Input FFT width")
parser.add_argument("--p0", type=float, default=0.714525, help="Input pulse period")
parser.add_argument("--tbins", type=int, default=256, help="Output phase bins")
parser.add_argument("--median", type=int, default=5, help="Median filter width")
parser.add_argument("--infile", type=str, help="Input filename", required=True)
parser.add_argument("--trim", type=float, help="Trim length in seconds", default=0.0)
parser.add_argument("--verbose", action="store_true", default=False)
parser.add_argument("--outfile", type=str, help="Output filename", required=True)
parser.add_argument("--sigma", type=float, help="De-noise sigma threshold", default=3.5)
parser.add_argument("--ltrim", type=float, help="Lower trim value (secs)", default=0.0)
parser.add_argument("--utrim", type=float, help="Upper trim value (secs)", default=0.0)
parser.add_argument("--dmsmear", type=float, help="Max DM-based smear time in seconds", default=0.0)
parser.add_argument("--dm", type=float, help="DM of observation", default=0.0)
parser.add_argument("--freq", type=float, help="Center frequency of observation", default=0.0)
parser.add_argument("--bw", type=float, help="Bandwidth", default=0.0)
parser.add_argument("--hpass", action="store_true", default=False)
parser.add_argument("--halpha", type=float, help="Alpha value for high-pass", default=0.01)
parser.add_argument("--mpass", action="store_true", help="Enable mid-pass filter", default=False)
parser.add_argument("--malpha", type=float, help="Alpha value for mid-pass", default=0.3)

    

args = parser.parse_args()

#
# Compute parameters we'll require to roll the columns, based on
#  smear time.
#
dmsmear = 0.0
if (args.dmsmear > 0.0 or (args.dm > 0.0 and args.freq > 0.0 and args.bw > 0.0)):
    
    dmsmear = args.dmsmear
    if (args.dm > 0.0):
        dmsmear = compute_smear(args.freq, args.bw, args.dm)
        if (args.verbose):
            print ("Computed smear time of %f secs" % dmsmear)
    #
    # Convert smear time into number of samples at input srate
    #
    dmsamps = dmsmear / (1.0 / args.srate)
    dmsamps = round(dmsamps)
    if (args.verbose):
        print ("dmsamps %d" % dmsamps)
        
    #
    # We create a "prebuf" that is as long as the maximum number of samples
    #  in the smear time
    #
    prebuf = numpy.zeros((int(dmsamps),args.width))

    #
    # Compute the offsets/delays/roll-amounts, based on
    #  number of samples, starting at highest, and decreasing
    #  by dmsamps/args.width each time
    #
    dmoffsets = []
    a = dmsamps
    for i in range(args.width):
        dmoffsets.append(round(a))
        a -= float(dmsamps)/float(args.width)
    
    #
    # Then flip it
    #
    dmoffsets = numpy.flip(numpy.array(dmoffsets))
    if (args.verbose):
        print ("dmoffsets: %s" % str(dmoffsets))

#
# Pull in data as if it's a 1D array of float32
#
inarray = numpy.fromfile(args.infile, dtype=numpy.float32)

#
# Reshape into a 2D array arranged by FFT width
#
inarray = inarray.reshape((-1,args.width))

#
# Prepend some extra zeros if we're de-dispersing, then roll the columns
#  appropriately...
#
if (dmsmear > 0.0):
    cols = [x for x in range(args.width)]
    dirn = numpy.multiply(dmoffsets, -1)
    if (args.verbose):
        print ("dirn %s" % str(dirn))
    n = inarray.shape[0]
    inarray[:,cols] = inarray[numpy.mod(numpy.arange(n)[:,None] + dirn,n),cols]
#
# Do a sum on each row
#
#
timeseries = numpy.sum(inarray,axis=1)
if (args.verbose):
    print ("Input contains %d seconds of data" % (len(timeseries)/args.srate))

if (args.trim > 0.0):
    samples = args.trim * args.srate
    samples = int(samples)
    timeseries=timeseries[samples:-samples]

#
# Do unbalanced edge-trim (creating a kind of "window")
#
ltrimsamps = int(args.ltrim * args.srate)
utrimsamps = int(args.utrim * args.srate)

if (utrimsamps > 0 or ltrimsamps > 0):
    if (utrimsamps > 0):
        timeseries = timeseries[ltrimsamps:-utrimsamps]
    else:
        timeseries = timeseries[ltrimsamps:]

if (args.verbose):
    print ("After trim, timeseries contains %d seconds of data" % (len(timeseries)/args.srate))

#
# Eliminate pesky large spikes, which are likely RFI
#   
nreplace = 0

#
# First compute mean and STD
#
mean = numpy.mean(timeseries)
std = numpy.std(timeseries)

if (args.verbose):
    print ("std %f mean %f" % (std, mean))

#
# Perform replacement with numpy magic
#
nreplace = len(timeseries[timeseries>(mean+(args.sigma*std))])
nreplace += len(timeseries[timeseries<(mean-(args.sigma*std))])
timeseries[timeseries>(mean+(args.sigma*std))] = mean
timeseries[timeseries<(mean-(args.sigma*std))] = mean

if (args.verbose):
    print ("nreplace %d (%f %%)" % (nreplace, 100.0*(float(nreplace)/len(timeseries))))
    
#
# If also doing median filtering...
#
if (args.median > 0):
    #
    # Reshape back into a 2D array
    #
    timeseries = timeseries.reshape((-1,args.median))

    #
    # Compute median on each row, producing a new
    #   median-filtered time series
    #
    timeseries = numpy.median(timeseries,axis=1)

#
# Construct empty phase-bin output array
#
bins = numpy.zeros(args.tbins)
bcounts = numpy.zeros(args.tbins)

#
# Time increment for incoming samples
#
mincr = 1.0/args.srate
if (args.median > 0):
    mincr = 1.0/(args.srate/args.median)

#
# Initialize Mission Elapsed Timer
#
MET = 0.0

#
# Compute bin width
#
tbinw = args.p0 / float(args.tbins)

#
# Place time series into phase bins
#
lpass = timeseries[0]
mpass = timeseries[0]
alpha = args.halpha
beta = 1.0 - alpha
malpha = 0.3
mbeta = 1.0 - malpha
for v in timeseries:
    
    if (args.hpass):
        lpass = alpha*v + beta*lpass
        fv = v - (0.95*lpass)
    else:
        fv = v
    
    if (args.mpass):
        mpass = fv * malpha + mbeta * mpass
        fv = mpass
    #fv = v
    #
    # Compute which phase bin for this sample
    #
    which = MET / (tbinw)
    which = int(which) % args.tbins
    
    #
    # Place sample in that phase bin
    # Increment count
    #
    bins[which] += fv
    bcounts[which] += 1
    
    #
    # Increment Mission Elapsed Timer by sample time
    #
    MET += mincr

#
# Print all the phase bins
#
reduced = numpy.divide(bins,bcounts)
reduced = numpy.divide(reduced, min(reduced))
std = numpy.std(reduced)
mean = numpy.mean(reduced)
fp = open(args.outfile, "w")
for i in range(len(bins)):
    fp.write("%f %13.8f\n" % ((i*tbinw)/args.p0, (reduced[i]-mean)/std))
fp.close()
