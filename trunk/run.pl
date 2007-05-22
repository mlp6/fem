#!/usr/bin/perl

use strict;
use warnings;

my $dyna_deck = $ARGV[0];
my $node = $ENV{'HOSTNAME'};
my $pwd = $ENV{'PWD'};

system("ls-dyna ncpu=4 i=$dyna_deck");

open(MAILBODY,">mailbody");
print MAILBODY "$node\n";
print MAILBODY "$pwd\n";
close(MAILBODY);
system("mail -s \'$dyna_deck\' mark.palmeri\@duke.edu < mailbody");
unlink('mailbody');
