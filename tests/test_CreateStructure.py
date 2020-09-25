"""test_CreateStructure.py
"""

from pathlib import Path
testPath = Path(__file__).parent

def test_define_struct_type():
    from fem.mesh.CreateStructure import define_struct_type

    class Args:
        sphere = False
        ellipsoid = False
        cube = False
        layer = True

    args = Args()
    struct_type = define_struct_type(args)

    assert struct_type == "layer"

def test_findStructNodeIDs():
    from fem.mesh.CreateStructure import findStructNodeIDs

    structNodeIDs = findStructNodeIDs(testPath / "nodes.dyn", "layer", [3.0, -0.5, 0.0])

    assert 779 in structNodeIDs
    assert 39 not in structNodeIDs
    assert 1331 in structNodeIDs


def test_findStructElemIDs():
    from fem.mesh.CreateStructure import findStructElemIDs

    (elems, structElemIDs) = findStructElemIDs(testPath / "elems.dyn", [1331,])

    assert 1000 in structElemIDs
    assert 100 not in structElemIDs