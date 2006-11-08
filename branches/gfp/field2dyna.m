function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse,LatApod,ElevApod)
%function []=field2dyna(NodeName,alpha,Fnum,focus,Frequency,Transducer,Impulse,LatApod,ElevApod)
% -----------------------------------------------------------
% INPUT:
% NodeName (string) - file name to read nodes from (*.dyn or nodes.asc)
% alpha - 0.5, 1.0, etc.
% Fnum - F/# (e.g. 1.3)
% focus - [x y z] (m)
% thr - 0.05 (throw out stuff below 5% of the peak value
% Frequency - center frequency (MHz)
% Transducer (string) - 'vf105','vf73'
% Impulse (string) - 'gaussian','exp'
% LatApod (boolean) - 1 (yes), 0 (no)
% ElevApod (boolean) - 1 (yes), 0 (no)
%
% OUTPUT:
% dyna_ispta*.mat and output*.asc files are saved
% output*.asc files contain the nodal forces to input into the dyna deck
%
% Example:
% field2dyna('/home/mlp6/thermal/therm74nodes.dyn',0.5,1.3,[0 0 0.02],
% 7.2,'vf105','gaussian',1,1);
%
% ----------------------------------------------------------
% Originally Written - Mark 07/31/03
% Added frequency as an input parameter - Mark 01/31/05
% ----------------------------------------------------------
% Added input variables Transducer and IMPULSE to pass to
% fieldprms3d_arfi.
% Mark 06/15/05
% ----------------------------------------------------------
% Added apodization
% Mark 11/05/06
% ----------------------------------------------------------
% Added elevation apodization in addition to lateral
% apodization.
% Mark 11/07/06
% ----------------------------------------------------------

% README!!
disp('THIS IS A MODIFIED VERSION OF CODE FOR COMPARISON WITH');
disp('GIANMARCO''S SIMULATIONS - IT SAVES DIFFERENT VARIABLES');
disp('SPECIFICALLY PRESSURE WAVEFORMS AND START TIMES');

% read in the nodes
disp('Reading in node data...');
measurementPointsandNodes=read_dyna_nodes(NodeName);

% skip node number, use just coords
measurementPoints=measurementPointsandNodes(:,2:4);

% invert the z axis
measurementPoints(:,3)=-measurementPoints(:,3);

% switch x and y so plane of symmetry is elevation, not lateral
tmp=measurementPoints(:,1:2);
measurementPoints(:,1:2)=[tmp(:,2) tmp(:,1)];

% convert from cm -> m 
measurementPoints=measurementPoints/100; 

disp('Node data scaled and reformated.');

% create a variable structure to pass to fieldprms3d_arfi
FIELD_PARAMS.measurementPointsandNodes = measurementPointsandNodes;
FIELD_PARAMS.measurementPoints = measurementPoints;
FIELD_PARAMS.alpha = alpha;
FIELD_PARAMS.Fnum = Fnum;
FIELD_PARAMS.focus = focus;
FIELD_PARAMS.Frequency = Frequency;
FIELD_PARAMS.Transducer = Transducer;
FIELD_PARAMS.Impulse = Impulse;
FIELD_PARAMS.LatApod = LatApod;
FIELD_PARAMS.ElevApod = ElevApod;

% perform the field calculation
disp('Simulating the pressure field using Field II');
[isptaout,FIELD_PARAMS]=fieldprms3d_arfi(FIELD_PARAMS);

% save isptaout file, along with the pressures and start times
%eval(sprintf('save dyna_ispta_att%.1f.mat isptaout FIELD_PARAMS pressure StartTimes',alpha));

disp('The next step is to run makeLoadsTemps.');
disp('This will generate point loads and initial temperatures.');
