#!/usr/bin/env python3
import numpy as np
import os
import sys

import argparse

parser = argparse.ArgumentParser(description="Process bulk de-disp output file")
parser.add_argument("--infile", help="Input filename", required=True)
parser.add_argument("--srate", type=float, help="Sample rate", required=True)

args = parser.parse_args()

vals = np.fromfile(args.infile, dtype=np.float32)
sincr = 1.0 / args.srate

start = 0.0
for v in vals:
    sys.stdout.write("%f %13.8f\n" % (start*1000.0, v))
    start += sincr
    
