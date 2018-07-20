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
point_type focus;
char *nodeFileName, *elemsFileName, *transducer, *impulse;
double alpha, fnum, freq;
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

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "alpha")) == NULL) {
		fprintf(stderr, "couldn't find alpha in probe file\n");
		return(0);
		}
	alpha = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "fnum")) == NULL) {
		fprintf(stderr, "couldn't find fnum in probe file\n");
		return(0);
		}
	fnum = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "focus")) == NULL) {
		fprintf(stderr, "couldn't find focus in probe file\n");
		return(0);
		}
	focusParams = jsonTemp;

	if ((jsonTemp = cJSON_GetObjectItem(focusParams, "x")) == NULL) {
		fprintf(stderr, "couldn't find x in probe file\n");
		return(0);
		}
	focus.x = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(focusParams, "y")) == NULL) {
		fprintf(stderr, "couldn't find y in probe file\n");
		return(0);
		}
	focus.y = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(focusParams, "z")) == NULL) {
		fprintf(stderr, "couldn't find z in probe file\n");
		return(0);
		}
	focus.z = jsonTemp->valuedouble;


	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "freq")) == NULL) {
		fprintf(stderr, "couldn't find freq in probe file\n");
		return(0);
		}
	freq = jsonTemp->valuedouble;

	if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "transducer")) == NULL) {
		fprintf(stderr, "couldn't find transducer in probe file\n");
		return(0);
		}
	transducer = jsonTemp->valuestring;

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

	field2dyna(nodeFileName, alpha, fnum,
		focus, freq, transducer, impulse,
		threads, lowNslow,
	    elemsFileName, verbose);

/*
	field2dyna(char *nodeFileName, double alpha, double fnum,
		struct Focus focus, double freq, char *transducer, char *impulse,
		int threads, int lowNslow,
	    char *elemFileName, int forceNonlinear)

field2dyna("./myNodes.dyn", .5, 1.3, focus, 7.2, "vf105", "gaussian", 1, 0,
	"../tests/elems.dyn", 1);
*/

}
