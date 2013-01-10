function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse)
%function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse)
% ------------------------------------------------------------------------------
% INPUT:
% NodeName (string) - file name to read nodes from (nodes.asc); this file
% cannot have any headers/footers/comments
% alpha - 0.5, 1.0, etc.
% Fnum - F/# (e.g. 1.3)
% focus - [x y z] (m) "Field" coordinates
% Frequency - excitation frequency (MHz)
% Transducer (string) - 'vf105','vf73'
% Impulse (string) - 'gaussian','exp'
%
% OUTPUT:
% dyna_ispta*.mat and output*.asc files are saved
% output*.asc files contain the nodal forces to input into the dyna deck
%
% Example:
% field2dyna('nodes.dyn',0.5,1.3,[0 0 0.02],7.2,'vf105','gaussian');
% ------------------------------------------------------------------------------
% MODIFICATION HISTORY
% ------------------------------------------------------------------------------
% Originally Written - Mark 07/31/03
% Added frequency as an input parameter - Mark 01/31/05
% ------------------------------------------------------------------------------
% Added input variables Transducer and IMPULSE to pass to fieldprms3d_arfi.
% Mark 06/15/05
% ------------------------------------------------------------------------------
% removed dependence on nodes.asc for the input nodes; can now work on nodes.dyn
% assuming that all of the comments are delineated with '*'
% Mark 2011-04-21
% ------------------------------------------------------------------------------

addpath('/home/mlp6/matlab/Field_II_7.10');

% read in the nodes
fid = fopen(NodeName,'r');
measurementPointsandNodes=textscan(fid,'%f%f%f%f','CommentStyle','*','Delimiter',',');
fclose(fid);
measurementPointsandNodes = cell2mat(measurementPointsandNodes);

% skip node number, use just coords
measurementPoints=measurementPointsandNodes(:,2:4);

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
[intensity,FIELD_PARAMS]=dynaField(FIELD_PARAMS);

% save intenstiy file
eval(sprintf('save dyna-I-f%.2f-F%.1f-FD%.3f-a%.1f.mat intensity FIELD_PARAMS',Frequency,Fnum,focus(3),alpha));

disp('The next step is to run makeLoadsTemps.');
disp('This will generate point loads and initial temperatures.');
