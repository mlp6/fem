/*
% function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, threads, numNodes,
%	lownslow)
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

dynaField(struct FieldParams params, int threads, int numNodes, int lowNslow,
	int verbose)
{
int dynaWrite();
int i, j;
aperture_type *Th = NULL;
int32 info;
cJSON *commands, *probeInfo;
cJSON *jsonTemp;
FILE *jsonInput;
char jsonFileName[128];
long len;
char *data, *out;
int noElements, noSubX, noSubY;
int noElementsY;
double width, height, kerf, Rconvex, Rfocus, eleSize, radius;
double fractBandwidth, centerFreq;
point_type *points;
double exciteFreqHz;
signal_type *excitationPulse = NULL;
signal_type *impulseResponse = NULL, *formatExpImpResp(), *gaussPulse();
signal_type **pressure = NULL;
double *intensity;
double stepSize;
double freqAtt, attF0, att;
int numCYC = 50;
int numExpPnts;
int numSteps;
double lensCorrection, correctAxialLens();
double temp;
char outFileName[80];
int xdcGetSize;
double *timeValues, *voltageValues;

/* how do I do check_add_probes? */

/*
 * initialize Field II; field_init is in the provided c library; the '-1'
 * arg supresses ascii output.
 */
	
	sys_con = field_init(-1);

/* set transducer-independent parameters */

	fprintf(stderr, "in dynaField verbose %d\n", verbose);

	if (verbose >= 1) {
		fprintf(stderr, "sampling frequency %d\n", params.samplingFrequencyHz);
		fprintf(stderr, "alpha_dBcmMHz %f\n", params.alpha_dBcmMHz);
		fprintf(stderr, "fnum %f\n", params.fnum);
		fprintf(stderr, "frequency %f\n", params.frequencyMHz);
		fprintf(stderr, "transducer %s transducer Type %s\n",
			params.transducer, params.transducerType);
		fprintf(stderr, "points %f %f %f\n",
			params.pointsAndNodes[0].x,
			params.pointsAndNodes[0].y,
			params.pointsAndNodes[0].z);
		}

/*
 * splint throws a warning here because set_field wants doubles even though
 * some params are really ints. I'm going to ignore it; I think the code is
 * clearer without the cast.
 */

	set_field("c", params.soundSpeed_MperSec);
	set_field("fs", params.samplingFrequencyHz);

	set_field("threads", params.threads);

	if (verbose >= 1) fprintf(stderr, "PARALLEL THREADS: %d param threads %d\n",
		threads, params.threads);

/*
 * okay. I think this is what is going on. we have to compute 'Th', which
 * comes from one of the xdc calls in fieldII, and we have to compute
 * 'impulseResponse'. impulseResponse is either computed as a gaussian, or
 * computed from experimental data read in from a probe file. at this point
 * it's not clear what other info I'll need from the probe file.
 */

/* get info from JSON; this assumes that the JSON probe file is local */
/* 	strcpy(jsonFileName, "./c52.json"); */
	sprintf(jsonFileName, "./%s.json", params.transducer);

	if ((jsonInput = fopen(jsonFileName, "rb")) == NULL) {
		fprintf(stderr, "couldn't open json file %s\n", jsonFileName);
		return(0);
		}

	fseek(jsonInput, 0, SEEK_END);
	len = ftell(jsonInput);

	fseek(jsonInput, 0, SEEK_SET);

	if ((data = (char *)malloc(len+1)) == NULL) {
		fprintf(stderr, "couldn't allocate space for json data\n");
		return(0);
		}

	if (fread(data, 1, len, jsonInput) != len) {
		fprintf(stderr, "couldn't read json data\n");
		return(0);
		}

	fclose(jsonInput);

	probeInfo = cJSON_Parse(data);
	if (!probeInfo) {
		printf("Error before: [%s]\n", cJSON_GetErrorPtr());
		return(0);
		}

	else {
		out = cJSON_Print(probeInfo);
		free(out);
		}

	if (verbose >= 2) fprintf(stderr, "array size %d\n", cJSON_GetArraySize(probeInfo));

/* if any of the requested items is missing, it's a fatal error.
 * note that the elements that are in a probe file depend on the probe, so
 * we have to use 'transducerType' to decide what to parse.
 */

/* set aperture. we currently recognize 4 types:
 *
 *	concave
 *	convex_focused_array
 *	focused_multirow
 *	focused_array
 *
 */

	if (strstr(params.transducerType, "concave") != NULL) {
/* optical piston only? should this be handled differently? */

		if (verbose >= 1) fprintf(stderr, "calling xdc_concave\n");

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "fractionalBandwidth")) == NULL) {
			fprintf(stderr, "couldn't find fractBandwidth in probe file\n");
			return(0);
			}
		fractBandwidth = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "eleSize")) == NULL) {
			fprintf(stderr, "couldn't find eleSize in probe file\n");
			return(0);
			}
		eleSize = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "radius")) == NULL) {
			fprintf(stderr, "couldn't find radius in probe file\n");
			return(0);
			}
		radius = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "Rfocus")) == NULL) {
			fprintf(stderr, "couldn't find Rfocus in probe file\n");
			return(0);
			}
		Rfocus = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "centerFrequency")) == NULL) {
			fprintf(stderr, "couldn't find centerFreq in probe file\n");
			return(0);
			}
		centerFreq = jsonTemp->valuedouble;

		Th = xdc_concave(radius, Rfocus, eleSize);
		if (Th == NULL) {
			fprintf(stderr, "error calling xdc_concave\n");
			return(0);
			}
		}

	else if (strstr(params.transducerType, "convex_focused_array") != NULL) {

		if (verbose >= 1) fprintf(stderr, "calling xdc_convex_focused_array\n");

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noElements")) == NULL) {
			fprintf(stderr, "couldn't find noElements in probe file\n");
			return(0);
			}
		noElements = jsonTemp->valueint;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noSubX")) == NULL) {
			fprintf(stderr, "couldn't find noSubX in probe file\n");
			return(0);
			}
		noSubX = jsonTemp->valueint;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noSubY")) == NULL) {
			fprintf(stderr, "couldn't find noSubY in probe file\n");
			return(0);
			}
		noSubY = jsonTemp->valueint;

		if (verbose >= 2) fprintf(stderr, "elements %d subX %d subY %d\n", noElements,
			noSubX, noSubY);

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "width")) == NULL) {
			fprintf(stderr, "couldn't find width in probe file\n");
			return(0);
			}
		width = jsonTemp->valuedouble;

		if (verbose >= 2) fprintf(stderr, "width %f\n", width);

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "height")) == NULL) {
			fprintf(stderr, "couldn't find height in probe file\n");
			return(0);
			}
		height = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "kerf")) == NULL) {
			fprintf(stderr, "couldn't find kerf in probe file\n");
			return(0);
			}
		kerf = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "Rconvex")) == NULL) {
			fprintf(stderr, "couldn't find Rconvex in probe file\n");
			return(0);
			}
		Rconvex = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "Rfocus")) == NULL) {
			fprintf(stderr, "couldn't find Rfocus in probe file\n");
			return(0);
			}
		Rfocus = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "fractionalBandwidth")) == NULL) {
			fprintf(stderr, "couldn't find fractBandwidth in probe file\n");
			return(0);
			}
		fractBandwidth = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "centerFrequency")) == NULL) {
			fprintf(stderr, "couldn't find centerFreq in probe file\n");
			return(0);
			}
		centerFreq = jsonTemp->valuedouble;

		if (verbose >= 2) fprintf(stderr, "type %s\n", cJSON_GetObjectItem(probeInfo, "probeType")->valuestring);


		if (verbose >= 2) fprintf(stderr, "%d %f %f %f %f %f %d %d %f %f %f\n",
			noElements, width, height, kerf, Rconvex, Rfocus, noSubX,
			noSubY, params.focusM.x, params.focusM.y, params.focusM.z);

		Th = xdc_convex_focused_array(noElements, width, height, kerf, Rconvex,
			Rfocus, noSubX, noSubY, params.focusM);
		if (Th == NULL) {
			fprintf(stderr, "error calling xdc_convex_focused_array\n");
			return(0);
			}
		if (verbose >= 2) fprintf(stderr, "xdc_convex_focused_array; info: %s %s\n",
			Th->information.name, Th->information.create_date);
		}

	else if (strstr(params.transducerType, "focused_multirow") != NULL) {
/* linear only? should this be handled differently? */

		if (verbose >= 1) fprintf(stderr, "calling xdc_focused_multirow\n");

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noElements")) == NULL) {
			fprintf(stderr, "couldn't find noElements in probe file\n");
			return(0);
			}
		noElements = jsonTemp->valueint;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noSubX")) == NULL) {
			fprintf(stderr, "couldn't find noSubX in probe file\n");
			return(0);
			}
		noSubX = jsonTemp->valueint;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noSubY")) == NULL) {
			fprintf(stderr, "couldn't find noSubY in probe file\n");
			return(0);
			}
		noSubY = jsonTemp->valueint;

		if (verbose >= 2) fprintf(stderr, "elements %d subX %d subY %d\n", noElements,
			noSubX, noSubY);

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "width")) == NULL) {
			fprintf(stderr, "couldn't find width in probe file\n");
			return(0);
			}
		width = jsonTemp->valuedouble;

		if (verbose >= 2) fprintf(stderr, "width %f\n", width);

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "height")) == NULL) {
			fprintf(stderr, "couldn't find height in probe file\n");
			return(0);
			}
		height = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "kerf")) == NULL) {
			fprintf(stderr, "couldn't find kerf in probe file\n");
			return(0);
			}
		kerf = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "Rfocus")) == NULL) {
			fprintf(stderr, "couldn't find Rfocus in probe file\n");
			return(0);
			}
		Rfocus = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "fractionalBandwidth")) == NULL) {
			fprintf(stderr, "couldn't find fractBandwidth in probe file\n");
			return(0);
			}
		fractBandwidth = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "centerFrequency")) == NULL) {
			fprintf(stderr, "couldn't find centerFreq in probe file\n");
			return(0);
			}
		centerFreq = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noElementsY")) == NULL) {
			fprintf(stderr, "couldn't find noElementsY in probe file\n");
			return(0);
			}
		noElementsY = jsonTemp->valuedouble;

		Th = xdc_focused_multirow(noElements, width, noElementsY, &height,
			kerf, kerf, Rfocus, noSubX, noSubY, params.focusM);
		if (Th == NULL) {
			fprintf(stderr, "error calling xdc_focused_multirow\n");
			return(0);
			}
		}

	else if (strstr(params.transducerType, "focused_array") != NULL) {

		if (verbose >= 1) fprintf(stderr, "calling xdc_focused_array\n");

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noElements")) == NULL) {
			fprintf(stderr, "couldn't find noElements in probe file\n");
			return(0);
			}
		noElements = jsonTemp->valueint;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noSubX")) == NULL) {
			fprintf(stderr, "couldn't find noSubX in probe file\n");
			return(0);
			}
		noSubX = jsonTemp->valueint;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "noSubY")) == NULL) {
			fprintf(stderr, "couldn't find noSubY in probe file\n");
			return(0);
			}
		noSubY = jsonTemp->valueint;

		if (verbose >= 2) fprintf(stderr, "elements %d subX %d subY %d\n", noElements,
			noSubX, noSubY);

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "width")) == NULL) {
			fprintf(stderr, "couldn't find width in probe file\n");
			return(0);
			}
		width = jsonTemp->valuedouble;

		if (verbose >= 2) fprintf(stderr, "width %f\n", width);

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "height")) == NULL) {
			fprintf(stderr, "couldn't find height in probe file\n");
			return(0);
			}
		height = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "kerf")) == NULL) {
			fprintf(stderr, "couldn't find kerf in probe file\n");
			return(0);
			}
		kerf = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "Rfocus")) == NULL) {
			fprintf(stderr, "couldn't find Rfocus in probe file\n");
			return(0);
			}
		Rfocus = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "fractionalBandwidth")) == NULL) {
			fprintf(stderr, "couldn't find fractBandwidth in probe file\n");
			return(0);
			}
		fractBandwidth = jsonTemp->valuedouble;

		if ((jsonTemp = cJSON_GetObjectItem(probeInfo, "centerFrequency")) == NULL) {
			fprintf(stderr, "couldn't find centerFreq in probe file\n");
			return(0);
			}
		centerFreq = jsonTemp->valuedouble;

		if (verbose >= 2) fprintf(stderr, "type %s\n", cJSON_GetObjectItem(probeInfo, "probeType")->valuestring);


		if (verbose >= 2) fprintf(stderr, "%d %f %f %f %f %f %d %d %f %f %f\n",
			noElements, width, height, kerf, Rconvex, Rfocus, noSubX,
			noSubY, params.focusM.x, params.focusM.y, params.focusM.z);

		Th = xdc_focused_array(noElements, width, height, kerf,
			Rfocus, noSubX, noSubY, params.focusM);
		if (Th == NULL) {
			fprintf(stderr, "error calling xdc_focused_array\n");
			return(0);
			}
		if (verbose >= 2) fprintf(stderr, "xdc_focused_array; info: %s %s\n",
			Th->information.name, Th->information.create_date);
		}

	else fprintf(stderr, "unknown aperture command\n");


/*
 * I think the next thing is to set impulse. this seems to be the same for
 * all the apertures. the matlab code calls defineImpulseResponse() which
 * calls the matlab routine 'gauspuls', but since I had to write my own
 * I'm going to skip defineImpulseResponse()
 */

	if (strcmp(params.impulse, "gaussian") == 0) {
		impulseResponse = gaussPulse(fractBandwidth, centerFreq, params,
			verbose);

		if (impulseResponse == NULL) {
			fprintf(stderr, "error calling gaussPulse\n");
			return(0);
			}
		}

	else if (strcmp(params.impulse, "exp") == 0) {

		fprintf(stderr, "calling readExpData\n");
		numExpPnts = readExpData(probeInfo, &timeValues, &voltageValues,
			verbose);

		fprintf(stderr, "numExpPnts %d\n", numExpPnts);
/*
		for (i = 0; i < numExpPnts; i++)
			fprintf(stderr, "%e\n", voltageValues[i]);
*/

		impulseResponse = formatExpImpResp(numExpPnts, timeValues,
			voltageValues, params.samplingFrequencyHz, verbose);

		if (impulseResponse == NULL) {
			fprintf(stderr, "error calling formatExpImpResp\n");
			return(0);
			}
		}

	info = RECT;

/*
 * note that 'ROWS*' is specific to the type of info you request from xdc_get
 */

	xdcGetSize = ROWS_RECT * noElements * noSubY;

	if (verbose >= 1) fprintf(stderr, "calling xdc_get; size is %d\n", xdcGetSize);

	if ((params.ThData = (double *)malloc(xdcGetSize * sizeof(double))) == NULL) {
		fprintf(stderr, "couldn't allocate space for ThData\n");
		return(0);
		}

	xdc_get(Th, info, params.ThData);

	if (verbose >= 1) fprintf(stderr, "back from xdc_get\n");

	if (verbose >= 2) {
		fprintf(stderr, "num apertures from sys_con %d\n",
			sys_con->No_apertures);
		fprintf(stderr, "rect? %d\n", sys_con->Use_rectangles);
		fprintf(stderr, "tri? %d\n", sys_con->Use_triangles);

		fprintf(stderr, "back from xdc_get, got %f %f %f\n", params.ThData[7],
			params.ThData[8], params.ThData[9]);

		if (verbose == 3)
			for (i = 0; i < 26 * noElements * noSubX * noSubY; i += 26) {
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
	
	if (verbose >= 1) fprintf(stderr, "calling cAL\n");

	lensCorrection = correctAxialLens(params.ThData, ROWS_RECT,
		noElements * noSubY, verbose); 

	if (lensCorrection == -1) return(0);

	if (verbose >= 1) fprintf(stderr, "back from cAL, correction %g\n", lensCorrection);

	if (verbose >= 2) for (i = 0; i < 10; i++)
		fprintf(stderr, "uncorrected z %g\n", params.pointsAndNodes[i].z);

	for (i = 0; i < numNodes; i++)
		params.pointsAndNodes[i].z += lensCorrection;
	
	if (verbose >= 2) for (i = 0; i < 10; i++)
		fprintf(stderr, "corrected z %g\n", params.pointsAndNodes[i].z);

/* define the impulse response */

	xdc_impulse(Th, impulseResponse);

	exciteFreqHz = params.frequencyMHz * 1000000;
	stepSize = 1.0 / params.samplingFrequencyHz;

	if (verbose >= 1) fprintf(stderr, "params.frequencyMHz %f exciteFreqHz %f stepSize %g\n",
		params.frequencyMHz, exciteFreqHz, stepSize);

	numSteps = (int )ceil ((double )numCYC / exciteFreqHz / stepSize);

	excitationPulse = alloc_signal(numSteps, 0);

	if (excitationPulse == NULL) {
		fprintf(stderr, "couldn't allocate excitationPulse\n");
		return(0);
		}

	if (verbose >= 1) fprintf(stderr, "setting excitationPulse; numSteps %d\n", numSteps);

	temp = 2 * M_PI * exciteFreqHz * stepSize;

	for (i = 0; i < numSteps; i++) {
		excitationPulse->data[i] = sin(i * temp);
		if (verbose >= 2) fprintf(stderr, "data %g\n", excitationPulse->data[i]);
		}

	if (verbose >= 1) fprintf(stderr, "calling excitation\n");
	if (verbose >= 2) {
		fprintf(stderr, "before call %d %d\n", Th->excitation->allocated,
			Th->excitation->no_samples);

		for (i = 0; i < 30; i++)
			fprintf(stderr, "got %f\n", Th->excitation->data[i]);
		}

	xdc_excitation(Th, excitationPulse);

	if (verbose >= 1) fprintf(stderr, "back from excitation\n");
	if (verbose >= 2) {
		fprintf(stderr, "got %d %d\n", Th->excitation->allocated,
			Th->excitation->no_samples);

		for (i = 0; i < Th->excitation->no_samples; i++)
			fprintf(stderr, "got %f\n", Th->excitation->data[i]);
		}

/* frequency atten. in dB/m/Hz */
	freqAtt = params.alpha_dBcmMHz * 100 / 1E6;

	attF0 = exciteFreqHz;
	att = freqAtt * attF0; /* set non freq. dep. to be centered here */
	set_field("att", att);
	set_field("Freq_att", freqAtt);
	set_field("att_f0", attF0);
	set_field("use_att", 1);

	if (verbose >= 1) fprintf(stderr, "freqAtt %g attF0 %g att %g\n", freqAtt, attF0,
		att);

/*
% compute Ispta at each location for a single tx pulse
% optimizing by computing only relevant nodes... will assume others are zero
 *
 * how many points does calc_hp return?
 *
 */

	if (verbose >= 1) fprintf(stderr, "calling calc_hp; numNodes %d\n", numNodes);

	if (verbose >= 2) field_info;

/*
 * calc_hp just wants the xyz coordinates, but pointsAndNodes includes the
 * node id. may not need the id, but for now I'm going to make a copy.
 */

	if ((points = (point_type *)malloc(numNodes * sizeof(point_type))) == NULL) {
		fprintf(stderr, "couldn't allocate space for points\n");
		return(0);
		}

	for (i = 0; i < numNodes; i++) {
		points[i].x = params.pointsAndNodes[i].x;
		points[i].y = params.pointsAndNodes[i].y;
		points[i].z = params.pointsAndNodes[i].z;
		
		if (verbose >= 2) fprintf(stderr, "x %f, y %f, z %f\n", points[i].x,
			points[i].y, points[i].z);
		}

/* have to init intensity to 0 so we can sum into it */

	if ((intensity = (double *)calloc(numNodes, sizeof(double))) == NULL) {
		fprintf(stderr, "couldn't allocate space for intensity\n");
		return(0);
		}

	if (lowNslow) {
		if (verbose >= 1) fprintf(stderr, "running low-n-slow\n");
		for (i = 0; i < numNodes; i++) {
			if (verbose >= 2) fprintf(stderr, "i %d\n", i);

			pressure = calc_hp(Th, 1, &points[i]);
			if (pressure == NULL) {
				fprintf(stderr, "call to calc_hp failed\n");
				return(0);
				}

			if (verbose == 3) fprintf(stderr, "num samples %d\n",
				pressure[0]->no_samples);
			if (verbose == 3) for (j = 0; j < pressure[0]->no_samples; j++)
				fprintf(stderr, "pressure %g\n", pressure[0]->data[j]);
			for (j = 0; j < pressure[0]->no_samples; j++)
				intensity[i] += pressure[0]->data[j] * pressure[0]->data[j];
			free_signal(pressure[0]);
			}
		}
	else {
		pressure = calc_hp(Th, numNodes, points);

		if (pressure == NULL) {
			fprintf(stderr, "call to calc_hp failed\n");
			return(0);
			}

		for (i = 0; i < numNodes; i++)
			for (j = 0; j < pressure[i]->no_samples; j++)
				intensity[i] += pressure[i]->data[j] * pressure[i]->data[j];
		}

	if (verbose >= 2) for (i = 0; i < numNodes; i++)
		fprintf(stderr, "intensity %g\n", intensity[i]);

	if (verbose >= 1) fprintf(stderr, "done with calc_hp; num samples at 0 %d\n",
		pressure[0]->no_samples);

	if (verbose == 3) for (j = 0; j < pressure[0]->no_samples; j++)
			fprintf(stderr, "%g\n", pressure[0]->data[j]);

	if (verbose == 3) for (i = 0; i < numNodes; i++) {
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
 *	int soundSpeed_MperSec
 *	int samplingFrequencyHz
 *	double alpha_dBcmMHz
 *	double fnum
 *	point_type focusM (struct of three doubles)
 *	double frequency
 *  length of transducer character string, int
 *  transducer, character string
 *  length of impulse character string, int
 *	impulse, character string
 *	pointsAndNodes, which is numNodes nodeEntry structs (one int,
 *		three doubles)
 *	int ROWS * noElements * noSubY
 *	ThData, which is ROWS * noElements * noSubY doubles. ROWS is a constant
 *		determined by the return of 'xdc_get, and noElements, noSubY come
 *		from the probe description file. in our case, it appears that we only
 *		care about rectangles.
 */

	sprintf(outFileName, "dyna-I-f%.2f-F%.1f-FD%.3f-a%.2f.new",
		params.frequencyMHz, params.fnum, params.focusM.z, params.alpha_dBcmMHz);

	if (verbose >= 1) fprintf(stderr, "file name %s\n", outFileName);

	if (dynaWrite(outFileName, intensity, params, numNodes, xdcGetSize, verbose) == -1) {
		fprintf(stderr, "dynaWrite failed\n");
		return(0);
		}

	return(1);

}
