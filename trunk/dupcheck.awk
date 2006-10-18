#! /bin/awk -f
#
# dupcheck.awk - check for duplicate node load definitions in a dyna deck
#
# command line:
# ./dupcheck.awk inputfile.dyn
#
# duplicate node numbers will be printed to the screen; you will
# have to manually modify the deck w/ a text editor to see which of the
# duplicate definitions you want to keep
#
# mark 01/12/02

# initialized variables
# trigger - run the conditional statements run only when
# 	in the appropriate load section of the dyna deck
# loadname - name of the load card being used in the dyna deck (i.e.
#	when should the trigger be activated)
# count - variable to keep track of number of entries in the load card

BEGIN { trigger = 0;
	loadname = "*LOAD_NODE_POINT";
	count = 0;
	}

{

### only process data in the 'loadnode' card of the input deck ###
if ($1 == loadname)
	trigger = 1;
# the next statement should turn off the trigger once it reaches the next
# card, whose name will vary depending on the deck, but its name should be
# the only entry on that line
if (trigger == 1 && $1 != loadname && NF == 1)
	trigger = 0;
###

# check for duplicates in the load card
if (trigger == 1)
	{
	count++;
	node[count]=$1;
	line[count]=NR;
	for(i=0;i<count;i++)
		{
		if($1 == node[i])
			printf("node %s multiply defined in %s on lines %s and %s\n",$1,loadname,line[i],NR)
		}
	}

}	
