"""Create res_sim.mat from disp.dat.
"""


def main():
    """ """
    args = read_cli()
    if args.legacynodes:
        legacynodes = True
    else:
        legacynodes = False

    run(args.dynadeck, args.ressim, args.nodedyn, args.dispout, legacynodes)


def run(dynadeck, disp_comp=2, disp_scale=-1e4, ressim="res_sim.mat",
        nodedyn="nodes.dyn", dispout="disp.dat", legacynodes=False):
    """

    Args:
        dynadeck (str): main dyna input deck
        disp_comp (int): component of displacement to extract
        disp_scale (float): displacement scaling
        ressim (str): result filename to write
        nodedyn (str): node defintion input filename
        dispout (str): binary displacement input filename
        legacynodes (Boolean): node IDs written with each timestep in dispout

    """
    from fem.mesh import fem_mesh

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    image_plane = extract_image_plane(snic, axes, ele_pos=0.0)

    header = read_header(dispout)
    t = gen_t(extract_dt(dynadeck), header['num_timesteps'])

    arfidata = extract_arfi_data(dispout, header, image_plane, disp_comp,
                                 disp_scale, legacynodes)

    save_res_sim(ressim, arfidata, axes, t)

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

        arfidata = preallocate_arfidata(image_plane, header['num_timesteps'])

        print('Total Timesteps: {}'.format(header['num_timesteps']))
        print('Extracting timestep:', end=' ')

        for t in trange:
            print(('%i' % t), end=' ', flush=True)
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

        print('\nDone extracting all timesteps.')

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


def read_cli():
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
    args = par.parse_args()

    return args


def extract_image_plane(snic, axes, ele_pos):
    """extract 2D imaging plane node IDs

    Extract a 2D matrix of the imaging plane node IDs based on the
    elevation position (mesh coordinates).

    Args:
      snic: sorted node IDs and coordinates
      axes: spatial axes
      ele_pos: elevation position for plane of interest

    Returns:
      image_plane (node IDs)

    """
    import numpy as np

    ele0 = np.min(np.where(axes[0] >= ele_pos))
    image_plane = np.squeeze(snic['id'][ele0, :, :]).astype(int)

    return image_plane


def save_res_sim(resfile, arfidata, axes, t, axis_scale=(-10, 10, -10)):
    """Save res_sim.[mat,h5,pvd] file with arfidata and relevant axes.

    Data are saved as float32 (single) to save space.

    Args:
        resfile (str): res_sim.[mat,h5,pvd] filename
        arfidata (ndarray): arfidata (3D or 4D (added elev dim, axes[0]))
        axes (ndarrays tuple): ele, lat, axial (mesh units)
        t (ndarray): time
        axis_scale (floats tuple): scale axes sign & mag

    Raises:
        KeyError: Trying to save unknown output type.

    """
    import os

    # scale axes
    if arfidata.ndim == 4:
        elev = axis_scale[0] * axes[0]
    lat = axis_scale[1] * axes[1]
    axial = axis_scale[2] * axes[2]
    if axis_scale[2] < 1:
        axial = axial[::-1]

    print('Saving data to: {}'.format(resfile), flush=True)

    kwargs = {'resfile': resfile,
              'arfidata': arfidata,
              'axial': axial,
              'lat': lat,
              't': t}
    if arfidata.ndim == 4:
        kwargs['elev'] = elev

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
    """Save HDF5 file."""
    import h5py
    r = h5py.File(kwargs['resfile'], 'w')
    r.create_dataset(data=kwargs['arfidata'],
                     name="arfidata",
                     compression="gzip",
                     compression_opts=9)
    r.create_dataset(data=kwargs['lat'],
                     name="lat",
                     compression="gzip",
                     compression_opts=9)
    r.create_dataset(data=kwargs['axial'],
                     name="axial",
                     compression="gzip",
                     compression_opts=9)
    if kwargs['arfidata'].ndim == 4:
        r.create_dataset(data=kwargs['elev'],
                         name="elev",
                         compression="gzip",
                         compression_opts=9)
    r.create_dataset(data=kwargs['t'],
                     name="t",
                     compression="gzip",
                     compression_opts=9)


def savemat(**kwargs):
    """Save Matlab v5 file.

    Raises:
        TypeError: arfidata >4 GB

    """
    from scipy.io import savemat as save_mat

    if kwargs['arfidata'].nbytes > 4e9:
        raise TypeError("arfidata >4 GB, cannot be saved as MATLAB v5")

    resfile = kwargs['resfile']
    kwargs.pop('resfile')

    save_mat(resfile, kwargs, do_compression=True)


def savepvd(**kwargs):
    """Save Paraview PVD rectilinear (VTR) time series data.

    Paraview data formats: https://www.paraview.org/Wiki/ParaView/Data_formats

    Raises:
        ValueError: Not saving 3D time series data.
        FileExistsError: PVD file directory cannot be created.

    Todo:
        Need unit test
    """
    from pyevtk.hl import gridToVTK
    import os
    import numpy as np

    if kwargs['arfidata'].ndim != 4:
        raise ValueError("Trying to save timeseries VTR data not supported.")

    resfileprefix = os.path.splitext(kwargs['resfile'])[0]
    resfilepath = '{}_pvd'.format(resfileprefix)
    try:
        os.mkdir(resfilepath)
    except FileExistsError:
        raise FileExistsError("Cannot create PVD file directory.")

    try:
        os.chdir(resfilepath)
    except FileNotFoundError:
        raise FileNotFoundError("Cannot find the PVD file directory.")

    with open(kwargs['resfile'], 'w') as pvd:

        pvd.write('<?xml version="1.0"?>\n')
        pvd.write('<VTKFile type="Collection" version="0.1" \
                  byte_order="LittleEndian" \
                  compressor="vtkZLibDataCompressor">\n')
        pvd.write('<Collection>\n')

        for ts, time in enumerate(kwargs['t']):

            arfidata = np.asfortranarray(np.squeeze(kwargs['arfidata'][:, :, :, ts])).transpose()

            vtrfilename = '{}_PVD_T{:04d}'.format(resfileprefix, ts)

            pvd.write('<DataSet timestep="{}" group="" part="0" \
                      file="{}.vtr"/>\n'.format(ts, vtrfilename))

            gridToVTK('./{}'.format(vtrfilename), kwargs['elev'].ravel(), kwargs['lat'].ravel(),
                      kwargs['axial'].ravel(), pointData={'arfidata': arfidata})
        pvd.write('</Collection>\n')
        pvd.write('</VTKFile>\n')


def read_header(dispout):
    """Read header (first 3 words) from disp.dat

    Args:
      dispout: disp.dat filename

    Returns:
      header (num_nodes, num_dims, num_timesteps)

    """
    import struct

    word_size = 4  # bytes
    d = open_dispout(dispout)
    num_nodes = struct.unpack('f', d.read(word_size))
    num_dims = struct.unpack('f', d.read(word_size))
    num_timesteps = struct.unpack('f', d.read(word_size))
    header = {'num_nodes': int(num_nodes[0]),
              'num_dims': int(num_dims[0]),
              'num_timesteps': int(num_timesteps[0])}
    return header


def extract_dt(dyn_file):
    """extract time step (dt) from dyna input deck

    assumes that input deck is comma-delimited

    Args:
      dyn_file: input.dyn filename

    Returns:
      dt from input.dyn binary data save parameter

    """
    found_database = False
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

    return dt


def open_dispout(dispout):
    """open dispout file for reading

    Args:
      dispout: str) dispout filename (disp.dat)

    Returns:
      dispout file object

    """
    if dispout.endswith('.xz'):
        import lzma
        dispout = lzma.open(dispout, 'rb')
    else:
        dispout = open(dispout, 'rb')

    return dispout


def preallocate_arfidata(image_plane, num_timesteps):
    """pre-allocate arfidata array

    Args:
      image_plane: sorted node IDs on selected imaging plane
      num_timesteps: number of timesteps to extract

    Returns:
      arfidata

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
        raise IndeError("Unexpected number of dimensions in sorted nodes.")

    return arfidata


def gen_t(dt, num_timesteps):
    """generate time vector, starting at 0

    Args:
        dt (float): time between saved timesteps
        num_timesteps (int): number of total timesteps

    Returns:
        t (list):

    """
    t = [float(x) * dt for x in range(0, num_timesteps)]

    return t


def extract3Darfidata(dynadeck=None, disp_comp=2, disp_scale=-1e4,
                      ressim="res_sim.h5", nodedyn="nodes.dyn",
                      dispout="disp.dat.xz"):
    """Extract 3D volume of specified displacement component.

    Args:
        dynadeck (str): LS-DYNA3D input deck (used to get dt)
        disp_comp (int): displacement component to extract (0, 1, 2)
        disp_scale (float): displacement scaling factor (cm -> um)
        ressim (str): output file name (can be MAT or HDF5)
        nodedyn (str): node input file
        dispout (str): binary displacement data
    """

    from fem.mesh import fem_mesh
    import numpy as np

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
