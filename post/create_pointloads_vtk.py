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
        
    # writing .vts file header
    # making sure file extension is correct
    if '.' in loadout and not loadout.endswith('.vts'):
        loadout = loadout[:loadout.find('.')]
        loadout = loadout + '.vts'
 
    loadout = open(loadout, 'w')
    loadout.write('<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">\n')

    # writing node position data to .vts file
    for line in nodes:
        # getting number of elements in x, y, z dimensions
        # as well as total number of nodes (for node ID)
        if 'numElem=' in line:
            # parse dimensions from node file header
            dimensionsStart = line.find('[')
            dimensionsEnd = line.find(']')
            dimensions = line[dimensionsStart+1:dimensionsEnd].split(', ')
            dimensions = [int(x) for x in dimensions]
            numNodes = (dimensions[0]+1)*(dimensions[1]+1)*(dimensions[2]+1)

            # writing volume dimensions to .vts file, and finishing up header
            loadout.write('\t<StructuredGrid WholeExtent="0 %d 0 %d 0 %d">\n' \
                              % (dimensions[0], dimensions[1], dimensions[2]))
            loadout.write('\t\t<Piece Extent="0 %d 0 %d 0 %d">\n' \
                              % (dimensions[0], dimensions[1], dimensions[2]))
            loadout.write('\t\t\t<Points>\n')
            loadout.write('\t\t\t\t<DataArray type="Float32" Name="Array" NumberOfComponents="3" format="ascii">\n')

        # reading node position data from nodefile
        if not line.startswith('$') and not line.startswith('*'):
            raw_data = line.split(',')
            loadout.write('\t\t\t\t\t%s %s %s\n' \
                              % (raw_data[1], raw_data[2], raw_data[3]))
            # just write one set of values for testing
            # REMOVE WHEN READY FOR FULL RUN
            break
        
    # done writing node position data
    loadout.write('\t\t\t\t</DataArray>\n')
    loadout.write('\t\t\t</Points>\n')
    nodes.close()

    # writing node id data
    loadout.write('\t\t\t<PointData Scalars="node_id" Vectors="displacement">\n')
    loadout.write('\t\t\t\t<DataArray type="Float32" Name="node_id" format="ascii">\n')
    for i in range(1, numNodes):
        loadout.write('\t\t\t\t\t%.1f\n' % i)
        # just write one set of values for testing
        # REMOVE WHEN READY FOR FULL RUN
        break
    loadout.write('\t\t\t\t</DataArray>\n')

    

#    for line in loads:
        
            
if __name__ == "__main__":
    main()
