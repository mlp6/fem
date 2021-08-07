from pathlib import Path

testPath = Path(__file__).parent

def test_create_disp_dat(dispdatgood, nodout1, tmpdir):
    """test writing disp.dat file
    """

    from fem.post.create_disp_dat import create_disp_dat
    import filecmp

    dispdat = tmpdir.join('disp.dat')

    create_disp_dat(str(nodout1), str(dispdat), 1, False)

    assert filecmp.cmp(dispdat, dispdatgood)
