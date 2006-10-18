function CombineCenterLines(NoCenterLines,Tmin,Tmax);
% function CombineCenterLines(NoCenterLines,Tmin,Tmax);
% script to combine center line data for lesion sims
% Mark 02/17/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% converted to a function for use in many sim directories
% this will only work for cirs.dyn simulations since there are
% some hard-coded values, e.g. the spacing of centerlines
% RUN IN THE CENTER LINE DIRECTORY!!
%
% INPUTS:
% NoCenterLines (int) - number of centerlines, including
% symmetry; should be an odd number
% Tmin (int) - min time step to extract
% Tmax (int) - max time step to extract
%
% OUTPUTS: CenterLines.mat is created in the CWD
%
% Mark 04/14/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% what directory are we working in
cwd = pwd;

% load in list of nodes on center line
% this loads in a variable, 'ii', that has the center line
% node IDs
load /emfd/mlp6/CIRS_FEM/center_node_list.mat

% setup variables
% number of total centerlines to grab (including symmetry)
% this should always be an odd number!!
%NoCenterLines = 25; 
% minimum time step from the sims to grab
%Tmin = 2;  
% maximum time step from the sims to grab
%Tmax = 31;

% setup axes
axial = (1:124)*0.2; % mm
lat = ((0:NoCenterLines-1)*0.2);
lat = lat - max(lat)/2;

% setup two vectors to loop through for the lateral offset
% simulations (e.g., 0p2 -> M = 0, N = 2)
% ASSUMING THAT LINE SPACING IS 0.2 mm and a max of 41 lines!!
MA = [0 0 0 0 1 1 1 1 1 2 2 2 2 2 3 3 3 3 3 4];
NA = [2 4 6 8 0 2 4 6 8 0 2 4 6 8 0 2 4 6 8 0];
M(1:floor(NoCenterLines/2)) = MA(1:floor(NoCenterLines/2))
N(1:floor(NoCenterLines/2)) = NA(1:floor(NoCenterLines/2))

% for each time step, load in the centerline displacement
% data and assemble in into 'matrix'
% 'matrix' is a 3-dim variable: lat pos x axial pos x time

% start with the center lateral location
disp('Processing the center line');
eval(sprintf('load %s/zdisp.mat',cwd));
for t = Tmin:Tmax,
  matrix(ceil(NoCenterLines/2),:,t) = -zdisp(ii,4,t)'*1e4;
end;

% now go through the laterally-offset locations
for LatIndex = 1:length(M),
	disp(sprintf('Lateral line %i of %i',LatIndex,length(M)));
	eval(sprintf('load %s/%ip%imm/zdisp.mat',cwd,M(LatIndex),N(LatIndex)));
	for t = Tmin:Tmax,
		% stick the data on both sides of the center lateral location
		matrix(ceil(NoCenterLines/2)-LatIndex,:,t) = -zdisp(ii,4,t)'*1e4;   
		matrix(ceil(NoCenterLines/2)+LatIndex,:,t) = -zdisp(ii,4,t)'*1e4;   
	end;
end;

% allocate space for the normalization matrix 
matrixnorm = ones(size(matrix(:,:,Tmin)));

% now fill the normalization matrix with the homogeneous displacement
% profile (1) at the first time step (Tmin)
for i=1:NoCenterLines,
  matrixnorm(i,:) = matrix(1,:,2);
end;

% now, normalize all of the displacement data for all time by matrixnorm
for t=Tmin:Tmax,
  matrix2(:,:,t) = matrix(:,:,t)./matrixnorm;
end;

% now lets save the data
clear zdisp;
disp('Saving data to file');
save CenterLines.mat *

% finally, let's take a look at the results
%figure;
%imagesc(lat,axial,matrix2(:,:,2)',[0 1]);
%axis image;
%colormap(gray);
%colorbar;
%title('Normalized Image');
%xlabel('Lateral Position (mm)');
%ylabel('Depth (mm)');

