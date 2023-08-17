
class DynaMeshConstraintsMixin:
    def constrain_boundary_nodes(self):
        """
        This function adds two types of boundary constraints:
            1) Nodes on the bottom of the mesh (zmin face) are fully constrained (translational and rotational on x,y,z axes) to prevent the face from slipping during the simulation. This ensures all nodal displacements within the mesh are due to mesh deformations and prevents global mesh displacement.
            2) Nodes on the symmetry faces are constrained to not translate in the normal direction to the symmetry plane and to not rotate in the symmetry plane. For example, a mesh with a y-z symmetry plane face would be constrained to have no x translations and no y or z rotations.

        See DYNA Manual 1 *NODE section for rc and tc constraints
        - tc = translational constraint
        - rc = rotational constraint
        If constraints set in *NODE file, the following pattern is used:
            0: no constraints
            1: constrained x 
            2: constrained y
            3: constrained z
            4: constrained x and y
            5: constrained y and z
            6: constrained z and x
            7: constrained x, y, and z
        For example, if the tc parameter for a node is set to 4, the x and y displacements will be constrained to 0. 
        """
        # Plane node indices are plane node ids - 1

        # Only retrieve nodes on outer edge of mesh
        plane_thickness = 1

        # For each symmetry plane, constrain normal translations and in-plane rotations
        for plane in self.symmetry_planes:
            print(f"symmetry plane: {plane}")
            plane_node_ids = self.get_plane_node_ids(plane, plane_thickness)

            if plane == 'xmax':
                # Constrain x translations and y,z rotations
                self.nodes['tc'][plane_node_ids - 1] = 1
                self.nodes['rc'][plane_node_ids - 1] = 5
            # elif plane == 'ymax':
            elif plane == 'ymin':
                # Constrain y translations and x,z rotations
                self.nodes['tc'][plane_node_ids - 1] = 2
                self.nodes['rc'][plane_node_ids - 1] = 6                
            else:
                raise ValueError(f"Invalid symmetry plane: '{plane}'")

        # Fully constrain zmin plane to prevent mesh displacements. This causes the node displacements to be purely deformations rather than moving the whole mesh in any direction.
        plane_node_ids = self.get_plane_node_ids('zmin', plane_thickness)
        self.nodes['tc'][plane_node_ids - 1] = 7
        self.nodes['rc'][plane_node_ids - 1] = 7

        # Fully constrain PML planes if they exist
        if self.has_pml():
            for plane in self.pml_planes:
                print(f"pml plane: {plane}")
                plane_node_ids = self.get_plane_node_ids(plane, plane_thickness)
                self.nodes['tc'][plane_node_ids - 1] = 7
                self.nodes['rc'][plane_node_ids - 1] = 7