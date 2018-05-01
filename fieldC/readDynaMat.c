#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "field.h"		/* includes field_II.h */

#define RECT 1	/* type of info we want from xdc_get */
#define ROWS_RECT 26	/* rows xdc_get returns for each rectangle */
#define ROWS_TRI 15	/* rows xdc_get returns for each triangle */

sys_con_type   *sys_con;      /*  System constants for Field II */ 

void
main()
{
int i, length, xdcGetSize;
char c[4];
char c1;
char inFileName[80];
char temp[80];
FILE *inptr;
struct FieldParams params;
int numNodes;
double *intensity;

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
 *	transducer length and character string
 *	impulse length and character string
 *	pointsAndNodes, which is numNodes nodeEntry structs (one int,
 *		three doubles)
 *	int ROWS * no_elements * no_sub_y
 *	ThData, which is ROWS * no_elements * no_sub_y doubles. ROWS is a constant
 *		determined by the return of 'xdc_get, and no_elements, no_sub_y come
 *		from the probe description file. in our case, it appears that we only
 *		care about rectangles.
 */

	sprintf(inFileName, "dyna-I-f7.20-F1.3-FD0.020-a0.50.ned");

	fprintf(stderr, "file name %s\n", inFileName);

/* open input file */

    if ((inptr = fopen(inFileName, "rb")) == NULL) {
		fprintf(stderr, "couldn't open input file %s\n", inFileName);
		exit(EXIT_FAILURE);
		}

	if (fread(&numNodes, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read numNodes\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "numNodes %d\n", numNodes);

	if (fread(&params.threads, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read threads\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.threads %d\n", params.threads);

	if (fread(&params.soundSpeed, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read soundSpeed\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.soundSpeed %d\n", params.soundSpeed);

	if (fread(&params.samplingFrequency, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read samplingFrequency\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.samplingFrequency %d\n", params.samplingFrequency);

	intensity = (double *)malloc(sizeof(double) * numNodes);

	if (fread(intensity, sizeof(double), numNodes, inptr) != numNodes) {
		fprintf(stderr, "failed to read intensity\n");
		exit(EXIT_FAILURE);
		}

	for (i = 0; i < numNodes; i++)
		fprintf(stderr, "intensity %g\n", intensity[i]);

	if (fread(&params.alpha, sizeof(double), 1, inptr) != 1) {
		fprintf(stderr, "failed to read alpha\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.alpha %f\n", params.alpha);

	if (fread(&params.fnum, sizeof(double), 1, inptr) != 1) {
		fprintf(stderr, "failed to read fnum\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.fnum %f\n", params.fnum);

	if (fread(&params.focus, sizeof(point_type), 1, inptr) != 1) {
		fprintf(stderr, "failed to read focus\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.focus %f %f %f\n", params.focus.x, params.focus.y,
		params.focus.z);

	if (fread(&params.frequency, sizeof(double), 1, inptr) != 1) {
		fprintf(stderr, "failed to read frequency\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.frequency %f\n", params.frequency);

	if (fread(&length, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read transducer length\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "transducer length %d\n", length);

	if (fread(temp, sizeof(char), length, inptr) != length) {
		fprintf(stderr, "failed to read transducer\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "temp %s\n", temp);
	params.transducer = temp;
	fprintf(stderr, "trans %s\n", params.transducer);

	if (fread(&length, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read impulse length\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "impulse length %d\n", length);

	if (fread(temp, sizeof(char), length, inptr) != length) {
		fprintf(stderr, "failed to read impulse\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "temp %s\n", temp);
	params.impulse = temp;
	fprintf(stderr, "impulse %s\n", params.impulse);

	fprintf(stderr, "params.impulse %s\n", temp);

	params.pointsAndNodes = (struct nodeEntry *)malloc(sizeof(struct nodeEntry) * numNodes);

	if (fread(params.pointsAndNodes, sizeof(struct nodeEntry), numNodes, inptr) != numNodes) {
		fprintf(stderr, "failed to read points and nodes\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.pointsAndNodes %d %f %f %f\n", params.pointsAndNodes[1].nodeID, params.pointsAndNodes[1].x, params.pointsAndNodes[1].y, params.pointsAndNodes[1].z);

	if (fread(&xdcGetSize, sizeof(int), 1, inptr) != 1) {
		fprintf(stderr, "failed to read size of xdc_get\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "xdcGetSize %d\n", xdcGetSize);

/* 	if (fread(params.ThData, sizeof(double), ROWS_RECT * no_elements * no_sub_y, inptr) != ROWS_RECT * no_elements * no_sub_y) { */

	fprintf(stderr, "foo\n");
	params.ThData = (double *)malloc(sizeof(double) * xdcGetSize);

	if (params.ThData == NULL) {
		fprintf(stderr, "failed to allocate ThData\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "foo\n");
	if (fread(params.ThData, sizeof(double), xdcGetSize, inptr) != xdcGetSize) {
		fprintf(stderr, "failed to read ThData\n");
		exit(EXIT_FAILURE);
		}

	fprintf(stderr, "params.ThData %f %f %f\n", params.ThData[7], params.ThData[8], params.ThData[9]);
	fclose(inptr);
}
