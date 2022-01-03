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

#
# Helper to produce a vector that is mostly zeros, but with 1s in the middle 10%
#
def tp_vector(fftsize):
    rvec = [0.0]*fftsize
    mid = int(fftsize/2)
    tenp = float(fftsize)*0.1
    tenp = int(tenp)
    fivep = int(tenp/2)
    for ndx in range(mid-fivep,mid+fivep+1):
        rvec[ndx] = 1.0
    return rvec

def harvest(pacer,prefix,permdir,seconds):
    global movelist
    
    #
    # Handle files on the "movelist"
    #
    for f in movelist:
        shutil.move(f,permdir)
    
    movelist = []
    
    #
    # Harvest data that isn't associated with an event
    #
    
    #
    # First find "event" files in the buffer directory
    #
    flist = glob.glob(prefix+"frb-event-*")
    
    #
    # Create empty event dictionary
    #
    evdict = {}
    for f in flist:
        sts = os.stat(f)
        #
        # Add event only if it's "fresh"
        #
        if ((time.time() - sts.st_mtime) <= seconds*10):
            evdict[f] = sts.st_mtime
        
        #
        # Otherwise, remove
        #
        else:
            os.remove(f)
            
    #
    # Find matching buffer file
    #
    flist = glob.glob(prefix+"frb-buffer-*")
    for f in flist:
        sts = os.stat(f)
        
        #
        # We have a buffer file, see if there's a matching "event" file
        #
        for ev in evdict:
            #
            # If the event falls within the purview of the buffer file
            #
            if sts.st_mtime > evdict[ev] and (sts.st_mtime-seconds) < evdict[ev]:
                #
                # Move event file to perm directory
                #
                try:
                    shutil.move(ev,permdir)
                except:
                    pass
                
                if ((time.time() - sts.st_mtime) > seconds):
                    try:
                        shutil.move(f,permdir)
                    except:
                        pass
                else:
                    #
                    # Defer buffer movement to next cycle--buffer may be partially-full
                    #
                    movelist.append(f)
                
    
    #
    # Delete buffers that are old enough and didn't match any events
    #
    for f in flist:
        if (f not in movelist):
            if os.path.exists(f):
                sts = os.stat(f)
                if ((time.time() - sts.st_mtime) > seconds*10):
                    os.remove(f)        
        
    return True

def write_rate(fn, rate):
    fp = open(fn, "w")
    fp.write("%d\n" % rate)
    fp.close()
    return True


def compute_crate(fftsize,srate):
    rates = [x for x in range(6500,2500,-25)]
    
    for r in rates:
        d = float(srate)/float(fftsize)
        d /= float(r)
        
        if (d == float(int(d))):
            return r
    return 2500

    
