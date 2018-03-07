import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '../post/'))


def test_preallocate_arfidata(sorted_nodes, axes):
    from create_res_sim import preallocate_arfidata

    from create_res_sim import extract_image_plane
    image_plane = extract_image_plane(sorted_nodes, axes, 0.0)

    arfidata = preallocate_arfidata(image_plane, 3)

    assert arfidata.shape == (11, 11, 3)


def test_extract_image_plane(sorted_nodes, axes):
    from create_res_sim import extract_image_plane

    image_plane = extract_image_plane(sorted_nodes, axes, 0.0)

    assert image_plane.shape == (11, 11)
    assert image_plane[0][0] == 11
    assert image_plane[0][-1] == 1221
    assert image_plane[-1][0] == 121
    assert image_plane[-1][-1] == 1331


def test_get_t():
    """test generation of time vector
    """
    from create_res_sim import gen_t

    t = gen_t(0.1, 10)

    assert len(t) == 10
    assert t[0] == 0.0
    assert t[9] == 0.9


def test_savemat(tmpdir):
    from create_res_sim import run
    from scipy.io import loadmat

    matfile = tmpdir.join('res_sim_test.mat')
    valid_data_path = '{}/../examples/gauss_qsym_pml'.format(myPath)

    run(dynadeck='{}/gauss_qsym_pml.dyn'.format(valid_data_path),
        dispout='{}/disp.dat.xz'.format(valid_data_path),
        nodedyn='{}/nodes.dyn'.format(valid_data_path), ressim=matfile.strpath)

    valid_data = loadmat('{}/res_sim_valid.mat'.format(valid_data_path))
    test_data = loadmat(matfile.strpath)

    assert test_data['arfidata'][10, 10, 2] == valid_data['arfidata'][10, 10, 2]
