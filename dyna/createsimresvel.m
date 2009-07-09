function []=createsimresvel(zdispfile,node_asc,TimeStep,TerminationTime);
% function []=createsimresvel(zdispfile);
% Summary: Create simres.mat that shares the same format as experimental
% res*.mat files.
%
% INPUTS:
%   zdispfile (string) - path for zdisp.mat created by createzdisp.m
%   node_asc (string) - path to the node ID & coordinate ASCII file (no dyna
%                       headers/footers)
%   TimeStep (float) - time step b/w d3plot data saves (s)
%   TerminationTime (float) - final time simulated (s)
%
%   Requires the function SortNodeIDs.m - should be in the svn repository.
% 
% OUTPUTS:
%   This saves the file simres.mat to the CWD.
%
% Mark 03/07/08
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This version saves velocity data.
%
% Mark Palmeri (mark.palmeri@duke.edu)
% 2008-12-02 (15:35)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% load zdisp
load(zdispfile);

[SortedNodeIDs,ele,lat,axial]=SortNodeIDs(node_asc);

% find the imaging plane
ele0 = min(find(ele >= 0));
image_plane = squeeze(SortedNodeIDs(ele0,:,:));

for t=1:size(vel,3),
    temp(vel(:,1,1)) = vel(:,4,t);
    temp2 = -temp(image_plane)*1e4;
    temp2 = shiftdim(temp2,1);
    arfidata(:,:,t) = temp2;
end;

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

arfidata_zvel = arfidata;
save res_sim_zvel.mat arfidata_zvel lat axial t
