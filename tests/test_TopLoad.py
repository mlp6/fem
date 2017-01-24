"""test_bc.py
"""

import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')


def test_extract_top_plane_nodes():
    from TopLoads import extract_top_plane_nodes

    (direction, planeNodeIDs) = extract_top_plane_nodes(nodefile='nodes.dyn', top_face=[0, 0, 0, 0, 0, 1])

    assert direction == 3
    #TODO: test planeNodeIDs


def test_write_bc(tmpdir):
    from TopLoads import writeNodeLoads
    f = tmpdir.join("top_load.dyn")
    writeNodeLoads(loadfile=f.strpath, planeNodeIDs=[[1, 2 ,3], [4, 5, 6]], loadtype='disp', direction=3, lcid=1)
    lines = f.readlines()
    assert lines[1] == "*BOUNDARY_PRESCRIBED_MOTION_NODE\n"
    assert lines[2] == "1,3,2,1,-1.0\n"
    assert lines[-1] == "*END\n"


def test_read_cli():
    from TopLoad import read_cli
    import sys

    sys.argv = ['TopLoad.py', '--direction 2']
    opts = read_cli()
    assert opts.direction == 2
