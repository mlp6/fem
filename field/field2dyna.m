function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse, ElemName, ForceNonlinear)
%function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse)
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
%
% OUTPUT:
% dyna_ispta*.mat file is saved to CWD
%
% Example:
% field2dyna('nodes.dyn',0.5,1.3,[0 0 0.02],7.2,'vf105','gaussian');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath('/home/nl91/matlab/Field_II_7.10');

% read in the nodes
fid = fopen(NodeName,'r');
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

% perform the field calculation
[intensity,FIELD_PARAMS]=dynaField(FIELD_PARAMS, 4);

% save intensity file
eval(sprintf('save dyna-I-f%.2f-F%.1f-FD%.3f-a%.1f.mat intensity FIELD_PARAMS',Frequency,Fnum,focus(3),alpha));

% check if non-uniform force scaling must be done
isUniform = checkUniform(measurementPoints);
if (~isUniform || ForceNonlinear == 1)
    % should run calcNodeVol.py
    fprintf('This is a non-linear mesh. Generating node volume file.\n')
    if (exist('ElemName') ~= 0)
        eval(sprintf('nodeVolSuccess = system(''python calcNodeVol.py --nodefile %s --elefile %s'');', NodeName, ElemName));
        if (nodeVolSuccess ~= 0)
            fprintf('Node volume generation failed. Check to make sure node and element files exist in specified directory.\n')
        else
            fprintf('NodeVolume.txt has been created.\n')
        end
    else
        error('Non-linear mesh detected. Need element file to calculate node volumes.');
    end
else
    fprintf('This is a linear mesh.\n');
end

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

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [isUniform] = checkUniform(measurementPoints)
% function [isUniform] = checkUniform(measurementPoints)
%
% check to see if mesh is linear or nonlinear. if mesh is nonlinear, this means that
% force scaling needs to be done
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
x = unique(measurementPoints(:, 1));
y = unique(measurementPoints(:, 2));
z = unique(measurementPoints(:, 3));
isUniform = all(abs(diff(x)/(x(2)-x(1))-1 < 10^-9)) &&...
            all(abs(diff(y)/(y(2)-y(1))-1 < 10^-9)) &&...
            all(abs(diff(z)/(z(2)-z(1))-1 < 10^-9));
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
