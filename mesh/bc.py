#!/bin/env python
"""
bc.py

Apply boundary conditions to rectangular solid meshes (the majority of the FE
sims); can handle quarter-, half-, and no symmetry models.

There are 6 faces in these models; we need to:
 1. Find all of them, and
 2. Apply the appropriate BCs

We'll loop through all of the nodes, see if they are on a face or edge, and
then apply the appropriate BC.

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
    import fem_mesh
    import sys

    fem_mesh.check_version()

    opts = read_cli()

    BCFILE = open_bcfile(opts, sys.argv[0])

    nodeIDcoords = load_nodeIDs_coords(opts.nodefile)

    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)
    axdiff = [axes[0][1]-axes[0][0],
              axes[1][1]-axes[1][0],
              axes[2][1]-axes[2][0]]

    segID = 1

    # BACK
    axis = 0
    axis_limit = axes[0].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if opts.nonreflect:
        segID = writeSeg(BCFILE, 'BACK', segID, planeNodeIDs)
    elif opts.pml:
        apply_pml(opts.nodefile, opts.elefile, BCFILE, planeNodeIDs, axis,
                  axis_limit, axis_limit+opts.num_pml_elems*axdiff[axis],
                  opts.pml_partID)

    # FRONT
    axis = 0
    axis_limit = axes[0].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if (opts.sym == 'q') or (opts.sym == 'h'):
        # no top / bottom rows (those will be defined in the
        # top/bottom defs)
        writeNodeBC(BCFILE, planeNodeIDs[1:-1], '1,0,0,0,1,1')
    else:
        if opts.nonreflect:
            segID = writeSeg(BCFILE, 'FRONT', segID, planeNodeIDs)
        elif opts.pml:
            apply_pml(opts.nodefile, opts.elefile, BCFILE, planeNodeIDs, axis,
                      axis_limit-opts.num_pml_elems*axdiff[axis],
                      axis_limit, opts.pml_partID)

    # LEFT (push side; non-reflecting or symmetry)
    axis = 1
    axis_limit = axes[1].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    # if quarter-symmetry, then apply BCs, in addition to a
    # modified edge; and don't deal w/ top/bottom
    if opts.sym == 'q':
        writeNodeBC(BCFILE, planeNodeIDs[1:-1], '0,1,0,1,0,1')
    # else make it a non-reflecting boundary
    else:
        if opts.nonreflect:
            segID = writeSeg(BCFILE, 'LEFT', segID, planeNodeIDs)
        elif opts.pml:
            apply_pml(opts.nodefile, opts.elefile, BCFILE, planeNodeIDs, axis,
                      axis_limit, axis_limit+opts.num_pml_elems*axdiff[axis],
                      opts.pml_partID)

    # RIGHT (non-reflecting)
    axis = 1
    axis_limit = axes[1].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if opts.nonreflect:
        segID = writeSeg(BCFILE, 'RIGHT', segID, planeNodeIDs)
    elif opts.pml:
        apply_pml(opts.nodefile, opts.elefile, BCFILE, planeNodeIDs, axis,
                  axis_limit-opts.num_pml_elems*axdiff[axis],
                  axis_limit, opts.pml_partID)

    # BOTTOM
    axis = 2
    axis_limit = axes[2].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if opts.nonreflect:
        segID = writeSeg(BCFILE, 'BOTTOM', segID, planeNodeIDs)
        if opts.bottom == 'full':
            writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')
        elif opts.bottom == 'inplane':
            writeNodeBC(BCFILE, planeNodeIDs, '0,0,1,1,1,0')
    elif opts.pml:
        apply_pml(opts.nodefile, opts.elefile, BCFILE, planeNodeIDs, axis,
                  axis_limit, axis_limit+opts.num_pml_elems*axdiff[axis],
                  opts.pml_partID)

    # TOP (transducer face)
    axis = 2
    axis_limit = axes[2].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if opts.nonreflect:
        segID = writeSeg(BCFILE, 'TOP', segID, planeNodeIDs)
        if opts.top:
            writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')
    elif opts.pml:
        apply_pml(opts.nodefile, opts.elefile, BCFILE, planeNodeIDs, axis,
                  axis_limit-opts.num_pml_elems*axdiff[axis],
                  axis_limit, opts.pml_partID)

    if opts.nonreflect:
        write_nonreflecting(BCFILE, segID)

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
    parser.add_argument("--pml_partID",
                        help="part ID to assign to PML",
                        default=2)
    parser.add_argument("--num_pml_elems",
                        help="number of elements in PML (5-10)",
                        default=5)
    parser.add_argument("--top",
                        help="fully constrain top (xdcr surface)",
                        dest='top',
                        action='store_true')
    parser.add_argument("--notop",
                        help="top (xdcr surface) unconstrained",
                        dest='top',
                        action='store_false')
    parser.set_defaults(top=True)
    parser.add_argument("--bottom", help="full / inplane constraint"
                        "of bottom boundary (opposite transducer surface) "
                        "[full, inplane]", default="full")
    s = parser.add_mutually_exclusive_group(required=True)
    s.add_argument("--nonreflect",
                   help="apply non-reflection boundaries",
                   dest='nonreflect',
                   action='store_true')
    s.add_argument("--pml",
                   help="apply perfect matching layers",
                   dest='pml',
                   action='store_true')
    s.set_defaults(nonreflect=False, pml=False)

    opts = parser.parse_args()

    return opts


def load_nodeIDs_coords(nodefile):
    """
    load in node IDs and coordinates, excluding '*' keyword lines
    """
    import fem_mesh
    import numpy as n
    header_comment_skips = fem_mesh.count_header_comment_skips(nodefile)
    nodeIDcoords = n.loadtxt(nodefile,
                             delimiter=',',
                             comments='*',
                             skiprows=header_comment_skips,
                             dtype=[('id', 'i4'), ('x', 'f4'), ('y', 'f4'),
                                    ('z', 'f4')])
    return nodeIDcoords


def open_bcfile(opts, cmdline):
    """
    open BC file for writing and write header with command line
    """
    BCFILE = open(opts.bcfile, 'w')
    BCFILE.write("$ Generated using %s with the following options:\n" %
                 cmdline)
    BCFILE.write("$ %s\n" % opts)
    return BCFILE


def write_nonreflecting(BCFILE, segID):
    """
    write non-reflecting boundaries (set segment references)
    """
    BCFILE.write('*BOUNDARY_NON_REFLECTING\n')
    for i in range(1, segID):
        BCFILE.write('%i,0.0,0.0\n' % i)
    BCFILE.write('*END\n')


def apply_pml(nodefile, elefile, BCFILE, planeNodeIDs, axis, axmin, axmax,
              pml_partID):
    """
    Apply full nodal constraints to the outer face nodes and then create outer
    layers that are assigned to *MAT_PML_ELASTIC.
    """
    import CreateStructure as CS

    writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')

    structNodeIDs = CS.findStructNodeIDs(nodefile,
                                         'layer',
                                         (axis, axmin, axmax))

    (elems, structElemIDs) = CS.findStructElemIDs(elefile, structNodeIDs)

    CS.write_struct_elems('elems_pml.dyn', pml_partID, elems, structNodeIDs,
                          structElemIDs)

if __name__ == "__main__":
    main()
