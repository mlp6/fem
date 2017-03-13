"""test_GaussExc.py
"""

import os
import sys
import pytest
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')

center = [0.0, 0.0, -2.0]
sigma = [0.25, 0.25, 0.25]
amp = 1.0


def test_calc_gauss_amp():
    """test node assigmnet of Gaussian amplitude under all symmetry conditions
    """
    from GaussExc import calc_gauss_amp

    node_xyz = [1, 0.0, 0.0, -2.0]

    assert calc_gauss_amp(node_xyz, center, sigma, amp, sym="none") == 1.0
    assert calc_gauss_amp(node_xyz, center, sigma, amp, sym="hsym") == 0.5
    assert calc_gauss_amp(node_xyz, center, sigma, amp, sym="qsym") == 0.25

    node_xyz = [1, 0.25, 0.0, -2.0]

    assert round(calc_gauss_amp(node_xyz, center, sigma, amp, sym="none") -
                 0.36787944117144233, 5) == 0
    assert round(calc_gauss_amp(node_xyz, center, sigma, amp, sym="hsym") -
                 0.36787944117144233, 5) == 0
    assert round(calc_gauss_amp(node_xyz, center, sigma, amp, sym="qsym") -
                 0.36787944117144233 / 2, 5) == 0


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


def test_read_process_nodes():
    """read_process_nodes

    This is tricky to test since it calls a lot of other functions.
    Probably need to refactor to make a more meaningful, independent test.
    """
    pass


def test_write_load_file(tmpdir):
    """write_load_file
    """
    from GaussExc import write_load_file

    f = tmpdir.join("loads.dyn")
    load_nodeID_amp = [(1, 2.0), (3, 4.0)]
    write_load_file(f.strpath, load_nodeID_amp)

    lines = f.readlines()
    assert lines[0][0] == "$"
    assert lines[1] == "*LOAD_NODE_POINT\n"
    assert lines[2] == "1,3,1,-2.0000\n"
    assert lines[3] == "3,3,1,-4.0000\n"
    assert lines[-1] == "*END\n"
