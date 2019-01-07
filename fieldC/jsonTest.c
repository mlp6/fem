#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"

main(int argc, char **argv)
{
cJSON *probeInfo;
cJSON *impulseCmd;
cJSON *time, *times;
cJSON *voltage, *voltages;
FILE *input;
long len;
char *data, *out;

/* get info from JSON */
	input = fopen(argv[1],"rb");
	fseek(input,0,SEEK_END);
	len=ftell(input );
	fseek(input,0,SEEK_SET);
	data=(char*)malloc(len+1);
	fread(data,1,len,input);
	fclose(input);

	probeInfo = cJSON_Parse(data);
	if (!probeInfo) {
		printf("Error before: [%s]\n",cJSON_GetErrorPtr());
		}

/*
	else {
		out=cJSON_Print(probeInfo);
		printf("%s\n",out);
		free(out);
		}
*/

	impulseCmd = cJSON_GetObjectItem(probeInfo, "impulseResponse");
	printf(cJSON_GetObjectItem(impulseCmd, "wavetype")->valuestring);

	times = cJSON_GetObjectItem(impulseCmd, "time");

	cJSON_ArrayForEach(time, times) {
		printf("%e\n", time->valuedouble);
		}

	voltages = cJSON_GetObjectItem(impulseCmd, "voltage");

	cJSON_ArrayForEach(voltage, voltages) {
		printf("%e\n", voltage->valuedouble);
		}
}
