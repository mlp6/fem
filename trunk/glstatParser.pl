#!/usr/bin/perl
# glstatParser.pl - parse ls-dyna glstat energy output into individual files
# with time-dependent quantities; the names of the output files (*.asc) are
# based on the varaible names
# 
# Usage: glstatParser.pl < glstat
#
# Mark 04/03/07

use warnings;

# open files for writing output
open(KINETIC_ENERGY,'>KineticEnergy.asc');
open(INTERNAL_ENERGY,'>InternalEnergy.asc');
open(TOTAL_ENERGY,'>TotalEnergy.asc');
open(HOURGLASS_ENERGY,'>HourglassEnergy.asc');
open(EXTERNAL_WORK,'>ExternalWork.asc');

while(<>) {
    chomp;
    my @fields = split(' ',$_); 
    if($#fields >= 1) {
        if($fields[0] =~ "^time...") {
            $time = $fields[$#fields];
        }
        elsif($fields[0] =~ "^kinetic") {
            print KINETIC_ENERGY "$time $fields[$#fields]\n";
        }
        elsif($fields[0] =~ "^internal") {
            print INTERNAL_ENERGY "$time $fields[$#fields]\n";
        }
        elsif($fields[0] =~ "^total" && $fields[1] =~ "^energy...") {
            print TOTAL_ENERGY "$time $fields[$#fields]\n";
        }
        elsif($fields[0] =~ "^hourglass") {
            print HOURGLASS_ENERGY "$time $fields[$#fields]\n";
        }
        elsif($fields[0] =~ "^external" && $fields[1] =~ "^work") {
            print EXTERNAL_WORK "$time $fields[$#fields]\n";
        }
    }
}

# close output files
close KINETIC_ENERGY;
close INTERNAL_ENERGY;
close TOTAL_ENERGY;
close HOURGLASS_ENERGY;
close EXTERNAL_WORK;
