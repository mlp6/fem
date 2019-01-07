/*
function [impulseResponse]=defineImpResp(fBW,Fc,FIELD_PARAMS);
% function [impulseResponse]=defineImpResp(fBW,Fc,FIELD_PARAMS);
% Define the impulse reponse of the array, either using a Gaussian or
% experimentally-measured data.
%
% INPUTS:
%   fBW (float) - fractional bandwidth
%   Fc (float) - center frequency (Hz)
%   FIELD_PARAMS (struct) - Field II parameters
%
% OUTPUTS:
%   impulseResponse (float vector) - impulse response at the specified sampling
%   frequency
%
% Mark 06/20/07
%
% Ned 3/30/2018
*/

#include <stdio.h>
#include <string.h>
#include "field.h"

double *
defineImpulseResponse(double fBW, double fc, struct FieldParams params)
{

	if (strstr(params.impulse, "gaussian") != NULL) {
		fprintf(stderr, "Impulse Response: Gaussian\n");
		return(gaussPulse(fBW, fc, params));
		}

	else if (strstr(params.impulse, "exp")) {
		fprintf(stderr, "Impulse Response: Experimental\n");
		return(NULL);
		}
}
