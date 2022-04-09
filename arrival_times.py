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
parser.add_argument("--title", type=str, help="Plot title", default="Channel powers")
parser.add_argument("--times", action="store_true", help="Show times", default=False)

args = parser.parse_args()

a=numpy.fromfile(args.infile, dtype=numpy.float32)
if (len(a) % args.chans != 0):
	a=a[0:len(a)-(len(a) % args.chans)]
nr=int(len(a)/args.chans)
print ("nr is %d" % nr)

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
peaks=[]

if args.times == False:
    for c in range(0,args.chans):
        yaxis = []
        for r in range(start,end):
            yaxis.append(a2[r][c]+c*0.001)
        peaks.append(numpy.argmax(yaxis))
        plt.plot(xaxis,yaxis,label="Ch:%d" % c)
    plt.xlabel("Time (msec)")
    plt.grid(True)
    plt.title(args.title)
    plt.legend()
    plt.show()
else:
    for c in range(0,args.chans):
        yaxis = []
        for r in range(start,end):
            yaxis.append(a2[r][c]+c*0.001)
        peaks.append(numpy.argmax(yaxis)/(args.crate/1000.0))
    xaxis = range(0,args.chans)
    ideal=[]
    for i in range(0,args.chans):
        ideal.append(numpy.max(peaks)*((i/float(args.chans)*(i/float(args.chans)))))
    ideal.reverse()
    plt.plot(xaxis,peaks,label="Times")
    plt.plot(xaxis,ideal,label="Ideal", linewidth=2.0, linestyle="dashed")
    plt.xlabel("Channel number")
    plt.ylabel("Arrival time (msec)")
    plt.title(args.title)
    plt.grid(True)
    plt.legend()
    plt.show()
    

    
"""
atimes = numpy.subtract(atimes, numpy.min(atimes))
for v in atimes:
    print ("%d" % v)

"""    
