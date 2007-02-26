#!/usr/bin/python
# create_nodes.py - create 3D node definitions using my LS-DYNA
# conventions instead of relying on ls-prepost2 for simple
# rectagular solid meshes
# Mark 02/24/07

import numpy

# setup coordinate limits in cm
xmax = 0
xmin = -0.26
ymin = 0
ymax = 1.0
zmin = -3.0
zmax = -1.2
xstep = 0.002
ystep = 0.002
zstep = 0.005

# initialize the nodeID counter
nodeID = 0

# create the output file object
fileOut = file('refined_nodes.asc','w')

# loop over the three dimensions to create all of the nodes
# and write them to fileOut
for x in numpy.arange(xmin,xmax+xstep,xstep):
    for y in numpy.arange(ymin,ymax+ystep,ystep):
        for z in numpy.arange(zmin,zmax+zstep,zstep):
            nodeID = nodeID + 1
            print >> fileOut, '%i,%f,%f,%f' % (nodeID, x, y, z)
 
fileOut.close()
