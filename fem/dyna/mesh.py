from dataclasses import dataclass, field
from itertools import product

import numpy as np

from ._constraints import DynaMeshConstraintsMixin
from ._loads import DynaMeshLoadsMixin
from ._structure import DynaMeshStructureMixin
from ._writer import DynaMeshWriterMixin
from .material import Material

# Data types for nodes and elements numpy record arrays
NODES_DT = [
    ('id', 'i4'), ('x', 'f4'), ('y', 'f4'),
    ('z', 'f4'), ('tc', 'i4'), ('rc', 'i4')
]
ELEMS_DT = [
    ('id', 'i4'), ('pid', 'i4'), 
    ('n1', 'i4'), ('n2', 'i4'), ('n3', 'i4'), ('n4', 'i4'),
    ('n5', 'i4'), ('n6', 'i4'), ('n7', 'i4'), ('n8', 'i4')
]

@dataclass
class Coordinates:
    """
    Defines coordinate system parameters for a 3D rectangular region.
    """

    # Number of samples in x, y, and z dimensions
    nx: int
    ny: int
    nz: int

    # Min and max values for each dimension
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float

    # Coordinates for each axis
    x: np.ndarray = field(init=False, repr=False)
    y: np.ndarray = field(init=False, repr=False)
    z: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        # Setup coordinates for each axis
        self.x = np.linspace(self.xmin, self.xmax, self.nx)
        self.y = np.linspace(self.ymin, self.ymax, self.ny)
        self.z = np.linspace(self.zmin, self.zmax, self.nz)

@dataclass
class DynaMesh(
        DynaMeshConstraintsMixin,
        DynaMeshLoadsMixin,
        DynaMeshStructureMixin,
        DynaMeshWriterMixin,
    ):
    """
    Mesh container class to hold mesh state and methods for writing mesh state to files. Contains nodes and elements numpy record arrays, properties describing the mesh state, and strings formatted as LS-DYNA cards with information about the mesh materials, loading conditions, simulation timing controls, FEM simulation database writers, and master keyword files. 

    """

    # Basic properties of an isotropic rectangular mesh
    coords: Coordinates
    symmetry: str      # Options: q - quarter symmetry, hx - half symmetry in x normal plane, hy - half symmetry in y normal plane, n - no symmetry
    material: Material

    # Total materials in the mesh
    n_materials: int = 0

    # Nodes numpy record array and related properties
    nodes: np.ndarray = field(init=False, repr=False)
    n_nodes: int = field(init=False)

    # Elements numpy record array and related properties
    elems: np.ndarray = field(init=False, repr=False)
    nex: int = field(init=False)
    ney: int = field(init=False)
    nez: int = field(init=False)
    n_elems: int = field(init=False)

    # List of node ids in pml (if applicable)
    pml_node_ids: list[int] = field(default_factory=list)

    # Strings for each LS-DYNA deck card set
    material_card_string: str = field(init=False, repr=False)
    load_card_string: str = field(init=False, repr=False)
    control_card_string: str = field(init=False, repr=False)
    database_card_string: str = field(init=False, repr=False)
    master_card_string: str = field(init=False, repr=False)

    def __post_init__(self):
        # Set total number of nodes (treating each sample in the coordinate system as a mesh node)
        self.n_nodes = self.coords.nx * self.coords.ny * self.coords.nz
        
        # Create nodes numpy record array
        self.nodes = self._create_nodes_record_array()

        # Set number of elements in each dimension and the total number of elements
        self.nex, self.ney, self.nez = self.coords.nx - 1, self.coords.ny - 1, self.coords.nz - 1
        self.n_elems = self.nex * self.ney * self.nez

        # Create elements numpy record array
        self.elems = self._create_elems_record_array()

        # Generate new part id for the mesh background
        new_part_id = self.get_new_part_id()
        
        # Add background material to material card string
        self.material_card_string = self.material.format_material_part_and_section_cards(new_part_id, title='background')

    def _create_nodes_record_array(self):
        """
        Interal method to create nodes record array from mesh properties set on object initialization.
        """
        # Create node id array (1 based indexing)
        node_ids = np.arange(self.n_nodes) + 1

        # Create (n_node x 3) array of all coordinates in the mesh where each row is a 3-tuple of the (x,y,z) coordinates of each node
        coords_cartesian_product = np.array(list(product(
            self.coords.x, self.coords.y, self.coords.z
        )))

        # Initialize the translational and rotational constraints for each node as 0 (no constraints in any dimension)
        node_tc_and_rc = np.zeros((self.n_nodes,2))

        # Combine node ids, coodinates, and constraints into single numpy record array
        nodes_arr = np.concatenate((
            node_ids.reshape(-1,1),
            np.array(coords_cartesian_product), 
            node_tc_and_rc
            ), axis=1
        )
        return np.rec.fromarrays(nodes_arr.T, dtype=NODES_DT)
    
    def _create_elems_record_array(self):
        """
        Interal method to create elements record array from mesh properties set on object initialization and nodes array.
        """
        # Reshape nodes for 3D matrix indexing
        nodes_3d = self.get_nodes_3d()

        # For each element in each dimension, find the nodes that make up element. Elements are assumed to be rectangular volumes and the nodes are the 8 vertices of the element. 
        elems_list = []
        for iez in range(self.nez):
            for iey in range(self.ney):
                for iex in range(self.nex):
                    # Get nodes of (iex, iey, iez) element
                    elem_nodes = nodes_3d[iex:iex+2, iey:iey+2, iez:iez+2]['id'].reshape(-1,)

                    # Reorder nodes to follow LS-DYNA's expected format for rectangular volume elements (see *ELEMENT_SOLID documentation)
                    elem_nodes[2:4] = np.flip(elem_nodes[2:4])
                    elem_nodes[6:8] = np.flip(elem_nodes[6:8])

                    # Add element nodes to list
                    elems_list.append( elem_nodes )

        # Create element id array (1 based indexing)
        elem_ids = np.arange(self.n_elems) + 1
        
        # Initialize all elements to have the same part id
        part_ids = np.ones((self.n_elems,1))

        # Combine element ids, part ids, and element nodes into single numpy record array
        elems_arr = np.concatenate((
            elem_ids.reshape(-1,1),
            part_ids,
            np.array(elems_list)
            ), axis=1
        )
        return np.rec.fromarrays(elems_arr.T, dtype=ELEMS_DT)
    
    def add_pml(self, pml_thickness):
        """
        Add pml to a mesh without any structures. Can be used if structures have been set, but the structures won't have material specific pmls and the pml will only match the mesh background elasticity.

        Args:
            pml_thickness (int): Thickness of pml layer (number of nodes)
        """

        # Get new part id for the pml
        new_part_id = self.get_new_part_id()

        # Update material card string with pml material
        self.material_card_string += self.material.format_material_part_and_section_cards(
            new_part_id, title='background pml', is_pml_material=True
        )

        # Find nodes in pml and add as a structure to the elements array
        self.pml_node_ids = self.find_nodes_in_pml(pml_thickness)
        self.add_struct_to_elems(self.pml_node_ids, new_part_id)
    
    def find_nodes_in_pml(self, pml_thickness):
        """
        Find all nodes within a pml based on mesh symmetry and pml_thickness.

        Args:
            pml_thickness (int): Thickness of pml (in number of nodes).

        Returns:
            np.array: Nodes within the pml layers
        """
        # Get the non-symmetry planes based on mesh symmetry
        symmetry_planes, non_symmetry_planes = self.get_symmetry_and_non_symmetry_planes()

        # For each non-symmetry plane, get all node ids within the pml_thickness
        pml_node_ids = []
        for plane in non_symmetry_planes:
            pml_node_ids.extend( self.get_plane_node_ids(plane, pml_thickness) ) 

        # Return unique ids (removes ids from overlapping plane edges)
        return np.unique(pml_node_ids)
    
    def get_elems_3d(self):
        """ Reshape elements array to 3D for matrix indexing. """
        return self.elems.reshape(self.nex, self.ney, self.nez) 

    def get_nodes_3d(self):
        """ Reshape nodes array to 3D for matrix indexing. """
        return self.nodes.reshape(self.coords.nx, self.coords.ny, self.coords.nz)
    
    def get_new_part_id(self):
        """ Create a new part id and increment the total number of materials. """
        self.n_materials += 1
        return self.n_materials

    def get_plane_node_ids(self, direction, thickness):
        """
        Get all node ids within a plane of the mesh.

        Args:
            direction (str): Normal (signed) direction of plane. Options: 'xmin', 'xmax', 'ymin', 'ymax', 'zmin', and 'zmax'.
            thickness (int): Thickness of plane to find node ids.

        Returns:
            np.array: 1D numpy array of node ids from the plane.
        """
        # Reshape for 3D indexing
        nodes_3d = self.get_nodes_3d()

        # Extract nodes from direction with specified thickness
        if direction == 'xmin':
            plane_nodes = nodes_3d[0:thickness,:,:]
        elif direction == 'xmax':
            plane_nodes = nodes_3d[-thickness:,:,:]
        elif direction == 'ymin':
            plane_nodes = nodes_3d[:,0:thickness,:]
        elif direction == 'ymax':
            plane_nodes = nodes_3d[:,-thickness:,:]
        elif direction == 'zmin':
            plane_nodes = nodes_3d[:,:,0:thickness]
        elif direction == 'zmax':
            plane_nodes = nodes_3d[:,:,-thickness:]
        else:
            raise ValueError(f"Direction '{direction}' invalid")
        
        # Return only the node ids
        return plane_nodes['id'].reshape(-1,)
    
    def get_symmetry_and_non_symmetry_planes(self):
        """
        Get symmetry and non-symmetry planes based on the symmetry condition.

        Returns:
            tuple[set[str]]: Tuple of two sets of strings containing the symmetry (set 1) and non-symmetry (set 2) plane names.
        """
        # Set of all planes
        all_planes =  {'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'}
        
        # Set symmetry planes set based on mesh symmetry condition
        if self.symmetry == 'q':
            symmetry_planes = {'xmax', 'ymax'}
        elif self.symmetry == 'hx':   # symmetry on x normal (yz plane)
            symmetry_planes = {'xmax'}
        elif self.symmetry == 'hy':   # symmetry on y normal (xz plane)
            symmetry_planes = {'ymax'}
        elif self.symmetry == 'n':
            symmetry_planes = {None}
        else:
            raise ValueError(f"Invalid plane symmetry type: '{self.symmetry}'")

        # Non-symmetry planes are the set difference 
        non_symmetry_planes = all_planes - symmetry_planes
        return symmetry_planes, non_symmetry_planes
    
    def has_pml(self):
        """
        Function to check if the mesh has a perfectly matched layer (pml).
        """
        return True if len(self.pml_node_ids) else False

    

