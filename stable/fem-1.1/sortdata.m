function [A,B,lat,ax]=sortdata(node_loc,value,correct_flag);
% function [A,B,lat,ax]=sortdata(node_loc,value);
% sortdata.m - modified version of Steve Hsu's code that sorts my nodes 
% spatially and spits values into those positions
%
% INPUTS:
% node_loc - output variable from read_dyna_nodes.m
%	1st column is node IDs
%	2nd column is x coordinate
%	3rd column is y coordinate
%	4th column is z coordinate
% value - value to be sorted spatially (e.g. force, isptaout, etc)
% correct_flag - which correction scheme to use to re-align the lines
%	         spatially
%	1 - cirs.dyn
%
% OUTPUTS:
% A - 3D matrix of spatially-sorted node IDs
% B - 3D matrix of spatially-sorted values 
% lat - lateral axis labels (mm)
% ax - axial axis labels (mm)
%
% mark 11/13/03 

lat = intersect(node_loc(:,3),node_loc(:,3));
axial = intersect(node_loc(:,4),node_loc(:,4));
ele = intersect(node_loc(:,2),node_loc(:,2));

A = zeros(length(axial),length(lat),length(ele));
B = zeros(length(axial),length(lat),length(ele));

for(i=1:length(node_loc))
  latpos = find(lat == node_loc(i,3));
  axpos = find(axial == node_loc(i,4));
  elepos = find(ele == node_loc(i,2));
  A(axpos,latpos,elepos) = node_loc(i,1);
  B(axpos,latpos,elepos) = value(i);
  
end;

% which correction scheme do we need?
switch correct_flag
	% cirs.dyn
	case 1,
		A2 = A(:,2:2:104,:);
		A2(:,53:104,:) = A(:,107:2:end,:);
		B2 = B(:,2:2:104,:);
		B2(:,53:104,:) = B(:,107:2:end,:);
		lat = (1:104)*0.2;	% mm
		ax = -(1:126)*0.2;	% mm
end;

A = A2;
B = B2;
