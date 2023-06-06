from dataclasses import dataclass, field

import numpy as np

from .material import Material


@dataclass
class Structure:
    shape: str
    material: Material
    args: list = field(default_factory=list)

class DynaMeshStructureMixin:
    def add_struct_list(self, struct_list):
        for s in struct_list:
            self.add_struct(s.shape, s.material, *s.args)

    def add_struct(self, shape, material, *struct_args):
        # Get nodes in struct
        nodes_in_struct = self.find_nodes_in_struct(shape, *struct_args)
        
        new_part_id = self.get_new_part_id()
        self.add_struct_to_elems(nodes_in_struct, new_part_id)

        # Create material, part, and section solid cards
        self.material_card_string += material.format_material_part_and_section_cards(
            new_part_id, title=shape
        )

        if self.has_pml():
            pml_and_struct_nodes = np.intersect1d(self.pml_node_ids, nodes_in_struct)
            if len(pml_and_struct_nodes) > 0:
                pml_part_id = self.get_new_part_id()
                self.add_struct_to_elems(pml_and_struct_nodes, pml_part_id)
                self.material_card_string += material.format_material_part_and_section_cards(
                    pml_part_id, title=shape+' pml', is_pml_material=True
                )

    def add_struct_to_elems(self, node_ids_in_struct, new_part_id, in_struct_definition='all'):
        """
        Edits the elems numpy array to change the part id of elements within a structure. By default, an element is considered within a structure if all element nodes are within the structure. The original implementation of this library considered an element to be in the structure if any nodes where within the structure. 

        Args:
            node_ids_in_struct (list): List of node ids within the structure.
            new_part_id (int): LS-DYNA part_id for the structure elements.
            in_struct_definition (str, optional): Switch for changing whether all element nodes need to be within a structure for the element to have the structure's part_id or if one or more nodes need to be within the structure. Defaults to 'all'.
        """
        def nodes_in_struct(elem_node_list, node_ids_in_struct): 
            if in_struct_definition == 'all':
                return all(elem_node_id in node_ids_in_struct for elem_node_id in elem_node_list)
            elif in_struct_definition == 'any':
                return any(elem_node_id in node_ids_in_struct for elem_node_id in elem_node_list)
            else:
                raise ValueError(f"Invalid 'in_struct_defition: {in_struct_definition}. Options: 'all', 'any'.")
        
        # For each element, check if the element is considered in the structure. Update part_id if it is.
        for elem_id, elem_part_id, *elem_node_list in self.elems:
            if nodes_in_struct(elem_node_list, node_ids_in_struct):
                # elem_id - 1 because id is 1-based indexing
                self.elems['pid'][elem_id-1] = new_part_id

    def find_nodes_in_struct(self, shape, *struct_args):
        """
        Dispatcher function to find nodes in arbitrary structures. Create a new 'find_nodes_in_shape' function and add it to the dispatcher list to extend possible shapes. Passes arbitrary arguments and keyword arguments to shape functions.

        Args:
            shape (str): Shape argument to change which shape function is called.

        Returns:
            list: List of node ids contained within the shape.
        """
        if shape == 'rectangle':
            struct_node_ids = self.find_nodes_in_rectangle(*struct_args)
        elif shape == 'sphere':
            struct_node_ids = self.find_nodes_in_sphere(*struct_args)
        elif shape == 'cylinder':
            struct_node_ids = self.find_nodes_in_cylinder(*struct_args)
        else:
            raise ValueError(f"Invalid shape: '{shape}'")
        return struct_node_ids
    
    def find_nodes_in_rectangle(self, xmin, xmax, ymin, ymax, zmin, zmax):
        """
        Find all nodes within a rectangular region of the mesh.

        Args:
            xmin (float): Minimum extent of rectangle in x dimension
            xmax (float): Maximum extent of rectangle in x dimension
            ymin (float): Minimum extent of rectangle in y dimension
            ymax (float): Maximum extent of rectangle in y dimension
            zmin (float): Minimum extent of rectangle in z dimension
            zmax (float): Maximum extent of rectangle in z dimension

        Returns:
            list: List of node ids contained within the rectangular region.
        """
        struct_node_ids = []
        for nid, x, y, z, tc, rc in self.nodes:
            in_x_extent = (x >= xmin) and (x <= xmax)
            in_y_extent = (y >= ymin) and (y <= ymax)
            in_z_extent = (z >= zmin) and (z <= zmax)

            if in_x_extent and in_y_extent and in_z_extent:
                struct_node_ids.append(nid)
        return struct_node_ids

    def find_nodes_in_sphere(self, xc, yc, zc, radius):
        """
        Find all nodes within a spherical region of the mesh.

        Args:
            xc (float): X coordinate of sphere centroid.
            yc (float): Y coordinate of sphere centroid.
            zc (float): Z coordinate of sphere centroid.
            radius (float): Radius of spherical region.

        Returns:
            list: List of node ids contained within the spherical region.
        """
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
        """
        Find all nodes within a cylindrical region of the mesh. This function by default extends the longitudinal direction of the cylinder all the way through the mesh, similar to the CIRS cylindrical phantoms or when modeling fibers. A new function would be needed for fibers with length smaller than the mesh geometry. 

        Args:
            s1 (float): Center of cross-sectional circle along dimension 1. The definition of dimension 1 depends on the longitudinal_direction kwarg (eg, with longitudinal_direction='x', dimension 1 is y and dimension 2 is z). See code below for definitions.
            s2 (float): Center of cross-sectional circle along dimension 2.
            srad (float): Radius of the cross-sectional circle.
            longitudinal_direction (str, optional): Dimension to consider the longitudinal axis of the cylinder region. Defaults to 'x'.

        Returns:
            list: List of node ids contained within the cylindrical region.
        """
        struct_node_ids = []
        for nid, nx, ny, nz, tc, rc in self.nodes:
            if longitudinal_direction == 'x':  
                n1, n2 = ny, nz     # cross-sectional circle dimensions: 1=y, 2=z
            elif longitudinal_direction == 'y': 
                n1, n2 = nx, nz     # cross-sectional circle dimensions: 1=x, 2=z
            elif longitudinal_direction == 'z':
                n1, n2 = nx, ny     # cross-sectional circle dimensions: 1=x, 2=y
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

