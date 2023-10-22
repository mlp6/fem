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
            self.add_struct(s.shape, s.material, s.args)

    def add_struct(self, shape, material, struct_args, title=None):
        """
        Adds a structure to the mesh. Edits the part id for elements within the structure, creates the structure material, part, and section cards, and adds a PML for the structure if structure elements overlap with the PML. 

        Args:
            shape (str): Shape of the structure.
            material (Material): Material object of the structure.
            struct_args (list): List of parameters to create structure.
        """
        if title is None:
            title = shape + f', struct_args={str(struct_args).replace(" ", "")}'

        # Get the ids of all nodes within the structure
        nodes_in_struct = self.find_nodes_in_struct(shape, *struct_args)

        # Add structure material to material list
        new_part_id = self.add_material(material, title=title)

        # Update the part id of elements in the structure
        self.add_struct_to_elems(nodes_in_struct, new_part_id)

        # If the mesh has a PML, edit the PML material where the structure overlaps to have the same elastic properties
        if self.has_pml():
            # Find nodes in both the PML and the structure
            pml_and_struct_nodes = np.intersect1d(self.pml_node_ids, nodes_in_struct)

            if len(pml_and_struct_nodes) > 0:
                # Add pml material to material list
                pml_part_id = self.add_material(material, title=title+' pml', base_material_index=new_part_id)

                # Update the part id of elements in both the structure and PML
                self.add_struct_to_elems(pml_and_struct_nodes, pml_part_id)

    def add_struct_to_elems(self, node_ids_in_struct, new_part_id, in_struct_definition='all'):
        """
        Edits the elems numpy array to change the part id of elements within a structure.
        By default, an element is considered within a structure if all element nodes are within the structure.

        Args:
            node_ids_in_struct (list): List of node ids within the structure.
            new_part_id (int): LS-DYNA part_id for the structure elements.
            in_struct_definition (str, optional): Switch for changing whether all element nodes
            need to be within a structure for the element to have the structure's part_id or if one or
            more nodes need to be within the structure. Defaults to 'all'.
        """
        if in_struct_definition not in ('all', 'any'):
            raise ValueError(f"Invalid 'in_struct_definition: {in_struct_definition}. Options: 'all', 'any'.")

        node_ids_in_struct = set(node_ids_in_struct)
        elems_unstructured = self.get_elems_unstructured()

        # Create a mask of elements that meet the condition based on in_struct_definition
        if in_struct_definition == 'all':
            condition = np.all(np.isin(elems_unstructured[:, 2:], list(node_ids_in_struct)), axis=1)
        elif in_struct_definition == 'any':
            condition = np.any(np.isin(elems_unstructured[:, 2:], list(node_ids_in_struct)), axis=1)

        # Update the part_id values for the elements that meet the condition
        self.elems['pid'][condition] = new_part_id


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
        cond_x = (self.nodes['x'] >= xmin) & (self.nodes['x'] <= xmax)
        cond_y = (self.nodes['y'] >= ymin) & (self.nodes['y'] <= ymax)
        cond_z = (self.nodes['z'] >= zmin) & (self.nodes['z'] <= zmax)
        return self.nodes['id'][cond_x & cond_y & cond_z]

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
        node_dist_to_sphere_center = np.sqrt(
            np.power((self.nodes['x'] - xc), 2) +
            np.power((self.nodes['y'] - yc), 2) +
            np.power((self.nodes['z'] - zc), 2)
        )
        return self.nodes['id'][node_dist_to_sphere_center < radius]

    def find_nodes_in_cylinder(self, s1, s2, srad, longitudinal_direction='x'):
        """
        Find all nodes within a cylindrical region of the mesh. This function by default extends the longitudinal direction of the cylinder all the way through the mesh, similar to the CIRS cylindrical phantoms or when modeling fibers. A new function would be needed for fibers with length smaller than the mesh geometry. 

        Args:
            s1 (float): Center of cross-sectional circle along dimension 1 in centimeters. The definition of dimension 1 depends on the longitudinal_direction kwarg (eg, with longitudinal_direction='x', dimension 1 is y and dimension 2 is z). See code below for definitions.
            s2 (float): Center of cross-sectional circle along dimension 2 in centimeters.
            srad (float): Radius of the cross-sectional circle in centimeters.
            longitudinal_direction (str, optional): Dimension to consider the longitudinal axis of the cylinder region. Defaults to 'x', in other words, the cylinder extrudes in the 'x' (or elevational) direction.

        Returns:
            list: List of node ids contained within the cylindrical region.
        """
        if longitudinal_direction == 'x':  
            # cross-sectional circle dimensions: 1=y, 2=z
            # Distance from transverse cross-section circle to node
            r_node = np.sqrt(
                np.power((self.nodes['y'] - s1), 2) +
                np.power((self.nodes['z'] - s2), 2) 
            )
        elif longitudinal_direction == 'y': 
            # cross-sectional circle dimensions: 1=x, 2=z
            r_node = np.sqrt(
                np.power((self.nodes['x'] - s1), 2) +
                np.power((self.nodes['z'] - s2), 2) 
            )
        elif longitudinal_direction == 'z':
            # cross-sectional circle dimensions: 1=x, 2=y
            r_node = np.sqrt(
                np.power((self.nodes['x'] - s1), 2) +
                np.power((self.nodes['y'] - s2), 2) 
            )
        else:
            raise ValueError(f"Invalid longitudinal direction of cylinder: '{longitudinal_direction}'")

        return self.nodes['id'][r_node < srad]

