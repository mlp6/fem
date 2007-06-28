function []=dyna_convolve_FR(nodename,tmax)
%function %[]=dyna_convolve_FR(nodename,tmax)
% 
% Generate dyna_convolve_FR file for convolveFR.m
%
% INPUTS:
% nodename (string) - file name containing *NODE data
% tmax (int) - max t*.asc file to read in
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
% Modified to read in dyna output from mutiple time steps
% Mark 12/15/02
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
% Removed the correction factor (obsolete).  
% Modified to accomodate multiple meshes.
% Mark 04/13/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
% Removed the need to input the number of nodes in each
% dimension and the node spacing.  These values are now
% internally computed from the nodal data.
% Mark 07/27/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 

endofline=sprintf('\n');

fid=fopen(nodename,'r');
if (fid == -1),
        disp(['Can''t open ' nodename]);
        return;
        end;
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*NODE')),
        s=fscanf(fid,'%s',1);
        end;
c=fscanf(fid,'%c',1);
while(c~=endofline);
        c=fscanf(fid,'%c',1);
        end;
disp('Reading in node data')
[nodedata,count]=fscanf(fid,'%i %f %f %f',[4,inf]);
nodedata=nodedata';

disp(nodename)
whos nodedata;
% find the nodes on the symmetry plane of the model
index=1;
for i=1:length(nodedata)
	if(abs(nodedata(i,2)) < 1e-4),
		nodes(index)=nodedata(i,1);
		node_coord(1,index)=nodedata(i,2);
		node_coord(2,index)=nodedata(i,3);
		node_coord(3,index)=nodedata(i,4);
		index=index+1;
	end;
end;
disp('Node and node coordinate matrices created')
fclose(fid);

% now, all of the data is read in... lets re-sort it into a
% plane sort the node IDs by y-coordinate
[Y,I]=sort(node_coord(2,:));
nodes=nodes(I);
node_coord(2,:) = node_coord(2,I);
node_coord(3,:) = node_coord(3,I);

% figure out the number of nodes in the axial and lateral
% dimensions 
NoAxNodes = length(find(node_coord(2,:) == min(node_coord(2,:))))
NoLatNodes = length(node_coord(3,:))/NoAxNodes

% reshape the z-coordinates into a plane matrix, along with
% corresponding node IDs
node_coord3=reshape(node_coord(3,:),NoAxNodes,NoLatNodes);
nodefind = reshape(nodes,NoAxNodes,NoLatNodes);

% computer the node spacing in the axial and lateral dimensions
AxMax = max(node_coord(3,:));
AxMin = min(node_coord(3,:));
AxNodeSpace = abs(AxMax - AxMin)/(NoAxNodes - 1);
AxNodeSpace = AxNodeSpace * 10 % convert from cm -> mm
LatMax = max(node_coord(2,:));
LatMin = min(node_coord(2,:));
LatNodeSpace = abs(LatMax - LatMin)/(NoLatNodes - 1);
LatNodeSpace = LatNodeSpace * 10 % convert from cm -> mm

% now sort each column of the matrix to have ascending axial entries
for m=1:NoAxNodes,
	[Z,N]=sort(node_coord3(m,:));
	nodefind(m,:)=nodefind(m,N);
end;

% create temperature matrix
temps = zeros(NoAxNodes,NoLatNodes,tmax);

%%% CHANGED TO ACCOMODATE ADDITIONAL FRAMES %%%
for n=1:tmax,
	disp(n);
	filetemp=load(sprintf('t%i.asc',n));
	t(:,:)=filetemp;
%whos t nodedata nodefind
	T = zeros(length(nodedata),1);
	T(t(:,1))=t(:,2);
whos t nodedata nodefind T
	temps(:,:,n)=T(nodefind);
	clear t;	
end;

clear T

% lets plot the output
lat = (0:(NoLatNodes-1))*LatNodeSpace;
lat = lat - max(lat)/2;
ax = ((NoAxNodes-1):-1:0)*AxNodeSpace;
figure;
imagesc(lat,ax,temps(:,:,1));
xlabel('Laterial Position (mm)')
ylabel('Axial Position (mm)')
colorbar;

save dyna_convolve_FR.mat temps lat ax NoAxNodes NoLatNodes AxNodeSpace LatNodeSpace
