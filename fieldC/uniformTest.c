#include <stdio.h>
#include <stdlib.h>
#include "field.h"

main()
{
int debug = 0, numNodes, ret;
struct nodeEntry *pointsAndNodes, *readMpn();

	pointsAndNodes = readMpn("./myNodesNonUniform.dyn", &numNodes, debug);
	if (pointsAndNodes == NULL) {
		fprintf(stderr, "didn't get enough values from readMpn\n");
		exit(0);
		}
	fprintf(stderr, "numNodes %d\n", numNodes);
	fprintf(stderr, "point 0 %f %f %f\n",
		pointsAndNodes[1].x,
		pointsAndNodes[1].y,
		pointsAndNodes[1].z);

	ret = checkUniform(pointsAndNodes, numNodes, debug);

	fprintf(stderr, "ret %d\n", ret);

}
