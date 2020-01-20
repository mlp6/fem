function [dynaImat] = field2dyna(NodeName, field_params_json, ElemName, ForceNonlinear)
% function [dynaImat] = field2dyna(NodeName, field_params_json, ElemName, ForceNonlinear)
%
% INPUT:
%   NodeName (string) - file name to read nodes from (e.g., nodes.dyn); needs to
%                       be a comma-delimited file with header/footer lines that
%                       start with '*'
%   field_params_json (str) - JSON filename
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

FIELD_PARAMS = read_json(field_params_json);

FIELD_PARAMS.measurementPointsandNodes = measurementPointsandNodes;
% setup some input argument defaults
if (nargin < 8),
    threads = 1;
end;

if (nargin < 9),
    lownslow = true;
end;

% perform the field calculation
[intensity, FIELD_PARAMS] = dynaField(FIELD_PARAMS);

% save intensity file
dynaImat = sprintf('dyna-I-f%.2f-F%.1f-FD%.3f-a%.2f.mat', ...
                   FIELD_PARAMS.freq_MHz, FIELD_PARAMS.fnum, ...
                   FIELD_PARAMS.focus_m(3), FIELD_PARAMS.alpha_dB_cm_MHz);
save(dynaImat, 'intensity', 'FIELD_PARAMS');

% check if non-uniform force scaling must be done
isUniform = checkUniform(measurementPointsandNodes(:,2:4));
if (nargin < 4)
    ForceNonlinear = 0;
end
if (~isUniform || ForceNonlinear == 1)
    % should run calcNodeVol.py
    fprintf('This is a non-linear mesh. Generating node volume file.\n')
    if (nargin < 11)
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
