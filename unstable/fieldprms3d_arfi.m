function [isptaout,FIELD_PARAMS]=fieldprms3d_arfi(FIELD_PARAMS)
% function [isptaout,FIELD_PARAMS]=fieldprms3d_arfi(FIELD_PARAMS)
% --------------------------------------------------------------------------
% this function generates isptaout values at the nodal locations for 
% conversion to force and input into the dyna deck (performed by make_asc.m)
% INPUTS:
% FIELD_PARAMS.alpha (float) - absoprtion (dB/cm/MHz)
% FIELD_PARAMS.measurementPoints - nodal locations from field2dyna.m
% FIELD_PARAMS.Fnum (float) - F/#
% FIELD_PARAMS.focus - [x y z] (m)
% FIELD_PARAMS.Frequency (float) - push frequency (MHz)
%								 6.67 (VF10-5)
%								 4.21 (VF7-3)
% FIELD_PARAMS.Transducer (string) - 'vf105'; select the
% transducer-dependent parameters to use for the simulation
% FIELD_PARAMS.Impulse (string) - 'guassian','exp'; use a Guassian function
% based on the defined fractional bandwidth and center
% frequency, or use the experimentally-measured impulse
% response
%
% OUTPUT:
% isptaout - Ispta values at all of the node locations
% FIELD_PARAMS - field parameter structure
%
% Mark 07/31/03
% --------------------------------------------------------------------------
% Added frequency as an input parameter.
% Added ability to load in experimental impulse response data.
% Mark 01/31/05
% --------------------------------------------------------------------------
% Cleaned up the order of the definiting of parameters in the
% code to make it more readable.  The code now allows for the
% transducer definition and the impulse response to be passed
% as input variables.
% Mark 06/16/05
% --------------------------------------------------------------------------
% Incorportated FIELD_PARAMS structure.
% Mark 07/28/05
% --------------------------------------------------------------------------
% Fixed Transducer reference (FIELD_PARAMS.Transducer)
% Mark 08/08/05
% --------------------------------------------------------------------------
% Make sure that no_elements is an integer (floor).
% Mark 11/05/06
% --------------------------------------------------------------------------
% Separated the center & excitation frequencies.
% Broke out probe definitions into separate functions.
% Mark 06/15/07
% --------------------------------------------------------------------------

field_init(-1)

%set_field('use_triangles',1);
%set_field('use_lines',1);

% define transducer-independent parameters
FIELD_PARAMS.soundSpeed=1540;
set_field('c',FIELD_PARAMS.soundSpeed); 

FIELD_PARAMS.samplingFrequency = 200e6;
set_field('fs',FIELD_PARAMS.samplingFrequency);

% define transducer-dependent parameters
switch FIELD_PARAMS.Transducer
    case 'vf105'
        [Th,fractionalBandwidth,centerFrequency]=vf105(FIELD_PARAMS);
    case 'vf73'
        [Th,fractionalBandwidth,centerFrequency]=vf73(FIELD_PARAMS);
    case 'vf105_gfp'  % "VF105" as setup by Gianmarco in his linear/nonlinear simulations
        [Th,fractionalBandwidth,centerFrequency]=vf105gfp(FIELD_PARAMS);
    case 'pl35elegra'
        [Th,fractionalBandwidth,centerFrequency]=pl35elegra(FIELD_PARAMS);
    case 'ph41'
        [Th,fractionalBandwidth,centerFrequency]=ph41(FIELD_PARAMS);
end;

% frequency is now an input variable
exciteFreq=FIELD_PARAMS.Frequency*1e6;  % Hz

% define the impulse response
switch FIELD_PARAMS.Impulse
  case 'gaussian',
    % define the impulse response as a Gaussian pulse
		% this assumes that the center frequency of the array is
		% at the transmit frequency of the pulse - not necessarily
		% true, but adequate for frequencies near the resonant freq
    disp('Impulse Response: Gaussian');
    tc = gauspuls('cutoff', centerFrequency, fractionalBandwidth, -6, -40);
    t = -tc:1/FIELD_PARAMS.samplingFrequency:tc;
    impulseResponse =gauspuls(t, centerFrequency, fractionalBandwidth);
  case 'exp',
    % load in the experimental impulse response data
    disp('Impulse Response: Experimental');
		switch FIELD_PARAMS.Transducer
			case 'vf105'
				load /moredata/mlp6/VF105_Bandwidth/FieldImpulseResponseVF105_200e6.mat
			case 'vf73'
				disp('An experimental impulse response for this transducer has not been defined!');
		end;
end;
xdc_impulse(Th, impulseResponse);

% define the excitation pulse
ncyc=50;
texcite=0:1/FIELD_PARAMS.samplingFrequency:ncyc/exciteFreq;
excitationPulse=sin(2*pi*exciteFreq*texcite);
xdc_excitation(Th,excitationPulse);

% set absoprtion
%alpha=.5; - assumes you set alpha externally
Freq_att=FIELD_PARAMS.alpha*100/1e6; % dB/cm/MHz
att_f0=exciteFreq; 
att=Freq_att*att_f0; % set non freq. dep. to be cntered here
set_field('att',att);
set_field('Freq_att',Freq_att);
set_field('att_f0',att_f0);
set_field('use_att',1);
 
% compute Ispta at each location for a single tx pulse
% optimizing by computing only relevant nodes... will assume others are zero
StartTime = fix(clock);
disp(sprintf('Start Time: %i:%i',StartTime(4),StartTime(5)));
tic;
EstCount = 1000;  % number of calculations to average over to
									 % make calc time estimates
for i=1:size(FIELD_PARAMS.measurementPoints,1)
 	[pressure, startTime] = calc_hp(Th, FIELD_PARAMS.measurementPoints(i,:));
 	isptaout(i)=sum(pressure.*pressure);
	if(i==1),
		tic,
	end;
	if(i==EstCount),
		EstCalcTime = toc; % s
		EstRunTime = (EstCalcTime/EstCount)*(size(FIELD_PARAMS.measurementPoints,1)-1)/60; % min
		% empirically, the run times tend to be 2x the calculated estimate, so I'm going to multiple
		% EstRunTime x 2
		disp(sprintf('Estimate Run Time = %.1f m',EstRunTime*2));
	end;	
end
CalcTime = toc; % s
ActualRunTime = CalcTime/60; % min
disp(sprintf('Actual Run Time = %.1f m\n',ActualRunTime));

field_end;
