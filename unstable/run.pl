#!/usr/bin/perl
# run.pl - run an ls-dyna-s job using lamexec
# INPUTS:   $dyna_deck (string) - name of the dyna deck
#           $precision (char)   - precision to invoke
#                               - s: single
#                               - d: double
#           $ncpu (int)         - number of cpus to utilize
#
# OUTPUTS: None
#
# EXAMPLE: (lamexec np1 -w -D /path/run.pl > /path/run.out 2>&1 &)
#
# Mark 06/11/07

use strict;
use warnings;

my $dyna_deck = $ARGV[0];
my $precision = $ARGV[1];
my $ncpu = $ARGV[2];
my $node = $ENV{'HOSTNAME'};
my $pwd = $ENV{'PWD'};

system("ls-dyna-$precision ncpu=$ncpu i=$dyna_deck");

open(MAILBODY,">mailbody");
print MAILBODY "$node\n";
print MAILBODY "$pwd\n";
close(MAILBODY);
system("mail -s \'$dyna_deck\' mark.palmeri\@duke.edu < mailbody");
unlink('mailbody');
