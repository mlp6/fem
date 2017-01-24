'''
TopLoad.py - Generate compression conditions for the top surface of the
specified mesh.  Search through the provided node file, extract the top layer of
nodes and write out point loads for each matching node. Nodes are written in
spatially-sorted order.

Copyright 2015-2017 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License.  You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.
'''

__author__ = "Mark Palmeri "
__email__ = "mlp6@duke.edu"
__license__ = "Apache v2.0"


def main():
    """way too complicated for now
    """

    opts = read_cli()
    generate_loads(loadtype=opts.loadtype, amplitude=opts.amplitude, lcid=opts.lcid, nodefile=opts.nodefile,
                   top_face=(0, 0, 0, 0, 0, 1))

def generate_loads(loadtype='disp', amplitude=-1.0, loadfile='top_load.dyn', nodefile='nodes.dyn',
                   top_face =(0, 0, 0, 0, 0, 1), lcid=1):
    """ apply loads to

    :param loadtype: 'disp', 'vel', 'accel', 'force'
    :param direction: 0 - x, 1 - y, 2 - z
    :param amplitude: scalar of load type
    :param loadfile: written loadfile name
    :param nodefile: 'nodes.dyn'
    :param top_face: [0, 0, 0, 0, 0, 1]
    :param lcid: load curve ID
    :return:
    """

    (direction, planeNodeIDs) = extract_top_plane_nodes(nodefile=nodefile, top_face=top_face)
    writeNodeLoads(loadfile, planeNodeIDs, loadtype, direction, amplitude, lcid)


def extract_top_plane_nodes(nodefile, top_face):
    """

    :param nodefile:
    :param top_face:
    :return: direction, planeNodeIDs
    """
    import numpy as np
    from fem.mesh import fem_mesh

    top_face = np.array(top_face)

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    # extract spatially-sorted node IDs on a the top z plane
    axis = int(np.floor(np.divide(top_face.nonzero(),2)))
    if np.mod(top_face.nonzero(), 2) == 1:
        plane = (axis, axes[axis].max())
    else:
        plane = (axis, axes[axis].min())

    planeNodeIDs = fem_mesh.extractPlane(snic, axes, plane)
    direction = axis+1

    return (direction, planeNodeIDs)


def writeNodeLoads(loadfile, planeNodeIDs, loadtype, direction, amplitude, lcid):
    """write load keyword file

    :param loadfile: load filename
    :param planeNodeIDS: array of node IDs
    :param loadtype [str]: disp, vel, accel, force
    :param direction: 1, 2, 3
    :param amplitude:
    :param lcid: LCID
    :returns: None
    """
    import sys

    LOADFILE = open(loadfile, 'w')

    if loadtype == 'disp' or loadtype == 'vel' or loadtype == 'accel':
        LOADFILE.write("*BOUNDARY_PRESCRIBED_MOTION_NODE\n")
    elif loadtype == 'force':
        LOADFILE.write("*LOAD_NODE_POINT\n")
    else:
        sys.exit('ERROR: Invalid loadtype specified (can only be disp, '
                 'force, vel or accel)')

    if loadtype == 'disp':
        dofs =  '%i,2,%i,%f' % (direction, lcid, amplitude)
    elif loadtype == 'vel':
        dofs =  '%i,0,%i,%f' % (direction, lcid, amplitude)
    elif loadtype == 'accel':
        dofs = '%i,1,%i,%f' % (direction, lcid, amplitude)
    elif loadtype == 'force':
        dofs = '%i,%i,%f' % (direction, lcid, amplitude)

    for i in planeNodeIDs:
        for j in i:
            LOADFILE.write("%i,%s\n" % (j, dofs))

    LOADFILE.write("*END\n")
    LOADFILE.close()


def read_cli():
    """read CLI args
    """
    import argparse as argp

    par = argp.ArgumentParser(description="Generate loading conditions for the top surface of the specified mesh.",
                              formatter_class=argp.ArgumentDefaultsHelpFormatter)
    par.add_argument("--loadfile",
                     help="compression load defintion output file",
                     default="topload.dyn")
    par.add_argument("--nodefile",
                     help="node definition input file",
                     default="nodes.dyn")
    par.add_argument("--loadtype",
                     help="apply nodal prescribed displacements (disp), point "
                     "loads (force), velocity (vel) or acceleration (accel)",
                     default="disp")
    par.add_argument("--amplitude",
                     help="amplitude of load",
                     type=float,
                     default=1.0)
    par.add_argument("--top_face",
                     help="array with 1 indicating top face (xmin, xmax, ymin, ymax, zmin, zmax)",
                     nargs="+",
                     type=int,
                     default=(0, 0, 0, 0, 0, 1)
                     )
    par.add_argument("--lcid",
                     help="Load Curve ID to apply to these loads",
                     default=1)

    opts = par.parse_args()

    return opts

if __name__ == "__main__":
    main()
