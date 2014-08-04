#!/bin/env python
"""
create_disp_dat.py

Create disp.dat file from nodout file.

This is replacing StuctPost, which relied on LS-PREPOST, to extract data from
d3plot* files.  (LS-PREPOST no longer works gracefully on the cluster w/o
GTK/video support.)  Instead of working with d3plot files, this approach now
utilizes ASCII nodout files.  Also replaced the Matlab scritps, so this should
run self-contained w/ less dependencies.

EXAMPLE
=======
create_disp_dat.py

=======
Copyright 2014 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__license__ = "Apache v2.0"


def main():
    import sys

    if sys.version_info[:2] < (2, 7):
        sys.exit("ERROR: Requires Python >= 2.7")

    # let's read in some command-line arguments
    args = parse_cli()

    # default to make a binary file if output file type isn't indicated
    if (not args.vtk and not args.dat):
        args.dat = True

    # open nodout file
    if args.nodout.endswith('gz'):
        import gzip
        print("Extracting gzip-compressed data . . .\n")
        nodout = gzip.open(args.nodout, 'r')
    else:
        print("Extracting data . . .\n")
        nodout = open(args.nodout, 'r')

    # create output file
    if (args.dat):
        create_dat(args, nodout)

    if (args.vtk):
        create_vtk(args, nodout)

def create_dat(args, nodout):
    import sys

    # open dispout for binary writing
    dispout = open(args.dispout, 'wb')

    header_written = False
    timestep_read = False
    timestep_count = 0
    for line in nodout:
        if 'nodal' in line:
            timestep_read = True
            timestep_count = timestep_count + 1
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
                process_timestep_data(data, dispout)
            else:
                raw_data = line.split()
                corrected_raw_data = correct_Enot(raw_data)
                data.append(map(float, corrected_raw_data))

    # close all open files
    dispout.close()
    nodout.close()

def create_vtk(args, nodout):
    import sys

    disp_position = open('pos_temp.txt', 'w')
    disp_displace = open('disp_temp.txt', 'w')

    positions_written = False
    timestep_read = False
    firstLine = True
    timestep_count = 0
    numNodes = 0

    for line in nodout:
        if 'n o d a l' in line:
            raw_data = line.split()
            # get time value of timestep
            # consider using regular expressions rather than hardcoding this value?
            timestep_value = str(float(raw_data[28])) 
        if 'nodal' in line:
            # x, y, z hold range of x, y, z coordinates ([min, max])
            firstLine = True
            x = []
            y = []
            z = []
            timestep_read = True
            timestep_count = timestep_count + 1
            if timestep_count == 1:
                sys.stdout.write('Time Step: ')
                sys.stdout.flush()
            sys.stdout.write('%i ' % timestep_count)
            sys.stdout.flush()
            continue
        if timestep_read is True:
            if line.startswith('\n'):  #done reading a time step
                timestep_read = False
                positions_written = True
                x.append(float(lastReadCoords[0]))
                y.append(float(lastReadCoords[1]))
                z.append(float(lastReadCoords[2]))
                print x
                print y
                print z
                print numNodes
                break
            else:
                raw_data = line.split()
                # get minimum range of x, y, z coordinates
                if firstLine is True:
                    x.append(float(raw_data[10]))
                    y.append(float(raw_data[11]))
                    z.append(float(raw_data[12]))
                    firstLine = False
                # save the position coordinates in case they are the last ones to be read.
                # this is useful for getting the range of x, y, z coordinates
                lastReadCoords = raw_data[10:13]
                # write displacements to temporary file
                disp_displace.write(' '.join(raw_data[1:4])+'\n')
                # write positions to temporary file. since positions
                # are the same for all timesteps, this only needs to be done once.
                # same with number of nodes
                if not positions_written:
                    disp_position.write(' '.join(raw_data[10:13])+'\n')
                    numNodes += 1

"""    # quick check to make sure file extension is correct
    if (args.dispout.endswith('.dat')):
        args.dispout = args.dispout.replace('.dat', '.vts')

    # open dispout for VTK file writing
    dispout = open(args.dispout, 'w')
    
    # writing the VTK file outline
   dispout.write(
<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">
  <StructuredGrid WholeExtent="">
  <Piece Extent="">
    <PointData Scalars="node_id" Vectors="displacement">
      <DataArray type="Float32" Name="node_id" format="ascii">
      </DataArray>
      <DataArray NumberOfComponents="3" type="Float32" Name="displacement" format="ascii">
      </DataArray>
    </PointData>
    <Points>
      <DataArray type="Float32" Name="Array" NumberOfComponents="3" format="ascii">
      </DataArray>
    </Points>
  </Piece>
  </StructuredGrid>
</VTKFile>)"""

    # time dependence! look at .pvd file stucture for instructions on how to create this.

def parse_cli():
    '''
    parse command-line interface arguments
    '''
    import argparse

    parser = argparse.ArgumentParser(description="Generate disp.dat "
                                     "data from an ls-dyna nodout file.",
                                     formatter_class=
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodout",
                        help="ASCII file containing nodout data",
                        default="nodout.gz")
    parser.add_argument("--dispout", help="name of the binary displacement "
                        "output file", default="disp.dat")
    parser.add_argument("--dat", help="create a binary file", action='store_true')
    parser.add_argument("--vtk", help="create a vtk file", action='store_true')
    args = parser.parse_args()

    return args


def generate_header(data, outfile):
    '''
    generate headers from data matrix of first time step
    '''
    import re
    header = {}
    header['numnodes'] = data.__len__()
    header['numdims'] = 4  # node ID, x-val, y-val, z-val
    ts_count = 0
    t = re.compile('time')
    if outfile.name.endswith('gz'):
        import gzip
        n = gzip.open(outfile.name)
    else:
        n = open(outfile.name)

    with n as f:
        for line in f:
            if t.search(line):
                ts_count = ts_count + 1
    # the re.search detects 1 extra line, so subtract 1
    header['numtimesteps'] = ts_count - 1

    return header


def write_headers(outfile, header):
    '''
    write binary header information to reformat things on read downstream
    'header' is a dictionary containing the necessary information
    '''
    import struct
    outfile.write(struct.pack('fff', header['numnodes'],
                              header['numdims'], header['numtimesteps']))


def process_timestep_data(data, outfile):
    '''
    operate on each time step data row
    '''
    import struct
    # write all node IDs, then x-val, then y-val, then z-val
    [outfile.write(struct.pack('f', data[j][i]))
        for i in [0, 1, 2, 3]
        for j in range(len(data))]

def correct_Enot(raw_data):
    '''
    ls-dyna seems to drop the 'E' when the negative exponent is three digits,
    so check for those in the line data and change those to 'E-100' so that
    we can convert to floats
    '''
    import re
    for i in range(len(raw_data)):
        raw_data[i] = re.sub(r'(?<!E)\-[1-9][0-9][0-9]', 'E-100', raw_data[i])
    return raw_data

if __name__ == "__main__":
    main()

