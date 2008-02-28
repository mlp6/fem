#! /usr/bin/perl 
# split the elements and nodes created by ls-prepost2 into two
# separate files (elems.dyn and nodes.dyn)
#
# USAGE:  ParseElemsNodes < PrePostFile
#
# Mark 05/04/05
#
# Mod Hx
#
# Changed the field separation character from spaces -> commas
# in the output files (Mark 08/08/05)
# 
# Mark Palmeri
# Deparment of Biomedical Engineering
# Pratt School of Engineering
# Duke University

# check to make sure that you aren't going to clobber a
# pre-existing file
if(-e 'elems.dyn') {die "elems.dyn already exists" }
if(-e 'nodes.dyn') {die "nodes.dyn already exists" }

# open file handles for the element and node files
open(ELEMFILE,'> elems.dyn');
open(NODEFILE,'> nodes.dyn');
open(NODEASC,'> nodes.asc');

# print the header for each file
print ELEMFILE "*ELEMENT_SOLID\n";
print NODEFILE "*NODE\n";

while(<>)
	{
	# remove the EOL characters from each line
  chomp;

	# split up each line into columns delimited by spaces
  @fields = split(' ',$_);

	# split the field entries using commas in the output file
	$printout = join ",", @fields;

	# node entries will have 4 entries per line, while element
	# entries will have 10 entries per line
  if( ($#fields + 1) == 4)
		{
		#print NODEFILE "@fields\n"; 
		print NODEFILE "$printout\n"; 
		print NODEASC "$printout\n"; 
		}
	elsif( ($#fields + 1) == 10)
		{
		print ELEMFILE "$printout\n";
		}
	}

# print to footer for each file
print ELEMFILE "*END\n";
print NODEFILE "*END\n";

# close the file handles
close(ELEMFILE);
close(NODEFILE);
close(NODEASC);
