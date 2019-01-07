#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <math.h>
#include <gsl/gsl_interp.h>
#include "field.h"

#define StartTest -4E-7
#define StopTest 4E-7

signal_type *
formatExpImpResp(int numPnts, double *timeValues, double *voltageValues,
	int samplingFrequencyHz, int verbose)
{
double *newTimeValues;
double *newVoltageValues;
double timeAtMaxIntensity;
double minTime = DBL_MIN;
double maxTime = -DBL_MIN;
double maxVoltage = -DBL_MIN;
double stepSize;
int i, j, maxVoltageIndex, numSteps;
int startIndex, stopIndex;
signal_type *impulseResponse;
int pntsSampled;

/* find the max voltage */

	for (i = 0; i < numPnts; i++) {
		if (maxVoltage < voltageValues[i]) {
			maxVoltage = voltageValues[i];
			maxVoltageIndex = i;
			}
		}

	if (verbose >= 1) fprintf(stderr, "index %d max voltage %e\n",
		maxVoltageIndex, maxVoltage);

/* normalize the voltages */

	for (i = 0; i < numPnts; i++)
		voltageValues[i] /= maxVoltage;


/*
 * center the time axis around the max intensity. the matlab code recalculated
 * the index of the maximum value, but the normalization shouldn't change
 * that, so I skipped it. note that I have to save the time associated with
 * the max intensity, because in the time array, it goes to 0 as I do the
 * centering.
 */

	timeAtMaxIntensity = timeValues[maxVoltageIndex];

	for (i = 0; i < numPnts; i++)
		timeValues[i] = timeValues[i] - timeAtMaxIntensity;

/* now find the min and max times */

	for (i = 0; i < numPnts; i++) {
		if (minTime > timeValues[i]) minTime = timeValues[i];

		if (maxTime < timeValues[i]) maxTime = timeValues[i];
		}

	if (verbose >= 1) fprintf(stderr, "min time %e max time %e\n", minTime,
		maxTime);

/* re-sample the data to match the Field II sampling frequency */

	if (verbose >= 1) fprintf(stderr, "sampling %d\n", samplingFrequencyHz);
	stepSize = 1.0 / samplingFrequencyHz;

	if (verbose >= 1) fprintf(stderr, "diff %e\n", maxTime - minTime);
	numSteps = (int )ceil(((maxTime - minTime) * samplingFrequencyHz));

	if (verbose >= 1) fprintf(stderr, "step size %e numSteps %d\n", stepSize, numSteps);

	if ((newTimeValues = (double *)malloc(sizeof(double) * numSteps)) == NULL) {
		fprintf(stderr, "in readExpData, couldn't allocate space for new times\n");
		return(0);
		}

	for (i = 0; i < numSteps; i++) {
		newTimeValues[i] = minTime + i * stepSize;
		}

/*
 * now we find the voltage values at each of the new times by interpolating
 * from the old times and voltages.
 */

/* initialize and allocate the gsl objects */

	gsl_interp *interpolation = gsl_interp_alloc (gsl_interp_linear, numPnts);

	gsl_interp_init(interpolation, timeValues, voltageValues, numPnts);

	gsl_interp_accel * accelerator =  gsl_interp_accel_alloc();

/* get interpolation the new times */

	if ((newVoltageValues = (double *)malloc(sizeof(double) * numSteps)) == NULL) {
		fprintf(stderr, "in readExpData, couldn't allocate space for new voltage\n");
		return(0);
		}

	for (i = 0; i < numSteps; i++) {
		newVoltageValues[i] = gsl_interp_eval(interpolation, timeValues,
			voltageValues, newTimeValues[i], accelerator);

		if (verbose >= 3) fprintf(stderr, "\n%e", newVoltageValues[i]);
		}

/* find the indices of NewTime to use for the Field II impulse response */

	for (i = 0; i < numSteps; i++) {
		if (newTimeValues[i] > StartTest) {
			startIndex = i;
			break;
			}
		}

	for (i = 0; i < numSteps; i++)
		if (newTimeValues[i] > StopTest) {
			stopIndex = i;
			break;
			}

	pntsSampled = stopIndex - startIndex;

	if (verbose >= 1) fprintf(stderr,
		"\nstartIndex %d, stopIndex %d pntsSampled %d\n", startIndex,
		stopIndex, pntsSampled);

	impulseResponse = alloc_signal(pntsSampled, 0);

	for (i = startIndex, j = 0; i < stopIndex; i++, j++) {
		impulseResponse->data[j] = newVoltageValues[i];
		if (verbose >= 3) fprintf(stderr, "%e\n", newVoltageValues[i]);
		}

	return(impulseResponse);
}
