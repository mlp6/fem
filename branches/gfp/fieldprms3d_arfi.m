function [isptaout,FIELD_PARAMS,pressure,StartTimes]=fieldprms3d_arfi(FIELD_PARAMS)
% function [isptaout,FIELD_PARAMS,pressure,StartTimes]=fieldprms3d_arfi(FIELD_PARAMS)
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
%	pressure - vector of pressure waveforms
%	StartTimes - start times for the pressure vectors
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

field_init(-1)

%set_field('use_triangles',1);
%set_field('use_lines',1);

% define transducer-independent parameters
FIELD_PARAMS.soundSpeed=1540;
set_field('c',FIELD_PARAMS.soundSpeed); 

FIELD_PARAMS.samplingFrequency = 100e6;
set_field('fs',FIELD_PARAMS.samplingFrequency);

% define transducer-dependent parameters
switch FIELD_PARAMS.Transducer
	case 'vf105'
		disp('Transducer: VF10-5');
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
		Th = xdc_focused_multirow (no_elements,width,no_elements_y,height, ...  
							kerf,kerf,Rfocus,no_sub_x,no_sub_y,FIELD_PARAMS.focus); 
		% define the fractional bandwidth
		fractionalBandwidth = 0.5;
	case 'vf73'
		disp('Transducer: VF7-3');
		no_elements_y=1;
		width=.2e-3;
		kerf=0.02e-3;
		pitch = width + kerf;
		height=7.5e-3;
		% define # of elements based on F/#
		no_elements=(FIELD_PARAMS.focus(3)/FIELD_PARAMS.Fnum)/pitch;
		no_elements = floor(no_elements);
		% lens focus
		Rfocus=37.5e-3;
		% mathematically sub-dice elements to make them ~1 lambda dimensions
		no_sub_y=height/width;
		no_sub_x=1;
		% define the transducer handle
		Th = xdc_focused_multirow (no_elements,width,no_elements_y,height, ...  
							kerf,kerf,Rfocus,no_sub_x,no_sub_y,FIELD_PARAMS.focus);           
		% define the fractional bandwidth
		fractionalBandwidth = 0.5;
	case 'vf105_gfp'  % "VF105" as setup by Gianmarco in his
										% linear/nonlinear simulations
		disp('Transducer: VF10-5 (GFP setup)');
		no_elements_y=1;
		width=.2e-3;
		kerf=0.02e-3;
		pitch = width + kerf;
		height=5e-3;
		% define # of elements based on F/#
		no_elements=(FIELD_PARAMS.focus(3)/FIELD_PARAMS.Fnum)/pitch;
		no_elements = floor(no_elements);
		% lens focus
		Rfocus=20e-3;
		% mathematically sub-dice elements to make them ~1 lambda dimensions
		no_sub_y=height/width;
		no_sub_x=1;
		if(FIELD_PARAMS.ElevApod ~= 1),
			% define the transducer handle
			Th = xdc_focused_multirow (no_elements,width,no_elements_y,height, ...  
							kerf,kerf,Rfocus,no_sub_x,no_sub_y,FIELD_PARAMS.focus); 
		else,
			% artificially breakup the single element in elevation
			% into multiple elements to apply an apodiztion profile
			no_elements_y = no_sub_y;
			no_sub_y = 1;
			height = height / no_elements_y;
			Th = xdc_focused_multirow (no_elements,width,no_elements_y,height, ...  
							kerf,kerf,Rfocus,no_sub_x,no_sub_y,FIELD_PARAMS.focus); 
		end;
		% define the fractional bandwidth
		% Gianmarco's is very broadband, so I will artifcially put
		% it at 2.0
		fractionalBandwidth = 2.0;
end;

% frequency is now an input variable
centerFrequency=FIELD_PARAMS.Frequency*1e6;  % Hz

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
texcite=0:1/FIELD_PARAMS.samplingFrequency:ncyc/centerFrequency;
excitationPulse=sin(2*pi*centerFrequency*texcite);
xdc_excitation(Th,excitationPulse);

% set absoprtion
%alpha=.5; - assumes you set alpha externally
Freq_att=FIELD_PARAMS.alpha*100/1e6; % dB/cm/MHz
att_f0=centerFrequency; 
att=Freq_att*att_f0; % set non freq. dep. to be cntered here
set_field('att',att);
set_field('Freq_att',Freq_att);
set_field('att_f0',att_f0);
set_field('use_att',1);
 
% apply apodization (lateral and elevation dimensions)
if(FIELD_PARAMS.LatApod == 1 && FIELD_PARAMS.ElevApod ~= 1),
	disp('Setting raised cosine apodization in lateral dimension...');
	lat_apod=(1-1*cos(2*pi*(0:no_elements-1)/(no_elements-1)))/2;
	xdc_apodization(Th,0,lat_apod);
end;
elseif(FIELD_PARAMS.LatApod == 1 && FIELD_PARAMS.ElevApod == 1),
	disp('Setting raised cosine apodization in lateral and elevation dimensions...');
	lat_apod=(1-1*cos(2*pi*(0:no_elements-1)/(no_elements-1)))/2;
	elev_apod=(1-1*cos(2*pi*(0:no_elements_y-1)/(no_elements_y-1)))/2;
	apod = repmat(lat_apod,no_elements_y,1).*repmat(elev_apod,69,1)';
end;
elseif(FIELD_PARAMS.LatApod ~= 1 && FIELD_PARAMS.ElevApod == 1),
	elev_apod=(1-1*cos(2*pi*(0:no_elements_y-1)/(no_elements_y-1)))/2;
	apod = ones(no_elements_y,no_elements);
	apod = apod.*repmat(elev_apod,69,1)';
end;

% compute Ispta at each location for a single tx pulse
% optimizing by computing only relevant nodes... will assume others are zero
StartTime = fix(clock);
disp(sprintf('Start Time: %i:%i',StartTime(4),StartTime(5)));
tic;
EstCount = 1000;  % number of calculations to average over to
									 % make calc time estimates

% open data to save binary data to
fid = fopen('node_data.bin','wb');

count = 0; % binary data count index
for i=1:size(FIELD_PARAMS.measurementPoints,1),
 	[pressure, startTime] = calc_hp(Th, FIELD_PARAMS.measurementPoints(i,:));
 	isptaout=sum(pressure.*pressure);
	nodeID = FIELD_PARAMS.measurementPointsandNodes(i,1);

	% save data to a binary file
	count = fwrite(fid,nodeID,'real*4') + count;
	count = fwrite(fid,isptaout,'real*4') + count;
	count = fwrite(fid,startTime,'real*4') + count;
	count = fwrite(fid,pressure,'real*4') + count;
	
	nodeID_count(i,:) = [nodeID count];
	
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

fclose(fid); % close binary data file
% save the nodeID_count variable
save nodeID_count.mat nodeID_count;
save parameters.mat FIELD_PARAMS;

CalcTime = toc; % s
ActualRunTime = CalcTime/60; % min
disp(sprintf('Actual Run Time = %.1f m\n',ActualRunTime));

field_end;
