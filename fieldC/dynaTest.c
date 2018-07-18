#include <stdio.h>
#include "field.h"

main()
{
int numNodes;
struct FieldParams params;
struct nodeEntry *pointsAndNodes, *readMpn();
point_type focus;
int verbose = 0;

	params.impulse = "gaussian";
	params.samplingFrequency = 100E6;

	focus.x = 0;
	focus.y = 0;
	focus.z = 0.02;

/*
*/
	params.alpha = 0.5;
	params.fnum = 1.3;
	params.focus = focus;
	params.frequency = 7.2;
	params.transducer = "vf105";
	params.threads = 1;

	params.soundSpeed = 1540;

	params.pointsAndNodes = readMpn("./myNodes.dyn", &numNodes, verbose);
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

	dynaField(params, 1, numNodes);
}
