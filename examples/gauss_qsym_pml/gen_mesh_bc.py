def main():
    from fem.mesh import GenMesh
    from fem.mesh import bc

    xyz = (-1.5, 0.0, 0.0, 1.5, -3.0, 0.0)
    numElem = (75, 75, 150)
    GenMesh.run(xyz, numElem)

    # setup quarter symmetry condition
    pml_elems = ((5, 0), (0, 5), (5, 5))
    face_constraints = (('1,1,1,1,1,1', '1,0,0,0,1,1'),
                        ('0,1,0,1,0,1', '1,1,1,1,1,1'),
                        ('1,1,1,1,1,1', '1,1,1,1,1,1'))
    edge_constraints = (((0,1),(1,0),(0,0)),'1,1,0,1,1,1')

    bc.apply_pml(pml_elems, face_constraints, edge_constraints)

if __name__ == "__main__":
    main()
