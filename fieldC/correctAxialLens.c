/*
% function lens_correction_m = correct_axial_lens(thData)
% 
% INPUTS:   thData - array of values from Field II xdc_get(Th, 'rect')
%
% OUTPUTS:  lens_correction_m (float) - axial shift of the center of the center
%                                       element (m)
*/

#include <stdio.h>
#include <limits.h>

double
correctAxialLens(double *thData, int rows, int numPoints, int debug)
{
int i;
/*
 * the array returned by xdc_get for the RECT case has x, y, and z at
 * 8, 9 and 10, which for a C array is 7, 8, 9.
 */
int xPosLoc = 7;
int zPosLoc = 9;
double correction;
int indexMin;

/* find center element */

	if (debug) fprintf(stderr, "in correctAxialLens, rows %d, numPoints %d\n",
		rows, numPoints);

	for (i = 0; i < numPoints; i++) {
		if (thData[rows * i + xPosLoc] >= 0) {
				indexMin = i;
				break;
				}
			}

	if (debug) fprintf(stderr, "in correctAxialLens, indexMin %d\n", indexMin);
	correction = thData[rows * indexMin + zPosLoc];
	if (debug) fprintf(stderr, "in correctAxialLens, correction %g\n", correction);
	return(correction);
}
