"""test_TopLoad.py
"""

import sys
import os
import pytest
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(myPath, '/../mesh/'))


def test_extract_top_plane_nodes():
    from TopLoad import extract_top_plane_nodes

    nodefile = '%s/nodes.dyn' % myPath
    planeNodeIDs = extract_top_plane_nodes(nodefile=nodefile,
                                           top_face=[0, 0, 0, 0, 0, 1])

    assert planeNodeIDs[0][0] == 1211
    assert planeNodeIDs[-1][-1] == 1331


def test_writeNodeLoads_disp(tmpdir):
    from TopLoad import writeNodeLoads
    f = tmpdir.join("topload.dyn")
    writeNodeLoads(loadfile=f.strpath, planeNodeIDs=[[1, 2, 3], [4, 5, 6]],
                   loadtype='disp', direction=2, amplitude=-1.0, lcid=1)
    lines = f.readlines()
    assert lines[0] == "*BOUNDARY_PRESCRIBED_MOTION_NODE\n"
    assert lines[1] == "1,3,2,1,-1.000000\n"
    assert lines[-1] == "*END\n"


def test_writeNodeLoads_force(tmpdir):
    from TopLoad import writeNodeLoads
    f = tmpdir.join("topload.dyn")
    writeNodeLoads(loadfile=f.strpath, planeNodeIDs=[[1, 2, 3], [4, 5, 6]],
                   loadtype='force', direction=2, amplitude=-1.0, lcid=1)
    lines = f.readlines()
    assert lines[0] == "*LOAD_NODE_POINT\n"
    assert lines[1] == "1,3,1,-1.000000\n"
    assert lines[-1] == "*END\n"


def test_read_cli():
    from TopLoad import read_cli
    import sys

    sys.argv = ['TopLoad.py', '--amplitude', '-5.0']
    opts = read_cli()
    assert opts.amplitude == -5.0
