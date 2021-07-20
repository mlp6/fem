"""create_res_sim.py - extract data for display in different formats from disp.dat binary"""
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """ """
    args = __read_cli()
    if args.legacynodes:
        legacynodes = True
    else:
        legacynodes = False

    run(args.dynadeck, args.ressim, args.nodedyn, args.dispout, legacynodes)


def run(dynadeck, disp_comp=2, disp_scale=-1e4, ressim="res_sim.mat",
        nodedyn="nodes.dyn", dispout="disp.dat", legacynodes=False, plane_pos:float=0.0, plane_orientation:int=0):
    """helper function to run high-level, 2D plane extraction

    look at using extract3Darfidata to get full, 3D datasets exported (e.g., to view in Paraview)

    Args:
        dynadeck (str): main dyna input deck
        disp_comp (int): component of displacement to extract
        disp_scale (float): displacement scaling
        ressim (str): result filename to write
        nodedyn (str): node defintion input filename
        dispout (str): binary displacement input filename
        legacynodes (Boolean): node IDs written with each timestep in dispout
        plane_pos (float): position of the plane to extract (in the specified plane_orientation)
        plane_orientation (int): orientation plane to extract from (0 = elev, 1 = lateral, 2 = axial)
    
    """
    import sys
    from pathlib import Path

    meshPath = Path(__file__).parents[1] / "mesh"
    sys.path.insert(0, str(meshPath))

    import fem_mesh

    try:
        plane_pos
    except NameError:
        plane_pos = ele_pos
        
        
    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)
    
    image_plane = extract_image_plane(snic, axes, plane_pos, plane_orientation)

    header = read_header(dispout)
    t = __gen_t(extract_dt(dynadeck), header['num_timesteps'])
    arfidata = extract_arfi_data(dispout, header, image_plane, disp_comp,
                                 disp_scale, legacynodes)
    axis_scale=(-10, 10, -10)
    save_res_sim(ressim, arfidata, axes, t, axis_scale, plane_pos, plane_orientation)
    
    return 0


def extract_arfi_data(dispout, header, image_plane, disp_comp=2,
                      disp_scale=-1e4, legacynodes=False):
    """extract ARFI data from disp.dat

    Args:
        dispout (str): name of disp.dat file
        header (dict): num_nodes, num_dims, num_timesteps
        image_plane (ndarray): matrix of image plane node IDs spatially sorted
        disp_comp (int): disp component index to extract (0, 1, 2 [default, z])
        legacynodes (Boolean): node IDs repeated every timestep
        disp_scale (float):  cm -> um

    Returns:
        arfidata (ndarray):

    Raises:
        IndexError: unexpected arfidata dimensions

    """
    import numpy as np
    import struct

    word_size = 4
    header_bytes = 3 * word_size
    first_timestep_words = header['num_nodes'] * header['num_dims']
    first_timestep_bytes = header['num_nodes'] * header['num_dims'] * word_size
    timestep_bytes = header['num_nodes'] * (header['num_dims'] - 1) * word_size

    with open_dispout(dispout) as fid:
        trange = [x for x in range(1, header['num_timesteps'] + 1)]

        arfidata = __preallocate_arfidata(image_plane, header['num_timesteps'])

        logger.info(f"Total Timesteps: {header['num_timesteps']}")
        logger.info('Extracting timestep:')

        for t in trange:
            logger.info(f'{t}')
            if (t == 1) or legacynodes:
                fmt = 'f' * int(first_timestep_words)
                fid.seek(header_bytes + first_timestep_bytes * (t - 1), 0)
                disp_slice = np.asarray(struct.unpack(fmt,
                                        fid.read(first_timestep_bytes)), int)
                disp_slice = np.reshape(disp_slice, (header['num_nodes'],
                                        header['num_dims']), order='F')
                # extract the nodcount()e IDs on the image plane and save
                nodeidlist = disp_slice[:, 0].squeeze()
                zdisp = np.zeros((nodeidlist.max() + 1, 1))
                # disp_comp + 1 to take into account node IDs in first timestep
                zdisp = create_zdisp(nodeidlist,
                                     disp_slice[:, (disp_comp + 1)].squeeze(),
                                     zdisp)

            # node IDs not saved after the first timestep in latest disp.dat
            # files (flagged by legacynodes boolean)
            else:
                fmt = 'f' * int(timestep_bytes / word_size)
                fid.seek(header_bytes + first_timestep_bytes +
                         timestep_bytes * (t - 2), 0)
                disp_slice = struct.unpack(fmt, fid.read(timestep_bytes))
                disp_slice = np.reshape(disp_slice, (header['num_nodes'],
                                                     (header['num_dims'] - 1)),
                                        order='F')
                zdisp = create_zdisp(nodeidlist,
                                     disp_slice[:, disp_comp].squeeze(),
                                     zdisp)

            if arfidata.ndim == 3:
                for (i, j), nodeid in np.ndenumerate(image_plane):
                    arfidata[j, i, t - 1] = disp_scale * zdisp[nodeid]
            elif arfidata.ndim == 4:
                for (k, i, j), nodeid in np.ndenumerate(image_plane):
                    arfidata[j, i, k, t - 1] = disp_scale * zdisp[nodeid]
            else:
                raise IndexError("Unexpected # of dimensions for arfidata.")

        logger.info('\nDone extracting all timesteps.')

    # ndenumerate only iterates in C-ordering, so flip this over to match the
    # F-ordering of Matlab-like code
    arfidata = np.flipud(arfidata)

    return arfidata


def create_zdisp(nodeidlist, disp_slice_z_only, zdisp):
    """create zdisp array from squeezed disp_slice at appropriate index

    Args:
        nodeidlist: first column of disp_slice with node IDs in row order
        disp_slice_z_only: squeezed disp_slice of just zdisp
        zdisp:

    Returns:
        zdisp (ndarray): rows corresponding to node ID

    """
    import numpy as np

    for i, nodeid in np.ndenumerate(nodeidlist):
        zdisp[nodeid] = disp_slice_z_only[i]

    return zdisp


def __read_cli():
    """read in command line arguments"""

    import argparse as ap

    par = ap.ArgumentParser(description="Generate res_sim.mat from disp.dat",
                            formatter_class=ap.ArgumentDefaultsHelpFormatter)
    par.add_argument("--dispout",
                     help="name of the binary displacement output file",
                     default="disp.dat")
    par.add_argument("--ressim",
                     help="name of the matlab output file",
                     default="res_sim.mat")
    par.add_argument("--nodedyn",
                     help="ls-dyna node definition file",
                     default="nodes.dyn")
    par.add_argument("--dynadeck",
                     help="ls-dyna input deck",
                     default="dynadeck.dyn")
    par.add_argument("--legacynodes",
                     help="read in disp.dat file that has node IDs saved for"
                          "each timestep",
                     action="store_true")
    par.add_argument("--plane_pos", 
                     help = "pos of plane wanted to extract",
                     default = 0.0)
    par.add_argument("--plane_orientation",
                     help = "what orientation plane to use 0 = elev, 1 = lat, 2 = ax",
                     default = 0)
    args = par.parse_args()

    return args


def extract_image_plane(snic, axes, plane_pos:float=0.0, direction:int=0):
    """extract 2D imaging plane node IDs

    Extract a 2D matrix of the imaging plane node IDs based on the
    elevation position (mesh coordinates).

    Args:
        snic: sorted node IDs and coordinates
        axes: spatial axes
        plane_pos (float): position of the plane to extract (in the specified plane_orientation)
        plane_orientation (int): orientation plane to extract from (0 = elev, 1 = lateral, 2 = axial)

    Raises:
        TypeError: deprecated ele_pos passed as keyword argument
        ValueError: invalid direction axis specified

    Returns:
        image_plane (node IDs)

    """
    import numpy as np

    if direction < 0 or direction > 2:
        logging.error('Not a valid axes direction.')
        raise ValueError('Invalid direction axis specified.')

    plane = np.min(np.where(axes[direction]>=plane_pos))

    if direction == 0:
        image_plane = np.squeeze(snic['id'][plane,:,:]).astype(int)
    elif direction == 1:
        image_plane = np.squeeze(snic['id'][:,plane,:]).astype(int)
    elif direction == 2:
        image_plane = np.squeeze(snic['id'][:,:,plane]).astype(int)
    
    return image_plane


def save_res_sim(resfile, arfidata, axes, t, axis_scale=(-10, 10, -10), plane_pos=None, plane_orientation=None):
    """Save res_sim.[mat,h5,pvd] file with arfidata and relevant axes.

    Data are saved as float32 (single) to save space.

    Args:
        resfile (str): res_sim.[mat,h5,pvd] filename
        arfidata (ndarray): arfidata (3D or 4D (added elev dim, axes[0]))
        axes (ndarrays tuple): ele, lat, axial (mesh units)
        t (ndarray): time
        axis_scale (floats tuple): scale axes sign & mag
        plane_pos (float): position of the plane to extract (in the specified plane_orientation)
        plane_orientation (int): orientation plane to extract from (0 = elev, 1 = lateral, 2 = axial)

    Raises:
        ValueError: Cannot save 2D PVD timeseries data.
        KeyError: Trying to save unknown output type.

    """
    import os
    # scale axes
    if arfidata.ndim == 4:
        elev = axis_scale[0] * axes[0]
    lat = axis_scale[1] * axes[1]
    axial = axis_scale[2] * axes[2]

    if plane_orientation == 0: # means an elevational plane
        lat = axis_scale[1] * axes[1]
        axial = axis_scale[2] * axes[2]
        elev = axis_scale[0] * plane_pos # pass value of what it was at
        if axis_scale[2] < 1:
            axial = axial[::-1]
    elif plane_orientation == 1: #means a lateral plane
        elev = axis_scale[0] * axes[0]
        lat = axis_scale[1] * plane_pos
        axial = axis_scale[2] * axes [2]
        if axis_scale[2]<1:
            axial = axial[::-1]
    elif plane_orientation == 2:
        elev = axis_scale[0] * axes[0]
        lat = axis_scale[1] * axes[1]
        axial = axis_scale[2] * plane_pos 
        
        
    logger.info(f'Saving data to: {resfile}')   

    kwargs = {'resfile': resfile,
              'arfidata': arfidata,
              'axial': axial,
              'lat': lat,
              'elev': elev,
              't': t}   

    output_switch = {
        '.h5': saveh5,
        '.mat': savemat,
        '.pvd': savepvd}

    try:
        filetype = os.path.splitext(resfile)[-1]
        output_switch[filetype](**kwargs)
    except ValueError:
        raise ValueError("Cannot save 2D PVD timeseries data.")
    except KeyError:
        raise KeyError("resfile filetype not recognized")


def saveh5(**kwargs):
    """Save HDF5 file with gzip compression.

    Args:
        arfidata (float): 4D arfidata matrix
        axial (float): depth axis vector [mm]
        lat (float): lateral axis vector [mm]
        elev (float): elevation axis vector [mm]
        t (float): time vector (s)
        resfile (str): 'res_sim.pvd'

    """
    import h5py

    compression = {'shuffle': True,
                   'compression': 'gzip',
                   'compression_opts': 4}

    with h5py.File(kwargs['resfile'], 'w') as r:
        r.create_dataset(data=kwargs['arfidata'],
                         name="arfidata",
                         **compression)
        r.create_dataset(data=kwargs['lat'],
                         name="lat",
                         **compression)
        r.create_dataset(data=kwargs['axial'],
                         name="axial",
                         **compression)
        if kwargs['arfidata'].ndim == 4:
            r.create_dataset(data=kwargs['elev'],
                             name="elev",
                             **compression)
        r.create_dataset(data=kwargs['t'],
                         name="t",
                         **compression)


def savemat(**kwargs):
    """Save Matlab v5 file.

    Args:
        arfidata (float): 4D arfidata matrix
        axial (float): depth axis vector [mm]
        lat (float): lateral axis vector [mm]
        elev (float): elevation axis vector [mm]
        t (float): time vector (s)
        resfile (str): 'res_sim.pvd'

    Raises:
        TypeError: arfidata >4 GB

    """
    from scipy.io import savemat as save_mat

    if kwargs['arfidata'].nbytes > 4e9:
        raise TypeError("arfidata >4 GB, cannot be saved as MATLAB v5")

    resfile = kwargs['resfile']
    kwargs.pop('resfile')

    save_mat(resfile, kwargs, do_compression=True)


def savepvd(ts_start=0, part=0, **kwargs):
    """Save Paraview PVD rectilinear (VTR) time series data.

    Paraview data formats: https://www.paraview.org/Wiki/ParaView/Data_formats

    Args:
        ts_start (int): override starting timestep index from 0 to this value
        arfidata (float): 4D arfidata matrix
        axial (float): depth axis vector [mm]
        lat (float): lateral axis vector [mm]
        elev (float): elevation axis vector [mm]
        t (float): time vector (s)
        resfile (str): 'res_sim.pvd'

    Raises:
        ValueError: Not saving 3D time series data.
        FileExistsError: PVD file directory cannot be created.
    """
    from pyevtk.hl import gridToVTK
    import os
    import numpy as np
    from pathlib import Path

    if kwargs['arfidata'].ndim != 4:
        raise ValueError("Trying to save timeseries VTR data not supported.")

    resfile = Path(kwargs['resfile'])
    resfileprefix = resfile.with_suffix('')

    with open(resfile, 'w') as pvd:

        pvd.write('<?xml version="1.0"?>\n')
        pvd.write('<VTKFile type="Collection" version="0.1" '
                  'byte_order="LittleEndian" '
                  'compressor="vtkZLibDataCompressor">\n')
        pvd.write('    <Collection>\n')

        veldata_calc = np.diff(np.asfortranarray(kwargs['arfidata']), axis=3, prepend=0)

        num_timesteps = len(kwargs['t'])-1
        for ts, time in enumerate(kwargs['t']):

            arfidata = np.asfortranarray(np.squeeze(kwargs['arfidata']
                                                    [:, :, :, ts])).transpose()

            veldata = np.asfortranarray(np.squeeze(veldata_calc[:, :, :, ts])).transpose()

            timestep = ts_start + ts
            vtrfilename = Path(f'{resfileprefix.name}_T{ts:04d}.vtr')

            logger.info(f"Writing {vtrfilename}. [{ts}/{num_timesteps}]")

            pvd.write(f'        <DataSet timestep="{timestep}" group="" part="{part}" file="{vtrfilename.name}"/>\n')

            kwargs['elev'] = np.array(kwargs['elev'])
            gridToVTK(vtrfilename.with_suffix('').name,
                      kwargs['elev'].ravel(),
                      kwargs['lat'].ravel(),
                      kwargs['axial'].ravel(),
                      pointData={'arfidata': arfidata,
                                 'veldata': veldata})
        pvd.write('    </Collection>\n')
        pvd.write('</VTKFile>\n')


def read_header(dispout, word_size_bytes: int = 4):
    """Read header (first 3 words) from dispout

    Args:
      dispout: disp.dat filename
      word_size_bytes (int): 4

    Returns:
      header (dict): keys: num_nodes, num_dims, num_timesteps

    """
    import struct

    with open_dispout(dispout) as d:
        num_nodes = struct.unpack('f', d.read(word_size_bytes))
        num_dims = struct.unpack('f', d.read(word_size_bytes))
        num_timesteps = struct.unpack('f', d.read(word_size_bytes))

    header = {'num_nodes': int(num_nodes[0]),
              'num_dims': int(num_dims[0]),
              'num_timesteps': int(num_timesteps[0])}

    return header


def extract_dt(dyn_file):
    """extract time step (dt) from dyna input deck (assume comma-delimited)

    Args:
      dyn_file (str): input.dyn filename

    Raises:
      FileNotFoundError

    Returns:
      dt (float): timestep interval

    """
    found_database = False
    try:
        with open(dyn_file, 'r') as d:
            for dyn_line in d:
                if found_database:
                    line_items = dyn_line.split(',')
                    # make sure we're not dealing with a comment
                    if '$' in line_items[0]:
                        continue
                    else:
                        dt = float(line_items[0])
                        break
                elif '*DATABASE_NODOUT' in dyn_line:
                    found_database = True
    except FileNotFoundError:
        raise FileNotFoundError

    return dt


def open_dispout(dispout):
    """open dispout file for reading, potentially using lzma

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
        raise ImportError("LZMA module not available (maybe xz-devel needs to be installed).")
    from pathlib import Path

    dispout = Path(dispout)

    if dispout.name.endswith('.xz'):
        try:
            dispout = lzma.open(dispout, 'rb')
        except FileNotFoundError:
            raise FileNotFoundError
    else:
        try:
            dispout = open(dispout, 'rb')
        except FileNotFoundError:
            raise FileNotFoundError

    return dispout


def __preallocate_arfidata(image_plane, num_timesteps: int):
    """pre-allocate arfidata array

    Args:
      image_plane: sorted node IDs on selected imaging plane
      num_timesteps (int): number of timesteps to extract

    Returns:
      arfidata (ndarray): 3D or 4D array (x, [y,], z, t)

    Raises:
        IndexError: unexpected number of sorted node dimensions

    """
    import numpy as np

    num_timesteps = int(num_timesteps)

    if image_plane.ndim == 2:
        arfidata = np.zeros((image_plane.shape[1], image_plane.shape[0],
                             num_timesteps), dtype=np.float32)
    elif image_plane.ndim == 3:
        arfidata = np.zeros((image_plane.shape[2], image_plane.shape[1],
                             image_plane.shape[0], num_timesteps),
                            dtype=np.float32)
    else:
        raise IndexError("Unexpected number of dimensions in sorted nodes.")

    return arfidata


def __gen_t(dt: float, num_timesteps: int) -> list:
    """generate time vector, starting at 0

    Args:
        dt (float): time between saved timesteps
        num_timesteps (int): number of total timesteps

    Returns:
        t (list): list of times

    """
    t = [float(x) * dt for x in range(0, num_timesteps)]

    return t


def extract3Darfidata(dynadeck="dynadeck.dyn", disp_comp=2, disp_scale=-1e4,
                      ressim="res_sim.h5", nodedyn="nodes.dyn",
                      dispout="disp.dat"):
    """Extract 3D volume of specified displacement component.

    Args:
        dynadeck (str): LS-DYNA3D input deck (used to get dt)
        disp_comp (int): displacement component to extract (0, 1, 2)
        disp_scale (float): displacement scaling factor (cm -> um)
        ressim (str): output file name [.mat, .h5, .pvd]
        nodedyn (str): node input file
        dispout (str): binary displacement data
    """
    import sys
    from pathlib import Path

    meshPath = Path(__file__).parents[1] / "mesh"
    sys.path.insert(0, str(meshPath))

    import fem_mesh

    if not ressim.endswith(('.mat', '.h5', '.pvd')):
        raise NameError('Output res_sim filename not supported')

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    header = read_header(dispout)
    dt = extract_dt(dynadeck)
    t = [float(x) * dt for x in range(0, header['num_timesteps'])]

    arfidata = extract_arfi_data(dispout, header, snic['id'],
                                 disp_comp, disp_scale, legacynodes=False)

    save_res_sim(ressim, arfidata, axes, t)


if __name__ == "__main__":
    main()
