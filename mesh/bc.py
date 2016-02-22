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
    num_pml_elems = opts.num_pml_elems
    pml_partID = opts.pml_partID
    sym = opts.sym
    nonreflect = opts.nonreflect
    pml = opts.pml
    bottom = opts.bottom
    top = opts.top

    if pml:
        pmlfile = create_pml_elems_file(elefile)

    # TODO: replace w/ explicit variable value prints
    BCFILE = open_bcfile(opts, argv[0])

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)
    [elems] = fem_mesh.load_elems(elefile)
    [sorted_elemIDs] = fem_mesh.SortElemIDs(elems, axes)

    axdiff = axis_spacing(axes)

    # TODO: Change input syntax to something like:
    # nodeBC = [(1, 1, 1, 1, 1, 1), (0, 1, 0, 1, 1, 1), ...] ordered by [xmin,
    # xmax, ymin, ymax, ...]
    # pmlElems = [0, 5, 0, 5, 5, 5] ordered by [xmin, xmax, ymin, ...]
    # qsym_edge = [0, 1, 1, 0, 0, 0]
    segID = 1

    # BACK
    axis = 0
    axis_limit = axes[0].min()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'BACK', segID, planeNodeIDs)
    elif pml:
        apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis,
                  axis_limit, axis_limit+num_pml_elems*axdiff[axis],
                  pml_partID)

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
            apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis,
                      axis_limit-num_pml_elems*axdiff[axis],
                      axis_limit, pml_partID)

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
            apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis,
                      axis_limit, axis_limit+num_pml_elems*axdiff[axis],
                      pml_partID)

    # RIGHT (non-reflecting)
    axis = 1
    axis_limit = axes[1].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'RIGHT', segID, planeNodeIDs)
    elif pml:
        apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis,
                  axis_limit-num_pml_elems*axdiff[axis],
                  axis_limit, pml_partID)

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
        apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis,
                  axis_limit, axis_limit+num_pml_elems*axdiff[axis],
                  pml_partID)

    # TOP (transducer face)
    axis = 2
    axis_limit = axes[2].max()
    planeNodeIDs = fem_mesh.extractPlane(snic, axes, (axis, axis_limit))
    if nonreflect:
        segID = writeSeg(BCFILE, 'TOP', segID, planeNodeIDs)
        if top:
            writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')
    elif pml:
        apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis,
                  axis_limit-num_pml_elems*axdiff[axis],
                  axis_limit, pml_partID)

    if nonreflect:
        write_nonreflecting(BCFILE, segID)

    BCFILE.write('*END\n')
    BCFILE.close()


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


def writeNodeBC(BCFILE, planeNodeIDs, dofs):
    """write BC keywords to BC input file

    :param BCFILE: file IO object
    :param planeNodeIDs: 2D array
    :param str dofs: degrees of freedom
    """
    BCFILE.write('*BOUNDARY_SPC_NODE\n')
    for i in planeNodeIDs:
        for j in i:
            BCFILE.write("%i,0,%s\n" % (j[0], dofs))


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
    p.add_argument("--top",
                   help="fully constrain top (xdcr surface)",
                   dest='top',
                   action='store_true')
    p.add_argument("--notop",
                   help="top (xdcr surface) unconstrained",
                   dest='top',
                   action='store_false')
    p.set_defaults(top=True)
    p.add_argument("--bottom",
                   help="full / inplane constraint of bottom boundary "
                   "(opposite transducer surface) [full, inplane]",
                   default="full")
    s = p.add_mutually_exclusive_group(required=True)
    s.add_argument("--nonreflect",
                   help="apply non-reflection boundaries",
                   dest='nonreflect',
                   action='store_true')
    s.add_argument("--pml",
                   help="apply perfect matching layers",
                   dest='pml',
                   action='store_true')
    s.set_defaults(nonreflect=False, pml=False)

    opts = p.parse_args()

    return opts


def open_bcfile(opts, cmdline):
    """ open BC file for writing and write header

    TODO: only pass in filename (don't need entire BC object!!)

    :param opts: argparse object
    :param str cmdline: command line text to put in header
    :returns: BCFILE
    """
    BCFILE = open(opts.bcfile, 'w')
    BCFILE.write("$ Generated using %s with the following options:\n" %
                 cmdline)
    BCFILE.write("$ %s\n" % opts)

    return BCFILE


def write_nonreflecting(BCFILE, segID):
    """write non-reflecting boundaries (set segments)

    :param BCFILE: file IO object
    :param int segID: segment ID #
    """
    BCFILE.write('*BOUNDARY_NON_REFLECTING\n')
    for i in range(1, segID):
        BCFILE.write('%i,0.0,0.0\n' % i)


def apply_pml(nodefile, pmlfile, BCFILE, planeNodeIDs, axis, axmin, axmax,
              pml_partID):
    """apply PMLs

    Apply full nodal constraints to the outer face nodes and then create outer
    layers that are assigned to *MAT_PML_ELASTIC.

    TODO: delinieate input params
    """
    import CreateStructure as CS

    writeNodeBC(BCFILE, planeNodeIDs, '1,1,1,1,1,1')

    structNodeIDs = CS.findStructNodeIDs(nodefile,
                                         'layer',
                                         (axis+1, axmin, axmax))

    (elems, structElemIDs) = CS.findStructElemIDs(pmlfile,
                                                  structNodeIDs)

    CS.write_struct_elems(pmlfile, pml_partID, elems, structNodeIDs,
                          structElemIDs)


def create_pml_elems_file(elefile):
    """
    Create a new output elements file that the PML elements will be defined in
    that has '_pml' added to the filename.  Assume elefile ends with '.dyn'.

    this could be a homogeneous elems.dyn file, or a struct.dyn file

    :param elefile: elems.dyn (filename)
    :returns: pmlfile (filename)
    """
    from shutil import copy

    pmlfile = elefile.replace('.dyn', '_pml.dyn')

    copy(elefile, pmlfile)

    return pmlfile


def axis_spacing(axes):
    """calculate node spacing along each axis

    :param axes:
    :return: axdiff
    """

    axdiff = [axes[0][1]-axes[0][0],
              axes[1][1]-axes[1][0],
              axes[2][1]-axes[2][0]]
    return axdiff


if __name__ == "__main__":
    main()
