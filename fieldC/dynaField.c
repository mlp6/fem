/*
% function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, threads, lownslow)
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
%   FIELD_PARAMS.Impulse (string) - 'gaussian','exp'; use a Gaussian function
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
#include <string.h>
#include <math.h>
#include "field.h"		/* includes field_II.h */
#include "cJSON.h"

#define RECT 1	/* type of info we want from xdc_get */
#define ROWS_RECT 26	/* rows xdc_get returns for each rectangle */
#define ROWS_TRI 15	/* rows xdc_get returns for each triangle */

sys_con_type   *sys_con;      /*  System constants for Field II */ 

dynaField(struct FieldParams params, int threads, int numNodes, int lowNslow)
{
int i, j;
int debug = 0;
aperture_type *Th;
int32 info;
cJSON *commands, *impulseCmd, *probeInfo;
FILE *input;
long len;
char *data, *out;
int no_elements, no_sub_x, no_sub_y;
int no_elements_y;
double width, height, kerf, Rconvex, Rfocus;
double heights;
double convexRadius, elvFocus, pitch, fractBandwidth, centerFreq;
point_type *focus, *points;
double exciteFreq, texcite;
signal_type *excitationPulse;
signal_type *impulseResponse, *gaussPulse();
signal_type **pressure;
double *intensity;
double stepSize;
double freqAtt, attF0, att;
int numCYC = 50;
int numSteps;
char *thCmd;
double f0, phase, bw;
char *wavetype;
double lensCorrection, correctAxialLens();
double temp;
char outFileName[80];
FILE *outptr;
int xdcGetSize;

/* how do I do check_add_probes? */

/*
 * initialize Field II; field_init is in the provided c library; the '-1'
 * arg supresses ascii output.
 */
	
	sys_con = field_init(-1);

/* set transducer-independent parameters */

	if (debug) {
		fprintf(stderr, "sampling frequency %d\n", params.samplingFrequency);
		fprintf(stderr, "alpha %f\n", params.alpha);
		fprintf(stderr, "fnum %f\n", params.fnum);
		fprintf(stderr, "frequency %f\n", params.frequency);
		fprintf(stderr, "points %f %f %f\n",
			params.pointsAndNodes[0].x,
			params.pointsAndNodes[0].y,
			params.pointsAndNodes[0].z);
			}

	set_field("c", params.soundSpeed);
	set_field("fs", params.samplingFrequency);

	set_field("threads", params.threads);

	if (debug) fprintf(stderr, "PARALLEL THREADS: %d param threads %d\n",
		threads, params.threads);

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

	if (debug) fprintf(stderr, "array size %d\n", cJSON_GetArraySize(probeInfo));

	no_elements = cJSON_GetObjectItem(probeInfo, "no_elements")->valueint;
	no_sub_x = cJSON_GetObjectItem(probeInfo, "no_sub_x")->valueint;
	no_sub_y = cJSON_GetObjectItem(probeInfo, "no_sub_y")->valueint;

	if (debug) fprintf(stderr, "elements %d subX %d subY %d\n", no_elements,
		no_sub_x, no_sub_y);

	width = cJSON_GetObjectItem(probeInfo, "width")->valuedouble;
	if (debug) fprintf(stderr, "width %f\n", width);
	height = cJSON_GetObjectItem(probeInfo, "height")->valuedouble;
	kerf = cJSON_GetObjectItem(probeInfo, "kerf")->valuedouble;
	Rconvex = cJSON_GetObjectItem(probeInfo, "Rconvex")->valuedouble;
	Rfocus = cJSON_GetObjectItem(probeInfo, "Rfocus")->valuedouble;
	convexRadius = cJSON_GetObjectItem(probeInfo, "convex_radius")->valuedouble;
	elvFocus = cJSON_GetObjectItem(probeInfo, "elv_focus")->valuedouble;
	pitch = cJSON_GetObjectItem(probeInfo, "pitch")->valuedouble;
	fractBandwidth = cJSON_GetObjectItem(probeInfo, "fractionalBandwidth")->valuedouble;
	centerFreq = cJSON_GetObjectItem(probeInfo, "centerFrequency")->valuedouble;

	if (debug) fprintf(stderr, "type %s\n", cJSON_GetObjectItem(probeInfo, "probe_type")->valuestring);

	commands = cJSON_GetObjectItem(probeInfo, "commands");
	thCmd = cJSON_GetObjectItem(commands, "Th")->valuestring;
	if (debug) fprintf(stderr, "Th command %s\n", thCmd);

/* set aperture. as of now, there are only 3 xdc calls for this */

	if (strstr(thCmd, "xdc_concave") != NULL) {
/* optical piston only? should this be handled differently? */
		fprintf(stderr, "calling xdc_concave\n");
		Th = xdc_concave(9.5E-3, 38E-3, 0.5E-3);
		}

	else if (strstr(thCmd, "xdc_convex_focused_array") != NULL) {
		fprintf(stderr, "calling xdc_convex_focused_array\n");
		if (debug) fprintf(stderr, "%d %f %f %f %f %f %d %d %f %f %f\n",
			no_elements,width,height,kerf,Rconvex, Rfocus,no_sub_x,
			no_sub_y,params.focus.x, params.focus.y, params.focus.z);

		Th = xdc_convex_focused_array(no_elements,width,height,kerf,Rconvex,
			Rfocus,no_sub_x,no_sub_y,params.focus);
		if (debug) fprintf(stderr, "xdc_convex_focused_array; info: %s %s\n",
			Th->information.name, Th->information.create_date);
		}

	else if (strstr(thCmd, "xdc_focused_multirow") != NULL) {
/* linear only? should this be handled differently? */
		fprintf(stderr, "calling xdc_focused_multirow\n");
		no_elements_y = 1;
		heights = height;
		Th = xdc_focused_multirow(no_elements,width,no_elements_y,&heights,
			kerf,kerf, Rfocus,no_sub_x,no_sub_y,params.focus);
		}

	else fprintf(stderr, "unknown aperture command\n");

	if (debug) fprintf(stderr, "impulse response command %s\n",
		cJSON_GetObjectItem(commands, "impulseResponse")->valuestring);

	impulseCmd = cJSON_GetObjectItem(probeInfo, "impulse_response");

	f0 = cJSON_GetObjectItem(impulseCmd, "f0")->valueint;
	phase = cJSON_GetObjectItem(impulseCmd, "phase")->valueint;
	bw = cJSON_GetObjectItem(impulseCmd, "bw")->valueint;
	wavetype = cJSON_GetObjectItem(impulseCmd, "wavetype")->valuestring;
	
	if (debug) fprintf(stderr, "f0 %f phase %f bw %f\n", f0, phase, bw);
	if (debug) fprintf(stderr, "wavetype %s\n", wavetype);

/*
 * I think the next thing is to set impulse. this seems to be the same for
 * all the apertures. the matlab code calls defineImpulseResponse() which
 * calls the matlab routine 'gauspuls', but since I had to write my own
 * I'm going to skip defineImpulseResponse()
 */

	impulseResponse = gaussPulse(fractBandwidth, centerFreq, params, debug);

	if (debug) fprintf(stderr, "back\n");
	if (debug) fprintf(stderr, "impulse response %f %f %f\n",
		impulseResponse->data[0], impulseResponse->data[1],
		impulseResponse->data[2]);
	if (debug) fprintf(stderr, "num apertures from sys_con %d\n",
		sys_con->No_apertures);

	info = RECT;

/*
 * note that 'ROWS*' is specific to the type of info you request from xdc_get
 */

	xdcGetSize = ROWS_RECT * no_elements * no_sub_y;

	if (debug) fprintf(stderr, "calling xdc_get; size is %d\n", xdcGetSize);

	params.ThData = (double *)malloc(xdcGetSize * sizeof(double));
	

	xdc_get(Th, info, params.ThData);

	if (1) {
		fprintf(stderr, "num apertures from sys_con %d\n",
			sys_con->No_apertures);
		fprintf(stderr, "rect? %d\n", sys_con->Use_rectangles);
		fprintf(stderr, "tri? %d\n", sys_con->Use_triangles);

		fprintf(stderr, "back from xdc_get, got %f %f %f\n", params.ThData[7],
			params.ThData[8], params.ThData[9]);

		if (debug > 1)
			for (i = 0; i < 26*no_elements*no_sub_x*no_sub_y; i += 26) {
				fprintf(stderr, "%3.0f %3.0f \n", params.ThData[i],
					params.ThData[i+1]);
				}
		fprintf(stderr, "\n");
		fprintf(stderr, "finished xdc_get\n");
		}

/*
% figure out the axial shift (m) that will need to be applied to the scatterers
% to accomodate the mathematical element shift due to the lens
 *
 * have to tell correctAxialLens() how many data points we have
*/
	
	if (debug) fprintf(stderr, "calling cAL\n");

	lensCorrection = correctAxialLens(params.ThData, ROWS_RECT,
		no_elements * no_sub_y, debug); 

	if (debug) fprintf(stderr, "back from cAL, correction %g\n", lensCorrection);

	if (debug) for (i = 0; i < 10; i++)
		fprintf(stderr, "uncorrected z %g\n", params.pointsAndNodes[i].z);

	for (i = 0; i < numNodes; i++)
		params.pointsAndNodes[i].z += lensCorrection;
	
	if (debug) for (i = 0; i < 10; i++)
		fprintf(stderr, "corrected z %g\n", params.pointsAndNodes[i].z);

/* define the impulse response */

	xdc_impulse(Th, impulseResponse);

	exciteFreq = params.frequency * 1000000;
	stepSize = 1.0 / params.samplingFrequency;

	if (debug) fprintf(stderr, "params.frequency %f exciteFreq %f stepSize %g\n",
		params.frequency, exciteFreq, stepSize);
	numSteps = ceil ((double )numCYC / exciteFreq / stepSize);

	excitationPulse = alloc_signal(numSteps, 0);

	fprintf(stderr, "setting excitationPulse; numSteps %d\n", numSteps);

	temp = 2 * M_PI * exciteFreq * stepSize;

	for (i = 0; i < numSteps; i++) {
		excitationPulse->data[i] = sin(i * temp);
		if (debug) fprintf(stderr, "data %g\n", excitationPulse->data[i]);
		}

	if (debug) fprintf(stderr, "calling excitation\n");
	if (debug) fprintf(stderr, "before call %d %d\n",
		Th->excitation->allocated, Th->excitation->no_samples);

	if (debug) for (i = 0; i < 30; i++)
		fprintf(stderr, "got %f\n", Th->excitation->data[i]);

	xdc_excitation(Th, excitationPulse);

	if (debug) fprintf(stderr, "back from excitation\n");
	if (debug) fprintf(stderr, "got %d %d\n", Th->excitation->allocated,
		Th->excitation->no_samples);

	if (debug > 1) for (i = 0; i < Th->excitation->no_samples; i++)
		fprintf(stderr, "got %f\n", Th->excitation->data[i]);

	freqAtt = params.alpha * 100 / 1E6; /* frequency atten. in dB/cm/MHz */

	attF0 = exciteFreq;
	att = freqAtt * attF0; /* set non freq. dep. to be centered here */
	set_field("att", att);
	set_field("Freq_att", freqAtt);
	set_field("att_f0", attF0);
	set_field("use_att", 1);

	if (debug) fprintf(stderr, "freqAtt %g attF0 %g att %g\n", freqAtt, attF0,
		att);

/*
% compute Ispta at each location for a single tx pulse
% optimizing by computing only relevant nodes... will assume others are zero
*
* how many points does calc_hp return?
*
*/

	if (debug) fprintf(stderr, "calling calc_hp; numNodes %d\n", numNodes);

	if (debug) field_info;

/*
 * calc_hp just wants the xyz coordinates, but pointsAndNodes includes the
 * node id. may not need the id, but for now I'm going to make a copy.
 */

	points = (point_type *)malloc(numNodes * sizeof(point_type));

	for (i = 0; i < numNodes; i++) {
		points[i].x = params.pointsAndNodes[i].x;
		points[i].y = params.pointsAndNodes[i].y;
		points[i].z = params.pointsAndNodes[i].z;
		
		if (debug) fprintf(stderr, "x %f, y %f, z %f\n", points[i].x,
			points[i].y, points[i].z);
		}

/* have to init intensity to 0 so we can sum into it */

	intensity = (double *)calloc(numNodes, sizeof(double));

	if (1) {
		fprintf(stderr, "running low-n-slow\n");
		for (i = 0; i < numNodes; i++) {
			if (debug) fprintf(stderr, "i %d\n", i);
			pressure = calc_hp(Th, 1, &points[i]);
			if (debug) fprintf(stderr, "num samples %d\n",
				pressure[0]->no_samples);
			if (debug) for (j = 0; j < pressure[0]->no_samples; j++)
				fprintf(stderr, "pressure %g\n", pressure[0]->data[j]);
			for (j = 0; j < pressure[0]->no_samples; j++)
				intensity[i] += pressure[0]->data[j] * pressure[0]->data[j];
			}
		}
	else {
		pressure = calc_hp(Th, numNodes, points);
		for (i = 0; i < numNodes; i++)
			for (j = 0; j < pressure[i]->no_samples; j++)
				intensity[i] += pressure[i]->data[j] * pressure[i]->data[j];
		}

	if (debug) for (i = 0; i < numNodes; i++)
		fprintf(stderr, "intensity %g\n", intensity[i]);

	if (debug) fprintf(stderr, "done with calc_hp; num samples at 0 %d\n",
		pressure[0]->no_samples);

	if (debug) for (j = 0; j < pressure[0]->no_samples; j++)
			fprintf(stderr, "%g\n", pressure[0]->data[j]);

	if (debug > 1) for (i = 0; i < numNodes; i++) {
		fprintf(stderr, "AAAAAAAAAAAAAAAAA; num samples at %d %d\n", i,
			pressure[i]->no_samples);
		for (j = 0; j < pressure[i]->no_samples; j++)
			fprintf(stderr, "j %d pressure %g %g\n", j, pressure[i]->data[j], pressure[i]->data[j]);
		}

/*
 * the original code wrote out the intensity and the field params from
 * 'field2dyna', but I'm going to do it here. the file will be:
 *
 * int numNodes
 *
 * intensity, numNodes doubles
 *
 * fieldParams:
 *
 *  int threads
 *	int soundSpeed
 *	int samplingFrequency
 *	double alpha
 *	double fnum
 *	point_type focus (struct of three doubles)
 *	double frequency
 *	transducer, character string
 *	impulse, character string
 *	pointsAndNodes, which is numNodes nodeEntry structs (one int,
 *		three doubles)
 *	int ROWS * no_elements * no_sub_y
 *	ThData, which is ROWS * no_elements * no_sub_y doubles. ROWS is a constant
 *		determined by the return of 'xdc_get, and no_elements, no_sub_y come
 *		from the probe description file. in our case, it appears that we only
 *		care about rectangles.
 */

	sprintf(outFileName, "dyna-I-f%.2f-F%.1f-FD%.3f-a%.2f.ned",
		params.frequency, params.fnum, params.focus.z, params.alpha);

	fprintf(stderr, "file name %s\n", outFileName);

/* open output file */

    if ((outptr = fopen(outFileName, "wb")) == NULL) {
		fprintf(stderr, "couldn't open output file %s\n", outFileName);
		exit(EXIT_FAILURE);
		}

	if (fwrite(&numNodes, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write numNodes\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.threads, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write threads\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.soundSpeed, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write soundSpeed\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.samplingFrequency, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write samplingFrequency\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(intensity, sizeof(double), numNodes, outptr) != numNodes) {
		fprintf(stderr, "failed to write intensity\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.alpha, sizeof(double), 1, outptr) != 1) {
		fprintf(stderr, "failed to write alpha\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.fnum, sizeof(double), 1, outptr) != 1) {
		fprintf(stderr, "failed to write fnum\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.focus, sizeof(point_type), 1, outptr) != 1) {
		fprintf(stderr, "failed to write focus\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&params.frequency, sizeof(double), 1, outptr) != 1) {
		fprintf(stderr, "failed to write frequency\n");
		exit(EXIT_FAILURE);
		}

	i = strlen(params.transducer) + 1;

	if (fwrite(&i, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write length of transducer string\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(params.transducer, sizeof(char), i, outptr) != i) {
		fprintf(stderr, "failed to write transducer\n");
		exit(EXIT_FAILURE);
		}

	i = strlen(params.impulse) + 1;

	if (fwrite(&i, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write length of impulse string\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(params.impulse, i, 1, outptr) != 1) {
		fprintf(stderr, "failed to write impulse\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(params.pointsAndNodes, sizeof(struct nodeEntry), numNodes, outptr) != numNodes) {
		fprintf(stderr, "failed to write points and nodes\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(&xdcGetSize, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write size of xdc_get\n");
		exit(EXIT_FAILURE);
		}

/*
*/
	if (fwrite(params.ThData, sizeof(double), xdcGetSize, outptr) != xdcGetSize) {
		fprintf(stderr, "failed to write ThData\n");
		exit(EXIT_FAILURE);
		}

	fclose(outptr);
}
