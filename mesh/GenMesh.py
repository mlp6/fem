#!/bin/env python2.7
'''
GenMesh.py - generate a mesh (nodes and elements files) to be used by LS-DYNA

LICENSE:
Copyright (C) 2013 Mark L. Palmeri

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__ = "Mark Palmeri (mlp6)"
__created = "2013-08-21"
__modified__ = "2013-08-21"
__license__ = "GPLv3"


def main():
    import sys
    import numpy as n

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate new element structure file as specified on the command line.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nodefile", dest="nodefile", help="node definition input file", default="nodes.dyn")
    parser.add_argument("--elefile", dest="elefile", help="element definition input file", default="elems.dyn")
    parser.add_argument("--meshgen", dest="meshgen", help="mesh generation parameters file (lspp4 format)", default="MeshGen.cfile")
    parser.add_argument("--partid", dest="partid", help="part ID to assign to the new structure", default=1)

    args = parser.parse_args()

    # read the mesh generation parameter file
    readMeshGen(args.meshgen)

    # generate node output file
    writeNodes(args.nodefile)

    # generate element output file
    writeElems(args.elefile)

#############################################################################################################################
def readMeshGen(meshgen):
    MESHGENFILE = open(

#############################################################################################################################
def writeNodes(nodefile):
    NODEFILE = open(nodefile, 'w')
    NODEFILE.write("$ Generated using %s (modified %s) with the following options:\n" % (sys.argv[0], __modified__))
    NODEFILE.write("$ %s\n" % args)
    NODEFILE.write('*NODE\n')
    writeNodes(NODEFILE)
    NODEFILE.write('*END')
    NODEEFILE.close()

#############################################################################################################################
def writeElems(elefile):
    ELEMFILE = open(elefile, 'w')
    ELEMFILE.write("$ Generated using %s (modified %s) with the following options:\n" % (sys.argv[0], __modified__))
    ELEMFILE.write("$ %s\n" % args)
    ELEMFILE.write('*ELEMENT_SOLID\n')
    ELEMFILE.write('*END')
    ELEMFILE.close()

#############################################################################################################################

if __name__ == "__main__":
    main()
