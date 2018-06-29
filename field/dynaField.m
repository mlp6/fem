function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS)
% function [intensity, FIELD_PARAMS]=dynaField(FIELD_PARAMS)
%
% Generate intensity values at the nodal locations for conversion to force and
% input into the dyna deck.
%
% PARAMS:
%   FIELD_PARAMS (struct)
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
set_field('c', FIELD_PARAMS.sound_speed_m_s);
set_field('fs', FIELD_PARAMS.sampling_freq_Hz);

set_field('threads', FIELD_PARAMS.threads);
disp(sprintf('PARALLEL THREADS: %d', FIELD_PARAMS.threads));

% define the transducer definition
probe = readProbeJson(FIELD_PARAMS.Transducer);
Th = genTh(probe);

% compute or load the experimentally-measured impulse response
impulseResponse = defineImpResp(probe.fractionalBandwidth, probe.centerFrequency, FIELD_PARAMS);

% check specs of the defined transducer
FIELD_PARAMS.Th_data = xdc_get(Th, 'rect');

% figure out the axial shift (m) that will need to be applied to the scatterers
% to accomodate the mathematical element shift due to the lens
lens_correction_m = correct_axial_lens(FIELD_PARAMS.Th_data);
FIELD_PARAMS.measurementPointsandNodes(:, 4) = FIELD_PARAMS.measurementPointsandNodes(:, 4) + lens_correction_m;

xdc_center_focus(Th, FIELD_PARAMS.center_focus_m');

% define the impulse response
xdc_impulse(Th, impulseResponse);

% define the excitation pulse
exciteFreq=FIELD_PARAMS.freq_MHz*1e6; % Hz
ncyc=50;
texcite=0:1/FIELD_PARAMS.sampling_freq_Hz:ncyc/exciteFreq;
excitationPulse=sin(2*pi*exciteFreq*texcite);
xdc_excitation(Th, excitationPulse);

% set attenuation
Freq_att=FIELD_PARAMS.alpha_dB_cm_MHz*100/1e6; % FIELD_PARAMS in dB/cm/MHz
att_f0=exciteFreq;
att=Freq_att*att_f0; % set non freq. dep. to be centered here
set_field('att', att);
set_field('Freq_att', Freq_att);
set_field('att_f0', att_f0);
set_field('use_att', 1);
 
if FIELD_PARAMS.lownslow,
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
