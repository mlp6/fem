function []=createsimreslat(zdispfile,node_asc,TimeStep,TerminationTime);
% function []=createsimreslat(zdispfile);
%
% Create simres.mat that shares the same format as experimental res*.mat files.
%
% INPUTS:
%   zdispfile (string) - path for zdisp.dat created by createzdisp.m
%   node_asc (string) - path to the node ID & coordinate ASCII file (no dyna
%                       headers/footers)
%   TimeStep (float) - time step b/w d3plot data saves (s)
%   TerminationTime (float) - final time simulated (s)
%
%   Requires the function SortNodeIDs.m - should be in the svn repository.
% 
% OUTPUTS:
%   Saves the file sim_res.mat to the CWD.
%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MODIFICATION HISTORY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Originally written
% Mark 03/07/08
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2009-07-08
% Modified to read individual time steps from the zdisp.dat binary file so that
% large chunks of RAM are needed.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% This will now be done in the timestep loop, streamed from the zdisp.dat file.
% load zdisp
% load(zdispfile);

[SortedNodeIDs,ele,lat,axial]=SortNodeIDs(node_asc);

% find the imaging plane
ele0 = min(find(ele >= 0));
image_plane = squeeze(SortedNodeIDs(ele0,:,:));

% load in some parameters from zdisp.dat
if(exist(zdispfile,'file') == 0),
    error(sprintf('%s does not exist.  Make sure that zdisp.mat files are converted to zdisp.dat .',zdispfile));
end;
zdisp_fid = fopen(zdispfile,'r');

NUM_NODES = fread(zdisp_fid,1,'float32');
NUM_DIMS = fread(zdisp_fid,1,'float32');
NUM_TIMESTEPS = fread(zdisp_fid,1,'float32');

%for t=1:size(zdisp,3),
for t=1:NUM_TIMESTEPS,

    % extract the zdisp values for the appropriate time step
    fseek(zdisp_fid,3*4+NUM_NODES*NUM_DIMS*(t-1)*4,-1);
    zdisp_slice = fread(zdisp_fid,NUM_NODES*NUM_DIMS,'float32');
    zdisp_slice = double(reshape(zdisp_slice,NUM_NODES,NUM_DIMS));

    %temp(zdisp(:,1,1)) = zdisp(:,4,t);
    % changed to extract the lateral displacement (3), not the axial (4)
    %temp(zdisp_slice(:,1)) = zdisp_slice(:,4);
    temp(zdisp_slice(:,1)) = zdisp_slice(:,3);
    temp2 = -temp(image_plane)*1e4;
    temp2 = shiftdim(temp2,1);
    arfidata(:,:,t) = temp2;

end;

% setup the axis and time variables
t=0:TimeStep:TerminationTime; % s
axial = -axial';
axial = axial*10; % convert to mm
lat = lat';
lat = lat*10; % convert to mm

% make sure that the correct number of time steps are in the 't' variable - if
% not, truncate ones off the end b/c the number of dumped time steps can come
% up one short from the calculated number of data dumps
if(length(t) ~= size(arfidata,3)),
    if(length(t) < size(arfidata,3)),
        arfidata = arfidata(:,:,1:length(t));
    else,
        t = t(1:size(arfidata,3));
    end;
end;

save res_sim_lat.mat arfidata lat axial t
