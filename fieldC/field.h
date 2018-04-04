#include <pthread.h>
#include "field_II.h"

struct nodeEntry {
	int nodeID;
	double x, y, z;
	};

struct FieldParams {
	double alpha;
	struct nodeEntry *pointsAndNodes;
	double fnum;
	point_type focus;
	double frequency;
	char *transducer, *impulse;
	int threads;
	int soundSpeed, samplingFrequency;
	double *ThData;
	};
