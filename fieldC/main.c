/* test routine */

#include <stdio.h>
#include "field.h"
#include "cJSON.h"

sys_con_type   *sys_con;

/*
 * main takes one argument, the name of a JSON file that has the parameters
 * to be passed to field2dyna. if there's no file name, we'll exit.
 */

main(int argc, char **argv)
{
int i, len;
FILE *input;
cJSON *focusParams, *probeInfo;
char *field2dyna();
char *data;
point_type focus;
char *nodeFileName, *elemsFileName, *transducer, *impulse;
double alpha, fnum, freq;
int threads, lowNslow, forceNonlinear;

	if (argc != 2) {
		fprintf(stderr, "the routine requires a JSON file as an argument!\n");
		exit(0);
		}

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
		exit(0);
		}

	nodeFileName = cJSON_GetObjectItem(probeInfo, "nodeFileName")->valuestring;
	alpha = cJSON_GetObjectItem(probeInfo, "alpha")->valuedouble;
	fnum = cJSON_GetObjectItem(probeInfo, "fnum")->valuedouble;

	focusParams = cJSON_GetObjectItem(probeInfo, "focus");
	focus.x = cJSON_GetObjectItem(focusParams, "x")->valuedouble;
	focus.y = cJSON_GetObjectItem(focusParams, "y")->valuedouble;
	focus.z = cJSON_GetObjectItem(focusParams, "z")->valuedouble;

	freq = cJSON_GetObjectItem(probeInfo, "freq")->valuedouble;

	transducer = cJSON_GetObjectItem(probeInfo, "transducer")->valuestring;
	impulse = cJSON_GetObjectItem(probeInfo, "impulse")->valuestring;

	threads = cJSON_GetObjectItem(probeInfo, "threads")->valueint;
	lowNslow = cJSON_GetObjectItem(probeInfo, "lowNslow")->valueint;

	elemsFileName = cJSON_GetObjectItem(probeInfo, "elemsFileName")->valuestring;

	forceNonlinear = cJSON_GetObjectItem(probeInfo, "forceNonlinear")->valueint;

	field2dyna(nodeFileName, alpha, fnum,
		focus, freq, transducer, impulse,
		threads, lowNslow,
	    elemsFileName, forceNonlinear);

/*
	field2dyna(char *nodeFileName, double alpha, double fnum,
		struct Focus focus, double freq, char *transducer, char *impulse,
		int threads, int lowNslow,
	    char *elemFileName, int forceNonlinear)

field2dyna("./myNodes.dyn", .5, 1.3, focus, 7.2, "vf105", "gaussian", 1, 0,
	"../tests/elems.dyn", 1);
*/

}