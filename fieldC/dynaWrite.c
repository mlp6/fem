#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "field.h"

dynaWrite(char *outFileName, double *intensity, struct FieldParams params, int numNodes, int xdcGetSize)
{
int i;
FILE *outptr;

fprintf(stderr, "output file %s\n", outFileName);

/* open output file */

    if ((outptr = fopen(outFileName, "wb")) == NULL) {
		fprintf(stderr, "couldn't open output file %s\n", outFileName);
		exit(EXIT_FAILURE);
		}

	if (fwrite(&numNodes, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write numNodes\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(intensity, sizeof(double), numNodes, outptr) != numNodes) {
		fprintf(stderr, "failed to write intensity\n");
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

/* not saving null character for transducer or impulse */

	i = strlen(params.transducer);

	if (fwrite(&i, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "failed to write length of transducer string\n");
		exit(EXIT_FAILURE);
		}

	if (fwrite(params.transducer, sizeof(char), i, outptr) != i) {
		fprintf(stderr, "failed to write transducer\n");
		exit(EXIT_FAILURE);
		}

	i = strlen(params.impulse);

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
