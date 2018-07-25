/*
% function [dynaImat] = field2dyna(NodeName, alpha, Fnum, focus, Frequency,
%	Transducer, Impulse, threads, lownslow, ElemName, verbose)
%
% INPUT:
%   NodeName (string) - file name to read nodes from (e.g., nodes.dyn); needs
%                       to be a comma-delimited file with header/footer lines
%                       that start with '*'
%   alpha_dBcmMHz - 0.5, 1.0, etc. (dB/cm/MHz)
%   Fnum - F/# (e.g. 1.3)
%   focusM - [x y z] (meters) "Field" coordinates
%   Frequency - excitation frequency (MHz)
%   Transducer (string) - 'vf105','vf73'
%   Impulse (string) - 'gaussian','exp'
%   threads (int) - number of parallel threads to use for Field II Pro
%   lownslow (bool) - low memory footprint, or faster parallel (high RAM)
%		[default = 0]
%   ElemName (string) - file name to read elements from (default: elems.dyn);
%                       like node file, needs to be comma-delimited.
%
% OUTPUT:
%   dyna-I-*.mat file is saved to CWD and filename string returned
%
% EXAMPLE:
% dynaImatfile = field2dyna('nodes.dyn', 0.5, 1.3, [0 0 0.02], 7.2, 'vf105',
%	'gaussian', ..., 12, 'elems.dyn', 1);
%
% Mark Palmeri
% mlp6@duke.edu
% 2015-03-17
%
* Ned Danieley
*
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "field.h"

int checkOnAxis();

char *
field2dyna(char *nodeName, double alpha_dBcmMHz, double fnum, point_type focusM,
	double freqMHz, char *transducer, char *impulse, int threads, int lowNslow,
	char *elemName, int verbose)
{
int dynaField();
int i, numNodes;
int isUniform;
double temp;
struct nodeEntry *pointsAndNodes, *readMpn();
struct FieldParams fieldParams;
char nodeVolFileName[80];
char calcNodeVolCmd[80];
int status;

	fprintf(stderr, "in field2dyna, verbose %d\n", verbose);

	if (verbose >= 1) {
		fprintf(stderr, "in field2dyna, calling readMpn; node name %s\n",
			nodeName);
		fprintf(stderr, "in field2dyna, alpha_dBcmMHz %f fnum %f freqMHz %f\n",
			alpha_dBcmMHz, fnum, freqMHz);
		fprintf(stderr, "in field2dyna, focus x %f y %f z %f \n", focusM.x,
			focusM.y, focusM.z);
		fprintf(stderr, "in field2dyna, transducer %s\n", transducer);
		fprintf(stderr, "in field2dyna, impulse %s\n", impulse);
		fprintf(stderr, "in field2dyna, threads %d\n", threads);
		fprintf(stderr, "in field2dyna, lowNslow %d\n", lowNslow);
		fprintf(stderr, "in field2dyna, element name %s\n", elemName);
		fprintf(stderr, "in field2dyna, verbose %d\n", verbose);
		}

	pointsAndNodes = readMpn(nodeName, &numNodes, verbose);
	if (pointsAndNodes == NULL) {
		fprintf(stderr, "didn't get enough values from readMpn\n");
		exit(0);
		}

	if (verbose >= 1) fprintf(stderr, "after readMpn; numNodes %d\n", numNodes);

	if (verbose == 3) for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 1, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);

	if (!checkOnAxis(pointsAndNodes, numNodes)) {
		fprintf(stderr, "There are no nodes in the lateral / elevation plane = 0 (imaging plane).\n");
		fprintf(stderr, "This can lead to inaccurate representations of the intensity fields!!')\n");
		}

	if (verbose == 3) for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 2, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);

/* invert the z axis */
	for (i = 0; i < numNodes; i++) pointsAndNodes[i].z = -pointsAndNodes[i].z;

	if (verbose == 3) for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 3, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);

/* switch x and y */
	for (i = 0; i < numNodes; i++) {
		temp = pointsAndNodes[i].x;
		pointsAndNodes[i].x = pointsAndNodes[i].y;
		pointsAndNodes[i].y = temp;
		}
	if (verbose == 3) for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 4, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);


/* change from centimeters to meters */
	for (i = 0; i < numNodes; i++) {
		pointsAndNodes[i].x /= 100;
		pointsAndNodes[i].y /= 100;
		pointsAndNodes[i].z /= 100;
		}

	if (verbose == 3) for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 5, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);

/* populate structure for dynaField */

	fieldParams.pointsAndNodes = pointsAndNodes;
	fieldParams.alpha_dBcmMHz = alpha_dBcmMHz;
	fieldParams.fnum = fnum;
	fieldParams.focusM = focusM;
	fieldParams.frequencyMHz = freqMHz;
	fieldParams.transducer = transducer;
	fieldParams.impulse = impulse;
	fieldParams.soundSpeed_MperSec = 1540;
	fieldParams.samplingFrequencyHz = 100e6;
	fieldParams.threads = threads;

	if (verbose >= 1) fprintf(stderr, "in field2dyna, focus x %f y %f z %f\n", fieldParams.focusM.x, fieldParams.focusM.y, fieldParams.focusM.z);

/* call dynaField here */

	if (dynaField(fieldParams, threads, numNodes, lowNslow, verbose) == 0) {
		fprintf(stderr, "in field2dyna, call to dynaField failed\n");
		exit(0);
		}
}
