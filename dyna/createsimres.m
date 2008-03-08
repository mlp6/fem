function []=createsimres(zdispfile,node_asc,TimeStep,TerminationTime);
% function []=createsimres(zdispfile);
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

% load zdisp
load(zdispfile);

[SortedNodeIDs,ele,lat,axial]=SortNodeIDs(node_asc);

% find the imaging plane
ele0 = min(find(ele >= 0));
image_plane = squeeze(SortedNodeIDs(ele0,:,:));

for t=1:size(zdisp,3),
    temp(zdisp(:,1,1)) = zdisp(:,4,t);
    temp2 = -temp(image_plane)*1e4;
    temp2 = shiftdim(temp2,1);
    arfidata(:,:,t) = temp2;
end;

t=0:TimeStep:TerminationTime; % s
axial = -axial';
axial = axial*10; % convert to mm
lat = lat';
lat = lat*10; % convert to mm

save simres.mat arfidata lat axial t
