"""test_fem_mesh.py
"""

import sys

import os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


def test_loadnodeidscoords():
    from fem_mesh import load_nodeIDs_coords
    nodefile = '%s/nodes.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)

    assert nodeIDcoords[0][1] == -1.0
    assert nodeIDcoords[-1][0] == 1331
    assert nodeIDcoords[-1][2] == 1.0


def test_loadelems():
    from fem_mesh import load_elems
    elefile = '%s/elems.dyn' % myPath
    elems = load_elems(elefile)

    assert elems[0][0] == 1
    assert elems[0][-1] == 133
    assert elems[-1][0] == 1000
    assert elems[-1][-1] == 1330


def test_sortnodeids():
    """test node ID sorting by both order and coordinate locations
    """
    from fem_mesh import load_nodeIDs_coords
    from fem_mesh import SortNodeIDs
    nodefile = '%s/nodes.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)
    [snic, axes] = SortNodeIDs(nodeIDcoords, sort=False)

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

    [snic, axes] = SortNodeIDs(nodeIDcoords, sort=True)

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


def test_SortElems():
    from fem_mesh import load_nodeIDs_coords
    from fem_mesh import load_elems
    from fem_mesh import SortNodeIDs
    from fem_mesh import SortElems

    nodefile = '%s/nodes.dyn' % myPath
    elefile = '%s/elems.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)
    [snic, axes] = SortNodeIDs(nodeIDcoords)
    elems = load_elems(elefile)
    sorted_elems = SortElems(elems, axes)

    assert sorted_elems[0][0][0][0] ==  1
    assert sorted_elems[0][0][0][2] ==  1
    assert sorted_elems[0][0][0][-1] ==  133
    assert sorted_elems[-1][-1][-1][0] == 1000
    assert sorted_elems[-1][-1][-1][2] == 1198
    assert sorted_elems[-1][-1][-1][-1] == 1330


def test_extractPlane():
    """test all that all 6 planes are extracted as expected
    """
    from fem_mesh import load_nodeIDs_coords
    from fem_mesh import SortNodeIDs
    from fem_mesh import extractPlane

    nodefile = '%s/nodes.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)
    [snic, axes] = SortNodeIDs(nodeIDcoords)

    planeNodeIDs = extractPlane(snic, axes, [0, -1.0])
    assert planeNodeIDs.shape == (11, 11)
    assert planeNodeIDs['id'][0, 0] == 1
    assert planeNodeIDs['id'][0, 10] == 111
    assert planeNodeIDs['id'][10, 0] == 1211
    assert planeNodeIDs['id'][10, 10] == 1321

    planeNodeIDs = extractPlane(snic, axes, [0, 0.0])
    assert planeNodeIDs.shape == (11, 11)
    assert planeNodeIDs['id'][0, 0] == 11
    assert planeNodeIDs['id'][0, 10] == 121
    assert planeNodeIDs['id'][10, 0] == 1221
    assert planeNodeIDs['id'][10, 10] == 1331

    planeNodeIDs = extractPlane(snic, axes, [1, 0.0])
    assert planeNodeIDs.shape == (11, 11)
    assert planeNodeIDs['id'][0, 0] == 1
    assert planeNodeIDs['id'][0, 10] == 11
    assert planeNodeIDs['id'][10, 0] == 1211
    assert planeNodeIDs['id'][10, 10] == 1221

    planeNodeIDs = extractPlane(snic, axes, [1, 1.0])
    assert planeNodeIDs.shape == (11, 11)
    assert planeNodeIDs['id'][0, 0] == 111
    assert planeNodeIDs['id'][0, 10] == 121
    assert planeNodeIDs['id'][10, 0] == 1321
    assert planeNodeIDs['id'][10, 10] == 1331

    planeNodeIDs = extractPlane(snic, axes, [2, -1.0])
    assert planeNodeIDs.shape == (11, 11)
    assert planeNodeIDs['id'][0, 0] == 1
    assert planeNodeIDs['id'][0, 10] == 11
    assert planeNodeIDs['id'][10, 0] == 111
    assert planeNodeIDs['id'][10, 10] == 121

    planeNodeIDs = extractPlane(snic, axes, [2, 0.0])
    assert planeNodeIDs.shape == (11, 11)
    assert planeNodeIDs['id'][0, 0] == 1211
    assert planeNodeIDs['id'][0, 10] == 1221
    assert planeNodeIDs['id'][10, 0] == 1321
    assert planeNodeIDs['id'][10, 10] == 1331

