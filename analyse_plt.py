#!/usr/bin/python3
import numpy
import os
import time
import sys
from scipy.stats import moyal
from scipy.stats import pearsonr
import math
import argparse

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



fp = open(args.infile, "r")
lines = fp.readlines()

analysed = []
num = len(lines)
for l in lines:
    toks = l.split()
    analysed.append(float(toks[1]))

#
# Pick out the middle 200 items
#
analysed = analysed[int(num/2)-100:int(num/2)+100]

#
# Normalize and adjust
#
analysed = numpy.divide(analysed, numpy.max(analysed))
analysed = interpolator(analysed, 2)
analysed = numpy.subtract(analysed, numpy.min(analysed))
analysed = numpy.divide(analysed, numpy.max(analysed))


#
# Compute pearson correlation coefficients
#
coeffs = []
coeffs.append(pearsonr(analysed,curve)[0])
coeffs.append(pearsonr(analysed, curve2)[0])
coeffs.append(pearsonr(analysed, curve3)[0])
coeffs.append(pearsonr(analysed, curve4)[0])

#print (coeffs)

matched = False
for c in coeffs:
    if (c >= args.threshold):
        matched = True

if (matched == True):
    print ("Matched")
else:
    print ("No match")


"""
curve.tofile('curve.dat', sep="\n")
curve2.tofile('curve2.dat', sep="\n")
curve3.tofile('curve3.dat', sep="\n")
curve4.tofile('curve4.dat', sep="\n")
analysed.tofile('analysed.dat', sep="\n")
"""




