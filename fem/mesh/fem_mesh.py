"""fem_mesh.py - ubiquitous functions for many meshing operations"""
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_version():
    """check Python version >=3.7

    Args:
        None

    Raises:
        ImportError: Python < 3.7

    Returns:
        None

    """
    from sys import version_info, exit

    if version_info[:2] < (3, 7):
        raise ImportError("Python >= 3.7 required.")


def strip_comments(nodefile):
    """string comment lines starting with $

    Args:
      nodefile: keyword filename

    Returns:
        nodefile_nocmt (str): nodefile stripped of comments

    """
    from os import system

    nodefile_nocmt = f'{nodefile}.tmp'
    system(f"egrep -v '(^\\*|^\\$)' {nodefile} > {nodefile_nocmt}")

    return nodefile_nocmt


def count_header_comment_skips(nodefile):
    """count comments lines to skip before the first keyword (*)

    Args:
      nodefile: node keyword filename

    Raises:
        FileNotFoundError: Cannot open the specified node file.

    Returns:
        count (int): number of comment lines before first keyword

    """
    import re
    node = re.compile(r'\*', re.UNICODE)
    count = 1
    try:
        with open(nodefile) as f:
            for line in f:
                if node.match(line):
                    return count
                else:
                    count = count + 1
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot open {nodefile}.")


def rm_tmp_file(nodefile_nocmt):
    """remove temporary pytest nodefile

    Args:
      nodefile_nocmt (str): pytest temporary nodefile

    Raises:
        OSError: cannot remove temporary pytest nodefile

    Returns:
        None

    """
    from os import remove

    try:
        remove(nodefile_nocmt)
    except OSError:
        raise OSError


def extractPlane(snic, axes, plane):
    """extract plane node IDs

    Extract the node IDs on a specified plane from a sorted node ID &
    coordinate 3D array.

    Args:
        snic (ndarray): sorted node IDs & coordinates array
        axes (list): list of unique coordinates in the x, y, and z dimensions
        plane (list): indices of the plane to extract (x=0, y=1, z=2)

    Raises:
        IndexError: specified plane index does not exist

    Returns:
        planeNodeIDs (spatially-sorted 2D node IDs on specified plane)

    Examples:
        planeNodeIDs = extractPlane(snic,axes,(0,-0.1))

    """
    from sys import exit
    from numpy import where

    plane_axis_index = where(axes[plane[0]] == plane[1])
    if plane[0] == 0:
        planeNodeIDs = snic['id'][plane_axis_index[0], :, :]
    elif plane[0] == 1:
        planeNodeIDs = snic['id'][:, plane_axis_index[0], :]
    elif plane[0] == 2:
        planeNodeIDs = snic['id'][:, :, plane_axis_index[0]]
    else:
        raise IndexError("Specified plane index to extract does not exist.")

    planeNodeIDs = planeNodeIDs.squeeze()
    return planeNodeIDs


def SortNodeIDs(nic, sort=False):
    """spatially sort node IDs into 3D matrix

    Args:
        nic (ndarray): nodeIDcoords [# nodes x 4, dtype = i4,f4,f4,f4]
        sort (Boolean): False (assume node ordering)
                        True (spatially sort)

    Returns:
        SortedNodeIDs (ndarray): n matrix (x,y,z), axes

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
        snic = snic.reshape((axes[0].size, axes[1].size, axes[2].size),
                            order='F')
    else:
        snic = nic.reshape((axes[0].size, axes[1].size, axes[2].size),
                           order='F')

    return [snic, axes]


def SortElems(elems, axes):
    """spatially sort node IDs into 3D matrix

    Args:
        elems (ndarray): element definitions, as read from elems.dyn
        axes (list): lists of x, y, z axis positions

    Returns:
        sorted_elems (ndarray)

    """
    sorted_elems = elems.reshape((axes[0].size - 1,
                                  axes[1].size - 1,
                                  axes[2].size - 1),
                                  order='F')

    return sorted_elems


def load_nodeIDs_coords(nodefile="nodes.dyn"):
    """load in node IDs and coordinates

    Exclude '*' keyword lines.

    Args:
        nodefile (str): 'nodes.dyn'

    Returns:
        nodeIDcoords (ndarray)

    """
    import numpy as np
    header_comment_skips = count_header_comment_skips(nodefile)
    nodeIDcoords = np.loadtxt(nodefile,
                              delimiter=',',
                              comments='*',
                              skiprows=header_comment_skips,
                              dtype=[('id', 'i4'), ('x', 'f4'), ('y', 'f4'),
                                     ('z', 'f4')])

    return nodeIDcoords


def load_elems(elefile="elems.dyn"):
    """load element definitions

    Args:
      elefile (str): 'elems.dyn'

    Returns:
      elems (ndarray)

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
