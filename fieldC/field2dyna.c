/*
% function [dynaImat] = field2dyna(NodeName, alpha, Fnum, focus, Frequency,
%	Transducer, Impulse, threads, lownslow, ElemName, ForceNonlinear)
%
% INPUT:
%   NodeName (string) - file name to read nodes from (e.g., nodes.dyn); needs
%                       to be a comma-delimited file with header/footer lines
%                       that start with '*'
%   alpha - 0.5, 1.0, etc. (dB/cm/MHz)
%   Fnum - F/# (e.g. 1.3)
%   focus - [x y z] (m) "Field" coordinates
%   Frequency - excitation frequency (MHz)
%   Transducer (string) - 'vf105','vf73'
%   Impulse (string) - 'gaussian','exp'
%   threads (int) - number of parallel threads to use for Field II Pro
%   lownslow (bool) - low memory footprint, or faster parallel (high RAM)
%		[default = 0]
%   ElemName (string) - file name to read elements from (default: elems.dyn);
%                       like node file, needs to be comma-delimited.
%   ForceNonlinear(int) - optional input argument. Set as 1 if you want to
%                         force nodal volumes to be calculated.
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
% Ned Danieley
*/
#include <stdio.h>
#include <stdlib.h>
#include "field.h"

int checkOnAxis();

char *
field2dyna(char *nodeName, double alpha, double fnum, point_type focus,
	double freq, char *transducer, char *impulse, int threads,
	int lowNslow, char *elemName, int forceNonlinear)
{
int i, numNodes;
double temp;
struct nodeEntry *pointsAndNodes, *readMpn();
struct FieldParams fieldParams;

	fprintf(stderr, "in field2dyna, focus x %f fnum %f freq %f\n", focus.x, fnum, freq);
	fprintf(stderr, "in field2dyna, alpha %f fnum %f freq %f\n", alpha, fnum, freq);
	fprintf(stderr, "in field2dyna, threads %d\n", threads);
	fprintf(stderr, "in field2dyna, calling readMpn; node name %s\n", nodeName);
	fprintf(stderr, "in field2dyna, transducer %s\n", transducer);

	pointsAndNodes = readMpn(nodeName, &numNodes);

	fprintf(stderr, "after readMpn; numNodes %d\n", numNodes);

/*
	for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 1, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);
*/

	if (!checkOnAxis(pointsAndNodes, numNodes)) {
		fprintf(stderr, "There are no nodes in the lateral / elevation plane = 0 (imaging plane).\n");
		fprintf(stderr, "This can lead to inaccurate representations of the intensity fields!!')\n");
		}

/*
	for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 2, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);

*/
/* invert the z axis */
	for (i = 0; i < numNodes; i++) pointsAndNodes[i].z = -pointsAndNodes[i].z;

/*
	for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 3, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);

*/
/* switch x and y */
	for (i = 0; i < numNodes; i++) {
		temp = pointsAndNodes[i].x;
		pointsAndNodes[i].x = pointsAndNodes[i].y;
		pointsAndNodes[i].y = temp;
		}
/*
	for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 4, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);
e/


/* change from centimeters to meters */
	for (i = 0; i < numNodes; i++) {
		pointsAndNodes[i].x /= 100;
		pointsAndNodes[i].y /= 100;
		pointsAndNodes[i].z /= 100;
		}

/*
	for (i = 0; i < 13; i++)
	    fprintf(stderr, "field2dyna 5, node %d is %d, %f, %f, %f\n", i, pointsAndNodes[i].nodeID, pointsAndNodes[i].x, pointsAndNodes[i].y, pointsAndNodes[i].z);
*/

/* populate structure for dynaField */

	fieldParams.pointsAndNodes = pointsAndNodes;
	fieldParams.alpha = alpha;
	fieldParams.fnum = fnum;
	fieldParams.focus = focus;
	fieldParams.frequency = freq;
	fieldParams.transducer = transducer;
	fieldParams.impulse = impulse;
	fieldParams.soundSpeed = 1540;
	fieldParams.samplingFrequency = 100e6;
	fieldParams.threads = threads;

/*
 * at this point the matlab code sets up some defaults, because apparently
 * you can call a matlab function without passing all the arguments that it
 * excepts. can't do that in C.
 */

/* call dynaField here */

	dynaField(fieldParams, threads, lowNslow, numNodes);
}
