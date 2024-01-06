import numpy as np
from scipy.interpolate import interpn
from scipy.io import loadmat

from ._writer import format_dyna_number


def generate_arf_load_curve_timing(t_arf, dt):
    """
    Create a ARF dyna timing curve. Can generate trapezoidal excitations by adjusting dt.

    Args:
        t_arf (float): ARF push duration (seconds).
        dt (float): Time step to transition ARF load on and off (seconds).

    Returns:
        list[list]: X and y values of load curve timing.
    """
    if dt <= 0:
        dt = 1e-6

    t = [
        [0, 0],
        [dt, 1],
        [dt + t_arf, 1],
        [2 * dt + t_arf, 0],
    ]
    return t


def generate_multipush_load_curve_timing(t_arf, dt, n_arf, tracks_between, prf):
    """
    Create a multi-push dyna timing curve. Can generate symmetric trapezoidal excitations by adjusting dt.

    Args:
        t_arf (float): ARF push duration (seconds).
        dt (float): Time step to transition ARF load on and off (seconds).
        n_arf (int): Number of successive ARF excitations.
        tracks_between (int): Number of tracking pulses between each ARF push.
        prf (float): Scanner pulse repetition frequency (Hz)

    Returns:
        list[list]: X and y values of load curve timing.
    """
    if dt <= 0:
        dt = 1e-6

    # Delay between each arf push
    t_delay = (tracks_between + 1) / prf

    t = []
    for iarf in range(n_arf):
        narf_delay = iarf * t_delay
        t.extend(
            [
                [narf_delay, 0],
                [narf_delay + dt, 1],
                [narf_delay + dt + t_arf, 1],
                [narf_delay + 2 * dt + t_arf, 0],
            ]
        )
    return t


def generate_multipush_hydrophone_measured_load_curve_timing(
    t_arf, dt, n_arf, tracks_between, prf_arf, prf_track
):
    """
    Create a multi-push dyna timing curve matching hydrophone measured prfs. Can generate symmetric trapezoidal excitations by adjusting dt.

    Args:
        t_arf (float): ARF push duration (seconds).
        dt (float): Time step to transition ARF load on and off (seconds).
        n_arf (int): Number of successive ARF excitations.
        tracks_between (int): Number of tracking pulses between each ARF push.
        prf_push (float): Scanner pulse repetition frequency (Hz) during push
        prf_track (float): Scanner pulse repetition frequency (Hz) during tracks

    Returns:
        list[list]: X and y values of load curve timing.
    """
    if dt <= 0:
        dt = 1e-6

    # Delay between each arf push
    t_delay = (1 / prf_arf) + tracks_between * (1 / prf_track)

    t = []
    for iarf in range(n_arf):
        narf_delay = iarf * t_delay
        t.extend(
            [
                [narf_delay, 0],
                [narf_delay + dt, 1],
                [narf_delay + dt + t_arf, 1],
                [narf_delay + 2 * dt + t_arf, 0],
            ]
        )
    return t


class DynaMeshLoadsMixin:
    def add_load_curve(self, load_curve_id, load_type, load_timing_args):
        """
        Creates a *DEFINE_CURVE dyna card string to define the timing and amplitude of an applied load. Serves as a dispatcher function for multiple different load types.

        Args:
            load_curve_id (int): Unique load curve ID associated with a load.
            load_type (str): Defines the function used to generate load curve timings.
            load_timing_args (list): List of arguments to pass to load curve timing generation function.
        """
        # Get timing array based on load curve type
        if load_type == "arf":
            t = generate_arf_load_curve_timing(*load_timing_args)
        elif load_type == "multipush":
            t = generate_multipush_load_curve_timing(*load_timing_args)
        elif load_type == "multipush-hydrophone":
            t = generate_multipush_hydrophone_measured_load_curve_timing(
                *load_timing_args
            )
        else:
            raise ValueError("Invalid load_type.")

        # Format timing array for load curve string
        load_timing_str = ""
        for a, o in t:
            load_timing_str += (
                f"{format_dyna_number(a, 20):>20}{format_dyna_number(o, 20):>20}\n"
            )

        # Construct load curve string
        self.load_curve_card_string += (
            "*DEFINE_CURVE\n"
            "$ Load curve for load_type={load_type}\n"
            "$ Load timing args: {load_timing_args}\n"
            "$ lcid, sidr, sfa, sfo, offa, offo, dattyp\n"
            "{lcid},0,1.0,1.0,0.0,0.0,0\n"
            "$                 a1                  o1\n"
            "{load_timing}"
        ).format(
            load_type=load_type,
            load_timing_args=str(load_timing_args),
            lcid=load_curve_id,
            load_timing=load_timing_str,
        )

    def make_loads_temps(
        self,
        load_curve_id,
        arf_push_duration,
        cv,
        arf_intensity_file,
        normalization_isppa=None,
        normalization_intensity_file=None,
    ):
        if normalization_isppa is not None and normalization_intensity_file is not None:
            raise ValueError(
                "Cannot provide both normalization_isppa and normalization_intensity_file."
            )

        if normalization_isppa is None and normalization_intensity_file is None:
            raise ValueError(
                "Must provide either normalization_isppa or normalization_intensity_file."
            )

        if normalization_isppa is not None:
            pass
        else:
            pass

    def interpolate_field_to_dyna_intensities(self, field_load_file):
        mat = loadmat(field_load_file)

        if "ax_extent" in mat["FIELD_PARAMS"].dtype.names:
            extent = dict(
                lat=mat["FIELD_PARAMS"]["lat_extent"][0, 0].reshape(
                    -1,
                ),
                ele=mat["FIELD_PARAMS"]["ele_extent"][0, 0].reshape(
                    -1,
                ),
                ax=mat["FIELD_PARAMS"]["ax_extent"][0, 0].reshape(
                    -1,
                ),
            )
        else:
            mpn = mat["FIELD_PARAMS"]["measurementPoints"][0, 0]
            extent = dict(
                lat=np.unique(mpn[:, 0]),
                ele=np.unique(mpn[:, 1]),
                ax=np.unique(mpn[:, 2]),
            )

        nlat, nele, nax = len(extent["lat"]), len(extent["ele"]), len(extent["ax"])
        intensity = mat["intensity"].reshape(nax, nlat, nele)

        # Swap to dyna coord system (ele, lat, -ax)
        intensity = np.swapaxes(intensity, 0, 2)
        intensity = np.flip(intensity, axis=2)

        field_points = (extent["ele"] * 1e2, extent["lat"] * 1e2, -extent["ax"] * 1e2)
        dyna_points = self.coords.flatten()
        intensity_interp = interpn(
            field_points,
            intensity,
            dyna_points,
            method="linear",
            bounds_error=False,
            fill_value=0.0,
        )

        node_ids = np.arange(self.n_nodes) + 1
        return node_ids, intensity_interp

    def calculate_point_loads_from_field_intensities(
        self, intensity, normalization_isppa, alpha_np, c
    ):
        # c is in cm/s

        field_isppa = np.max(intensity)
        intensity = intensity / field_isppa

        # toss intensities below 5% of Isppa
        intensity[intensity < 0.05] = 0

        # now zero out values near the transducer face b/c they violated the farfield assumption in field
        coords = self.coords.flatten()
        intensity[np.isclose(coords[:, 2], 0, atol=0.001)] = 0

        # normalize
        intensity = intensity * normalization_isppa

        # convert intensities from Watts to cgs units
        intensity = intensity * 10000000

        # Calculate force from F = (2*alpha*I)/c
        body_forces = (2 * alpha_np * intensity) / c
        point_loads = body_forces * self.get_element_volume()

        if self.symmetry == "q":
            # if the load is on the symmetry axis (x = y = 0), then divide by 4; if not, check if it is on a symmetry face (x = 0 || y = 0), then divide by 2. '^' is the XOR operator
            idxq = np.isclose(coords[:, 0], 0, atol=1e-4) & np.isclose(
                coords[:, 1], 0, atol=1e-4
            )
            point_loads[idxq] = point_loads[idxq] / 4
            idxh = np.isclose(coords[:, 0], 0, atol=1e-4) ^ np.isclose(
                coords[:, 1], 0, atol=1e-4
            )
            point_loads[idxh] = point_loads[idxh] / 2
        elif self.symmetry == "hy":
            # if the load is on the symmetry face (y=0), then divide by 2
            idxh = np.isclose(coords[:, 1], 0, atol=1e-4)
            point_loads[idxh] = point_loads[idxh] / 2
        elif self.symmetry == "hx":
            # if the load is on the symmetry face (x=0), then divide by 2
            idxh = np.isclose(coords[:, 0], 0, atol=1e-4)
            point_loads[idxh] = point_loads[idxh] / 2

        return point_loads

    def add_field_arf_load(self, field_load_file, normalization_isppa, load_curve_id):
        mat = loadmat(field_load_file)
        c = (
            mat["FIELD_PARAMS"]["soundSpeed"][0, 0][0][0] * 100
        )  # convert from m/s to cm/s
        alpha_db = mat["FIELD_PARAMS"]["alpha"][0, 0][0][0]
        frequency = mat["FIELD_PARAMS"]["Frequency"][0, 0][0][0]
        alpha_np = alpha_db * frequency / 8.616

        node_ids, intensity = self.interpolate_field_to_dyna_intensities(
            field_load_file
        )
        point_loads = self.calculate_point_loads_from_field_intensities(
            intensity, normalization_isppa, alpha_np, c
        )

        dof = 3
        coord_sys_id = 0
        load_string = ""
        for nid, load in zip(node_ids, point_loads):
            if load > 0:
                load_string += f"{nid},{dof},{load_curve_id},{format_dyna_number(-load)},{coord_sys_id}\n"

        self.load_card_string += (
            "*LOAD_NODE_POINT\n"
            "$ Load curve generated from: {field_load_file}\n"
            "$ Normalization ISPPA = {norm_isppa} W/cm^2\n"
            "$ Frequency = {frequency} MHz\n"
            "$ Alpha = {alpha_np} Np, {alpha_db} dB/cm/MHz\n"
            "$ Element Volume = {elem_vol} cm^3\n"
            "$ Intensity Threshold = 5%\n"
            "$ nid, dof, lcid, force, cid\n"
            "{load_string}"
            "*END\n"
        ).format(
            field_load_file=str(field_load_file),
            norm_isppa=format_dyna_number(normalization_isppa),
            frequency=format_dyna_number(frequency),
            alpha_np=format_dyna_number(alpha_np),
            alpha_db=format_dyna_number(alpha_db),
            elem_vol=format_dyna_number(self.get_element_volume()),
            load_string=load_string,
        )
