#!/bin/env python
"""
create_pointloads_vtk.py

Creates .vts file, which can be viewed in Paraview, from node and point loads files.

EXAMPLE
=======
python create_disp_dat.py --nodefile nodes.dyn --loadfile PointLoads.dyn --loadout loadout.vts
=======
"""

def main():
    import sys

    if sys.version_info[:2] < (2, 7):
        sys.exit("ERROR: Requires Python >= 2.7")

    # let's read in some command-line arguments
    args = parse_cli()

    # open nodes.dyn file
    print("Extracting data . . .\n")
    nodes = open(args.nodefile, 'r')
    loads = open(args.loadfile, 'r')

    # create output file
    create_vtk(nodes, loads, args.loadout)

def parse_cli():
    '''
    parse command-line interface arguments
    '''
    import argparse

    parser = argparse.ArgumentParser(description="Generate .vts "
                                     "file from nodes and PointLoads files.",
                                     formatter_class=
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodefile",
                        help="name of ASCII file containing node IDs and positions",
                        default="nodes.dyn")
    parser.add_argument("--loadfile", help="name of PointLoads file ",
                        default="disp.dat")
    parser.add_argument("--loadout", help="name of output .vts file",
                        default="nodeLoads.vts")
    args = parser.parse_args()

    return args

def create_vtk(nodes, loads, loadout):
    '''
    write .vts file from node and load files
    '''
    for line in nodes:
        # getting number of elements in x, y, z dimensions
        # as well as total number of nodes (for node ID)
        if 'numElem=' in line:
            dimensionsStart = line.find('[')
            dimensionsEnd = line.find(']')
            dimensions = line[dimensionsStart+1:dimensionsEnd].split(', ')
            dimensions = [int(x) for x in dimensions]
            numNodes = (dimensions[0]+1)*(dimensions[1]+1)*(dimensions[2]+1)
            #print numNodes
if __name__ == "__main__":
    main()
