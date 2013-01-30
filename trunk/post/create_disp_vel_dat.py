#!/usr/local/bin/python2.7
'''
create_disp_vel_dat.py - create disp.dat and vel.dat files from a nodout file

This is replacing StuctPost, which relied on ls-prepost to extract data from
d3plot files, but no longer works gracefully on the cluster w/o GTK/video
support; now working with ASCII nodout files.  Also replaced the Matlab
scritps, so this should run self-contained w/ less dependencies.

2013-01-29 [mlp6]
* add Creative Commons license
* using argparse now for --help default value display

LICENSE:
This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License (CC BY-NC-SA 3.0)
http://creativecommons.org/licenses/by-nc-sa/3.0/
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2012-11-02"
__modified__ = "2013-01-29"
__email__ = "mark.palmeri@duke.edu"
__license__ = "CC BY-NC-SA 3.0"

def main():
    import os,sys,math
    import numpy as n
    
    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate disp.dat and vel.dat data from an ls-dyna nodout file.",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodout",help="ASCII file containing nodout data",default="nodout.gz")
    parser.add_argument("--disp",help="generate dispout file [Boolean (flag for true)]",action='store_true')
    parser.add_argument("--dispout",help="name of the binary displacement output file",default="disp.dat")
    parser.add_argument("--vel",help="generate velout file [Boolean (flag for true)]",action='store_true')
    parser.add_argument("--velout",help="name of the binary velocity output file",default="vel.dat")

    args = parser.parse_args()
    disp = args.disp
    vel = args.vel

    # open dispout and velout for binary writing
    if disp:
	dispout = open(args.dispout,'wb')
    if vel:
        velout = open(args.velout,'wb')

    # open nodout file
    if args.nodout.endswith('gz'):
        import gzip
        nodout = gzip.open(args.nodout,'r')
    else:
        nodout = open(args.nodout,'r')

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
    ls-dyna seems to drop the 'E' when the negative exponent is 100, so check for those in the line
    data and add the 'E' so that we can convert to floats
    '''
    import re
    for i in range(len(raw_data)):
        raw_data[i] = re.sub(r'(?<!E)\-1[0-9][0-9]','E-100',raw_data[i])
    return raw_data
##################################################################################################
if __name__ == "__main__":
    main()
