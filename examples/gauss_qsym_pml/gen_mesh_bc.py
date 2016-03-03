def main():
    from fem.mesh import fem_mesh as fm
    from fem.mesh import bc
    from fem.mesh import GenMesh as mesh

    numElem = (75, 75, 150)
    pos = mesh.calc_node_pos((-1.5, 0.0, 0.0, 1.5, -3.0, 0.0), numElem)
    mesh.writeNodes(pos)
    mesh.writeElems(numElem)

    # setup quarter symmetry condition
    pml_elems = ((5, 0), (0, 5), (5, 5))
    face_constraints = (('1,1,1,1,1,1', '1,0,0,0,1,1'),
                        ('0,1,0,1,0,1', '1,1,1,1,1,1'),
                        ('1,1,1,1,1,1', '1,1,1,1,1,1'))
    edge_constraints = (((0,1),(1,0),(0,0)),'1,1,0,1,1,1')

    nodeIDcoords = fm.load_nodeIDs_coords()
    [snic, axes] = fm.SortNodeIDs(nodeIDcoords)
    elems = fm.load_elems()
    sorted_elems = fm.SortElems(elems, axes)

    sorted_pml_elems = bc.assign_pml_elems(sorted_elems, pml_elems)
    bc.write_pml_elems(sorted_pml_elems)

    bcdict = bc.assign_node_constraints(snic, axes, face_constraints)
    bcdict = bc.assign_edge_sym_constraints(bcdict, snic, axes,
                                            edge_constraints, pml_elems)
    bc.write_bc(bcdict)

if __name__ == "__main__":
    main()
