function [zdisp]=grab_zdisp(fname,nodes)
% function [zdisp]=grab_zdisp(fname,nodes)
% outpt_fname - displacement output filename
% nodes - nodes where to extract z-disp information 
% mark 09/03/02

endofline=sprintf('\n');

fid=fopen(fname,'r');
if (fid == -1),
        disp(['Can''t open ' fname]);
        return;
        end;

% now, lets extract the displacements for these nodes
% find last word just before data... 
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*NODAL_DISPLACEMENT')),
        s=fscanf(fid,'%s',1);
        end;

% Find start of next line...        
c=fscanf(fid,'%c',1);
while(c~=endofline);
        c=fscanf(fid,'%c',1);
        end;

% Suck in data...  
disp('reading in displacement data...')
[data,count]=fscanf(fid,'%d %e %e %e',[4,inf]);
data=data';
disp('finding axial displacement at given nodes...')
for i=1:length(nodes)
        [j,k]=find(nodes(i) == data(:,1));
	% get the z-disp for the defined nodes
        zdisp(i)=data(j,4);
end;
fclose(fid);

