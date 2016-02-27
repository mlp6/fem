"""conftest.py
"""

import sys
import os
import pytest

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


@pytest.fixture
def sorted_elems():
    """create sorted elements numpy array from nodes.dyn & elems.dyn

    :returns: sorted_elems
    """
    from fem_mesh import load_nodeIDs_coords
    from fem_mesh import load_elems
    from fem_mesh import SortNodeIDs
    from fem_mesh import SortElems

    nodefile = '%s/nodes.dyn' % myPath
    elefile = '%s/elems.dyn' % myPath

    nodeIDcoords = load_nodeIDs_coords(nodefile)
    [snic, axes] = SortNodeIDs(nodeIDcoords)
    elems = load_elems(elefile)
    sorted_elems = SortElems(elems, axes)

    return sorted_elems

