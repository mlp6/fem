'''
GenMesh.py

Generate a 3D rectilinear mesh as node and element input files for LS-DYNA3D.

LICENSE:
The MIT License (MIT)

Copyright (c) 2014 Mark L. Palmeri

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__created = "2013-08-21"
__modified__ = "2014-02-21"
__version__ = __modified__
__license__ = "MIT"


def main():
    import sys
    import fem_mesh

    fem_mesh.check_version()

    # read in CLI arguments
    args = parse_cli()

    # generate node & element output files
    out_file_header = "$ Generated using %s (v%s) with the following "
    "options:\n" % (sys.argv[0], __version__)

    writeNodes(args.nodefile, out_file_header)
    writeElems(args.elefile, out_file_header)


def writeNodes(nodefile, header_comment):
    NODEFILE = open(nodefile, 'w')
    NODEFILE.write("%s\n" % (header_comment))
    NODEFILE.write('*NODE\n')
    NODEFILE.write('*END')
    NODEFILE.close()


def writeElems(elefile, header_comment):
    ELEMFILE = open(elefile, 'w')
    ELEMFILE.write("%s\n" % (header_comment))
    ELEMFILE.write('*ELEMENT_SOLID\n')
    ELEMFILE.write('*END')
    ELEMFILE.close()


def parse_cli():
    import argparse as ap

    par = ap.ArgumentParser(description="Generate rectilinear 3D mesh as "
                            "specified on the command line.",
                            formatter_class=ap.ArgumentDefaultsHelpFormatter)
    par.add_argument("--nodefile",
                     dest="nodefile",
                     help="node definition input file",
                     default="nodes.dyn")
    par.add_argument("--elefile",
                     dest="elefile",
                     help="element definition input file",
                     default="elems.dyn")
    par.add_argument("--partid",
                     dest="partid",
                     help="part ID to assign to the new structure",
                     default=1)
    par.add_argument("--n1",
                     dest="n1",
                     help="first mesh vertex (x, y, z)",
                     default=(-1, -1, 0))
    par.add_argument("--n2",
                     dest="n2",
                     help="second mesh vertex (x, y, z)",
                     default=(1, 1, 0))
    par.add_argument("numElem",
                     dest="numElem",
                     help="number of elements (ints) in each dimension "
                          "(x, y, z)",
                     default=(10, 10, 10))

    args = par.parse_args()

    return args


if __name__ == "__main__":
    main()
