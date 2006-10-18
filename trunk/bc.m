function bc(ifname,zmin,zmax,nodespc);
% function bc(ifname,zmin,zmax,nodespc);
%
% Assign boundary conditions to the structural dyna models.
% Fully contraint the top (transducer) and bottom surfaces, and
% apply symmetry contraints along the axial-lateral face,
% centered in elevation.
% INPUTS:
%   ifname (string) - filename of dyna input deck to read in
%   *NODE card with read_dyna_nodes.m
%   zmin - location of the bottom surface (assuming negative
%   z-axis); in units that the mesh was built in
%   zmax - location of the top surface (usually at 0)
%   nodespc - spacing b/w nodes (to determine a search
%   tolerance); units mesh was built in
% OUTPUTS:  ascii file bc.dyn is written; this is imported into
% the dyna deck under the *BOUNDARY_SPC_NODES card
%
% Mark 03/24/05

% output file name to write BC info for input into deck under
% *BOUNDARY_SPC_NODE
fname='bc.dyn';
fid=fopen(fname,'w');

% write header to the output file
fprintf(fid,'*BOUNDARY_SPC_NODE\n');

% read in the dyna nodes and their coordinates
% Node ID : x-coord : y-coord : z-coord
disp('Reading in the nodal data');
MPN=read_dyna_nodes(ifname);
whos MPN

% now go through all of the nodes, select the ones that fall on
% the planes of interest, and apply the appropriate boundary
% conditions
disp('Checking each node for existence on the top/bottom surface or the symmetry plane');
for i=1:length(MPN)

	% apply full contraints to the top and bottom faces
	if(MPN(i,4)<(zmin + nodespc/2) | MPN(i,4)>(zmax - nodespc/2))
	%if(MPN(i,4) == zmin |  MPN(i,4) == zmax )
		fprintf(fid,'%d,0,1,1,1,1,1,1 \n',MPN(i,1));

	% apply symmetry contraints to the symmetry plane (very top
	% and bottom corners are excluded by the first conditional
	% statement to avoid duplciate assignments
	%elseif(MPN(i,2)==0.0)
	elseif(MPN(i,2) > -nodespc/2)
		fprintf(fid,'%d,0,1,0,0,0,1,1 \n',MPN(i,1));

	end;	

end;	

% write footer and close the output file
disp('Done writing bc.asc');
fprintf(fid,'*END\n');
fclose(fid);
