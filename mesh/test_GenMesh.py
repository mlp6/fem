"""test_GenMesh.py

Mark Palmeri
mlp6@duke.edu
2016-01-30
"""


def test_calc_node_pos():
    from GenMesh import calc_node_pos
    assert calc_node_pos((0, 2, 3, 5, 6, 8), (2, 2, 2)) == \
        [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0], [6.0, 7.0, 8.0]]
