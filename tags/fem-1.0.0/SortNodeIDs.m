function [SortedNodeIDs,x,y,z]=SortNodeIDs(nodes_file);
% function [SortedNodeIDs,x,y,z]=SortNodeIDs(nodes_file);
% SortNodeIDs - spatially sort the Node IDs
%
% INPUTS: nodes_file (string) - file containing the node IDs
% and coordinates; comma delimited
%
% OUTPUTS: SortedNodeIDs (int) - 3D matrix of spatially sorted node IDs
%
% Mark 07/21/06
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Updated to round out the tolerance errors that HyperMesh can
% introduce in the mesh generation that screws up the sorting
% algorithm
% Mark 09/17/06
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

tic;

% load in the node IDs and corresponding coordinates
% headers/footers must be stripped from this file
nodes=load(nodes_file);

% clean up the precision of the node locations since the
% HyperMesh generation tolerance was so poor; this will help
% with the sorting and the unique functions
scale = 100;
nodes(:,2) = nodes(:,2) * scale;
nodes(:,2) = round(nodes(:,2));
nodes(:,2) = nodes(:,2) / scale;
nodes(:,3) = nodes(:,3) * scale;
nodes(:,3) = round(nodes(:,3));
nodes(:,3) = nodes(:,3) / scale;
nodes(:,4) = nodes(:,4) * scale;
nodes(:,4) = round(nodes(:,4));
nodes(:,4) = nodes(:,4) / scale;

% what are the axes
x = unique(nodes(:,2));
x = x(end:-1:1);
y = unique(nodes(:,3));
z = unique(nodes(:,4));
z = z(end:-1:1);

% numbers of nodes in each dimension
NumX = length(x)
NumY = length(y)
NumZ = length(z)

% check to make sure that the dimensions are okay, otherwise
% the reshape operation will fail
if(NumX * NumY * NumZ ~= size(nodes,1)),
	error('ERROR: Dimension mismatch; make sure the sort tolerance is adequate');
end;

% sort the node IDs by x, y, and z coordinates, in that order
sorted_nodes = sortrows(nodes,[-4 3 -2]);

SortedNodeIDs = reshape(sorted_nodes(:,1),[NumX NumY NumZ]);

toc;
