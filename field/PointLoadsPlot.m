function []= PointLoadsPlot(NodeName, LoadName, randSelect)
%% PointLoadsPlot
% This function uses a node file and its corresponding point loads file to
% create a 3d vector plot (quiver plot) of the point loads. If there are
% greater than 1000 nodes, only 1000 of those will be used to create the
% quiver plot.
% NodeName - name of nodes file
% LoadName - name of PointLoads file
% randSelect - random or non-random point selection for >1000 nodes

if (nargin < 3)
    randSelect = 0;
end
fid = fopen(NodeName, 'r');
measurementPointsandNodes=textscan(fid,'%f%f%f%f','CommentStyle','*','Delimiter',',');
fclose(fid);
measurementPointsandNodes=cell2mat(measurementPointsandNodes);

fid = fopen(LoadName, 'r');
% keep reading lines until we get to where the nodes and point loads begin.
% this is after the line with the element/node volume info.
while 1
    loadLine = fgetl(fid);
    if (~isempty(strfind(loadLine, 'Volume')))
        break; 
    end
end
nodeLoads = textscan(fid,'%f%f%f%f%f','CommentStyle','$','Delimiter',',');
fclose(fid);

nodeLoads = cell2mat(nodeLoads);
quivPlot = measurementPointsandNodes(nodeLoads(:, 1), :);
quivPlot = [quivPlot nodeLoads(:, 4)];

if length(quivPlot) > 1000
    % random mpn selection
    if (randSelect)
        quivSelect = randperm(length(quivPlot), 1000);
        quivPlot = quivPlot(quivSelect, :);
    % non-random mpn selection
    else
        quivSelect = round(length(quivPlot)/1000);
        quivPlot = quivPlot(1:quivSelect:length(quivPlot), :);
    end
end

figure(1);
quiver3(quivPlot(:, 2), quivPlot(:, 3), quivPlot(:, 4), zeros(size(quivPlot(:, 1))), zeros(size(quivPlot(:, 1))), quivPlot(:, 5));
hold on

if length(measurementPointsandNodes) > 1000
    % random mpn selection
    if (randSelect)
        mpnSelect = randperm(length(measurementPointsandNodes), 1000);
        measurementPointsandNodes = measurementPointsandNodes(mpnSelect, :);
    % non-random mpn selection
    else
        mpnSelect = round(length(measurementPointsandNodes)/1000);
        measurementPointsandNodes = measurementPointsandNodes(1:mpnSelect:length(measurementPointsandNodes), :); 

    end
end
scatter3(measurementPointsandNodes(:,2), measurementPointsandNodes(:, 3), measurementPointsandNodes(:,4))
hold off

xlabel('x (m)')
ylabel('y (m)')
zlabel('z (m)')
title('Nodal Coordinates and Loads')