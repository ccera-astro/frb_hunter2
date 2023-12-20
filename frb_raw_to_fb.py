#!/usr/bin/env python3
import numpy as np
import os
import sys
import struct
import calendar
import json

import argparse

    
def write_fb_header(fn, fp, srate, freq, bandwidth, declination, ra, evu, sname, ffts):
    sn = "???" if sname == None else sname
    build_header_info(fn, fp, sn, ra, declination, freq, bandwidth, srate, ffts, evu)
   
#
# Convert to the weirdness that is the hybrid floating-point
#  time format used by SIGPROC
#
def convert_sigproct(v):
    sign = 1.0
    if (v < 0.0):
        sign = -1.0
    v = abs(v)
    itime = int(float(v)*3600.0)
    hours = int(itime/3600)
    minutes = int((itime-(hours*3600))/60)
    seconds = itime - (hours*3600) - (minutes*60)
    timestr="%02d%02d%02d.0" % (sign*hours, minutes, seconds)
    return(float(timestr))
#
# This will cause a header block to be prepended to the output file
#
# Thanks to Guillermo Gancio (ganciogm@gmail.com) for the inspiration
#   and much of the original code
#
# This seems to be broken for Python3
#
#
# This will cause a header block to be prepended to the output file
#
# Thanks to Guillermo Gancio (ganciogm@gmail.com) for the inspiration
#   and much of the code
#
#
import time
import struct
import sys

def write_element_name(fp,elem):
    fp.write(struct.pack('i',len(elem)))
    if (sys.version_info[0] >= 3):
        fp.write(bytes(elem, encoding='utf8'))
    else:
        fp.write(elem)

def write_element_data(fp,elem,t):
    if (t != None and t != "str"):
        fp.write(struct.pack(t, elem))
    else:
        fp.write(struct.pack('i', len(elem)))
        if (sys.version_info[0] >= 3):
            fp.write(bytes(elem, encoding='utf8'))
        else:
            fp.write(elem)

#
# Build the header for the output .FIL
#
# We get called via a poller in the flow-graph at a fairly-brisk pace
#  so that we can enable writing of the actual data as soon as possible.
#
def build_header_info(fn, fp,source_name,source_ra,source_dec,freq,bw,fbrate,fbsize,first):

    #
    # Time for one sample, in sec
    #
    tsamp=1.0/float(fbrate)

    #
    # Frequency offset between channels, in MHz
    # Negative to indicate channels are ordered highest-to-lowest
    #  some older tooling *REQUIRES* this ordering, so might
    #  as well follow the tradition, and that's the way the
    #  flow-graph and de-dispersion is also organized.
    #
    f_off=bw/fbsize
    f_off /= 1.0e6
    f_off *= -1

    #
    # Highest frequency represented in FB, in MHz
    #
    high_freq = freq+(bw/2.0)
    high_freq  /= 1.0e6
    high_freq -= (f_off/2.0)

    #
    # Lowest
    #
    low_freq = freq-(bw/2.0)
    low_freq /= 1.0e6
    low_freq += (f_off/2.0)

    #
    # Number of subbands
    #
    sub_bands=fbsize


    #
    # MJD
    # Good to within probably 50ms of system time
    #
    t_start = (first/86400.0)+40587.0;

    #
    # The rest here is mostly due to Guillermo Gancio ganciogm@gmail.com
    #
    # With considerable updates done here to support Python3
    #
    stx="HEADER_START"
    write_element_name(fp,stx)

    #-- Establish file type and name
    #
    write_element_name(fp,"rawdatafile")
    write_element_data(fp, fn, "str")

    #-- Source RA (J2000)
    #
    write_element_name(fp, "src_raj")
    source_ra = convert_sigproct(source_ra)
    write_element_data (fp, source_ra, 'd')

    #-- Source DEC (J2000)
    #
    write_element_name(fp, "src_dej")
    source_dec= convert_sigproct(source_dec)
    write_element_data(fp, source_dec, 'd')
    
    #--
    #
    write_element_name(fp, "az_start")
    write_element_data(fp, 0.0, 'd')

    #--
    #
    write_element_name(fp, "za_start")
    write_element_data(fp, 0.0, 'd')

    #-- MJD of first sample -- approximately
    #
    write_element_name(fp, "tstart")
    write_element_data(fp, float(t_start), 'd')

    #-- Frequency spacing between channels
    #
    write_element_name(fp, "foff")
    write_element_data(fp, f_off, 'd')

    #-- Frequency of 1st (lowest) channel in the FB
    #
    write_element_name(fp, "fch1")
    write_element_data(fp, high_freq, 'd')

    #-- Number of channels in the FB
    #
    write_element_name(fp, "nchans")
    write_element_data(fp, sub_bands, 'i')

    #-- Data type--raw data
    #
    write_element_name(fp, "data_type")
    write_element_data(fp, 1, 'i')

    #-- ???
    #
    write_element_name(fp, "ibeam")
    write_element_data(fp, 1, 'i')

    #-- Data bits: either 8 bit int or 32-bit float
    #
    write_element_name(fp, "nbits")
    nb = 32
    write_element_data(fp, nb, 'i')

    #-- Sample period
    #
    write_element_name(fp, "tsamp")
    write_element_data(fp, tsamp, 'd')

    #-- Single beam
    #
    write_element_name(fp, "nbeams")
    write_element_data(fp, 1, 'i')

    #-- Single IF (fom one polarization)
    #
    write_element_name(fp, "nifs")
    write_element_data(fp, 1, 'i')

    #-- The catalog name of the source
    #
    write_element_name(fp, "source_name")
    write_element_data(fp, source_name, "str")

    #-- Machine id.  Arbitrary
    #
    write_element_name(fp, "machine_id")
    write_element_data(fp, 20, 'i')

    #-- Telescope id.  Arbitrary
    #
    write_element_name(fp, "telescope_id")
    write_element_data(fp, 20, 'i')

    #-- End of header
    etx="HEADER_END"
    write_element_name(fp, etx)
    
    return True

def main():
    #
    # Main
    #
    parser = argparse.ArgumentParser(description="Process bulk de-disp output file")
    parser.add_argument("--infile", help="Input filename", required=True)
    parser.add_argument("--srate", type=float, help="Sample rate", required=True)
    parser.add_argument("--freq", type=float, help="Center Frequency", required=True)
    parser.add_argument("--bandwidth", type=float, help="Bandwidth", required=True)
    parser.add_argument("--decln", type=float, help="Declination", required=True)
    parser.add_argument("--outfile", type=str, help="Output file", required=True)
    parser.add_argument("--json", type=str, help="Housekeeping JSON file", default=None)
    parser.add_argument("--offset", type=float, help="Event time offset", default=0.0)
    parser.add_argument("--fftsize", type=int, help="FFT bins", default=32)
    parser.add_argument("--lmst", type=float, help="LMST of event", default=None)
    parser.add_argument("--sname", type=str, help="Name of Source", default=None)
    

    args = parser.parse_args()
    
    resid = 0.0
    #
    # Load JSON file that contains lots of meaty things
    #
    if (args.json != None):
        jfp = open(args.json, "r")
        jdict = json.load(jfp)
        jfp.close()
        
        #
        # Parse the event time:
        #
        # YYYY MM DD hh:mm:ss
        #
        evtoks = jdict["date"].split()
        ltp = time.gmtime()
        
        tm_year = int(evtoks[0])
        tm_mon = int(evtoks[1])
        tm_mday = int(evtoks[2])
        
        
        todtoks = jdict["evtime"].split(":")
        
        tm_hour = int(todtoks[0])
        tm_min = int(todtoks[1])
        tm_sec = int(float(todtoks[2]))
    else:
        mt = os.stat(args.infile).st_mtime
        
        #
        # Get file size, convert to number of records
        #
        sz = os.stat(args.infile).st_size
        sz /= 4
        sz /= args.fftsize
        
        #
        # Turn that into time, subtract to derive start time
        #
        toff = sz * (1.0 / float(args.srate))
        mt -= toff
        evutime = mt
        
    if (args.json != None):
        #
        # Convert into struct_time
        #
        ltp = time.struct_time((tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec,
            0, 0, -1))
        
        #
        # Then interpret it as GMT -- why the "time" module doesn't have this,
        #  I dunno.
        #
        evutime = calendar.timegm(ltp)
        evutime -= args.offset
        evutime += resid

    #
    # Open output file
    #
    ofp = open(args.outfile, "wb")


    #
    # Determine LMST from input JSON
    # We use LMST as RA, because our site uses meridan-transit
    #   antenna.
    #
    #
    if (args.json != None):
        lmst_toks = jdict["lmst"]
        lmst_toks = lmst_toks.split(",")
        lmst = float(lmst_toks[0])
        lmst += float(lmst_toks[1])/60.0
        lmst += float(lmst_toks[2])/3600.0
    else:
        lmst = args.lmst
    
    #
    # Bring in the input file as 32-bit floats and make into
    #  1D NUMPY array.
    #
    vals = np.fromfile(args.infile, dtype=np.float32)
    cols = args.fftsize
    rows = int(len(vals)/args.fftsize)

    #
    # Reshape into 2D
    #
    vals = np.reshape(vals, (rows,cols))


    #
    # We have enough for the SIGPROC header
    #
    write_fb_header(args.outfile, ofp, args.srate, args.freq, args.bandwidth, args.decln, lmst, evutime,
        args.sname, args.fftsize)


    #
    # Iterate through the rows, reversing each row
    #  (Because SIGPROC requires the channels in reverse order)
    #
    for row in vals:
        irow = list(row)
        irow.reverse()
        s = struct.pack('f'*len(irow), *irow)
        ofp.write(s)
    ofp.close()

if __name__ == "__main__":
    main()
