"""test_bc.py
"""

import sys

import os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


def test_assign_pml_elems():
    from bc import assign_pml_elems

    # TODO: this can probably be put into some sort of pytest fixture
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

    pml_elems = ((3, 0), (0, 1), (2, 3))

    sorted_pml_elems = assign_pml_elems(sorted_elems, pml_elems)

    # check the xmin face
    assert sorted_pml_elems[sorted_pml_elems['id']==1]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==2]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==3]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==4]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==91]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==92]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==93]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==94]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==901]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==902]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==903]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==904]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==991]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==992]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==993]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==994]['pid'] == 2

    # check the ymax face
    assert sorted_pml_elems[sorted_pml_elems['id']==95]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==100]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==995]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==1000]['pid'] == 2

    # check the zmax face
    assert sorted_pml_elems[sorted_pml_elems['id']==910]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==810]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==710]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==610]['pid'] == 1

    # check the zmin face
    assert sorted_pml_elems[sorted_pml_elems['id']==10]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==110]['pid'] == 2
    assert sorted_pml_elems[sorted_pml_elems['id']==210]['pid'] == 1

