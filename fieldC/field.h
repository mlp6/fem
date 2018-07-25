#include <pthread.h>
#include "field_II.h"

extern sys_con_type   *sys_con;

struct nodeEntry {
	int nodeID;
	double x, y, z;
	};

struct FieldParams {
	int threads;
	int soundSpeed_MperSec, samplingFrequencyHz;
	double alpha_dBcmMHz;
	double fnum;
	point_type focusM;
	double frequencyMHz;
	char *transducer, *transducerType, *impulse;
	struct nodeEntry *pointsAndNodes;
	double *ThData;
	};
