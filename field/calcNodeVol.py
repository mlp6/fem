import math
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Creates node volume file from nodes.dyn and elems.dyn, specified on the command-line.')
parser.add_argument("--nodefile", dest="nodefile", help = "node definition input file", default="nodes.dyn")
parser.add_argument("--elefile", dest="elefile", help = "element definition input file", default="elems.dyn")
parser.add_argument("--nodevolfile", dest="nodevolfile", help = "name of output node volume file", default="NodeVolume.txt")

args = parser.parse_args()
nodeFile = open(args.nodefile, 'r')
elemFile = open(args.elefile, 'r');

NCdict = {}

for line in nodeFile:
    if not(line.startswith("*")):
    	line = line.rstrip()
    	node = line.split(',')
    	NCdict[node[0]]=node

elemVolDict = {}
for i in elemFile:
    if not(i.startswith("*")):
    	i = i.rstrip()
   	line = i.split(',')
   	element = line[0];
   	nodes = line[2:]
    
    	node1 = NCdict[nodes[0]]
    	node2 = NCdict[nodes[1]]
    	node3 = NCdict[nodes[2]]
    	node4 = NCdict[nodes[3]]
    	node5 = NCdict[nodes[4]]
    	node6 = NCdict[nodes[5]]
    	node7 = NCdict[nodes[6]]
    	node8 = NCdict[nodes[7]]

	# The three pyramids will have bases constructed from nodes: 1,2,3,4; nodes: 1,5,6,2; nodes: 2,6,7,3; The apex of each pyramid will be the 8th node

			
	#Convert all my coordinates from strings to floats

    	x1,x2,x3,x4,x5,x6,x7,x8 = float(node1[1]), float(node2[1]),float(node3[1]), float(node4[1]), float(node5[1]), float(node6[1]), float(node7[1]), float(node8[1])
    	y1,y2,y3,y4,y5,y6,y7,y8 = float(node1[2]), float(node2[2]),float(node3[2]), float(node4[2]), float(node5[2]), float(node6[2]), float(node7[2]), float(node8[2])
    	z1,z2,z3,z4,z5,z6,z7,z8 = float(node1[3]), float(node2[3]),float(node3[3]), float(node4[3]), float(node5[3]), float(node6[3]), float(node7[3]), float(node8[3])

	#Calculate the area of the three bases assuming planar, arbitrary quadrilaterals

	#Base 1

    	a = math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)	#Four Sides
    	b = math.sqrt((x2-x3)**2+(y2-y3)**2+(z2-z3)**2)
    	c = math.sqrt((x3-x4)**2+(y3-y4)**2+(z3-z4)**2)
    	d = math.sqrt((x4-x1)**2+(y4-y1)**2+(z4-z1)**2)
    	p = math.sqrt((x1-x3)**2+(y1-y3)**2+(z1-z3)**2)	#Diagonals
    	q = math.sqrt((x4-x2)**2+(y4-y2)**2+(z4-z2)**2)
		
    	s = (a+b+c+d)/2
		
    	Area1 = math.sqrt((s-a)*(s-b)*(s-c)*(s-d)-0.25*(a*c+b*d+p*q)*(a*c+b*d-p*q))
		
	#Base 2

    	a = math.sqrt((x1-x5)**2+(y1-y5)**2+(z1-z5)**2)	#Four Sides
    	b = math.sqrt((x5-x6)**2+(y5-y6)**2+(z5-z6)**2)
    	c = math.sqrt((x6-x2)**2+(y6-y2)**2+(z6-z2)**2)
    	d = math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
    	p = math.sqrt((x1-x6)**2+(y1-y6)**2+(z1-z6)**2)	#Diagonals
    	q = math.sqrt((x2-x5)**2+(y2-y5)**2+(z2-z5)**2)
        
    	s = (a+b+c+d)/2
        
    	Area2 = math.sqrt((s-a)*(s-b)*(s-c)*(s-d)-0.25*(a*c+b*d+p*q)*(a*c+b*d-p*q))		
	#Base 3

    	a = math.sqrt((x2-x6)**2+(y2-y6)**2+(z2-z6)**2)	#Four Sides
   	b = math.sqrt((x6-x7)**2+(y6-y7)**2+(z6-z7)**2)
    	c = math.sqrt((x7-x3)**2+(y7-y3)**2+(z7-z3)**2)
    	d = math.sqrt((x3-x2)**2+(y3-y2)**2+(z3-z2)**2)
    	p = math.sqrt((x2-x7)**2+(y2-y7)**2+(z2-z7)**2)	#Diagonals
    	q = math.sqrt((x3-x6)**2+(y3-y6)**2+(z3-z6)**2)
		
    	s = (a+b+c+d)/2
		
    	Area3 = math.sqrt((s-a)*(s-b)*(s-c)*(s-d)-0.25*(a*c+b*d+p*q)*(a*c+b*d-p*q))
		
	#Now, we've calculated bases for each of the three pyramids and need to find the distance the 8th node is from the plane made by the bases, Planes: 1,4,2; 1,2,5; 2,3,6

	#Define 2 vectors on the plane of each base:

	#Base 1 Vectors to get plane equation:    Ax+By+Cz+D=0 

    	AB = np.array([(x4-x1),(y4-y1),(z4-z1)])	#Vector 1
    	AC = np.array([(x2-x1),(y2-y1),(z2-z1)])	#Vector 2
    	normal1 = np.cross(AB,AC)				#Cross product vector 1 x vector 2
    	Q,R,S = normal1[0],normal1[1],normal1[2]	#Normal Vector to plane: (Ai,Bj,Ck)
		
    	D = -Q*x1-R*y1-S*z1		#Constant component of plane equation
		
    	H1 = abs((Q*x8+R*y8+S*z8+D)/(math.sqrt(Q**2+R**2+S**2))) #Distance to apex of pyramid
		
    	Volume1 = Area1*H1/3.0		#Volume of pyramid 1
		
	#Base 2 Vectors to get plane equation:    Ax+By+Cz+D=0 

    	AB = np.array([(x2-x1),(y2-y1),(z2-z1)])	#Vector 1
    	AC = np.array([(x5-x1),(y5-y1),(z5-z1)])	#Vector 2
    	normal1 = np.cross(AB,AC)				#Cross product vector 1 x vector 2

    	Q,R,S = normal1[0],normal1[1],normal1[2]	#Normal Vector to plane: (Ai,Bj,Ck)
		
    	D = -Q*x1-R*y1-S*z1		#Constant component of plane equation
		
    	H2 = abs((Q*x8+R*y8+S*z8+D)/(math.sqrt(Q**2+R**2+S**2))) #Distance to apex of pyramid
		
    	Volume2 = Area2*H2/3.0		#Volume of pyramid 2
		
	#Base 3 Vectors to get plane equation:    Ax+By+Cz+D=0 

    	AB = np.array([(x3-x2),(y3-y2),(z3-z2)])	#Vector 1
    	AC = np.array([(x6-x2),(y6-y2),(z6-z2)])	#Vector 2
    	normal1 = np.cross(AB,AC)				#Cross product vector 1 x vector 2

    	Q,R,S = normal1[0],normal1[1],normal1[2]	#Normal Vector to plane: (Ai,Bj,Ck)
		
    	D = -Q*x2-R*y2-S*z2		#Constant component of plane equation
		
    	H3 = abs((Q*x8+R*y8+S*z8+D)/(math.sqrt(Q**2+R**2+S**2))) #Distance to apex of pyramid
		
    	Volume3 = Area3*H3/3.0		#Volume of pyramid 3
		
    	# Sum the volumes of the three pyramids to get the volume of the element
    	# Add element and its volume to a element to volume map
    	elemVolDict[element] = Volume1+Volume2+Volume3
    	#print element

Nodedict = {}
elemFile.seek(0,0) # return to start of elements file
nodeFile.seek(0,0) # return to start of nodes file
for line in elemFile:
    if not(line.startswith("*")):
    	line = line.strip()
    	EN = line.split(',')
    	for i in range(2, 10):
        	if EN[i] in Nodedict:
            		tempList = Nodedict[EN[i]]
            		tempList.append(EN[0])
            		Nodedict[EN[i]] = tempList
        	else:
            		tempList = []
            		tempList.append(EN[0])
            		Nodedict[EN[i]] = tempList

nodeElemDict = {}
for node in nodeFile:
    if not(node.startswith("*")):
    	nodeelem = []			#makes an empty list
    	node = node.rstrip()
    	node = node.split(',')
    	nodeelem.insert(0,node[0])		#Defines first part of new array as the node ID
		#node = [' %s ' % node[0]]		#Defines nodes independently so we don't pick up internal values and can't be the first value because of the leading comma
			#Adds the element to the list for that particular node
    	if node[0] in Nodedict:
        	nodeelem = nodeelem + Nodedict[node[0]]
	nodeElemDict[int(node[0])] = nodeelem

NODEVOLUME = open(args.nodevolfile,'w') #creates a new file to post our node volumes to

#for node in sorted(nodeElemDict.iterkeys()):
for node in nodeElemDict:
    nodeelem = nodeElemDict[node]
    numberelements = len(nodeelem) - 1
    if numberelements > 0:
        NODEVOLUME.write('%s ' % nodeelem[0])  #Writes the node number to a new file
        Volumes = []
        while numberelements>0:
            Volumes.append(elemVolDict[nodeelem[numberelements]])   #Appends all the element volumes to a list based on their dictionary volumes
            numberelements = numberelements -1	 
        average = sum(Volumes)/len(Volumes)			#Calculates average volume around a node
        NODEVOLUME.write('%s \n' % average)		#writes the average volume to the node volume file and returns
    else:
        print("No Volume Data for Node: %s" % nodeelem[0])
NODEVOLUME.close()
nodeFile.close()
elemFile.close()
