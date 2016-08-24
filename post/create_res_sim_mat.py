"""
:mod:`create_res_sim_mat` -- create res_sim.mat from disp.dat

.. module:: create_res_sim_mat
   :synopsis: create res_sim.mat from disp.dat
   :license: Apache v2.0, see LICENSE for details
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

    return 0


def run(dynadeck, disp_comp=2, disp_scale=-1e4, ressim="res_sim.mat", nodedyn="nodes.dyn", dispout="disp.dat.xz", legacynodes=False):
    """

    :param dynadeck: main dyna input deck
    :param disp_comp=2: component of displacement to extract
    :param disp_scale=-1e4: displacement scaling
    :param ressim: default = "res_sim.mat"
    :param nodedyn: default = "nodes.dyn"
    :param dispout: default = "disp.dat.xz"
    :return: 0
    """
    from fem.mesh import fem_mesh

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    image_plane = extract_image_plane(snic, axes, ele_pos=0.0)

    header = read_header(dispout)
    dt = extract_dt(dynadeck)
    t = [float(x)*dt for x in range(0, header['num_timesteps'])]

    arfidata = extract_arfi_data(dispout, header, image_plane, disp_comp, disp_scale, legacynodes)

    save_res_mat(ressim, arfidata, axes, t)

    return 0


def extract_arfi_data(dispout, header, image_plane, disp_comp=2, disp_scale=-1e4, legacynodes=False):
    """ extract ARFI data from disp.dat

    :param dispout: name of disp.dat file
    :param header: num_nodes, num_dims, num_timesteps
    :param image_plane: matrix of image plane node IDs spatially sorted
    :param disp_comp: displacement component index to extract (0, 1, 2 [default, z])
    :param legacynodes: Boolean flag to use legacy disp.dat format with node
                        IDs repeated every timestep (default = False)
    :returns: arfidata matrix

    """
    import numpy as np
    import struct

    word_size = 4
    header_bytes = 3*word_size
    first_timestep_words = header['num_nodes']*header['num_dims']
    first_timestep_bytes = header['num_nodes']*header['num_dims']*word_size
    timestep_bytes = header['num_nodes']*(header['num_dims']-1)*word_size

    if dispout.endswith('.xz'):
        import lzma
        fid = lzma.open(dispout, 'rb')
    else:
        fid = open(dispout, 'rb')

    trange = [x for x in range(1, header['num_timesteps']+1)]

    # pre-allocate arfidata ndarray
    if image_plane.ndim == 2:
        arfidata = np.zeros((image_plane.shape[1], image_plane.shape[0],
                             len(trange)), dtype=np.float32)
    elif image_plane.ndim == 3:
        arfidata = np.zeros((image_plane.shape[2], image_plane.shape[1],
                             image_plane.shape[0], len(trange)), dtype=np.float32)
    else:
        print("image_plane has an unaccounted for number of dimensions")

    print(('Time step:'), end=' ')
    for t in trange:
        # extract the disp values for the appropriate time step
        if (t == 1) or legacynodes:
            print(('%i' % t), end=' ', flush=True)
            fmt = 'f'*int(first_timestep_words)
            fid.seek(header_bytes + first_timestep_bytes*(t-1), 0)
            disp_slice = np.asarray(struct.unpack(fmt,
                                    fid.read(first_timestep_bytes)), int)
            disp_slice = np.reshape(disp_slice, (header['num_nodes'],
                                    header['num_dims']), order='F')
            # extract the nodcount()e IDs on the image plane and save
            nodeidlist = disp_slice[:, 0].squeeze()
            zdisp = np.zeros((nodeidlist.max()+1, 1))
            # disp_comp + 1 to take into account node IDs in first timestep
            zdisp = create_zdisp(nodeidlist, disp_slice[:, (disp_comp+1)].squeeze(), zdisp)

        # node IDs are _not_ saved after the first timestep in latest disp.dat
        # files (flagged by legacynodes boolean)
        else:
            print(('%i' % t), end=' ', flush=True)
            fmt = 'f'*int(timestep_bytes/word_size)
            fid.seek(header_bytes + first_timestep_bytes +
                     timestep_bytes*(t-2), 0)
            disp_slice = struct.unpack(fmt, fid.read(timestep_bytes))
            disp_slice = np.reshape(disp_slice, (header['num_nodes'],
                                                 (header['num_dims']-1)),
                                    order='F')
            zdisp = create_zdisp(nodeidlist, disp_slice[:, disp_comp].squeeze(), zdisp)

        if arfidata.ndim == 3:
            for (i, j), nodeid in np.ndenumerate(image_plane):
                arfidata[j, i, t-1] = disp_scale*zdisp[nodeid]
        elif arfidata.ndim == 4:
            for (k, i, j), nodeid in np.ndenumerate(image_plane):
                arfidata[j, i, k, t-1] = disp_scale*zdisp[nodeid]
        else:
            print("arfidata has an unaccounted for number of dimensions")


    print('done!')
    fid.close()

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
    image_plane = np.squeeze(snic[ele0, :, :]).astype(int)

    return image_plane


def save_res_mat(resfile, arfidata, axes, t, axis_scale=(-10, 10, -10)):
    """ save res_sim.mat file using variables scanner-generated data

    data are saved as float32 to save space

    :param resfile: res_sim.mat filename
    :param arfidata: arfidata matrix (3D or 4D (added elev dim, axes[0]))
    :param axes: ele, lat, axial (mesh units)
    :param t: time
    :param axis_scale: scale sign and magnitude of axes [default: [-10, 10, -10]]
    :returns: 0

    """
    from scipy.io import savemat

    # scale axes
    if arfidata.ndim == 4:
        elev = axis_scale[0]*axes[0]
    lat = axis_scale[1]*axes[1]
    axial = axis_scale[2]*axes[2]
    if axis_scale[2] < 1:
        axial = axial[::-1]

    if resfile.endswith('.h5'):
        import h5py
        r = h5py.File(resfile, 'w')
        r.create_dataset(data=arfidata, name="arfidata",
                         compression="gzip", compression_opts=9)
        r.create_dataset(data=lat, name="lat",
                         compression="gzip", compression_opts=9)
        r.create_dataset(data=axial, name="axial",
                         compression="gzip", compression_opts=9)
        if arfidata.ndim == 4:
            r.create_dataset(data=elev, name="elev",
                             compression="gzip", compression_opts=9)
    elif resfile.endwith('.mat'):
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
        print("resfile filetype not recognized")

    return 0


def read_header(dispout):
    """ Read header (first 3 words) from disp.dat

    :param dispout: disp.dat filename
    :returns: header (num_nodes, num_dims, num_timesteps)

    """
    import struct

    word_size = 4  # bytes
    if dispout.endswith('.xz'):
        import lzma
        d = lzma.open(dispout, 'rb')
    else:
        d = open(dispout, 'rb')
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


if __name__ == "__main__":
    main()
