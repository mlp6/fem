#!/usr/bin/perl -w
###################################################################
# 
# CreateLesion1.1.pl - changed from the inefficient LN ("Lesion
# Node") lookup array to a hash lookup.  Uses 1/100 of the RAM
# v1.0 uses (200K vs. 200 MB), and it is faster (9.5 vs. 14
# seconds for cirs.dyn model).
#
# Mark 02/16/06
#
###################################################################
#
# CreateLesion1.0.pl - determine the elements that fall w/i a
# specfied radius of a center point, and assign them different
# material properties than the background material
#
# INPUTS:
#	NodeFile (string) - file containing the *NODE information
#	(generated by ParseElemsNodes)
# ElemFile (string) - file containing the *ELEMENT_SOLID
# information (generated by ParseElemsNodes)
# CenterX (float) - x-coordinate of center point (mesh units)
# CenterY (float) - y-coordinate of center point (mesh units)
# CenterZ (float) - z-coordinate of center point (mesh units)
# Radius (float) - radius of sphere (mesh units)
#
# OUTPUT:
# lesion.dyn - ASCII file with the new *ELEMENT_SOLID data
# sphere elements are assigned part #2, while background is
# part #1
#
# Mark 05/13/05
#
###################################################################

# check that the correct number of input arguments are
# provided (6)
if(($#ARGV+1) != 6) { die "Wrong number of input arguments (!=6)" }

$CenterX = "$ARGV[2]";
$CenterY = "$ARGV[3]";
$CenterZ = "$ARGV[4]";
$Radius = "$ARGV[5]";

# open up the files with the nodal and element information
open(NODEFILE,"<$ARGV[0]") || die "The node input file couldn't be opened!";
open(ELEMFILE,"<$ARGV[1]") || die "The element input file couldn't be opened!";

# check to make sure that lesion.dyn doesn't already exist so
# that we don't clobber a valid file; if it doesn't exist, then
# create the output file
if (-e 'lesion.dyn') {
  die "lesion.dyn already exists!"
  }
else {
  open(LESIONFILE,'> lesion.dyn');
  print LESIONFILE "*ELEMENT_SOLID\n";
  }

# read in the nodes and see which ones fall within the sphere
# that has been specfied by the user
print "Reading and processing node data\n";
# initialize the index of lesion nodes found to 0
$NodeCount = 0;
#$LN_count = 0;

# phased out from v1.0 -> v1.1 b/c waste of memory and
# comparitive logic below
# initialize the @LN array
#for ($i = 0; $i < 9999999; ++$i) {
#	$LN[$i] = 0;
#}

while(<NODEFILE>) {
	# remove the EOL character
  chomp;

  # split the line into data fields with spaces as the
  # delimiting character  
  @fields = split(',',$_);

  # the actual node IDs and coordinates occupy 4 columns (the
  # header and footer are only a single column)
  if( ($#fields + 1) == 4) {
		$NodeCount = ++$NodeCount;
		$NodeRadius = sqrt(($fields[1] - $CenterX)**2 + ($fields[2] - $CenterY)**2 + ($fields[3] - $CenterZ)**2);
		if($NodeRadius < $Radius) {
			$hash{$fields[0]}++;
			#$LN[$fields[0]] = 1;
		}
	}
}

#open(KEYS,'>keys.out');
@keys = keys %hash;
$size = @keys;
#while ($#keys >= 0) { print KEYS pop(@keys),"\n"; }
#close(KEYS);

print $size." lesion nodes found out of ".$NodeCount." total nodes\n"; 

close(NODEFILE);

print "Check the delimiting character (,) for the element data!\n";

# see chop command in the while loop below
#print "\nWARNING - chopping off space from last node entry for each element!!
#If this space doesn't exist, then the node ID will be corrupted,
#but without any error!!\n\n";

$elcount = 0;
while(<ELEMFILE>) {
  # remove the EOL character
  chomp;

	# split the line into data fields with commas or spaces as
	# the delimiting character  
  @fields = split(',',$_);
  #@fields = split(' ',$_);

  # the element ID and part ID are the first two columns; the
  # following 8 are the nodes associated with that element
  if( ($#fields + 1) == 10) {

		# the last field has an erroneous space added to it; so we
		# have to chop it off!!
		#chop $fields[9];

		# check to see if any of the nodes for this element match
		# the nodes that are in the lesion 
		# if so, change the part ID -> 2
		if(exists $hash{$fields[2]} || 
			 exists $hash{$fields[3]} || 
		   exists $hash{$fields[4]} || 
			 exists $hash{$fields[5]} || 
			 exists $hash{$fields[6]} || 
			 exists $hash{$fields[7]} || 
			 exists $hash{$fields[8]} || 
			 exists $hash{$fields[9]}) {
				$fields[1] = 2;
				print LESIONFILE join(",",@fields)."\n";
				$elcount = ++$elcount;
		}
		else {
			$fields[1] = 1;
			print LESIONFILE join(",",@fields)."\n";
		}
  }
}

close(ELEMFILE);

print "$elcount elements converted from part ID 1 -> 2\n";

# print the footer and close lesion.dyn
print LESIONFILE "*END\n";
close(LESIONFILE);

print "Done writing element data to lesion.dyn\n";