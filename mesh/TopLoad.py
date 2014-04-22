#!/usr/local/bin/python2.7
'''
TopLoad.py - Generate compression conditions for the top surface of
the specified mesh.  Search through the provided node file, extract the top
layer of nodes and write out point loads for each matching node. Nodes are
written in spatially-sorted order.

This code was based on the older CompressLoad.pl and on bc.py

MODIFICATION HISTORY:
v0.2 (Mark Palmeri [2011-11-09])
Imported SortNodeIDs and extractPlane from bc.py instead of having them copied
here.

v0.3 (Mark Palmeri, 2013-01-10)
* converted from OptionParser to argparse
* renamed to more general "TopLoad.py" from "CompressLoad.py"
* added new inputs for direction, loadtype, amplitude and LCID

v0.3.1 (Mark Palmeri, 2013-01-17)
* fixed amplitude formatted print output from %i -> %f

v0.3.2 (Mark Palmeri, 2013-01-29)
* using argparse to display default options on --help

LICENSE:
This work is licensed under a Creative Commons
Attribution-NonCommercial-ShareAlike 3.0 Unported License (CC BY-NC-SA 3.0)
http://creativecommons.org/licenses/by-nc-sa/3.0/
'''

__author__ = "Mark Palmeri "
__email__ = "mark.palmeri@duke.edu"
__created__ = "2011-11-09"
__modified__ = "2013-01-29"
__version__ = "0.3.2"
__license__ = "CC BY-NC-SA 3.0"


def main():
    import sys
    import numpy as n
    from bc import SortNodeIDs, extractPlane
    import fem_mesh

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    opts = read_cli()
    loadtype = opts.loadtype
    direction = int(opts.direction)
    amplitude = float(opts.amplitude)
    lcid = int(opts.lcid)

    # open the top load file to write
    LOADFILE = open(opts.loadfile, 'w')
    if loadtype == 'disp' or loadtype == 'vel' or loadtype == 'accel':
        LOADFILE.write("*BOUNDARY_PRESCRIBED_MOTION_NODE\n")
    elif loadtype == 'force':
        LOADFILE.write("*LOAD_NODE_POINT\n")
    else:
        sys.exit('ERROR: Invalid loadtype specified (can only be disp, '
                 'force, vel or accel)')

    LOADFILE.write("$ Generated using %s (version %s) with the following "
                   "options:\n" % (sys.argv[0], __version__))
    LOADFILE.write("$ %s\n" % opts)

    # load in all of the node data, excluding '*' lines
    nodefile_nocmt = fem_mesh.strip_comments(opts.nodefile)
    nodeIDcoords = n.loadtxt(nodefile_nocmt,
                             delimiter=',',
                             comments='*',
                             dtype=[('id', 'i4'), ('x', 'f4'),
                                    ('y', 'f4'), ('z', 'f4')])

    # there are 6 faces in these models; we need to (1) find the top face and
    # (2) apply the appropriate loads
    [snic, axes] = SortNodeIDs(nodeIDcoords)

    # extract spatially-sorted node IDs on a the top z plane
    plane = (2, axes[2].max())
    planeNodeIDs = extractPlane(snic, axes, plane)

    # write out nodes on the top z plane with corresponding load values
    # (direction of motion, nodal displacement (accel, vel, etc), temporal load
    # curve ID, scale factor for load curve)
    # TODO: would like to clean this up with a dictionary to associate the
    # prescribed motions with their integer IDs with one statement instead of
    # three conditional statements below
    if loadtype == 'disp':
        writeNodeLoads(LOADFILE, planeNodeIDs, '%i,2,%i,%f' %
                       (direction, lcid, amplitude))
    elif loadtype == 'vel':
        writeNodeLoads(LOADFILE, planeNodeIDs, '%i,0,%i,%f' %
                       (direction, lcid, amplitude))
    elif loadtype == 'accel':
        writeNodeLoads(LOADFILE, planeNodeIDs, '%i,1,%i,%f' %
                       (direction, lcid, amplitude))
    elif loadtype == 'force':
        writeNodeLoads(LOADFILE, planeNodeIDs, '%i,%i,%f' %
                       (direction, lcid, amplitude))

    LOADFILE.write("*END\n")

    # close all of our files open for read/write
    LOADFILE.close()


def writeNodeLoads(LOADFILE, planeNodeIDs, dofs):
    for i in planeNodeIDs:
        for j in i:
            LOADFILE.write("%i,%s\n" % (j[0], dofs))


def read_cli():
    # lets read in some command-line arguments
    import argparse as argp

    par = argp.ArgumentParser(description="Generate loading conditions "
                              "for the top surface of the specified mesh.",
                              formatter_class=
                              argp.ArgumentDefaultsHelpFormatter)
    par.add_argument("--loadfile",
                     help="compression load defintion output file",
                     default="topload.dyn")
    par.add_argument("--nodefile",
                     help="node definition input file",
                     default="nodes.dyn")
    par.add_argument("--loadtype",
                     help="apply nodal prescribed displacements (disp), point "
                     "loads (force), velocity (vel) or acceleration (accel)",
                     default="disp")
    par.add_argument("--direction",
                     help="direction of load [1 - x, 2 - y, 3 - z]",
                     default=3)
    par.add_argument("--amplitude",
                     help="amplitude of load", default=1.0)
    par.add_argument("--lcid",
                     help="Load Curve ID (as function of time) to apply to "
                     "these loads", default=1)

    opts = par.parse_args()

    return opts

if __name__ == "__main__":
    main()
