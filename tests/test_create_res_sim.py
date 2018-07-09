import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '../post/'))


def test_preallocate_arfidata(sorted_nodes, axes):
    from create_res_sim import __preallocate_arfidata

    from create_res_sim import extract_image_plane
    image_plane = extract_image_plane(sorted_nodes, axes, 0.0)

    arfidata = __preallocate_arfidata(image_plane, 3)

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
    from create_res_sim import __gen_t

    t = __gen_t(0.1, 10)

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

    assert (test_data['arfidata'][10, 10, 2] ==
            valid_data['arfidata'][10, 10, 2])


def test_saveh5(tmpdir):
    from create_res_sim import run
    import h5py

    h5file = tmpdir.join('res_sim_test.h5')
    valid_data_path = '{}/../examples/gauss_qsym_pml'.format(myPath)

    run(dynadeck='{}/gauss_qsym_pml.dyn'.format(valid_data_path),
        dispout='{}/disp.dat.xz'.format(valid_data_path),
        nodedyn='{}/nodes.dyn'.format(valid_data_path), ressim=h5file.strpath)

    valid_data = h5py.File('{}/res_sim_valid.h5'.format(valid_data_path))
    test_data = h5py.File(h5file.strpath)

    assert (test_data['arfidata'][10, 10, 2] ==
            valid_data['arfidata'][10, 10, 2])


def test_savepvd(tmpdir):
    """Test the PVD/VTR files written correctly."""
    from create_res_sim import extract3Darfidata as run
    import filecmp

    pvdfile = tmpdir.join('res_sim.pvd')
    valid_data_path = '{}/../examples/gauss_qsym_pml'.format(myPath)

    run(dynadeck='{}/gauss_qsym_pml.dyn'.format(valid_data_path),
        dispout='{}/disp.dat.xz'.format(valid_data_path),
        nodedyn='{}/nodes.dyn'.format(valid_data_path), ressim=pvdfile.strpath)

    valid_pvd = '{}/res_sim.pvd'.format(valid_data_path)
    test_pvd = pvdfile.strpath

    assert filecmp.cmp(valid_pvd, test_pvd)
