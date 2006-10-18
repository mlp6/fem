function []=centerplane_movie(numframes)
% function []=centerplane_movie(numframes)
%
% load in the centerplane 2D node set and the result file from the 
% current working directory
%
% tell it how many frames to process
%
% it will spit out a movie.mat file that has axis variables, and disp
% through time (displacement data in microns, + away from transducer)
%
% mark 09/18/03

load /emfd/mlp6/CIRS_FEM/centerplane.mat
load zdisp.mat

%index = zeros(max(zdisp(:,1,1)),1);
for i = 1:numframes,
	data(zdisp(:,1,1)) = zdisp(:,4,i);
	disp(:,:,i) = -data(nodefind)*1e4;
end;

ax = (1:size(nodefind,1))*0.2;
lat = (1:size(nodefind,2))*0.2;

%imagesc(lat,ax,disp,[0 20])
%xlabel('Lateral Position (mm)')
%ylabel('Axial Position (mm)')
