function []= PointLoadsPlot(NodeName, LoadName)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here

fid = fopen(NodeName, 'r');
measurementPointsandNodes=textscan(fid,'%f%f%f%f','CommentStyle','*','Delimiter',',');
fclose(fid);
measurementPointsandNodes=cell2mat(measurementPointsandNodes);

xCoord = measurementPointsandNodes(:, 2);
yCoord = measurementPointsandNodes(:, 3);
zCoord = measurementPointsandNodes(:, 4);

fid = fopen(LoadName, 'r');
% keep reading lines until we get to where the nodes and point loads begin
% which is after the line with the element/node volume info.
while 1
    loadLine = fgetl(fid);
    if (~isempty(strfind(loadLine, 'Volume')))
        break; 
    end
end
nodeLoads = textscan(fid,'%f%f%f%f%f','CommentStyle','$','Delimiter',',');
fclose(fid);
nodeLoads = cell2mat(nodeLoads);
quivPlot = zeros(length(nodeLoads), 4);
for i = 1:length(nodeLoads)
    [nodeID, y] = find(measurementPointsandNodes(:, 1) == nodeLoads(i, 1));
    quivPlot(i, :) = [measurementPointsandNodes(nodeID, 2), measurementPointsandNodes(nodeID, 3), ...
                measurementPointsandNodes(nodeID, 4), nodeLoads(i, 4)];
end
quiver3(quivPlot(:, 1), quivPlot(:, 2), quivPlot(:, 3), zeros(size(quivPlot(:, 1))), zeros(size(quivPlot(:, 1))), quivPlot(:, 4));
hold on
%scatter3(quivPlot(:, 1), quivPlot(:, 2), quivPlot(:, 3))
scatter3(xCoord(1:100:length(xCoord)), yCoord(1:100:length(yCoord)), zCoord(1:100:length(zCoord)))
xlabel('x (m)')
ylabel('y (m)')
zlabel('z (m)')
title('Nodal Coordinates and Loads')
end

