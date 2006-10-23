function [nodes,node_coord]=grab_nodes(fname,axis_flag)
% function [nodes,node_coord]=grab_nodes(fname,axis_flag)
% grab desired nodes and corresponding coordinates from *.dyn file
% mark 09/03/02
%
% MODIFICATION HX:
% now includes axis flag to determine which axis to plot
% 1-x, 2-y, 3-z -> all are through focus
% mark 04/26/03
endofline=sprintf('\n');
  
% Open file
fid=fopen(fname,'r');
if (fid == -1),
	disp(['Can''t open ' fname]);
	return;
	end;
 
% load in nodes and locations to select the appropriate axis for 
% generating a plot
% find last word just before data... 
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*NODE')),
	s=fscanf(fid,'%s',1);
	end;

% Find start of next line...        
c=fscanf(fid,'%c',1);
while(c~=endofline);
	c=fscanf(fid,'%c',1);
	end;

% Suck in data...  
disp('reading in center axis node data...')
[nodedata,count]=fscanf(fid,'%i %f %f %f',[4,inf]);
nodedata=nodedata';
% find the nodes along the z-axis on the back of the model
index=1;
for i=1:length(nodedata)
	if(axis_flag == 3),
	% find the nodes down the center axis (back)
		if(nodedata(i,2) == 0.0 & nodedata(i,3) < 0.04 & nodedata(i,3) > 0.0) 
		nodes(index)=nodedata(i,1);
		node_coord(index)=nodedata(i,4);
		index=index+1;
		end;
	elseif(axis_flag == 2)
	% find nodes along the lateral axis through the focus	
		if(nodedata(i,2) == 0.0 & nodedata(i,4) < -1.95 & nodedata(i,4) > -2.00) 
		nodes(index)=nodedata(i,1);
		node_coord(index)=nodedata(i,3);
		index=index+1;
		end;
	elseif(axis_flag == 1)
	% find nodes along the elevation axis through the focus	
		if(nodedata(i,4) < -1.95 & nodedata(i,4) > -2.00 & nodedata(i,3) > 0.0 & nodedata(i,3) < 0.04), 
		nodes(index)=nodedata(i,1);
		node_coord(index)=nodedata(i,2);
		index=index+1;
		end;
	end;
end;
disp('node and node coordinate matrices created...')
fclose(fid);
