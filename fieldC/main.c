/* test routine */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "field.h"
#include "cJSON.h"

sys_con_type   *sys_con;

/*
 * main requires at least one argument, the name of a JSON file that has the
 * parameters to be passed to field2dyna. if there's no file name, we'll exit.
 * there's also an optional 'verbose' flag.
 */

const char *usage[] = {
	"Usage: field2dyna [verbosity] inputFileName\n",
	"Options:\n",
	"\t-v[vv]            amount of verbosity\n",
	0};

main(int argc, char **argv)
{
int i, j, len;
int verbose = 0;
FILE *input;
cJSON *focusParams, *probeInfo;
cJSON *jsonTemp;
char *field2dyna();
char *data;
char inputFileName[128];
point_type focusM;
char *nodeFileName, *elemsFileName, *transducer, *transducerType, *impulse;
double alpha_dBcmMHz, fnum, freqMHz;
int threads, lowNslow;

	if (argc <= 1) {
		fprintf(stderr, "the routine requires a JSON file as an argument!\n");
		exit(0);
		}

	for (i = 1; i < argc; i++) {
		if (argv[i][0] == '-')
			switch(argv[i][1]) {
				default:
					fprintf(stderr, "\nbad arg: %s\n\n", argv[i]);
					for (j = 0; usage[j]; j++)
						fprintf(stderr, "%s", usage[j]);
					fprintf(stderr, "\n");
					exit(0);

				case 'v':       /*  verbose*/
					verbose = strlen(argv[i]) - 1;
					break;
				}
		else {
			strcpy(inputFileName, argv[i]);
			}
		}

/* get info from JSON */
	input = fopen(inputFileName, "rb");

	fseek(input, 0, SEEK_END);
	len = ftell(input);
	fseek(input, 0, SEEK_SET);
	data = (char *)malloc(len + 1);
	fread(data, 1, len, input);
	fclose(input);

	probeInfo = cJSON_Parse(data);
	if (!probeInfo) {
		printf("Error before: [%s]\n",cJSON_GetErrorPtr());
		exit(0);
		}

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "nodeFileName")) == NULL) {
		fprintf(stderr, "couldn't find nodeFileName in probe file\n");
		return(0);
		}
	nodeFileName = jsonTemp->valuestring;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "alpha_dBcmMHz")) == NULL) {
		fprintf(stderr, "couldn't find alpha_dBcmMHz in probe file\n");
		return(0);
		}
	alpha_dBcmMHz = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "fnum")) == NULL) {
		fprintf(stderr, "couldn't find fnum in probe file\n");
		return(0);
		}
	fnum = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "focusM")) == NULL) {
		fprintf(stderr, "couldn't find focusM in probe file\n");
		return(0);
		}
	focusParams = jsonTemp;

	if ((jsonTemp = cJSON_GetObjectItem(focusParams, "x")) == NULL) {
		fprintf(stderr, "couldn't find x in probe file\n");
		return(0);
		}
	focusM.x = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(focusParams, "y")) == NULL) {
		fprintf(stderr, "couldn't find y in probe file\n");
		return(0);
		}
	focusM.y = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(focusParams, "z")) == NULL) {
		fprintf(stderr, "couldn't find z in probe file\n");
		return(0);
		}
	focusM.z = jsonTemp->valuedouble;


	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "freqMHz")) == NULL) {
		fprintf(stderr, "couldn't find freqMHz in probe file\n");
		return(0);
		}
	freqMHz = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "transducer")) == NULL) {
		fprintf(stderr, "couldn't find transducer in probe file\n");
		return(0);
		}
	transducer = jsonTemp->valuestring;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "transducerType")) == NULL) {
		fprintf(stderr, "couldn't find transducerType in probe file\n");
		return(0);
		}
	transducerType = jsonTemp->valuestring;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "impulse")) == NULL) {
		fprintf(stderr, "couldn't find impulse in probe file\n");
		return(0);
		}
	impulse = jsonTemp->valuestring;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "threads")) == NULL) {
		fprintf(stderr, "couldn't find threads in probe file\n");
		return(0);
		}
	threads = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "lowNslow")) == NULL) {
		fprintf(stderr, "couldn't find lowNslow in probe file\n");
		return(0);
		}
	lowNslow = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "elemsFileName")) == NULL) {
		fprintf(stderr, "couldn't find elemsFileName in probe file\n");
		return(0);
		}
	elemsFileName = jsonTemp->valuestring;

	field2dyna(nodeFileName, alpha_dBcmMHz, fnum,
		focusM, freqMHz, transducer, transducerType, impulse,
		threads, lowNslow,
	    elemsFileName, verbose);

}
