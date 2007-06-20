function [out,lat,ax]=centerplane(zdisp,t)
% function [out,lat,ax]=centerplane(zdisp,t)
%
% DESCRIPTION:
% pull out the centerplane data from the zdisp variable for a
% given time step
% 
% INPUT:
% zdisp - read in the zdisp.mat variable
% t - what time step do you want data extracted from?
%
% OUTPUT:
% out - 2D matrix of centerplane displacement data (um) at t
% lat - lateral axis (mm)
% ax - axial axis (mm)
%
% Mark 02/19/04
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Added the lateral (lat) and axial (ax) axis variables
% Mark 12/18/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

load /moredata/mlp6/CIRS_FEM/centerplane.mat

% node spacing is 0.2 mm in the geometric shadow of the
% transducer (cirs.dyn)
ax = (0:(size(nodefind,1)-1))*0.2;
lat = (0:(size(nodefind,2)-1))*0.2;
% center the lateral axis about 0
lat = lat - max(lat)/2;

temp(zdisp(:,1,1)) = zdisp(:,4,t);
out(:,:) = -temp(nodefind)*1e4;
