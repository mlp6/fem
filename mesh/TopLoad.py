#!/usr/local/bin/python2.7
'''
TopLoad.py - Generate compression conditions for the top surface of the
specified mesh.  Search through the provided node file, extract the top layer of
nodes and write out point loads for each matching node. Nodes are written in
spatially-sorted order.

Copyright 2015 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
'''
from __future__ import absolute_import

__author__ = "Mark Palmeri "
__email__ = "mlp6@duke.edu"
__license__ = "Apache v2.0"


def main():
    """way too complicated for now
    """

    import sys
    import numpy as n
    import fem_mesh

    fem_mesh.check_version()

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

    LOADFILE.write("$ Generated using %s with the following "
                   "options:\n" % sys.argv[0])
    LOADFILE.write("$ %s\n" % opts)

    # load in all of the node data, excluding '*' lines
    header_comment_skips = fem_mesh.count_header_comment_skips(opts.nodefile)
    nodeIDcoords = n.loadtxt(opts.nodefile,
                             delimiter=',',
                             skiprows=header_comment_skips,
                             comments='*',
                             dtype=[('id', 'i4'), ('x', 'f4'),
                                    ('y', 'f4'), ('z', 'f4')])

    # there are 6 faces in these models; we need to (1) find the top face and
    # (2) apply the appropriate loads
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    # extract spatially-sorted node IDs on a the top z plane
    plane = (2, axes[2].max())
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, plane)

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
    """write load keyword file

    :param LOADFILE: file object
    :param planeNodeIDS: array of node IDs
    :param dofs: degrees of freedom to constrain
    :returns: None

    """
    for i in planeNodeIDs:
        for j in i:
            LOADFILE.write("%i,%s\n" % (j[0], dofs))


def read_cli():
    """read CLI args
    """

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
