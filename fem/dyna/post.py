import struct

import logging

import pathlib
import os

import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    args = parse_args()
    extract_and_save_arfidata(
        args.sim_path,
        output_filename=args.output_filename,
        disp_direction=args.disp_direction,
        disp_scale=args.disp_scale,
    )


def parse_args():
    import argparse as ap

    par = ap.ArgumentParser(
        description="Generate res_sim.mat from disp.dat",
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    par.add_argument(
        "--sim_path",
        help="Path to simulation directory (where Master.dyn and simulation results are saved). Default is current folder since this function is usually run from command line within the simulation results directory.",
        default="./",
        type=str,
    )
    par.add_argument(
        "--output_filename",
        help="Output FEM data file name (recommended to keep as default unless good reason)",
        default="res_sim.mat",
        type=str,
    )
    par.add_argument(
        "--disp_direction",
        help="Direction to extract FEM displacement. Options: axial, lat, ele",
        default="axial",
        type=str,
    )
    par.add_argument(
        "--disp_scale",
        help="Scaling factor to apply to FEM displacements. Default value of -1e4 converts the FEM displacements from negative centimeters to positive microns before saving.",
        default="-1e4",
        type=float,
    )

    args = par.parse_args()

    return args


def load_arfidata(res_sim_file):
    """
    Load arfidata whether it was saved with matlab v7.3 or not

    Args:
        res_sim_file (str): Path to res_sim file

    """
    try:
        from scipy.io import loadmat

        mat = loadmat(res_sim_file)
        arfidata = mat["arfidata"]
        axial = mat["axial"]
        lat = mat["lat"]
        ele = mat["ele"]
        t = mat["t"]

    except NotImplementedError:
        import h5py

        with h5py.File(res_sim_file, "r") as f:
            arfidata = f["arfidata"][:]
            axial = f["axial"][:]
            lat = f["lat"][:]
            ele = f["ele"][:]
            t = f["t"][:]

        # h5py reads in opposite ordering that loadmat does
        arfidata = np.transpose(arfidata, (3, 2, 1, 0))

    # Make all coordinate vectors 1D arrays
    axial = np.reshape(axial, (-1,))
    lat = np.reshape(lat, (-1,))
    ele = np.reshape(ele, (-1,))
    t = np.reshape(t, (-1,))

    return arfidata, axial, lat, ele, t


def extract_and_save_arfidata(
    sim_base_path,
    disp_direction="axial",
    disp_scale=-1e4,
    output_filename="res_sim.mat",
):
    # Get all necessary file paths for the rest of the function
    file_paths = get_file_paths(sim_base_path)

    # Read mesh size values from node_set.dyn if it exists or nodes.dyn if it doesn't
    if file_paths["node_set"] is not None:
        mesh_size = extract_mesh_size(file_paths["node_set"])
    else:
        mesh_size = extract_mesh_size(file_paths["nodes"])

    # Extract arfidata from disp.dat binary file
    arfidata = extract_arfidata(
        file_paths["dispout"],
        mesh_size["nz"],
        mesh_size["nx"],
        mesh_size["ny"],
        disp_direction=disp_direction,
        disp_scale=disp_scale,
    )

    # Number of time points and delta t
    nt = arfidata.shape[3]
    dt = extract_dt(file_paths["master"])

    # Construct coordinate axes based on convention
    axial = np.abs(
        10 * np.linspace(mesh_size["zmax"], mesh_size["zmin"], mesh_size["nz"])
    )
    ele = 10 * np.linspace(mesh_size["xmin"], mesh_size["xmax"], mesh_size["nx"])
    lat = 10 * np.linspace(mesh_size["ymin"], mesh_size["ymax"], mesh_size["ny"])
    t = np.linspace(0, nt * dt, nt)

    # Round unncessary precision
    axial = np.round(axial, 2)
    ele = np.round(ele, 2)
    lat = np.round(lat, 2)

    # Construct kwargs dict and save
    resfile = file_paths["dispout"].parent.joinpath(output_filename)
    kwargs = {
        "resfile": resfile,
        "arfidata": arfidata,
        "axial": axial,
        "lat": lat,
        "ele": ele,
        "t": t,
    }

    output_switch = {".h5": saveh5, ".mat": savemat, ".pvd": savepvd}

    try:
        filetype = os.path.splitext(resfile)[-1]
        output_switch[filetype](**kwargs)
    except ValueError:
        raise ValueError("Cannot save 2D PVD timeseries data.")
    except KeyError:
        raise KeyError("resfile filetype not recognized")


def extract_arfidata(dispout, nax, nele, nlat, disp_direction="axial", disp_scale=1e-4):
    disp_comp = {
        "ele": 0,
        "lat": 1,
        "axial": 2,
    }.get(disp_direction)

    header = read_header(dispout)
    nt = header["num_timesteps"]
    nnodes = header["num_nodes"]
    ndims = header["num_dims"]

    word_size = 4
    header_bytes = 3 * word_size
    first_timestep_words = nnodes * ndims
    first_timestep_bytes = nnodes * ndims * word_size
    timestep_bytes = nnodes * (ndims - 1) * word_size

    # Preallocate arfidata (ax, lat, ele, time)
    arfidata = np.zeros((nax, nlat, nele, nt))

    with open_dispout(dispout) as fid:
        for idx_t in range(nt):
            # First displacement slice also has nodes so there are some off-by-one index differences between parsing the first and remaining time steps from disp.dat binary
            if idx_t == 0:
                # Read first displacement slice from binary file
                fmt = "f" * int(first_timestep_words)
                fid.seek(header_bytes, 0)
                disp_slice = struct.unpack(fmt, fid.read(first_timestep_bytes))

                # Reshape from 1d array (w,) to 2d array (nnodes, ndims)
                disp_slice = np.reshape(disp_slice, (nnodes, ndims), order="F")

                # Extract displacements from disp_comp dimension (x, y, or z displacements) and reshape into (nax, nlat, nele)
                arfidata[:, :, :, idx_t] = disp_scale * disp_slice[
                    :, disp_comp + 1
                ].reshape(nax, nlat, nele)
            else:
                # Read remaining displacement slices from binary file
                fmt = "f" * int(timestep_bytes / word_size)
                fid.seek(
                    header_bytes + first_timestep_bytes + timestep_bytes * (idx_t - 1),
                    0,
                )
                disp_slice = struct.unpack(fmt, fid.read(timestep_bytes))

                # Reshape from 1d array (w,) to 2d array (nnodes, ndims)
                disp_slice = np.reshape(disp_slice, (nnodes, ndims - 1), order="F")

                # Extract displacements from disp_comp dimension (x, y, or z displacements) and reshape into (nax, nlat, nele)
                arfidata[:, :, :, idx_t] = disp_scale * disp_slice[
                    :, disp_comp
                ].reshape(nax, nlat, nele)

    # Corrects the z axis (axial) displacements to follow convention
    arfidata = np.flipud(arfidata)

    # # Transpose to match convention (ax, lat, ele, t)
    # arfidata = np.transpose(arfidata, (0, 2, 1, 3))

    return arfidata


def extract_mesh_size(node_file_path):
    """
    Extracts mesh size (n elements, min coordinate, max coordinate, delta between coordinates) from either a nodes.dyn or node_set.dyn file.

    Args:
        node_file_path (str, pathlib.Path): Path to node.dyn or node_set.dyn file

    Returns:
        dict of str: int or float: Mesh values dictionary
    """
    values = {}
    for pattern in ["$ nx=", "$ ny=", "$ nz="]:
        with open(node_file_path, "r") as file:
            for line in file:
                if line.startswith(pattern):
                    parts = line[2:].split(", ")
                    for part in parts:
                        k, v = part.split("=")
                        if any(substring in k for substring in ["min", "max", "d"]):
                            values[k] = float(v)
                        else:
                            values[k] = int(v)
    return values


def extract_dt(dyn_file):
    """
    Extract time step (dt) from dyna input deck (assume comma-delimited)

    Args:
      dyn_file (str): input.dyn filename

    Raises:
      FileNotFoundError

    Returns:
      dt (float): timestep interval

    """
    found_database = False
    try:
        with open(dyn_file, "r") as d:
            for dyn_line in d:
                if found_database:
                    line_items = dyn_line.split(",")
                    # make sure we're not dealing with a comment
                    if "$" in line_items[0]:
                        continue
                    else:
                        dt = float(line_items[0])
                        break
                elif "*DATABASE_NODOUT" in dyn_line:
                    found_database = True
    except FileNotFoundError:
        raise FileNotFoundError

    return dt


def get_file_paths(sim_path):
    """
    This function gets the file paths necessary for post-processing dyna simulations

    Args:
        sim_path (str, pathlib.Path): Path to simulation directory (where Master.dyn and simulation results are saved)

    Returns:
        dict of str: pathlib.Path: File paths for nodes.dyn, node_set.dyn, Master.dyn, and disp.dat files
    """
    # Make sure path is a Pathlib Path object and an absolute path
    sim_path = pathlib.Path(sim_path)
    sim_path = sim_path.resolve()

    # Get base path of simulations
    sim_base_path = sim_path.parents[1]

    node_set_path = sim_base_path.joinpath("node_set.dyn")
    master_path = sim_path.joinpath("Master.dyn")
    dispout_path = sim_path.joinpath("disp.dat")

    file_paths = dict(
        sim=sim_path,
        base=sim_base_path,
        nodes=sim_base_path.joinpath("nodes.dyn"),
        node_set=node_set_path if node_set_path.is_file() else False,
        master=master_path if master_path.is_file() else False,
        dispout=dispout_path if dispout_path.is_file() else False,
    )
    return file_paths


def open_dispout(dispout):
    """
    Open dispout file for reading, potentially using lzma

    Args:
        dispout (pathlib / str): dispout file

    Raises:
        FileNotFoundError: disp.dat[.xz] file cannot be found
        ImportError: LZMA package not available

    Returns:
        dispout (obj): open file object

    """
    try:
        import lzma
    except ImportError:
        raise ImportError(
            "LZMA module not available (maybe xz-devel needs to be installed)."
        )
    from pathlib import Path

    dispout = Path(dispout)

    if dispout.name.endswith(".xz"):
        try:
            dispout = lzma.open(dispout, "rb")
        except FileNotFoundError:
            raise FileNotFoundError
    else:
        try:
            dispout = open(dispout, "rb")
        except FileNotFoundError:
            raise FileNotFoundError

    return dispout


def read_header(dispout, word_size_bytes: int = 4):
    """
    Read header (first 3 words) from dispout

    Args:
      dispout: disp.dat filename
      word_size_bytes (int): 4

    Returns:
      header (dict): keys: num_nodes, num_dims, num_timesteps

    """

    with open_dispout(dispout) as d:
        num_nodes = struct.unpack("f", d.read(word_size_bytes))
        num_dims = struct.unpack("f", d.read(word_size_bytes))
        num_timesteps = struct.unpack("f", d.read(word_size_bytes))

    header = {
        "num_nodes": int(num_nodes[0]),
        "num_dims": int(num_dims[0]),
        "num_timesteps": int(num_timesteps[0]),
    }

    return header


def saveh5(**kwargs):
    """
    Save HDF5 file with gzip compression.

    Args:
        arfidata (float): 4D arfidata matrix
        axial (float): depth axis vector [mm]
        lat (float): lateral axis vector [mm]
        ele (float): elevation axis vector [mm]
        t (float): time vector (s)
        resfile (str): 'res_sim.pvd'

    """
    import h5py

    compression = {"shuffle": True, "compression": "gzip", "compression_opts": 4}

    with h5py.File(kwargs["resfile"], "w") as r:
        r.create_dataset(data=kwargs["arfidata"], name="arfidata", **compression)
        r.create_dataset(data=kwargs["lat"], name="lat", **compression)
        r.create_dataset(data=kwargs["axial"], name="axial", **compression)
        if kwargs["arfidata"].ndim == 4:
            r.create_dataset(data=kwargs["ele"], name="ele", **compression)
        r.create_dataset(data=kwargs["t"], name="t", **compression)


def savemat(**kwargs):
    """
    Save Matlab v5 file.

    Args:
        arfidata (float): 4D arfidata matrix
        axial (float): depth axis vector [mm]
        lat (float): lateral axis vector [mm]
        ele (float): elevation axis vector [mm]
        t (float): time vector (s)
        resfile (str): 'res_sim.pvd'

    Raises:
        TypeError: arfidata >4 GB

    """
    from scipy.io import savemat as save_mat

    if kwargs["arfidata"].nbytes > 4e9:
        raise TypeError("arfidata >4 GB, cannot be saved as MATLAB v5")

    resfile = kwargs["resfile"]
    kwargs.pop("resfile")

    save_mat(resfile, kwargs, do_compression=True)


def savepvd(ts_start=0, part=0, **kwargs):
    """
    Save Paraview PVD rectilinear (VTR) time series data.

    Paraview data formats: https://www.paraview.org/Wiki/ParaView/Data_formats

    Args:
        ts_start (int): override starting timestep index from 0 to this value
        arfidata (float): 4D arfidata matrix
        axial (float): depth axis vector [mm]
        lat (float): lateral axis vector [mm]
        ele (float): elevation axis vector [mm]
        t (float): time vector (s)
        resfile (str): 'res_sim.pvd'

    Raises:
        ValueError: Not saving 3D time series data.
        FileExistsError: PVD file directory cannot be created.
    """
    import os
    from pathlib import Path

    import numpy as np
    from pyevtk.hl import gridToVTK

    if kwargs["arfidata"].ndim != 4:
        raise ValueError("Trying to save timeseries VTR data not supported.")

    resfile = Path(kwargs["resfile"])
    resfileprefix = resfile.with_suffix("")

    with open(resfile, "w") as pvd:
        pvd.write('<?xml version="1.0"?>\n')
        pvd.write(
            '<VTKFile type="Collection" version="0.1" '
            'byte_order="LittleEndian" '
            'compressor="vtkZLibDataCompressor">\n'
        )
        pvd.write("    <Collection>\n")

        veldata_calc = np.diff(np.asfortranarray(kwargs["arfidata"]), axis=3, prepend=0)

        num_timesteps = len(kwargs["t"]) - 1
        for ts, time in enumerate(kwargs["t"]):
            arfidata = np.asfortranarray(
                np.squeeze(kwargs["arfidata"][:, :, :, ts])
            ).transpose()

            veldata = np.asfortranarray(
                np.squeeze(veldata_calc[:, :, :, ts])
            ).transpose()

            timestep = ts_start + ts
            vtrfilename = Path(f"{resfileprefix}_T{ts:04d}.vtr")

            logger.info(f"Writing {vtrfilename.name}. [{ts}/{num_timesteps}]")

            pvd.write(
                f'        <DataSet timestep="{timestep}" group="" part="{part}" file="{vtrfilename.name}"/>\n'
            )

            gridToVTK(
                str(vtrfilename.with_suffix("")),
                kwargs["ele"].ravel(),
                kwargs["lat"].ravel(),
                kwargs["axial"].ravel(),
                pointData={"arfidata": arfidata, "veldata": veldata},
            )
        pvd.write("    </Collection>\n")
        pvd.write("</VTKFile>\n")


if __name__ == "__main__":
    main()
