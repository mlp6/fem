#!/usr/bin/perl
# matlabRun.pl - run matlab sims for different seeds
#
# INPUTS: Command line integers [representing the seed(s)]
# OUTPUT: Creates run scripts containing the node name & seed number; and 
#         matlab output files with the same prefixes
#
# Example: matlabRun.pl 1 2 3 4
#
# Mark 03/08/07

use strict;
use warnings;

my $node = `hostname -s`;
chomp($node);
my $cwd = `pwd`;
chomp($cwd);

for (my $i = 0; $i <= $#ARGV; ++$i) {
    my $RunFile = "$node$ARGV[$i]"; 
    open(MATRUN,"> $RunFile.m");
    print MATRUN "arfiscans($ARGV[$i],'$cwd/');\n";
    print MATRUN "system(\"mail -s \'$RunFile\' mlp6\@philip.egr.duke.edu < $RunFile.m\");";
    close(MATRUN);     
    system("nice -n 19 matlab -nojvm -nosplash -glnx86 < $RunFile.m > $RunFile.out 2>&1 &");
}
