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


def create_dat(nodout="nodout", dispout="disp.dat", legacynodes=False):
    """create binary data file

    :param str nodout: nodout file create my ls-dyna (default = "nodout")
    :param str dispout: default = "disp.dat"
    :param boolean legacynodes: are node definitions written every timestep (default = False)
    """
    global writenode
    import sys

    nodout = open(nodout, 'r')
    dispout = open(dispout, 'wb')

    header_written = False
    timestep_read = False
    timestep_count = 0
    writenode = True
    for line in nodout:
        if 'nodal' in line:
            timestep_read = True
            timestep_count += 1
            if timestep_count == 1:
                sys.stdout.write('Time Step: ')
                sys.stdout.flush()
            sys.stdout.write('%i ' % timestep_count)
            sys.stdout.flush()
            data = []
            continue
        if timestep_read is True:
            if line.startswith('\n'):  # done reading the time step
                timestep_read = False
                # if this was the first time, everything needed to be read to
                # get node count for header
                if not header_written:
                    header = generate_header(data, nodout)
                    write_headers(dispout, header)
                    header_written = True
                if timestep_count > 1 and not legacynodes:
                    writenode = False
                process_timestep_data(data, dispout, writenode)
            else:
                raw_data = line.split()
                try:
                    raw_data = [float(x) for x in raw_data]
                except ValueError:
                    raw_data = correct_Enot(raw_data)
                    raw_data = [float(x) for x in raw_data]
                data.append(list(raw_data))

    # close all open files
    dispout.close()
    nodout.close()

    return 0


def parse_cli():
    """parse command-line interface arguments
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate disp.dat "
                                     "data from an ls-dyna nodout file.",
                                     formatter_class=
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodout",
                        help="ASCII file containing nodout data",
                        default="nodout")
    parser.add_argument("--dispout",
                        help="name of the binary displacement output file",
                        default="disp.dat")
    parser.add_argument("--legacynodes",
                        help="repeat saving node IDs for each timestep",
                        action="store_true")
    args = parser.parse_args()

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

    searches for 'time' in lines

    :param outfile:
    :returns: ts_count

    """
    ts_count = -1  # start at -1 (one extra instance of 'time' in nodout)
    with open(outfile, 'r') as f:
        for line in f:
            if 'time' in line:
                ts_count += 1
    return ts_count


def write_headers(outfile, header):
    """write binary header

    write binary header information to reformat things on read downstream

    :param str outfile: output file object
    :param header: dictcontaining the necessary information
    :returns: None

    """
    import struct
    outfile.write(struct.pack('fff',
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
    import struct

    # columns are node ID, x-disp, y-disp, z-disp
    if writenode:
        cols2write = [0, 1, 2, 3]
    else:
        cols2write = [1, 2, 3]

    [outfile.write(struct.pack('f', data[j][i])) for i in cols2write for j in range(len(data))]


def correct_Enot(raw_data):
    """
    ls-dyna seems to drop the 'E' when the negative exponent is three digits,
    so check for those in the line data and change those to 'E-100' so that
    we can convert to floats
    """
    import re
    for i in range(len(raw_data)):
        raw_data[i] = re.sub(r'(?<!E)\-[1-9][0-9][0-9]',
                             'E-100',
                             raw_data[i])
    return raw_data


if __name__ == "__main__":
    main()
