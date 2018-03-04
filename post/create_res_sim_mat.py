"""
:mod:`create_res_sim_mat` -- create res_sim.mat from disp.dat

.. module:: create_res_sim_mat
   :synopsis: create res_sim.mat from disp.dat
   :copyright: Copyright 2016 Mark Palmeri

.. moduleauthor:: Mark Palmeri <mlp6@duke.edu>
"""


def main():
    args = read_cli()
    if args.legacynodes:
        legacynodes = True
    else:
        legacynodes = False

    run(args.dynadeck, args.ressim, args.nodedyn, args.dispout, legacynodes)


def run(dynadeck, disp_comp=2, disp_scale=-1e4, ressim="res_sim.mat",
        nodedyn="nodes.dyn", dispout="disp.dat", legacynodes=False):
    """

    :param dynadeck: main dyna input deck
    :param disp_comp=2: component of displacement to extract
    :param disp_scale=-1e4: displacement scaling
    :param ressim: default = "res_sim.mat"
    :param nodedyn: default = "nodes.dyn"
    :param dispout: default = "disp.dat"
    :return: 0
    """
    from fem.mesh import fem_mesh

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    image_plane = extract_image_plane(snic, axes, ele_pos=0.0)

    header = read_header(dispout)
    t = gen_t(extract_dt(dynadeck), header['num_timesteps'])

    arfidata = extract_arfi_data(dispout, header, image_plane, disp_comp,
                                 disp_scale, legacynodes)

    save_res_mat(ressim, arfidata, axes, t)

    return 0


def extract_arfi_data(dispout, header, image_plane, disp_comp=2,
                      disp_scale=-1e4, legacynodes=False):
    """ extract ARFI data from disp.dat

    :param dispout: name of disp.dat file
    :param header: num_nodes, num_dims, num_timesteps
    :param image_plane: matrix of image plane node IDs spatially sorted
    :param disp_comp: disp component index to extract (0, 1, 2 [default, z])
    :param legacynodes: Boolean flag to use legacy disp.dat format with node
                        IDs repeated every timestep (default = False)
    :returns: arfidata matrix

    """
    import numpy as np
    import struct
    from warnings import warn

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
                warn("unexpected number of dimensions for arfidata")

        print('\nDone extracting all timesteps.')

    # ndenumerate only iterates in C-ordering, so flip this over to match the
    # F-ordering of Matlab-like code
    arfidata = np.flipud(arfidata)

    return arfidata


def create_zdisp(nodeidlist, disp_slice_z_only, zdisp):
    """create zdisp array from squeezed disp_slice at appropriate index

    :param nodeidlist: first column of disp_slice with node IDs in row order
    :param disp_slice_z_only: squeezed disp_slice of just zisp
    :returns: zdisp -- array of z-disp in rows corresponding to node ID
                       (for fast read access)

    """
    import numpy as np

    for i, nodeid in np.ndenumerate(nodeidlist):
        zdisp[nodeid] = disp_slice_z_only[i]

    return zdisp


def read_cli():
    """ read in command line arguments
    """

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

    :param snic: sorted node IDs and coordinates
    :param axes: spatial axes
    :param ele_pos: elevation position for plane of interest
    :returns: image_plane (node IDs)

    """
    import numpy as np

    ele0 = np.min(np.where(axes[0] >= ele_pos))
    image_plane = np.squeeze(snic['id'][ele0, :, :]).astype(int)

    return image_plane


def save_res_mat(resfile, arfidata, axes, t, axis_scale=(-10, 10, -10)):
    """ save res_sim.mat file using variables scanner-generated data

    data are saved as float32 to save space

    :param resfile: res_sim.mat filename
    :param arfidata: arfidata matrix (3D or 4D (added elev dim, axes[0]))
    :param axes: ele, lat, axial (mesh units)
    :param t: time
    :param axis_scale: scale axes sign & mag [default: [-10, 10, -10]]
    :returns: 0

    """
    from scipy.io import savemat
    from warnings import warn

    if arfidata.nbytes > 4e9 and resfile.endswith('.mat'):
        warn('arfidata exceeds 4 GB and cannot be written to MATLAB v5\n'
             'format; you must use HDF5 (*.h5)')

    # scale axes
    if arfidata.ndim == 4:
        elev = axis_scale[0] * axes[0]
    lat = axis_scale[1] * axes[1]
    axial = axis_scale[2] * axes[2]
    if axis_scale[2] < 1:
        axial = axial[::-1]

    print('Saving data to: {}'.format(resfile), flush=True)
    if resfile.endswith('.h5'):
        import h5py
        r = h5py.File(resfile, 'w')
        r.create_dataset(data=arfidata,
                         name="arfidata",
                         compression="gzip",
                         compression_opts=9)
        r.create_dataset(data=lat,
                         name="lat",
                         compression="gzip",
                         compression_opts=9)
        r.create_dataset(data=axial,
                         name="axial",
                         compression="gzip",
                         compression_opts=9)
        if arfidata.ndim == 4:
            r.create_dataset(data=elev,
                             name="elev",
                             compression="gzip",
                             compression_opts=9)
        r.create_dataset(data=t,
                         name="t",
                         compression="gzip",
                         compression_opts=9)
    elif resfile.endswith('.mat'):
        if arfidata.ndim == 4:
            savemat(resfile,
                    {'arfidata': arfidata,
                     'lat': lat,
                     'axial': axial,
                     'elev': elev,
                     't': t},
                    do_compression=True
                    )
        else:
            savemat(resfile,
                    {'arfidata': arfidata,
                     'lat': lat,
                     'axial': axial,
                     't': t},
                    do_compression=True
                    )
    else:
        warn("resfile filetype not recognized")

    return 0


def read_header(dispout):
    """ Read header (first 3 words) from disp.dat

    :param dispout: disp.dat filename
    :returns: header (num_nodes, num_dims, num_timesteps)

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
    """ extract time step (dt) from dyna input deck

    assumes that input deck is comma-delimited

    :param dyn_file: input.dyn filename
    :returns: dt from input.dyn binary data save parameter

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

    :param dispout: (str) dispout filename (disp.dat)
    :return: dispout file object
    """
    if dispout.endswith('.xz'):
        import lzma
        dispout = lzma.open(dispout, 'rb')
    else:
        dispout = open(dispout, 'rb')

    return dispout


def preallocate_arfidata(image_plane, num_timesteps):
    """ pre-allocate arfidata array

    :param image_plane: sorted node IDs on selected imaging plane
    :param num_timesteps: number of timesteps to extract
    :return: arfidata
    """
    import numpy as np
    from warnings import warn

    num_timesteps = int(num_timesteps)

    if image_plane.ndim == 2:
        arfidata = np.zeros((image_plane.shape[1], image_plane.shape[0],
                             num_timesteps), dtype=np.float32)
    elif image_plane.ndim == 3:
        arfidata = np.zeros((image_plane.shape[2], image_plane.shape[1],
                             image_plane.shape[0], num_timesteps),
                            dtype=np.float32)
    else:
        warn("unexpected number of dimensions in sorted nodes")

    return arfidata


def gen_t(dt, num_timesteps):
    """generate time vector, starting at 0

    :param dt: time between saved timesteps
    :param num_timesteps: number of total timesteps
    :return: t
    """
    t = [float(x) * dt for x in range(0, num_timesteps)]

    return t


def extract3Darfidata(dynadeck=None, disp_comp=2, disp_scale=-1e4,
                      ressim="res_sim.h5", nodedyn="nodes.dyn",
                      dispout="disp.dat.xz"):
    """extract 3D volume of specified displacement component

    :param dynadeck: LS-DYNA3D input deck (used to get dt)
    :param disp_comp=2: displacement component to extract (0, 1, 2)
    :param disp_scale=1e4: displacement scaling factor (cm -> um)
    :param ressim="res_sim.h5": output file name (can be MAT or HDF5)
    :param nodedyn="nodes.dyn": node input file
    :param dispout="disp.dat.xz": binary displacement data
    """

    from fem.mesh import fem_mesh
    import fem.post.create_res_sim_mat as create_res_sim
    import numpy as np

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    header = create_res_sim.read_header(dispout)
    dt = create_res_sim.extract_dt(dynadeck)
    t = [float(x) * dt for x in range(0, header['num_timesteps'])]

    arfidata = create_res_sim.extract_arfi_data(dispout, header, snic['id'],
                                                disp_comp, disp_scale,
                                                legacynodes=False)

    create_res_sim.save_res_mat(ressim, arfidata, axes, t)


if __name__ == "__main__":
    main()
