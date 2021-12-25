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

def ts_file(pacer,ts,prefix):
    fn = prefix + "ts-" + "%d" % (int(ts)) + ".txt"
    fp = open(fn, "w")
    fp.write ("%.2f\n" % ts)
    fp.close()
    return True

recently_triggered = 0
events = []

def add_event(event):
	global events
	events.append(event)

def harvest(pacer,prefix,permdir):
    global events
    flist = glob.glob(prefix+"frb-buffer-*")
    myevents = copy.deepcopy(events)
    
    #
    # Harvest data that isn't associated with an event
    #
    for f in flist:
        ts = f.replace(prefix+"frb-buffer-", "")
        ts = int(ts)
        
        #
        # Time-indicator on file shows it is in the events list
        #
        if (ts in myevents or ts+1 in myevents or ts-1 in myevents):
            continue
        
        #
        # File cannot be removed unless it isn't in "myevents" AND it hasn't
        #  been touched in 5 seconds or more
        #
        sts = os.stat(f)
        if ((time.time() - sts.st_mtime) > 5):
            os.remove(f)
    #
    # Anything that has survived the above gauntlet and is older than 10 seconds
    #  likely deserves to be preserved as "event data"
    #
    for f in flist:
        if (os.path.exists(f)):
            sts = os.stat(f)
            if ((time.time() - sts.st_mtime) > 10):
                ts = f.replace(prefix+"frb-buffer-", "")
                ts = int(ts)
                
                #
                # Confirm in event data
                #
                if (ts in myevents or ts+1 in myevents or ts-1 in myevents):
                    f2 = f.replace("buffer", "evdata")
                    f2 += ".bin"
                    shutil.move(f,permdir+os.path.basename(f2))
                    f2 = f.replace("frb-buffer-", "frb-event-")
                    f2 += ".json"
                    if (os.path.exists(f2)):
                        shutil.move(f2, permdir+os.path.basename(f2))
                
    return True
    
    
    
