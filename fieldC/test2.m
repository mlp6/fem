fid=fopen("myNodes.dyn",'r')

endofline = sprintf('\n');

s = fscanf(fid, '%s', 1);
while (~strcmp(s, '*NODE')),
s = fscanf(fid, '%s', 1);
end

c = fscanf(fid, '%c', 1);
while(c ~= endofline);
c = fscanf(fid, '%c', 1);disp
end

% read points in

[mpn] = fscanf(fid, '%d,%f,%f,%f', [4, inf])

% switch rows, columns

mpn = mpn'

% invert z axis

mpn(:,4)=-mpn(:,4);

% swap x, y

mpn(:,2:3)=[mpn(:,3) mpn(:,2)];

% centimeters to meters

mpn(:,2:4)=mpn(:,2:4)/100;

FIELD_PARAMS.measurementPointsandNodes = mpn;
FIELD_PARAMS.alpha = 0.5;
FIELD_PARAMS.Fnum = 1.3;

FIELD_PARAMS.focus = [0, 0, 0.02];

FIELD_PARAMS.Frequency = 7.2;
FIELD_PARAMS.Transducer = 'vf105';
FIELD_PARAMS.Impulse = 'gaussian';

FIELD_PARAMS.soundSpeed=1540;
FIELD_PARAMS.samplingFrequency = 100e6;

field_init(-1)

set_field('c', FIELD_PARAMS.soundSpeed);
set_field('fs', FIELD_PARAMS.samplingFrequency);

set_field('threads', 1);

% these numbers are from the c52 JSON

Th=xdc_convex_focused_array(192, .0002925, .0112, 3.25e-05, .0394, .0725, 1, 7, FIELD_PARAMS.focus)

% some numbers from c52, some from defineImpResp.m

tc=gauspuls('cutoff',3e6,.7,-6,-40)

t=-tc:1/FIELD_PARAMS.samplingFrequency:tc;

impulseResponse= gauspuls(t,3e6,.7);

FIELD_PARAMS.Th_data = xdc_get(Th, 'rect');

% find the center element of the array (x == 0)
center_ele_index = min(find(FIELD_PARAMS.Th_data(8,:)>=0));

% find axial offset of the center of this center element
lens_correction_m = FIELD_PARAMS.Th_data(10,center_ele_index);

% figure out the axial shift (m) that will need to be applied to the scatterers
% to accomodate the mathematical element shift due to the lens

FIELD_PARAMS.measurementPointsandNodes(:, 4) = FIELD_PARAMS.measurementPointsandNodes(:, 4) + lens_correction_m;

% define the impulse response

xdc_impulse(Th, impulseResponse)

% define the excitation pulse

exciteFreq=FIELD_PARAMS.Frequency*1e6;

ncyc=50;

texcite=0:1/FIELD_PARAMS.samplingFrequency:ncyc/exciteFreq;

excitationPulse=sin(2*pi*exciteFreq*texcite);

xdc_excitation(Th, excitationPulse);

% set attenuation

Freq_att=FIELD_PARAMS.alpha*100/1e6;
att_f0=exciteFreq;
att=Freq_att*att_f0;
set_field('att', att);
set_field('Freq_att', Freq_att);
set_field('att_f0', att_f0);
set_field('use_att', 1);

numNodes = size(FIELD_PARAMS.measurementPointsandNodes, 1);
[pressure, startTime] = calc_hp(Th,squeeze(double(FIELD_PARAMS.measurementPointsandNodes(:,2:4))));

field_end;
