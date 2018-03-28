#include <pthread.h>
#include "field_II.h"

struct nodeEntry {
	int nodeID;
	float x, y, z;
	};

struct FieldParams {
	float alpha;
	struct nodeEntry *pointsAndNodes;
	float fnum;
	point_type focus;
	float frequency;
	char *transducer, *impulse;
	int threads, lowNslow;
	int soundSpeed, samplingFrequency;
	double *ThData;
	};
