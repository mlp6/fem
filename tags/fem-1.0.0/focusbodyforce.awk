#! /bin/awk -f
#
# focusbodyforce.awk - grab subset of node IDs from a dyna deck for applying
# node loads in a conical shape; then apply an appropriate body force
# based on the number of nodes grabbed and volume of cone; force is directed 
# towards the focus
#
# modified to not assume focus @ (0,0,0)
#
# based on bodyforce.awk script
#
# assuming a 1/4 mesh c z-axis symmetry, c nodes in +x +y quadrant
# $0 = entire line, $1 = node ID, $2 = x-coord, $3 = y-coord, $4 = z-coord
#
# command line:
# ./focusbodyforce.awk -v bf=# inputfile.dyn
# bf - body force value
#
# output file "fbf.asc" is created
#
# mark 02/08/02
# modified 02/11/02
# 

# initialized variables
# trigger - execute conditions only when appropriate
# bigrad - large radius of the cone
# smallrad - small radius of the cone
# zstart - where to start cone along z-axis
# zstop - where to stop cone along z-axis
# ?trig - trigger to start node ID collection for respective dimension
# ?tol - tolerance for node selection for respective dimension
# radtol - tolerance for the radius measurement

BEGIN { trigger = 0;
	bigrad = 0.06;
	smallrad = 0.02;
	zstart = 0;
	zstop = 0.4;
	ztrig = 0;
	xtrig = 0;
	ytrig = 0;
	ztol = 0.001;
	xtol = 0.001;
	ytol = 0.001;
	radtol = 0.001;
	nodecount = 0;
	done = 0; 		# remains 1 after nodes are grabbed
	}

{

### only process data in the NODE card of the input deck ###
if ($1 == "*NODE")
	{
	trigger = 1;
	done = 1;
	}
if ($1 == "*MAT_ELASTIC")
	trigger = 0;
###

# select nodes in the conical region defined by the initialzed parameters
#
# NF condition is to insure that 4 columns of data are being processed
# providing a further check that the correct input is being processed

if (trigger == 1 && NF == 4)
	{
	# set boundaries in z
	if ($4 > (zstart - ztol) && $4 < (zstop + ztol))
		{
		# compute radius as a function of z
		# radius = (((bigrad - smallrad)/(zstop-zstart)) * $4 + smallrad)
		radius = (((bigrad - smallrad)/(zstop-zstart)) * $4 + smallrad-((bigrad - smallrad)/(zstop-zstart))*zstart)
		# select nodes w/i radius for z
		if (sqrt($2^2 + $3^2) < (radius + radtol))
			{
			# create an array of node IDs
			nodecount++;
			loadarray[nodecount]=$1;
			xcoord[nodecount]=$2;
			ycoord[nodecount]=$3;
			zcoord[nodecount]=$4;
			}
		}
	}

if (trigger == 0 && done == 1)
	{
	done = 0; 	# only need to execute this loop once
	# A and B are intergration coefficients
	A = ((bigrad-smallrad)/(zstop-zstart));
	B = smallrad - zstart * A;
	volume = 3.414 * (A*A*bigrad*bigrad*bigrad/3 + A*B*bigrad*bigrad + B*B*bigrad - A*A*smallrad*smallrad*smallrad/3 - A*B*smallrad*smallrad - B*B*smallrad);
	# negative to have force vectors point towards focus
	nodeload = -volume * bf / nodecount;	
	# modification to calculate where to focus of the cone is
	m = ((bigrad-smallrad)/(zstop-zstart));
	deltaz = smallrad/m;
	zfocus = zstart - deltaz;
	for(i=1;i<=nodecount;i++)
		{
		# for each node, need to calculate unit vector and then 
		# multiply that by the appropriate node body force
		magnitude = sqrt(xcoord[i]*xcoord[i]+ycoord[i]*ycoord[i]+(zcoord[i]-zfocus)*(zcoord[i]-zfocus));
		# what to do with node at focus
		if(magnitude == 0)
			{
			printf("%s,3,1,%s,0\n",loadarray[i],nodeload) > "fbf.asc"
			continue;
			}
		# all other nodes
		# x-coordinate of force
		xforce = (xcoord[i]/magnitude)*nodeload;
		printf("%s,1,1,%2.2s,0\n",loadarray[i],xforce) > "fbf.asc"
		# y-coordinate of force
		yforce = (ycoord[i]/magnitude)*nodeload;
		printf("%s,2,1,%2.2s,0\n",loadarray[i],yforce) > "fbf.asc"
		# z-coordinate of force
		zforce = ((zcoord[i]-zfocus)/magnitude)*nodeload;
		printf("%s,3,1,%2.2s,0\n",loadarray[i],zforce) > "fbf.asc"
		}
	}
}	
