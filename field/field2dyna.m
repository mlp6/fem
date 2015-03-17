function [dynaImat] = field2dyna(NodeName, alpha, Fnum, focus, Frequency, Transducer, Impulse, ElemName, ForceNonlinear)
% function [dynaImat] = field2dyna(NodeName, alpha, Fnum, focus, Frequency, Transducer, Impulse, ElemName, ForceNonlinear)
%
% INPUT:
%   NodeName (string) - file name to read nodes from (e.g., nodes.dyn); needs to
%                       be a comma-delimited file with header/footer lines that
%                       start with '*'
%   alpha - 0.5, 1.0, etc. (dB/cm/MHz)
%   Fnum - F/# (e.g. 1.3)
%   focus - [x y z] (m) "Field" coordinates
%   Frequency - excitation frequency (MHz)
%   Transducer (string) - 'vf105','vf73'
%   Impulse (string) - 'gaussian','exp'
%   ElemName (string) - file name to read elements from (default: elems.dyn);
%                       like node file, needs to be comma-delimited.
%   ForceNonlinear(int) - optional input argument. Set as 1 if you want to
%                         force nodal volumes to be calculated.
%
% OUTPUT:
%   dyna-I-*.mat file is saved to CWD and filename string returned
%
% EXAMPLE:
% dynaImatfile = field2dyna('nodes.dyn', 0.5, 1.3, [0 0 0.02], 7.2, 'vf105', 'gaussian', ...
%                            12, 'elems.dyn', 1);
%
% Mark Palmeri
% mlp6@duke.edu
% 2015-03-17

measurementPointsandNodes = read_mpn(NodeName);

% check to see if there are nodes in the x = y = 0 plane to make sure that
% "on axis" intensities are properly captured
check_on_axis(measurementPointsandNodes(:,2:4));

% invert the z axis
measurementPointsandNodes(:,4)=-measurementPointsandNodes(:,4);

% switch x and y so plane of symmetry is elevation, not lateral
measurementPointsandNodes(:,2:3)=[measurementPointsandNodes(:,3) measurementPointsandNodes(:,2)];
  
% convert from cm -> m
measurementPointsandNodes(:,2:4)=measurementPointsandNodes(:,2:4)/100;

% create a variable structure to pass to dynaField
FIELD_PARAMS.measurementPointsandNodes = measurementPointsandNodes;
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
[intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS);

% save intensity file
dynaImat = sprintf('save dyna-I-f%.2f-F%.1f-FD%.3f-a%.2f.mat intensity FIELD_PARAMS', ...
                    Frequency, Fnum, focus(3), alpha);
save(dynaImat, 'intensity' 'FIELD_PARAMS');

% check if non-uniform force scaling must be done
isUniform = checkUniform(measurementPointsandNodes(:,2:4));
if (nargin < 9)
    ForceNonlinear = 0;
end
if (~isUniform || ForceNonlinear == 1)
    % should run calcNodeVol.py
    fprintf('This is a non-linear mesh. Generating node volume file.\n')
    if (nargin < 9)
        warning('This is a non-linear mesh, but elements file was not given as an input argument. Skipping node volume file generation.')
    else
        NodeVolumeFilename = ['NodeVolume_' NodeName '_' ElemName '.txt'];
        if (exist(NodeVolumeFilename, 'file') == 0)
            eval(sprintf('nodeVolSuccess = system(''python calcNodeVol.py --nodefile %s --elefile %s --nodevolfile %s'');', NodeName, ElemName, NodeVolumeFilename));
            if (nodeVolSuccess ~= 0)
              fprintf('Node volume generation failed. Check to make sure node and element files exist in specified directory.\n')
            else
              fprintf('%s has been created.\n', ['NodeVolume_' NodeName '_' ElemName '.txt'])
            end
        else
            disp('Node volume file already exists; not generating new one');
        end
    end
else
    fprintf('This is a linear mesh.\n');
end

disp('The next step is to run makeLoadsTemps.');
disp('This will generate point loads and initial temperatures.');
