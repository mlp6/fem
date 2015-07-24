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


def main():
    import os
    import sys
    import fem_mesh

    args = read_cli()

    if args.legacynodes:
        legacynodes = 'true'
    else:
        legacynodes = 'false'

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(args.nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    image_plane = extractImagePlane(snic, axes, elePosition=0.0)

    header = readHeader(args.dispout)
    TimeStep = extractTimeStep(args.nodedyn);
    t = [x*TimeStep for x in range(0, (header['NUM_TIMESTEPS']-1))]

    arfidata = extractARFIdata(args.dispout, header, image_plane, args.legacynodes)

    save_res_mat(args.ressim, arfidata, lat, axial, t)


def extractARFIdata(dispout, header, image_plane, legacynodes):
    """ extract ARFI data from disp.dat

    :param dispout: name of disp.dat file
    :param header: NUM_NODES, NUM_DIMS, NUM_TIMESTEPS
    :param image_plane: matrix of image plane node IDs spatially sorted
    :param legacynodes: boolean flag to use legacy disp.dat format with node IDs repeated every timestep
    :return arfidata:  arfidata matrix
    """
    import numpy as np
    import struct

    headerBytes = 3*4;

    fid = open(dispout, 'rb')
    # TODO: convert this loop from Matlab -> Python
    for t in range(1, header['NUM_TIMESTEPS']+1):
        print t
        # extract the disp values for the appropriate time step
        if t == 1 or legacynodes:
            # TODO: confirm that unpack_from does the same as a seek and starts from the beginning each time!
            # TODO: generate 'f' based on the length of data to be read in
            disp_slice = struct.unpack_from('f', fid.read(header['NUM_NODES']*header['NUM_DIMS']),
                                            headerBytes + header['NUM_NODES']*header['NUM_DIMS']*(t-1)*4)
            disp_slice = np.reshape(disp_slice, header['NUM_NODES'], header['NUM_DIMS'])
            # extract the node IDs on the image plane and save
            nodeIDlist = disp_slice[:, 1]
            # reduce disp_slice to just have the x,y,z disps
            disp_slice = disp_slice[:, 2:4]
        # node IDs are _not_ saved after the first timestep in latest disp.dat files
        # (flagged by legacynodes boolean)
        else:
            disp_slice = struct.unpack_from('f', fid.read(header['NUM_NODES']*(header['NUM_DIMS']-1)),
                                                 headerBytes + header['NUM_NODES']*header['NUM_DIMS']*4 +
                                                 header['NUM_NODES']*(header['NUM_DIMS']-1)*4*(t-2))
            disp_slice = np.reshape(disp_slice, header['NUM_NODES'], (header['NUM_DIMS']-1))

        temp[nodeIDlist] = disp_slice[:, 3]
        temp2 = -temp(image_plane)*1e4
        temp2 = shiftdim(temp2, 1)
        arfidata[:, :, t] = temp2
        clear temp temp2

    fid.close()

    return arfidata


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
                     help="read in disp.dat file that has node IDs saved for each timestep",
                     action="store_true")
    args = par.parse_args()

    return args


def extractImagePlane(snic, axes, elePosition):
    """ Extract a 2D matrix of the imaging plane node IDs based on the elevation position (mesh coordinates)
    """
    import numpy as np

    ele0 = min(np.where(axes[0] >= elePosition))
    image_plane = snic[ele0, :, :]

    return image_plane


def save_res_mat(resfile, arfidata, lat, axial, t):
    """ save res_sim.mat file using variables scanner-generated data
    data are saved as float32 to save space
    """
    from scipy.io import savemat
    import numpy as np

    # convert to mm and transpose
    axial = -10*np.transpose(axial)
    lat = 10*np.transpose(lat)

    savemat(resfile,
            {'arfidata': arfidata,
             'lat': lat,
             'axial': axial,
             't': t},
            do_compression = True
    )


def readHeader(dispout):
    """ Read header (first 3 words) from disp.dat

    :param dispout: disp.dat filename
    :return header: NUM_NODES, NUM_DIMS, NUM_TIMESTEPS
    """
    import struct

    word_size = 4  # bytes
    d = open(dispout, 'rb')
    NUM_NODES = struct.unpack('f', d.read(word_size))
    NUM_DIMS = struct.unpack('f', d.read(word_size))
    NUM_TIMESTEPS = struct.unpack('f', d.read(word_size))
    header = {'NUM_NODES': NUM_NODES,
              'NUM_DIMS': NUM_DIMS,
              'NUM_TIMESTEPS': NUM_TIMESTEPS}
    return header

def extractTimeStep(dyn_file):
    """ extract time step (dt) from dyna input deck
    assumes that input deck is comma-delimited

    :param dyn_file: input.dyn filename
    :return TimeStep: dt from input.dyn binary data save parameter
    """
    foundDatabase = False;
    with open(dyn_file, 'r') as d:
        for dyn_line in d:
            if foundDatabase:
                line_items = dyn_line.split(',')
                # make sure we're not dealing with a comment
                if '$' in line_items[0]:
                    continue
                else:
                    TimeStep = float(line_items[0])
                    return TimeStep
            elif '*DATABASE_BINARY_D3PLOT' in dyn_line:
                foundDatabase = True


if __name__ == "__main__":
    main()
