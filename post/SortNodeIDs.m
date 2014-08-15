function [SortedNodeIDs,ele,lat,axial]=SortNodeIDs(nodes_file);
% function [SortedNodeIDs,ele,lat,axial]=SortNodeIDs(nodes_file);
% SortNodeIDs - spatially sort the Node IDs
%
% INPUTS: 
%   nodes_file (string) - file containing the node IDs
%                         and coordinates; comma delimited
%
% OUTPUTS: 
%   SortedNodeIDs (int) - 3D matrix of spatially sorted node IDs
%   ele (floats) - unique elevation axis
%   lat (floats) - unique lateral axis
%   axial (floats) - unique axial axis
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% First crack at this...
% Mark 07/21/06
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Updated to round out the tolerance errors that HyperMesh can
% introduce in the mesh generation that screws up the sorting
% algorithm
% Mark 09/17/06
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Updated the comments to reflect what is actually going on.
% Mark 03/07/08
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% changed nodes.asc -> nodes.dyn (i.e., handle header/footer starting with '*'
% Mark 2011-04-21
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

tic;

% load in the node IDs and corresponding coordinates
nodes = read_mpn(nodes_file,4);

% clean up the precision of the node locations since the
% HyperMesh generation tolerance was so poor; this will help
% with the sorting and the unique functions
scale = 1000;
for i=2:4,
    nodes(:,i) = nodes(:,i) * scale;
    nodes(:,i) = round(nodes(:,i));
    nodes(:,i) = nodes(:,i) / scale;
end;

% what are the axes
ele = unique(nodes(:,2));
ele = ele(end:-1:1);
lat = unique(nodes(:,3));
axial = unique(nodes(:,4));
axial = axial(end:-1:1);

% numbers of nodes in each dimension
NumX = length(ele)
NumY = length(lat)
NumZ = length(axial)

% check to make sure that the dimensions are okay, otherwise
% the reshape operation will fail
if(NumX * NumY * NumZ ~= size(nodes,1)),
  error('ERROR: Dimension mismatch; make sure the sort tolerance is adequate');
end;

% sort the node IDs by x, y, and z coordinates, in that order
sorted_nodes = sortrows(nodes,[-4 3 -2]);

SortedNodeIDs = reshape(sorted_nodes(:,1),[NumX NumY NumZ]);

toc;
