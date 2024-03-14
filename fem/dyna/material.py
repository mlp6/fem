from dataclasses import dataclass, field
import math
import numpy as np
from typing import Optional

from .utils import format_dyna_number


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

    def __str__(self):
        pass

    def format_part_card(self, pid, secid, mid, title=None):
        title_string = ""
        if title is not None:
            title_string = "$ Title\n" f"{title}\n"

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

    def format_material_part_and_section_cards(
        self, part_id, title=None, is_pml_material=False
    ):
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
    density: float  # mass density (g/cm^3)
    E: float  # young's modulus (Pa)
    nu: float  # poisson's ratio
    da: float = 0.0
    db: float = 0.0
    K: float = 0.0

    def format_material_card(self, mid):
        dyna_card_string = (
            "*MAT_ELASTIC\n"
            "$ \tMass Density = {density} g/cm^3\n"
            "$ \tYoung's Modulus = {E_kpa:.2f} kPa, {E_ba:.2f} Ba\n"
            "$ \tPoisson's Ratio = {poisson}\n"
            "$ MID, DENSITY, E, PR, DA, DB, K\n"
            "{mid:d},{density},{E},{poisson},{da},{db},{K}\n"
        ).format(
            E_kpa=self.E / 1e3,
            E_ba=self.E * 10,
            mid=mid,
            density=format_dyna_number(self.density),
            E=format_dyna_number(self.E * 10),  # convert to barye
            poisson=format_dyna_number(self.nu),
            da=format_dyna_number(self.da),
            db=format_dyna_number(self.db),
            K=format_dyna_number(self.K),
        )
        return dyna_card_string

    def format_pml_card(self, mid):
        dyna_card_string = (
            "*MAT_PML_ELASTIC\n"
            "$ PML Card to match elasticity of MAT_ELASTIC isotropic material\n"
            "$ \tMass Density = {density} g/cm^3\n"
            "$ \tYoung's Modulus = {E_kpa:.2f} kPa, {E_ba:.2f} Ba\n"
            "$ \tPoisson's Ratio = {nu}\n"
            "$ MID, DENSITY, E, NU\n"
            "{mid:d},{density},{E},{nu}\n"
        ).format(
            E_kpa=self.E / 1e3,
            E_ba=self.E * 10,
            mid=mid,
            density=format_dyna_number(self.density),
            E=format_dyna_number(self.E * 10),  # convert to barye
            nu=format_dyna_number(self.nu),
        )
        return dyna_card_string


@dataclass(kw_only=True)
class KelvinMaxwellViscoelastic(Material):
    density: float  # mass density (g/cm^3)
    E: float  # young's modulus (Pa)
    nu: float  # poisson's ratio
    eta: float  # viscous modulus (Pa.s)
    K: float = field(init=False)  # bulk modulus
    g0: float = field(init=False)  # short-time shear modulus
    gi: float = field(init=False)  # long-time (infinite) shear modulus
    dc: float = field(init=False)  # decay constant (depends on formulation option f0)
    tau: float = field(init=False)  # ratio of viscosity to elasticity
    f0: int = 1  # formulation option (maxwell = 0, kelvin = 1)
    s0: int = 0

    def __post_init__(self):
        self.tau = self.eta / self.E
        self.K = 10 * (self.E / (3 * (1 - 2 * self.nu)))  # bulk modulus in Barye
        self.gi = 10 * (self.E / (2 * (1 + self.nu)))  # gi in Barye

        # 200gi used to make 3rd param too stiff of a spring so it acts as a wire
        # makes 3 parameter model into a 2 parameter model
        self.g0 = 200 * self.gi  # g0 in Barye
        self.dc = (self.tau * self.gi) / self.g0

    def format_material_card(self, mid):
        dyna_card_string = (
            "*MAT_KELVIN-MAXWELL_VISCOELASTIC\n"
            "$ 3 Parameter Standard Linear Model in {rep} representation\n"
            "$ \tMass Density = {density} g/cm^3\n"
            "$ \tYoung's Modulus = {E_kpa:.2f} kPa, {E_ba:.2f} Ba\n"
            "$ \tViscous Modulus = {eta:.2f} Pa.s\n"
            "$ \tTau = {tau:.5f} ms\n"
            "$ \tPoisson's Ratio = {nu:.5f}\n"
            "$ MID, DENSITY, K, G0, Gi, dc, f0, s0\n"
            "{mid:d},{density},{K},{g0},{gi},{dc},{f0},{s0}\n"
        ).format(
            rep="Kelvin" if self.f0 else "Maxwell",
            E_kpa=self.E / 1e3,
            E_ba=self.E * 10,
            eta=self.eta,
            tau=1e3 * self.tau,
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
            "$ PML Card to match elasticity of MAT_KELVIN-MAXWELL_VISCOELASTIC material\n"
            "$ \tMass Density = {density} g/cm^3\n"
            "$ \tYoung's Modulus = {E_kpa:.2f} kPa, {E_ba:.2f} Ba\n"
            "$ \tPoisson's Ratio = {nu}\n"
            "$ MID, DENSITY, E, NU\n"
            "{mid:d},{density},{E},{nu}\n"
        ).format(
            E_kpa=self.E / 1e3,
            E_ba=self.E * 10,
            mid=mid,
            density=format_dyna_number(self.density),
            E=format_dyna_number(self.E * 10),  # Convert from pascal to barye
            nu=format_dyna_number(self.nu),
        )
        return dyna_card_string


@dataclass(kw_only=True)
class TransverselyIsotropicElastic(Material):
    # if inc then dont pass muT or check equation condition
    rotation_angle: float
    tilt_angle: float
    density: float  # mass density (g/cm^3)
    EL: float
    ET: float
    muL: float
    muT: Optional[float] = None
    vLT: Optional[float] = 0.499

    a: np.ndarray = field(init=False)  #
    d: np.ndarray = field(init=False)  #
    vTT: float = field(init=False)

    aopt: float = 2.0
    g: float = 0.0
    sigf: float = 0.0
    XP: float = 0.0
    YP: float = 0.0
    ZP: float = 0.0
    MACF: float = 1.0
    v: list = field(default_factory=list)
    beta: float = 0.0
    ref: float = 0.0

    def __post_init__(self):
        if not self.v:
            self.v = np.array([0.0, 0.0, 0.0])

        self.set_a_and_d_vectors(self.rotation_angle, self.tilt_angle)
        self.vTT = 1 - (1 / 2) * (self.ET / self.EL)

        if self.muT is None:
            # self.muT = int(self.ET / (2 * (1 + self.vTT)))
            self.muT = self.ET / (2 * (1 + self.vTT))

        if not np.isclose(self.tilt_angle, 0):
            raise NotImplementedError

    def set_a_and_d_vectors(self, rotation_angle, tilt_angle):
        self.a = np.array(
            [
                math.cos(math.radians(rotation_angle)),
                math.sin(math.radians(rotation_angle)),
                0,
            ]
        )
        self.d = np.array([0, 0, 1])

    def format_card_properties(self, mid):
        card_props_string = (
            "$ C is the stiff (or AOS) direction\n"
            "$ MID, DENSITY, Ea, Eb, Ec, PRba, PRca, PRcb\n"
            "{mid:d},{density},{ET},{ET},{EL},{vTT},{vLT},{vLT}\n"
            "$ Gab, Gbc, Gca, AOPT, g, sigf\n"
            "{muT},{muL},{muL},{aopt},{g},{sigf}\n"
            "$ c=axd is an angle 0 with y-axis\n"
            "$ XP, YP, ZP, a1, a2, a3, MACF\n"
            "{XP},{YP},{ZP},{a1},{a2},{a3},{MACF}\n"
            "$ v1, v2, v3, d1, d2, d3, beta, ref\n"
            "{v1},{v2},{v3},{d1},{d2},{d3},{beta},{ref}\n"
        ).format(
            mid=mid,
            density=format_dyna_number(self.density),
            ET=format_dyna_number(self.ET),
            EL=format_dyna_number(self.EL),
            vTT=format_dyna_number(self.vTT),
            vLT=format_dyna_number(self.vLT),
            muT=format_dyna_number(self.muT),
            muL=format_dyna_number(self.muL),
            aopt=format_dyna_number(self.aopt),
            g=format_dyna_number(self.g),
            sigf=format_dyna_number(self.sigf),
            XP=format_dyna_number(self.XP),
            YP=format_dyna_number(self.YP),
            ZP=format_dyna_number(self.ZP),
            a1=format_dyna_number(self.a[0]),
            a2=format_dyna_number(self.a[1]),
            a3=format_dyna_number(self.a[2]),
            MACF=format_dyna_number(self.MACF),
            v1=format_dyna_number(self.v[0]),
            v2=format_dyna_number(self.v[1]),
            v3=format_dyna_number(self.v[2]),
            d1=format_dyna_number(self.d[0]),
            d2=format_dyna_number(self.d[1]),
            d3=format_dyna_number(self.d[2]),
            beta=format_dyna_number(self.beta),
            ref=format_dyna_number(self.ref),
        )
        return card_props_string

    def format_material_card(self, mid):
        return "*MAT_ORTHOTROPIC_ELASTIC\n" + self.format_card_properties(mid)

    def format_pml_card(self, mid):
        return "*MAT_PML_ORTHOTROPIC_ELASTIC\n" + self.format_card_properties(mid)
