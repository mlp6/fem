/* test routine */

#include <stdio.h>

main()
{
int i;
char *field2dyna();

struct nodeEntry {
	int nodeID;
	float x, y, z;
	} *nodes, *readMpn();

struct Focus {
    int x, y, z;
	} focus;

	focus.x = 1;
	focus.y = 1;
	focus.z = 1;
/*
field2dyna(char *nodeName, float alpha, float fnum, struct Focus focus,
    float freq, char *transducer, char *impulse, int threads,
	    int lowNslow, char *elemName, int forceNonlinear)
*/
field2dyna("../tests/nodes.dyn", .1, .1, focus,
    100.1, "VF", "gaussian", 1,
	    0, "../tests/elems.dyn", 0);

/* 	nodes = readMpn("../tests/nodes.dyn");


	fprintf(stderr, "printing\n");

	for (i = 0; i < 13; i++)
	fprintf(stderr, "node %d is %d, %f, %f, %f\n", i, nodes[i].nodeID, nodes[i].x, nodes[i].y, nodes[i].z);
*/
}
