#!/usr/bin/env python

#!/usr/bin/python
#!/bin/env python

from __future__ import division

"""
Using (x1, y1, z1) and (x2, y2, z2) as opposite corners of a meshgrid
and Ele, yEle, and zEle as the number of x, y, and z elements, respectively,
this script generates a linear mesh and defined by nodes.dyn and 
elems.dyn.

Inputs: corner1 = (x1,y1,z1)
        corner2 = (x2,y2,z2)
        numbElements = (x,y,z)
Outputs: nodes.dyn <-- Lists the x, y, and z location of each node in the mesh
         elements.dyn <-- Lists the 8 defining nodes for each element in the mesh

LICENSE
=======
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
"""

__author__ = "Jackson Bruce Morton II"
__email__ = "jmorton27@gmail.com"
__date__ = "2014-01-16"
__modified__ = "2014-04-14"
__license__ = "GPLv3"

import os
# import sys             # The 'sys' and 'numpy' modules are not being used.
# import numpy as np

corner1 = [1,1,1] # corner1 = Corner of meshgrid (x1,y1,z1)
corner2 = [3,3,3] # corner2 = Opposite corner of meshgrid (x2,y2,z2)
numbElements = [2,2,2] # numElements = Number of x elements, y elements, and z elements, respectively.

import sys,argparse
parser = argparse.ArgumentParser(description='Generate nodes.txt and elements.txt files based on user inputs.')
parser.add_argument("--corner_1", help="One of the corners that defines the mesh.", default=corner1, nargs=3, type=int)
parser.add_argument("--corner_2", help="The seconds corner that defines the mesh.", default=corner2, nargs=3, type=int)
parser.add_argument("--numElements", help="The number of mesh elements in the x direction ,y direction, and z direction, respectively.", default=numbElements, nargs=3,type=int)
args = parser.parse_args()

corner_1 = args.corner_1
corner_2 = args.corner_2
numElements = args.numElements
print "corner_1:", corner_1 
print"numElements:", numElements

# Corner of meshgrid (x1,y1,z1)
x1 = corner_1[0]
y1 = corner_1[1]
z1 = corner_1[2]

# Opposite corner of meshgrid (x2,y2,z2)
x2 = corner_2[0]
y2 = corner_2[1]
z2 = corner_2[2]

# Number of x elements, y elements, and z elements, respectively.
xEle = numElements[0]
yEle = numElements[1]
zEle = numElements[2]

def main():
#    import sys, argparse
    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")
    
    node_counter()
    element_counter()
###############################################################################
def node_counter():  
    '''
    node_counter() returns a file, nodes.dyn, that defines the x, y, and z location
    of each node in the mesh using the following format:
    "nodeID"  "x"  "y"  "z"
    where each node is given a unique interger value nodeID and is defined by
    a unique set of coordinates (x,y,z).  The total number of rows in "nodes.dyn"
    is equal to the number of nodes in the mesh.
    '''
    Test1 = True # Define a boolean that runs the testing parameters when 'True'.
    fid = open('nodes.dyn','w+')
    for i in range(1,xEle+2):
        for j in range(1,yEle+2):
            for k in range(1,zEle+2):
                nodeID = (i-1)*((yEle+1)*(zEle+1))+(j-1)*(zEle+1)+k
                x = x1 + (i-1)*(x2-x1)/xEle
                y = y1 + (j-1)*(y2-y1)/yEle
                z = z1 + (k-1)*(z2-z1)/zEle
                fid.write("%i,%.2f,%.2f,%.2f\n" % (nodeID, x, y, z))
                print("%i %.2f %.2f %.2f\n" % (nodeID, x, y, z))

# Testing for node_counter is executed when Test1 = True.
                if Test1 == True:  
                    # CHECK 1: Make sure the nodeID is never greater than the total
                    #          number of nodes in the mesh.
                    if nodeID > (xEle+1)*(yEle+1)*(zEle+1): # CHECK #1
                        print "ERROR: Some nodeID values exceed the total number of nodes."  
                        break
                    # CHECK 2: Make sure that x, y, and z values are always within 
                    #          the range defined by corner1 and corner2.
                    if x<x1 or x>x2: # CHECK #2
                        print "ERROR: An 'x' value exists outside the expected range."
                        break
                    if y<y1 or y>y2:
                        print "ERROR: A 'y' value exists outside the expected range."
                        break
                    if z<z1 or z>z2:
                        print "ERROR: A 'z' value exists outside the expected range."
                        break
            else:
                continue
            break
        else:
            continue
        break
    #fid.split(None, -1)
    fid.close()

###############################################################################
def element_counter():   
    '''
    element_counter() returns a file, elements.dyn, that lists the 8 nodes that 
    define each elelent in the mesh using the following format:
    "elementID"  "part"  "n1"  "n2"  "n3"  "n4"  "n5"  "n6"  "n7"  "n8"
    where each element is given a unique interger value elementID and is defined by
    the 8 nodes that are positioned at the 8 unique corners of the element. In this
    script, "part" is always assumed to be equal to 1. "n1", "n2",..., "n8" are
    the nodeIDs of the 8 nodes that define the element, as characterized by nodes.dyn.
    The total number of rows in "elements.dyn" is equal to the number of elements in 
    the mesh.
    '''
    Test2 = True
    part = 1
    file2 = open('elements.dyn','w+')
    for i in range(1,xEle+1):
        for j in range(1,yEle+1):
            for k in range(1,zEle+1):
                elementID = (i-1)*(yEle*zEle) + (j-1)*zEle + k
                n1 = (i-1)*((yEle+1)*(zEle+1))+(j-1)*(zEle+1)+k
                n2 = n1+(zEle+1)
                n3 = n2+1
                n4 = n1+1
                n5 = n1+(yEle+1)*(zEle+1)
                n6 = n5+(zEle+1)
                n7 = n6+1
                n8 = n5+1
               
                file2.write("%i %i %i %i %i %i %i %i %i %i\n" % (elementID,part,n1,n2,n3,n4,n5,n6,n7,n8))
                print("%i %i %i %i %i %i %i %i %i %i" % (elementID,part,n1,n2,n3,n4,n5,n6,n7,n8))

nodeID = (i-1)*((yEle+1)*(zEle+1))+(j-1)*(zEle+1)+k
                x = x1 + (i-1)*(x2-x1)/xEle
                y = y1 + (j-1)*(y2-y1)/yEle
                z = z1 + (k-1)*(z2-z1)/zEle

# Testing for node_counter is executed when Test2 = True.
                if Test2 == True:  
                    # CHECK 1: Make sure the elementID is never greater than the total
                    #          number of elements in the mesh.
                    if elementID > xEle*yEle*zEle: # CHECK #1
                        print "ERROR: Some elementID values exceed the total number of elements."  
                        break
                    # CHECK 2 (could be added later):Check to see that for any element
                    #         there are only two discrete valeus for x, y, and z.
            else:
                continue
            break
        else:
            continue
        break

    file2.close()
  
###############################################################################          

if __name__ == "__main__":
    main()