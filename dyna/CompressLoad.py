#!/usr/local/bin/python2.7
'''
CompressLoad.py - Generate compression conditions for the top surface of the specified mesh.  Search through the provided node file, extract the top layer of nodes and write out point loads for each matching node. Nodes are written in spatially-sorted order

This code was based on the older CompressLoad.pl and on bc.py

MODIFICATION HISTORY:
v0.2 (Mark Palmeri [2011-11-09])
Imported SortNodeIDs and extractPlane from bc.py instead of having them copied here.
'''

__author__ = "Nick Bottenus (nbb5)"
#__date__ = "2011-10-06"
__date__ = "2011-11-09"
__version__ = "0.2"

def main():
    import pdb 
    import os,sys,math
    import numpy as n
    from bc import SortNodeIDs, extractPlanes

    if sys.version < '2.6':
        sys.exit("ERROR: Requires Python >= v2.6")

    from optparse import OptionParser

    # lets read in some command-line arguments
    parser = OptionParser(usage="Generate compression conditions for the top surface of the specified mesh.  \n\n%prog [OPTIONS]...",version="%s" % __version__)
    parser.add_option("--loadfile",dest="loadfile",help="compression load defintion output file [default = %default]",default="topload.dyn")
    parser.add_option("--nodefile",dest="nodefile",help="node definition input file [default = %default]",default="nodes.dyn")

    (opts,args) = parser.parse_args()

    # open the top load file to write
    LOADFILE = open(opts.loadfile,'w')
    LOADFILE.write("*BOUNDARY_PRESCRIBED_MOTION_NODE\n")
    LOADFILE.write("$ Generated using %s (version %s) with the following options:\n" % (sys.argv[0],__version__))
    LOADFILE.write("$ %s\n" % opts)
    
    # load in all of the node data, excluding '*' lines
    nodeIDcoords = n.loadtxt(opts.nodefile, delimiter=',', comments='*', dtype=[('id','i4'),('x','f4'),('y','f4'),('z','f4')])

    # there are 6 faces in these models; we need to (1) find the top face and (2) apply the appropriate loads
    [snic, axes] = SortNodeIDs(nodeIDcoords)
    
    # extract spatially-sorted node IDs on a the top z plane
    plane = (2,axes[2].max())
    planeNodeIDs = extractPlane(snic,axes,plane)

    # write out nodes on the top z plane with corresponding load values 
    #(direction of motion, nodal displacement (accel, vel, etc), temporal load curve ID, scale factor for load curve)
    writeNodeLoads(LOADFILE,planeNodeIDs,'3,2,1,-1.0')
    LOADFILE.write("*END\n")

    # close all of our files open for read/write
    LOADFILE.close()

#############################################################################################################################
def writeNodeLoads(LOADFILE,planeNodeIDs,dofs):
    import pdb
    for i in planeNodeIDs:
	for j in i:
	 	LOADFILE.write("%i,%s\n" % (j[0],dofs))
#############################################################################################################################
    
if __name__ == "__main__":
    main()

