'''
create_disp_vel_dat.py - create disp.dat and vel.dat files from a nodout file

This is replacing StuctPost, which relied on ls-prepost to extract data from
d3plot files, but no longer works gracefully on the cluster w/o GTK/video
support; now working with ASCII nodout files.  Also replaced the Matlab
scritps, so this should run self-contained w/ less dependencies.
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2012-11-02"
__modified__ = "2012-12-31"
__email__ = "mark.palmeri@duke.edu"

def main():
    import os,sys,math
    import numpy as n
    
    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate disp.dat and vel.dat data from an ls-dyna nodout file.")
    parser.add_argument("--nodout",help="ASCII file containing nodout data [default = nodout]",default="nodout")
    parser.add_argument("--disp",help="generate dispout file [Boolean (flag for true)]",action='store_true')
    parser.add_argument("--dispout",help="name of the binary displacement output file [default = disp.dat]",default="disp.dat")
    parser.add_argument("--vel",help="generate velout file [Boolean (flag for true)]",action='store_true')
    parser.add_argument("--velout",help="name of the binary velocity output file [default = vel.dat]",default="vel.dat")

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
                sys.stdout.write('  Time Step: ')
            sys.stdout.write('%i ' % timestep_count)
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
        vevlout.close()
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
    numTScmd = 'grep time %s | wc -l' % outfile.name
    header['numtimesteps'] = int(subprocess.check_output(numTScmd, shell=True))
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
        for i in range(0,data.__len__()):
            outfile.write(struct.pack('ffff',data[i][0],data[i][1],data[i][2],data[i][3]))
    if outtype == 'vel': 
        for i in range(0,data.__len__()):
            outfile.write(struct.pack('ffff',data[i][0],data[i][4],data[i][5],data[i][6]))
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
