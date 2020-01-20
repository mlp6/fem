import pytest

def test_savevtk_data_nparray(savevtk_data):
    """test that nparray data read in correctly
    """
    from numpy import ndarray

    assert isinstance(savevtk_data, ndarray)
    assert savevtk_data[0, 0, 0] == 1.0
    assert savevtk_data[3, 4, 5] == 20.0


def test_savevtk_data_nparray_attribute(savevtk_data):
    from fem.post.savevtk import SaveVTK

    vtkobj = SaveVTK(savevtk_data, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))

    assert vtkobj.data.all() == savevtk_data.all()


def test_savevtk_data_origin(savevtk_data):
    from fem.post.savevtk import SaveVTK

    vtkobj = SaveVTK(savevtk_data, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))

    assert vtkobj.origin[0] == 0.0
    assert vtkobj.origin[1] == 1.0
    assert vtkobj.origin[2] == 2.0


def test_savevtk_data_origin(savevtk_data):
    from fem.post.savevtk import SaveVTK

    vtkobj = SaveVTK(savevtk_data, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))

    assert vtkobj.spacing[0] == 0.1
    assert vtkobj.spacing[1] == 0.2
    assert vtkobj.spacing[2] == 0.3


def test_savevtk_data_3D_tuple(savevtk_data):
    from fem.post.savevtk import SaveVTK

    data3d = (savevtk_data, savevtk_data, savevtk_data)

    vtkobj = SaveVTK(data3d, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))

    assert vtkobj.data['x'].all() == savevtk_data.all()
    assert vtkobj.data['y'].all() == savevtk_data.all()
    assert vtkobj.data['z'].all() == savevtk_data.all()


def test_savevtk_raise_3D_exception(savevtk_data):
    from fem.post.savevtk import SaveVTK

    data3d = (savevtk_data, savevtk_data, savevtk_data[:, :, 0:2])

    with pytest.raises(IndexError):
        vtkobj = SaveVTK(data3d, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))


def test_write_scalar(savevtk_data, tmpdir):
    from fem.post.savevtk import SaveVTK

    fname = tmpdir.join('scalar.vtk')

    vtkobj = SaveVTK(savevtk_data, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))

    vtkobj.save_scalar(fname.strpath, dataname="scalars",
                       header_comment="unit test")

    with open(fname.strpath, 'r') as written_file:
        text = written_file.readlines()

    assert text[1] == 'unit test\n'
    assert text[2] == 'ASCII\n'
    assert text[5].split()[2] == '5'
    assert text[7].startswith('ORIGIN')
    assert text[8].split()[3] == '0.300'
    assert text[10].split()[1] == '120'
    assert text[20].split()[0] == '4.000000e+00'
    assert text[32].split()[3] == '1.600000e+01'


def test_write_vector(savevtk_data, tmpdir):
    from fem.post.savevtk import SaveVTK

    fname = tmpdir.join('vector.vtk')

    data3d = (savevtk_data, savevtk_data, savevtk_data)

    vtkobj = SaveVTK(data3d, (0.0, 1.0, 2.0), (0.1, 0.2, 0.3))

    vtkobj.save_vector(fname.strpath, dataname="vectors",
                       header_comment="vector unit test")

    with open(fname.strpath, 'r') as written_file:
        text = written_file.readlines()

    assert text[1] == 'vector unit test\n'
    assert text[2] == 'ASCII\n'
    assert text[5].split()[2] == '5'
    assert text[7].startswith('ORIGIN')
    assert text[8].split()[3] == '0.300'
    assert text[10].split()[1] == '120'
    assert text[29].split()[17] == '8.000000'
    assert text[32].split()[17] == '20.000000'
