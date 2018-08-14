#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"

readExpData(cJSON *probeInfo, double **timeValues, double **voltageValues)
{
cJSON *impulseCmd;
cJSON *time, *times;
cJSON *voltage, *voltages;
int i, numPnts = 0;

	impulseCmd = cJSON_GetObjectItem(probeInfo, "impulseResponse");
	fprintf(stderr, "%s\n", cJSON_GetObjectItem(impulseCmd, "wavetype")->valuestring);

	times = cJSON_GetObjectItem(impulseCmd, "time");

/*
 * we don't know ahead of time how many data points there are, so I'll make
 * an initial pass through the data to get a count. interestly, it doesn't
 * look like I need to reset the 'times' variable to do the second count.
 */

	cJSON_ArrayForEach(time, times) {
		numPnts++;
/* 		if (numPnts < 30) printf("%e\n", time->valuedouble); */
		}

	fprintf(stderr, "num points %d\n", numPnts);

	if ((*timeValues = (double *)malloc(sizeof(double) * numPnts)) == NULL) {
		fprintf(stderr, "in readExpData, couldn't allocate space for times\n");
		return(0);
		}

	if ((*voltageValues = (double *)malloc(sizeof(double) * numPnts)) == NULL) {
		fprintf(stderr, "in readExpData, couldn't allocate space for voltages\n");
		return(0);
		}

	i = 0;

	cJSON_ArrayForEach(time, times) {
		(*timeValues)[i++] = time->valuedouble;
/* 		if (i < 20) printf("%e\n", time->valuedouble); */
		}

	voltages = cJSON_GetObjectItem(impulseCmd, "voltage");

	fprintf(stderr, "getting voltages\n");

	i = 0;
	cJSON_ArrayForEach(voltage, voltages) {
		(*voltageValues)[i++] = voltage->valuedouble;
/* 		printf("%e\n", voltage->valuedouble); */
		}

	return(numPnts);
}
