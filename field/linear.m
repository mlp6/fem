function [Th,impulseResponse]=linear(FIELD_PARAMS);
% function [Th,impulseResponse]=linear(FIELD_PARAMS);
%
% Create 'Th' transducer handle and define the fractional bandwidth for a
% typical linear array
% 
% Mark Palmeri
% mlp6@duke.edu
% 2014-08-07

disp('Transducer: Linear');
no_elements_y=1;
width=.2e-3;
kerf=0.02e-3;
pitch = width + kerf;
height=5e-3;
% define # of elements based on F/#
no_elements=(FIELD_PARAMS.focus(3)/FIELD_PARAMS.Fnum)/pitch;
no_elements = floor(no_elements);
% lens focus
Rfocus=19e-3;
% mathematically sub-dice elements to make them ~1 lambda dimensions
no_sub_y=height/width;
no_sub_x=1;
% define the transducer handle
Th = xdc_focused_multirow(no_elements,width,no_elements_y,height,kerf,kerf,Rfocus,no_sub_x,no_sub_y,FIELD_PARAMS.focus);
% define the fractional bandwidth
fractionalBandwidth = 0.5;
centerFrequency = 7.56e6;

% compute and load the experimentally-measured impulse response
[impulseResponse]=defineImpResp(fractionalBandwidth,centerFrequency,FIELD_PARAMS);

