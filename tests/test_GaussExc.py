"""test_GaussExc.py
"""

import os
import sys
import pytest
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


def test_calc_gauss_amp():
    """test node assigmnet of Gaussian amplitude
    """
    from GaussExc import calc_gauss_amp

    node_xyz = [1, 0.0, 0.0, -2.0]
    center = [0.0, 0.0, -2.0]
    sigma = [0.25, 0.25, 0.25]
    amp = 1.0

    assert calc_gauss_amp(node_xyz, center, sigma, amp) == 1.0

    node_xyz = [1, 0.25, 0.0, -2.0]

    assert round(calc_gauss_amp(node_xyz, center, sigma, amp) -
                 0.36787944117144233, 5) == 0


def test_sym_scale_amp():
    """test symmetry scaling of point load
    """
    from GaussExc import sym_scale_amp

    assert sym_scale_amp([1, 0.0, 0.0, -2.0], 8.0, 'qsym') == 2.0
    assert sym_scale_amp([1, 0.0, 0.0, -2.0], 8.0, 'hsym') == 4.0
    assert sym_scale_amp([1, 0.0, 0.0, -2.0], 8.0, 'none') == 8.0


def test_check_num_fields():
    """test that error is raised
    """
    from GaussExc import check_num_fields

    assert check_num_fields([1.0, 1.0, 2.0, 3.0]) == 0
    with pytest.raises(SyntaxError) as excinfo:
        check_num_fields([1.0, 1.0, 2.0, 3.0, 4.0])
    assert "Unexpected number of node columns" in str(excinfo.value)


"""
def test_writeNodes(tmpdir):
    from GenMesh import writeNodes

    nodefile = "nodes.dyn"
    f = tmpdir.join(nodefile)
    writeNodes(pos, f.strpath, header_comment)
    lines = f.readlines()
    assert lines[0] == header_comment+"\n"
    assert lines[1] == "*NODE\n"
    assert lines[2] == "1,0.000000,3.000000,6.000000\n"
    assert lines[-1] == "*END\n"
"""