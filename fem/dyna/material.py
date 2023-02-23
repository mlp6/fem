from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Material:
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
        "$      pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n"
        f"{pid:>10}{secid:>10}{mid:>10}{self.eosid:>10}{self.hgid:>10}{self.grav:>10}{self.adpopt:>10}{self.tmid:>10}\n"
        )
        return dyna_card_string
    
    def format_section_solid_card(self, secid):
        dyna_card_string = (
        "*SECTION_SOLID\n"
        "$    secid    elform       aet\n"
        f"{secid:>10}{self.elform:>10}{self.aet:>10}\n"
        )
        return dyna_card_string
    
    def format_material_part_and_section_cards(self, id, title=None, is_pml_material=False):
        if is_pml_material:
            material_card_string = self.format_pml_card(id)
        else:
            material_card_string = self.format_material_card(id)
        
        part_card_string = self.format_part_card(id, id, id, title=title)
        section_solid_string = self.format_section_solid_card(id)

        return material_card_string + part_card_string + section_solid_string + '\n'

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
        self.dc = (self.tau * self.gi) / self.g0

    def format_material_card(self, mid):
        dyna_card_string = (
        "*MAT_KELVIN-MAXWELL_VISCOELASTIC\n"
        f"$ -- Youngs = {self.E:.2f} kPa, Viscosity = {self.eta:.2f} Pa.s, Tau = {1e3*self.tau:.2f} ms, Poisson = {self.nu:.5f}\n"
        "$ MID, DENSITY, K, G0, Gi, dc, f0, s0\n"
        f"{mid:d},{self.density: #.7G},{self.K: #.8E},{self.g0: #.8G},{self.gi: #.8G},{self.dc: #.8E},{self.f0: #.8G},{self.s0: #.8G}\n"
        )
        return dyna_card_string
    
    def format_pml_card(self, mid):
        dyna_card_string = (
        "*MAT_PML_ELASTICC\n"
        "$ MID, DENSITY, E, NU\n"
        f"{mid:d},{self.density: #.8G},{self.E: #.8G},{self.nu: #.8G}\n"
        )
        return dyna_card_string
