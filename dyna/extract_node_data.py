#!/usr/local/bin/python2.7
'''
extract_node_data.py - extract nodal time history ASCII files from d3plot files.

This code is based on some of the functionality in the older StructPost and
ThermalPost perl scripts.
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2012-02-14"
__version__ = "0.1"


def main():
    import sys, os
    import numpy as n

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate result dat/mat files from FE data.  \n\nPROG [OPTIONS]...",version="%s" % __version__)
    parser.add_argument("--dynadeck",dest="dynadeck",help="path for the dyna input deck [default = arfi.dyn]",default="arfi.dyn")
    parser.add_argument("--nodes",dest="nodes",help="path to node definitions [default = nodes.dyn]",default="nodes.dyn")
    parser.add_argument("--fcomp",dest="fcomp",help="type of output data to extract [default = disp]; other options include vel, vms, maxshear, thermal",default="disp")
    parser.add_argument("--lspp",dest="lspp",help="absolute path for ls-prepost [default = /usr/local/bin/ls-prepost2]",default="/usr/local/bin/ls-prepost2")

    args = parser.parse_args()

    TerminationTime = extractTime(args.dynadeck,'*CONTROL_TERMINATION')
    TimeStep = extractTime(args.dynadeck,'*DATABASE_BINARY_D3PLOT')
    NumTimeSteps = int(TerminationTime/TimeStep)

    cfile = lspp_cfile(args.fcomp,sys.argv[0],__version__,NumTimeSteps)

    os.system('%s -nographics c=%s' % (args.lspp,cfile))

    print('Post-processing of model results is complete.\n')

#############################################################################################################################
def lspp_cfile(fcomp,commandline,ver,NumTimeSteps):
    import os
    cfile = 'lspp.cfile'
    LSPP_CFILE = open(cfile,'w')
    LSPP_CFILE.write("$ Generated using %s (version %s) with fcomp = %s\n" % (commandline,ver,fcomp))
    LSPP_CFILE.write('open d3plot d3plot\n')
    LSPP_CFILE.write('fringe 25\n')
    for t in range(1,NumTimeSteps+1):
        if fcomp == 'disp':
            LSPP_CFILE.write('output ./node_data_%i.asc %i 1 0 1 0 0 1 0 0 0 0 0 0\n' % (t,t))
        elif fcomp == 'maxshear':
            LSPP_CFILE.write('output ./node_data_t%i.asc %i 1 0 1 0 0 0 0 0 1 0 0 0 0 0\n' % (t,t))
        elif fcomp == 'vel':
            LSPP_CFILE.write('output ./node_data_t%i.asc %i 1 0 1 0 0 0 1 0 0 0 0 0 0 0\n' % (t,t))
        elif fcomp == 'thermal':
            LSPP_CFILE.write('output ./node_data_t%i.asc %i 1 0 1 0 0 0 0 0 1 0 0 0\n' % (t,t));
        # NEED TO STILL ADD VMS OPTION
    LSPP_CFILE.close()
    return cfile

#############################################################################################################################
def extractTime(dynadeck,keyword):
    '''
    Extract either termination time or dump time for d3plot files to compute the number of time steps that need to be extracted.
    The time of interest is the first number on the line after the specified keyword.
    '''

    deckfid = open(dynadeck,'r')

    work_next_line = 0

    for line in deckfid:
        if work_next_line == 1:
            return float(line.split(',')[0])
        elif line.startswith(keyword):
            work_next_line = 1
        
    deckfid.close()

#############################################################################################################################
    
if __name__ == "__main__":
    main()
