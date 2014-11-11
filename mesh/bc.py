#!/bin/env python
"""
bc.py

Apply boundary conditions to rectangular solid meshes (the majority of the FE
sims); can handle quarter- and half-symmetry models.

EXAMPLE
=======
NEED THIS

=======
Copyright 2014 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__license__ = "Apache v2.0"


def main():
    import sys
    import numpy as n
    import fem_mesh

    fem_mesh.check_version()

    opts = read_cli()

    # open the boundary condition file to write
    BCFILE = open(opts.bcfile, 'w')
    BCFILE.write("$ Generated using %s with the following options:\n" %
                 sys.argv[0])
    BCFILE.write("$ %s\n" % opts)

    # load in all of the node data, excluding '*' lines
    header_comment_skips = fem_mesh.count_header_comment_skips(opts.nodefile)
    nodeIDcoords = n.loadtxt(opts.nodefile,
                             delimiter=',',
                             comments='*',
                             skiprows=header_comment_skips,
                             dtype=[('id', 'i4'), ('x', 'f4'), ('y', 'f4'),
                                    ('z', 'f4')])

    # there are 6 faces in these models; we need to (1) find all of them and
    # (2) apply the appropriate BCs we'll loop through all of the nodes, see if
    # they are on a face or edge, and then apply the appropriate BC
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    # extract spatially-sorted node IDs on a specified plane (these could be
    # internal or external)
    segID = 1
    for r in range(0, 3):
        for m in ('bcmin', 'bcmax'):
            if m == 'bcmin':
                plane = (r, axes[r].min())
            elif m == 'bcmax':
                plane = (r, axes[r].max())
            planeNodeIDs = fem_mesh.extractPlane(snic, axes, plane)
            if r == 0:  # front/back (front - symmetry, back - non-reflecting)
                if m == 'bcmin':  # back (non-reflecting)
                    segID = writeSeg(BCFILE, 'BACK', segID, planeNodeIDs)
                elif m == 'bcmax':  # front (symmetry)
                    if (opts.sym == 'q') or (opts.sym == 'h'):
                        # no top / bottom rows (those will be defined in the
                        # top/bottom defs)
                        writeNodeBC(BCFILE, planeNodeIDs[1:-1], '1,0,0,0,1,1')
                    else:
                        if opts.sym != 'none':
                            sys.exit("ERROR: invalid symmetry flag specified"
                                     "(front face)")
                        segID = writeSeg(BCFILE, 'FRONT', segID, planeNodeIDs)
            elif r == 1:  # left/right (non-reflecting; left - symmetry)
                if m == 'bcmin':  # left (push side)
                    # if quarter-symmetry, then apply BCs, in addition to a
                    # modified edge; and don't deal w/ top/bottom
                    if opts.sym == 'q':
                        writeNodeBC(BCFILE, planeNodeIDs[1:-1], '0,1,0,1,0,1')
                    # else make it a non-reflecting boundary
                    else:
                        if (opts.sym != 'h') and (opts.sym != 'none'):
                            sys.exit("ERROR: invalid symmetry flag specified"
                                     " (left/push face)")
                        segID = writeSeg(BCFILE, 'LEFT', segID, planeNodeIDs)
                if m == 'bcmax':  # right
                    segID = writeSeg(BCFILE, 'RIGHT', segID, planeNodeIDs)
            elif r == 2:  # top/bottom (fully-contrained & non-reflecting)
                if m == 'bcmin':  # bottom
                    segID = writeSeg(BCFILE, 'BOTTOM', segID, planeNodeIDs)
                    if opts.bottom == 'full':
                        writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')
                    elif opts.bottom == 'inplane':
                        writeNodeBC(BCFILE, planeNodeIDs, '0,0,1,1,1,0')
                    else:
                        sys.exit('ERROR: specific bottom BC invalid '
                                 '(can only be full or inplane)')
                if m == 'bcmax':  # top
                    segID = writeSeg(BCFILE, 'TOP', segID, planeNodeIDs)
                    if opts.top:
                        writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')

    # write non-reflecting boundaries (set segment references)
    BCFILE.write('*BOUNDARY_NON_REFLECTING\n')
    for i in range(1, segID):
        BCFILE.write('%i,0.0,0.0\n' % i)
    BCFILE.write('*END\n')

    # close all of our files open for read/write
    BCFILE.close()


def writeSeg(BCFILE, title, segID, planeNodeIDs):
    BCFILE.write('*SET_SEGMENT_TITLE\n')
    BCFILE.write('%s\n' % title)
    BCFILE.write('%i\n' % segID)
    for i in range(0, (len(planeNodeIDs) - 1)):
        (a, b) = planeNodeIDs.shape
        for j in range(0, (b - 1)):
            BCFILE.write("%i,%i,%i,%i\n" % (planeNodeIDs[i, j][0],
                                            planeNodeIDs[i + 1, j][0],
                                            planeNodeIDs[i + 1, j + 1][0],
                                            planeNodeIDs[i, j + 1][0]))
    segID = segID + 1
    return segID


def writeNodeBC(BCFILE, planeNodeIDs, dofs):
    BCFILE.write('*BOUNDARY_SPC_NODE\n')
    # don't grab the top / bottom rows (those will be defined in the top/bottom
    # defs)
    for i in planeNodeIDs:
        for j in i:
            BCFILE.write("%i,0,%s\n" % (j[0], dofs))


def read_cli():
    """
    read command line arguments
    """
    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate boundary condition"
                                     " data as specified on the command line.",
                                     formatter_class=
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--bcfile", help="boundary condition output file",
                        default="bc.dyn")
    parser.add_argument("--nodefile", help="node defintion input file",
                        default="nodes.dyn")
    parser.add_argument("--sym", help="quarter (q), half (h) symmetry "
                        "or none (none)", default="q")
    parser.add_argument("--top",
                        help="fully constrain top (xdcr surface)",
                        dest='top',
                        action='store_true')
    parser.add_argument("--notop",
                        help="top (xdcr surface) unconstrained",
                        dest='top',
                        action='store_false')
    parser.set_defaults(top=True)
    parser.add_argument("--bottom", help="full / inplane constraint "
                        "of bottom boundary (opposite transducer surface) "
                        "[full, inplane]", default="full")

    opts = parser.parse_args()

    return opts


if __name__ == "__main__":
    main()
