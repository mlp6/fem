def test_parse_nodoutR61():
    """correctly parse data from R6.1 nodout files
    """
    from fem.post.create_disp_dat import parse_line

    nodout = open("tests/nodout", "r")
    n = nodout.readlines()
    line = n[8]
    raw_data = parse_line(line)

    assert raw_data[0] == 6
    assert raw_data[1] == 0.0
    assert raw_data[3] == -1.5


def test_parse_nodoutR8():
    """correctly parse data from R8 nodout files
    """
    from fem.post.create_disp_dat import parse_line

    nodout = open("tests/nodout", "r")
    n = nodout.readlines()
    line = n[10]
    raw_data = parse_line(line)

    assert raw_data[0] == 8
    assert raw_data[1] == 0.0
    assert raw_data[3] == -1.5


def test_correct_Enot():
    """test fix -??? -> E-100
    """
    from fem.post.create_disp_dat import parse_line

    nodout = open("tests/nodout", "r")
    n = nodout.readlines()
    line = n[9]

    raw_data = parse_line(line)

    assert raw_data[3] == 0.0


def test_count_timesteps():
    """test counting time steps in nodout
    """
    from fem.post.create_disp_dat import count_timesteps

    ts_count = count_timesteps("tests/nodout")

    assert ts_count == 2


def test_write_header():
    """test writing disp.dat header
    """
    from fem.post.create_disp_dat import open_dispout
    from fem.post.create_disp_dat import write_headers
    import struct

    header = {'numnodes': 4,
              'numdims': 3,
              'numtimesteps': 2
              }

    fname = 'test.dat'
    dispout = open_dispout(fname)
    write_headers(dispout, header)
    dispout.close()

    with open(fname, 'rb') as dispout:
        header = struct.unpack('fff', dispout.read(4*3))

    assert header[0] == 4.0
    assert header[1] == 3.0
    assert header[2] == 2.0
