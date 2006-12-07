# ModDynDeck.pl - modify lines of a dyna deck to eliminate
# having to do repetative manual changes
# Mark 11/16/06

while(<>) {
	# remove the EOL character from each line
  chomp;

	$cntrl_hg = "*CONTROL_HOURGLASS";
	if($_ =~ m/^$cntrl_hg/) {
		print "\$".$cntrl_hg."\n";
		$NextLine = 1;
	}
	elsif($NextLine == 1) {
		print "\$".$_."\n";
		print "*HOURGLASS\n";
		print "1,4,0.1,1\n";
		$NextLine = 0;
	}
	elsif($_ =~ m/^*PART/) {
		print "*PART\n";
		print "\n";
		print "1,1,1,0,1,0,0\n";
		$part2 = 2;
	}
	elsif($part2 > 0) {
		$part2 = $part2 - 1;	
	}
	else {
		print "$_\n";
	}
}
