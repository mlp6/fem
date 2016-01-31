"""test_GenMesh.py

Mark Palmeri
mlp6@duke.edu
2016-01-30
"""

xyz = (0, 2, 3, 5, 6, 8)
numElem = (2, 2, 2)
pos = [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0], [6.0, 7.0, 8.0]]


def test_calc_node_pos():
    """calculate unique x, y, z positions for the mesh
    """
    from GenMesh import calc_node_pos
    assert calc_node_pos(xyz, numElem) == pos


def test_check_x0_y0():
    from GenMesh import check_x0_y0
    assert check_x0_y0(pos) != 1

    pos2 = pos
    pos2[1][1] = 0.0
    assert check_x0_y0(pos2) == 0
