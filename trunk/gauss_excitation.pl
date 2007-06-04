#!/usr/bin/perl -w
# gauss_excitation.pl - define an axisymmetric Gaussian s/w excitation to do
# shear wave reconstructions on excitations with known (simple) geometries
#
# INPUTS: None (but variables are set below)
#
# OUTPUT:
# gauss_excitation.dyn (ASCII format) is written.  This can be directly read
# into the master dyna deck for the *LOAD_NODE_POINT card.
#
# Mark 07/26/06

# assuming that the center of the excitation is at (0,0)
$sigma_x = 0.1; # s.d. (cm)
$sigma_y = 0.2;  # s.d. (cm)
$A = 1;  # Gaussian amplitude (this can be scaled by the load curve)
$Amin = 0.05; # amplitude threshold to stop creating point loads 
$zmax = -1.0; # "top" of the push (cm)
$zmin = -2.0; # "bottom" of the push (cm)
$SearchTol = 0.0001; # spatial tolerance to search for nodal locations (cm)

# open up the file with the nodal information
open(NODEFILE,"<sw_nodes.dyn") || die "The input file couldn't be opened!";

# check to make sure that gauss_excitation.dyn doesn't already
# exist so that we don't clobber a valid file; if it doesn't
# exist, then create the output file
if (-e 'gauss_excitation.dyn') { 
    die "gauss_excitation.dyn already exists!" 
}
else {
    open(EXCFILE,'> gauss_excitation.dyn');	
    print EXCFILE "\$ -------------------------------\n";
    print EXCFILE "\$ gauss_excitation.pl parameters\n";
    print EXCFILE "\$ zmin = $zmin\n";
    print EXCFILE "\$ zmax = $zmax\n";
    print EXCFILE "\$ sigma_x = $sigma_x\n";
    print EXCFILE "\$ sigma_y = $sigma_y\n";
    print EXCFILE "\$ A = $A\n";
    print EXCFILE "\$ Amin = $Amin\n";
    print EXCFILE "\$ -------------------------------\n";
    print EXCFILE "*LOAD_NODE_POINT\n";
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
            
        # compute the amplitude of the Gaussian function at the node
        $nodeA = $A * exp( -(($fields[1]/$sigma_x)**2 + ($fields[2]/$sigma_y)**2));
        # precision needs to be limited by constraints of ls-dyna
        $nodeA = sprintf "%.4f", $nodeA;
    
        # check to see if the node amplitude is greater than the min threshold
        if($nodeA > $Amin && $fields[3] <= $zmax && $fields[3] >= $zmin) {
            # if the nodes are on the symmetry edge, then cut the
            # magnitude by 1/4
            if(abs($fields[1]) < $SearchTol && abs($fields[2]) < $SearchTol) {
                $nodeA = $nodeA/4;
                print EXCFILE "$fields[0],3,1,$nodeA,0\n";
            }
            # if the node aren't on the edge, but are on the symmetry
            # plane, then cut the magnitude by 1/2
            elsif(abs($fields[1]) < $SearchTol || abs($fields[2]) < $SearchTol) {
                $nodeA = $nodeA/2;
                print EXCFILE "$fields[0],3,1,$nodeA,0\n";
            }
            else {
                print EXCFILE "$fields[0],3,1,$nodeA,0\n";
            }
        }
    }
}

close(NODEFILE);

# print the footer and close bc.dyn
print EXCFILE "*END\n";
close(EXCFILE);
