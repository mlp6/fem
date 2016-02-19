"""test_fem_mesh.py
"""

import sys

import os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


def test_loadnodeidscoords():
    """

    :return:
    """
    from fem_mesh import load_nodeIDs_coords
    nodefile = '%s/nodes.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)

    assert nodeIDcoords[0][1] == -1.0
    assert nodeIDcoords[-1][0] == 1331
    assert nodeIDcoords[-1][2] == 1.0


def test_sortnodeids():
    """

    :return:
    """
    from fem_mesh import load_nodeIDs_coords
    from fem_mesh import SortNodeIDs
    nodefile = '%s/nodes.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)
    [snic, axes] = SortNodeIDs(nodeIDcoords)

    assert axes[0][0] == -1.0
    assert axes[1][0] == 0.0
    assert axes[2][0] == -1.0
    assert axes[0][-1] == 0.0
    assert axes[1][-1] == 1.0
    assert axes[2][-1] == 0.0

    assert snic[0][0][0][0] == 1
    assert snic[0][0][0][1] == -1.0
    assert snic[0][0][0][2] == 0.0
    assert snic[0][0][0][3] == -1.0

    assert snic[-1][-1][-1][0] == 1331
    assert snic[-1][-1][-1][1] == 0.0
    assert snic[-1][-1][-1][2] == 1.0
    assert snic[-1][-1][-1][3] == 0.0
