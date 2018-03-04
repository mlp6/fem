import os
import sys
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '../post/'))


def test_savevtk_data_nparray():
    """test that nparray is read in correctly
    """
    from savevtk import SaveVTK
    from scipy.io import loadmat
    import numpy as np

    d = loadmat('{}/savevtk_data.mat'.format(myPath))
    data = d['data']

    assert isinstance(data, np.ndarray)
    assert data[0, 0, 0] == 1.0
    assert data[3, 4, 5] == 20.0
