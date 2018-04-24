#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "field.h"

struct nodeEntry testDyn[] = {
1,-1.000000,0.000000,-1.000000,
2,-0.900000,0.000000,-1.000000,
3,-0.800000,0.000000,-1.000000,
4,-0.700000,0.000000,-1.000000,
5,-0.600000,0.000000,-1.000000,
6,-0.500000,0.000000,-1.000000,
7,-0.400000,0.000000,-1.000000,
8,-0.300000,0.000000,-1.000000,
9,-0.200000,0.000000,-1.000000,
10,-0.100000,0.000000,-1.000000
};

void
main(int argc, char **argv)
{
int i;
struct nodeEntry *pointsAndNodes, *readMpn();
char *nodeName = "./myNodesShort.dyn";
char cmd[50];
int numNodes;
int correctNumNodes;
FILE *checkResult;

	if ((argc == 1) || (strcmp(argv[1], "readMpn") == 0)) {
		fprintf(stderr, "test is readMpn\n");

/*
 * have to test that I read the correct number of nodes AND that I get the
 * correct point values.
 */

		fprintf(stderr, "testing, calling readMpn; node name %s\n", nodeName);

/* check number of nodes first */

	    pointsAndNodes = readMpn(nodeName, &numNodes);
		fprintf(stderr, "after readMpn; numNodes %d\n", numNodes);
		sprintf(cmd, "grep '^[0-9]' %s | wc -l", nodeName);
/* 		fprintf(stderr, "cmd %s\n", cmd); */
		checkResult = popen(cmd, "r");
		fscanf(checkResult, "%d", &correctNumNodes);
		fclose(checkResult);
		fprintf(stderr, "after system; correctNumNodes %d\n", correctNumNodes);
		if (numNodes != correctNumNodes) {
			fprintf(stderr, "readMpn test failed: wrong num nodes\n");
			exit(0);
			}

/* now check values */
		for (i = 0; i < numNodes; i++) {
			if ((testDyn[i].x != pointsAndNodes[i].x) ||
				(testDyn[i].y != pointsAndNodes[i].y) ||
				(testDyn[i].z != pointsAndNodes[i].z)) {
					fprintf(stderr, "readMpn test failed: values didn't match\n");
					exit(0);
					}
			}
		}
	else if (strcmp(argv[1], "checkOnAxis") == 0) {
		fprintf(stderr, "test is checkOnAxis\n");
		nodeName = "./myNodes.dyn";
	    pointsAndNodes = readMpn(nodeName, &numNodes);
		if (checkOnAxis(pointsAndNodes, numNodes) == 1)
			fprintf(stderr, "checkOnAxis correct for good node list\n");
		else fprintf(stderr, "checkOnAxis wrong for good node list\n");
		nodeName = "./myNodesBadAxis.dyn";
	    pointsAndNodes = readMpn(nodeName, &numNodes);
		if (checkOnAxis(pointsAndNodes, numNodes) == 0)
			fprintf(stderr, "checkOnAxis correct for bad node list\n");
		else fprintf(stderr, "checkOnAxis wrong for bad node list\n");
		}
}
