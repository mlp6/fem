import warnings
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
class UniformCoordinates:
    """
    Defines coordinate system parameters for a 3D rectangular region.
    """

    # Number of samples in x, y, and z dimensions
    nx: int
    ny: int
    nz: int

    # Min and max values for each dimension (in centimeters)
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float

    # Coordinates for each axis (in centimeters)
    x: np.ndarray = field(init=False, repr=False)
    y: np.ndarray = field(init=False, repr=False)
    z: np.ndarray = field(init=False, repr=False)

    # Distance between nodes in each direction (in centimeters)
    dx: float = field(init=False)
    dy: float = field(init=False)
    dz: float = field(init=False)

    def __post_init__(self):
        # Setup coordinates for each axis
        self.x = np.linspace(self.xmin, self.xmax, self.nx)
        self.y = np.linspace(self.ymin, self.ymax, self.ny)
        self.z = np.linspace(self.zmin, self.zmax, self.nz)

        # Calculate distance between nodes in each direction
        self.dx = self.x[1] - self.x[0]
        self.dy = self.y[1] - self.y[0]
        self.dz = self.z[1] - self.z[0]

    def flatten(self):
        """
        Create (n_node x 3) array of all coordinates in the mesh where each row is a 3-tuple of the (x,y,z) coordinates of each node. Reordering is to use 'Fortran' or 'F' indexing (see https://numpy.org/doc/stable/reference/generated/numpy.reshape.html) to be compatible with legacy node readers. 
        """
        arr = np.array(list(product(
            self.z, self.y, self.x
        )))

        return arr[:, [2,1,0]]

@dataclass
class UniformMesh(
        DynaMeshConstraintsMixin,
        DynaMeshLoadsMixin,
        DynaMeshStructureMixin,
        DynaMeshWriterMixin,
    ):
    """
    Mesh container class to hold mesh state and methods for writing mesh state to files. Contains nodes and elements numpy record arrays, properties describing the mesh state, and strings formatted as LS-DYNA cards with information about the mesh materials, loading conditions, simulation timing controls, FEM simulation database writers, and master keyword files. 
    """
    # Basic properties of an isotropic rectangular mesh
    coords: UniformCoordinates
    symmetry: str      # Options: q - quarter symmetry, hx - half symmetry in x normal plane, hy - half symmetry in y normal plane, n - no symmetry
    material: Material

    # Total materials and loads in the mesh
    n_materials: int = field(init=False, default=0)

    # Nodes numpy record array and related properties
    nodes: np.ndarray = field(init=False, repr=False)
    n_nodes: int = field(init=False)

    # Elements numpy record array and related properties
    elems: np.ndarray = field(init=False, repr=False)
    nex: int = field(init=False)
    ney: int = field(init=False)
    nez: int = field(init=False)
    n_elems: int = field(init=False)

    # Symmetry, non-symmetry, and pml plane sets (if applicable)
    symmetry_planes: set[str] = field(default_factory=set)
    non_symmetry_planes: set[str] = field(default_factory=set)
    pml_planes: set[str] = field(default_factory=set)

    # List of node ids in pml (if applicable)
    pml_node_ids: list[int] = field(default_factory=list, repr=False)

    # Strings for each LS-DYNA deck card set
    part_and_section_card_string: str = field(init=False, repr=False, default='')
    material_card_string: str = field(init=False, repr=False, default='')
    load_card_string: str = field(init=False, repr=False, default='')
    load_curve_card_string: str = field(init=False, repr=False, default='')
    control_card_string: str = field(init=False, repr=False, default='')
    database_card_string: str = field(init=False, repr=False, default='')
    master_card_string: str = field(init=False, repr=False, default='')

    def __post_init__(self):
        self._validate_symmetry_condition()

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
        self.part_and_section_card_string, self.material_card_string = self.material.format_material_part_and_section_cards(new_part_id, title='background')

    def _validate_symmetry_condition(self):
        def _is_zero(v):
            return np.isclose(v, 0.0, atol=1e-9)
        
        def _check_for_zero_crossing(v_str):
            if not any(_is_zero(getattr(self.coords, v_str))):
                warnings.warn(f"No zero crossing found on {v_str} axis. Make sure {v_str}min and {v_str}max coordinate extents are equal magnitude and the n{v_str} is odd")

        # Warn if nx, ny, or nz are even
        if (self.coords.nx % 2 == 0) or (self.coords.ny % 2 == 0) or (self.coords.nz % 2 == 0):
            warnings.warn("Either nx, ny, or nz was set to an even number. This could cause there to not be any nodes at the zero crossing of the axis with an even number of nodes. Change to odd number to avoid bugs unless you know what you're doing")

        all_planes =  {'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'}
        symmetry_planes = set()
        for dim in ['xmin', 'xmax', 'ymin', 'ymax']:
            if _is_zero(getattr(self.coords, dim)):
                symmetry_planes.add(dim)

        # Quarter symmetry: make sure x and y both have zero as a min or max
        if self.symmetry == 'q':
            if len(symmetry_planes) != 2:
                raise ValueError(f"Two planes should have either the min or max at zero for quarter symmetry. Planes found at zero: {symmetry_planes}")

        # Half symmetry: make sure either x or y have zero as a min or max
        elif self.symmetry == 'hx':
            # symmetry on x normal (yz plane)
            # if (len(symmetry_planes) != 1) and (not symmetry_planes[0].startswith('x')):   
            if (len(symmetry_planes) != 1) and ('xmin' not in symmetry_planes or 'xmax' not in symmetry_planes):   
                raise ValueError(f"Either xmin or xmax only should be zero for hx symmetry. Planes found at zero: {symmetry_planes}")
            
            _check_for_zero_crossing('y')

        elif self.symmetry == 'hy':
            # symmetry on y normal (xz plane)
            if (len(symmetry_planes) != 1) and (not symmetry_planes[0].startswith('y')):   
                raise ValueError(f"Either ymin or ymax only should be zero for hy symmetry. Planes found at zero: {symmetry_planes}")
            
            _check_for_zero_crossing('x')

        # No symmetry: warn if min and max extents are different since there won't be a node at 0
        elif self.symmetry == 'n':
            if (len(symmetry_planes) != 0):
                raise ValueError(f"None of the min or max extents of x or y should be at zero for a no symmetry mesh. Planes found at zero: {symmetry_planes}")

            symmetry_planes = {None}

            _check_for_zero_crossing('x')
            _check_for_zero_crossing('y')
        else:
            raise ValueError(f"Invalid plane symmetry type: '{self.symmetry}'")
        
        self.non_symmetry_planes = all_planes - symmetry_planes
        self.symmetry_planes
        

    def _create_nodes_record_array(self):
        """
        Interal method to create nodes record array from mesh properties set on object initialization.
        """
        # Create node id array (1 based indexing)
        node_ids = np.arange(self.n_nodes) + 1

        # Create (n_node x 3) array of all coordinates in the mesh where each row is a 3-tuple of the (x,y,z) coordinates of each node
        coords_cartesian_product = self.coords.flatten()

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
    
    def add_pml(self, pml_thickness, exclude_faces=None):
        """
        Add pml to a mesh without any structures. Can be used if structures have been set, but the structures won't have material specific pmls and the pml will only match the mesh background elasticity.

        Args:
            pml_thickness (int): Thickness of pml layer (number of elements)
            exclude_faces (list[str], optional): List of faces to exclude from the PML. Defaults to None. Options: 'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'.
        """
        if exclude_faces is None:
            exclude_faces = []

        # Get new part id for the pml
        new_part_id = self.get_new_part_id()

        # Update material card string with pml material
        part_and_section_card_string, material_card_string = self.material.format_material_part_and_section_cards(
            new_part_id, title='background pml', is_pml_material=True
        )
        self.part_and_section_card_string += part_and_section_card_string
        self.material_card_string += material_card_string

        # Find nodes in pml and add as a structure to the elements array
        self.pml_node_ids = self.find_nodes_in_pml(pml_thickness, exclude_faces)
        self.add_struct_to_elems(self.pml_node_ids, new_part_id)
    
    def find_nodes_in_pml(self, pml_thickness, exclude_faces):
        """
        Find all nodes within a pml based on mesh symmetry and pml_thickness.

        Args:
            pml_thickness (int): Thickness of pml (in number of elements).
            exclude_faces (list[str]): List of faces to exclude from the PML. 

        Returns:
            np.array: Nodes within the pml layers
        """

        # For each non-symmetry plane, get all node ids within the pml_thickness
        pml_thickness += 1  # number of nodes = number of elements + 1
        pml_node_ids = []
        for plane in self.non_symmetry_planes:
            if plane not in exclude_faces:
                self.pml_planes.add(plane)
                pml_node_ids.extend( self.get_plane_node_ids(plane, pml_thickness) ) 

        # Return unique ids (removes ids from overlapping plane edges)
        return np.unique(pml_node_ids)
    
    def get_elems_3d(self):
        """ Reshape elements array to 3D for matrix indexing. """
        return self.elems.reshape(self.nex, self.ney, self.nez, order='F') 

    def get_nodes_3d(self):
        """ Reshape nodes array to 3D for matrix indexing. """
        return self.nodes.reshape(self.coords.nx, self.coords.ny, self.coords.nz, order='F')
        # return self.nodes.reshape(self.coords.nx, self.coords.ny, self.coords.nz)
    
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
    
    def get_element_volume(self):
        """
        Returns the volume of each element (assumes they are all the same).
        """
        x_elem_len = (self.coords.xmax - self.coords.xmin) / self.nex
        y_elem_len = (self.coords.ymax - self.coords.ymin) / self.ney
        z_elem_len = (self.coords.zmax - self.coords.zmin) / self.nez
        return x_elem_len * y_elem_len * z_elem_len
    
    def has_pml(self):
        """
        Function to check if the mesh has a perfectly matched layer (pml).
        """
        return True if len(self.pml_node_ids) else False

    
