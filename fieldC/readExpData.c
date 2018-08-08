#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"

readExpData(cJSON *probeInfo)
{
cJSON *impulseCmd;
cJSON *time, *times;
cJSON *voltage, *voltages;

	impulseCmd = cJSON_GetObjectItem(probeInfo, "impulseResponse");
	printf(cJSON_GetObjectItem(impulseCmd, "wavetype")->valuestring);

	times = cJSON_GetObjectItem(impulseCmd, "time");

	fprintf(stderr, "getting times\n");

	cJSON_ArrayForEach(time, times) {
		printf("%e\n", time->valuedouble);
		}

	voltages = cJSON_GetObjectItem(impulseCmd, "voltage");

	fprintf(stderr, "getting voltages\n");

	cJSON_ArrayForEach(voltage, voltages) {
		printf("%e\n", voltage->valuedouble);
		}
}
