#!/usr/bin/perl -w
# BoundCond - Assign boundary conditions to the structural dyna
# models.  Fully contrained top (transducer) and bottom
# surfances with symmetry contraints along the axial-lateral
# face centered in elevation (assumed at x = 0).  This script
# was ported over from bc.m to be more efficient when working
# with large meshes.  (matlab - 8 sec, perl - 4 sec)
#
# INPUTS:
# NodeName (string) - file containing *NODE data (and only *NODE data);
#                     one of the files created using ParseElemsNodes
# zmin (float) - depth of the bottom surface (assuming negative
#                z-axis) in units the mesh was built in
# zmax (float) - location of the top surface (usually 0)
# nodespc (float) - spacing b/w nodes to determine a search
#                   tolerance for the surfances being searched for 
#                   (mesh units again)
# OUTPUT:
# bc.dyn (ASCII format) is written.  This can be directly read
# into the master dyna deck for the *BOUNDAY_SPC_NODE card.
#
# Mark 05/13/05


# check that the correct number of input arguments are
# provided (4)
if(($#ARGV+1) != 4) { die "Wrong number of input arguments (!=4)" }

$zmin = "$ARGV[1]";
$zmax = "$ARGV[2]";
$nodespc = "$ARGV[3]";

# open up the file with the nodal information
open(NODEFILE,"<$ARGV[0]") || die "The input file couldn't be opened!";

# check to make sure that bc.dyn doesn't already exist so that
# we don't clobber a valid file; if it doesn't exist, then
# create the output file
if (-e 'bc.dyn') { 
	die "bc.dyn already exists!" 
	}
else {
	open(BCFILE,'> bc.dyn');	
	print BCFILE "*BOUNDARY_SPC_NODE\n";
	}

while(<NODEFILE>) {
	# remove the EOL character
	chomp;

	# split the line into data fields with spaces as the
	# delimiting character	
	@fields = split(' ',$_);

	# the actual node IDs and coordinates occupy 4 columns (the
	# header and footer are only a single column)
	if( ($#fields + 1) == 4) {
		
		# check to see if the node fall on the top or bottom
		# surface
		if($fields[3] < ($zmin + $nodespc/2) || $fields[3] > ($zmax - $nodespc/2)) {
			# if it does, then make the node fully contrained
			print BCFILE "$fields[0],0,1,1,1,1,1,1\n";
			}

		# if it isn't on the top/bottom, then check if it is on the
		# symmetry plane
		elsif ($fields[1] > -$nodespc/2) {
			print BCFILE "$fields[0],0,1,0,0,0,1,1\n";
			}
	}
}

close(NODEFILE);

# print the footer and close bc.dyn
print BCFILE "*END\n";
close(BCFILE);

