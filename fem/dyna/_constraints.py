
class DynaMeshConstraintsMixin:
    def constrain_boundary_nodes(self):
        """
        
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

        # Get symmetry and non-symmetry planes based on mesh symmetry conditions
        # Plane node indices are plane node ids - 1
        symmetry_planes, non_symmetry_planes = self.get_symmetry_and_non_symmetry_planes()

        # Only retrieve nodes on outer edge of mesh
        plane_thickness = 1

        # For each symmetry plane, constrain normal translations and in-plane rotations
        for plane in symmetry_planes:
            plane_node_ids = self.get_plane_node_ids(plane, plane_thickness)

            if plane == 'xmax':
                # Constrain x translations and y,z rotations
                self.nodes['tc'][plane_node_ids - 1] = 1
                self.nodes['rc'][plane_node_ids - 1] = 5
            elif plane == 'ymax':
                # Constrain y translations and x,z rotations
                self.nodes['tc'][plane_node_ids - 1] = 2
                self.nodes['rc'][plane_node_ids - 1] = 6                
            else:
                raise ValueError(f"Invalid symmetry plane: '{plane}'")

        # Fully constrain zmin plane to prevent mesh displacements. This causes the node displacements to be purely deformations rather than moving the whole mesh in any direction.
        plane_node_ids = self.get_plane_node_ids('zmin', plane_thickness)
        self.nodes['tc'][plane_node_ids - 1] = 7
        self.nodes['rc'][plane_node_ids - 1] = 7