#!/usr/local/bin/python2.7
'''
CreateStructure.py - create "simple" structures in the FE meshes (e.g., spheres, layers)

This code was based on the older CreateLesion.pl and CreateLayer.pl scripts.

v0.1.1 (2013-01-29) [mlp6]
* using argparse to display default input values with --help
* added license information

LICENSE:
This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License (CC BY-NC-SA 3.0)
http://creativecommons.org/licenses/by-nc-sa/3.0/
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2010-11-24"
__modified__ = "2013-01-29"
__version__ = "0.1.1"
__license__ = "CC BY-NC-SA 3.0"

def main():
    import sys
    import numpy as n

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate new element structure file as specified on the command line.",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--nefile",dest="nefile",help="new element definition output file",default="struct.dyn")
    parser.add_argument("--nodefile",dest="nodefile",help="node definition input file",default="nodes.dyn")
    parser.add_argument("--elefile",dest="elefile",help="element definition input file",default="elems.dyn")
    parser.add_argument("--partid",dest="partid",help="part ID to assign to the new structure",default=2)
    parser.add_argument("--struct",dest="struct",help="type of structure (e.g., sphere, layer)",default="sphere")
    parser.add_argument("--sopts",dest="sopts",help="structure options (see in-code comments)",nargs='+',type=float)

    args = parser.parse_args()

    # find nodes in the structure and assign them to a dictionary
    structNodeIDs = findStructNodeIDs(args.nodefile,args.struct,args.sopts)

    # find elements that contain the structure nodes
    (elems, structElemIDs) = findStructElemIDs(args.elefile,structNodeIDs)

    # generate the new element file with the structure elements assigned the new part ID
    NEFILE = open(args.nefile,'w')
    NEFILE.write("$ Generated using %s (version %s) with the following options:\n" % (sys.argv[0],__version__))
    NEFILE.write("$ %s\n" % args)
    NEFILE.write('$ # Structure Nodes = %i\n' % structNodeIDs.__len__())
    NEFILE.write('$ # Structure Elements = %i\n' % structElemIDs.__len__())
    NEFILE.write('*ELEMENT_SOLID\n')
    for i in elems:
        if structElemIDs.has_key(i[0]):
            i[1] = args.partid
        NEFILE.write('%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\n' % (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9]))
    NEFILE.write('*END')
    NEFILE.close()

#############################################################################################################################
def findStructNodeIDs(nodefile,struct,sopts):
    import sys
    import numpy as n

    nodeIDcoords = n.loadtxt(nodefile, delimiter=',', comments='*', dtype=[('id','i4'),('x','f4'),('y','f4'),('z','f4')])

    structNodeIDs = {}

    if struct == 'sphere':
        '''
        sopts is assumed to be a 4 element tuple with the following items:
            sphere center coordinates (x,y,z)
            sphere radius
        ''' 
        for i in nodeIDcoords:
            nodeRad = n.sqrt(n.power((i[1]-sopts[0]),2) + n.power((i[2]-sopts[1]),2) + n.power((i[3]-sopts[2]),2))
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

    else:
        sys.exit('ERROR: The specific structure (%s) is not defined' % struct)
    
    if structNodeIDs.__len__ == 0:
        sys.exit('ERROR: no structure nodes were found')

    return structNodeIDs
#############################################################################################################################
def findStructElemIDs(elefile,structNodeIDs):
    import sys
    import numpy as n

    elems = n.loadtxt(elefile, delimiter=',', comments='*', dtype=[('id','i4'),('pid','i4'),('n1','i4'),('n2','i4'),('n3','i4'),('n4','i4'),('n5','i4'),('n6','i4'),('n7','i4'),('n8','i4')])

    structElemIDs = {}

    for i in elems:
        if structNodeIDs.has_key(i[2] or i[3] or i[4] or i[5] or i[6] or i[7] or i[8] or i[9]):
            structElemIDs[i[0]] = True
    
    if structElemIDs.__len__ == 0:
        sys.exit('ERROR: no structure elements were found')

    return (elems, structElemIDs)
#############################################################################################################################
    
if __name__ == "__main__":
    main()
