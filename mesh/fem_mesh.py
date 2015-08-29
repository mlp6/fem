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
from __future__ import absolute_import
from __future__ import print_function


def check_version():
    """
    Check that at least python2.7 is being used for argparse compatibility
    """
    import sys

    if sys.version_info[:2] < (2, 7):
        sys.exit("ERROR: Requires Python >= 2.7")


def strip_comments(nodefile):
    import os
    nodefile_nocmt = '%s.tmp' % nodefile
    os.system("egrep -v '(^\*|^\$)' %s > %s" % (nodefile, nodefile_nocmt))
    return nodefile_nocmt


def count_header_comment_skips(nodefile):
    """
    count the number of file head comments lines to skip before the first
    keyword (line starting with *)
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
    import os
    try:
        os.remove(nodefile_nocmt)
    except OSError as e:
        print(('ERROR: %s - %s.' % (e.argsfilename, e.argsstrerror)))

def extractPlane(snic, axes, plane):
    '''
    Extract the node IDs on a specified plane from a sorted node ID &
    coordinate 3D array.

    INPUTS:
        snic - sorted node IDs & coordinates array
        axes - list of unique coordinates in the x, y, and z dimensions
        plane - list:
            index - index of the plane to extract (x=0, y=1, z=2)
            coord - coordinate of the plane to extract (must exist in axes
                    list)

    OUPUTS:
        planeNodeIDs - spatially-sorted 2D node IDs on the specified plane

    EXAMPLE: planeNodeIDs = extractPlane(snic,axes,(0,-0.1))
    '''
    import sys

    if plane[0] == 0:
        planeNodeIDs = snic[axes[plane[0]] == plane[1], :, :]
    elif plane[0] == 1:
        planeNodeIDs = snic[:, axes[plane[0]] == plane[1], :]
    elif plane[0] == 2:
        planeNodeIDs = snic[:, :, axes[plane[0]] == plane[1]]
    else:
        sys.exit("ERROR: Specified plane index to extract does not exist")

    planeNodeIDs = planeNodeIDs.squeeze()
    return planeNodeIDs


def SortNodeIDs(nic):
    '''
    Sort the node IDs by spatial coordinates into a 3D matrix and return the
    corresponding axes

    INPUTS:
        nic - nodeIDcoords (n matrix [# nodes x 4, dtype = i4,f4,f4,f4])

    OUTPUTS:
        SortedNodeIDs - n matrix (x,y,z)
        x - array
        y - array
        z - array
    '''

    import sys
    import numpy as n

    axes = [n.unique(nic['x']), n.unique(nic['y']), n.unique(nic['z'])]

    # test to make sure that we have the right dimension (and that precision
    # issues aren't adding extra unique values)
    if len(nic) != (axes[0].size * axes[1].size * axes[2].size):
        sys.exit('ERROR: Dimension mismatch - possible precision error '
                 'when sorting nodes (?)')

    # sort the nodes by x, y, then z columns
    I = nic.argsort(order=('x', 'y', 'z'))
    snic = nic[I]
    snic = snic.reshape((axes[0].size, axes[1].size, axes[2].size))

    return [snic, axes]


def load_nodeIDs_coords(nodefile):
    """
    load in node IDs and coordinates, excluding '*' keyword lines
    """
    import fem_mesh
    import numpy as n
    header_comment_skips = fem_mesh.count_header_comment_skips(nodefile)
    nodeIDcoords = n.loadtxt(nodefile,
                             delimiter=',',
                             comments='*',
                             skiprows=header_comment_skips,
                             dtype=[('id', 'i4'), ('x', 'f4'), ('y', 'f4'),
                                    ('z', 'f4')])
    return nodeIDcoords