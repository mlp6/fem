'''
create_disp_vel_dat.py - create disp.dat and vel.dat files from a nodout file

This is replacing StuctPost, which relied on ls-prepost to extract data from
d3plot files, but no longer works gracefully on the cluster w/o GTK/video
support; now working with ASCII nodout files.  Also replaced the Matlab
scritps, so this should run self-contained w/ less dependencies.
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2012-11-02"
__modified__ = "2012-12-22"
__email__ = "mark.palmeri@duke.edu"

'''
% INPUTS:   ModelType - 'struct' or 'therm' 
%           NoFiles - number of t*.asc files to convert
%
% OUTPUT: disp/therm.dat is written to CWD
%           All data is float32 with the format:
%               NUM_NODES
%               NUM_DIMS (Node ID, X, Y, Z displacements)
%               NUM_TIMESTEPS
%               The rest of the data are the concatenation of NUM_NODES x NUM_DIMS x NUM_TIMESTEPS.
'''


def main():
    import os,sys,math
    import numpy as n
    
    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate disp.dat and vel.dat data from an ls-dyna nodout file.")
    parser.add_argument("--nodout",help="ASCII file containing nodout data [default = nodout]",default="nodout")
    parser.add_arfument("--disp",help="generate dispout file [default = True]",store=True)
    parser.add_argument("--dispout",help="name of the binary displacement output file [default = disp.dat]",default="disp.dat")
    parser.add_arfument("--vel",help="generate velout file [default = False]",store=False)
    parser.add_argument("--velout",help="name of the binary velocity output file [default = vel.dat]",default="vel.dat")

    args = parser.parse_args()

    # open dispout and velout for binary writing
    if disp:
	dispout = open(args.dispout,'wb')
    if vel:
        velout = open(args.velout,'wb')

    # open nodout file
    nodout = open(nodout,'r')

    header_written = False
    timestep_read = False
    for line in nodout:
        if line.__contains__('nodal'):
            timestep_read = True
            data = []
            continue
        if timestep_read is True:
            if line.startwith('\n'):
                timestep_read = False
                if not header_written:
                    header = generate_header(data)
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
                data.append(map(float, line.split()))

    # close all open files
    if dispout:
        dispout.close()
    if velout:
        vevlout.close()
    nodout.close()
##################################################################################################
def generate_header(data,outfile):
    '''
    generate headers from data matrix of first time step
    '''
    import subprocess
    header={'numnodes' : data.__len__()}
    header={'numdims' : 3}
    numTScmd = 'grep time %s | wc -l' % outfile.name
    header={'numtimesteps' : int(subprocess.check_output(numTScmd, shell=True))} 
##################################################################################################
def write_headers(outfile,header):
    '''
    write binary header information to reformat things on read downstream
    'header' is a dictionary containing the necessary information
    '''
    import struct
    outfile.write(struct.pack('f',header{'numnodes'},header{'numdims'},header{'numtimesteps'}))
##################################################################################################
def process_timestep_data(data,outtype,outfile):
    if outtype == 'disp':
        outfile.write(struct.pack('f',[data[i][0:3] for i in range(0,data.__len__())]))
    if outtype == 'vel': 
        outfile.write(struct.pack('f',[data[i][4:7] for i in range(0,data.__len__())]))
##################################################################################################
if __name__ == "__main__":
    main()
