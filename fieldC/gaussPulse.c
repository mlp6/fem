/*
 * try to compute the gaussian-modulated sinusoidal
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "field.h"

gaussPulse(double fbw, double fc, struct FieldParams params)
{
double fv, power, ref;
double tc, delta, tv;
double impulse, *impulseResponse, stepSize;
double freq;
double ye, yc;
int i, numSteps;

/*
	fprintf(stderr, "in pulse; fbw %f fc %f\n", fbw, fc);
	fprintf(stderr, "in pulse; params.impulse %s\n", params.impulse);
 */

	if (strstr(params.impulse, "gaussian")) {

/* first calculate the cutoff frequency */

		power = -6.0/20;
		ref = pow(10.0, power);

		power = -40./20;
		delta = pow(10.0, power);

		fv = -pow((fc * fbw), 2) / (8.0 * log(ref));
		tv = 1 / (4 * M_PI * M_PI * fv);

		fprintf(stderr, "got gaussian; ref %f, delta %f, a %f\n", ref, delta, fv);

		tc = sqrt(-2 * tv * log(delta));
		fprintf(stderr, "tc %f\n", tc);

/* 		params.samplingFrequency = 5000; */
		numSteps = (int) (tc * params.samplingFrequency) * 2;
		freq = (double) params.samplingFrequency;

		fprintf(stderr, "freq %f, numSteps %d\n", freq, numSteps);

		impulseResponse = (double *)malloc(numSteps * sizeof(double));
		stepSize = 1.0/params.samplingFrequency;

		impulse = -tc;
		fprintf(stderr, "starting loop, stepSize %e\n", stepSize);

		impulse = -tc;
		ye = exp(-impulse * impulse / (2 * tv));
		impulseResponse[0] = ye * cos(2 * M_PI * fc * impulse);

		fprintf(stderr, "impulse %f, ye %f, yc %f\n", impulse, ye, impulseResponse[0]);
		for (i = 1; i < numSteps; i++) {
			impulse = -tc + i * stepSize;
			ye = exp(-impulse * impulse / (2 * tv));
			impulseResponse[i] = ye * cos(2 * M_PI * fc * impulse);
			fprintf(stderr, "impulse %f, ye %f, yc %f\n", impulse, ye, impulseResponse[i]);
			}
		fprintf(stderr, "finished loop\n");
		}

	if (strstr(params.impulse, "exp")) {
		fprintf(stderr, "got exp\n");
		}
}
			
