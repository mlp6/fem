function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse,numWorkers)
%function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse,numWorkers)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INPUT:
% NodeName (string) - file name to read nodes from (e.g., nodes.dyn); needs to
% be a comma-delimited file with header/footer lines that
% start with *
% alpha - 0.5, 1.0, etc. (dB/cm/MHz)
% Fnum - F/# (e.g. 1.3)
% focus - [x y z] (m) "Field" coordinates
% Frequency - excitation frequency (MHz)
% Transducer (string) - 'vf105','vf73'
% Impulse (string) - 'gaussian','exp'
% numWorkers (int) - number of parallel jobs to spawn in dynaField()
%
% OUTPUT:
% dyna_ispta*.mat file is saved to CWD
%
% Example:
% field2dyna('nodes.dyn',0.5,1.3,[0 0 0.02],7.2,'vf105','gaussian',12);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath('/home/mlp6/matlab/Field_II_7.10');

% read in the nodes
try
    fid = fopen(NodeName,'r');
catch exception
    error(sprintf('%s does not exist',NodeName));
end

measurementPointsandNodes=textscan(fid,'%f%f%f%f','CommentStyle','*','Delimiter',',');
fclose(fid);
measurementPointsandNodes = cell2mat(measurementPointsandNodes);

% skip node number, use just coords
measurementPoints=measurementPointsandNodes(:,2:4);

% check to see if there are nodes in the x = y = 0 plane to make sure that
% "on axis" intensities are properly captured
check_on_axis(measurementPoints);

% invert the z axis
measurementPoints(:,3)=-measurementPoints(:,3);

% switch x and y so plane of symmetry is elevation, not lateral
tmp=measurementPoints(:,1:2);
measurementPoints(:,1:2)=[tmp(:,2) tmp(:,1)];
  
% convert from cm -> m
measurementPoints=measurementPoints/100;

% create a variable structure to pass to dynaField
FIELD_PARAMS.measurementPointsandNodes = measurementPointsandNodes;
FIELD_PARAMS.measurementPoints = measurementPoints;
FIELD_PARAMS.alpha = alpha;
FIELD_PARAMS.Fnum = Fnum;
FIELD_PARAMS.focus = focus;
FIELD_PARAMS.Frequency = Frequency;
FIELD_PARAMS.Transducer = Transducer;
FIELD_PARAMS.Impulse = Impulse;

% below are hard-coded constants (transducer independent)
FIELD_PARAMS.soundSpeed=1540;
FIELD_PARAMS.samplingFrequency = 200e6;

% small sample of measurementPoints testing
FIELD_PARAMS.measurementPoints = measurementPoints(1:60000, :);

% perform the field calculation
intensity=dynaField(FIELD_PARAMS,numWorkers);

% save intensity file
eval(sprintf('save dyna-I-f%.2f-F%.1f-FD%.3f-a%.2f.mat intensity FIELD_PARAMS',Frequency,Fnum,focus(3),alpha));

disp('The next step is to run makeLoadsTemps.');
disp('This will generate point loads and initial temperatures.');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function check_on_axis(measurementPoints)
% function check_on_axis(measurementPoints)
%
% check to see if nodes exist on the x = y = 0 plane to insure that the
% intensity fields are properly represented
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
xlocs = unique(measurementPoints(1,:));
ylocs = unique(measurementPoints(2,:));

% test for x and y locations that are at 0 (imaging plane), and if both don't exist, then display a warning
if((max(xlocs==0) + max(ylocs==0)) < 2),
    warning('There are not nodes in the lateral / elevation plane = 0 (imaging plane). This can lead to inaccurate representations of the intensity fields!!');
end
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
