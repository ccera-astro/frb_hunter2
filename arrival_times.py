#!/usr/bin/python3
import numpy
import math
import sys
import os
import time
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Extract arrival times across the FB")

parser.add_argument("--infile", type=str, help="Input filename", required=True)
parser.add_argument("--chans", type=int, help="Number of bins in FB", default=16)
parser.add_argument("--crate", type=float, help="Channel sample rate", default=12500.0)

args = parser.parse_args()

a=numpy.fromfile(args.infile, dtype=numpy.float32)
nr=int(len(a)/args.chans)

middle = int(nr/2)
start = middle-200
end = middle+200
a2 = numpy.reshape(a,(nr,args.chans))
atimes=[]
for c in range(0,args.chans):
    ta = []
    for r in range(start,end):
        ta.append(a2[r][c])
    atimes.append(numpy.argmax(ta))

tstart = 0.0
tincr = 1.0/args.crate
tincr *= 1000.0
xaxis = [x for x in numpy.arange(0,tincr*400,tincr)]
for c in range(0,args.chans):
    yaxis = []
    for r in range(start,end):
        yaxis.append(a2[r][c]+c*0.001)
    plt.plot(xaxis,yaxis,label="Ch:%d" % c)
plt.xlabel("Time (msec)")
plt.title("Channel powers")
plt.legend()
plt.show()
    
"""
atimes = numpy.subtract(atimes, numpy.min(atimes))
for v in atimes:
    print ("%d" % v)

"""    
