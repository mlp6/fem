import datetime
import pathlib

import numpy as np

from ._structure import Structure
from .utils import format_dyna_number


class DynaMeshWriterMixin:
    def set_control(self, end_time, dt_init=1e-6, tssfac=0.02):
        """
        Create a control card string. These cards set total simulation length, initial simulation backend time step, and time step scaling factor.

        Args:
            end_time (_type_): _description_
            dt_init (_type_, optional): _description_. Defaults to 1e-6.
            tssfac (float, optional): _description_. Defaults to 0.02.
        """
        self.control_card_string = (
            "*CONTROL_ENERGY\n"
            "$ hgen, rwen, slnten, rylen\n"
            "2,2,2,2\n"
            "*CONTROL_MPP_IO_NOFULL\n"
            "*CONTROL_TERMINATION\n"
            "$ endtim, endcyc, dtmin, endeng, endmas\n"
            "{endtim},0,0.0,0.0,0.0\n"
            "*CONTROL_TIMESTEP\n"
            "$ dtinit, tssfac, isdo, tslimt, dt2ms, lctm, erode, ms1st\n"
            "{dtinit},{tssfac},0,0.0,0.0,1,0,0\n"
        ).format(
            endtim=format_dyna_number(end_time),
            dtinit=format_dyna_number(dt_init),
            tssfac=format_dyna_number(tssfac),
        )

    # def set_database(self, dt=2.5e-5, create_node_set=True, **create_node_set_kwargs):
    def set_database(self, dt=2.5e-5, create_node_set=True):
        """
        Create a database card string. These cards set how often and for which nodes LS-DYNA will write information during the FEM simulation.

        Args:
            dt (float, optional): Time set for LS-DYNA database writes during the simulation. Defaults to 2.5e-5.
        """
        node_set_card = ""
        match create_node_set:
            case Structure(shape="rectangle", args=_):
                shape = create_node_set.shape
                struct_args = create_node_set.args

                self.node_set_ids = self.find_nodes_in_struct(shape, *struct_args)
                self.node_set_string = f"Node set includes all nodes with shape={shape} and struct_args={str(struct_args).replace(' ', '')}"
            case True:
                # Create a node set based on the non-PML nodes
                mask = np.isin(self.nodes["id"], self.pml_node_ids, assume_unique=True)
                self.node_set_ids = self.nodes["id"][~mask]
                self.node_set_string = (
                    "Node set includes all nodes within the bounds of the PML."
                )
            case False:
                # Don't create a node set (which is actually the following single card that puts all nodes in the set)
                node_set_card = "*SET_NODE_GENERAL\n" "1\n" "ALL\n"
            case _:
                raise ValueError(
                    "When creating a node set, must either have a PML (in which case, the node set will be all non-pml nodes) or define a rectangular structure where nodes in the structure will be saved. The create_node_set argument did not match any implemented patterns."
                )

        self.database_card_string = (
            "*DATABASE_NODOUT\n"
            "$ dt, binary, lcur, ioopt, option1, option2\n"
            "{dt},0,0,1,0.0,0\n"
            "*DATABASE_EXTENT_BINARY\n"
            "$ neiph, neips, maxint, strflg, sigflg, epsflg, rltflg, engflg\n"
            "0,0,3,0,2,2,2,1\n"
            "$ cmpflg, ieverp, beamip, dcomp, shge, stssz, n3thdt, ialemat\n"
            "0,0,0,4,1,1,2,0\n"
            "*DATABASE_FORMAT\n"
            "$ iform, ibinary\n"
            "0,1\n"
            "*DATABASE_HISTORY_NODE_SET\n"
            "$ id1, id2, id3, id4, id5, id6, id7, id8\n"
            "1,0,0,0,0,0,0,0\n"
            "{node_set_card}"
        ).format(dt=format_dyna_number(dt), node_set_card=node_set_card)

    def set_master(self, title=""):
        """
        Creates LS-DYNA master keyword file. Includes control and database cards so these must be set first.

        Args:
            title (str, optional): Optional title to put at the top of the LS-DYNA deck. Defaults to ''.
        """
        if not self.control_card_string:
            raise AttributeError(
                "Control card string not set. Create a control card string before the master card string."
            )

        if not self.database_card_string:
            raise AttributeError(
                "Database card string not set. Create a database card string before the master card string."
            )

        if not self.part_and_section_card_string:
            raise ValueError(
                "Write the material card before the master card to set the parts_and_sections string. This string has to be in the master keyword file."
            )

        include_cards = (
            "*INCLUDE\n"
            "Materials.dyn\n"
            "*INCLUDE\n"
            "LoadCurves.dyn\n"
            "*INCLUDE\n"
            "../NodalLoads.dyn\n"
            "*INCLUDE\n"
            "../../elems.dyn\n"
            "*INCLUDE\n"
            "../../nodes.dyn\n"
        )

        if self.has_node_set():
            include_cards += "*INCLUDE\n" "../../node_set.dyn\n"

        self.master_card_string = (
            "$ LS-DYNA Keyword file created by fem.dyna Python functions\n"
            "$ Created on {current_time}\n"
            "*KEYWORD\n"
            "$ \n"
            f"$ {100*'-'}\n"
            "$ Control Cards\n"
            f"$ {100*'-'}\n"
            "$ \n"
            "{control}"
            f"$ {100*'-'}\n"
            "$ Database Cards\n"
            f"$ {100*'-'}\n"
            "{database}"
            f"$ {100*'-'}\n"
            "$ Part and Section Cards\n"
            f"$ {100*'-'}\n"
            "{parts_and_sections}"
            f"$ {100*'-'}\n"
            "$ Externally Defined Cards\n"
            f"$ {100*'-'}\n"
            "{include_cards}"
            "*END\n"
        ).format(
            current_time=datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
            control=self.control_card_string,
            database=self.database_card_string,
            parts_and_sections=self.part_and_section_card_string,
            include_cards=include_cards,
        )

    def write_all_dyna_cards(
        self,
        project_path,
        load_folder_name,
        material_folder_name,
        master_filename="Master.dyn",
        sim_title="",
    ):
        """
        Writes all dyna cards necessary to run a simulation to file. Generates the following directory structure:

        project_path/nodes.dyn
                    /elems.dyn
                    /node_set.dyn (if applicable)
                    /load_folder_name/
                                     /NodalLoads.dyn
                                     /material_folder_name/Materials.dyn
                                                          /LoadCurves.dyn
                                                          /master_filename

        Args:
            project_path (str): Path to base directory for simulations with shared mesh (nodes and elements files).
            load_folder_name (str): Folder name for loading type used in simulation.
            material_folder_name (str): Folder name for material used in simulation.
            master_filename (str, optional): Name of master keyword file. Defaults to 'Master.dyn'.
        """
        # Write nodes and elements to project path
        self.write_mesh_cards(project_path)

        # Write all other cards
        self.write_non_mesh_cards(
            project_path,
            load_folder_name,
            material_folder_name,
            master_filename=master_filename,
            sim_title=sim_title,
        )

    def write_mesh_cards(self, project_path):
        """
        Writes all dyna mesh cards. Generates the following directory structure:

        project_path/nodes.dyn
                    /elems.dyn
                    /node_set.dyn (if applicable)

        Args:
            project_path (str): Path to base directory for simulations with shared mesh (nodes and elements files).
        """
        # Create a Path object for each subpath. Create folders if necessary.
        project_path = pathlib.Path(project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        # Write nodes and elements to project path
        self.write_nodes(project_path)
        self.write_elems(project_path)

    def write_non_mesh_cards(
        self,
        project_path,
        load_folder_name,
        material_folder_name,
        master_filename="Master.dyn",
        sim_title="",
    ):
        """
        Writes all non-mesh cards necessary to run a simulation to file. Generates the following directory structure:

        project_path/load_folder_name/
                                     /NodalLoads.dyn
                                     /material_folder_name/Materials.dyn
                                                          /LoadCurves.dyn
                                                          /master_filename

        Args:
            project_path (str): Path to base directory for simulations with shared mesh (nodes and elements files).
            load_folder_name (str): Folder name for loading type used in simulation.
            material_folder_name (str): Folder name for material used in simulation.
            master_filename (str, optional): Name of master keyword file. Defaults to 'Master.dyn'.
        """
        # Create a Path object for each subpath. Create folders if necessary.
        project_path = pathlib.Path(project_path)
        load_path = project_path / load_folder_name
        material_path = load_path / material_folder_name
        material_path.mkdir(parents=True, exist_ok=True)

        # Write loads to load path
        self.write_dyna_card(load_path, "NodalLoads.dyn", self.load_card_string)

        # Write materials, load curve, master keyword file to material path
        self.write_materials(material_path)
        self.write_dyna_card(
            material_path, "LoadCurves.dyn", self.load_curve_card_string
        )
        self.set_master(title=sim_title)
        self.write_dyna_card(material_path, master_filename, self.master_card_string)

    def write_dyna_card(self, base_path, filename, text):
        """
        Wrapper for basic writing strings to file. Useful for dyna cards held as strings in memory.
        """
        base_path = pathlib.Path(base_path)
        base_path.mkdir(parents=True, exist_ok=True)
        with open(base_path / filename, "w") as fh:
            fh.write(text)

    def write_materials(self, material_card_path):
        """
        Write materials list of dictionaries to Materials.dyn file. Parts and section cards are also reset and saved as part of the mesh object, but these cards are not written to file until the master card is written.

        Args:
            material_card_path (str): Path to save Materials.dyn card
        """

        # Reset part/section and materials cards
        self.part_and_section_card_string = ""
        self.material_card_string = ""

        for mat in self.materials:
            part_and_section_card_string, material_card_string = mat[
                "material"
            ].format_material_part_and_section_cards(
                mat["part_id"],
                title=mat["title"],
                is_pml_material=False,
            )

            self.part_and_section_card_string += part_and_section_card_string
            self.material_card_string += material_card_string

        for mat in self.pml_materials:
            part_and_section_card_string, material_card_string = mat[
                "material"
            ].format_material_part_and_section_cards(
                mat["part_id"],
                title=mat["title"],
                is_pml_material=True,
            )

            self.part_and_section_card_string += part_and_section_card_string
            self.material_card_string += material_card_string

        self.write_dyna_card(
            material_card_path, "Materials.dyn", self.material_card_string
        )

    def write_nodes(self, base_path="./", header_comment=""):
        """
        Write nodes array to file. Format follows LS-DYNA manual for *NODE cards. Translational and rotational constraints for each node are included.

        Args:
            base_path (str, optional): Path to save nodes.dyn. Defaults to './'.
            header_comment (str, optional): Comment to add to top of nodes file. Defaults to "".
        """
        # Make sure base_path is a Path object
        base_path = pathlib.Path(base_path)
        with open(base_path / "nodes.dyn", "w") as fh:
            # Only add header comment line if one exists
            if header_comment:
                fh.write(f"$ {header_comment}\n")

            # Write nodes card header
            fh.write("*NODE\n")
            fh.write(f"$ Mesh size:\n")
            fh.write(f"$ Number of nodes = {self.nodes.shape[0]}\n")
            fh.write(
                f"$ nx={self.coords.nx}, xmin={self.coords.xmin:.4f}, xmax={self.coords.xmax:.4f}, dx={self.coords.dx:.4f}\n"
            )
            fh.write(
                f"$ ny={self.coords.ny}, ymin={self.coords.ymin:.4f}, ymax={self.coords.ymax:.4f}, dy={self.coords.dy:.4f}\n"
            )
            fh.write(
                f"$ nz={self.coords.nz}, zmin={self.coords.zmin:.4f}, zmax={self.coords.zmax:.4f}, dz={self.coords.dz:.4f}\n"
            )
            fh.write(f"$ symmetry={self.symmetry}\n")
            fh.write("$ nid, x, y, z, tc, rc\n")

            # Write all nodes to file
            for nid, x, y, z, tc, rc in self.nodes:
                fh.write(f"{nid},{x:.6f},{y:.6f},{z:.6f},{tc},{rc}\n")

            fh.write("*END\n")

        if self.has_node_set():
            with open(base_path / "node_set.dyn", "w") as fh:
                # Write nodes card header
                fh.write("*SET_NODE_LIST_TITLE\n")
                fh.write("Database Nodout Nodes\n")
                fh.write(f"$ {self.node_set_string}\n")
                fh.write(f"$ Number of nodes in set = {len(self.node_set_ids)}\n")
                node_set = self.nodes[
                    self.node_set_ids - 1
                ]  # -1 since node_ids are 1-based indexing and slicing is 0-based
                for d in "xyz":
                    coords = np.unique(node_set[d])
                    fh.write(
                        f"$ n{d}={coords.shape[0]}, {d}min={np.min(coords):.4f}, {d}max={np.max(coords):.4f}\n"
                    )
                fh.write("$ sid, da1, da2, da3, da4, solver\n")
                fh.write("1,0.0,0.0,0.0,0.0,MECH\n")
                fh.write("$ nid1, nid2, nid3, nid4, nid5, nid6, nid7, nid8\n")

                # Write all nodes in node set to file
                row = ""
                for i, value in enumerate(self.node_set_ids):
                    remainder = (i + 1) % 8
                    if remainder != 1:
                        row += ","
                    row += str(value)
                    if (remainder == 0) or (i == len(self.node_set_ids) - 1):
                        fh.write(row + "\n")
                        row = ""
                fh.write("*END\n")

    def write_elems(self, base_path="./", header_comment=""):
        """
        Write elements array to file. Format follows LS-DYNA manual for *ELEMENT_SOLID cards.

        Args:
            base_path (str, optional): Path to save elems.dyn. Defaults to './'.
            header_comment (str, optional): Comment to add to top of elemenets file. Defaults to "".
        """
        # Make sure base_path is a path object
        base_path = pathlib.Path(base_path)
        with open(base_path / "elems.dyn", "w") as fh:
            # Only add header comment line if one exists
            if header_comment:
                fh.write(f"$ {header_comment}\n")

            # Write elements card header
            fh.write("*ELEMENT_SOLID\n")
            fh.write(f"$ Number of elements = {self.elems.shape[0]}\n")
            fh.write("$ nid, pid, n1, n2, n3, n4, n5, n6, n7, n8\n")

            # Write all elements to file
            for nid, pid, n1, n2, n3, n4, n5, n6, n7, n8 in self.elems:
                fh.write(f"{nid},{pid},{n1},{n2},{n3},{n4},{n5},{n6},{n7},{n8}\n")

            fh.write("*END\n")
