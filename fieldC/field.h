#include <pthread.h>
#include "field_II.h"

extern sys_con_type   *sys_con;

struct nodeEntry {
	int nodeID;
	double x, y, z;
	};

struct FieldParams {
	int threads;
	int soundSpeed, samplingFrequency;
	double alpha;
	double fnum;
	point_type focus;
	double frequency;
	char *transducer, *impulse;
	struct nodeEntry *pointsAndNodes;
	double *ThData;
	};
