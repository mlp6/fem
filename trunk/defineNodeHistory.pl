#!/usr/bin/perl -w
# defineNodeHistory.pl - define LS-DYNA node set for output
#
# INPUTS: None (but variables are set below)
#
# OUTPUT:
# node_history.dyn (ASCII format) is written.  This can be directly read into
# the master dyna deck for the *DATABASE_HISTORY_NODE card.
#
# Mark 05/11/07

$depth = 1.5; # cm
$SearchTol = 0.0001; # spatial tolerance to search for nodal locations (cm)
$x_sym_face = 0;  # coordinate of the elevation symmetry face

# open up the file with the nodal information
open(NODEFILE,"<sw_nodes.dyn") || die "The input file couldn't be opened!";

# check to make sure that gauss_excitation.dyn doesn't already
# exist so that we don't clobber a valid file; if it doesn't
# exist, then create the output file
if (-e 'node_history.dyn') { 
    die "node_history.dyn already exists!" 
}
else {
    open(EXCFILE,'> node_history.dyn');	
    print EXCFILE "*DATABASE_HISTORY_NODE\n";
}

while(<NODEFILE>) {
    # remove the EOL character
    chomp;

    # split the line into data fields with spaces as the
    # delimiting character	
    @fields = split(',',$_);

    # the actual node IDs and coordinates occupy 4 columns (the
    # header and footer are only a single column)
    if( ($#fields + 1) == 4) {
            
        # find the nodes at the specified depth (and elevation symmetry plane)
        if(abs($fields[1]-$x_sym_face) < $SearchTol && abs(abs($fields[3])- $depth) < $SearchTol) {
                print EXCFILE "$fields[0]\n";
        }

    }
}

close(NODEFILE);

# print the footer and close the output file 
print EXCFILE "*END\n";
close(EXCFILE);
