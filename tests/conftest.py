"""conftest.py
"""

import sys
import pytest
from pathlib import Path

meshPath = Path(__file__).parents[1] / "mesh"
testPath = Path(__file__).parent
sys.path.insert(0, str(meshPath))


@pytest.fixture
def nodeIDcoords():
    """create node ID and coordinate matrix from nodes.dyn

    :returns: [snic, axes]
    """
    from fem_mesh import load_nodeIDs_coords

    nodeIDcoords = load_nodeIDs_coords(testPath / "nodes.dyn")

    return nodeIDcoords


@pytest.fixture
def sorted_elems(nodeIDcoords):
    """create sorted elements numpy array from nodes.dyn & elems.dyn

    :returns: sorted_elems
    """
    from fem_mesh import load_elems
    from fem_mesh import SortElems
    from fem_mesh import SortNodeIDs
    elems = load_elems(testPath / "elems.dyn")
    [snic, axes] = SortNodeIDs(nodeIDcoords, sort=False)
    sorted_elems = SortElems(elems, axes)

    return sorted_elems


@pytest.fixture
def sorted_nodes(nodeIDcoords):
    """create sorted nodes numpy array from nodes.dyn & elems.dyn

    :returns: sorted_nodes
    """
    from fem_mesh import SortNodeIDs
    [sorted_nodes, axes] = SortNodeIDs(nodeIDcoords, sort=False)

    return sorted_nodes


@pytest.fixture
def axes(nodeIDcoords):
    """create axes numpy array from nodes.dyn & elems.dyn

    :returns: axes
    """
    from fem_mesh import SortNodeIDs
    [sorted_nodes, axes] = SortNodeIDs(nodeIDcoords, sort=False)

    return axes


@pytest.fixture
def mktmpdir(tmpdir_factory):
    """create temporary directory for unit tests in test_create_disp

    :param tmpdir_factory:
    :return: tmpdir
    """
    tmpdir = tmpdir_factory.mktemp('tmp')
    return tmpdir


@pytest.fixture
def savevtk_data():
    from scipy.io import loadmat

    d = loadmat(testPath / "savevtk_data.mat")
    savevtk_data = d['data']

    return savevtk_data
