import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '/../post/'))


def test_preallocate_arfidata(sorted_nodes, axes):
    from create_res_sim_mat import preallocate_arfidata

    from create_res_sim_mat import extract_image_plane
    image_plane = extract_image_plane(sorted_nodes, axes, 0.0)

    arfidata = preallocate_arfidata(image_plane, 3)

    assert arfidata.shape == (11, 11, 3)


def test_extract_image_plane(sorted_nodes, axes):
    from create_res_sim_mat import extract_image_plane

    image_plane = extract_image_plane(sorted_nodes, axes, 0.0)

    assert image_plane.shape == (11, 11)
    assert image_plane[0][0] == 11
    assert image_plane[0][-1] == 1221
    assert image_plane[-1][0] == 121
    assert image_plane[-1][-1] == 1331


def test_get_t():
    """test generation of time vector
    """
    from create_res_sim_mat import gen_t

    t = gen_t(0.1, 10)

    assert len(t) == 10
    assert t[0] == 0.0
    assert t[9] == 0.9
