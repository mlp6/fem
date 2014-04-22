"""
CreateStructure.py

Create "simple" structures in the FE meshes (e.g., spheres, layers). This code
was based on the older CreateLesion.pl and CreateLayer.pl scripts.

===============================================================================
MODIFICATION HISTORY
===============================================================================
v0.1.1 (2013-01-29) [mlp6]
* using argparse to display default input values with --help
* added license information

v0.1.2 (2013-03-05) [brb17]
* added struct for ellipsoid of arbitrary size and orientation

v0.1.3 (2013-05-05) [nbb5]
* added struct for cube

v0.2a [mlp6]
* PEP8 compliant
* removed depreciated dict.has_keys()
* changed versions to date stamps
* THIS VERSION WILL YIELD SLIGHTLY DIFFERENT OUTPUT THAN PREVIOUS VERSIONS
  + Round-off error was affecting previous versions, causing a small difference
    in the structural boundaries
  + This version will round-up, making structures slightly larger if there were
    ambiguous boundaries in previous meshes
* migrated to python3

===============================================================================
LICENSE
===============================================================================
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
===============================================================================
"""

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__license__ = "MIT"
__version__ = "v0.2a"


def main():
    import sys
    import fem_mesh

    fem_mesh.check_version()

    # lets read in some CLI arguments
    args = parse_cli()

    # find nodes in the structure and assign them to a dictionary
    structNodeIDs = findStructNodeIDs(args. nodefile, args.struct, args.sopts)

    # find elements that contain the structure nodes
    (elems, structElemIDs) = findStructElemIDs(args.elefile, structNodeIDs)

    # generate the new element file with the structure elements assigned the
    # new part ID
    NEFILE = open(args.nefile, 'w')
    NEFILE.write("$ Generated using %s (version %s) with the following "
                 "options:\n" % (sys.argv[0], __version__))
    NEFILE.write("$ %s\n" % args)
    NEFILE.write('$ # Structure Nodes = %i\n' % structNodeIDs.__len__())
    NEFILE.write('$ # Structure Elements = %i\n' % structElemIDs.__len__())
    NEFILE.write('*ELEMENT_SOLID\n')
    for i in elems:
        if i[0] in structElemIDs:
        #if structElemIDs.has_key(i[0]):
            i[1] = args.partid
        j = i.tolist()
        NEFILE.write('%s\n' % ','.join('%i' % val for val in j[0:10]))
    NEFILE.write('*END')
    NEFILE.close()


def parse_cli():
    import argparse

    par = argparse.ArgumentParser(
        description="Generate new element structure file as specified on the"
        "command line.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    par.add_argument("--nefile", dest="nefile", help="new element definition"
                     "output file", default="struct.dyn")
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
                     default=2)
    par.add_argument("--struct",
                     dest="struct",
                     help="type of structure (sphere, layer, ellipsoid, cube)",
                     default="sphere")
    par.add_argument("--sopts",
                     dest="sopts",
                     help="structure options (see in-code comments)",
                     nargs='+',
                     type=float)

    args = par.parse_args()

    return args


def findStructNodeIDs(nodefile, struct, sopts):
    import sys
    import numpy as n
    import math as m
    import fem_mesh

    nodefile_nocmt = fem_mesh.strip_comments(nodefile)
    nodeIDcoords = n.loadtxt(nodefile_nocmt,
                             delimiter=',',
                             comments='*',
                             dtype=[('id', 'i4'), ('x', 'f4'),
                                    ('y', 'f4'), ('z', 'f4')])
    structNodeIDs = {}

    if struct == 'sphere':
        '''
        sopts is assumed to be a 4 element tuple with the following items:
            sphere center coordinates (x,y,z)
            sphere radius
        '''
        for i in nodeIDcoords:
            nodeRad = n.sqrt(n.power((i[1] - sopts[0]), 2) +
                             n.power((i[2] - sopts[1]), 2) +
                             n.power((i[3] - sopts[2]), 2))
            if nodeRad < sopts[3]:
                structNodeIDs[i[0]] = True

    elif struct == 'layer':
        '''
        sopts is assumed to be a 3 element tuple with the following items:
            dimension for normal to layer (x = 1, y = 2, z = 3)
            layer bounds (min,max)
        '''
        for i in nodeIDcoords:
            if i[sopts[0]] > sopts[1] and i[sopts[0]] < sopts[2]:
                structNodeIDs[i[0]] = True

    elif struct == 'ellipsoid':
        '''
        sopts is assumed to be a 9 element tuple with the following items:
            ellipsoid center coordinates (x,y,z)
            ellipsoid half-axis lengths (a,b,c)
            ellipsoid euler angles (phi,theta,psi) in DEGREES
        '''
        cph = m.cos(m.radians(sopts[6]))    # cos(phi)
        sph = m.sin(m.radians(sopts[6]))    # sin(phi)
        cth = m.cos(m.radians(sopts[7]))    # cos(theta)
        sth = m.sin(m.radians(sopts[7]))    # sin(theta)
        cps = m.cos(m.radians(sopts[8]))    # cos(psi)
        sps = m.sin(m.radians(sopts[8]))    # sin(psi)

        # rotation matrix
        R = n.matrix([[cth * cps, -cph * sps + sph * sth * cps, sph * sps +
                       cph * sth * cps],
                      [cth * sps, cph * cps + sph * sth * sps,
                       -sph * cps + cph * sth * sps],
                      [-sth, sph * cth, cph * cth]])
        # diagonal maxtrix of squared ellipsoid half-axis lengths
        A = n.matrix([[n.power(sopts[3], 2), 0, 0],
                      [0, n.power(sopts[4], 2), 0],
                      [0, 0, n.power(sopts[5], 2)]])
        # A matrix - eigenvalues are a^2,b^2,c^2 (square of half-axis lengths),
        # eigenvectors are directions of the orthogonal principal axes
        A = R.transpose().dot(A).dot(R)

        # locate nodes within ellipsoid
        for i in nodeIDcoords:
            radVec = n.matrix([[i[1] - sopts[0]],
                               [i[2] - sopts[1]],
                               [i[3] - sopts[2]]])
            if radVec.transpose().dot(A.I).dot(radVec) <= 1:
                structNodeIDs[i[0]] = True

    elif struct == 'cube':
        '''
        sopts is assumed to be a 6 element tuple with the following items:
            Location of most-negative corner (x,y,z) Respective cube dimensions
            (w,l,h)
        '''
        for i in nodeIDcoords:
            if i[1] >= sopts[0] and \
                i[1] <= (sopts[0] + sopts[3]) and \
                i[2] >= sopts[1] and \
                i[2] <= (sopts[1] + sopts[4]) and \
                i[3] >= sopts[2] and \
                    i[3] <= (sopts[2] + sopts[5]):
                        structNodeIDs[i[0]] = True

    else:
        sys.exit('ERROR: The specific structure (%s) is not defined' % struct)

    if structNodeIDs.__len__ == 0:
        sys.exit('ERROR: no structure nodes were found')

    return structNodeIDs


def findStructElemIDs(elefile, structNodeIDs):
    import sys
    import numpy as n
    import fem_mesh

    elefile_nocmt = fem_mesh.strip_comments(elefile)
    elems = n.loadtxt(elefile_nocmt, delimiter=',', comments='*',
                      dtype=[('id', 'i4'), ('pid', 'i4'), ('n1', 'i4'),
                             ('n2', 'i4'), ('n3', 'i4'), ('n4', 'i4'),
                             ('n5', 'i4'), ('n6', 'i4'), ('n7', 'i4'),
                             ('n8', 'i4')])

    structElemIDs = {}

    for i in elems:
        # I hate this hard-coded syntax, but this works (for now)
        j = i.tolist()
        insideStruct = any(x in structNodeIDs for x in j[2:10])
        if insideStruct:
            structElemIDs[i[0]] = True

    if structElemIDs.__len__ == 0:
        sys.exit('ERROR: no structure elements were found')

    return (elems, structElemIDs)


if __name__ == "__main__":
    main()
