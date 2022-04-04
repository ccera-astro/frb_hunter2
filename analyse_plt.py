#!/usr/bin/python3
import numpy
import os
import time
import sys
from scipy.stats import moyal
from scipy.stats import pearsonr
import math
import argparse
import matplotlib.pyplot as plt

def interpolator(arr,factor):
    
    out = []
    tmp = []
    for v in arr:
        for i in range(0,factor):
            tmp.append(v)
    y = tmp[0]
    for i in range(len(tmp)):
        y = 0.3*tmp[i] + 0.7*y
        out.append(y)
    return(out)
            
def decimator(arr,factor):
    tmp = []
    out = []
    
    for i in range(0,len(arr),factor):
        
        x = 0
        for j in range(0,factor):
            x = x + arr[i+j]
        x /= factor
        tmp.append(x)
    
    y = tmp[0]
    for i in range(len(tmp)):
        y = 0.3*tmp[i] + 0.7*y
        out.append(y)
    
    return(out)


parser = argparse.ArgumentParser(description="Analyse residual FRB pulse plot")

parser.add_argument("--infile", type=str, help="Input filename", required=True)
parser.add_argument("--threshold", type=float, help="Correlation threshold", default=0.6)
parser.add_argument("--debug", action='store_true', help="Enable debug", default=False)
parser.add_argument("--title", type=str, help="Plot title", default="FRB profile")
parser.add_argument("--crate", type=float, help="Channel rate", default=12500.0)


args = parser.parse_args()

  
#
# Generate a moyal curve, and extract the middle
#
curve=moyal.pdf(numpy.arange(-50,50,0.1))
curve=curve[300:300+400]

#
# Same curve, different timescale
#
curve2=moyal.pdf(numpy.arange(-50,50,0.1))
curve2=curve2[400:400+200]
curve2=interpolator(curve2,2)
curve2=numpy.add(curve2,0.0)

# Same curve, another different timescale
#
curve3=moyal.pdf(numpy.arange(-50,50,0.1))
curve3=curve3[450:450+100]
curve3=interpolator(curve3,4)
curve3=numpy.add(curve3,0.0)

#
# Same curve, yat another different timescale
#
curve4=moyal.pdf(numpy.arange(-50,50,0.1))
curve4=curve4[425:425+150]
curve4=interpolator(curve4,8)
curve4=decimator(curve4,3)

#
# Normalize  the curves
#
curve = numpy.divide(curve, numpy.max(curve))
curve2 = numpy.divide(curve2, numpy.max(curve2))
curve3 = numpy.divide(curve3, numpy.max(curve3))
curve4 = numpy.divide(curve4, numpy.max(curve4))



#
# Grab data from the .plt file
#
fp = open(args.infile, "r")
lines = fp.readlines()
fp.close()

#
# Go through the lines of data, and build a list
#  with the profile points.  The points are in the
#  2nd column, and the first column is just time offset.
#
analysed = []
num = len(lines)
for l in lines:
    toks = l.split()
    analysed.append(float(toks[1]))

#
# Pick out the middle 200 items from the profile data--
#  The code saves a 2-second "window" of data, but really
#   the pulse should be in the middle somewhere, and we
#   sample at around 12kHz
#
analysed = analysed[int(num/2)-100:int(num/2)+100]

#
# Normalize and adjust
#
# We're trying to adjust the pulse profile to be at the same
#  scale as the curves we're testing against
#
analysed = numpy.divide(analysed, numpy.max(analysed))
analysed = interpolator(analysed, 2)
analysed = numpy.subtract(analysed, numpy.min(analysed))
analysed = numpy.divide(analysed, numpy.max(analysed))


#
# Compute PearsonR correlation coefficients
#
coeffs = []
coeffs.append(pearsonr(analysed, curve)[0])
coeffs.append(pearsonr(analysed, curve2)[0])
coeffs.append(pearsonr(analysed, curve3)[0])
coeffs.append(pearsonr(analysed, curve4)[0])

if (args.debug == True):
    print (coeffs)

#
# Go through each coeff, testing for match condition
#
matched = False
for c in coeffs:
    if (c >= args.threshold):
        matched = True

if (matched == True):
    print ("Matched")
else:
    print ("No match")


if (args.debug == True):
    start = 0.0
    tincr = 1.0/(args.crate*2)
    tincr *= 1000.0
    xaxis = [x for x in numpy.arange(0,tincr*len(analysed),tincr)]
    mx = numpy.argmax(coeffs)
    plt.plot(xaxis,curve,label="Landau Curve: 1", linewidth=2.5 if mx == 0 else 1.0,
        linestyle="dashed" if mx == 0 else "solid")
        
    plt.plot(xaxis,curve2,label="Landau Curve: 2", linewidth=2.5 if mx == 1 else 1.0,
        linestyle="dashed" if mx == 1 else "solid")
        
    plt.plot(xaxis,curve3,label="Landau Curve: 3", linewidth=2.5 if mx == 2 else 1.0,
        linestyle="dashed" if mx == 2 else "solid")
        
    plt.plot(xaxis,curve4,label="Landau Curve: 4", linewidth=2.5 if mx == 3 else 1.0,
        linestyle="dashed" if mx == 3 else "solid")
        
    plt.plot(xaxis,analysed,label="Burst")
    plt.xlabel("Time (msec)")
    plt.ylabel("Normalized magnitude")
    plt.title(args.title)
    plt.grid(True)
    plt.legend()
    plt.show()
    #curve.tofile('curve.dat', sep="\n")
    #curve2.tofile('curve2.dat', sep="\n")
    #curve3.tofile('curve3.dat', sep="\n")
    #urve4.tofile('curve4.dat', sep="\n")
    #analysed.tofile('analysed.dat', sep="\n")
