function [nodes,node_coord]=grab_lat_nodes(fname)
% function [nodes,node_coord]=grab_lat_nodes(fname)
% grab desired nodes and corresponding coordinates from *.dyn file
% mark 09/03/02

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
	% find the nodes down the center axis (back)
       if(nodedata(i,2) == 0.0 & nodedata(i,4) < -1.97 & nodedata(i,4) > -2.02) 
		nodes(index)=nodedata(i,1);
		node_coord(index)=nodedata(i,4);
		index=index+1;
	end
end;
disp('node and node coordinate matrices created...')
fclose(fid);

