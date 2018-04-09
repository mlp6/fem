/* test routine */

#include <stdio.h>
#include "field.h"

main()
{
int i;
char *field2dyna();

struct nodeEntry {
	int nodeID;
	double x, y, z;
	} *nodes, *readMpn();

point_type focus;

	focus.x = 2;
	focus.y = 1;
	focus.z = 1;

/*
field2dyna(char *nodeName, double alpha, double fnum, struct Focus focus,
    double freq, char *transducer, char *impulse, int threads,
	    char *elemName, int forceNonlinear)
*/

field2dyna("./myNodes.dyn", .1, .1, focus, 100.1, "VF", "gaussian", 2,
	"../tests/elems.dyn", 0);

/* 	nodes = readMpn("../tests/nodes.dyn");


	fprintf(stderr, "printing\n");

	for (i = 0; i < 13; i++)
	fprintf(stderr, "node %d is %d, %f, %f, %f\n", i, nodes[i].nodeID, nodes[i].x, nodes[i].y, nodes[i].z);
*/
}
