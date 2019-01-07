#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gsl/gsl_interp.h>

int main (void)
{
//sample data
//double x[4] = { 1970, 1980, 1990, 2000 };
//double y[4] = {   12,   11,   14,   13 };
double x[500], y[500];
double newtimes[200];
FILE *input;
int i;

	if ((input = fopen("times", "r")) == NULL) {
		fprintf(stderr, "oops\n");
		exit(0);
		}

	for (i = 0; i < 500; i++) fscanf(input, "%lf", &x[i]);

	fclose(input);

/* 	for (i = 0; i < 500; i++) fprintf(stderr, "%e\n", x[i]); */

	input = fopen("volts", "r");

	for (i = 0; i < 500; i++) fscanf(input, "%lf", &y[i]);

	fclose(input);

	input = fopen("newtimes", "r");

	for (i = 0; i < 200; i++) fscanf(input, "%lf", &newtimes[i]);

	fclose(input);

//initialise and allocate the gsl objects

	gsl_interp *interpolation = gsl_interp_alloc (gsl_interp_linear,500);

	gsl_interp_init(interpolation, x, y, 500);
	gsl_interp_accel * accelerator =  gsl_interp_accel_alloc();

//get interpolation for x = 1981

	for (i = 0; i < 200; i++) {
		double value = gsl_interp_eval(interpolation, x, y, newtimes[i],
			accelerator);

		printf("\n%g",value);
		}

//output:
//11.3

return 0;
}
