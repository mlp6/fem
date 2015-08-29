""" create_res_sim_mat.py

create res_sim.mat file from disp.dat

EXAMPLE: python create_res_sim_mat.py --dynadeck desk.dyn

Copyright 2015 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import
from __future__ import print_function
from six.moves import range


def main():
    import fem_mesh

    args = read_cli()

    if args.legacynodes:
        legacynodes = True
    else:
        legacynodes = False

    node_id_coords = fem_mesh.load_nodeIDs_coords(args.nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    image_plane = extract_image_plane(snic, axes, ele_pos=0.0)

    header = read_header(args.dispout)
    dt = extract_dt(args.dynadeck)
    t = [float(x)*dt for x in range(0, header['num_timesteps'])]

    arfidata = extract_arfi_data(args.dispout, header, image_plane,
                                 legacynodes)

    save_res_mat(args.ressim, arfidata, axes, t)


def extract_arfi_data(dispout, header, image_plane, legacynodes):
    """ extract ARFI data from disp.dat

    :param dispout: name of disp.dat file
    :param header: num_nodes, num_dims, num_timesteps
    :param image_plane: matrix of image plane node IDs spatially sorted
    :param legacynodes: boolean flag to use legacy disp.dat format with node
                        IDs repeated every timestep
    :return arfidata:  arfidata matrix
    """
    import numpy as np
    import struct

    word_size = 4
    header_bytes = 3*word_size
    first_timestep_words = header['num_nodes']*header['num_dims']
    first_timestep_bytes = header['num_nodes']*header['num_dims']*word_size
    timestep_bytes = header['num_nodes']*(header['num_dims']-1)*word_size

    fid = open(dispout, 'rb')
    trange = [x for x in range(1, header['num_timesteps']+1)]
    arfidata = np.zeros((image_plane.shape[1], image_plane.shape[0],
                         len(trange)), dtype=np.float32)
    print(('Working on time step: '), end=' ')
    for t in trange:
        # extract the disp values for the appropriate time step
        if (t == 1) or legacynodes:
            print(('%i ' % t), end=' ')
            fmt = 'f'*int(first_timestep_words)
            fid.seek(header_bytes + first_timestep_bytes*(t-1), 0)
            disp_slice = np.asarray(struct.unpack(fmt,
                                    fid.read(first_timestep_bytes)), int)
            disp_slice = np.reshape(disp_slice, (header['num_nodes'],
                                    header['num_dims']), order='F')
            # extract the nodcount()e IDs on the image plane and save
            nodeidlist = disp_slice[:, 0].squeeze()
            # just work with the z-disp (index 3)
            zdisp = np.zeros((nodeidlist.max()+1, 1))
            zdisp = create_zdisp(nodeidlist, disp_slice[:, 3].squeeze(), zdisp)

        # node IDs are _not_ saved after the first timestep in latest disp.dat
        # files (flagged by legacynodes boolean)
        else:
            print(('%i ' % t), end=' ')
            fmt = 'f'*int(timestep_bytes/word_size)
            fid.seek(header_bytes + first_timestep_bytes +
                     timestep_bytes*(t-2), 0)
            disp_slice = struct.unpack(fmt, fid.read(timestep_bytes))
            disp_slice = np.reshape(disp_slice, (header['num_nodes'],
                                                 (header['num_dims']-1)),
                                    order='F')
            # just work with the z-disp (index 2)
            zdisp = create_zdisp(nodeidlist, disp_slice[:, 2].squeeze(), zdisp)

        # TODO: this should have some optimized form (list comprehension?)
        for (i, j), nodeid in np.ndenumerate(image_plane):
            arfidata[j, i, t-1] = -1e4*zdisp[nodeid]

    print('done!')
    fid.close()

    return arfidata


def create_zdisp(nodeidlist, disp_slice_z_only, zdisp):
    """create zdisp array from squeezed disp_slice at appropriate index

    :param nodeidlist: first column of disp_slice with node IDs in row order
    :param disp_slice_z_only: squeezed disp_slice of just zisp
    :return zdisp: array of z-disp in rows corresponding to node ID
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
    """ Extract a 2D matrix of the imaging plane node IDs based on the
    elevation position (mesh coordinates)
    """
    import numpy as np

    ele0 = min(np.where(axes[0] >= ele_pos))
    image_plane = np.squeeze(snic[ele0, :, :])

    return image_plane


def save_res_mat(resfile, arfidata, axes, t):
    """ save res_sim.mat file using variables scanner-generated data
    data are saved as float32 to save space
    :param resfile: res_sim.mat filename
    :param arfidata: arfidata matrix
    :param axes: ele, lat, axial (mesh units)
    :param t: time
    :return void:
    """
    from scipy.io import savemat

    # convert to mm
    axial = -10*axes[2]
    axial = axial[::-1]
    lat = 10*axes[1]

    savemat(resfile,
            {'arfidata': arfidata,
             'lat': lat,
             'axial': axial,
             't': t},
            do_compression=True
            )


def read_header(dispout):
    """ Read header (first 3 words) from disp.dat

    :param dispout: disp.dat filename
    :return header: num_nodes, num_dims, num_timesteps
    """
    import struct

    word_size = 4  # bytes
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
    :return dt: dt from input.dyn binary data save parameter
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
            elif '*DATABASE_BINARY_D3PLOT' in dyn_line:
                found_database = True

    return dt

if __name__ == "__main__":
    main()
