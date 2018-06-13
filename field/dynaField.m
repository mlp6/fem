function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, threads, lownslow)
% function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS, threads, lownslow)
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
%   threads (int) - number of parallel threads to use [default = numCores]
%   lownslow (bool) - low RAM footprint, but much slower
%
% OUTPUT:
%   intensity - intensity values at all of the node locations
%   FIELD_PARAMS - field parameter structure
%
% EXAMPLE:
%   [intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS)
%

% figure out where this function exists to link probes submod
functionDir = fileparts(which(mfilename));

% check that Field II is in the Matlab search path, and initialize
check_start_Field_II;

% define transducer-independent parameters
set_field('c', FIELD_PARAMS.soundSpeed);
set_field('fs', FIELD_PARAMS.samplingFrequency);

if (nargin < 2),
    threads = feature('numCores');
end
set_field('threads', threads);
disp(sprintf('PARALLEL THREADS: %d', threads));

% TODO: load in params from JSON -> probe struct
% define the transducer
switch probe.name
    case {'vf105', 'vf135', 'vf73', 'vf105gfp', 'sonivate', 'tu15l8w', 'l74', ...
          'l94', 'l124', 'l145', 'i7505', 'acunav64', 'acunav128', ...
          'acunav128_fullapp', 'er7bl', 'p42', 'ph41', 'pl35elegra'}
        Th = xdc_focused_multirow(probe.no_elements, probe.width,
                                  probe.no_elements_y, probe.height, ... 
                                  probe.kerf, probe.kerf, probe.Rfocus, ...
                                  probe.no_sub_x, probe.no_sub_y, ...
                                  FIELD_PARAMS.focus);
    case {'c52', 'c52v', 'ch41', 'ch62', 'ev94'}
        Th = xdc_convex_focused_array(probe.no_elements, probe.width, probe.height, ...
                                      probe.kerf, probe.Rconvex, probe.Rfocus, ...
                                      probe.no_sub_x, probe.no_sub_y, ...
                                      FIELD_PARAMS.focus);
    otherwise
        warning('Specified probe not explicitly handled.')


% compute and load the experimentally-measured impulse response
%%%% TODO: Make sure that exp vs gausian properly handled w/i defineImpResp %%%%
impulseResponse = defineImpResp(fractionalBandwidth, centerFrequency, FIELD_PARAMS);

% check specs of the defined transducer
FIELD_PARAMS.Th_data = xdc_get(Th, 'rect');

% figure out the axial shift (m) that will need to be applied to the scatterers
% to accomodate the mathematical element shift due to the lens
lens_correction_m = correct_axial_lens(FIELD_PARAMS.Th_data);
FIELD_PARAMS.measurementPointsandNodes(:, 4) = FIELD_PARAMS.measurementPointsandNodes(:, 4) + lens_correction_m;

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
if (nargin < 3),
    lownslow = true;
end;

if lownslow,
    disp('Running low-n-slow... ')
    numNodes = size(FIELD_PARAMS.measurementPointsandNodes, 1);
    for i = 1:numNodes,
        [pressure, startTime] = calc_hp(Th, squeeze(double(FIELD_PARAMS.measurementPointsandNodes(i,2:4))));
        intensity(i) = sum(pressure.*pressure);
    end
else,
    disp('Running high-n-fast... ')
    [intensity, startTime] = calc_hp(Th, squeeze(double(FIELD_PARAMS.measurementPointsandNodes(:,2:4))));
    intensity = sum(intensity.*intensity);
end

intensity = single(intensity);

field_end;
