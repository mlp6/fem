=head1 FEM Perl Module

This is a Perl module that contains functions for pre- and post-processing FEM models.  These functions were originally cut & pasted into a variety of scripts, but they are now being consolidated into a portable module.  

Mark 05/22/07

=cut

package fem;
use strict;

our (@ISA, @EXPORT, @EXPORT_OK, $VERSION);

use Exporter;
$VERSION = 1.0.0;
@ISA = qw(Exporter);

@EXPORT = qw(readNodeCoords);
@EXPORT_OK = qw();

=head2 readNodeCoords($nodeFileName)

Create a hash of node IDs associated with x, y, and z coordinates.  This
function assumes (for now) that the node data provide in the definitions file
is comma-delimited.  Lines with > 4 fields are ignored.    

=cut


sub readNodeCoords {

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

=head2 stripHeaders($prefix,$suffix)

Strip headers (and footers) from otherwise space-delimited xy pair data (as
typically saved by ls-prepost2).  $prefix represents the common part of each
file name with a $suffix file extension (e.g., n#.asc -> $prefix = 'n',
$suffix = 'asc').  The original files are not preserved.

=cut


sub stripHeaders {
    my $prefix = $_[0];
    my $suffix = $_[1];
    our @files = <$prefix*.$suffix>;

    foreach my $file (@files) {
        print "Stripping the header of $file\n";

        # open the original file
        open(FILE,"<$file") || die "Cannot open $file";

        # spit the headerless data into a temp file
        open(TEMPFILE, ">$file.temp");

        while (<FILE>) {
            chomp;
            our @fields = split(' ',$_);
            if ($#fields == 1) {
                print TEMPFILE $_,"\n";
            }
        }

        close(FILE);
        close(TEMPFILE);

        # replace the original file with the temp file
        system("mv $file.temp $file");
    }

}
1;
