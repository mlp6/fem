#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "field.h"

dynaWrite(char *outFileName, double *intensity, struct FieldParams params, int numNodes, int xdcGetSize, int verbose)
{
int i;
FILE *outptr;

	if (verbose >= 1) fprintf(stderr, "output file %s\n", outFileName);

/* open output file */

    if ((outptr = fopen(outFileName, "wb")) == NULL) {
		fprintf(stderr, "dynaWrite: couldn't open output file %s\n", outFileName);
		return(-1);
		}

	if (fwrite(&numNodes, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write numNodes\n");
		return(-1);
		}

	if (fwrite(intensity, sizeof(double), numNodes, outptr) != numNodes) {
		fprintf(stderr, "dynaWrite: failed to write intensity\n");
		return(-1);
		}

	if (fwrite(&params.threads, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write threads\n");
		return(-1);
		}

	if (fwrite(&params.soundSpeed_MperSec, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write soundSpeed\n");
		return(-1);
		}

	if (fwrite(&params.samplingFrequencyHz, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write samplingFrequencyHz\n");
		return(-1);
		}

	if (fwrite(&params.alpha_dBcmMHz, sizeof(double), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write alpha_dBcmMHz\n");
		return(-1);
		}

	if (fwrite(&params.fnum, sizeof(double), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write fnum\n");
		return(-1);
		}

	if (fwrite(&params.focusM, sizeof(point_type), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write focus\n");
		return(-1);
		}

	if (fwrite(&params.frequencyMHz, sizeof(double), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write frequency\n");
		return(-1);
		}

/* not saving null character for transducer or impulse */

	i = strlen(params.transducer);

	if (fwrite(&i, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write length of transducer string\n");
		return(-1);
		}

	if (fwrite(params.transducer, sizeof(char), i, outptr) != i) {
		fprintf(stderr, "dynaWrite: failed to write transducer\n");
		return(-1);
		}

	i = strlen(params.impulse);

	if (fwrite(&i, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write length of impulse string\n");
		return(-1);
		}

	if (fwrite(params.impulse, i, 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write impulse\n");
		return(-1);
		}

	if (fwrite(params.pointsAndNodes, sizeof(struct nodeEntry), numNodes, outptr) != numNodes) {
		fprintf(stderr, "dynaWrite: failed to write points and nodes\n");
		return(-1);
		}

	if (fwrite(&xdcGetSize, sizeof(int), 1, outptr) != 1) {
		fprintf(stderr, "dynaWrite: failed to write size of xdc_get\n");
		return(-1);
		}

/*
*/
	if (fwrite(params.ThData, sizeof(double), xdcGetSize, outptr) != xdcGetSize) {
		fprintf(stderr, "dynaWrite: failed to write ThData\n");
		return(-1);
		}

	fclose(outptr);

	return(1);
}
