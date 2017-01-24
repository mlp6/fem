"""
:mod:`bc` -- boundary conditions
================================

.. module:: bc
   :synopsis: apply boundary conditions to rectangular solid meshes
   :license: Apache v2.0 (see LICENSE for details)
   :copyright: Copyright 2015--2016 Mark Palmeri

.. moduleauthor:: Mark Palmeri <mlp6@duke.edu>

"""

def main():
    """apply prescribed boundary conditions to nodes/face segments
    """
    opts = read_cli()

    if pml_elems:
        apply_pml(opts.pml_elems, opts.face_constraints, opts.edge_constraints,
                  opts.nodefile, opts.elefile, opts.pmlfile, opts.bcfile, opts.pml_partID)
    elif nonreflect_faces:
        apply_nonreflect(opts.face_constraints, opts.edge_constraints, opts.nodefile,
                         opts.elefile, opts.bcfile, opts.segfile)

    return 0


def apply_face_bc_only(face_constraints, nodefile="nodes.dyn", bcfile="bc.dyn"):
    """driver function to apply node BCs just to faces

    :param face_constraints: 3x2 array of strings, specifying the BCs on each face (3), min/max (2)
    :param nodefile: default - 'nodes.dyn'
    :param bcfile: 'defauly - 'bc.dyn'
    :return:
    """

    from fem.mesh import fem_mesh

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    bcdict = assign_node_constraints(snic, axes, face_constraints)

    write_bc(bcdict, bcfile)

    return 0


def apply_pml(pml_elems, face_constraints, edge_constraints,
              nodefile="nodes.dyn", elefile="elems.dyn", pmlfile="elems_pml.dyn",
              bcfile="bc.dyn", pml_partID=2):
    """
    driver function to apply PML boundary conditions

    :param pml_elems: 3x2 array of ints specifying thickness of PML elements (5--10) on each PML layer
    :param face_constraints: 3x2 array of strings, specifying the BCs on each face (3), min/max (2)
    :param edge_constraints: 1x6 vector of BCs on each edge
    :param nodefile: default - 'nodes.dyn'
    :param elefile: default - 'elems.dyn'
    :param pmlfile: default - 'elems_pml.dyn'
    :param bcfile: 'defauly - 'bc.dyn'
    :param pml_partID: default - 2
    :return:
    """
    from fem.mesh import fem_mesh

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)
    elems = fem_mesh.load_elems(elefile)
    sorted_elems = fem_mesh.SortElems(elems, axes)

    sorted_pml_elems = assign_pml_elems(sorted_elems, pml_elems, pml_partID)
    write_pml_elems(sorted_pml_elems, pmlfile)

    bcdict = assign_node_constraints(snic, axes, face_constraints)
    bcdict = constrain_sym_pml_nodes(bcdict, snic, axes, pml_elems, edge_constraints)
    bcdict = assign_edge_sym_constraints(bcdict, snic, axes, edge_constraints)
    write_bc(bcdict, bcfile)

    return 0

def apply_nonreflect(face_constraints, edge_constraints, nodefile="nodes.dyn",
                     elefile="elems.dyn", bcfile="bc.dyn", segfile="nonreflect_segs.dyn"):
    """
    driver function to generate non-reflecting boundaries

    :param face_constraints: vector of face constraints, ordered from xmin to zmax
    :param edge_constraints: vector of edge constraints, ordered from xmin to zmax
    :param nodefile: default - 'nodes.dyn'
    :param elefile: default - 'elems.dyn'
    :param bcfile: default - 'bc.dyn'
    :param segfile: default - 'nonreflect_segs.dyn'
    :return: 0 on success
    """
    from fem.mesh import fem_mesh

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    segID = 1
    seg_names = [['XMIN', 'XMAX'], ['YMIN', 'YMAX'], ['ZMIN', 'ZMAX']]
    SEGBCFILE = open(segfile, 'w')
    for a in range(0, 3):
        for m in range(0, 2):
            if face_constraints[a][m] == '1,1,1,1,1,1':
                if m == 0:
                    axis_limit = axes[a][0]
                else:
                    axis_limit = axes[a][-1]
                planeNodeIDs = fem_mesh.extractPlane(snic, axes, (a, axis_limit))
                segID = writeSeg(SEGBCFILE, seg_names[a][m], segID, planeNodeIDs)
    write_nonreflecting(SEGBCFILE, segID)
    SEGBCFILE.close()

    bcdict = assign_node_constraints(snic, axes, face_constraints)
    bcdict = assign_edge_sym_constraints(bcdict, snic, axes, edge_constraints)
    write_bc(bcdict, bcfile)

    return 0


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
            BCFILE.write("%i,%i,%i,%i\n" % (planeNodeIDs[i, j],
                                            planeNodeIDs[i + 1, j],
                                            planeNodeIDs[i + 1, j + 1],
                                            planeNodeIDs[i, j + 1]))
    segID = segID + 1

    return segID


def write_bc(bcdict, bc="bc.dyn"):
    """write node BCs

    :param bcdict: dict of node BCs, with DOF values
    :param bcfile: boundary conditions filename (bc.dyn)
    """

    bcf = open(bc, 'w')
    bcf.write("$ Generated using bc.py\n")
    bcf.write('*BOUNDARY_SPC_NODE\n')
    for i in bcdict:
        bcf.write('%i,0,' % i)
        bcf.write('%s\n' % bcdict[i])
    bcf.write('*END\n')
    bcf.close()

    return 0

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
    p.add_argument("--segfile",
                   help="non-reflected segments boundary condition output file",
                   default="nonreflect_segs.dyn")
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
    p.add_argument("--face_constraints",
                   help="constrain face DOFs")
    p.add_argument("--edge_constraints",
                   help="constrain edge DOFs")
    p.add_argument("--pmlfile",
                    help="PML element output filename",
                    default="elems_pml.dyn")
    s = p.add_mutually_exclusive_group(required=True)
    s.add_argument("--nonreflect",
                   help="apply non-reflection boundaries",
                   dest='nonreflect',
                   action='store_true')
    s.add_argument("--pml",
                   help="apply perfect matching layers",
                   dest='pml',
                   action='store_true')
    opts = p.parse_args()

    return opts


def write_nonreflecting(BCFILE, segID):
    """write non-reflecting boundaries (set segments) to input file with segments

    ASSUMES THAT SEGMENT FILE HAS ALREADY BEEN WRITTEN TO AND NOT TERMINATED WITH *END

    :param BCFILE: file IO object
    :param int segID: maximum segment ID #, assuming started at 1
    :returns: 0 on success
    """
    BCFILE.write('*BOUNDARY_NON_REFLECTING\n')
    for i in range(1, segID):
        BCFILE.write('%i,0.0,0.0\n' % i)
    BCFILE.write('*END\n')

    return 0

def assign_pml_elems(sorted_elems, pml_elems, pml_partID='2'):
    """assign PML elements in the sorted element matrix

    :param sorted_elems: sorted element matrix
    :param pml_elems: list of tuples of # PML elems on each axis edge
                      ([[xmin, max], [ymin, ymax], ...)
    :param pml_partID: default = 2
    :return: sorted_pml_elems (to be written to new file)
    """
    sorted_elems['pid'][0:pml_elems[0][0], :, :] = pml_partID
    sorted_elems['pid'][-1:-pml_elems[0][1]-1:-1, :, :] = pml_partID
    sorted_elems['pid'][:, 0:pml_elems[1][0], :] = pml_partID
    sorted_elems['pid'][:, -1:-pml_elems[1][1]-1:-1, :] = pml_partID
    sorted_elems['pid'][:, :, 0:pml_elems[2][0]] = pml_partID
    sorted_elems['pid'][:, :, -1:-pml_elems[2][1]-1:-1] = pml_partID

    return sorted_elems


def assign_node_constraints(snic, axes, face_constraints):
    """assign node constraints to prescribed node planes

    Nodes shared on multiple faces have are assigned with the following order
    of precedence: z, y, x

    :param snic: sorted node IDs and coordinates from nodes.dyn
    :param axes: mesh axes [x, y, z]
    :param face_constraints: list of DOF strings ordered by
                             ((xmin, max), (ymin, ...)
                             (e.g., (('1,1,1,1,1,1' , '0,1,0,0,1,0'),...)
    :return: bcdict - dictionary of node BC to be written to bc.dyn
    """
    from fem.mesh.fem_mesh import extractPlane
    from numpy import ndenumerate

    bcdict = {}
    for axis in range(0, 3):
        for axlim in range(0, 2):
            if axlim == 0:
                axis_limit = axes[axis].min()
            else:
                axis_limit = axes[axis].max()
            planeNodeIDs = extractPlane(snic, axes, (axis, axis_limit))
            for i, id in ndenumerate(planeNodeIDs):
                bcdict[id] = face_constraints[axis][axlim]

    return bcdict


def constrain_sym_pml_nodes(bcdict, snic, axes, pml_elems, edge_constraints):
    """make sure that all "side" nodes for the PML elements are fully
    constrained, instead of being assigned the symmetry constraints

    THIS FUNCTION IS NOT NEEDED!!

    :param bcdict:
    :param snic:
    :param axes:
    :param pml_elems:
    :param edge_constraints:
    :return: bcdict
    """
    from fem.mesh.fem_mesh import extractPlane
    from numpy import ndenumerate

    # look for x symmetry face
    for axis in range(0, 2):
        if edge_constraints[0][axis][0]:
            axis_limit = axes[axis].min()
        elif edge_constraints[0][axis][1]:
            axis_limit = axes[axis].max()
        if axis_limit is not None:
            planeNodeIDs = extractPlane(snic, axes, (axis, axis_limit))
            pml_node_ids_zmin = planeNodeIDs[:, 0:(pml_elems[2][0]+1)]
            pml_node_ids_zmax = planeNodeIDs[:, -(pml_elems[2][1]+1):]
            for i, id in ndenumerate(pml_node_ids_zmin):
                bcdict[id] = "%s" % '1,1,1,1,1,1'
            for i, id in ndenumerate(pml_node_ids_zmax):
                bcdict[id] = "%s" % '1,1,1,1,1,1'
        axis_limit = None

    return bcdict


def assign_edge_sym_constraints(bcdict, snic, axes, edge_constraints):
    """modify/create node BCs for quarter-symmetry edge

    :param bcdict: dict of nodal BCs
    :param snic: sorted node IDs and coordinates
    :param axes: spatial axis vectors
    :param edge_constraints: list with vector indicating edge & constraint
                             (e.g., to specify the edge shared by the xmax
                             and ymin faces to allow just z translation:
                             (((0,1),(1,0),(0,0)),'1,1,0,1,1,1')
    :return: bcdict (updated from face assignment)
    """
    from warnings import warn
    from fem.mesh.fem_mesh import extractPlane

    # look for edge shared with an x face
    axis = 0
    if edge_constraints[0][axis][0]:
        axis_limit = axes[axis].min()
    elif edge_constraints[0][axis][1]:
        axis_limit = axes[axis].max()
    else:
        warn('Symmetry edge not shared by an x-face specified;'
             'no edge BCs defined')
        return 1
    planeNodeIDs = extractPlane(snic, axes, (axis, axis_limit))

    # restrict nodes to those on specified edge
    ortho_axis = 1
    if edge_constraints[0][ortho_axis][0]:
        edge_nodes = planeNodeIDs[0,:]
    elif edge_constraints[0][ortho_axis][1]:
        edge_nodes = planeNodeIDs[-1,:]
    else:
        warn('Orthogonal plane to x-face is not a y-face; no edge BCs defined')
        return 1

    # do not assign BCs to nodes associated with zmin/zmax faces
    edge_nodes = edge_nodes[1:-1]
    for i in edge_nodes:
        bcdict[i] = "%s" % edge_constraints[1]

    return bcdict

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
