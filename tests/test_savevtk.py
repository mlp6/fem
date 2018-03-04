import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '../post/'))


def test_savevtk_data_nparray(savevtk_data):
    """test that nparray data read in correctly
    """
    from numpy import ndarray

    assert isinstance(savevtk_data, ndarray)
    assert savevtk_data[0, 0, 0] == 1.0
    assert savevtk_data[3, 4, 5] == 20.0


def test_savevtk_data_nparray_attribute(savevtk_data):
    from savevtk import SaveVTK

    vtkobj = SaveVTK(savevtk_data, (0.0, 0.0, 0.0), (0.1, 0.1, 0.1))

    assert savevtk_data.all() == vtkobj.data.all()
