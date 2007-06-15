function [node_loc] = read_dyna_nodes(fname);
% function [node_loc] = read_dyna_nodes(fname);                     
%
% fname is the name of your .dyn file
%
% node_loc is array of node locations in the format
%  NODE_NUMBER X Y Z
% node_loc it has as many rows as there are nodes
%
% NOTE:  You cannot have any comment lines b/w *NODE and the
% four column data format - this will cause the script to
% choke!!
%
% Mark 08/04/05

endofline=sprintf('\n');
  
% Open file
fid=fopen(fname,'r');
if (fid == -1),
	disp(['Can''t open ' fname]);
	return;
	end;
 
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
[node_loc,count]=fscanf(fid,'%d,%f,%f,%f',[4,inf]);
node_loc=node_loc';
fclose(fid);
