# this module will be imported in the into your flowgraph
import os
import ephem
import time
import numpy as np
import shutil
import glob
import copy
import shutil
import json

movelist = []


def write_rate(fn, rate):
    fp = open(fn, "w")
    fp.write("%d\n" % rate)
    fp.close()
    return True


def compute_crate(fftsize,srate):
    rates = [x for x in range(8700,2500,-25)]
    for r in rates:
        d = float(srate)/float(fftsize)
        d /= float(r)
        
        if (d == float(int(d))):
            return r
    return 2500

    
