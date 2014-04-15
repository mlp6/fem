function []= PointLoadsPlot(NodeName, LoadName)
%% PointLoadsPlot
% This function uses a node file and its corresponding point loads file to
% create a 3d vector plot (quiver plot) of the point loads.
% NodeName - name of nodes file
% LoadName - name of PointLoads file

fid = fopen(NodeName, 'r');
measurementPointsandNodes=textscan(fid,'%f%f%f%f','CommentStyle','*','Delimiter',',');
fclose(fid);
measurementPointsandNodes=cell2mat(measurementPointsandNodes);

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
    nodeLoads(i, 1)
end
quiver3(quivPlot(:, 1), quivPlot(:, 2), quivPlot(:, 3), zeros(size(quivPlot(:, 1))), zeros(size(quivPlot(:, 1))), quivPlot(:, 4));
hold on
%scatter3(quivPlot(:, 1), quivPlot(:, 2), quivPlot(:, 3))
scatter3(measurementPointsandNodes(1:100:length(measurementPointsandNodes(:,2)), 2),...
         measurementPointsandNodes(1:100:length(measurementPointsandNodes(:,2)), 3),...
         measurementPointsandNodes(1:100:length(measurementPointsandNodes(:,2)), 4))
xlabel('x (m)')
ylabel('y (m)')
zlabel('z (m)')
title('Nodal Coordinates and Loads')
hold off
end

