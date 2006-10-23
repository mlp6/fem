for i = 1:length(measurementPointsandNodes),
if(measurementPointsandNodes(i,3) < 0.0 & isptaout(i)/max(isptaout) > 0.0001),
	[index]=find(measurementPointsandNodes(:,3) < ...
		-measurementPointsandNodes(i,3) + 0.01 & ...
		measurementPointsandNodes(:,3) > ...
		-measurementPointsandNodes(i,3)-0.01);
	for j=1:length(index),
		if(measurementPointsandNodes(j,2) == measurementPointsandNodes(i,2) & measurementPointsandNodes(j,4) == measurementPointsandNodes(i,4))
		disp('fixing value...')
		isptaout(i) = isptaout(index(j));
		end;
	end;
end;
end;
