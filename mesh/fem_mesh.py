"""
fem_mesh.py

Generic functions for all meshing functions

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


def check_version():
    """check at least python2.7

    Needed for argparse compatibility

    """
    from sys import version_info, exit

    if version_info[:2] < (2, 7):
        exit("ERROR: Requires Python >= 2.7")


def strip_comments(nodefile):
    """strip comments
    string comment lines starting with $

    :param nodefile: keyword filename
    """
    from os import system
    nodefile_nocmt = '%s.tmp' % nodefile
    system("egrep -v '(^\*|^\$)' %s > %s" % (nodefile, nodefile_nocmt))

    return nodefile_nocmt


def count_header_comment_skips(nodefile):
    """count file head comments lines

    count the number of file head comments lines to skip before the first
    keyword (line starting with *)

    :param nodefile: node keyword filename

    """
    import re
    node = re.compile('\*')
    count = 1
    with open(nodefile) as f:
        for line in f:
            if node.match(line):
                return count
            else:
                count = count + 1


def rm_tmp_file(nodefile_nocmt):
    from os import remove
    try:
        remove(nodefile_nocmt)
    except OSError as e:
        print(('ERROR: %s - %s.' % (e.argsfilename, e.argsstrerror)))


def extractPlane(snic, axes, plane):
    """extract plane node IDs

    Extract the node IDs on a specified plane from a sorted node ID &
    coordinate 3D array.

    :param snic: sorted node IDs & coordinates array
    :param axes: list of unique coordinates in the x, y, and z dimensions
    :param plane: list
            index - index of the plane to extract (x=0, y=1, z=2)
            coord - coordinate of the plane to extract (must exist in axes
                    list)
    :returns: planeNodeIDs (spatially-sorted 2D node IDs on specified plane)
    :example: planeNodeIDs = extractPlane(snic,axes,(0,-0.1))
    """
    from sys import exit

    print(snic.shape)
    plane_axis_index = axes[plane[0]] == plane[1]
    print(plane_axis_index)
    if plane[0] == 0:
        planeNodeIDs = snic['id'][:, :, plane_axis_index]
    elif plane[0] == 1:
        planeNodeIDs = snic['id'][:, plane_axis_index, :]
    elif plane[0] == 2:
        planeNodeIDs = snic['id'][plane_axis_index, :, :]
    else:
        exit("ERROR: Specified plane index to extract does not exist")

    planeNodeIDs = planeNodeIDs.squeeze()
    return planeNodeIDs


def SortNodeIDs(nic, sort=False):
    """spatially sort node IDs into 3D matrix

    :param nic: nodeIDcoords (n matrix [# nodes x 4, dtype = i4,f4,f4,f4])
    :param sort: False (assume node ordering); True (spatially sort)
    :returns: [SortedNodeIDs - n matrix (x,y,z), axes]
    """
    from sys import exit
    from numpy import unique

    axes = [unique(nic['x']), unique(nic['y']), unique(nic['z'])]

    # test to make sure that we have the right dimension (and that precision
    # issues aren't adding extra unique values)
    if len(nic) != (axes[0].size * axes[1].size * axes[2].size):
        exit('ERROR: Dimension mismatch - possible precision error '
             'when sorting nodes (?)')

    # sort the nodes by x, y, then z columns
    if sort:
        I = nic.argsort(order=('x', 'y', 'z'))
        snic = nic[I]
        snic = snic.reshape((axes[0].size, axes[1].size, axes[2].size))
    else:
        snic = nic.reshape((axes[0].size, axes[1].size, axes[2].size))

    return [snic, axes]


def SortElems(elems, axes):
    """spatially sort node IDs into 3D matrix

    :param elems: element definitions, as read from elems.dyn
    :param axes: lists of x, y, z axis positions
    :returns: sorted_elems
    """

    sorted_elems = elems.reshape((axes[0].size-1,
                                  axes[1].size-1,
                                  axes[2].size-1))

    return sorted_elems


def load_nodeIDs_coords(nodefile="nodes.dyn"):
    """load in node IDs and coordinates

    Exclude '*' keyword lines

    :param nodefile: node filename (nodes.dyn)
    :returns: nodeIDcoords (numpy array)
    """
    from numpy import loadtxt
    header_comment_skips = count_header_comment_skips(nodefile)
    nodeIDcoords = loadtxt(nodefile,
                           delimiter=',',
                           comments='*',
                           skiprows=header_comment_skips,
                           dtype=[('id', 'i4'), ('x', 'f4'), ('y', 'f4'),
                                  ('z', 'f4')])
    return nodeIDcoords


def load_elems(elefile="elems.dyn"):
    """

    :param elefile: elems.dyn
    :return: elems
    """
    from numpy import loadtxt
    header_comment_skips = count_header_comment_skips(elefile)
    elems = loadtxt(elefile,
                    delimiter=',',
                    comments='*',
                    skiprows=header_comment_skips,
                    dtype=[('id', 'i4'), ('pid', 'i4'), ('n1', 'i4'),
                           ('n2', 'i4'), ('n3', 'i4'), ('n4', 'i4'),
                           ('n5', 'i4'), ('n6', 'i4'), ('n7', 'i4'),
                           ('n8', 'i4')])

    return elems