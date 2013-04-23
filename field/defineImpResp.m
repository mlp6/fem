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

switch FIELD_PARAMS.Impulse
    case 'gaussian',
        disp('Impulse Response: Gaussian');
        tc = gauspuls('cutoff',Fc,fBW,-6,-40);
        t = -tc:1/FIELD_PARAMS.samplingFrequency:tc;
        impulseResponse =gauspuls(t,Fc,fBW);
    case 'exp',
        disp('Impulse Response: Experimental');
        [impulseResponse]=formatExpImpResp(FIELD_PARAMS);
end;
