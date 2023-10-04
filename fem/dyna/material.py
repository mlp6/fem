from dataclasses import dataclass, field

from ._writer import format_dyna_number


@dataclass(kw_only=True)
class Material:
    """
    Base class for LS-DYNA materials. Inherit from this class whenever creating a new material class. Includes part and section solid keyword arguments that have reasonable defaults and can still be set on subclass material object instantiation. Also provides functions necessary for writing section solid and part cards and overrideable functions for material and pml card writing.
    """
    # Part kwargs
    eosid: int = 0
    hgid: int = 0
    grav: int = 0
    adpopt: int = 0
    tmid: int = 0

    # Section solid kwargs
    elform: int = 2
    aet: int = 0

    def format_material_card(self, mid):
        pass

    def format_pml_card(self, mid):
        pass

    def format_part_card(self, pid, secid, mid, title=None):
        title_string = ''
        if title is not None:
            title_string = (
                "$ Title\n"
                f"{title}\n"
            )

        dyna_card_string = (
        "*PART\n"
        f"{title_string}"
        "$ pid, secid, mid, eosid, hgid, grav, adpopt, tmid\n"
        f"{pid},{secid},{mid},{self.eosid},{self.hgid},{self.grav},{self.adpopt},{self.tmid}\n"
        )
        return dyna_card_string
    
    def format_section_solid_card(self, secid):
        dyna_card_string = (
        "*SECTION_SOLID\n"
        "$ secid, elform, aet\n"
        f"{secid},{self.elform},{self.aet}\n"
        )
        return dyna_card_string
    
    def format_material_part_and_section_cards(self, part_id, title=None, is_pml_material=False):
        if is_pml_material:
            material_card_string = self.format_pml_card(part_id)
        else:
            material_card_string = self.format_material_card(part_id)
        
        part_card_string = self.format_part_card(part_id, part_id, part_id, title=title)
        section_solid_card_string = self.format_section_solid_card(part_id)
        part_and_section_card_string = part_card_string + section_solid_card_string

        return part_and_section_card_string, material_card_string

@dataclass(kw_only=True)
class Elastic(Material):
    density: float                 
    E: float                       # young's modulus
    nu: float                      # poisson's ratio
    da: float = 0.0
    db: float = 0.0
    K: float = 0.0

    def format_material_card(self, mid):
        dyna_card_string = (
        "*MAT_ELASTIC\n"
        "$ MID, DENSITY, E, PR, DA, DB, K\n"
        "{mid:d},{density},{E},{poisson},{da},{db},{K}\n"
        ).format(
            mid=mid,
            density=format_dyna_number(self.density),
            E=format_dyna_number(self.E),
            poisson=format_dyna_number(self.nu),
            da=format_dyna_number(self.da),
            db=format_dyna_number(self.db),
            K=format_dyna_number(self.K),
        )
        return dyna_card_string
    
    def format_pml_card(self, mid):
        dyna_card_string = (
        "*MAT_PML_ELASTIC\n"
        "$ MID, DENSITY, E, NU\n"
        "{mid:d},{density},{E},{nu}\n"
        ).format(
            mid=mid,
            density=format_dyna_number(self.density),
            E=format_dyna_number(self.E),
            nu=format_dyna_number(self.nu),
        )
        return dyna_card_string

@dataclass(kw_only=True)
class KelvinMaxwellViscoelastic(Material):
    density: float                 
    E: float                       # young's modulus
    nu: float                      # poisson's ratio
    eta: float                     # viscous modulus
    K: float = field(init=False)   # bulk modulus
    g0: float = field(init=False)  
    gi: float = field(init=False)
    dc: float = field(init=False)
    tau: float = field(init=False)
    f0: int = 1
    s0: int = 0

    def __post_init__(self):
        self.tau = self.eta / self.E
        self.K = 10 * (self.E / (3*(1-2*self.nu)) ) # bulk modulus in Barye
        self.gi = 10 * (self.E / (2*(1+self.nu)))   # gi in Barye

        # 200gi used to make 3rd param too stiff of a spring so it acts as a wire 
        # makes 3 parameter model into a 2 parameter model
        self.g0 = 200*self.gi                         # g0 in Barye
        self.dc = (self.tau * self.gi) / self.g0     # 

    def format_material_card(self, mid):
        dyna_card_string = (
        "*MAT_KELVIN-MAXWELL_VISCOELASTIC\n"
        "$ -- Youngs = {E:.2f} kPa, Viscosity = {eta:.2f} Pa.s, Tau = {tau:.2f} ms, Poisson = {nu:.5f}\n"
        "$ MID, DENSITY, K, G0, Gi, dc, f0, s0\n"
        "{mid:d},{density},{K},{g0},{gi},{dc},{f0},{s0}\n"
        ).format(
            E=self.E,
            eta=self.eta,
            tau=1e3*self.tau,
            nu=self.nu,
            mid=mid,
            density=format_dyna_number(self.density),
            K=format_dyna_number(self.K),
            g0=format_dyna_number(self.g0),
            gi=format_dyna_number(self.gi),
            dc=format_dyna_number(self.dc),
            f0=format_dyna_number(self.f0),
            s0=format_dyna_number(self.s0),
        )
        return dyna_card_string
    
    def format_pml_card(self, mid):
        dyna_card_string = (
        "*MAT_PML_ELASTIC\n"
        "$ MID, DENSITY, E, NU\n"
        "{mid:d},{density},{E},{nu}\n"
        ).format(
            mid=mid,
            density=format_dyna_number(self.density),
            E=format_dyna_number(self.E),
            nu=format_dyna_number(self.nu),
        )
        return dyna_card_string
