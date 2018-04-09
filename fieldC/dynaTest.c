#include <stdio.h>
#include "field.h"

main()
{
int numNodes;
struct FieldParams params;
struct nodeEntry *pointsAndNodes, *readMpn();
point_type focus;

	params.impulse = "gaussian";
	params.frequency = 7.2;
	params.samplingFrequency = 100E6;

	focus.x = 2;
	focus.y = 1;
	focus.z = 1;

/*
	params.alpha = 0.1;
	params.fnum = 0.1;
	params.focus = focus;
	params.frequency = 100.1;
	params.transducer = "VF";
	params.threads = 1;
*/
	params.soundSpeed = 1540;

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
