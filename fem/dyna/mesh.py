import logging
from dataclasses import dataclass, field
from itertools import product

import numpy as np

from ._constraints import DynaMeshConstraintsMixin
from ._loads import DynaMeshLoadsMixin
from ._structure import DynaMeshStructureMixin
from ._writer import DynaMeshWriterMixin
from .material import Material
from .utils import count_header_comment_skips

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
    nx: int
    ny: int
    nz: int
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float
    zmax: float
    x: np.ndarray = field(init=False, repr=False)
    y: np.ndarray = field(init=False, repr=False)
    z: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
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
    coords: Coordinates
    symmetry: str
    material: Material
    n_materials: int = 0

    n_nodes: int = field(init=False)
    nodes: np.ndarray = field(init=False, repr=False)

    nex: int = field(init=False)
    ney: int = field(init=False)
    nez: int = field(init=False)
    n_elems: int = field(init=False)
    elems: np.ndarray = field(init=False, repr=False)

    pml_nodes: list[int] = field(default_factory=list)

    material_card_string: str = field(init=False, repr=False)

    def __post_init__(self):
        self.n_nodes = self.coords.nx * self.coords.ny * self.coords.nz
        self.nodes = self._create_nodes_record_array()

        self.nex, self.ney, self.nez = self.coords.nx - 1, self.coords.ny - 1, self.coords.nz - 1
        self.n_elems = self.nex * self.ney * self.nez
        self.elems = self._create_elems_record_array()

        new_part_id = self.get_new_part_id()
        self.material_card_string = self.material.format_material_part_and_section_cards(new_part_id, title='background')

    def _create_nodes_record_array(self):
        node_ids = np.arange(self.n_nodes) + 1

        coords_cartesian_product = np.array(list(product(
            self.coords.x, self.coords.y, self.coords.z
        )))

        node_tc_and_rc = np.zeros((self.n_nodes,2))

        nodes_arr = np.concatenate((
            node_ids.reshape(-1,1),
            np.array(coords_cartesian_product), 
            node_tc_and_rc
            ), axis=1
        )
        return np.rec.fromarrays(nodes_arr.T, dtype=NODES_DT)
    
    def _create_elems_record_array(self):
        nodes_3d = self.get_nodes_3d()

        elems_list = []
        for iez in range(self.nez):
            for iey in range(self.ney):
                for iex in range(self.nex):
                    elem_nodes = nodes_3d[iex:iex+2, iey:iey+2, iez:iez+2]['id'].reshape(-1,)
                    elem_nodes[2:4] = np.flip(elem_nodes[2:4])
                    elem_nodes[6:8] = np.flip(elem_nodes[6:8])
                    elems_list.append( elem_nodes )

        elem_ids = np.arange(self.n_elems) + 1
        part_ids = np.ones((self.n_elems,1))
        elems_arr = np.concatenate((
            elem_ids.reshape(-1,1),
            part_ids,
            np.array(elems_list)
            ), axis=1
        )
        return np.rec.fromarrays(elems_arr.T, dtype=ELEMS_DT)
    
    def add_pml(self, pml_thickness):
        new_part_id = self.get_new_part_id()
        self.material_card_string += self.material.format_material_part_and_section_cards(
            new_part_id, title='background pml', is_pml_material=True
        )
        self.pml_nodes = self.find_nodes_in_pml(pml_thickness)
        self.add_struct_to_elems(self.pml_nodes, new_part_id)
    
    def find_nodes_in_pml(self, pml_thickness):
        symmetry_planes, non_symmetry_planes = self.get_symmetry_and_non_symmetry_planes()

        pml_nodes = []
        for plane in non_symmetry_planes:
            pml_nodes.extend( self.get_plane_node_ids(plane, pml_thickness) ) 

        return np.unique(pml_nodes)
    
    def get_elems_3d(self):
        return self.elems.reshape(self.nex, self.ney, self.nez) 

    def get_nodes_3d(self):
        return self.nodes.reshape(self.coords.nx, self.coords.ny, self.coords.nz)
    
    def get_new_part_id(self):
        self.n_materials += 1
        return self.n_materials

    def get_plane_node_ids(self, direction, thickness):
        nodes_3d = self.get_nodes_3d()

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
        
        return plane_nodes['id'].reshape(-1,)
    
    def get_symmetry_and_non_symmetry_planes(self):
        all_planes =  {'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'}
        if self.symmetry == 'q':
            symmetry_planes = {'xmax', 'ymax'}
        elif self.symmetry == 'hx':   # symmetry on x normal (yz plane)
            symmetry_planes = {'xmax'}
        elif self.symmetry == 'hy':   # symmetry on y normal (xz plane)
            symmetry_planes = {'xmax'}
        elif self.symmetry == 'n':
            symmetry_planes = {None}
        else:
            raise ValueError(f"Invalid plane symmetry type: '{self.symmetry}'")

        non_symmetry_planes = all_planes - symmetry_planes
        return symmetry_planes, non_symmetry_planes
    
    def has_pml(self):
        return True if len(self.pml_nodes) else False

    

