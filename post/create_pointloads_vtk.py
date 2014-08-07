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
    print("Extracting data . . .")
    nodes = open(args.nodefile, 'r')

    if args.loadfile is None:
        loads = None
    else:
        loads = open(args.loadfile, 'r')

    # create output file
    if args.elefile is None:
        # if ele file not given, make a structured grid
        # using just nodes and loads files
        create_vts(args, nodes, loads, args.loadout)
    else:
        # if ele file is given, make an unstructured grid
        # containing part IDs.
        create_vtu(args, nodes, args.elefile, loads, args.loadout)

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
                        help="name of ASCII file containing node IDs and positions.",
                        default="nodes.dyn")
    parser.add_argument("--elefile",
                        help="name of ASCII file containing element IDs, part IDs, " 
                        "and node components. If this argument is given, then "
                        "an unstructured grid VTK file (.vtu) will be created "
                        "instead of a structured grid VTK file (.vts).", 
                        default=None)
    parser.add_argument("--loadfile", help="name of PointLoads file. Loads will "
                        "not be written to VTK file if load file is not given.",
                        default=None)
    parser.add_argument("--loadout", help="name of output .vts file.",
                        default="nodeLoads.vts")
    args = parser.parse_args()

    return args

def create_vts(args, nodes, loads, loadout):
    '''
    Writes .vts file from node and load files. StructuredGrid format assumes
    a linear mesh, so if your mesh is actually nonlinear, this script should be run
    using with an elements file.
    '''
        
    # writing .vts file header
    # making sure file extension is correct
    if '.' in loadout and not loadout.endswith('.vts'):
        loadout = loadout[:loadout.find('.')]
        loadout = loadout + '.vts'
 
    loadout = open(loadout, 'w')
    loadout.write('<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">\n')

    # writing opening tags and node position data to .vts file
    numNodes, numElems = writeNodePositions(loadout, args, 'vts')

    # writing point data(node IDs and loads)
    loadout.write('\t\t\t<PointData>\n')
    writeNodeIDs(loadout, args, numNodes)
    writePointLoads(loadout, loads, numNodes)
    loadout.write('\t\t\t</PointData>\n')

    # write closing tags
    loadout.write('\t\t</Piece>\n')
    loadout.write('\t</StructuredGrid>\n')
    loadout.write('</VTKFile>')
    loadout.close()

def create_vtu(args, nodes, elems, loads, loadout):
    # making sure file extension is correct
    if '.' in loadout and not loadout.endswith('.vtu'):
        loadout = loadout[:loadout.find('.')]
        loadout = loadout + '.vtu'
 
    # writing .vtu file header
    loadout = open(loadout, 'w')
    
    loadout.write('<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">\n')
    
    # writing node position data to .vtu file
    numNodes, numElems = writeNodePositions(loadout, args, 'vtu')

    # writing point data(node IDs and loads (if given))
    loadout.write('\t\t\t<PointData>\n')
    writeNodeIDs(loadout, args, numNodes)
    if not loads is None:
        writePointLoads(loadout, loads, numNodes)
    loadout.write('\t\t\t</PointData>\n')
    
    # writing cells using elefile
    writeCells(loadout, elems)
    
    # writing celldata using elefile
    loadout.write('\t\t\t<CellData>\n')
    writeCellData(loadout, elems)
    loadout.write('\t\t\t</CellData>\n')
    
    # write closing tags
    loadout.write('\t\t</Piece>\n')
    loadout.write('\t</UnstructuredGrid>\n')
    loadout.write('</VTKFile>')
    loadout.close()

def writeNodePositions(loadout, args, filetype):
    '''
    writes opening tags as well as node positions to 
    loadout file. returns array containing number of
    nodes (index = 0) and number of elements (index = 1).
    '''
    print 'Writing node positions'
    nodes = open(args.nodefile, 'r')

    headerWritten = False
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
            numElems = dimensions[0]*dimensions[1]*dimensions[2]

            # writing volume dimensions to .vts file, and finishing up header
            if filetype is 'vts':
                loadout.write('\t<StructuredGrid WholeExtent="0 %d 0 %d 0 %d">\n' \
                                  % (dimensions[0], dimensions[1], dimensions[2]))
                loadout.write('\t\t<Piece Extent="0 %d 0 %d 0 %d">\n' \
                                  % (dimensions[0], dimensions[1], dimensions[2]))
            if filetype is 'vtu':
                loadout.write('\t<UnstructuredGrid>\n')
                loadout.write('\t\t<Piece NumberOfPoints="%d" NumberOfCells="%d">\n' \
                                  % (numNodes, numElems))

            loadout.write('\t\t\t<Points>\n')
            loadout.write('\t\t\t\t<DataArray type="Float32" Name="Array" NumberOfComponents="3" format="ascii">\n')

            headerWritten = True

        if not headerWritten: # cannot get dimension data from nodefile header or nodes are nonlinear
            # get max node ID and coordinates of padding node
            numNodes = 0
            nodeCount = open(args.nodefile, 'r')
            for line in nodeCount:
                if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
                    raw_data = line.split(',')
                    numNodes = int(raw_data[0])
                    paddingNodePos = raw_data[1:]
            nodeCount.close()

            # count number of elements
            numElems = 0
            elemCount = open(args.elefile, 'r')
            for line in elemCount:
               if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
                   numElems += 1
            #pointCellHeaderPosition = loadout.tell()
            #loadout.write(' '*256)
            #loadout.write('\n')
            # initialize currentNode variable, which will be 
            # used for node position padding
            currentNode = 1

            loadout.write('\t<UnstructuredGrid>\n')
            loadout.write('\t\t<Piece NumberOfPoints="%d" NumberOfCells="%d">\n' \
                              % (numNodes, numElems))
            loadout.write('\t\t\t<Points>\n')
            loadout.write('\t\t\t\t<DataArray type="Float32" Name="Array" NumberOfComponents="3" format="ascii">\n')
            headerWritten = True


        # reading node position data from nodefile
        if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
            raw_data = line.split(',')
            while currentNode < int(raw_data[0]):
                loadout.write('\t\t\t\t\t%s %s %s' \
                              % (paddingNodePos[0], paddingNodePos[1], paddingNodePos[2]))
                currentNode += 1
            loadout.write('\t\t\t\t\t%s %s %s' \
                              % (raw_data[1], raw_data[2], raw_data[3]))
            currentNode += 1
        
    # done writing node position data
    loadout.write('\t\t\t\t</DataArray>\n')
    loadout.write('\t\t\t</Points>\n')
    nodes.close()

    return numNodes, numElems

def writeNodeIDs(loadout, args, numNodes):
    ''' 
    writes node IDs to loadout file
    '''

    print 'Writing node IDs'
    loadout.write('\t\t\t\t<DataArray type="Float32" Name="node_id" format="ascii">\n')
    for i in range(1, numNodes+1):
        loadout.write('\t\t\t\t\t%.1f\n' % i)
    loadout.write('\t\t\t\t</DataArray>\n')

def writePointLoads(loadout, loads, numNodes):
    '''
    writes point loads to loadout file
    '''
    print 'Writing point loads'
    loadout.write('\t\t\t\t<DataArray NumberOfComponents="3" type="Float32" Name="loads" format="ascii">\n')

    # note that PointLoads file only list nodes with nonzero loads,
    # so nodes not listed in the PointLoads file written with loads
    # of zero.
    currentNode = 1
    for line in loads:
        if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
            raw_data = line.split(',')
            while currentNode < int(raw_data[0]):
                    loadout.write('\t\t\t\t\t0.0 0.0 0.0\n')
                    currentNode += 1

            loadout.write('\t\t\t\t\t0.0 0.0 %f\n' % float(raw_data[3]))
            currentNode += 1 

    # finish writing zero load nodes into .vts file
    while currentNode <= numNodes:
        loadout.write('\t\t\t\t\t0.0 0.0 0.0\n')
        currentNode += 1 

    loadout.write('\t\t\t\t</DataArray>\n')

def writeCells(loadout, elefile):
    '''
    writes cell connectivity and types to loadout file
    '''
    print 'Writing cells'
    loadout.write('\t\t\t<Cells>\n')

    # unfortunately need to loop through entire elements file 3 separate times
    # to get info necessary for cell data. definitely easier to construct VTK file using
    # the legacy format, rather than the newer XML format in this case.

    # write cell connectivity array
    loadout.write('\t\t\t\t<DataArray type="Int32" Name="connectivity" Format="ascii">\n')
    elems = open(elefile, 'r')
    for line in elems:
        if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
            raw_data = line.split(',')
            loadout.write('\t\t\t\t\t')
            for nodeID in raw_data[2:]:
                # need to subtract one to convert to 0-based indices
                node = int(nodeID)
                node -= 1
                loadout.write('%d ' % node)
            loadout.write('\n')
    elems.close()
    loadout.write('\t\t\t\t</DataArray>\n')
    
    # write cell offsets
    loadout.write('\t\t\t\t<DataArray type="Int32" Name="offsets" Format="ascii">\n')
    elems = open(elefile, 'r')
    offset = 0
    for line in elems:
        if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
            raw_data = line.split(',')
            offset += len(raw_data[2:])
            loadout.write('\t\t\t\t\t %d\n' % offset)
    elems.close()
    loadout.write('\t\t\t\t</DataArray>\n')

    # write cell types
    # reference figures 2+3 on pages 9-10 for more info on types:
    # http://www.vtk.org/VTK/img/file-formats.pdf
    loadout.write('\t\t\t\t<DataArray type="Int32" Name="types" Format="ascii">\n')
    elems = open(elefile, 'r')
    for line in elems:
        if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
            raw_data = line.split(',')
            numVertices = len(raw_data[2:])
            if numVertices == 8:
                cellType = 12
            loadout.write('\t\t\t\t\t %d\n' % cellType)
    elems.close()
    loadout.write('\t\t\t\t</DataArray>\n')
    loadout.write('\t\t\t</Cells>\n')

    
def writeCellData(loadout, elefile):
    '''
    writes cell part IDs
    '''
    print 'Writing cell data'
    
    loadout.write('\t\t\t\t<DataArray type="Int32" Name="part id" Format="ascii">\n')
    elems = open(elefile, 'r')
    for line in elems:
        if not line.startswith('$') and not line.startswith('*') and not line.startswith('\n'):
            raw_data = line.split(',')
            loadout.write('\t\t\t\t\t%s\n' % raw_data[1])
    elems.close()
    loadout.write('\t\t\t\t</DataArray>\n')

if __name__ == "__main__":
    main()
