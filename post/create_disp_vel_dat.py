#!/bin/env python
"""
create_disp_vel_dat.py

Create disp.dat and vel.dat files from a nodout file.

This is replacing StuctPost, which relied on LS-PREPOST, to extract data from
d3plot* files.  (LS-PREPOST no longer works gracefully on the cluster w/o
GTK/video support.)  Instead of working with d3plot files, this approach now
utilizes ASCII nodout files.  Also replaced the Matlab scritps, so this should
run self-contained w/ less dependencies.

EXAMPLE
=======
create_disp_vel_dat.py --disp

=======
The MIT License (MIT)

Copyright (c) 2014 Mark L. Palmeri

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

__author__ = "Mark Palmeri (mlp6)"
__email__ = "mlp6@duke.edu"
__date__ = "2012-11-02"
__modified__ = "2013-07-29"
__license__ = "GPLv3"

def main():
    import os, sys, math
    import numpy as n

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description = "Generate disp.dat and vel.dat data from an ls-dyna nodout file.", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodout", help="ASCII file containing nodout data", default="nodout.gz")
    parser.add_argument("--disp", help="generate dispout file [Boolean (flag for true)]", action='store_true')
    parser.add_argument("--dispout", help="name of the binary displacement output file", default="disp.dat")
    parser.add_argument("--vel", help="generate velout file [Boolean (flag for true)]", action='store_true')
    parser.add_argument("--velout", help="name of the binary velocity output file", default="vel.dat")

    args = parser.parse_args()
    disp = args.disp
    vel = args.vel

    # check to make sure that at least one of disp or vel is output
    if args.disp is False and args.vel is False:
        sys.exit("ERROR: You are running this scipt without any output being created.  Specify --disp and/or --vel during execution.")

    # open dispout and velout for binary writing
    if disp:
	dispout = open(args.dispout, 'wb')
    if vel:
        velout = open(args.velout, 'wb')

    # open nodout file
    if args.nodout.endswith('gz'):
        import gzip
        nodout = gzip.open(args.nodout, 'r')
    else:
        nodout = open(args.nodout, 'r')

    header_written = False
    timestep_read = False
    timestep_count = 0
    for line in nodout:
        if line.__contains__('nodal'):
            timestep_read = True
            timestep_count = timestep_count + 1
            if timestep_count == 1:
                sys.stdout.write('Time Step: ')
                sys.stdout.flush()
            sys.stdout.write('%i ' % timestep_count)
            sys.stdout.flush()
            data = []
            continue
        if timestep_read is True:
            if line.startswith('\n'): # done reading the time step
                timestep_read = False
                if not header_written: # if this was the first time, everything needed
                                       # to be read to get node count for header
                    header = generate_header(data,nodout)
                    if disp:
                        write_headers(dispout,header)
                    if vel:
                        write_headers(velout,header)
                    header_written = True
		if disp:
                    process_timestep_data(data,'disp',dispout)
		if vel:
                    process_timestep_data(data,'vel',velout)
            else:
                raw_data = line.split()
                corrected_raw_data=correct_Enot(raw_data)
                data.append(map(float, corrected_raw_data))

    # close all open files
    if disp:
        dispout.close()
    if vel:
        velout.close()
    nodout.close()
##################################################################################################
def generate_header(data,outfile):
    '''
    generate headers from data matrix of first time step
    '''
    import subprocess
    header = {}
    header['numnodes'] = data.__len__()
    header['numdims'] = 4 # node ID, x-val, y-val, z-val
    if outfile.name.endswith('gz'):
        numTScmd = 'zgrep time %s | wc -l' % outfile.name
    else:
        numTScmd = 'grep time %s | wc -l' % outfile.name
    header['numtimesteps'] = int(subprocess.check_output(numTScmd, shell=True))-1 # one extra line is detected, so subtract 1
    return header
##################################################################################################
def write_headers(outfile,header):
    '''
    write binary header information to reformat things on read downstream
    'header' is a dictionary containing the necessary information
    '''
    import struct
    outfile.write(struct.pack('fff',header['numnodes'],header['numdims'],header['numtimesteps']))
##################################################################################################
def process_timestep_data(data,outtype,outfile):
    import struct
    if outtype == 'disp':
        for i in [0,1,2,3]: # write all node IDS, then x-val, then y-val, then z-val
            for j in range(len(data)):  # loop over all nodes
                outfile.write(struct.pack('f',data[j][i]))
    if outtype == 'vel':
        for i in [0,4,5,6]: # write all node IDS, then x-val, then y-val, then z-val
            for j in range(len(data)):  # loop over all nodes
                outfile.write(struct.pack('f',data[j][i]))
##################################################################################################
def correct_Enot(raw_data):
    '''
    ls-dyna seems to drop the 'E' when the negative exponent is three digits, so check for those in the line
    data and change those to 'E-100' so that we can convert to floats
    '''
    import re
    for i in range(len(raw_data)):
        raw_data[i] = re.sub(r'(?<!E)\-[1-9][0-9][0-9]','E-100',raw_data[i])
    return raw_data
##################################################################################################
if __name__ == "__main__":
    main()
