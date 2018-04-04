#include <stdio.h>
#include <string.h>
#include "field.h"

void
main(int argc, char **argv)
{
struct nodeEntry *pointsAndNodes, *readMpn();
char *nodeName;
char *cmd;
int numNodes;
int correctNumNodes;
FILE *checkResult;

	if ((argc == 1) || (strcmp(argv[1], "readMpn") == 0)) {
		fprintf(stderr, "test is readMpn\n");
		nodeName = "./myNodes.dyn";
/* 		fprintf(stderr, "testing, calling readMpn; node name %s\n", nodeName); */
	    pointsAndNodes = readMpn(nodeName, &numNodes);
/* 		fprintf(stderr, "after readMpn; numNodes %d\n", numNodes); */
		cmd = "grep '^[0-9]' ./myNodes.dyn | wc -l";
		checkResult = popen(cmd, "r");
		fscanf(checkResult, "%d", &correctNumNodes);
		fclose(checkResult);
/* 		fprintf(stderr, "after system; correctNumNodes %d\n", correctNumNodes); */
		if (numNodes == correctNumNodes)
			fprintf(stderr, "readMpn test successful\n");
		else fprintf(stderr, "readMpn test failed\n");
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
