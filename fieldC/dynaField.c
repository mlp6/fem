/*
% function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, threads, lownslow)
*
* no need for lownslow because C can't compute the whole array at once
*
%
% Generate intensity values at the nodal locations for conversion to force and
% input into the dyna deck.
%
% INPUTS:
%   FIELD_PARAMS.alpha (float) - absorption (dB/cm/MHz)
%   FIELD_PARAMS.measurementPointsandNodes - nodal IDs and spatial locations
%                                            from field2dyna.m
%   FIELD_PARAMS.Fnum (float) - F/#
%   FIELD_PARAMS.focus - [x y z] (m)
%   FIELD_PARAMS.Frequency (float) - push frequency (MHz)
%                                    6.67 (VF10-5)
%                                    4.21 (VF7-3)
%   FIELD_PARAMS.Transducer (string) - 'vf105'; select the
%       transducer-dependent parameters to use for the simulation
%   FIELD_PARAMS.Impulse (string) - 'guassian','exp'; use a Gaussian function
%       based on the defined fractional bandwidth and center
%       frequency, or use the experimentally-measured impulse
%       response
%   threads (int) - number of parallel threads to use [default = numCores]
%   lownslow (bool) - low RAM footprint, but much slower
%   numNodes - number of nodes from readMpn
%
% OUTPUT:
%   intensity - intensity values at all of the node locations
%   FIELD_PARAMS - field parameter structure
%
% EXAMPLE:
%   [intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS)
%
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "field.h"		/* includes field_II.h */
#include "cJSON.h"

dynaField(struct FieldParams params, int threads, int numNodes)
{
int i, j;
sys_con_type   *sys_con;      /*  System constants for Field II */ 
aperture_type *Th;
char *info;
cJSON *commands, *impulseResponse, *probeInfo;
cJSON *item;
FILE *input;
long len;
char *data, *out;
int no_elements, no_sub_x, no_sub_y;
double width, height, kerf, Rconvex, Rfocus;
double *foo;
point_type *focus;
double exciteFreq, texcite;
signal_type *excitationPulse;
signal_type **pressure;
double stepSize;
double freqAtt, attF0, att;
int numCYC = 50;
int numSteps;
double *intensity;
point_type *points;

/*
for (i = 0; i < 13; i++)
        fprintf(stderr, "in dynaField, node %d is %d, %f, %f, %f\n", i, params.pointsAndNodes[i].nodeID, params.pointsAndNodes[i].x, params.pointsAndNodes[i].y, params.pointsAndNodes[i].z);
*/

/* how do I do check_add_probes? */

/*
 * initialize Field II; field_init is in the provided c library; the '-1'
 * arg supresses ascii output.
 */
	
	sys_con = field_init(-1);

/* set transducer-independent parameters */

	set_field("c", params.soundSpeed);
	set_field("fs", params.samplingFrequency);
	set_field("threads", params.threads);
	fprintf(stderr, "PARALLEL THREADS: %d\n", threads);

/* get info from JSON */
	input = fopen("./c52Fixed.json","rb");
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

	else {
		out=cJSON_Print(probeInfo);
/* 		printf("%s\n",out); */
		free(out);
		}

	fprintf(stderr, "array size %d\n", cJSON_GetArraySize(probeInfo));

	no_elements = cJSON_GetObjectItem(probeInfo, "no_elements")->valueint;
	no_sub_x = cJSON_GetObjectItem(probeInfo, "no_sub_x")->valueint;
	no_sub_y = cJSON_GetObjectItem(probeInfo, "no_sub_y")->valueint;

	fprintf(stderr, "elements %d subX %d subY %d\n", no_elements, no_sub_x,
		no_sub_y);

	width = cJSON_GetObjectItem(probeInfo, "width")->valuedouble;
	fprintf(stderr, "width %f\n", width);
	height = cJSON_GetObjectItem(probeInfo, "height")->valuedouble;
	kerf = cJSON_GetObjectItem(probeInfo, "kerf")->valuedouble;
	Rconvex = cJSON_GetObjectItem(probeInfo, "Rconvex")->valuedouble;
	Rfocus = cJSON_GetObjectItem(probeInfo, "Rfocus")->valuedouble;

/*
	fprintf(stderr, "type %s\n", cJSON_GetObjectItem(probeInfo, "probe_type")->valuestring);
	commands = cJSON_GetObjectItem(probeInfo, "commands");
	fprintf(stderr, "Th %s\n", cJSON_GetObjectItem(commands, "Th")->valuestring);
	fprintf(stderr, "impulse response command %s\n", cJSON_GetObjectItem(commands, "impulseResponse")->valuestring);
	impulseResponse = cJSON_GetObjectItem(probeInfo, "impulse_response");
	fprintf(stderr, "center freq %d\n", cJSON_GetObjectItem(impulseResponse, "f0")->valueint);
	fprintf(stderr, "phase %d\n", cJSON_GetObjectItem(impulseResponse, "phase")->valueint);
	fprintf(stderr, "bw %d\n", cJSON_GetObjectItem(impulseResponse, "bw")->valueint);
*/

/* I think the next thing is to set Th, impulse */

	Th = xdc_convex_focused_array(no_elements,width,height,kerf,Rconvex,Rfocus,no_sub_x,no_sub_y,params.focus);

	fprintf(stderr, "#elements %d\n", Th->no_elements);
	fprintf(stderr, "num apertures from sys_con %d\n", sys_con->No_apertures);

	info = "rect";

/* 	foo = (double *)malloc(26*1344*sizeof(double)); */
	
	xdc_get(Th, info, foo);
	fprintf(stderr, "num apertures from sys_con %d\n", sys_con->No_apertures);
	fprintf(stderr, "rect? %d\n", sys_con->Use_rectangles);
	fprintf(stderr, "tri? %d\n", sys_con->Use_triangles);
/*
*/
	for (i = 0; i < 20; i++)
	fprintf(stderr, "back from xdc_get, got %f\n", foo[i]);
	fprintf(stderr, "done from xdc_get\n");

/*
% figure out the axial shift (m) that will need to be applied to the scatterers
% to accomodate the mathematical element shift due to the lens
*/
	
	exciteFreq = params.frequency * 1000000;
	stepSize = 1.0 / params.samplingFrequency;

	fprintf(stderr, "params.frequency %f exciteFreq %f stepSize %g\n", params.frequency, exciteFreq, stepSize);
	numSteps = (int) (numCYC / exciteFreq / stepSize);

	excitationPulse = (signal_type *)malloc(sizeof(signal_type));
	excitationPulse->data = (double *)malloc(numSteps * sizeof(double));
	fprintf(stderr, "setting excitationPulse; numSteps %d\n", numSteps);

	excitationPulse->data[0] = 0;

	for (i = 1; i < numSteps; i++) {
		excitationPulse->data[i] = sin(2 * M_PI * exciteFreq * i * stepSize);
		}

	fprintf(stderr, "calling excitation\n");
	xdc_excitation(Th, excitationPulse);
	fprintf(stderr, "back from excitation\n");

	freqAtt = params.alpha * 100 / 1E6; /* frequency atten. in dB/cm/MHz */

	attF0 = exciteFreq;
	att = freqAtt * attF0; /* set non freq. dep. to be centered here */
	set_field("att", att);
	set_field("Freq_att", freqAtt);
	set_field("att_f0", attF0);
	set_field("use_att", 1);

/*
% compute Ispta at each location for a single tx pulse
% optimizing by computing only relevant nodes... will assume others are zero
*
* how many points does calc_hp return?
*
*/
	intensity = (double *)malloc(sizeof(double));

	for (i = 0; i < numNodes; i++) {
		points->x = params.pointsAndNodes[i].x;
		points->y = params.pointsAndNodes[i].y;
		points->z = params.pointsAndNodes[i].z;

		pressure = calc_hp(Th, 1, points);
/* 		for (j = 0; j < ?; j++) intensity[i] +=  *(pressure[j]->data) * *(pressure[j]->data; */
		}
			

}
