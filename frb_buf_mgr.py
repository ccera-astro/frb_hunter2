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

recently_triggered = 0
events = []
def cur_sidereal(longitude):
    longstr = "%02d" % int(longitude)
    longstr = longstr + ":"
    longitude = abs(longitude)
    frac = longitude - int(longitude)
    frac *= 60
    mins = int(frac)
    longstr += "%02d" % mins
    longstr += ":00"
    x = ephem.Observer()
    x.date = ephem.now()
    x.long = longstr
    jdate = ephem.julian_date(x)
    tokens=str(x.sidereal_time()).split(":")
    hours=int(tokens[0])
    minutes=int(tokens[1])
    seconds=int(float(tokens[2]))
    sidt = "%02d,%02d,%02d" % (hours, minutes, seconds)
    return (sidt)

def save_frb_spectra(trig_val, fn,fftsize,longitude,prefix,decln,thresh,freq,bw,crate):
    global recently_triggered
    global events
    if (trig_val > thresh):
        if (recently_triggered <= 0):
            evt = time.time()
            ltp = time.gmtime(evt)
            frac = evt-float(int(evt))
            events.append(int(evt))
            newfn = "frb-event-%d" % (int(evt))
            sidt = cur_sidereal(longitude)
            sidbits = sidt.split(",")
            newfn += ".json"
            evdict = {}
            evdict["year"] = ltp.tm_year
            evdict["month"] = ltp.tm_mon
            evdict["day"] = ltp.tm_mday
            evdict["hour"] = ltp.tm_hour
            evdict["minute"] = ltp.tm_min
            evdict["second"] = ltp.tm_sec
            evdict["lmst_hour"] = int(sidbits[0])
            evdict["lmst_minute"] = int(sidbits[1])
            evdict["lmst_second"] = int(sidbits[2])
            evdict["frequency"] = freq
            evdict["bandwidth"] = bw
            evdict["chan_rate"] = crate
            evdict["declination"] = decln
            evdict["fftsize"] = fftsize
            evdict["threshold"] = thresh
            fp = open (prefix+newfn, "w")
            fp.write(json.dumps(evdict, indent=4))
            fp.write("\n")
            fp.close()
            
            #
            # Prevent re-triggering immediately
            #
            recently_triggered = 240
        else:
            recently_triggered -= 1
        
    return True

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
    
    
    
