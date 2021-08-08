"""create_disp_dat.py - generate disp.dat binary from nodout ASCII"""
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.warning('The SLOW Python implementation of create_disp_day is being used.  Consider using create_disp_dat_fast (C implementation via shared object or executable).')

def main():
    args = parse_cli()
    create_dat(args.nodout, args.dispout, args.legacynodes)


def create_dat(nodout="nodout", dispout="disp.dat", legacynodes=False):
    """Create binary data file from nodout ASCII file.

    Args:
        nodout (str):  nodout input filename
        dispout (str) : binary output filename
        legacynodes (Boolean):  (Default value = False)
    """
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
                        # if this was the first time, everything needed to
                        # be read to # get node count for header
                        if not header_written:
                            header = generate_header(data, nodout)
                            write_headers(dispout, header)
                            header_written = True
                            logger.info('Time Step: ')
                        if timestep_count > 1 and not legacynodes:
                            writenode = False
                        logger.info(f"{timestep_count}, ")
                        process_timestep_data(data, dispout, writenode)
                    else:
                        raw_data = parse_line(line)
                        data.append(list(raw_data))

    logger.info("done.")

    return 0


def parse_line(line):
    """Parse raw data line into vector of floats.

    Args:
        line (str): raw data line from nodout

    Returns:
        raw_data (list of floats): [nodeID, xdisp, ydisp, zdisp]

    """
    # first 10 characters (int)
    nodeID = float(line[0:10])
    # X,Y,Z-Disp are the next 3 columns, each are 12 characters:
    # [-]#.#####E[+/-]##
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

    return raw_data


def parse_line_regex(line):
    """Parse raw data line into list of floats using regex.

    This regex approach works, but is very slow!!  It also requires two helper functions to clean up
    malformed data written by ls-dyna (done on purpose, probably to save space).

    Args:
        line (str): raw data line from nodout

    Returns:
        raw_data (list of floats): [nodeID, xdisp, ydisp, zdisp]

    """
    try:
        raw_data = line.split()
        raw_data = [float(x) for x in raw_data]
    except ValueError:
        line = correct_neg(line)
        line = correct_Enot(line)
        raw_data = line.split()
        raw_data = [float(x) for x in raw_data[0:4]]

    return raw_data


def parse_cli():
    """parse command-line interface arguments"""
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

    Args:
        data (nparray): data
        outfile (str): output filename to count times from

    Returns:
        header (dict):

    """
    ts_count = count_timesteps(outfile.name)
    header = {'numnodes': len(data),
              'numdims': 4,
              'numtimesteps': ts_count
              }

    return header


def count_timesteps(outfile: str = 'nodout') -> int:
    """Count timesteps in to outfile.

    Searches for 'time' in lines, and then removes 1 extra entry that occurs
    for t = 0.  `grep` will be used on linux systems (way faster).

    Args:
        outfile (str): usually 'nodout'

    Returns:
        ts_count (int): number of time steps counted - 1

    """
    import platform

    logger.info("Reading number of time steps... ")
    if platform.system() == 'Linux':  # this is significantly faster
        from subprocess import PIPE, Popen
        p = Popen('grep time %s | wc -l' % outfile, shell=True, stdout=PIPE)
        ts_count = int(p.communicate()[0].strip().decode())
    else:
        logger.warning(f"Non-linux OS ({platform.system()}) detected: using slower python implementation")
        ts_count = 0
        with open(outfile, 'r') as f:
            for line in f:
                if 'time' in line:
                    ts_count += 1

    ts_count -= 1  # rm extra time count

    logger.info(f'there are {ts_count}.')

    return ts_count


def write_headers(outfile, header):
    """Write binary header.

    Write binary header information to reformat things on read downstream.

    Args:
        outfile (str): output file object
        header (dict):

    Returns:
      None

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

    Args:
        data (list): list of all data, with each entry containing [nodeID, xdisp, ydisp, zdisp]
        outfile (obj): output file object
        writenode (Boolean): Boolean if the node IDs should be written to save
            ~25% of the disp.dat file size

    Returns:
        None

    """
    from struct import pack

    # columns are node ID, x-disp, y-disp, z-disp
    if writenode:
        cols2write = [0, 1, 2, 3]
    else:
        cols2write = [1, 2, 3]

    [outfile.write(pack('f', data[j][i])) for i in cols2write
     for j in range(len(data))]


def correct_Enot(line):
    """Correct dropped 'E' in -??? scientific notation.

    ls-dyna seems to drop the 'E' when the negative exponent is three digits,
    so check for those in the line data and change those to 'E-100' so that
    we can convert to floats

    This is a helper function only called by parse_line_regex(), which is currently not being used
    by default.

    Args:
        line (str): string of split raw string data

    Returns:
        line with corrected -??? -> -E100

    """
    import re
    reEnnn = re.compile(r'(?<!E)\-[1-9][0-9][0-9]')

    line = re.sub(reEnnn, 'E-100', line)

    return line


def correct_neg(line):
    """Add space before negative coefficient numbers.

    This is a helper function only called by parse_line_regex(), which is currently not being used
    by default.

    Args:
        line (str): raw read line

    Returns:
        line (str): line with space(s) added before negative coefficients

    """
    import re
    rneg = re.compile(r'(-[1-9]\.)')
    line = re.sub(rneg, r' \1', line)

    return line


def open_dispout(dispout):
    """Open dispout file for writing.

    Args:
        dispout (str): dispout filename (disp.dat.xz)

    Returns:
        dispout (obj): file object

    """
    if dispout.endswith('.xz'):
        import lzma
        dispout = lzma.open(dispout, 'wb')
    else:
        dispout = open(dispout, 'wb')

    return dispout


if __name__ == "__main__":
    main()
