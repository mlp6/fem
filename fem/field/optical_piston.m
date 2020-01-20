function [Th,impulseResponse]=drug_piston(FIELD_PARAMS);
% function [Th,impulseResponse]=drug_piston(FIELD_PARAMS);
%
% create 'Th' transducer handle and define the fractional bandwidth for the
% drug delivery piston (NIH) for use by dynaField.m; also define the impulse
% response
%
% Mark 06/20/07

disp('Transducer: Optical Shear Wave (Richard)');

% piston focus and radius
focus=38.0e-3;
radius=9.5e-3;

% mathematical element size
ele_size=0.5e-3;

% define the transducer handle
Th = xdc_concave(radius,focus,ele_size);

% define the fractional bandwidth & center frequency 
fractionalBandwidth = 0.35;
centerFrequency = 5.0e6;

% compute and load the experimentally-measured impulse response
[impulseResponse]=defineImpResp(fractionalBandwidth,centerFrequency,FIELD_PARAMS);
