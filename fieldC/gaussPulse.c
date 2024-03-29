/*
 * try to compute the gaussian-modulated sinusoidal
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "field.h"

#define BWR -6.0
#define TPR -40.0

signal_type *
gaussPulse(double fbw, double fc, struct FieldParams params, int verbose)
{
double fv, power, ref;
double tc, delta, tv;
double impulse, stepSize;
signal_type *impulseResponse = NULL;
double freqHz;
double ye;
int i, numSteps;

	if (verbose >= 1) {
		fprintf(stderr, "in pulse; fbw %f fc %f\n", fbw, fc);
		fprintf(stderr, "in pulse; params.impulse %s\n", params.impulse);
		}

/*
 * if the impulse is gaussian, we compute the cutoff time and then the
 * gaussian response.
 */

	if (strstr(params.impulse, "gaussian")) {

/* first calculate the cutoff time */

/* Ref level (fraction of max peak) */
		power = BWR / 20;
		ref = pow(10.0, power);

/* variance is fv, mean is fc */

		fv = -pow((fc * fbw), 2) / (8.0 * log(ref));

/* Determine corresponding time-domain parameters: */

		tv = 1 / (4 * M_PI * M_PI * fv);

/* don't know what delta is */

		power = TPR / 20;
		delta = pow(10.0, power);

		if (verbose >= 2) fprintf(stderr, "got gaussian; ref %f, delta %f, fv %f, tv %g\n", ref, delta, fv, tv);

		tc = sqrt(-2 * tv * log(delta));
		if (verbose >= 2) fprintf(stderr, "tc %g\n", tc);

		if (verbose >= 2) fprintf(stderr, "sampling freqHz %d\n", params.samplingFrequencyHz);
		numSteps = (int )ceil((tc * params.samplingFrequencyHz) * 2);
		freqHz = (double) params.samplingFrequencyHz;

		if (verbose >= 2) fprintf(stderr, "freqHz %g, numSteps %d\n", freqHz, numSteps);

		impulseResponse = alloc_signal(numSteps, 0);

		if (impulseResponse == NULL) {
			fprintf(stderr, "error allocating impulseResponse\n");
			return(NULL);
			}

		stepSize = 1.0/params.samplingFrequencyHz;

		impulse = -tc;
		if (verbose >= 2) fprintf(stderr, "starting loop, stepSize %e\n", stepSize);

		impulse = -tc;
		ye = exp(-impulse * impulse / (2 * tv));
		impulseResponse->data[0] = ye * cos(2 * M_PI * fc * impulse);

		if (verbose >= 2) fprintf(stderr, "step 0 response %f\n", impulseResponse->data[0]);
		for (i = 1; i < numSteps; i++) {
			impulse = -tc + i * stepSize;
			ye = exp(-impulse * impulse / (2 * tv));
			impulseResponse->data[i] = ye * cos(2 * M_PI * fc * impulse);
			if (verbose == 3) fprintf(stderr, "step %d response %f\n", i, impulseResponse->data[i]);
			}
		if (verbose >= 2) fprintf(stderr, "finished loop\n");
		}

	if (strstr(params.impulse, "exp")) {
		fprintf(stderr, "got exp\n");
		}

	return(impulseResponse);
}
			
