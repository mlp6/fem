import datetime
import pathlib


def format_dyna_number(num):
    snum = str(num)

    if len(snum) > 10:
        # Convert number to scientific notation
        snum = "{:E}".format(num)

        # If number string is greater than 10 characters, remove leading zeros from exponent
        if len(snum) > 10:
            base, exponent = snum.split('E')
            sign = exponent[0]
            exponent = exponent[1:].lstrip('0')
            snum = base + 'E' + sign + exponent

        # If number string is still greater than 10 characters, remove precision bits to make it 10 characters long
        if len(snum) > 10: 
            base, exponent = snum.split('E')
            precision_bits_to_remove = len(snum) - (10 - len(exponent) + 2)
            snum = base[:-precision_bits_to_remove] + 'E' + exponent

    return snum

class DynaMeshWriterMixin:
    def set_control(self, end_time, dt_init=1e-6, tssfac=0.02):
        self.control_card_string = (
            "*CONTROL_ENERGY\n"
            "$#    hgen      rwen    slnten     rylen\n"
            "        2         2         2         2\n"
            "*CONTROL_MPP_IO_NOFULL\n"
            "*CONTROL_TERMINATION\n"
            "$#  endtim    endcyc     dtmin    endeng    endmas\n"
            "{endtim}        0     0.000     0.000     0.000\n"
            "*CONTROL_TIMESTEP\n"
            "$#  dtinit    tssfac      isdo    tslimt     dt2ms      lctm     erode     ms1st\n"
            "{dtinit}  {tssfac}         0     0.000     0.000         1         0         0\n"
            "$#  dt2msf   dt2mslc     imscl    unused    unused     rmscl\n"
            "    0.000         0         0                         0.000\n"
        ).format(
            endtim=format_dyna_number(end_time),
            dtinit=format_dyna_number(dt_init),
            tssfac=format_dyna_number(tssfac)
        )

    def set_database(self, dt=2.5e-5):
        self.database_card_string = (
            "*DATABASE_NODOUT\n"
            "$#      dt    binary      lcur     ioopt   option1   option2\n"
            "{dt}         0         0         1     0.000         0\n"
            "*DATABASE_EXTENT_BINARY\n"
            "$#   neiph     neips    maxint    strflg    sigflg    epsflg    rltflg    engflg\n"
            "        0         0         3         0         2         2         2         1\n"
            "$#  cmpflg    ieverp    beamip     dcomp      shge     stssz    n3thdt   ialemat\n"
            "        0         0         0         4         1         1         2         0\n"
            "$# nintsld   pkp_sen      sclp    unused     msscl     therm    intout    nodout\n"
            "        1         0     0.000                   0         0STRESS              \n"
            "$#    dtdt    resplt\n"
            "        0         0\n"
            "*DATABASE_HISTORY_NODE_SET\n"
            "$#     id1       id2       id3       id4       id5       id6       id7       id8\n"
            "        1         0         0         0         0         0         0         0\n"
        ).format(
            dt=format_dyna_number(dt)
        )
    
    def set_master(self, title=''): 
        self.master_card_string = (
            "$ LS-DYNA Keyword file created by fem.dyna Python functions\n"
            "$ Created on {current_time}\n"
            "*KEYWORD\n"
            "{control}"
            "{database}"
            "*INCLUDE\n"
            "../../nodes.dyn\n"
            "*INCLUDE\n"
            "../../elems.dyn\n"
            "*INCLUDE\n"
            "../NodalLoads.dyn\n"
            "*INCLUDE\n"
            "Materials.dyn\n"
            "*END\n"
        ).format(
            current_time=datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
            control=self.control_card_string,
            database=self.database_card_string
        )

    def write_all_dyna_cards(self, project_path, load_folder_name, material_folder_name):
        project_path = pathlib.Path(project_path)
        load_path = project_path / load_folder_name
        material_path = load_path / material_folder_name
        material_path.mkdir(parents=True, exist_ok=True)

        self.write_nodes(project_path)
        self.write_elems(project_path)

        self.write_dyna_card(material_path, 'Materials.dyn', self.material_card_string)
        self.write_dyna_card(material_path, 'Master.dyn', self.master_card_string)

    def write_dyna_card(self, base_path, filename, text):
        with open(base_path / filename, "w") as fh:
            fh.write(text)

    def write_nodes(self, base_path='./', header_comment=""):
        base_path = pathlib.Path(base_path)
        with open(base_path / 'nodes.dyn', 'w') as fh:
            if header_comment:
                fh.write(f"{header_comment}\n")
            fh.write("*NODE\n")
            fh.write("$ NID, x, y, z, TC, RC\n")

            for nid, x, y, z, tc, rc in self.nodes:
                fh.write(f"{nid},{x:.6f},{y:.6f},{z:.6f},{tc},{rc}\n")
            
            fh.write("*END\n")

    def write_elems(self, base_path='./', header_comment=""):
        base_path = pathlib.Path(base_path)
        with open(base_path / 'elems.dyn', 'w') as fh:
            if header_comment:
                fh.write(f"{header_comment}\n")
            fh.write("*ELEMENT_SOLID\n")
            fh.write("$ NID, PID, n1, n2, n3, n4, n5, n6, n7, n8\n")

            for nid, pid, n1, n2, n3, n4, n5, n6, n7, n8 in self.elems:
                fh.write(f"{nid},{pid},{n1},{n2},{n3},{n4},{n5},{n6},{n7},{n8}\n")
            
            fh.write("*END\n")

