import numpy as np


class DynaMeshStructureMixin:
    def add_struct(self, shape, material, struct_opts):
        # Get nodes in struct
        nodes_in_struct = self.find_nodes_in_struct(shape, *struct_opts)
        
        new_part_id = self.get_new_part_id()
        self.add_struct_to_elems(nodes_in_struct, new_part_id)

        # Create material, part, and section solid cards
        self.material_card_string += material.format_material_part_and_section_cards(
            new_part_id, title=shape
        )

        if self.has_pml():
            pml_and_struct_nodes = np.intersect1d(self.pml_nodes, nodes_in_struct)
            if len(pml_and_struct_nodes) > 0:
                pml_part_id = self.get_new_part_id()
                self.add_struct_to_elems(pml_and_struct_nodes, pml_part_id)
                self.material_card_string += material.format_material_part_and_section_cards(
                    pml_part_id, title=shape+' pml', is_pml_material=True
                )

    def add_struct_to_elems(self, nodes_in_struct, new_part_id):
        def all_nodes_in_struct(elem_node_list, nodes_in_struct): 
            return all(elem_node_id in nodes_in_struct for elem_node_id in elem_node_list)
        
        for elem_id, elem_part_id, *elem_node_list in self.elems:
            if all_nodes_in_struct(elem_node_list, nodes_in_struct):
                # elem_id - 1 because id is 1-based indexing
                self.elems['pid'][elem_id-1] = new_part_id

    def find_nodes_in_struct(self, shape, *struct_opts):
        if shape == 'cube':
            struct_node_ids = self.find_nodes_in_cube(*struct_opts)
        elif shape == 'sphere':
            struct_node_ids = self.find_nodes_in_sphere(*struct_opts)
        elif shape == 'cylinder':
            struct_node_ids = self.find_nodes_in_cylinder(*struct_opts)
        else:
            raise ValueError(f"Invalid shape: '{shape}'")
        return struct_node_ids
    
    def find_nodes_in_cube(self, xmin, xmax, ymin, ymax, zmin, zmax):
        struct_node_ids = []
        for nid, x, y, z, tc, rc in self.nodes:
            in_x_extent = (x >= xmin) and (x <= xmax)
            in_y_extent = (y >= ymin) and (y <= ymax)
            in_z_extent = (z >= zmin) and (z <= zmax)

            if in_x_extent and in_y_extent and in_z_extent:
                struct_node_ids.append(nid)
        return struct_node_ids

    def find_nodes_in_sphere(self, xc, yc, zc, radius):
        struct_node_ids = []
        for nid, x, y, z, tc, rc in self.nodes:
            node_dist_to_sphere_center = np.sqrt(
                np.power((x - xc), 2) +
                np.power((y - yc), 2) +
                np.power((z - zc), 2)
            )
            if node_dist_to_sphere_center < radius:
                struct_node_ids.append(nid)
        return struct_node_ids

    def find_nodes_in_cylinder(self, s1, s2, srad, longitudinal_direction='x'):
        struct_node_ids = []
        for nid, nx, ny, nz, tc, rc in self.nodes:
            if longitudinal_direction == 'x':
                n1, n2 = ny, nz
            elif longitudinal_direction == 'y': 
                n1, n2 = nx, nz
            elif longitudinal_direction == 'z':
                n1, n2 = nx, ny
            else:
                raise ValueError(f"Invalid longitudinal direction of cylinder: '{longitudinal_direction}'")

            # Distance from transverse cross-section circle to node
            r_node = np.sqrt(
                np.power((n1 - s1), 2) +
                np.power((n2 - s2), 2) 
            )
            if r_node < srad:
                struct_node_ids.append(nid)
        return struct_node_ids

