"""
:mod:`bc` -- boundary conditions
================================

.. module:: bc
   :synopsis: apply boundary conditions to rectangular solid meshes
   :license: Apache v2.0, see LICENSE for details
   :copyright: Copyright 2015 Mark Palmeri

.. moduleauthor:: Mark Palmeri <mlp6@duke.edu>

"""

def main():
    """apply prescribed boundary conditions to nodes/face segments

    TODO: THIS IS WAY TOO COMPLEX
    """

    import fem_mesh
    from sys import argv

    fem_mesh.check_version()

    opts = read_cli()
    nodefile = opts.nodefile
    elefile = opts.elefile
    pmlfile = opts.pmlfile
    pml_elems = opts.pml_elems
    pml_partID = opts.pml_partID
    nonreflect_faces = opts.nonreflect_faces
    node_constraints = opts.node_constraints

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)
    [elems] = fem_mesh.load_elems(elefile)
    [sorted_elems] = fem_mesh.SortElemIDs(elems, axes)
    axdiff = axis_spacing(axes)

    if pml_elems:
        sorted_pml_elems = assign_pml_elems(sorted_elems, pml_elems)
        write_pml_elems(sorted_pml_elems, pmlfile)
        write_bc_file()
    elif nonreflect_faces:
        write_nonreflecting(BCFILE, segID)
        write_bc_file()

    # TODO: Change input syntax to something like:
    # nodeBC = [[(1, 1, 1, 1, 1, 1), (0, 1, 0, 1, 1, 1)], ...] ordered by [xmin,
    # xmax, ymin, ymax, ...]
    # qsym_edge = [[0, 1], [1, 0], [0, 0]]

"""
    segID = 1

    # BACK
    axis = 0
    axis_limit = axes[0].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'BACK', segID, planeNodeIDs)
    elif pml:

    # FRONT
    axis = 0
    axis_limit = axes[0].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if (sym == 'q') or (sym == 'h'):
        # no top / bottom rows (those will be defined in the
        # top/bottom defs)
        writeNodeBC(BCFILE, planeNodeIDs[1:-1], '1,0,0,0,1,1')
    else:
        if nonreflect:
            segID = writeSeg(BCFILE, 'FRONT', segID, planeNodeIDs)
        elif pml:

    # LEFT (push side; non-reflecting or symmetry)
    axis = 1
    axis_limit = axes[1].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    # if quarter-symmetry, then apply BCs, in addition to a
    # modified edge; and don't deal w/ top/bottom
    if sym == 'q':
        writeNodeBC(BCFILE, planeNodeIDs[1:-1], '0,1,0,1,0,1')
    # else make it a non-reflecting boundary
    else:
        if nonreflect:
            segID = writeSeg(BCFILE, 'LEFT', segID, planeNodeIDs)
        elif pml:

    # RIGHT (non-reflecting)
    axis = 1
    axis_limit = axes[1].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'RIGHT', segID, planeNodeIDs)
    elif pml:

    # BOTTOM
    axis = 2
    axis_limit = axes[2].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'BOTTOM', segID, planeNodeIDs)
        if bottom == 'full':
            writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')
        elif bottom == 'inplane':
            writeNodeBC(BCFILE, planeNodeIDs, '0,0,1,1,1,0')
    elif pml:

    # TOP (transducer face)
    axis = 2
    axis_limit = axes[2].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'TOP', segID, planeNodeIDs)
        if top:
            writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')
    elif pml:


    # TODO: write_bc_file()
    """


def writeSeg(BCFILE, title, segID, planeNodeIDs):
    """write face segments to BC input file

    :param BCFILE: file IO object
    :param str title: header comment line
    :param int segID: segment ID #
    :param planeNodeIDs: 2D array
    :returns: segID (inc +1)
    """
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


def write_bc_file(planeNodeIDs, dofs, bcfile="bc.dyn"):
    """write BC keywords to BC file

    :param planeNodeIDs: 2D array
    :param str dofs: degrees of freedom
    :param bcfile: boundary conditiona filename (bc.dyn)
    """

    BCFILE = open(bcfile, 'w')
    BCFILE.write("$ Generated using %s with the following options:\n" %
                 cmdline)
    # TODO: replace w/ explicit variable value prints
    BCFILE.write("$ %s\n" % opts)
    BCFILE.write('*BOUNDARY_SPC_NODE\n')

    # TODO: replace with printing node BC dict
    for i in planeNodeIDs:
        for j in i:
            BCFILE.write("%i,0,%s\n" % (j[0], dofs))

    BCFILE.write('*END\n')
    BCFILE.close()

def read_cli():
    """read command line arguments

    :returns: opts (argparse object)
    """
    import argparse as ap

    # lets read in some command-line arguments
    p = ap.ArgumentParser(description="Generate boundary condition data as "
                          "specified on the command line.",
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)
    p.add_argument("--bcfile",
                   help="boundary condition output file",
                   default="bc.dyn")
    p.add_argument("--nodefile",
                   help="node defintion input file",
                   default="nodes.dyn")
    p.add_argument("--elefile",
                   help="elem defintion input file",
                   default="elems.dyn")
    p.add_argument("--sym",
                   help="quarter (q), half (h) symmetry or none (none)",
                   default="q")
    p.add_argument("--pml_partID",
                   help="part ID to assign to PML",
                   default=2)
    p.add_argument("--num_pml_elems",
                   type=int,
                   help="number of elements in PML (5-10)",
                   default=5)
    s = p.add_mutually_exclusive_group(required=True)
    s.add_argument("--nonreflect",
                   help="apply non-reflection boundaries",
                   dest='nonreflect',
                   action='store_true')
    s.add_argument("--pml",
                   help="apply perfect matching layers",
                   dest='pml',
                   action='store_true')
    s.set_defaults(nonreflect=False, pml=True)

    opts = p.parse_args()

    return opts


# TODO: consolidate this when writing the bc file
def write_nonreflecting(BCFILE, segID):
    """write non-reflecting boundaries (set segments)

    :param BCFILE: file IO object
    :param int segID: segment ID #
    """
    BCFILE.write('*BOUNDARY_NON_REFLECTING\n')
    for i in range(1, segID):
        BCFILE.write('%i,0.0,0.0\n' % i)


def assign_pml_elems(sorted_elems, pml_elems, pml_partID='2'):
    """assign PML elements in the sorted element matrix

    :param sorted_elems: sorted element matrix
    :param pml_elems: list of tuples of # PML elems on each axis edge ([[xmin, max], [ymin, ymax], ...)
    :param pml_partID: default = 2
    :return: sorted_pml_elems (to be written to new file)
    """
    sorted_elems['pid'][:, :, 0:pml_elems[0][0]] = pml_partID
    sorted_elems['pid'][:, :, -1:-pml_elems[0][1]-1:-1] = pml_partID
    sorted_elems['pid'][:, 0:pml_elems[1][0], :] = pml_partID
    sorted_elems['pid'][:, -1:-pml_elems[1][1]-1:-1, :] = pml_partID
    sorted_elems['pid'][0:pml_elems[2][0], :, :] = pml_partID
    sorted_elems['pid'][-1:-pml_elems[2][1]-1:-1, :, :] = pml_partID

    return sorted_elems

def write_pml_elems(sorted_pml_elems, pmlfile="elems_pml.dyn"):
    """Create a new elements file that the PML elements.

    :param sorted_pml_elems:
    :param pmlfile: default = elems_pml.dyn
    :returns:
    """
    from numpy import ndenumerate

    pml = open(pmlfile, 'w')
    pml.write('$ PML elements generated by bc.py\n')
    pml.write('*ELEMENT_SOLID\n')
    for i, e in ndenumerate(sorted_pml_elems):
        pml.write('%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\n' % (e['id'], e['pid'],
                                                     e['n1'], e['n2'],
                                                     e['n3'], e['n4'],
                                                     e['n5'], e['n6'],
                                                     e['n7'], e['n8']))
    pml.write('*END\n')
    pml.close()

    return 0


if __name__ == "__main__":
    main()
