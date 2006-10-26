% cat_node_data.m - concatenate the node data files into a
% single file, with the pressure data 'hashed' into rows
% associated w/ nodeID
% Mark 10/25/06

files = dir('node*.mat');
for i=1:size(files,1),
	disp(sprintf('%s (%i/%i)',files(i).name,i,size(files,1)));
	load(files(i).name);
	PRESSURE(nodeID,1:size(pressure,2)) = pressure(:,:);
	START_TIME(nodeID) = startTime;
	ISPTA(nodeID) = isptaout;
	clear pressure nodeID startTime isptaout;
end;

save nodedata.mat PRESSURE START_TIME ISPTA FIELD_PARAMS;
