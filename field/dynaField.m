function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, numWorkers)
% function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, numWorkers)
%
% Generate intensity values at the nodal locations for conversion to force and
% input into the dyna deck.
%
% INPUTS:
%   FIELD_PARAMS.alpha (float) - absoprtion (dB/cm/MHz)
%   FIELD_PARAMS.measurementPointsandNodes - nodal IDs and spatial locations
%                                            from field2dyna.m
%   FIELD_PARAMS.Fnum (float) - F/#
%   FIELD_PARAMS.focus - [x y z] (m)
%   FIELD_PARAMS.Frequency (float) - push frequency (MHz)
%                                    6.67 (VF10-5)
%                                    4.21 (VF7-3)
%   FIELD_PARAMS.Transducer (string) - 'vf105'; select the
%       transducer-dependent parameters to use for the simulation
%   FIELD_PARAMS.Impulse (string) - 'guassian','exp'; use a Guassian function
%       based on the defined fractional bandwidth and center
%       frequency, or use the experimentally-measured impulse
%       response
%
% OUTPUT:
%   intensity - intensity values at all of the node locations
%   FIELD_PARAMS - field parameter structure
%
% EXAMPLE:
%   [intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS, numWorkers)
%

% figure out where this function exists to link probes submod
functionDir = fileparts(which(mfilename));
probesPath = fullfile(functionDir, '../probes/fem');
check_add_probes(probesPath);

% check that Field II is in the Matlab search path, and initialize
check_start_Field_II;

% define transducer-independent parameters
set_field('c', FIELD_PARAMS.soundSpeed);
set_field('fs', FIELD_PARAMS.samplingFrequency);

% define transducer-dependent parameters
eval(sprintf('[Th,impulseResponse] = %s(FIELD_PARAMS);', FIELD_PARAMS.Transducer));

% check specs of the defined transducer
FIELD_PARAMS.Th_data = xdc_get(Th, 'rect');

% figure out the axial shift (m) that will need to be applied to the scatterers
% to accomodate the mathematical element shift due to the lens
FIELD_PARAMS.lens_correction_m = correct_axial_lens(FIELD_PARAMS.Th_data);

% define the impulse response
xdc_impulse(Th, impulseResponse);

% define the excitation pulse
exciteFreq=FIELD_PARAMS.Frequency*1e6; % Hz
ncyc=50;
texcite=0:1/FIELD_PARAMS.samplingFrequency:ncyc/exciteFreq;
excitationPulse=sin(2*pi*exciteFreq*texcite);
xdc_excitation(Th, excitationPulse);

% set attenuation
Freq_att=FIELD_PARAMS.alpha*100/1e6; % FIELD_PARAMS in dB/cm/MHz
att_f0=exciteFreq;
att=Freq_att*att_f0; % set non freq. dep. to be centered here
set_field('att', att);
set_field('Freq_att', Freq_att);
set_field('att_f0', att_f0);
set_field('use_att', 1);
 
% compute Ispta at each location for a single tx pulse
% optimizing by computing only relevant nodes... will assume others are zero
StartTime = fix(clock);
% disp(sprintf('Start Time: %i:%2.0i',StartTime(4),StartTime(5)));
Time = datestr(StartTime, 'HH:MM:SS PM');
disp(sprintf('Start Time: %s', Time))
tic;

useForLoop = false;

% if numWorkers not specified, default to 1 and don't use parallel version
if (nargin == 1)
    numWorkers = 1;
    useForLoop = true;
% if numWorkers specified as 1, don't use parallel version
elseif (numWorkers == 1)
    useForLoop = true;
else
    useForLoop = false;
    maxNumWorkers = feature('numCores');
    if (numWorkers > maxNumWorkers)
        warning('Invalid number of workers. Maximum is %i.  numWorkers set to %i', ...
            maxNumWorkers, maxNumWorkers);
        numWorkers = maxNumWorkers;
    end
end

if (useForLoop)
    numNodes = size(FIELD_PARAMS.measurementPointsandNodes, 1);
    progressPoints = 0:10000:numNodes;
    for i=1:numNodes,
      if ~isempty(intersect(i, progressPoints)),
          disp(sprintf('Processed %.1f%%', i * 100 / numNodes));
      end;
      if i == 1
          tic;
      end;
      % include the lens correction (axial shift)
      [pressure, startTime] = calc_hp(Th, FIELD_PARAMS.measurementPointsandNodes(i,2:4)+FIELD_PARAMS.len_correction_m);
      intensity(i) = sum(pressure.*pressure);
    end
else
    tic;
    intensity = dynaFieldPar(FIELD_PARAMS, numWorkers);
end

CalcTime = toc; % s
ActualRunTime = CalcTime/60; % min
disp(sprintf('Actual Run Time = %.3f m\n', ActualRunTime));

field_end;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [intensity, FIELD_PARAMS] = dynaFieldPar(FIELD_PARAMS, numWorkers)

% allocating number of workers
currentWorkers = matlabpool('size');
isPoolOpen = (currentWorkers > 0);
if (isPoolOpen)
    matlabpool close;
end

matlabpool('open', numWorkers);

spmd
    % separate the matrices such that each core gets a roughly equal number of
    % measurement points to perform calculations on.  also, distributes
    % matrices based on columns, rather than rows.
    codistPoints = codistributed(FIELD_PARAMS.measurementPointsandNodes(:,2:4), ...
        codistributor('1d', 1));
    pointsSize = size(FIELD_PARAMS.measurementPointsandNodes(:,2:4));
    
    FIELD_PARAMS.measurementPointsandNodes(:,2:4) = getLocalPart(codistPoints);
    [intensityCodist, FIELD_PARAMS] = dynaField(FIELD_PARAMS);
    
    % combine all the separate matrices again.
    intensityDist = codistributed.build(intensityCodist, ...
        codistributor1d(2, codistributor1d.unsetPartition, [1 pointsSize(1)]));
end
intensity = gather(intensityDist);
matlabpool close
