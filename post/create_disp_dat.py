#!/bin/env python
"""
:mod:`create_disp_dat` -- generate disp.dat binary from nodout ASCII

.. module:: create_disp_dat
   :synopsis: generate disp.dat binary from nodout ASCII
   :license: Apache v2.0, see LICENSE for details
   :copyright: Copyright 2016 Mark Palmeri

.. moduleauthor:: Mark Palmeri <mlp6@duke.edu>
"""


def main():
    args = parse_cli()
    create_dat(args.nodout, args.dispout, args.legacynodes)


def create_dat(nodout="nodout", dispout="disp.dat.xz", legacynodes=False):
    """create binary data file

    :param str nodout: nodout file created by ls-dyna (default = "nodout")
    :param str dispout: default = "disp.dat.xz"
    :param boolean legacynodes: node IDs written every timestep (default = False)
    """
    global writenode
    header_written = False
    timestep_read = False
    timestep_count = 0
    writenode = True

    with open(nodout, 'r') as nodout:
        with open_dispout(dispout) as dispout:
            for line in nodout:
                if 'nodal' in line:
                    timestep_read = True
                    timestep_count += 1
                    data = []
                    continue
                if timestep_read is True:
                    if line[0:2] == '\n':  # done reading the time step
                        timestep_read = False
                        # if this was the first time, everything needed to be read to
                        # get node count for header
                        if not header_written:
                            header = generate_header(data, nodout)
                            write_headers(dispout, header)
                            header_written = True
                            print('Time Step: ', end="", flush=True)
                        if timestep_count > 1 and not legacynodes:
                            writenode = False
                        print("%i " % timestep_count, end="", flush=True)
                        process_timestep_data(data, dispout, writenode)
                    else:
                        raw_data = parse_line(line)
                        data.append(list(raw_data))

    return 0


def parse_line(line):
    """parse raw data line into vector of floats

    The REGEX approach is just too slow for large nodout files, so I'm leveraging some a priori knowledge
    about the output format:
    Node ID - 10 characters (int)
    X,Y,Z-Disp are the next 3 columns, each are 12 characters: [-]#.#####E[+/-]##

    :param str line: raw data line from nodout
    :return: raw_data (vector of floats)
    """

    nodeID = float(line[0:10])
    try:
        xdisp = float(line[10:22])
    except ValueError:
        xdisp = 0.0
    try:
        ydisp = float(line[22:34])
    except ValueError:
        ydisp = 0.0
    try:
        zdisp = float(line[34:46])
    except ValueError:
        zdisp = 0.0

    raw_data = [nodeID, xdisp, ydisp, zdisp]

    """
    # THIS REGEX APPROACH WORKS, BUT IS VERY SLOW
    try:
        raw_data = line.split()
        raw_data = [float(x) for x in raw_data]
    except ValueError:
        line = correct_neg(line)
        line = correct_Enot(line)
        raw_data = line.split()
        raw_data = [float(x) for x in raw_data[0:4]]
    """

    return raw_data


def parse_cli():
    """parse command-line interface arguments
    """
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    p = ArgumentParser(description="Generate disp.dat "
                       "data from an ls-dyna nodout file.",
                       formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument("--nodout",
                   help="ASCII file containing nodout data",
                   default="nodout")
    p.add_argument("--dispout",
                   help="name of the binary displacement output file",
                   default="disp.dat")
    p.add_argument("--legacynodes",
                   help="repeat saving node IDs for each timestep",
                   action="store_true")
    args = p.parse_args()

    return args


def generate_header(data, outfile):
    """generate headers from data matrix of first time step

    :param data: data
    :param str outfile: output filename to count times from
    :returns: header

    """
    ts_count = count_timesteps(outfile.name)
    header = {'numnodes': len(data),
              'numdims': 4,
              'numtimesteps': ts_count
              }

    return header


def count_timesteps(outfile):
    """count timesteps written to nodout

    searches for 'time' in lines, and then removes 1 extra entry that occurs
    for t = 0

    grep will be used on linux systems (way faster)

    :param outfile: usually 'nodout'
    :returns: int ts_count

    """
    from sys import platform

    print("Reading number of time steps... ", end="", flush=True)
    if platform == "linux":
        from subprocess import PIPE, Popen
        p = Popen('grep time %s | wc -l' % outfile, shell=True, stdout=PIPE)
        ts_count = int(p.communicate()[0].strip().decode())
    else:
        print("Non-linux OS detected -> using slower python implementation", flush=True)
        ts_count = 0
        with open(outfile, 'r') as f:
            for line in f:
                if 'time' in line:
                    ts_count += 1

    ts_count -= 1 # rm extra time count

    print('there are {}.'.format(ts_count), flush=True)

    return ts_count


def write_headers(outfile, header):
    """write binary header

    write binary header information to reformat things on read downstream

    :param str outfile: output file object
    :param header: dictcontaining the necessary information
    :returns: None

    """
    from struct import pack

    outfile.write(pack('fff',
                       header['numnodes'],
                       header['numdims'],
                       header['numtimesteps']
                       )
                  )


def process_timestep_data(data, outfile, writenode):
    """write data for the entire timestep to outfile

    :param data:
    :param outfile: output file object
    :param writenode: Boolean if the node IDs should be written to save
                      ~25% of the disp.dat file size
    :returns: None

    """
    from struct import pack

    # columns are node ID, x-disp, y-disp, z-disp
    if writenode:
        cols2write = [0, 1, 2, 3]
    else:
        cols2write = [1, 2, 3]

    [outfile.write(pack('f', data[j][i])) for i in cols2write for j in range(len(data))]


def correct_Enot(line):
    """correct dropped 'E' in -??? scientific notation

    ls-dyna seems to drop the 'E' when the negative exponent is three digits,
    so check for those in the line data and change those to 'E-100' so that
    we can convert to floats

    :param str line: strict of split raw string data
    :return: line with corrected -??? -> -E100
    """
    import re
    reEnnn = re.compile(r'(?<!E)\-[1-9][0-9][0-9]')

    line = re.sub(reEnnn, 'E-100', line)

    return line


def correct_neg(line):
    """add space before negative coefficient numbers

    :param str line:
    :return: line with space(s) added before negative coefficients
    """
    import re
    rneg = re.compile(r'(-[1-9]\.)')
    line = re.sub(rneg, r' \1', line)

    return line


def open_dispout(dispout):
    """open dispout file for writing

    :param dispout: (str) dispout filename (disp.dat.xz)
    :return: dispout file object
    """
    if dispout.endswith('.xz'):
        import lzma
        dispout = lzma.open(dispout, 'wb')
    else:
        dispout = open(dispout, 'wb')

    return dispout


if __name__ == "__main__":
    main()
