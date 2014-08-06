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
    # create_vtk(args, nodes, loads)

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

if __name__ == "__main__":
    main()
