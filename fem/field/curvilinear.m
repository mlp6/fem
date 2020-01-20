function [Th,impulseResponse]=curvilinear(FIELD_PARAMS);
% function [Th,impulseResponse]=curvilinear(FIELD_PARAMS);
%
% Create 'Th' transducer handle and define the fractional bandwidth for a
% typical curvilinear array
%
% Mark Palmeri
% mlp6@duke.edu
% 2014-08-07

disp('Transducer: Curvilinear');

kerf=0.007e-3;
pitch = 0.477e-3;
width = pitch - kerf;
height=14e-3;

% define # of elements based on F/#
no_elements=(FIELD_PARAMS.focus(3)/FIELD_PARAMS.Fnum)/pitch;
no_elements = floor(no_elements);
if(no_elements > 128),
    no_elements = 128;
end;

% lens focus
Rfocus=48.8e-3;
Rconvex=42/1000;

% mathematically sub-dice elements to make them ~1 lambda dimensions
no_sub_y=2*height/width;
no_sub_x=2;

% define the transducer handle
Th = xdc_convex_focused_array(no_elements,width,height,kerf,Rconvex,Rfocus,no_sub_x,no_sub_y,FIELD_PARAMS.focus);

% define the fractional bandwidth & center frequency 
fractionalBandwidth = 3/2.5;
centerFrequency = 2.5e6;

% compute and load the experimentally-measured impulse response
[impulseResponse]=defineImpResp(fractionalBandwidth,centerFrequency,FIELD_PARAMS);
