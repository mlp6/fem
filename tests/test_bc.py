"""test_bc.py
"""

import sys
import os
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


def test_write_pml_elems(tmpdir, sorted_elems):
    from bc import write_pml_elems

    f = tmpdir.join("elems_pml.dyn")
    write_pml_elems(sorted_elems, pmlfile=f.strpath)
    lines = f.readlines()
    assert lines[0][0] == "$"
    assert lines[1] == "*ELEMENT_SOLID\n"
    assert lines[2] == "1,1,1,2,13,12,122,123,134,133\n"
    assert lines[-2] == "1000,1,1198,1199,1210,1209,1319,1320,1331,1330\n"
    assert lines[-1] == "*END\n"


def test_assign_node_constraints(nodeIDcoords):
    from fem_mesh import SortNodeIDs
    from bc import assign_node_constraints
    [snic, axes] = SortNodeIDs(nodeIDcoords, sort=False)
    node_constraints = (('1,1,1,1,1,1', '2,2,2,2,2,2'),
                        ('3,3,3,3,3,3', '4,4,4,4,4,4'),
                        ('5,5,5,5,5,5', '6,6,6,6,6,6'))
    bcdict = assign_node_constraints(snic, axes, node_constraints)

    assert bcdict[1] == '5,5,5,5,5,5'


def test_assign_pml_elems(sorted_elems):
    from bc import assign_pml_elems

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


def test_write_bc(tmpdir):
    from bc import write_bc
    bcdict = {1: '1,1,1,0,0,0', 2: '0,1,0,0,1,0'}
    f = tmpdir.join("bc.dyn")
    write_bc(bcdict, bcfile=f.strpath)
    lines = f.readlines()
    assert lines[1] == "*BOUNDARY_SPC_NODE\n"
    assert lines[2] == "1,1,1,1,0,0,0\n"
    assert lines[3] == "2,0,1,0,0,1,0\n"
    assert lines[-1] == "*END\n"

    return 0
