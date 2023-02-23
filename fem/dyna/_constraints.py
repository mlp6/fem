
class DynaMeshConstraintsMixin:
    def constrain_boundary_nodes(self):
        # Plane node indices are plane node ids - 1
        symmetry_planes, non_symmetry_planes = self.get_symmetry_and_non_symmetry_planes()

        plane_thickness = 1
        for plane in symmetry_planes:
            plane_node_ids = self.get_plane_node_ids(plane, plane_thickness)
            self.nodes['rc'][plane_node_ids - 1] = 4
            self.nodes['tc'][plane_node_ids - 1] = 7

        for plane in non_symmetry_planes:
            plane_node_ids = self.get_plane_node_ids(plane, plane_thickness)
            self.nodes['rc'][plane_node_ids - 1] = 7
            self.nodes['tc'][plane_node_ids - 1] = 7