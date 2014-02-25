function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse,numWorkers,ElemName, ForceNonlinear)
% function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse,numWorkers,ElemName, ForceNonlinear)
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
% ElemName (string) - file name to read elements from (default: elems.dyn);
% like node file, needs to be comma-delimited.
% ForceNonlinear(int) - optional input argument. Set as 1 if you want to
% force nodal volumes to be calculated.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OUTPUT:
% dyna_ispta*.mat file is saved to CWD
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXAMPLE:
% field2dyna('nodes.dyn',0.5,1.3,[0 0 0.02],7.2,'vf105','gaussian', 12,...
% 'elems.dyn', 1);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath('/home/mlp6/matlab/Field_II');

measurementPointsandNodes = read_mpn(NodeName);

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
% if numWorkers not specified, defaults to 1 (non-parallel version)
if (nargin >= 8)
    [intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS, numWorkers);
else
    [intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS);
end

% save intensity file
eval(sprintf('save dyna-I-f%.2f-F%.1f-FD%.3f-a%.2f.mat intensity FIELD_PARAMS',Frequency,Fnum,focus(3),alpha));

% check if non-uniform force scaling must be done
isUniform = checkUniform(measurementPoints);
if (nargin < 10)
    ForceNonlinear = 0;
end
if (~isUniform || ForceNonlinear == 1)
    % should run calcNodeVol.py
    fprintf('This is a non-linear mesh. Generating node volume file.\n')
    if (nargin < 9)
        warning('This is a non-linear mesh, but elements file was not given as an input argument. Skipping node volume file generation.')
    else
        if (exist(ElemName, 'file') ~= 0)
            eval(sprintf('nodeVolSuccess = system(''python calcNodeVol.py --nodefile %s --elefile %s --nodevolfile %s'');', NodeName, ElemName, ['NodeVolume_' NodeName '_' ElemName '.txt']));
            if (nodeVolSuccess ~= 0)
              fprintf('Node volume generation failed. Check to make sure node and element files exist in specified directory.\n')
            else
              fprintf('%s has been created.\n', ['NodeVolume_' NodeName '_' ElemName '.txt'])
            end
        else
            error('Element file name given as input argument could not be found.');
        end
    end
else
    fprintf('This is a linear mesh.\n');
end

disp('The next step is to run makeLoadsTemps.');
disp('This will generate point loads and initial temperatures.');
end


function check_on_axis(measurementPoints)
% function check_on_axis(measurementPoints)
%
% check to see if nodes exist on the x = y = 0 plane to insure that the
% intensity fields are properly represented
%
xlocs = unique(measurementPoints(1,:));
ylocs = unique(measurementPoints(2,:));

% test for x and y locations that are at 0 (imaging plane), and if both don't exist, then display a warning
if((max(xlocs==0) + max(ylocs==0)) < 2),
    warning('There are not nodes in the lateral / elevation plane = 0 (imaging plane). This can lead to inaccurate representations of the intensity fields!!');
end
end


function [isUniform] = checkUniform(measurementPoints)
% function [isUniform] = checkUniform(measurementPoints)
%
% check to see if mesh is linear or nonlinear. if mesh is nonlinear, this means
% that force scaling needs to be done
%
x = unique(measurementPoints(:, 1));
y = unique(measurementPoints(:, 2));
z = unique(measurementPoints(:, 3));
isUniform = all(abs(diff(x)/(x(2)-x(1))-1 < 10^-9)) &&...
            all(abs(diff(y)/(y(2)-y(1))-1 < 10^-9)) &&...
            all(abs(diff(z)/(z(2)-z(1))-1 < 10^-9));
end


function [mpn] = read_mpn(NodeName)
% 
% read nodes.dyn and extract points & nodes
%

% read in the nodes
try
    fid = fopen(NodeName,'r');
catch exception
    error(sprintf('%s does not exist',NodeName));
end

mpn = [];
nodecount = 0;
templine = fgetl(fid);
while ischar(templine)
    % check for comment line delimiters at start of line, and only parse data
    % if they do not exist
    comment_test = logical(regexp(templine,'^(\*|\$)'));
    if comment_test
        disp('Skipping comment line . . . ')
    else
        nodecount = nodecount + 1;
        val = regsplitcell(templine);
        mpn = [mpn; val'];
    end
    templine = fgetl(fid);
end

fclose(fid);
if (size(mpn,2) ~= 4 || size(mpn,1) ~= nodecount),
    error('ERROR: mpn matrix has inconsistent dimensions (%i x %i vs %i x %i)', size(mpn, 1), ...
                                                                                size(mpn, 2), ... 
                                                                                nodecount, ...
                                                                                4);
end
end


function [nodeval] = regsplitcell(templine)
val = regexp(templine, ',', 'split');
valstr = str2mat(val);
nodeval = str2num(valstr);
end
