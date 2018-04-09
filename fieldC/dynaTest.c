#include <stdio.h>
#include "field.h"

main()
{
int numNodes;
struct FieldParams params;
struct nodeEntry *pointsAndNodes, *readMpn();

	params.impulse = "gaussian";
	params.frequency = 7.2;
	params.samplingFrequency = 100E6;

	params.pointsAndNodes = readMpn("./myNodes.dyn", &numNodes);
	if (params.pointsAndNodes == NULL) {
		fprintf(stderr, "didn't get enough values from readMpn\n");
		exit(0);
		}
	fprintf(stderr, "numNodes %d\n", numNodes);
	fprintf(stderr, "point 0 %f %f %f\n",
		params.pointsAndNodes[1].x,
		params.pointsAndNodes[1].y,
		params.pointsAndNodes[1].z);

	fprintf(stderr, "sampling %d\n", params.samplingFrequency);

	dynaField(params, 1, 100);
}
