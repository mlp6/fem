package fem;
use strict;

our (@ISA, @EXPORT, @EXPORT_OK, $VERSION);

use Exporter;
$VERSION = 1.0.0;
@ISA = qw(Exporter);

@EXPORT = qw(readNodesCoords);
@EXPORT_OK = qw();

my $name = $ARGV;


sub readNodesCoords {
    my $nodeFileName = $_[0];
    open(NODEFILE, "< $nodeFileName") || die "The node definition file cannot be opened.";
    our %nodeCoords;
    while(<NODEFILE>) {
        # remove the EOL character
        chomp;

        # split the line into data fields with commas as the delimiting
        # character      
        my @fields = split(',',$_);

        # the actual node IDs and coordinates occupy 4 columns (the
        # header and footer are only a single column)
        # nodeID,x-coord,y-coord,z-coord
        if( ($#fields + 1) == 4) {
            # create a hash of node IDs with the spatial coordinates
            $nodeCoords{$fields[0]} = [ $fields[1], $fields[2], $fields[3] ];
        }
    }

    return %nodeCoords;
}

1;
