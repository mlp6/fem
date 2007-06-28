#!/usr/bin/perl
# zdispFocDepth.pl - extract the node z-disp histories along an output line into
# individual ASCII files to be read into a post-processor.  ls-prepost2 is used
# to extract the data from d3plot files since node history data is in different
# formats when run using ls-dyna vs. mpp-dyna
#
# INPUTS: None (but run-time variables are defined below)
# OUTPUTS: zdispData directory is created with individual ASCII files named by
#   nodes ID (e.g., n######zdisp.asc); these files have two columns of data 
#   (time & z displacement) in the units of the simulation
#
# Mark 05/21/07

use warnings;
use strict;
use fem;

# define parameters for the data extraction
my $depth = -1.5; # cm
my $SearchTol = 0.0001; # spatial search tolerance
my $x_face = 0; # x-coordinate to find the face of interest
my $nodeFileName = 'sw_nodes.dyn';
my $outputDir = 'zdispFocDepth';

# make sure that d3plot files exist before doing anything else
if (-e 'd3plot' == 0) { die "d3plot files are not present in the CWD"; }

# create the ASCII output directory
if (-e "$outputDir") { die "$outputDir directory already exists"; }
else { system("mkdir $outputDir"); }

our %nodeCoords = fem::readNodeCoords($nodeFileName);
my @nodeIDs = keys %nodeCoords;

# how many node IDs have to be processed
my $numNodeIDs = $#nodeIDs + 1;

# create a hash of the output nodes (not sorted yet)
foreach our $nodeID (@nodeIDs) {
    our %outputNodes; 
    if (abs($nodeCoords{$nodeID}[0] - $x_face) < $SearchTol && abs($nodeCoords{$nodeID}[2] - $depth) < $SearchTol) {
        $outputNodes{$nodeID} = $nodeCoords{$nodeID}[1];
    }
}

my @outNodes = keys our %outputNodes;
my $numOutNodes = $#outNodes + 1;
print "$numOutNodes of $numNodeIDs nodes are being output\n";

# sort output nodes by increasing y-coordinate
my @sortedOutNodes = sort { $outputNodes{$a} cmp $outputNodes{$b} } keys %outputNodes;

# create the lookup table and ls-prepost2 command file
open(LOOKUP,">$outputDir/zdispDataNodes.asc") || die "zdispDataNodes.asc cannot be created";
open(CFILE,">$outputDir.cfile") || die "$outputDir.cfile cannot be created";
print CFILE "openc d3plot \"d3plot\"\n";
print CFILE "ntime 7 @sortedOutNodes\n";
for my $nodeCount ( 0 .. $#sortedOutNodes ) {
    my $nodeCount_p1 = $nodeCount + 1;
    print LOOKUP "$sortedOutNodes[$nodeCount],$outputNodes{$sortedOutNodes[$nodeCount]}\n";
    print CFILE "xyplot 1 savefile xypair \"$outputDir/n$sortedOutNodes[$nodeCount].asc\" 1 $nodeCount_p1\n";
}
close(LOOKUP);
close(CFILE);

# run ls-prepost2
system("ls-prepost2 -nographics c=$outputDir.cfile");

# strip the lone header line on each output ASCII file to be read into a post-processing program
my $prefix = "$outputDir/n";
my $suffix = "asc";
fem::stripHeaders($prefix,$suffix);
